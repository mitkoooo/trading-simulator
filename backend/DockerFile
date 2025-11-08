FROM ghcr.io/astral-sh/uv:python3.12-bookworm AS base
ADD . /app
WORKDIR /app
RUN uv sync --locked 

FROM base AS development
EXPOSE 8000
ENV PYTHONUNBUFFERED=1 UV_LINK_MODE=copy
CMD ["uv", "run", "uvicorn", "app.server:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
