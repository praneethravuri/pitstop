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
