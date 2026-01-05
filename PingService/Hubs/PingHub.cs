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

    public override async Task OnConnectedAsync()
    {
        _logger.LogInformation($"Client connected: {Context.ConnectionId}");
        await base.OnConnectedAsync();
    }

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
