// ==============================================================================
// Program: PingGeneratorService.cs
// Programmer: Ethan-da-Tech-Wizard
// Last Modified: November 18, 2026
// Purpose: High-performance background service generating 20,000 synthetic coordinate
//          pings per second. Utilizes thread-safe concurrent collections, batching
//          queues, and throttled SignalR multicasting to simulate global sensor telemetry.
// ==============================================================================
// ConcurrentDictionary/ConcurrentQueue for lock-free sharing between the generator and
// broadcaster tasks; Stopwatch for uptime; IHubContext to push to SignalR clients
// from outside a hub.
using System.Collections.Concurrent;
using System.Diagnostics;
using Microsoft.AspNetCore.SignalR;
using PingService.Hubs;
using PingService.Models;

namespace PingService.Services;

/// <summary>
/// Background service that generates 20,000 coordinate pings per second
/// Tracks occurrence counts and broadcasts updates to connected clients
/// </summary>
public class PingGeneratorService : BackgroundService
{
    // IHubContext lets a background service send to connected clients without a hub instance.
    private readonly IHubContext<PingHub> _hubContext;
    private readonly ILogger<PingGeneratorService> _logger;

    // Thread-safe dictionary for tracking coordinate counts
    // Key: "lat,lon" text. Value: the mutable CoordinatePing. Grows without bound while running
    // (about 20,000 mostly-unique keys per second), so memory is the practical limit.
    private readonly ConcurrentDictionary<string, CoordinatePing> _coordinateCounts;

    // Control flags
    // volatile ensures the generator loop sees changes made by HTTP request threads.
    // The service starts paused so nothing is generated until an operator calls Start.
    private volatile bool _isPaused = true; // Start paused - require manual start
    // False until Start() is called the first time; Stop() clears it again.
    private volatile bool _isRunning = false; // Track if system has been started
    // Updated with Interlocked.Increment; read without a lock for stats (a slightly stale value is fine).
    private long _totalPingsGenerated = 0;
    private DateTime _startTime;
    private readonly Stopwatch _stopwatch;

    // Configuration
    // Tuning constants. Target rate is the goal, not a guarantee: Task.Delay granularity
    // (about 1-15 ms depending on the OS) means the real rate is usually lower.
    private const int TARGET_PINGS_PER_SECOND = 20000;
    // Pings generated per loop iteration; one delay is paid per batch instead of per ping.
    private const int BATCH_SIZE = 100; // Process in batches for efficiency
    // How often queued updates are flushed to clients.
    private const int BROADCAST_INTERVAL_MS = 100; // Broadcast updates every 100ms
    private const int STATS_INTERVAL_MS = 1000; // Broadcast stats every second

    // For batching updates to clients
    // Buffer between the generator (producer) and the broadcaster (consumer).
    private readonly ConcurrentQueue<PingUpdate> _updateQueue;

    // Thread-safe random number generation using thread-local storage ([ThreadStatic]).
    // Concurrency Design Rationale:
    // System.Random is NOT thread-safe; sharing an instance across parallel threads causes race conditions
    // and zero-returns. Using locks on a single Random causes severe lock contention at 20,000 ops/sec.
    // [ThreadStatic] gives each executing thread its own independent generator instance with zero lock overhead.
    // Caution: a [ThreadStatic] field initialiser would only run on the first thread, which is why
    // the lazy '??=' accessor below creates the Random on first use per thread.
    [ThreadStatic]
    private static Random? _random;
    private static Random RandomInstance => _random ??= new Random();

    // Dependencies come from DI. The collections are created here, not inline, so all fields stay readonly.
    public PingGeneratorService(
        IHubContext<PingHub> hubContext,
        ILogger<PingGeneratorService> logger)
    {
        _hubContext = hubContext;
        _logger = logger;
        _coordinateCounts = new ConcurrentDictionary<string, CoordinatePing>();
        _updateQueue = new ConcurrentQueue<PingUpdate>();
        _stopwatch = new Stopwatch();
    }

    // Step 1: Initialize parallel worker tasks for generation, broadcasting, and diagnostics
    // Runs for the app lifetime. Note this starts the stopwatch immediately even though
    // generation is paused until Start(), so Uptime includes idle time before the first start.
    // Task.WhenAll keeps the three loops running side by side; if one throws, the exception
    // surfaces here once all have finished.
    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        _startTime = DateTime.UtcNow;
        _stopwatch.Start();

        _logger.LogInformation("PingGeneratorService starting...");

