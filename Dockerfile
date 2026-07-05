# syntax=docker/dockerfile:1
FROM python:3.13-slim-bookworm

# Install uv.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Set working directory
WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy dependency files first
COPY pyproject.toml uv.lock ./

# Install dependencies
# --frozen ensures we stick to uv.lock versions
# --no-install-project installs only deps, not the project itself yet (caching layer)
RUN uv sync --frozen --no-install-project --no-dev

# Bake the F1 database into the image so containers start warm.
# ADD from URL is re-checksummed by BuildKit each build (no stale layer cache).
# The empty sidecar (matching _write_sidecar's "etag\nlast_modified\n" format)
# keeps F1DBClient._ensure_db() from re-downloading on first query; after the
# 24h TTL one refresh happens (empty etag mismatches remote), which picks up
# the weekly db update.
# The zip's bytes are kept in this ADD layer by design (baking the db into the
# image is the point); they're extracted below and /tmp/f1db.zip removed, but
# the ADD layer itself still carries the zip — that's the intended image size cost.
ADD https://github.com/praneethravuri/pitstop/releases/download/database/f1db.zip /tmp/f1db.zip
RUN python3 -c "import zipfile, os; os.makedirs('cache/f1db', exist_ok=True); zipfile.ZipFile('/tmp/f1db.zip').extractall('cache/f1db'); open('cache/f1db/f1db.db.etag', 'w').write('\n\n'); os.remove('/tmp/f1db.zip')"

# Copy source code
COPY src ./src
COPY README.md ./

# Install the project itself
RUN uv sync --frozen --no-dev

# Set path to use the virtual environment
ENV PATH="/app/.venv/bin:$PATH"

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PITSTOP_ENV=production
ENV PITSTOP_TRANSPORT=http
ENV PITSTOP_HOST=0.0.0.0
ENV PITSTOP_PORT=8000

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

# Entry point
ENTRYPOINT ["uv", "run", "pitstop"]
