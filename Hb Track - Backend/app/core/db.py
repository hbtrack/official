"""
Gerenciamento de conexão com PostgreSQL (Neon Free Tier)

Configuração com psycopg3 (async nativo) - compatível com Python 3.14+

Configuração para Neon Free:
- Pooler obrigatório (máx 3 conexões)
- pool_pre_ping = True (detecta conexão morta)
- pool_size = 5, max_overflow = 5
- pool_recycle = 1800 (30 min)
- Retry com backoff para cold start

Referências RAG:
- RDB1: PostgreSQL 17 com pgcrypto
- RDB3: timestamptz em UTC
- R33: Nada acontece fora de um vínculo
"""
from contextlib import contextmanager, asynccontextmanager
from typing import Generator, AsyncGenerator
import logging
import time
import asyncio

from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.exc import OperationalError, DBAPIError

from app.core.config import settings

logger = logging.getLogger(__name__)


# ============================================================================
# Database URL Conversion
# ============================================================================

def _get_sync_url(database_url: str) -> str:
    """Converte URL para psycopg2 (sync)."""
    url = database_url
    # Normalizar para psycopg2
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+psycopg2://", 1)
    elif url.startswith("postgresql+asyncpg://"):
        url = url.replace("postgresql+asyncpg://", "postgresql+psycopg2://", 1)
    elif url.startswith("postgresql+psycopg://"):
        url = url.replace("postgresql+psycopg://", "postgresql+psycopg2://", 1)
    return url


def _get_async_url(database_url: str) -> str:
    """Converte URL para psycopg async (psycopg3)."""
    url = database_url
    # Normalizar para psycopg async (psycopg3)
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+psycopg://", 1)
    elif url.startswith("postgresql+psycopg2://"):
        url = url.replace("postgresql+psycopg2://", "postgresql+psycopg://", 1)
    elif url.startswith("postgresql+asyncpg://"):
        url = url.replace("postgresql+asyncpg://", "postgresql+psycopg://", 1)
    return url


# ============================================================================
# Engine Configuration (Otimizado para Neon Free Tier)
# ============================================================================

def _create_sync_engine():
    """
    Cria engine SYNC com configurações otimizadas para Neon Free Tier.
    Usa psycopg2 para compatibilidade máxima.
    """
    from app.core.config import Settings
    current_settings = Settings()
    
    database_url = _get_sync_url(current_settings.DATABASE_URL)
    
    # Garantir que está usando pooler (produção)
    if "neon" in database_url and "-pooler" not in database_url:
        logger.warning("⚠️ DATABASE_URL não contém '-pooler'. Neon Free requer pooler!")
    
    pool_size = max(current_settings.DB_POOL_SIZE, 5)
    max_overflow = max(current_settings.DB_MAX_OVERFLOW, 5)
    
    logger.info(f"🔧 Creating SYNC engine (psycopg2)")
    logger.info(f"   Pool: size={pool_size}, overflow={max_overflow}")
    
    return create_engine(
        database_url,
        pool_pre_ping=True,
        pool_size=pool_size,
        max_overflow=max_overflow,
        pool_timeout=current_settings.DB_POOL_TIMEOUT,
        pool_recycle=current_settings.DB_POOL_RECYCLE,
        echo=current_settings.LOG_LEVEL == "DEBUG",
        future=True,
        connect_args={
            "connect_timeout": 30,
            "options": "-c timezone=utc",
        }
    )


def _create_async_engine():
    """
    Cria engine ASYNC com psycopg3.
    Compatível com Python 3.14+.

    NOTA: pool_pre_ping=False para evitar MissingGreenlet com psycopg3 async.
    O psycopg3 async não suporta o ping de pool síncrono do SQLAlchemy.
    """
    from app.core.config import Settings
    current_settings = Settings()

    database_url = _get_async_url(current_settings.DATABASE_URL)

    pool_size = max(current_settings.DB_POOL_SIZE, 5)
    max_overflow = max(current_settings.DB_MAX_OVERFLOW, 5)

    logger.info(f"🔧 Creating ASYNC engine (psycopg3)")
    logger.info(f"   Pool: size={pool_size}, overflow={max_overflow}")

    return create_async_engine(
        database_url,
        pool_pre_ping=False,  # Desabilitado - psycopg3 async não suporta ping sync
        pool_size=pool_size,
        max_overflow=max_overflow,
        pool_timeout=current_settings.DB_POOL_TIMEOUT,
        pool_recycle=current_settings.DB_POOL_RECYCLE,
        echo=current_settings.LOG_LEVEL == "DEBUG",
        # psycopg3 connect_args
        connect_args={
            "connect_timeout": 30,
            "options": "-c timezone=utc",
        }
    )


