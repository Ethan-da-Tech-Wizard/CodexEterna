// ==============================================================================
// Program: CoordinatePing.cs
// Programmer: Ethan-da-Tech-Wizard
// Last Modified: November 18, 2026
// Purpose: Data transfer objects (DTOs) and domain entity definitions representing
//          geospatial coordinate frequencies, batch telemetry messages, and system
//          throughput health metrics.
// ==============================================================================
// File-scoped namespace: applies to every type in this file.
namespace PingService.Models;

/// <summary>
/// Represents a geographic coordinate with its occurrence count
/// </summary>
// Step 1: Thread-safe data model tracking coordinate occurrences and timestamps
// NOTE: despite the step label above, instances are NOT internally thread-safe. The generator
// mutates Count/LastSeen from several threads via ConcurrentDictionary.AddOrUpdate, so counts
// are approximate under heavy contention.
public class CoordinatePing
{
    // Latitude in degrees (-90 to 90), rounded to 6 decimal places by the generator.
    public double Latitude { get; set; }
    // Longitude in degrees (-180 to 180), rounded to 6 decimal places by the generator.
    public double Longitude { get; set; }
    // How many times this exact coordinate pair has been generated.
    public long Count { get; set; }
    // UTC time of the most recent occurrence.
    public DateTime LastSeen { get; set; }

    // Dictionary/search key in the form "lat,lon". Uses the current culture's number
    // formatting, so a culture with a decimal comma would change the key text.
    public string CoordinateKey => $"{Latitude},{Longitude}";

    // Initialises a new coordinate; LastSeen is set to the creation time.
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
// Step 2: Lightweight wire DTO for low-overhead client transmission via SignalR
// Immutable-by-convention copy of a coordinate's count sent to browsers. Kept separate from
// CoordinatePing so the wire format stays small and independent of server-side state.
public class PingUpdate
{
    public double Latitude { get; set; }
    public double Longitude { get; set; }
    public long Count { get; set; }
    // UTC time the update was created on the server.
    public DateTime Timestamp { get; set; }

    // Captures the count at creation time; later increments do not change this object.
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
// Step 3: Aggregated system diagnostics and throughput metrics
// Snapshot of generator health, broadcast every second and returned by /api/ping/stats.
public class PingStats
{
    // Total pings since start or last Reset.
    public long TotalPingsGenerated { get; set; }
    // Number of distinct coordinate keys currently stored (memory grows with this).
    public int UniqueCoordinates { get; set; }
    // Average rate = total / elapsed stopwatch time (not an instantaneous rate).
    public double PingsPerSecond { get; set; }
    // True while generation is paused or stopped.
    public bool IsPaused { get; set; }
    // UTC time of the last start or reset.
    public DateTime StartTime { get; set; }
    // Time the generator stopwatch has been running.
    public TimeSpan Uptime { get; set; }
    // Managed heap size in MB from GC.GetTotalMemory (an estimate, not process RSS).
    public long MemoryUsageMB { get; set; }
}
