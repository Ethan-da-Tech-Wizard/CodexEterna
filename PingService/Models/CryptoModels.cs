// Program: CodexEterna - CryptoModels.cs
// Programmer: Ethan-da-Tech-Wizard (written with Claude, an AI assistant)
// Last Modified: 2026-11-18
// Purpose: Data classes for crypto monitoring: periodic price snapshots, individual trades, and live monitoring statistics.
namespace PingService.Models;

/// <summary>
/// Represents a 10-minute snapshot of crypto data
/// </summary>
// --- Snapshot record ---
public class CryptoSnapshot
{
    // Unique identifier for this snapshot; defaults to empty text so it is never null.
    public string Id { get; set; } = string.Empty;
    public string Symbol { get; set; } = string.Empty;
    public DateTime Timestamp { get; set; }
    // Price at the end of the interval (decimal avoids floating-point rounding errors with money).
    public decimal Price { get; set; }
    public decimal HighPrice { get; set; }
    public decimal LowPrice { get; set; }
    // Number of trades seen during the interval.
    public long TotalTrades { get; set; }
    // Length of the interval this snapshot covers, in minutes.
    public int IntervalMinutes { get; set; }
}

/// <summary>
/// Represents a single crypto trade
/// </summary>
// --- Individual trade ---
public class CryptoTrade
{
    public string Symbol { get; set; } = string.Empty;
    public decimal Price { get; set; }
    // Amount of the asset traded.
    public decimal Quantity { get; set; }
    public DateTime Timestamp { get; set; }
}

/// <summary>
/// Current crypto monitoring statistics
/// </summary>
// --- Live statistics ---
public class CryptoStats
{
    // True while the monitor is connected and collecting.
    public bool IsRunning { get; set; }
    public string Symbol { get; set; } = string.Empty;
    public decimal CurrentPrice { get; set; }
    public decimal HighPrice { get; set; }
    public decimal LowPrice { get; set; }
    // How many snapshots are stored so far.
    public int TotalSnapshots { get; set; }
    public DateTime LastSnapshotTime { get; set; }
    public TimeSpan Uptime { get; set; }
}
