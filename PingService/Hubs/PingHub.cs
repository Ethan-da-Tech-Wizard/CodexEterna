// ==============================================================================
// Program: PingHub.cs
// Programmer: Ethan-da-Tech-Wizard
// Last Modified: November 18, 2026
// Purpose: SignalR bidirectional WebSocket hub orchestrating low-latency multicast
//          broadcasts of coordinate frequency updates and system telemetry metrics
//          to all active dashboard client connections.
// ==============================================================================
using Microsoft.AspNetCore.SignalR;
using PingService.Models;

namespace PingService.Hubs;

/// <summary>
/// SignalR Hub for broadcasting real-time coordinate ping updates to connected clients
/// </summary>
public class PingHub : Hub
{
    private readonly ILogger<PingHub> _logger;

    public PingHub(ILogger<PingHub> logger)
    {
        _logger = logger;
    }

    // Step 1: Handle and audit new client WebSocket connections
    public override async Task OnConnectedAsync()
    {
        _logger.LogInformation($"Client connected: {Context.ConnectionId}");
        await base.OnConnectedAsync();
    }

    // Step 2: Safely deregister disconnected clients and clean up tracking contexts
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
        // The PingGeneratorService will handle broadcasting stats
    }

    /// <summary>
    /// Broadcast a ping update to all connected clients
    /// </summary>
    // Step 3: Multicast batch coordinate occurrence updates to connected observers
    public async Task BroadcastPingUpdate(PingUpdate update)
    {
        await Clients.All.SendAsync("ReceivePingUpdate", update);
    }

    /// <summary>
    /// Broadcast statistics to all connected clients
    /// </summary>
    public async Task BroadcastStats(PingStats stats)
    {
        await Clients.All.SendAsync("ReceiveStats", stats);
    }
}
