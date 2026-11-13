FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:0.8.15 /uv /usr/local/bin/uv
WORKDIR /app
COPY pyproject.toml uv.lock ./
COPY trading ./trading
RUN uv sync --frozen --no-dev && useradd --uid 10001 --create-home glitter && mkdir /app/data && chown -R glitter:glitter /app
USER glitter
ENV HOST=0.0.0.0 PORT=8000
EXPOSE 8000
CMD ["/app/.venv/bin/glitter-serve"]
