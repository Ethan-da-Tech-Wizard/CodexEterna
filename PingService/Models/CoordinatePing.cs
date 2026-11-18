// Program: CodexEterna - CoordinatePing.cs
// Programmer: Ethan-da-Tech-Wizard (written with Claude, an AI assistant)
// Last Modified: 2026-11-18
// Purpose: Data classes for a counted geographic coordinate, the update message pushed to browsers, and overall ping statistics.
namespace PingService.Models;

/// <summary>
/// Represents a geographic coordinate with its occurrence count
/// </summary>
// --- Coordinate record ---
public class CoordinatePing
{
    // Position in decimal degrees; latitude is north/south, longitude is east/west.
    public double Latitude { get; set; }
    public double Longitude { get; set; }
    // How many pings have been seen at exactly this coordinate.
    public long Count { get; set; }
    // UTC time of the most recent ping here.
    public DateTime LastSeen { get; set; }

    // Read-only text key (latitude,longitude) used to look the coordinate up in dictionaries.
    public string CoordinateKey => $"{Latitude},{Longitude}";

    // Creates a coordinate entry; the count defaults to one and LastSeen is stamped with the current UTC time.
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
// --- Real-time update message ---
public class PingUpdate
{
    public double Latitude { get; set; }
    public double Longitude { get; set; }
    public long Count { get; set; }
    // When this update was created (UTC).
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
// --- System statistics ---
public class PingStats
{
    // Running total of pings produced since start or last reset.
    public long TotalPingsGenerated { get; set; }
    // Number of distinct coordinates currently stored.
    public int UniqueCoordinates { get; set; }
    // Measured generation rate.
    public double PingsPerSecond { get; set; }
    // True while generation is temporarily paused.
    public bool IsPaused { get; set; }
    public DateTime StartTime { get; set; }
    public TimeSpan Uptime { get; set; }
    // Approximate process memory use, in megabytes.
    public long MemoryUsageMB { get; set; }
}
