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
    private readonly IHubContext<PingHub> _hubContext;
    private readonly ILogger<PingGeneratorService> _logger;

    // Thread-safe dictionary for tracking coordinate counts
    private readonly ConcurrentDictionary<string, CoordinatePing> _coordinateCounts;

    // Control flags
    private volatile bool _isPaused = true; // Start paused - require manual start
    private volatile bool _isRunning = false; // Track if system has been started
    private long _totalPingsGenerated = 0;
    private DateTime _startTime;
    private readonly Stopwatch _stopwatch;

    // Configuration
    private const int TARGET_PINGS_PER_SECOND = 20000;
    private const int BATCH_SIZE = 100; // Process in batches for efficiency
    private const int BROADCAST_INTERVAL_MS = 100; // Broadcast updates every 100ms
    private const int STATS_INTERVAL_MS = 1000; // Broadcast stats every second

    // For batching updates to clients
    private readonly ConcurrentQueue<PingUpdate> _updateQueue;
    private readonly SemaphoreSlim _updateSemaphore;

    // Random number generation (thread-safe via ThreadStatic)
    [ThreadStatic]
    private static Random? _random;
    private static Random RandomInstance => _random ??= new Random();

    public PingGeneratorService(
        IHubContext<PingHub> hubContext,
        ILogger<PingGeneratorService> logger)
    {
        _hubContext = hubContext;
        _logger = logger;
        _coordinateCounts = new ConcurrentDictionary<string, CoordinatePing>();
        _updateQueue = new ConcurrentQueue<PingUpdate>();
        _updateSemaphore = new SemaphoreSlim(1, 1);
        _stopwatch = new Stopwatch();
    }

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
    private async Task GeneratePingsAsync(CancellationToken stoppingToken)
    {
        _logger.LogInformation("Starting ping generation at {Rate} pings/second", TARGET_PINGS_PER_SECOND);

        // Calculate delay between batches
        var delayMicroseconds = (BATCH_SIZE * 1_000_000) / TARGET_PINGS_PER_SECOND;
        var delayMilliseconds = delayMicroseconds / 1000.0;

        while (!stoppingToken.IsCancellationRequested)
        {
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
    private void GenerateSinglePing()
    {
        // Generate random latitude (-90 to +90) and longitude (-180 to +180)
        // With 6 decimal precision
        double latitude = Math.Round((RandomInstance.NextDouble() * 180) - 90, 6);
        double longitude = Math.Round((RandomInstance.NextDouble() * 360) - 180, 6);

        string coordKey = $"{latitude},{longitude}";

        // Update or add coordinate count (thread-safe)
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
        Interlocked.Increment(ref _totalPingsGenerated);

        // Queue update for broadcasting
        _updateQueue.Enqueue(new PingUpdate(latitude, longitude, ping.Count));
    }

    /// <summary>
    /// Batch and broadcast updates to connected clients
    /// </summary>
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
            while (_updateQueue.TryDequeue(out var update) && updates.Count < 1000)
            {
                updates.Add(update);
            }

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
                    _logger.LogError(ex, "Error broadcasting ping updates");
                }
            }
        }
    }

    /// <summary>
    /// Periodically broadcast system statistics
    /// </summary>
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
    public IEnumerable<CoordinatePing> GetTopCoordinates(int count = 100)
    {
        return _coordinateCounts.Values
            .OrderByDescending(c => c.Count)
            .Take(count);
    }

    /// <summary>
    /// Get count for a specific coordinate
    /// </summary>
    public CoordinatePing? GetCoordinate(double latitude, double longitude)
    {
        string key = $"{latitude},{longitude}";
        _coordinateCounts.TryGetValue(key, out var ping);
        return ping;
    }

    /// <summary>
    /// Search coordinates by pattern
    /// </summary>
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
    public IEnumerable<CoordinatePing> GetAllCoordinates()
    {
        return _coordinateCounts.Values;
    }

    public bool IsPaused => _isPaused;
    public bool IsRunning => _isRunning;
}
