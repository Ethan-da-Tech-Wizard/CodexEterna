using Microsoft.AspNetCore.Mvc;
using PingService.Models;
using PingService.Services;

namespace PingService.Controllers;

/// <summary>
/// REST API for controlling ping generation and querying coordinate data
/// </summary>
[ApiController]
[Route("api/[controller]")]
public class PingController : ControllerBase
{
    private readonly PingGeneratorService _pingService;
    private readonly ILogger<PingController> _logger;

    public PingController(
        PingGeneratorService pingService,
        ILogger<PingController> logger)
    {
        _pingService = pingService;
        _logger = logger;
    }

    /// <summary>
    /// Get current system statistics
    /// </summary>
    [HttpGet("stats")]
    public ActionResult<PingStats> GetStats()
    {
        return Ok(_pingService.GetCurrentStats());
    }

    /// <summary>
    /// Get top N coordinates by occurrence count
    /// </summary>
    [HttpGet("top")]
    public ActionResult<IEnumerable<CoordinatePing>> GetTopCoordinates([FromQuery] int count = 100)
    {
        if (count < 1 || count > 10000)
            return BadRequest("Count must be between 1 and 10000");

        return Ok(_pingService.GetTopCoordinates(count));
    }

    /// <summary>
    /// Search for coordinates matching a pattern
    /// </summary>
    [HttpGet("search")]
    public ActionResult<IEnumerable<CoordinatePing>> SearchCoordinates(
        [FromQuery] string pattern,
        [FromQuery] int limit = 100)
    {
        if (string.IsNullOrWhiteSpace(pattern))
            return BadRequest("Pattern is required");

        if (limit < 1 || limit > 10000)
            return BadRequest("Limit must be between 1 and 10000");

        return Ok(_pingService.SearchCoordinates(pattern, limit));
    }

    /// <summary>
    /// Get count for a specific coordinate
    /// </summary>
    [HttpGet("coordinate")]
    public ActionResult<CoordinatePing> GetCoordinate(
        [FromQuery] double lat,
        [FromQuery] double lon)
    {
        var ping = _pingService.GetCoordinate(lat, lon);

        if (ping == null)
            return NotFound(new { message = "Coordinate not found", latitude = lat, longitude = lon });

        return Ok(ping);
    }

    /// <summary>
    /// Get filtered coordinates with advanced filtering options
    /// </summary>
    [HttpGet("filter")]
    public ActionResult<IEnumerable<CoordinatePing>> GetFilteredCoordinates(
        [FromQuery] double? minLat = null,
        [FromQuery] double? maxLat = null,
        [FromQuery] double? minLon = null,
        [FromQuery] double? maxLon = null,
        [FromQuery] long? minCount = null,
        [FromQuery] long? maxCount = null,
        [FromQuery] int? lastSeenMinutes = null,
        [FromQuery] string? hemisphere = null,
        [FromQuery] string sortBy = "count",
        [FromQuery] bool ascending = false,
        [FromQuery] int limit = 100)
    {
        if (limit < 1 || limit > 10000)
            return BadRequest("Limit must be between 1 and 10000");

        var results = _pingService.GetFilteredCoordinates(
            minLat, maxLat, minLon, maxLon, minCount, maxCount,
            lastSeenMinutes, hemisphere, sortBy, ascending, limit);

        return Ok(results);
    }

    /// <summary>
    /// Get coordinates by geographic region
    /// </summary>
    [HttpGet("region/{regionName}")]
    public ActionResult<IEnumerable<CoordinatePing>> GetCoordinatesByRegion(
        string regionName,
        [FromQuery] int limit = 100)
    {
        if (limit < 1 || limit > 10000)
            return BadRequest("Limit must be between 1 and 10000");

        var validRegions = new[] { "north_america", "south_america", "europe", "africa", "asia", "oceania" };
        if (!validRegions.Contains(regionName.ToLower()))
            return BadRequest($"Invalid region. Valid regions: {string.Join(", ", validRegions)}");

        var results = _pingService.GetCoordinatesByRegion(regionName, limit);
        return Ok(results);
    }

