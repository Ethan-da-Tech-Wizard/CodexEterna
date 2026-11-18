// ==============================================================================
// Program: CryptoController.cs
// Programmer: Ethan-da-Tech-Wizard
// Last Modified: November 18, 2026
// Purpose: REST API controller providing operational control and telemetry query
//          endpoints for the Binance cryptocurrency price ingestion engine. Exposes
//          manual lifecycle management (start/stop) and snapshot historical retrieval.
// ==============================================================================
using Microsoft.AspNetCore.Mvc;
using PingService.Models;
using PingService.Services;

namespace PingService.Controllers;

/// <summary>
/// REST API for controlling crypto monitoring and querying crypto data
/// </summary>
[ApiController]
[Route("api/[controller]")]
public class CryptoController : ControllerBase
{
    private readonly CryptoService _cryptoService;
    private readonly ILogger<CryptoController> _logger;

    public CryptoController(
        CryptoService cryptoService,
        ILogger<CryptoController> logger)
    {
        _cryptoService = cryptoService;
        _logger = logger;
    }

    /// <summary>
    /// Start crypto monitoring (requires manual confirmation from user)
    /// </summary>
    // Step 1: Validate system state and initiate cryptocurrency telemetry collection
    [HttpPost("start")]
    public IActionResult Start()
    {
        if (_cryptoService.IsRunning)
            return BadRequest(new { message = "Crypto monitoring is already running", status = "running" });

        _cryptoService.Start();
        _logger.LogInformation("Crypto monitoring STARTED via API - Connecting to Binance WebSocket");

        return Ok(new {
            message = "Crypto monitoring started - Connected to Binance BTC/USDT stream",
            status = "running",
            info = "Snapshots will be taken every 10 minutes and timestamped for historical analysis"
        });
    }

    /// <summary>
    /// Stop crypto monitoring immediately (ceases all operations)
    /// </summary>
    // Step 2: Gracefully terminate active WebSocket connections and background collection loops
    [HttpPost("stop")]
    public async Task<IActionResult> Stop()
    {
        if (!_cryptoService.IsRunning)
            return BadRequest(new { message = "Crypto monitoring is not running", status = "stopped" });

        await _cryptoService.StopAsync();
        _logger.LogInformation("Crypto monitoring STOPPED via API - Disconnected from Binance");

        return Ok(new {
            message = "Crypto monitoring stopped - All operations ceased immediately",
            status = "stopped"
        });
    }

    /// <summary>
    /// Get current crypto statistics
    /// </summary>
    // Step 3: Query in-memory aggregated statistics (high, low, latest spot price, uptime)
    [HttpGet("stats")]
    public ActionResult<CryptoStats> GetStats()
    {
        return Ok(_cryptoService.GetCurrentStats());
    }

    /// <summary>
    /// Get all crypto snapshots
    /// </summary>
    // Step 4: Retrieve historical 10-minute snapshot records for external analytics
    [HttpGet("snapshots")]
    public ActionResult<IEnumerable<CryptoSnapshot>> GetAllSnapshots()
    {
        return Ok(_cryptoService.GetAllSnapshots());
    }

    /// <summary>
    /// Get crypto snapshots by date range
    /// </summary>
    [HttpGet("snapshots/range")]
    public ActionResult<IEnumerable<CryptoSnapshot>> GetSnapshotsByDateRange(
        [FromQuery] DateTime startDate,
        [FromQuery] DateTime endDate)
    {
        if (startDate > endDate)
            return BadRequest(new { message = "Start date must be before end date" });

        var results = _cryptoService.GetSnapshotsByDateRange(startDate, endDate);
        return Ok(results);
    }

    /// <summary>
    /// Health check endpoint
    /// </summary>
    [HttpGet("health")]
    public IActionResult Health()
    {
        var stats = _cryptoService.GetCurrentStats();
        return Ok(new
        {
            status = "healthy",
            isRunning = stats.IsRunning,
            symbol = stats.Symbol,
            currentPrice = stats.CurrentPrice,
            totalSnapshots = stats.TotalSnapshots,
            uptime = stats.Uptime.ToString()
        });
    }
}
