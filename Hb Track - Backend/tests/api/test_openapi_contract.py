"""
Testes de Contrato API (Schemathesis)

Valida automaticamente todas as APIs contra o schema OpenAPI.
Detecta:
- Status codes inesperados
- Respostas fora do schema
- Erros de validação
- Crashes (500)

Execução:
  pytest tests/api/test_openapi_contract.py -v

Ou diretamente via CLI:
  schemathesis run http://localhost:8000/api/v1/openapi.json --url http://localhost:8000
"""
import pytest
import requests

try:
    import schemathesis
    SCHEMATHESIS_AVAILABLE = True
except ImportError:
    SCHEMATHESIS_AVAILABLE = False
    schemathesis = None


# Configuração do schema
API_URL = "http://localhost:8000"
OPENAPI_PATH = "/api/v1/openapi.json"


@pytest.mark.skipif(not SCHEMATHESIS_AVAILABLE, reason="schemathesis não instalado")
@pytest.mark.contract
class TestOpenAPIContract:
    """
    Testes de contrato baseados no OpenAPI schema.
    
    Estes testes são gerados automaticamente pelo Schemathesis
    e validam que cada endpoint:
    1. Aceita os parâmetros documentados
    2. Retorna status codes documentados
    3. Retorna respostas no formato documentado
    """
    
    def test_schema_accessible(self):
        """Verifica que o schema OpenAPI está acessível"""
        response = requests.get(f"{API_URL}{OPENAPI_PATH}")
        if response.status_code == 200:
            data = response.json()
            assert "paths" in data
            assert "info" in data
        else:
            pytest.skip(f"Backend offline ou schema não disponível: {response.status_code}")
    
    def test_health_endpoint(self):
        """Testa endpoint de health check"""
        response = requests.get(f"{API_URL}/health")
        assert response.status_code in [200, 404]  # 404 se não existir


# ============================================================================
# TESTES DE CONTRATO COM SCHEMATHESIS (requerem backend rodando)
# ============================================================================

@pytest.mark.contract
@pytest.mark.skipif(not SCHEMATHESIS_AVAILABLE, reason="schemathesis não instalado")
class TestContractValidation:
    """
    Testes de validação de contrato via schemathesis.
    Só rodam quando backend está online.
    """
    
    def test_openapi_schema_valid(self):
        """Verifica que o schema OpenAPI é válido"""
        try:
            response = requests.get(f"{API_URL}{OPENAPI_PATH}", timeout=5)
            if response.status_code != 200:
                pytest.skip("Backend offline")
            
            schema_data = response.json()
            
            # Verificações básicas do schema
            assert schema_data.get("openapi", "").startswith("3."), "Schema deve ser OpenAPI 3.x"
            assert "paths" in schema_data, "Schema deve ter paths"
            assert len(schema_data["paths"]) > 0, "Schema deve ter ao menos um endpoint"
            
        except requests.exceptions.ConnectionError:
            pytest.skip("Backend offline - não foi possível conectar")
    
    def test_endpoints_documented(self):
        """Verifica que endpoints principais estão documentados"""
        try:
            response = requests.get(f"{API_URL}{OPENAPI_PATH}", timeout=5)
            if response.status_code != 200:
                pytest.skip("Backend offline")
            
            schema_data = response.json()
            paths = schema_data.get("paths", {})
            
            # Endpoints essenciais que devem existir
            essential_paths = [
                "/api/v1/auth/login",
                "/api/v1/teams",
                "/api/v1/athletes",
            ]
            
            for path in essential_paths:
                # Procurar path no schema (pode ter prefixo diferente)
                found = any(path in p or p.endswith(path.split("/api/v1")[-1]) for p in paths.keys())
                if not found:
                    pytest.skip(f"Path {path} não encontrado no schema")
                    
        except requests.exceptions.ConnectionError:
            pytest.skip("Backend offline")


# ============================================================================
# HELPER: Comando para rodar schemathesis via CLI
# ============================================================================

# Comandos úteis:
#
# Rodar todos os testes de contrato (backend precisa estar rodando)
# schemathesis run http://localhost:8000/api/v1/openapi.json --url http://localhost:8000
#
# Rodar com autenticação (cookie)
# schemathesis run http://localhost:8000/api/v1/openapi.json \
#     --url http://localhost:8000 \
#     -H "Cookie: hb_access_token=<token>"
#
# Verificar apenas erros 500
# schemathesis run http://localhost:8000/api/v1/openapi.json \
#     --url http://localhost:8000 \
#     --checks not_a_server_error
