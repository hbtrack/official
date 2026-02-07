"""
Cache server-side usando cachetools

Implementa cache em memória com TTL para dados frequentemente acessados:
- User lookups
- Permission checks
- Organization data
- Reports aggregados (attendance, minutes, load, alerts)

Mantém arquitetura stateless usando TTL curtos e invalidação em updates.
"""
from functools import wraps
from typing import Optional, Callable, Any
from cachetools import TTLCache
import json
import logging

# Logger dedicado para cache - permite controle granular de nível
# Em dev: DEBUG para ver hits/misses
# Em prod: INFO para silenciar ou ver apenas invalidações
logger = logging.getLogger("hb.cache")

# Cache configurations
# TTL em segundos - valores curtos para manter dados frescos
USER_CACHE_TTL = 300  # 5 minutos
PERMISSION_CACHE_TTL = 300  # 5 minutos
ORGANIZATION_CACHE_TTL = 600  # 10 minutos
REPORT_CACHE_TTL = 120  # 2 minutos - relatórios agregados

# Max items por cache
CACHE_MAX_SIZE = 1000
REPORT_CACHE_MAX_SIZE = 512

# Caches globais
_user_cache = TTLCache(maxsize=CACHE_MAX_SIZE, ttl=USER_CACHE_TTL)
_permission_cache = TTLCache(maxsize=CACHE_MAX_SIZE, ttl=PERMISSION_CACHE_TTL)
_organization_cache = TTLCache(maxsize=CACHE_MAX_SIZE, ttl=ORGANIZATION_CACHE_TTL)
_report_cache = TTLCache(maxsize=REPORT_CACHE_MAX_SIZE, ttl=REPORT_CACHE_TTL)


# =============================================================================
# REPORT CACHE - Relatórios agregados
# =============================================================================

def make_report_key(prefix: str, **params) -> str:
    """
    Gera chave de cache para relatórios.
    
    Args:
        prefix: Tipo de relatório (attendance, minutes, load, alerts_load, alerts_injury)
        **params: Parâmetros do filtro (team_id, season_id, start_date, end_date)
    
    Returns:
        Chave única para o cache
    """
    # Converter UUIDs e datas para string
    clean_params = {}
    for k, v in params.items():
        if v is not None:
            clean_params[k] = str(v)
    return f"report:{prefix}:" + json.dumps(clean_params, sort_keys=True)


def get_cached_report(key: str) -> Optional[Any]:
    """
    Obtém relatório do cache.
    
    Returns:
        Dados cacheados ou None se não encontrado
    """
    if key in _report_cache:
        logger.debug("CACHE HIT  | key=%s", key)
        return _report_cache[key]
    logger.debug("CACHE MISS | key=%s", key)
    return None


def set_cached_report(key: str, data: Any) -> None:
    """
    Armazena relatório no cache.
    """
    _report_cache[key] = data
    logger.debug("CACHE SET  | key=%s", key)


def invalidate_report_cache() -> None:
    """
    Invalida todo o cache de relatórios.
    
    Deve ser chamado após writes em:
    - attendance
    - training_sessions
    - wellness_post
    - athletes (flags médicas)
    - medical_cases
    """
    size = len(_report_cache)
    _report_cache.clear()
    logger.debug("CACHE INVALIDATED | entries_cleared=%d", size)


def cache_user(func: Callable) -> Callable:
    """
    Decorator para cachear lookups de usuário por ID

    Uso:
        @cache_user
        def get_user_by_id(db: Session, user_id: str) -> Optional[User]:
            ...
    """
    @wraps(func)
    def wrapper(db, user_id: str, *args, **kwargs):
        cache_key = f"user:{user_id}"

        # Tentar obter do cache
        if cache_key in _user_cache:
            logger.debug(f"Cache HIT: {cache_key}")
            return _user_cache[cache_key]

        # Cache miss - buscar no banco
        logger.debug(f"Cache MISS: {cache_key}")
        result = func(db, user_id, *args, **kwargs)

        # Armazenar no cache se encontrou
        if result is not None:
            _user_cache[cache_key] = result

        return result

    return wrapper


