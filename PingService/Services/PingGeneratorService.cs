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
    private volatile bool _isPaused = false;
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
    /// Pause ping generation
    /// </summary>
    public void Pause()
    {
        _isPaused = true;
        _logger.LogInformation("Ping generation PAUSED");
    }

    /// <summary>
    /// Resume ping generation
    /// </summary>
    public void Resume()
    {
        _isPaused = false;
        _logger.LogInformation("Ping generation RESUMED");
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

    public bool IsPaused => _isPaused;
}