    /// <summary>
    /// Get aggregate statistics grouped by different dimensions
    /// </summary>
    [HttpGet("aggregate")]
    public ActionResult<Dictionary<string, object>> GetAggregateStats(
        [FromQuery] string groupBy = "hemisphere")
    {
        var validGroupings = new[] { "hemisphere", "quadrant", "count_range" };
        if (!validGroupings.Contains(groupBy.ToLower()))
            return BadRequest($"Invalid groupBy. Valid options: {string.Join(", ", validGroupings)}");

        var stats = _pingService.GetAggregateStats(groupBy);
        return Ok(new
        {
            groupBy = groupBy,
            stats = stats,
            timestamp = DateTime.UtcNow
        });
    }

    /// <summary>
    /// Start ping generation (requires manual confirmation from user)
    /// </summary>
    [HttpPost("start")]
    public IActionResult Start()
    {
        if (_pingService.IsRunning)
            return BadRequest(new { message = "Ping generation is already running", status = "running" });

        _pingService.Start();
        _logger.LogInformation("Ping generation STARTED via API - Data collection initiated");

        return Ok(new {
            message = "Ping generation started - System is now collecting 20,000 pings/second",
            status = "running",
            warning = "Large amounts of data will be collected. Use STOP to cease immediately."
        });
    }

    /// <summary>
    /// Stop ping generation immediately (ceases all operations)
    /// </summary>
    [HttpPost("stop")]
    public IActionResult Stop()
    {
        if (!_pingService.IsRunning)
            return BadRequest(new { message = "Ping generation is not running", status = "stopped" });

        _pingService.Stop();
        _logger.LogInformation("Ping generation STOPPED via API - All operations ceased");

        return Ok(new {
            message = "Ping generation stopped - All data collection ceased immediately",
            status = "stopped"
        });
    }

    /// <summary>
    /// Pause ping generation
    /// </summary>
    [HttpPost("pause")]
    public IActionResult Pause()
    {
        if (!_pingService.IsRunning)
            return BadRequest(new { message = "Cannot pause - system is not running" });

        if (_pingService.IsPaused)
            return BadRequest(new { message = "Already paused" });

        _pingService.Pause();
        _logger.LogInformation("Ping generation paused via API");

        return Ok(new { message = "Ping generation paused", status = "paused" });
    }

    /// <summary>
    /// Resume ping generation
    /// </summary>
    [HttpPost("resume")]
    public IActionResult Resume()
    {
        if (!_pingService.IsPaused)
            return BadRequest(new { message = "Not paused" });

        _pingService.Resume();
        _logger.LogInformation("Ping generation resumed via API");

        return Ok(new { message = "Ping generation resumed", status = "running" });
    }

    /// <summary>
    /// Toggle pause/resume
    /// </summary>
    [HttpPost("toggle")]
    public IActionResult Toggle()
    {
        if (_pingService.IsPaused)
        {
            _pingService.Resume();
            return Ok(new { message = "Resumed", status = "running" });
        }
        else
        {
            _pingService.Pause();
            return Ok(new { message = "Paused", status = "paused" });
        }
    }

    /// <summary>
    /// Reset all counters and data
    /// </summary>
    [HttpPost("reset")]
    public IActionResult Reset()
    {
        _pingService.Reset();
        _logger.LogInformation("Ping generation reset via API");

        return Ok(new { message = "System reset", status = "running" });
    }

    /// <summary>
    /// Get all unique coordinates (for comprehensive mapping)
    /// </summary>
    [HttpGet("all")]
    public ActionResult<IEnumerable<CoordinatePing>> GetAllCoordinates([FromQuery] int limit = 100000)
    {
        if (limit < 1 || limit > 1000000)
            return BadRequest("Limit must be between 1 and 1,000,000");

        var results = _pingService.GetAllCoordinates().Take(limit);
        return Ok(results);
    }

    /// <summary>
    /// Health check endpoint
    /// </summary>
    [HttpGet("health")]
    public IActionResult Health()
    {
        var stats = _pingService.GetCurrentStats();
        return Ok(new
        {
            status = "healthy",
            isRunning = _pingService.IsRunning,
            isPaused = stats.IsPaused,
            uptime = stats.Uptime.ToString(),
            pingsPerSecond = stats.PingsPerSecond,
            totalPings = stats.TotalPingsGenerated,
            uniqueCoordinates = stats.UniqueCoordinates
        });
    }
}
