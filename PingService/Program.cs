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

// Add Swagger for API documentation
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen(c =>
{
    c.SwaggerDoc("v1", new()
    {
        Title = "Coordinate Ping Service API",
        Version = "v1",
        Description = "Real-time coordinate ping generation and tracking system (20,000 pings/second)"
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
    service = "Coordinate Ping Service",
    version = "1.0.0",
    description = "Generates and tracks 20,000 coordinate pings per second",
    endpoints = new
    {
        dashboard = "/index.html",
        swagger = "/swagger",
        signalr = "/hubs/ping",
        api = "/api/ping"
    }
});

app.Logger.LogInformation("Starting Coordinate Ping Service...");
app.Logger.LogInformation("Dashboard: http://localhost:5000");
app.Logger.LogInformation("API: http://localhost:5000/api/ping");
app.Logger.LogInformation("SignalR Hub: http://localhost:5000/hubs/ping");
app.Logger.LogInformation("Swagger: http://localhost:5000/swagger");

app.Run();
