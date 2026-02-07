"""
Middlewares customizados

Referências RAG:
- R31: Ações críticas auditáveis
- R32: Log obrigatório (quem, quando, o quê)
"""
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import uuid
import logging
import time

logger = logging.getLogger(__name__)


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Middleware para adicionar Request ID único em cada requisição

    Usado para correlação de logs (R31, R32)
    
    O Request ID é:
    1. Recuperado do header X-Request-ID se fornecido pelo cliente
    2. Gerado automaticamente se não fornecido
    3. Propagado em todos os logs da requisição
    4. Retornado no header X-Request-ID da resposta
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        # Gerar ou pegar Request ID do header
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())

        # Adicionar ao request state para uso em handlers
        request.state.request_id = request_id

        # Timestamp de início para calcular duração
        start_time = time.perf_counter()

        # Log de entrada
        client_ip = request.client.host if request.client else "unknown"
        logger.info(
            f"→ {request.method} {request.url.path}",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": str(request.url.path),
                "client_ip": client_ip,
                "query_params": str(request.query_params) if request.query_params else None
            }
        )

        # Processar request
        try:
            response = await call_next(request)
        except Exception as e:
            # Log de erro
            duration_ms = (time.perf_counter() - start_time) * 1000
            logger.error(
                f"✗ {request.method} {request.url.path} - Exception: {str(e)}",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": str(request.url.path),
                    "duration_ms": round(duration_ms, 2),
                    "client_ip": client_ip
                },
                exc_info=True
            )
            raise

        # Calcular duração
        duration_ms = (time.perf_counter() - start_time) * 1000

        # Log de saída
        log_level = logging.INFO if response.status_code < 400 else logging.WARNING
        logger.log(
            log_level,
            f"← {request.method} {request.url.path} - {response.status_code}",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": str(request.url.path),
                "status_code": response.status_code,
                "duration_ms": round(duration_ms, 2),
                "client_ip": client_ip
            }
        )

        # Adicionar Request ID ao response header
        response.headers["X-Request-ID"] = request_id

        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware para adicionar headers de segurança

    Headers adicionados:
    - X-Content-Type-Options: nosniff
    - X-Frame-Options: DENY
    - X-XSS-Protection: 1; mode=block
    - Strict-Transport-Security (apenas em produção com HTTPS)
    - Content-Security-Policy (básico)
    """

    def __init__(
        self,
        app,
        is_production: bool = False,
        hsts_max_age: int = 31536000,
        hsts_include_subdomains: bool = True,
        hsts_preload: bool = True
    ):
        super().__init__(app)
        self.is_production = is_production
        self.hsts_max_age = hsts_max_age
        self.hsts_include_subdomains = hsts_include_subdomains
        self.hsts_preload = hsts_preload

    async def dispatch(self, request: Request, call_next) -> Response:
        # Forçar HTTPS em produção (redirect)
        if self.is_production and request.url.scheme != "https":
            # Em produção, assumir que há um proxy reverso (Nginx/Cloudflare)
            # que já trata HTTPS. Este check é redundante mas seguro.
            logger.warning(
                f"HTTP request in production: {request.url}",
                extra={"request_id": getattr(request.state, "request_id", "unknown")}
            )

        response = await call_next(request)

        # Headers de segurança básicos
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Content Security Policy básico
        response.headers["Content-Security-Policy"] = "default-src 'self'; frame-ancestors 'none'"

        # HSTS apenas em produção (com HTTPS)
        if self.is_production:
            hsts_value = f"max-age={self.hsts_max_age}"
            if self.hsts_include_subdomains:
                hsts_value += "; includeSubDomains"
            if self.hsts_preload:
                hsts_value += "; preload"
            response.headers["Strict-Transport-Security"] = hsts_value

        return response
