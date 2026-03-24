# ──────────────────────────────────────────────────────────────────────────────
# HB Track — Dockerfile multi-stage
# Stage builder : instala dependências em .venv isolado
# Stage runtime : imagem mínima com apenas o necessário para execução
# ENTRYPOINT    : gunicorn + UvicornWorker (ASGI — suporta HTTP e WebSocket)
# ──────────────────────────────────────────────────────────────────────────────

# ── Stage 1: builder ──────────────────────────────────────────────────────────
FROM python:3.12-slim AS builder

# Dependências de build (compilação de extensões C do psycopg2/cryptography)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build

# Copiar apenas requirements para aproveitar cache de camadas Docker
COPY requirements.txt .

# Criar virtualenv no path final (/app/.venv) para que os shebangs
# sejam válidos após a cópia para o stage runtime
RUN python -m venv /app/.venv \
    && /app/.venv/bin/pip install --upgrade pip --no-cache-dir \
    && /app/.venv/bin/pip install -r requirements.txt --no-cache-dir

# ── Stage 2: runtime ──────────────────────────────────────────────────────────
FROM python:3.12-slim AS runtime

LABEL org.opencontainers.image.source="https://github.com/hbtrack/hb-track"
LABEL org.opencontainers.image.description="HB Track — Backend API"

# Apenas runtime libs (libpq para psycopg2)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Usuário não-root por segurança (CWE-250)
RUN useradd --no-create-home --shell /bin/false hbtrack

WORKDIR /app

# Copiar apenas o venv compilado e o código da aplicação
COPY --from=builder /app/.venv /app/.venv
COPY src/       ./src/
COPY config/    ./config/
COPY scripts/   ./scripts/
COPY manage.py  ./

# Criar diretório de arquivos estáticos
RUN mkdir -p /app/staticfiles && chown -R hbtrack:hbtrack /app

# Virtualenv no PATH
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app/src:/app"
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Porta padrão do serviço
EXPOSE 8000

# Trocar para usuário não-root antes de iniciar
USER hbtrack

# Healthcheck interno (usado pelo Docker e pelo docker-compose)
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Gunicorn com UvicornWorker — suporta HTTP e WebSocket (ASGI)
ENTRYPOINT ["gunicorn", "config.asgi:application", \
    "--bind", "0.0.0.0:8000", \
    "--worker-class", "uvicorn.workers.UvicornWorker", \
    "--workers", "2", \
    "--timeout", "120", \
    "--graceful-timeout", "30", \
    "--access-logfile", "-", \
    "--error-logfile", "-" \
]
