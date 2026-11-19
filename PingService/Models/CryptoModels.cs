// ==============================================================================
// Program: CryptoModels.cs
// Programmer: Ethan-da-Tech-Wizard
// Last Modified: November 18, 2026
// Purpose: Data models defining cryptocurrency trade ticks, periodic 10-minute
//          aggregate snapshots, and runtime engine monitoring statistics for the
//          Binance market data pipeline.
// ==============================================================================
// File-scoped namespace for the crypto data models.
namespace PingService.Models;

/// <summary>
/// Represents a 10-minute snapshot of crypto data
/// </summary>
// Step 1: Snapshot model representing OHLC-style price windows
// NOTE: this class is mutable (public setters); it is only treated as read-only by convention
// once CryptoService has stored it.
// A snapshot summarises one interval (default 10 minutes) of the BTC/USDT feed.
public class CryptoSnapshot
{
    // Unique id (GUID string) assigned when the snapshot is taken.
    public string Id { get; set; } = string.Empty;
    // Trading pair, e.g. BTCUSDT.
    public string Symbol { get; set; } = string.Empty;
    // UTC time the snapshot was captured.
    public DateTime Timestamp { get; set; }
    // Last traded price at capture time. decimal avoids binary floating-point rounding for money.
    public decimal Price { get; set; }
    // Highest price seen during the interval.
    public decimal HighPrice { get; set; }
    // Lowest price seen during the interval.
    public decimal LowPrice { get; set; }
    // Number of trades received during the interval.
    public long TotalTrades { get; set; }
    // Length of the interval this snapshot covers.
    public int IntervalMinutes { get; set; }
}

/// <summary>
/// Represents a single crypto trade
/// </summary>
// Step 2: Atomic trade tick model received from Binance WebSocket stream
// One trade as parsed from the Binance stream.
public class CryptoTrade
{
    public string Symbol { get; set; } = string.Empty;
    public decimal Price { get; set; }
    // Amount of the base asset (BTC) traded.
    public decimal Quantity { get; set; }
    public DateTime Timestamp { get; set; }
}

/// <summary>
/// Current crypto monitoring statistics
/// </summary>
// Step 3: Runtime operational metrics tracking feed health and extrema
// Live monitor status returned by /api/crypto/stats.
public class CryptoStats
{
    // True while the monitor has been started and not stopped.
    public bool IsRunning { get; set; }
    public string Symbol { get; set; } = string.Empty;
    public decimal CurrentPrice { get; set; }
    public decimal HighPrice { get; set; }
    public decimal LowPrice { get; set; }
    // Number of snapshots stored in memory (they are lost on restart).
    public int TotalSnapshots { get; set; }
    // UTC time of the most recent snapshot, or the start time if none yet.
    public DateTime LastSnapshotTime { get; set; }
    public TimeSpan Uptime { get; set; }
}
