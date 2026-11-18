// ==============================================================================
// Program: CryptoModels.cs
// Programmer: Ethan-da-Tech-Wizard
// Last Modified: November 18, 2026
// Purpose: Data models defining cryptocurrency trade ticks, periodic 10-minute
//          aggregate snapshots, and runtime engine monitoring statistics for the
//          Binance market data pipeline.
// ==============================================================================
namespace PingService.Models;

/// <summary>
/// Represents a 10-minute snapshot of crypto data
/// </summary>
// Step 1: Immutable snapshot model representing OHLC-style price windows
public class CryptoSnapshot
{
    public string Id { get; set; } = string.Empty;
    public string Symbol { get; set; } = string.Empty;
    public DateTime Timestamp { get; set; }
    public decimal Price { get; set; }
    public decimal HighPrice { get; set; }
    public decimal LowPrice { get; set; }
    public long TotalTrades { get; set; }
    public int IntervalMinutes { get; set; }
}

/// <summary>
/// Represents a single crypto trade
/// </summary>
// Step 2: Atomic trade tick model received from Binance WebSocket stream
public class CryptoTrade
{
    public string Symbol { get; set; } = string.Empty;
    public decimal Price { get; set; }
    public decimal Quantity { get; set; }
    public DateTime Timestamp { get; set; }
}

/// <summary>
/// Current crypto monitoring statistics
/// </summary>
// Step 3: Runtime operational metrics tracking feed health and extrema
public class CryptoStats
{
    public bool IsRunning { get; set; }
    public string Symbol { get; set; } = string.Empty;
    public decimal CurrentPrice { get; set; }
    public decimal HighPrice { get; set; }
    public decimal LowPrice { get; set; }
    public int TotalSnapshots { get; set; }
    public DateTime LastSnapshotTime { get; set; }
    public TimeSpan Uptime { get; set; }
}
