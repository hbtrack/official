"""conftest para testes de integração do módulo video."""
import uuid
import pytest

_FIXED_ACTOR_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")


@pytest.fixture(autouse=True)
def inject_video_actor_id(monkeypatch):
    """Injeta actor_id fixo em todos os testes de integração do video.

    Os testes de integração do módulo video testam a lógica de negócio,
    não a autenticação JWT. O _get_actor_id real requer request._actor_id
    populado pelo JWTClaimsMiddleware, que não está presente no ambiente
    de testes. Este fixture substitui o helper por uma implementação que
    retorna um UUID fixo determinístico, reproduzindo o comportamento
    anterior ao auth enforcement (quando era um uuid4() inline stub).
    """
    import sys
    # Usar o módulo já registrado por config/urls.py (path "video.api", não "src.video.api")
    # para evitar RuntimeError de models duplicados no app registry do Django.
    video_api = sys.modules.get("video.api")
    if video_api is None:
        import video.api as video_api  # carregamento lazy (fixture roda antes das URLs)
    monkeypatch.setattr(video_api, "_get_actor_id", lambda req: _FIXED_ACTOR_ID)
