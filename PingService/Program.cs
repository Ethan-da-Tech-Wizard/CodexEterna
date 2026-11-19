// ==============================================================================
// Program: Program.cs
// Programmer: Ethan-da-Tech-Wizard
// Last Modified: November 18, 2026
// Purpose: Application bootstrap, dependency injection composition root, and HTTP
//          middleware pipeline configuration for the CodexEterna real-time data
//          streaming backend service.
// ==============================================================================
// Namespaces for the SignalR hub and the two background services registered below.
// (ImplicitUsings in the project supplies the System/ASP.NET namespaces.)
using PingService.Hubs;
using PingService.Services;

// Step 1: Initialize ASP.NET Core application builder and configuration
// Top-level statements: this file is the whole composition root, with no Main method.
var builder = WebApplication.CreateBuilder(args);

// Add services to the container
// Step 2: Register REST controllers and configure high-throughput SignalR options
// MVC controllers (PingController, CryptoController) discovered by attribute routing.
builder.Services.AddControllers();
builder.Services.AddSignalR(options =>
{
    // Detailed hub exceptions are sent to clients; useful while developing but can leak
    // internals, so consider disabling in production. 102400 bytes caps incoming message size.
    options.EnableDetailedErrors = true;
    options.MaximumReceiveMessageSize = 102400; // 100 KB
});

// Add PingGeneratorService as a singleton hosted service
// Step 3: Register background singleton hosted services for streaming data collection
// Each service is registered twice on purpose: once as a singleton so controllers can inject
// the concrete type, and once as a hosted service resolving that SAME instance. Registering
// only AddHostedService would create a second, separate instance.
builder.Services.AddSingleton<PingGeneratorService>();
builder.Services.AddHostedService<PingGeneratorService>(provider =>
    provider.GetRequiredService<PingGeneratorService>());

// Add CryptoService as a singleton hosted service
// Same dual-registration pattern for the Binance monitor.
builder.Services.AddSingleton<CryptoService>();
builder.Services.AddHostedService<CryptoService>(provider =>
    provider.GetRequiredService<CryptoService>());

// Add Swagger for API documentation
// Swagger/OpenAPI generation. The UI is only mapped in Development (see below).
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
// Restricted policy named "AllowConfiguredOrigins": only the origins listed (comma separated) in the
// CORS_ALLOWED_ORIGINS environment variable may call the API from a browser. The default is the
// dashboard's own origin on localhost:5000. A wildcard entry is rejected at startup because the
// SignalR hub needs credentials, which cannot be combined with "any origin". CORS is enforced by
// browsers only; it is not an authentication mechanism.
var allowedOrigins = (Environment.GetEnvironmentVariable("CORS_ALLOWED_ORIGINS")
        ?? "http://localhost:5000,http://127.0.0.1:5000")
    .Split(',', StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries);
if (allowedOrigins.Contains("*"))
{
    throw new InvalidOperationException("CORS_ALLOWED_ORIGINS must list explicit origins; '*' is not allowed");
}
builder.Services.AddCors(options =>
{
    options.AddPolicy("AllowConfiguredOrigins", policy =>
    {
        policy
            .WithOrigins(allowedOrigins)
            .AllowAnyMethod()
            .AllowAnyHeader()
            .AllowCredentials();
    });
});

// Step 4: Construct the web application pipeline
// Freeze service registration and build the request pipeline.
var app = builder.Build();

// Configure the HTTP request pipeline
// Swagger is limited to Development; the Docker image runs Production, so it is off there.
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI(c =>
    {
        c.SwaggerEndpoint("/swagger/v1/swagger.json", "Ping Service API v1");
        c.RoutePrefix = "swagger";
    });
}

// Middleware order matters: CORS before routing so preflight requests are answered.
app.UseCors("AllowConfiguredOrigins");

// Serve wwwroot/index.html as the default document and other static dashboard assets.
app.UseDefaultFiles();
app.UseStaticFiles();

app.UseRouting();

// Step 5: Map controller routes and SignalR WebSocket hub endpoints
// Attribute-routed REST endpoints; the SignalR hub below carries the live WebSocket stream.
app.MapControllers();
app.MapHub<PingHub>("/hubs/ping");

// Root endpoint
// Send visitors of the root URL to the dashboard page.
app.MapGet("/", () => Results.Redirect("/index.html"));

// API info endpoint
// Static service description for clients; the version string here is hard-coded text.
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

// Startup banner. The URLs are informational and assume the default port 5000.
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

// Blocks until shutdown (Ctrl+C / SIGTERM), then hosted services are stopped.
app.Run();
