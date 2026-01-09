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
    private ClientWebSocket? _webSocket;
    private readonly Uri _binanceWebSocketUri = new Uri("wss://stream.binance.com:9443/ws/btcusdt@trade");

    // Control flags
    private volatile bool _isRunning = false;
    private readonly Stopwatch _stopwatch;
    private DateTime _startTime;
    private DateTime _lastSnapshotTime;

    // Crypto data storage
    private readonly ConcurrentDictionary<string, CryptoSnapshot> _cryptoSnapshots;
    private readonly List<CryptoTrade> _recentTrades;
    private readonly object _tradesLock = new object();

    // Configuration
    private const int SNAPSHOT_INTERVAL_MINUTES = 10;
    private const int MAX_TRADES_BUFFER = 1000;
    private const int RECONNECT_DELAY_MS = 5000;

    // Current price tracking
    private decimal _currentPrice = 0;
    private decimal _highPrice = 0;
    private decimal _lowPrice = decimal.MaxValue;
    private long _totalTrades = 0;

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

    private async Task RunCryptoMonitoring(CancellationToken stoppingToken)
    {
        try
        {
            _logger.LogInformation("Connecting to Binance WebSocket...");

            _webSocket = new ClientWebSocket();
            await _webSocket.ConnectAsync(_binanceWebSocketUri, stoppingToken);

            _logger.LogInformation("Connected to Binance WebSocket - Monitoring BTC/USDT");

            // Start snapshot timer
            var snapshotTask = TakePeriodicSnapshots(stoppingToken);

            // Process incoming messages
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
            _logger.LogError(ex, "Error in crypto monitoring");
        }
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

    private void ProcessTradeMessage(string message)
    {
        try
        {
            var trade = JsonSerializer.Deserialize<BinanceTradeMessage>(message);
            if (trade != null)
            {
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
                BroadcastCurrentPriceAsync(_currentPrice).Wait();
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error processing trade message");
        }
    }

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

        // Reset interval stats
        _highPrice = _currentPrice;
        _lowPrice = _currentPrice;
        _totalTrades = 0;
        _lastSnapshotTime = now;

        // Broadcast snapshot to clients
        BroadcastSnapshotAsync(snapshot).Wait();
    }

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

    public bool IsRunning => _isRunning;
}

/// <summary>
/// Binance trade message format
/// </summary>
public class BinanceTradeMessage
{
    public string e { get; set; } = string.Empty; // Event type
    public long E { get; set; } // Event time
    public string s { get; set; } = string.Empty; // Symbol
    public string p { get; set; } = string.Empty; // Price
    public string q { get; set; } = string.Empty; // Quantity
    public long T { get; set; } // Trade time
}
