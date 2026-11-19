# Multi-stage Dockerfile for C# Ping Service

# Build stage
# SDK image (large, includes compilers) used only to build; it does not ship in the final image.
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src

# Copy project file and restore dependencies
# Copying just the project file first lets Docker cache the restore layer
# until package references change.
COPY PingService.csproj .
RUN dotnet restore

# Copy source code and build
# Now copy the rest of the source; edits to code do not invalidate the restore layer.
COPY . .
RUN dotnet build -c Release -o /app/build

# Publish stage
# Separate publish stage produces the trimmed deployable output.
FROM build AS publish
RUN dotnet publish -c Release -o /app/publish

# Runtime stage
# Runtime-only ASP.NET image: much smaller than the SDK image.
FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS runtime
WORKDIR /app

# Copy published app
COPY --from=publish /app/publish .

# Expose port
# Documents the listening port; actual publishing happens in docker-compose.yml.
EXPOSE 5000

# Set environment variables
# Bind Kestrel to all interfaces on port 5000 (plain HTTP) and run in Production mode,
# which disables the Swagger UI configured in Program.cs.
ENV ASPNETCORE_URLS=http://+:5000
ENV ASPNETCORE_ENVIRONMENT=Production

# Health check
# NOTE: uses curl, which the aspnet runtime image does not normally include, so this check
# may report unhealthy unless curl is installed. /api/ping/health is the endpoint probed.
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/api/ping/health || exit 1

# Run the application
# Start the published app; PingService.dll is the build output of PingService.csproj.
ENTRYPOINT ["dotnet", "PingService.dll"]