        // Start multiple background tasks
        var generatorTask = GeneratePingsAsync(stoppingToken);
        var broadcasterTask = BroadcastUpdatesAsync(stoppingToken);
        var statsTask = BroadcastStatsAsync(stoppingToken);

        await Task.WhenAll(generatorTask, broadcasterTask, statsTask);
    }

    /// <summary>
    /// Main ping generation loop - targets 20,000 pings/second
    /// </summary>
    // Step 2: High-throughput batch generation loop executing up to target frequency
    private async Task GeneratePingsAsync(CancellationToken stoppingToken)
    {
        _logger.LogInformation("Starting ping generation at {Rate} pings/second", TARGET_PINGS_PER_SECOND);

        // Calculate delay between batches
        // Delay per batch: 100 pings * 1,000,000 us / 20,000 per sec = 5,000 us = 5 ms.
        // Integers are used first, then converted to fractional milliseconds.
        var delayMicroseconds = (BATCH_SIZE * 1_000_000) / TARGET_PINGS_PER_SECOND;
        var delayMilliseconds = delayMicroseconds / 1000.0;

        while (!stoppingToken.IsCancellationRequested)
        {
            // Poll the pause flag every iteration. While paused, sleep 100 ms rather than spinning the CPU.
            if (!_isPaused)
            {
                // Generate batch of coordinates
                for (int i = 0; i < BATCH_SIZE; i++)
                {
                    GenerateSinglePing();
                }

                // Small delay to maintain target rate
                if (delayMilliseconds > 0)
                {
                    await Task.Delay(TimeSpan.FromMilliseconds(delayMilliseconds), stoppingToken);
                }
            }
            else
            {
                // When paused, check every 100ms
                await Task.Delay(100, stoppingToken);
            }
        }
    }

    /// <summary>
    /// Generate a single coordinate ping and update counts
    /// </summary>
    // One synthetic sensor reading.
    private void GenerateSinglePing()
    {
        // Generate random latitude (-90 to +90) and longitude (-180 to +180)
        // With 6 decimal precision
        // NextDouble() is in [0,1); scaled and shifted to a uniform range. Rounding to 6 decimals
        // (~0.1 m) makes exact duplicates rare, so most counts will be 1.
        double latitude = Math.Round((RandomInstance.NextDouble() * 180) - 90, 6);
        double longitude = Math.Round((RandomInstance.NextDouble() * 360) - 180, 6);

        string coordKey = $"{latitude},{longitude}";

        // Update or add coordinate count (thread-safe)
        // AddOrUpdate is atomic per key for add/replace, but the update lambda mutates the shared
        // object in place, so two threads hitting the same key could lose an increment. With a single
        // generator loop this is not an issue in practice.
        var ping = _coordinateCounts.AddOrUpdate(
            coordKey,
            new CoordinatePing(latitude, longitude, 1),
            (key, existing) =>
            {
                existing.Count++;
                existing.LastSeen = DateTime.UtcNow;
                return existing;
            }
        );

        // Increment total counter
        // Atomic increment for the global counter.
        Interlocked.Increment(ref _totalPingsGenerated);

        // Queue update for broadcasting
        // Queue a copy of the new count; if the broadcaster lags this queue can grow without limit.
        _updateQueue.Enqueue(new PingUpdate(latitude, longitude, ping.Count));
    }

    /// <summary>
    /// Batch and broadcast updates to connected clients
    /// </summary>
    // Step 3: Multicast batch updates via SignalR at bounded client refresh intervals
    // Consumer loop: every 100 ms, drain up to 1000 queued updates and send them as one batch
    // ("ReceivePingBatch") instead of 20,000 individual messages per second.
    // The batch size is checked BEFORE dequeuing (see DrainBatch), so items beyond the cap stay
    // queued for the next cycle instead of being removed and lost.
    private async Task BroadcastUpdatesAsync(CancellationToken stoppingToken)
    {
        var updates = new List<PingUpdate>(1000);

        while (!stoppingToken.IsCancellationRequested)
        {
            await Task.Delay(BROADCAST_INTERVAL_MS, stoppingToken);

            if (_updateQueue.IsEmpty)
                continue;

            // Dequeue updates
            updates.Clear();
            DrainBatch(_updateQueue, updates, 1000);

            if (updates.Count > 0)
            {
                try
                {
                    // Broadcast batch to all connected clients
                    await _hubContext.Clients.All.SendAsync(
                        "ReceivePingBatch",
                        updates,
                        stoppingToken);
                }
                catch (Exception ex)
                {
                    // A failed send must not kill the loop; log and continue with the next interval.
                    _logger.LogError(ex, "Error broadcasting ping updates");
                }
            }
        }
    }

    /// <summary>
    /// Moves up to <paramref name="maxItems"/> updates from the queue into <paramref name="target"/>.
    /// </summary>
    /// <remarks>
    /// The limit is tested before TryDequeue so that an item is never removed from the queue
    /// without being added to the batch (the earlier loop checked the limit afterwards and lost
    /// one update every time the queue held more than the cap).
    /// </remarks>
    /// <returns>The number of items moved.</returns>
    public static int DrainBatch(ConcurrentQueue<PingUpdate> queue, List<PingUpdate> target, int maxItems)
    {
        var moved = 0;
        // Cap first, dequeue second: that order is the whole fix.
        while (moved < maxItems && queue.TryDequeue(out var update))
        {
            target.Add(update);
            moved++;
        }
        return moved;
    }

    /// <summary>
    /// Periodically broadcast system statistics
    /// </summary>
    // Step 4: Compute and emit aggregate throughput and memory utilization metrics
    // Once per second push PingStats to everyone as "ReceiveStats".
    private async Task BroadcastStatsAsync(CancellationToken stoppingToken)
    {
        while (!stoppingToken.IsCancellationRequested)
        {
            await Task.Delay(STATS_INTERVAL_MS, stoppingToken);

            try
            {
                var stats = GetCurrentStats();
                await _hubContext.Clients.All.SendAsync("ReceiveStats", stats, stoppingToken);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error broadcasting stats");
            }
        }
    }

    /// <summary>
    /// Get current system statistics
    /// </summary>
    // Builds a stats snapshot. The rate is total divided by total elapsed stopwatch time, i.e.
    // an average since start/reset. Counter fields are read without locks, so values are
    // approximate while generation is running.
    public PingStats GetCurrentStats()
    {
        var elapsedSeconds = _stopwatch.Elapsed.TotalSeconds;
        var pingsPerSecond = elapsedSeconds > 0 ? _totalPingsGenerated / elapsedSeconds : 0;

        return new PingStats
        {
            TotalPingsGenerated = _totalPingsGenerated,
            UniqueCoordinates = _coordinateCounts.Count,
            PingsPerSecond = Math.Round(pingsPerSecond, 2),
            IsPaused = _isPaused,
            StartTime = _startTime,
            Uptime = _stopwatch.Elapsed,
            MemoryUsageMB = GC.GetTotalMemory(false) / (1024 * 1024)
        };
    }

    /// <summary>
    /// Get top N coordinates by count
    /// </summary>
    // Sorts all stored coordinates on every call: O(n log n) over a possibly huge dictionary.
    public IEnumerable<CoordinatePing> GetTopCoordinates(int count = 100)
    {
        return _coordinateCounts.Values
            .OrderByDescending(c => c.Count)
            .Take(count);
    }

    /// <summary>
    /// Get count for a specific coordinate
    /// </summary>
    // Direct dictionary lookup using the same "lat,lon" key format as GenerateSinglePing.
    public CoordinatePing? GetCoordinate(double latitude, double longitude)
    {
        string key = $"{latitude},{longitude}";
        _coordinateCounts.TryGetValue(key, out var ping);
        return ping;
    }

    /// <summary>
    /// Search coordinates by pattern
    /// </summary>
    // Linear scan with a case-insensitive substring match on the key; results ordered by count.
    public IEnumerable<CoordinatePing> SearchCoordinates(string pattern, int limit = 100)
    {
        return _coordinateCounts.Values
            .Where(c => c.CoordinateKey.Contains(pattern, StringComparison.OrdinalIgnoreCase))
            .OrderByDescending(c => c.Count)
            .Take(limit);
    }

    /// <summary>
    /// Get filtered coordinates with advanced filtering options
    /// </summary>
    // Builds a lazy LINQ pipeline; nothing runs until the caller enumerates the result.
    // Filters are ANDed. Enumerating a ConcurrentDictionary's Values is safe while it is being
    // modified, but gives a moving snapshot.
    public IEnumerable<CoordinatePing> GetFilteredCoordinates(
        double? minLat = null,
        double? maxLat = null,
        double? minLon = null,
        double? maxLon = null,
        long? minCount = null,
        long? maxCount = null,
        int? lastSeenMinutes = null,
        string? hemisphere = null,
        string sortBy = "count",
        bool ascending = false,
        int limit = 100)
    {
        // Start from every stored coordinate.
        var query = _coordinateCounts.Values.AsEnumerable();

        // Filter by latitude range
        if (minLat.HasValue)
            query = query.Where(c => c.Latitude >= minLat.Value);
        if (maxLat.HasValue)
            query = query.Where(c => c.Latitude <= maxLat.Value);

        // Filter by longitude range
        if (minLon.HasValue)
            query = query.Where(c => c.Longitude >= minLon.Value);
        if (maxLon.HasValue)
            query = query.Where(c => c.Longitude <= maxLon.Value);

        // Filter by count range
        if (minCount.HasValue)
            query = query.Where(c => c.Count >= minCount.Value);
        if (maxCount.HasValue)
            query = query.Where(c => c.Count <= maxCount.Value);

        // Filter by last seen time
        if (lastSeenMinutes.HasValue)
        {
            var cutoffTime = DateTime.UtcNow.AddMinutes(-lastSeenMinutes.Value);
            query = query.Where(c => c.LastSeen >= cutoffTime);
        }

        // Filter by hemisphere
        if (!string.IsNullOrEmpty(hemisphere))
        {
            // Latitude >= 0 counts as north and longitude >= 0 as east, so the equator and the
            // prime meridian belong to north and east. Unknown names add no filter.
            switch (hemisphere.ToLower())
            {
                case "north":
                    query = query.Where(c => c.Latitude >= 0);
                    break;
                case "south":
                    query = query.Where(c => c.Latitude < 0);
                    break;
                case "east":
                    query = query.Where(c => c.Longitude >= 0);
                    break;
                case "west":
                    query = query.Where(c => c.Longitude < 0);
                    break;
                case "northeast":
                    query = query.Where(c => c.Latitude >= 0 && c.Longitude >= 0);
                    break;
                case "northwest":
                    query = query.Where(c => c.Latitude >= 0 && c.Longitude < 0);
                    break;
                case "southeast":
                    query = query.Where(c => c.Latitude < 0 && c.Longitude >= 0);
                    break;
                case "southwest":
                    query = query.Where(c => c.Latitude < 0 && c.Longitude < 0);
                    break;
            }
        }

        // Sort
        // Unknown sortBy values fall through to ordering by count.
        query = sortBy.ToLower() switch
        {
            "latitude" => ascending ? query.OrderBy(c => c.Latitude) : query.OrderByDescending(c => c.Latitude),
            "longitude" => ascending ? query.OrderBy(c => c.Longitude) : query.OrderByDescending(c => c.Longitude),
            "lastseen" => ascending ? query.OrderBy(c => c.LastSeen) : query.OrderByDescending(c => c.LastSeen),
            _ => ascending ? query.OrderBy(c => c.Count) : query.OrderByDescending(c => c.Count)
        };

        return query.Take(limit);
    }

    /// <summary>
    /// Get coordinates by geographic region
    /// </summary>
    // Region -> approximate lat/lon bounding box (named tuple). Boxes are coarse and overlap,
    // e.g. asia and oceania share longitudes. Unknown names get the whole globe; the controller
    // validates names before calling this.
    public IEnumerable<CoordinatePing> GetCoordinatesByRegion(string region, int limit = 100)
    {
        var regionBounds = region.ToLower() switch
        {
            "north_america" => (minLat: 15.0, maxLat: 72.0, minLon: -170.0, maxLon: -50.0),
            "south_america" => (minLat: -56.0, maxLat: 13.0, minLon: -82.0, maxLon: -34.0),
            "europe" => (minLat: 36.0, maxLat: 71.0, minLon: -10.0, maxLon: 40.0),
            "africa" => (minLat: -35.0, maxLat: 37.0, minLon: -18.0, maxLon: 52.0),
            "asia" => (minLat: -10.0, maxLat: 80.0, minLon: 25.0, maxLon: 180.0),
            "oceania" => (minLat: -50.0, maxLat: 0.0, minLon: 110.0, maxLon: 180.0),
            _ => (minLat: -90.0, maxLat: 90.0, minLon: -180.0, maxLon: 180.0)
        };

        return GetFilteredCoordinates(
            minLat: regionBounds.minLat,
            maxLat: regionBounds.maxLat,
            minLon: regionBounds.minLon,
            maxLon: regionBounds.maxLon,
            limit: limit
        );
    }

    /// <summary>
    /// Get aggregate statistics by hemisphere or region
    /// </summary>
    // Counts of distinct coordinates (not pings) per bucket; hemisphere buckets overlap
    // (a point counts in one north/south and one east/west bucket). Unknown groupBy returns empty.
    public Dictionary<string, object> GetAggregateStats(string groupBy = "hemisphere")
    {
        var stats = new Dictionary<string, object>();

        if (groupBy.ToLower() == "hemisphere")
        {
            stats["North"] = _coordinateCounts.Values.Count(c => c.Latitude >= 0);
            stats["South"] = _coordinateCounts.Values.Count(c => c.Latitude < 0);
            stats["East"] = _coordinateCounts.Values.Count(c => c.Longitude >= 0);
            stats["West"] = _coordinateCounts.Values.Count(c => c.Longitude < 0);
        }
        else if (groupBy.ToLower() == "quadrant")
        {
            stats["NE"] = _coordinateCounts.Values.Count(c => c.Latitude >= 0 && c.Longitude >= 0);
            stats["NW"] = _coordinateCounts.Values.Count(c => c.Latitude >= 0 && c.Longitude < 0);
            stats["SE"] = _coordinateCounts.Values.Count(c => c.Latitude < 0 && c.Longitude >= 0);
            stats["SW"] = _coordinateCounts.Values.Count(c => c.Latitude < 0 && c.Longitude < 0);
        }
        else if (groupBy.ToLower() == "count_range")
        {
            // Histogram of how many times coordinates were generated.
            stats["1"] = _coordinateCounts.Values.Count(c => c.Count == 1);
            stats["2-5"] = _coordinateCounts.Values.Count(c => c.Count >= 2 && c.Count <= 5);
            stats["6-10"] = _coordinateCounts.Values.Count(c => c.Count >= 6 && c.Count <= 10);
            stats["11-50"] = _coordinateCounts.Values.Count(c => c.Count >= 11 && c.Count <= 50);
            stats["51+"] = _coordinateCounts.Values.Count(c => c.Count > 50);
        }

        return stats;
    }

    /// <summary>
    /// Start the ping generation system (requires manual activation)
    /// </summary>
    // First call arms the system and unpauses it; later calls act as Resume.
    // Stopwatch.Start() resumes timing after a Stop() without clearing elapsed time.
    public void Start()
    {
        if (!_isRunning)
        {
            _isRunning = true;
            _isPaused = false;
            _startTime = DateTime.UtcNow;
            _stopwatch.Start();
            _logger.LogInformation("Ping generation STARTED - System is now collecting data at {Rate} pings/second", TARGET_PINGS_PER_SECOND);
        }
        else
        {
            Resume();
        }
    }

    /// <summary>
    /// Stop the ping generation system immediately
    /// </summary>
    // Pauses generation and clears the running flag. Data is retained, so Start() continues
    // from the existing counts; use Reset() to clear them.
    public void Stop()
    {
        _isPaused = true;
        _isRunning = false;
        _stopwatch.Stop();
        _logger.LogInformation("Ping generation STOPPED - All operations ceased immediately");
    }

    /// <summary>
    /// Pause ping generation (temporary)
    /// </summary>
    // No-op unless the system has been started.
    public void Pause()
    {
        if (_isRunning)
        {
            _isPaused = true;
            _logger.LogInformation("Ping generation PAUSED");
        }
    }

    /// <summary>
    /// Resume ping generation (only if system is running)
    /// </summary>
    public void Resume()
    {
        if (_isRunning)
        {
            _isPaused = false;
            _logger.LogInformation("Ping generation RESUMED");
        }
    }

    /// <summary>
    /// Reset all counters and data
    /// </summary>
    // Clears data and counters, restarts the stopwatch. The paused/running state is unchanged.
    public void Reset()
    {
        _coordinateCounts.Clear();
        _totalPingsGenerated = 0;
        _startTime = DateTime.UtcNow;
        _stopwatch.Restart();
        _logger.LogInformation("Ping generation RESET");
    }

    /// <summary>
    /// Get all unique coordinates (for comprehensive mapping)
    /// </summary>
    // Returns the live Values collection (a snapshot copy for ConcurrentDictionary), which can be large.
    public IEnumerable<CoordinatePing> GetAllCoordinates()
    {
        return _coordinateCounts.Values;
    }

    // Read-only views of the control flags for controllers.
    public bool IsPaused => _isPaused;
    public bool IsRunning => _isRunning;
}
