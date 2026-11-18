// Program: CodexEterna - PingHub.cs
// Programmer: Ethan-da-Tech-Wizard (written with Claude, an AI assistant)
// Last Modified: 2026-11-18
// Purpose: SignalR hub that lets browsers connect for live ping updates and pushes updates and statistics to every connected client.
// --- Imports ---
using Microsoft.AspNetCore.SignalR;
using PingService.Models;

namespace PingService.Hubs;

/// <summary>
/// SignalR Hub for broadcasting real-time coordinate ping updates to connected clients
/// </summary>
// --- Hub ---
public class PingHub : Hub
{
    // Logger supplied by dependency injection.
    private readonly ILogger<PingHub> _logger;

    // Constructor: ASP.NET injects the logger automatically.
    public PingHub(ILogger<PingHub> logger)
    {
        _logger = logger;
    }

    // Called by SignalR whenever a browser connects; logs the connection id.
    public override async Task OnConnectedAsync()
    {
        _logger.LogInformation($"Client connected: {Context.ConnectionId}");
        await base.OnConnectedAsync();
    }

    // Called when a client leaves; the exception is non-null if the connection dropped unexpectedly.
    public override async Task OnDisconnectedAsync(Exception? exception)
    {
        _logger.LogInformation($"Client disconnected: {Context.ConnectionId}");
        await base.OnDisconnectedAsync(exception);
    }

    /// <summary>
    /// Client can request current stats
    /// </summary>
    public async Task RequestStats()
    {
        _logger.LogInformation($"Stats requested by {Context.ConnectionId}");
        // Intentionally logs only; the actual stats push happens elsewhere.
        // The PingGeneratorService will handle broadcasting stats
    }

    /// <summary>
    /// Broadcast a ping update to all connected clients
    /// </summary>
    public async Task BroadcastPingUpdate(PingUpdate update)
    {
        // Sends to every connected client; the text name must match the handler registered in the browser script.
        await Clients.All.SendAsync("ReceivePingUpdate", update);
    }

    /// <summary>
    /// Broadcast statistics to all connected clients
    /// </summary>
    public async Task BroadcastStats(PingStats stats)
    {
        // Same pattern for statistics, using the ReceiveStats handler name.
        await Clients.All.SendAsync("ReceiveStats", stats);
    }
}
