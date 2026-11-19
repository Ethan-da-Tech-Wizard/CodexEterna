// ==============================================================================
// Program: CryptoService.cs
// Programmer: Ethan-da-Tech-Wizard
// Last Modified: November 18, 2026
// Purpose: Long-running hosted background service establishing a persistent WebSocket
//          stream to Binance market feeds, parsing BTC/USDT live trades, calculating
//          rolling metrics, and periodically taking 10-minute snapshot records.
// ==============================================================================
// Concurrent collections for snapshots, ClientWebSocket for the Binance stream,
// System.Text.Json for parsing messages, and IHubContext to relay prices to dashboards.
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
    private readonly IHubContext<PingHub> _hubContext;
    private readonly ILogger<CryptoService> _logger;

    // WebSocket connection
    // Current connection; null while disconnected. Recreated on each (re)connect.
    private ClientWebSocket? _webSocket;
    // Binance public trade stream for BTC/USDT (no API key needed). Requires outbound internet
    // access; stream name 'btcusdt@trade' delivers one message per executed trade.
    private readonly Uri _binanceWebSocketUri = new Uri("wss://stream.binance.com:9443/ws/btcusdt@trade");

    // Control flags
    // Set by the controller via Start/StopAsync; read by the background loop on another thread.
    private volatile bool _isRunning = false;
    private readonly Stopwatch _stopwatch;
    private DateTime _startTime;
    // UTC time of the last snapshot (initialised to the start time).
    private DateTime _lastSnapshotTime;

    // Crypto data storage
    // Snapshots keyed by their timestamp text, held in memory only (lost on restart, never trimmed).
    private readonly ConcurrentDictionary<string, CryptoSnapshot> _cryptoSnapshots;
    // Rolling window of the most recent trades. List is not thread-safe, so all access
    // is guarded by _tradesLock. Nothing in this service reads it back yet.
    private readonly List<CryptoTrade> _recentTrades;
    private readonly object _tradesLock = new object();

    // Configuration
    // Interval between snapshots, cap on buffered trades, and the delay before reconnecting
    // after a dropped connection.
    private const int SNAPSHOT_INTERVAL_MINUTES = 10;
    private const int MAX_TRADES_BUFFER = 1000;
    private const int RECONNECT_DELAY_MS = 5000;

    // Current price tracking
    // Interval statistics, reset after each snapshot. These are plain fields updated by the
    // receive loop and read by HTTP threads without a lock (acceptable for display, not exact).
    // _lowPrice starts at decimal.MaxValue so the first trade becomes the low.
    private decimal _currentPrice = 0;
    private decimal _highPrice = 0;
    private decimal _lowPrice = decimal.MaxValue;
    private long _totalTrades = 0;

    // Dependencies come from DI; collections are initialised here.
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

    // Step 1: Main background daemon lifecycle management loop
    // Idle loop: until an operator calls Start() it only polls the flag once per second, so
    // no network connection is made at application startup.
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
                // Wait for manual start
                await Task.Delay(1000, stoppingToken);
            }
        }
    }

    // One connection session: connect, receive trades until closed or stopped, clean up and
    // (if still running) reconnect after a delay. The method returns after each session and
    // ExecuteAsync loops to start another.
    private async Task RunCryptoMonitoring(CancellationToken stoppingToken)
    {
        try
        {
            _logger.LogInformation("Connecting to Binance WebSocket...");

            _webSocket = new ClientWebSocket();
            await _webSocket.ConnectAsync(_binanceWebSocketUri, stoppingToken);

            _logger.LogInformation("Connected to Binance WebSocket - Monitoring BTC/USDT");

            // Start snapshot timer
            // Runs concurrently with the receive loop and is awaited after it ends. Caution: it is waiting on
            // a 10-minute Task.Delay, so after Stop it may keep this session open until that delay
            // elapses or the host shuts down.
            var snapshotTask = TakePeriodicSnapshots(stoppingToken);

            // Process incoming messages
            // Each ReceiveAsync result is treated as one complete JSON message. Trade messages are
            // much smaller than 8 KB, but fragmented frames (EndOfMessage = false) are not reassembled.
            var buffer = new byte[8192];
            while (_webSocket.State == WebSocketState.Open && _isRunning && !stoppingToken.IsCancellationRequested)
            {
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

            await snapshotTask;
        }
        catch (Exception ex)
        {
            // Any error (network drop, DNS failure) is logged; the finally block then decides about reconnecting.
            _logger.LogError(ex, "Error in crypto monitoring");
        }
        // Always release the socket. A graceful close is attempted only if it is still open.
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
                // Fixed delay between attempts (no exponential back-off).
                _logger.LogInformation("Reconnecting in {Delay}ms...", RECONNECT_DELAY_MS);
                await Task.Delay(RECONNECT_DELAY_MS);
            }
        }
    }

    // Step 4: Parse incoming JSON payload and update rolling price statistics
    // Parse one Binance trade JSON message and update price, extrema and the trade buffer.
    // Exceptions are caught per message so a bad payload cannot stop the stream.
    private void ProcessTradeMessage(string message)
    {
        try
        {
            // Property names match Binance's short JSON keys (case-sensitive: 'e' vs 'E').
            var trade = JsonSerializer.Deserialize<BinanceTradeMessage>(message);
            if (trade != null)
            {
                // Binance sends prices as strings to avoid floating-point loss, hence decimal.Parse.
                // Parse uses the current culture; an invariant-culture parse would be more robust.
                _currentPrice = decimal.Parse(trade.p);
                _totalTrades++;

                if (_currentPrice > _highPrice)
                    // Reset the per-interval statistics for the next window.
                    _highPrice = _currentPrice;

                if (_currentPrice < _lowPrice)
                    _lowPrice = _currentPrice;

                // Store recent trade
                // Guard the shared list. Trade time T is milliseconds since the Unix epoch.
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
                        // Drop the oldest entry (O(n) on a List, acceptable for a 1000-item buffer).
                        _recentTrades.RemoveAt(0);
                    }
                }

                // Broadcast current price to clients
                // Blocks the receive loop until the SignalR send finishes (sync-over-async). Simple and
                // preserves order, but a slow client path would throttle ingestion.
                BroadcastCurrentPriceAsync(_currentPrice).Wait();
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error processing trade message");
        }
    }

    // Timer loop: sleep for the interval, then record a snapshot if still running.
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

    // Step 5: Capture periodic 10-minute historical snapshot with timestamped record
    // Record the current state as a CryptoSnapshot, then restart the high/low window from the
    // current price so each snapshot covers only its own interval.
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
        // Second-resolution key, so two snapshots in the same second would collide (TryAdd would skip the second).
        var key = now.ToString("yyyy-MM-dd HH:mm:ss");
        _cryptoSnapshots.TryAdd(key, snapshot);

        _logger.LogInformation(
            "Snapshot taken - Price: ${Price}, High: ${High}, Low: ${Low}, Trades: {Trades}",
            _currentPrice, _highPrice, _lowPrice, _totalTrades);

        // Reset interval stats
        _highPrice = _currentPrice;
        _lowPrice = _currentPrice;
        _totalTrades = 0;
        _lastSnapshotTime = now;

        // Broadcast snapshot to clients
        BroadcastSnapshotAsync(snapshot).Wait();
    }

    // Push the latest price to all dashboards as "ReceiveCryptoPrice"; errors are logged, never thrown.
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

    // Push a finished snapshot as "ReceiveCryptoSnapshot".
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
    // Step 2: Explicit manual start command ensuring operator control over network activity
    public void Start()
    {
        if (!_isRunning)
        {
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
    // This is an overload of BackgroundService.StopAsync(CancellationToken), not an override; it is
    // the operator-initiated stop. Closing the socket makes the receive loop exit.
    public async Task StopAsync()
    {
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
    // Newest first.
    public IEnumerable<CryptoSnapshot> GetAllSnapshots()
    {
        return _cryptoSnapshots.Values.OrderByDescending(s => s.Timestamp);
    }

    /// <summary>
    /// Get snapshots by date range
    /// </summary>
    // Inclusive range filter on the snapshot timestamp, newest first.
    public IEnumerable<CryptoSnapshot> GetSnapshotsByDateRange(DateTime startDate, DateTime endDate)
    {
        return _cryptoSnapshots.Values
            .Where(s => s.Timestamp >= startDate && s.Timestamp <= endDate)
            .OrderByDescending(s => s.Timestamp);
    }

    /// <summary>
    /// Get current stats
    /// </summary>
    // Assemble a status object from the live fields. HighPrice/LowPrice reflect the current
    // interval; LowPrice reads decimal.MaxValue until the first trade arrives.
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

    // Read-only flag exposed to the controller.
    public bool IsRunning => _isRunning;
}

/// <summary>
/// Binance trade message format
/// </summary>
// DTO matching Binance's trade event JSON. Short lowercase/uppercase names are deliberate:
// System.Text.Json maps them by exact name, so renaming would break deserialisation.
public class BinanceTradeMessage
{
    // e = event type, E = event time (ms), s = symbol, p = price, q = quantity, T = trade time (ms).
    public string e { get; set; } = string.Empty; // Event type
    public long E { get; set; } // Event time
    public string s { get; set; } = string.Empty; // Symbol
    public string p { get; set; } = string.Empty; // Price
    public string q { get; set; } = string.Empty; // Quantity
    public long T { get; set; } // Trade time
}