# ============================================================================
# Engine Singletons (Lazy Loading para evitar conflito psycopg2/psycopg3)
# ============================================================================

# Engine SYNC (para rotas que precisam de sync)
engine = _create_sync_engine()

# Engine ASYNC - lazy loading para evitar MissingGreenlet
_async_engine = None
_AsyncSessionLocal = None


def get_async_engine():
    """Retorna o engine async, criando-o apenas quando necessário."""
    global _async_engine
    if _async_engine is None:
        _async_engine = _create_async_engine()
    return _async_engine


def get_async_session_local():
    """Retorna o async session maker, criando-o apenas quando necessário."""
    global _AsyncSessionLocal
    if _AsyncSessionLocal is None:
        _AsyncSessionLocal = async_sessionmaker(
            bind=get_async_engine(),
            class_=AsyncSession,
            autocommit=False,
            autoflush=False,
            expire_on_commit=False
        )
    return _AsyncSessionLocal


# SessionLocal SYNC
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    future=True,
    expire_on_commit=False
)

# AsyncSessionLocal - alias para compatibilidade com código existente
# Uso: session_maker = AsyncSessionLocal() ou get_async_session_local()
#      async with session_maker() as db: ...
AsyncSessionLocal = get_async_session_local


# ============================================================================
# Retry com Backoff (OBRIGATÓRIO para Cold Start do Neon)
# ============================================================================

def execute_with_retry(func, max_retries: int = 3, backoff_times: list = None):
    """
    Executa função com retry automático para cold start do Neon.
    """
    if backoff_times is None:
        backoff_times = [0.5, 1.0, 2.0]
    
    last_exception = None
    
    for attempt in range(max_retries):
        try:
            return func()
        except (OperationalError, DBAPIError) as e:
            last_exception = e
            error_msg = str(e).lower()
            
            retry_errors = [
                "connection refused",
                "connection reset", 
                "server closed",
                "connection unexpectedly",
                "timeout",
                "could not connect",
                "connection timed out",
            ]
            
            should_retry = any(err in error_msg for err in retry_errors)
            
            if should_retry and attempt < max_retries - 1:
                wait_time = backoff_times[min(attempt, len(backoff_times) - 1)]
                logger.warning(
                    f"🔄 Database connection failed (attempt {attempt + 1}/{max_retries}). "
                    f"Retrying in {wait_time}s..."
                )
                time.sleep(wait_time)
            else:
                raise
    
    raise last_exception


async def execute_with_retry_async(func, max_retries: int = 3, backoff_times: list = None):
    """
    Executa função ASYNC com retry automático.
    """
    if backoff_times is None:
        backoff_times = [0.5, 1.0, 2.0]
    
    last_exception = None
    
    for attempt in range(max_retries):
        try:
            return await func()
        except (OperationalError, DBAPIError) as e:
            last_exception = e
            error_msg = str(e).lower()
            
            retry_errors = [
                "connection refused",
                "connection reset", 
                "server closed",
                "connection unexpectedly",
                "timeout",
                "could not connect",
            ]
            
            should_retry = any(err in error_msg for err in retry_errors)
            
            if should_retry and attempt < max_retries - 1:
                wait_time = backoff_times[min(attempt, len(backoff_times) - 1)]
                logger.warning(
                    f"🔄 Async DB connection failed (attempt {attempt + 1}/{max_retries}). "
                    f"Retrying in {wait_time}s..."
                )
                await asyncio.sleep(wait_time)
            else:
                raise
    
    raise last_exception


# ============================================================================
# Healthcheck
# ============================================================================