def cache_permission(func: Callable) -> Callable:
    """
    Decorator para cachear verificações de permissão

    Uso:
        @cache_permission
        def check_user_permission(db: Session, user_id: str, permission: str) -> bool:
            ...
    """
    @wraps(func)
    def wrapper(db, user_id: str, permission: str, *args, **kwargs):
        cache_key = f"perm:{user_id}:{permission}"

        # Tentar obter do cache
        if cache_key in _permission_cache:
            logger.debug(f"Cache HIT: {cache_key}")
            return _permission_cache[cache_key]

        # Cache miss - executar verificação
        logger.debug(f"Cache MISS: {cache_key}")
        result = func(db, user_id, permission, *args, **kwargs)

        # Armazenar no cache
        _permission_cache[cache_key] = result

        return result

    return wrapper


def cache_organization(func: Callable) -> Callable:
    """
    Decorator para cachear dados de organização

    Uso:
        @cache_organization
        def get_organization_by_id(db: Session, org_id: str) -> Optional[Organization]:
            ...
    """
    @wraps(func)
    def wrapper(db, org_id: str, *args, **kwargs):
        cache_key = f"org:{org_id}"

        # Tentar obter do cache
        if cache_key in _organization_cache:
            logger.debug(f"Cache HIT: {cache_key}")
            return _organization_cache[cache_key]

        # Cache miss - buscar no banco
        logger.debug(f"Cache MISS: {cache_key}")
        result = func(db, org_id, *args, **kwargs)

        # Armazenar no cache se encontrou
        if result is not None:
            _organization_cache[cache_key] = result

        return result

    return wrapper


def invalidate_user_cache(user_id: str) -> None:
    """
    Invalida cache de um usuário específico

    Deve ser chamado após updates em users
    """
    cache_key = f"user:{user_id}"
    if cache_key in _user_cache:
        del _user_cache[cache_key]
        logger.info(f"Cache invalidado: {cache_key}")


def invalidate_permission_cache(user_id: str) -> None:
    """
    Invalida cache de permissões de um usuário

    Deve ser chamado após updates em memberships/roles
    """
    # Remover todas as permissões do usuário
    keys_to_remove = [k for k in _permission_cache.keys() if k.startswith(f"perm:{user_id}:")]
    for key in keys_to_remove:
        del _permission_cache[key]

    if keys_to_remove:
        logger.info(f"Cache invalidado: {len(keys_to_remove)} permissões do user {user_id}")


def invalidate_organization_cache(org_id: str) -> None:
    """
    Invalida cache de uma organização

    Deve ser chamado após updates em organizations
    """
    cache_key = f"org:{org_id}"
    if cache_key in _organization_cache:
        del _organization_cache[cache_key]
        logger.info(f"Cache invalidado: {cache_key}")


def clear_all_caches() -> None:
    """
    Limpa todos os caches

    Útil para testes ou refresh manual
    """
    _user_cache.clear()
    _permission_cache.clear()
    _organization_cache.clear()
    _report_cache.clear()
    logger.info("Todos os caches foram limpos")


def get_cache_stats() -> dict:
    """
    Retorna estatísticas dos caches

    Útil para monitoramento
    """
    return {
        "user_cache": {
            "size": len(_user_cache),
            "maxsize": _user_cache.maxsize,
            "ttl": USER_CACHE_TTL,
        },
        "permission_cache": {
            "size": len(_permission_cache),
            "maxsize": _permission_cache.maxsize,
            "ttl": PERMISSION_CACHE_TTL,
        },
        "organization_cache": {
            "size": len(_organization_cache),
            "maxsize": _organization_cache.maxsize,
            "ttl": ORGANIZATION_CACHE_TTL,
        },
        "report_cache": {
            "size": len(_report_cache),
            "maxsize": _report_cache.maxsize,
            "ttl": REPORT_CACHE_TTL,
        },
    }
