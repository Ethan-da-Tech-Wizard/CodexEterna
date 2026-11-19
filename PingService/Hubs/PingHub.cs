// ==============================================================================
// Program: PingHub.cs
// Programmer: Ethan-da-Tech-Wizard
// Last Modified: November 18, 2026
// Purpose: SignalR bidirectional WebSocket hub orchestrating low-latency multicast
//          broadcasts of coordinate frequency updates and system telemetry metrics
//          to all active dashboard client connections.
// ==============================================================================
// SignalR provides the Hub base class and the Clients proxy used for server-to-browser pushes.
using Microsoft.AspNetCore.SignalR;
using PingService.Models;

// File-scoped namespace for hubs.
namespace PingService.Hubs;

/// <summary>
/// SignalR Hub for broadcasting real-time coordinate ping updates to connected clients
/// </summary>
// The hub itself holds no state. The background services push data through
// IHubContext<PingHub>, so clients mostly just connect and listen; the hub methods below
// are optional entry points that clients (or server code) can invoke.
public class PingHub : Hub
{
    // Logger injected by DI.
    private readonly ILogger<PingHub> _logger;

    public PingHub(ILogger<PingHub> logger)
    {
        _logger = logger;
    }

    // Step 1: Handle and audit new client WebSocket connections
    public override async Task OnConnectedAsync()
    {
        _logger.LogInformation($"Client connected: {Context.ConnectionId}");
        // Always call the base implementation so SignalR completes its own connection setup.
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
    // Currently only logs the request: it does not send anything back. Stats are pushed
    // automatically every second by PingGeneratorService. (async without await compiles with
    // a warning.)
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
        // "ReceivePingUpdate" is the client-side handler name; it must match the JavaScript
        // connection.on(...) registration exactly.
        await Clients.All.SendAsync("ReceivePingUpdate", update);
    }

    /// <summary>
    /// Broadcast statistics to all connected clients
    /// </summary>
    public async Task BroadcastStats(PingStats stats)
    {
        // Same pattern; the PingGeneratorService uses this same method name for its periodic push.
        await Clients.All.SendAsync("ReceiveStats", stats);
    }
}
