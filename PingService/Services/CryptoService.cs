// Program: CodexEterna - CryptoService.cs
// Programmer: Ethan-da-Tech-Wizard (written with Claude, an AI assistant)
// Last Modified: 2026-11-18
// Purpose: Background service that streams live BTC/USDT trades from Binance over a WebSocket, tracks price and range, takes 10-minute snapshots and broadcasts updates to browsers.
// --- Imports ---
using System.Collections.Concurrent;
using System.Net.WebSockets;
using System.Text;
using System.Text.Json;
using System.Diagnostics;
using Microsoft.AspNetCore.SignalR;
using PingService.Hubs;
using PingService.Models;

namespace PingService.Services;

/// <summary>
/// Background service that monitors Binance crypto prices via WebSocket
/// Stores snapshots every 10 minutes with timestamps
/// </summary>
public class CryptoService : BackgroundService
{
    // Injected dependencies: the hub context lets this background service push messages to browsers.
    private readonly IHubContext<PingHub> _hubContext;
    private readonly ILogger<CryptoService> _logger;

    // WebSocket connection
    private ClientWebSocket? _webSocket;
    private readonly Uri _binanceWebSocketUri = new Uri("wss://stream.binance.com:9443/ws/btcusdt@trade");

    // Control flags
    // volatile because the flag is changed by HTTP requests and read by the background loop on other threads.
    private volatile bool _isRunning = false;
    // Measures uptime while monitoring is active.
    private readonly Stopwatch _stopwatch;
    private DateTime _startTime;
    private DateTime _lastSnapshotTime;

    // Crypto data storage
    // Thread-safe store of snapshots, keyed by their timestamp text.
    private readonly ConcurrentDictionary<string, CryptoSnapshot> _cryptoSnapshots;
    // Small rolling buffer of the latest trades; guarded by the lock below.
    private readonly List<CryptoTrade> _recentTrades;
    private readonly object _tradesLock = new object();

    // Configuration
    // Settings: snapshot spacing, trade buffer size, and pause before reconnecting.
    private const int SNAPSHOT_INTERVAL_MINUTES = 10;
    private const int MAX_TRADES_BUFFER = 1000;
    private const int RECONNECT_DELAY_MS = 5000;

    // Current price tracking
    // Running values for the current interval; the low starts at the maximum so any real price replaces it.
    private decimal _currentPrice = 0;
    private decimal _highPrice = 0;
    private decimal _lowPrice = decimal.MaxValue;
    private long _totalTrades = 0;

    /// <summary>
    /// Creates the service with its injected dependencies and empty storage.
    /// </summary>
    public CryptoService(
        IHubContext<PingHub> hubContext,
        ILogger<CryptoService> logger)
    {
        _hubContext = hubContext;
        _logger = logger;
        _stopwatch = new Stopwatch();
        _cryptoSnapshots = new ConcurrentDictionary<string, CryptoSnapshot>();
        _recentTrades = new List<CryptoTrade>();
    }

    /// <summary>
    /// Main background loop: idles until Start() is called, then runs the monitor.
    /// </summary>
    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        _logger.LogInformation("CryptoService initialized - awaiting manual start");

