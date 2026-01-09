namespace PingService.Models;

/// <summary>
/// Represents a 10-minute snapshot of crypto data
/// </summary>
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
