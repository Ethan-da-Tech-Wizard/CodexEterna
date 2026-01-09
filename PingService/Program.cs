using PingService.Hubs;
using PingService.Services;

var builder = WebApplication.CreateBuilder(args);

// Add services to the container
builder.Services.AddControllers();
builder.Services.AddSignalR(options =>
{
    options.EnableDetailedErrors = true;
    options.MaximumReceiveMessageSize = 102400; // 100 KB
});

// Add PingGeneratorService as a singleton hosted service
builder.Services.AddSingleton<PingGeneratorService>();
builder.Services.AddHostedService<PingGeneratorService>(provider =>
    provider.GetRequiredService<PingGeneratorService>());

// Add CryptoService as a singleton hosted service
builder.Services.AddSingleton<CryptoService>();
builder.Services.AddHostedService<CryptoService>(provider =>
    provider.GetRequiredService<CryptoService>());

// Add Swagger for API documentation
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
    options.AddPolicy("AllowAll", builder =>
    {
        builder
            .AllowAnyOrigin()
            .AllowAnyMethod()
            .AllowAnyHeader();
    });
});

var app = builder.Build();

// Configure the HTTP request pipeline
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI(c =>
    {
        c.SwaggerEndpoint("/swagger/v1/swagger.json", "Ping Service API v1");
        c.RoutePrefix = "swagger";
    });
}

app.UseCors("AllowAll");

app.UseDefaultFiles();
app.UseStaticFiles();

app.UseRouting();

app.MapControllers();
app.MapHub<PingHub>("/hubs/ping");

// Root endpoint
app.MapGet("/", () => Results.Redirect("/index.html"));

// API info endpoint
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

app.Run();
