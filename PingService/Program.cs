// Program: CodexEterna - Program.cs
// Programmer: Ethan-da-Tech-Wizard (written with Claude, an AI assistant)
// Last Modified: 2026-11-18
// Purpose: Application entry point: registers services, SignalR, Swagger and CORS, maps the routes and hub, and starts the web server.
// --- Imports ---
using PingService.Hubs;
using PingService.Services;

// --- Service registration ---
var builder = WebApplication.CreateBuilder(args);

// Add services to the container
builder.Services.AddControllers();
builder.Services.AddSignalR(options =>
{
    // Detailed errors help during development but should be turned off in production.
    options.EnableDetailedErrors = true;
    // Largest message a client may send to the hub.
    options.MaximumReceiveMessageSize = 102400; // 100 KB
});

// Add PingGeneratorService as a singleton hosted service
// Registered twice on purpose: once as a singleton so controllers can inject it, and once as a hosted service reusing that same instance so it also runs in the background.
builder.Services.AddSingleton<PingGeneratorService>();
builder.Services.AddHostedService<PingGeneratorService>(provider =>
    provider.GetRequiredService<PingGeneratorService>());

// Add CryptoService as a singleton hosted service
builder.Services.AddSingleton<CryptoService>();
builder.Services.AddHostedService<CryptoService>(provider =>
    provider.GetRequiredService<CryptoService>());

// Add Swagger for API documentation
// Swagger generates interactive API documentation.
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen(c =>
{
    c.SwaggerDoc("v1", new()
    {
        Title = "CodexEterna Data Pipeline API",
        Version = "v1",
        Description = "Real-time data collection: Coordinate pings (20k/sec) + Binance crypto monitoring + Sports data"
    });
});

// Add CORS for cross-origin requests
builder.Services.AddCors(options =>
{
    // Permissive CORS policy: any origin, method and header; narrow it for production.
    options.AddPolicy("AllowAll", builder =>
    {
        builder
            .AllowAnyOrigin()
            .AllowAnyMethod()
            .AllowAnyHeader();
    });
});

// --- Request pipeline ---
var app = builder.Build();

// Configure the HTTP request pipeline
if (app.Environment.IsDevelopment())
{
    // Swagger pages are exposed only in the Development environment.
    app.UseSwagger();
    app.UseSwaggerUI(c =>
    {
        c.SwaggerEndpoint("/swagger/v1/swagger.json", "Ping Service API v1");
        c.RoutePrefix = "swagger";
    });
}

// Order matters: CORS and static files run before routing.
app.UseCors("AllowAll");

app.UseDefaultFiles();
app.UseStaticFiles();

app.UseRouting();

app.MapControllers();
// Browsers connect to the live-update hub at this path.
app.MapHub<PingHub>("/hubs/ping");

// Root endpoint
app.MapGet("/", () => Results.Redirect("/index.html"));

// API info endpoint
// Simple JSON description of the service and its endpoints.
app.MapGet("/api/info", () => new
{
    service = "CodexEterna Data Pipeline",
    version = "2.0.0",
    description = "Multi-source real-time data collection platform",
    features = new[]
    {
        "Coordinate Ping Generation (20,000/sec)",
        "Binance Crypto Monitoring (BTC/USDT)",
        "Sports Data Collection (ESPN API)",
        "10-minute timestamped snapshots",
        "Manual start with confirmation required"
    },
    endpoints = new
    {
        dashboard = "/index.html",
        swagger = "/swagger",
        signalr = "/hubs/ping",
        pingApi = "/api/ping",
        cryptoApi = "/api/crypto",
        sportsService = "http://localhost:5001"
    }
});

// Startup banner printed to the log.
app.Logger.LogInformation("=======================================================");
app.Logger.LogInformation("CodexEterna Data Pipeline v2.0");
app.Logger.LogInformation("=======================================================");
app.Logger.LogInformation("Dashboard: http://localhost:5000");
app.Logger.LogInformation("Ping API: http://localhost:5000/api/ping");
app.Logger.LogInformation("Crypto API: http://localhost:5000/api/crypto");
app.Logger.LogInformation("SignalR Hub: http://localhost:5000/hubs/ping");
app.Logger.LogInformation("Swagger: http://localhost:5000/swagger");
app.Logger.LogInformation("=======================================================");
app.Logger.LogInformation("NOTE: All data collection requires MANUAL START");
app.Logger.LogInformation("Use dashboard buttons to begin data collection");
app.Logger.LogInformation("=======================================================");

// Start listening; this call blocks until the application shuts down.
app.Run();
