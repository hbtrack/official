"""
Configurações do sistema usando Pydantic Settings
Todas as configurações via variáveis de ambiente (12-factor app)

Ref: FASE 2 — Núcleo do backend
"""
from pathlib import Path
from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal, Optional

# Raiz do backend (onde está o .env)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    """
    Configurações globais do HB Tracking Backend

    Referências RAG:
    - R34: Clube único na V1
    - RDB1: PostgreSQL 17 (Neon)
    """

    # Environment (test = testes automatizados, rate limit desabilitado)
    ENV: Literal["local", "staging", "production", "test"] = "local"

    # API
    API_VERSION: str = "v1"
    API_TITLE: str = "HB Tracking API"
    API_DESCRIPTION: str = "Sistema de Gestão de Handebol"
    API_VERSION_NUMBER: str = "1.0.0"

    # Database (RDB1) - Configuração otimizada para Neon Free Tier
    DATABASE_URL: str = "postgresql://neondb_owner:npg_PrN5buzBWya1@ep-steep-bread-ad9uwqio-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
    DB_POOL_SIZE: int = 5          # Free tier: 5 conexões base para suportar requisições paralelas
    DB_MAX_OVERFLOW: int = 5       # Free tier: 5 extras para picos de carga
    DB_POOL_PRE_PING: bool = True  # OBRIGATÓRIO: detecta conexão morta
    DB_POOL_TIMEOUT: int = 45      # Timeout aumentado para obter conexão
    DB_POOL_RECYCLE: int = 1800    # Reciclar a cada 30 min (evita conexão morta)

    # Cache TTL (reduz queries no Free tier)
    CACHE_TTL_VINCULOS: int = 300      # 5 minutos
    CACHE_TTL_PERMISSOES: int = 300    # 5 minutos

    # Security
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRES_MINUTES: int = 30

    # Frontend URL (para links em emails)
    FRONTEND_URL: str = "http://localhost:3000"
    
    # WebSocket (Step 10)
    WEBSOCKET_RECONNECT_INITIAL_DELAY: int = 1        # Delay inicial em segundos
    WEBSOCKET_RECONNECT_MAX_DELAY: int = 30           # Delay máximo entre tentativas
    WEBSOCKET_RECONNECT_MULTIPLIER: float = 2.0       # Multiplicador exponential backoff
    WEBSOCKET_RECONNECT_MAX_ATTEMPTS: int = 10        # Máximo de tentativas de reconexão
    WEBSOCKET_HEARTBEAT_INTERVAL: int = 30            # Heartbeat a cada 30s
    WEBSOCKET_CLEANUP_INTERVAL: int = 300             # Cleanup de conexões órfãs a cada 5min
    
    # Notificações
    NOTIFICATION_RETENTION_DAYS: int = 20  # Reter notificações lidas por 20 dias
    
    # Políticas de convites
    INVITE_RESEND_COOLDOWN_HOURS: int = 48  # Cooldown de 48h entre reenvios
    INVITE_MAX_RESEND_COUNT: int = 3        # Máximo de 3 reenvios por convite
    
    # HTTPS/TLS (Produção)
    FORCE_HTTPS: bool = False  # Forçar HTTPS em produção
    HSTS_MAX_AGE: int = 31536000  # 1 ano em segundos
    HSTS_INCLUDE_SUBDOMAINS: bool = True
    HSTS_PRELOAD: bool = True

    # CORS — política determinística (AR_233)
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_ORIGIN_REGEX: Optional[str] = None
    CORS_ALLOW_HEADERS: str = "Authorization,Content-Type,Accept,X-CSRF-Token,X-Request-ID,X-Organization-ID"
    CORS_ALLOW_METHODS: str = "GET,POST,PUT,PATCH,DELETE,OPTIONS"
    CORS_EXPOSE_HEADERS: str = "X-Request-ID"
    CORS_MAX_AGE: int = 600

    @property
    def cors_origins_list(self) -> list[str]:
        """Converte CORS_ORIGINS de string para lista, com strip e filtro de vazios."""
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    @property
    def cors_allow_headers_list(self) -> list[str]:
        return [h.strip() for h in self.CORS_ALLOW_HEADERS.split(",") if h.strip()]

    @property
    def cors_allow_methods_list(self) -> list[str]:
        return [m.strip() for m in self.CORS_ALLOW_METHODS.split(",") if m.strip()]

    @property
    def cors_expose_headers_list(self) -> list[str]:
        return [h.strip() for h in self.CORS_EXPOSE_HEADERS.split(",") if h.strip()]

    # Email (Resend)
    RESEND_API_KEY: Optional[str] = None
    RESEND_FROM_EMAIL: str = "noreply@hbtracking.com"
    RESEND_FROM_NAME: str = "HB Track"
    RESEND_REPLY_TO: Optional[str] = None

    # Cloudinary (Upload de mídia)
    CLOUDINARY_CLOUD_NAME: str = ""
    CLOUDINARY_API_KEY: str = ""
    CLOUDINARY_API_SECRET: str = ""
    CLOUDINARY_UPLOAD_PRESET: Optional[str] = None  # Preset para uploads unsigned

    # Google Gemini AI (para parsing de PDFs de competição)
    GEMINI_API_KEY: Optional[str] = None

    # Celery + Redis (Step 18 - Alertas e Sugestões Automáticas)
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"
    CELERY_TIMEZONE: str = "America/Sao_Paulo"
    CELERY_TASK_TRACK_STARTED: bool = True
    CELERY_TASK_TIME_LIMIT: int = 300  # 5 minutos
    CELERY_WORKER_MAX_TASKS_PER_CHILD: int = 1000

    # Flower (Celery monitoring UI)
    FLOWER_PORT: int = 5555
    FLOWER_BASIC_AUTH: str = "admin:hbtrack2026"

    # Logging
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"

    # Institutional team lookup (R39)
    INSTITUTIONAL_TEAM_ID: Optional[str] = None
    INSTITUTIONAL_TEAM_ALIASES: str = "equipe institucional,grupo de avaliacao,avaliacao"

    @model_validator(mode="after")
    def validate_cors_policy(self) -> "Settings":
        """Regras de segurança CORS — fail-fast no boot (AR_233)."""
        if self.CORS_ALLOW_CREDENTIALS:
            # Regra 1: credentials=True + wildcard é inválido (browser bloqueia, RFC 6454)
            if "*" in self.cors_origins_list:
                raise ValueError(
                    "CORS inseguro: CORS_ALLOW_CREDENTIALS=True é incompatível com "
                    "wildcard em CORS_ALLOW_ORIGINS. Use lista explícita de origens."
                )
            # Regra 2: credentials=True + regex — somente lista explícita é auditável
            if self.CORS_ALLOW_ORIGIN_REGEX is not None:
                raise ValueError(
                    "CORS inseguro: CORS_ALLOW_CREDENTIALS=True é incompatível com "
                    "CORS_ALLOW_ORIGIN_REGEX. Use CORS_ALLOW_ORIGINS com lista explícita."
                )
        return self

    model_config = SettingsConfigDict(
        env_file=str(PROJECT_ROOT / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    @property
    def is_production(self) -> bool:
        return self.ENV == "production"

    @property
    def is_local(self) -> bool:
        return self.ENV == "local"


# Singleton instance
settings = Settings()