def warmup_database() -> bool:
    """Aquece o banco de dados no boot (sync)."""
    def _do_warmup():
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            return result.scalar() == 1
    
    try:
        logger.info("🔄 Warming up database...")
        success = execute_with_retry(_do_warmup)
        if success:
            logger.info("✅ Database connection ready")
        return success
    except Exception as e:
        logger.error(f"❌ Database warmup failed: {e}")
        return False


async def warmup_database_async() -> bool:
    """Aquece o banco de dados no boot (async)."""
    async def _do_warmup():
        async with get_async_engine().connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            return result.scalar() == 1
    
    try:
        logger.info("🔄 Warming up async database...")
        success = await execute_with_retry_async(_do_warmup)
        if success:
            logger.info("✅ Async database connection ready")
        return success
    except Exception as e:
        logger.error(f"❌ Async database warmup failed: {e}")
        return False


def healthcheck_db() -> dict:
    """Healthcheck completo do banco de dados."""
    def _do_healthcheck():
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            pg_version = result.scalar()
            
            result = conn.execute(text(
                "SELECT COUNT(*) FROM pg_extension WHERE extname = 'pgcrypto'"
            ))
            has_pgcrypto = result.scalar() > 0
            
            try:
                result = conn.execute(text(
                    "SELECT version_num FROM alembic_version LIMIT 1"
                ))
                alembic_version = result.scalar()
            except Exception:
                alembic_version = None
            
            return {
                "status": "healthy",
                "pg_version": pg_version.split()[1] if pg_version else "unknown",
                "pgcrypto_enabled": has_pgcrypto,
                "alembic_version": alembic_version,
                "pool_size": engine.pool.size(),
                "pool_checkedin": engine.pool.checkedin(),
            }
    
    try:
        return execute_with_retry(_do_healthcheck)
    except Exception as e:
        logger.error(f"Database healthcheck failed: {e}")
        return {"status": "unhealthy", "error": str(e)}


# ============================================================================
# Dependencies para Routers (SYNC)
# ============================================================================

def get_db() -> Generator[Session, None, None]:
    """Dependency SYNC para obter sessão de banco."""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Database error: {e}")
        raise
    finally:
        db.close()


def get_db_with_retry() -> Generator[Session, None, None]:
    """Dependency SYNC com retry para operações críticas."""
    def _create_session():
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        return db
    
    db = execute_with_retry(_create_session)
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Database error: {e}")
        raise
    finally:
        db.close()


@contextmanager
def db_context() -> Generator[Session, None, None]:
    """Context manager SYNC para uso fora de rotas."""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


# ============================================================================
# Dependencies para Routers (ASYNC)
# ============================================================================

async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency ASYNC para obter sessão de banco."""
    session_maker = get_async_session_local()
    async with session_maker() as db:
        try:
            yield db
            await db.commit()
        except Exception as e:
            await db.rollback()
            logger.error(f"Async database error: {e}")
            raise


async def get_async_db_with_retry() -> AsyncGenerator[AsyncSession, None]:
    """Dependency ASYNC com retry para operações críticas."""
    async def _create_session():
        session_maker = get_async_session_local()
        session = session_maker()
        await session.execute(text("SELECT 1"))
        return session

    db = await execute_with_retry_async(_create_session)
    try:
        yield db
        await db.commit()
    except Exception as e:
        await db.rollback()
        logger.error(f"Async database error: {e}")
        raise
    finally:
        await db.close()


@asynccontextmanager
async def async_db_context() -> AsyncGenerator[AsyncSession, None]:
    """Context manager ASYNC para uso fora de rotas."""
    session_maker = get_async_session_local()
    async with session_maker() as db:
        try:
            yield db
            await db.commit()
        except Exception:
            await db.rollback()
            raise


# Alias para Celery tasks (Step 18)
get_db_context = async_db_context


# ============================================================================
# Utility
# ============================================================================

def get_db_with_context(user_id: str | None = None, org_id: str | None = None):
    """Dependency com contexto de execução (user_id, org_id)."""
    def _inner() -> Generator[Session, None, None]:
        db = SessionLocal()
        db.info["user_id"] = user_id
        db.info["org_id"] = org_id
        try:
            yield db
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()
    return _inner


# Backward compat: alguns models antigos importavam Base daqui
from app.models.base import Base  # noqa: F401
