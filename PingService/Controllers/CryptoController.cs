// Program: CodexEterna - CryptoController.cs
// Programmer: Ethan-da-Tech-Wizard (written with Claude, an AI assistant)
// Last Modified: 2026-11-18
// Purpose: REST controller to start and stop crypto monitoring and to read its statistics and stored snapshots.
// --- Imports ---
using Microsoft.AspNetCore.Mvc;
using PingService.Models;
using PingService.Services;

namespace PingService.Controllers;

/// <summary>
/// REST API for controlling crypto monitoring and querying crypto data
/// </summary>
[ApiController]
[Route("api/[controller]")]
// --- Controller: routes begin with api/crypto (the controller name) ---
public class CryptoController : ControllerBase
{
    // Dependencies are injected by ASP.NET and kept read-only.
    private readonly CryptoService _cryptoService;
    private readonly ILogger<CryptoController> _logger;

    public CryptoController(
        CryptoService cryptoService,
        ILogger<CryptoController> logger)
    {
        // Store the injected services for use by the action methods.
        _cryptoService = cryptoService;
        _logger = logger;
    }

    /// <summary>
    /// Start crypto monitoring (requires manual confirmation from user)
    /// </summary>
    [HttpPost("start")]
    public IActionResult Start()
    {
        // Refuse a second start so only one connection is open at a time.
        if (_cryptoService.IsRunning)
            return BadRequest(new { message = "Crypto monitoring is already running", status = "running" });

        // Begin collecting; this does not wait for the work to finish.
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
    [HttpPost("stop")]
    public async Task<IActionResult> Stop()
    {
        // Nothing to stop: report that as a client error.
        if (!_cryptoService.IsRunning)
            return BadRequest(new { message = "Crypto monitoring is not running", status = "stopped" });

        // Wait until the service has fully shut down before answering.
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
    [HttpGet("stats")]
    public ActionResult<CryptoStats> GetStats()
    {
        // Return a live statistics object serialized as JSON.
        return Ok(_cryptoService.GetCurrentStats());
    }

    /// <summary>
    /// Get all crypto snapshots
    /// </summary>
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
        // Reject reversed ranges before querying.
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
        // Reuse the statistics object to build a small health summary.
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
