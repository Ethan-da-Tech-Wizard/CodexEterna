# Dockerfile for Python Sports Service

# Slim Debian-based Python 3.12 image keeps the final image small.
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Set environment variables
# PYTHONUNBUFFERED: flush logs immediately so `docker logs` is live.
# PYTHONDONTWRITEBYTECODE: skip .pyc files (useless in a container).
# PIP_*: no wheel cache and no version-check network call, keeping the layer small.
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
# gcc: build tools in case a Python dependency compiles from source.
# postgresql-client: handy for debugging the database from inside the container.
# curl: required by the HEALTHCHECK below.
# Cleaning the apt lists in the same RUN keeps them out of the layer.
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    postgresql-client \
    curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
# Copy requirements before the source so the pip layer stays cached until dependencies change.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
# Application source. Copied after dependencies for better layer caching.
COPY . .

# Expose port
# Documents the port uvicorn listens on; publishing is done in docker-compose.yml.
EXPOSE 5001

# Health check
# Marks the container unhealthy if /health fails 3 times in a row (probed every 30s).
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    # Create tables first (init_db.py exits non-zero on failure, so uvicorn then does not start),
    # then serve the API on all interfaces. Runs as root; no USER is set.
    CMD curl -f http://localhost:5001/health || exit 1

# Run database initialization and start the application
CMD ["sh", "-c", "python init_db.py && uvicorn app.main:app --host 0.0.0.0 --port 5001"]
