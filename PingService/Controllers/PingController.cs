// ==============================================================================
// Program: PingController.cs
// Programmer: Ethan-da-Tech-Wizard
// Last Modified: November 18, 2026
// Purpose: High-throughput REST API controller exposing management operations and
//          statistical queries for the simulated geospatial ping generation pipeline.
//          Supports real-time frequency tuning, geographic search, and occurrence ranking.
// ==============================================================================
// MVC attributes and result helpers. Other namespaces come from ImplicitUsings.
using Microsoft.AspNetCore.Mvc;
using PingService.Models;
using PingService.Services;

namespace PingService.Controllers;

/// <summary>
/// REST API for controlling ping generation and querying coordinate data
/// </summary>
// [ApiController] gives automatic 400s for invalid binding; the route resolves to /api/ping.
[ApiController]
[Route("api/[controller]")]
public class PingController : ControllerBase
{
    // The shared singleton generator (also running as a hosted service).
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
    // Step 1: Query global pipeline throughput and coordinate uniqueness statistics
    [HttpGet("stats")]
    // GET /api/ping/stats.
    public ActionResult<PingStats> GetStats()
    {
        return Ok(_pingService.GetCurrentStats());
    }

    /// <summary>
    /// Get top N coordinates by occurrence count
    /// </summary>
    // Step 2: Retrieve the top N most frequently generated coordinate pairs
    [HttpGet("top")]
    // GET /api/ping/top?count=N. The 10,000 cap bounds the response size and the sort cost.
    public ActionResult<IEnumerable<CoordinatePing>> GetTopCoordinates([FromQuery] int count = 100)
    {
        if (count < 1 || count > 10000)
            return BadRequest("Count must be between 1 and 10000");

        return Ok(_pingService.GetTopCoordinates(count));
    }

    /// <summary>
    /// Search for coordinates matching a pattern
    /// </summary>
    // Step 3: Perform prefix/substring pattern matching across cached coordinate keys
    [HttpGet("search")]
    // GET /api/ping/search?pattern=. Despite the step label (prefix/substring), the service does a
    // case-insensitive substring match against the "lat,lon" key text.
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
    // GET /api/ping/coordinate?lat=&lon=. Lookup is by exact key text, so the numbers must match
    // the stored 6-decimal values; 404 if never generated.
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
    // GET /api/ping/filter: all parameters are optional and combine with AND.
    // hemisphere: north/south/east/west/northeast/northwest/southeast/southwest.
    // sortBy: count (default), latitude, longitude, lastseen.
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
    // GET /api/ping/region/{name}. Regions are rough bounding boxes defined in the service, so
    // they overlap and include ocean areas. The name is checked against a whitelist first.
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
    // GET /api/ping/aggregate?groupBy=hemisphere|quadrant|count_range (case-insensitive).
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
    // POST /api/ping/start: begins generating (the service starts paused). 400 if already running.
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
    // POST /api/ping/stop: halts generation. Collected data is kept until Reset is called.
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
    // POST /api/ping/pause: temporary halt; only valid while running and not already paused.
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
    // POST /api/ping/resume: continues after a pause.
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
    // POST /api/ping/toggle: flips between paused and running in one call for a single UI button.
    // Note the service's Pause/Resume are no-ops unless the system was started first, yet this
    // endpoint still reports a new status.
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
    // POST /api/ping/reset: clears all stored coordinates and counters. The response's
    // "running" status is a fixed string and does not reflect the real state.
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
    // GET /api/ping/all: potentially very large (limit up to 1,000,000), unordered result.
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
    // GET /api/ping/health: also the target of the Docker HEALTHCHECK.
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
