namespace PingService.Models;

/// <summary>
/// Represents a geographic coordinate with its occurrence count
/// </summary>
public class CoordinatePing
{
    public double Latitude { get; set; }
    public double Longitude { get; set; }
    public long Count { get; set; }
    public DateTime LastSeen { get; set; }

    public string CoordinateKey => $"{Latitude},{Longitude}";

    public CoordinatePing(double latitude, double longitude, long count = 1)
    {
        Latitude = latitude;
        Longitude = longitude;
        Count = count;
        LastSeen = DateTime.UtcNow;
    }
}

/// <summary>
/// Update message sent to clients via SignalR
/// </summary>
public class PingUpdate
{
    public double Latitude { get; set; }
    public double Longitude { get; set; }
    public long Count { get; set; }
    public DateTime Timestamp { get; set; }

    public PingUpdate(double latitude, double longitude, long count)
    {
        Latitude = latitude;
        Longitude = longitude;
        Count = count;
        Timestamp = DateTime.UtcNow;
    }
}

/// <summary>
/// Statistics about the ping generation system
/// </summary>
public class PingStats
{
    public long TotalPingsGenerated { get; set; }
    public int UniqueCoordinates { get; set; }
    public double PingsPerSecond { get; set; }
    public bool IsPaused { get; set; }
    public DateTime StartTime { get; set; }
    public TimeSpan Uptime { get; set; }
    public long MemoryUsageMB { get; set; }
}