        while (!stoppingToken.IsCancellationRequested)
        {
            if (_isRunning)
            {
                await RunCryptoMonitoring(stoppingToken);
            }
            else
            {
                // Data collection only begins when a user asks for it.
                // Wait for manual start
                await Task.Delay(1000, stoppingToken);
            }
        }
    }

    /// <summary>
    /// Connects to Binance, reads trade messages until stopped or disconnected, then cleans up and reconnects if still running.
    /// </summary>
    private async Task RunCryptoMonitoring(CancellationToken stoppingToken)
    {
        try
        {
            _logger.LogInformation("Connecting to Binance WebSocket...");

            // Open a new connection for each monitoring session.
            _webSocket = new ClientWebSocket();
            await _webSocket.ConnectAsync(_binanceWebSocketUri, stoppingToken);

            _logger.LogInformation("Connected to Binance WebSocket - Monitoring BTC/USDT");

            // Start snapshot timer
            // Runs alongside the receive loop below; awaited at the end.
            var snapshotTask = TakePeriodicSnapshots(stoppingToken);

            // Process incoming messages
            // Reusable receive buffer; messages here are small text frames.
            var buffer = new byte[8192];
            while (_webSocket.State == WebSocketState.Open && _isRunning && !stoppingToken.IsCancellationRequested)
            {
                // Waits for the next message from the server.
                var result = await _webSocket.ReceiveAsync(
                    new ArraySegment<byte>(buffer),
                    stoppingToken);

                if (result.MessageType == WebSocketMessageType.Text)
                {
                    var message = Encoding.UTF8.GetString(buffer, 0, result.Count);
                    ProcessTradeMessage(message);
                }
                else if (result.MessageType == WebSocketMessageType.Close)
                {
                    _logger.LogWarning("WebSocket connection closed by server");
                    break;
                }
            }

            // Make sure the snapshot loop has finished before cleaning up.
            await snapshotTask;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error in crypto monitoring");
        }
        // Always release the socket, whatever happened above.
        finally
        {
            if (_webSocket != null)
            {
                if (_webSocket.State == WebSocketState.Open)
                {
                    await _webSocket.CloseAsync(
                        WebSocketCloseStatus.NormalClosure,
                        "Service stopped",
                        CancellationToken.None);
                }
                _webSocket.Dispose();
                _webSocket = null;
            }

            if (_isRunning)
            {
                // Reconnect if still running
                _logger.LogInformation("Reconnecting in {Delay}ms...", RECONNECT_DELAY_MS);
                await Task.Delay(RECONNECT_DELAY_MS);
            }
        }
    }

    /// <summary>
    /// Parses one trade message, updates price statistics and the recent-trade buffer, and pushes the new price to browsers.
    /// </summary>
    private void ProcessTradeMessage(string message)
    {
        try
        {
            var trade = JsonSerializer.Deserialize<BinanceTradeMessage>(message);
            if (trade != null)
            {
                // The exchange sends prices as text; decimal keeps exact values.
                _currentPrice = decimal.Parse(trade.p);
                _totalTrades++;

                if (_currentPrice > _highPrice)
                    _highPrice = _currentPrice;

                if (_currentPrice < _lowPrice)
                    _lowPrice = _currentPrice;

                // Store recent trade
                lock (_tradesLock)
                {
                    _recentTrades.Add(new CryptoTrade
                    {
                        Symbol = trade.s,
                        Price = _currentPrice,
                        Quantity = decimal.Parse(trade.q),
                        Timestamp = DateTimeOffset.FromUnixTimeMilliseconds(trade.T).UtcDateTime
                    });

                    // Keep buffer size manageable
                    if (_recentTrades.Count > MAX_TRADES_BUFFER)
                    {
                        _recentTrades.RemoveAt(0);
                    }
                }

                // Broadcast current price to clients
                // Blocks until the send completes so messages go out in order.
                BroadcastCurrentPriceAsync(_currentPrice).Wait();
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error processing trade message");
        }
    }

    /// <summary>
    /// Waits one interval at a time and records a snapshot while monitoring is running.
    /// </summary>
    private async Task TakePeriodicSnapshots(CancellationToken stoppingToken)
    {
        while (_isRunning && !stoppingToken.IsCancellationRequested)
        {
            await Task.Delay(TimeSpan.FromMinutes(SNAPSHOT_INTERVAL_MINUTES), stoppingToken);

            if (_isRunning)
            {
                TakeSnapshot();
            }
        }
    }

    /// <summary>
    /// Saves the current price, high, low and trade count as a snapshot, then resets the interval statistics.
    /// </summary>
    private void TakeSnapshot()
    {
        var now = DateTime.UtcNow;
        var snapshot = new CryptoSnapshot
        {
            Id = Guid.NewGuid().ToString(),
            Symbol = "BTCUSDT",
            Timestamp = now,
            Price = _currentPrice,
            HighPrice = _highPrice,
            LowPrice = _lowPrice,
            TotalTrades = _totalTrades,
            IntervalMinutes = SNAPSHOT_INTERVAL_MINUTES
        };

        // Store snapshot with timestamp key
        var key = now.ToString("yyyy-MM-dd HH:mm:ss");
        _cryptoSnapshots.TryAdd(key, snapshot);

        _logger.LogInformation(
            "Snapshot taken - Price: ${Price}, High: ${High}, Low: ${Low}, Trades: {Trades}",
            _currentPrice, _highPrice, _lowPrice, _totalTrades);

        // Each snapshot starts a fresh interval from the latest price.
        // Reset interval stats
        _highPrice = _currentPrice;
        _lowPrice = _currentPrice;
        _totalTrades = 0;
        _lastSnapshotTime = now;

        // Broadcast snapshot to clients
        BroadcastSnapshotAsync(snapshot).Wait();
    }

    /// <summary>
    /// Sends the latest price to every connected browser; failures are logged, not thrown.
    /// </summary>
    private async Task BroadcastCurrentPriceAsync(decimal price)
    {
        try
        {
            await _hubContext.Clients.All.SendAsync("ReceiveCryptoPrice", new
            {
                symbol = "BTCUSDT",
                price = price,
                timestamp = DateTime.UtcNow
            });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error broadcasting price");
        }
    }

    /// <summary>
    /// Sends a newly taken snapshot to every connected browser; failures are logged, not thrown.
    /// </summary>
    private async Task BroadcastSnapshotAsync(CryptoSnapshot snapshot)
    {
        try
        {
            await _hubContext.Clients.All.SendAsync("ReceiveCryptoSnapshot", snapshot);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error broadcasting snapshot");
        }
    }

    /// <summary>
    /// Start crypto monitoring (requires manual confirmation)
    /// </summary>
    public void Start()
    {
        if (!_isRunning)
        {
            // Flipping the flag wakes the background loop within a second.
            _isRunning = true;
            _startTime = DateTime.UtcNow;
            _lastSnapshotTime = DateTime.UtcNow;
            _stopwatch.Start();
            _logger.LogInformation("Crypto monitoring STARTED - Connecting to Binance WebSocket");
        }
    }

    /// <summary>
    /// Stop crypto monitoring immediately
    /// </summary>
    public async Task StopAsync()
    {
        // Clearing the flag makes the receive loop exit; the socket is then closed politely.
        _isRunning = false;
        _stopwatch.Stop();
        _logger.LogInformation("Crypto monitoring STOPPED - Disconnecting from Binance");

        if (_webSocket != null && _webSocket.State == WebSocketState.Open)
        {
            await _webSocket.CloseAsync(
                WebSocketCloseStatus.NormalClosure,
                "User requested stop",
                CancellationToken.None);
        }
    }

    /// <summary>
    /// Get all snapshots
    /// </summary>
    public IEnumerable<CryptoSnapshot> GetAllSnapshots()
    {
        // Newest snapshots first.
        return _cryptoSnapshots.Values.OrderByDescending(s => s.Timestamp);
    }

    /// <summary>
    /// Get snapshots by date range
    /// </summary>
    public IEnumerable<CryptoSnapshot> GetSnapshotsByDateRange(DateTime startDate, DateTime endDate)
    {
        return _cryptoSnapshots.Values
            .Where(s => s.Timestamp >= startDate && s.Timestamp <= endDate)
            .OrderByDescending(s => s.Timestamp);
    }

    /// <summary>
    /// Get current stats
    /// </summary>
    public CryptoStats GetCurrentStats()
    {
        return new CryptoStats
        {
            IsRunning = _isRunning,
            CurrentPrice = _currentPrice,
            HighPrice = _highPrice,
            LowPrice = _lowPrice,
            TotalSnapshots = _cryptoSnapshots.Count,
            LastSnapshotTime = _lastSnapshotTime,
            Uptime = _stopwatch.Elapsed,
            Symbol = "BTCUSDT"
        };
    }

    // Read-only view of the running flag for controllers.
    public bool IsRunning => _isRunning;
}

/// <summary>
/// Binance trade message format
/// </summary>
public class BinanceTradeMessage
{
    // Property names are single letters because they must match the field names in the exchange's JSON.
    public string e { get; set; } = string.Empty; // Event type
    public long E { get; set; } // Event time
    public string s { get; set; } = string.Empty; // Symbol
    public string p { get; set; } = string.Empty; // Price
    public string q { get; set; } = string.Empty; // Quantity
    public long T { get; set; } // Trade time
}
