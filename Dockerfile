FROM python:3.12-slim AS trader

ENV PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=utf-8 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    TRADER_CONFIG_DIR=/app/config

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
WORKDIR /app

# dependencies first (cached layer), then the project
COPY pyproject.toml uv.lock README.md ./
RUN uv sync --frozen --no-install-project --no-dev
COPY src ./src
COPY config ./config
RUN uv sync --frozen --no-dev

ENV PATH="/app/.venv/bin:$PATH"
# no secrets are baked into the image: keys arrive via env_file / environment at run time
CMD ["tradectl", "--help"]

FROM trader AS viewer

COPY tools/replay_viewer.py ./tools/replay_viewer.py
COPY tools/replay_viewer/ ./tools/replay_viewer/
COPY config/llm_profiles.paper.example.yaml ./config/llm_profiles.yaml
RUN groupadd --system --gid 10001 viewer \
    && useradd --system --uid 10001 --gid viewer viewer

ENV PYTHONDONTWRITEBYTECODE=1 \
    EXECUTION_ENABLED=false
USER 10001:10001
EXPOSE 8765
CMD ["python", "tools/replay_viewer.py", "--host", "0.0.0.0", "--session-only"]

FROM trader AS services
