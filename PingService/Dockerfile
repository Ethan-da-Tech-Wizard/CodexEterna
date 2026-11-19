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
# The aspnet runtime image ships neither curl nor wget, so the old `curl -f` check always failed
# and the container reported unhealthy. Debian's bash is present, so the check opens a TCP
# connection with bash's built-in /dev/tcp, sends a minimal HTTP/1.0 GET to /api/ping/health and
# passes only if the status line contains " 200 ". No packages are added to the image.
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD bash -c 'exec 3<>/dev/tcp/127.0.0.1/5000 && printf "GET /api/ping/health HTTP/1.0\r\nHost: localhost\r\n\r\n" >&3 && head -n1 <&3 | grep -q " 200 "' || exit 1

# Run the application
# Start the published app; PingService.dll is the build output of PingService.csproj.
ENTRYPOINT ["dotnet", "PingService.dll"]
