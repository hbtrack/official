"""
Invariant: INV-TRAIN-041
Classe F - OpenAPI Contract Validation (com autenticação)

Obrigação B:
  Validar contrato OpenAPI para GET /api/v1/teams (endpoint autenticado).
  
  - operationId: get_teams_api_v1_teams_get
  - method: GET
  - path: /api/v1/teams
  - responses: 200, 422
  - security: HTTPBearer (autenticação JWT obrigatória)
  
  Evidência: docs/_generated/openapi.json (FastAPI auto-generated schema)
  
  O teste valida que o contrato declarado no SPEC corresponde ao OpenAPI real:
    - operationId existe
    - method/path combinam
    - response codes estão documentados
    - security scheme está presente
  
  Este teste NÃO usa fixtures de DB (db, async_db).
  Valida apenas o contrato da API contra docs/_generated/openapi.json.
"""

import json
from pathlib import Path

import pytest


class TestInvTrain041TeamsContract:
    """
    INV-TRAIN-041: Contrato OpenAPI para endpoint teams (com auth)

    **SPEC**:
    ```yaml
    spec_version: "1.0"
    id: "INV-TRAIN-041"
    status: "CONFIRMADA"
    test_required: true

    units:
      - unit_key: "main"
        class: "F"
        required: true
        description: "Contrato OpenAPI para endpoint teams - validação com security"
        anchors:
          api.operation_id: "get_teams_api_v1_teams_get"
          api.method: "GET"
          api.path: "/api/v1/teams"
          api.responses:
            - "200"
            - "422"
          api.security:
            - "HTTPBearer"

    tests:
      primary: "tests/training/invariants/test_inv_train_041_teams_contract.py"
      node: "TestInvTrain041TeamsContract"
    ```
    """

    @staticmethod
    def _load_openapi_spec() -> dict:
        """Load OpenAPI JSON from generated schema"""
        openapi_path = Path(__file__).parents[3] / "docs" / "_generated" / "openapi.json"
        with open(openapi_path, encoding="utf-8") as f:
            return json.load(f)

    def test_operation_id_exists_in_openapi(self):
        """Valida que o operationId get_teams_api_v1_teams_get existe no openapi.json"""
        openapi_spec = self._load_openapi_spec()
        
        # Find all operationIds in the spec
        operation_ids = []
        for path_obj in openapi_spec.get("paths", {}).values():
            for method_obj in path_obj.values():
                if isinstance(method_obj, dict) and "operationId" in method_obj:
                    operation_ids.append(method_obj["operationId"])
        
        expected_operation_id = "get_teams_api_v1_teams_get"
        assert expected_operation_id in operation_ids, (
            f"operationId '{expected_operation_id}' not found in openapi.json. "
            f"Found: {operation_ids}"
        )

    def test_method_and_path_match_spec(self):
        """Valida que GET /api/v1/teams existe no openapi.json"""
        openapi_spec = self._load_openapi_spec()
        
        expected_path = "/api/v1/teams"
        expected_method = "get"
        
        paths = openapi_spec.get("paths", {})
        assert expected_path in paths, (
            f"Path '{expected_path}' not found in openapi.json. "
            f"Available paths: {list(paths.keys())}"
        )
        
        path_obj = paths[expected_path]
        assert expected_method in path_obj, (
            f"Method '{expected_method}' not found for path '{expected_path}'. "
            f"Available methods: {list(path_obj.keys())}"
        )

    def test_responses_documented(self):
        """Valida que respostas 200 e 422 estão documentadas para GET /api/v1/teams"""
        openapi_spec = self._load_openapi_spec()
        
        path_obj = openapi_spec["paths"]["/api/v1/teams"]
        method_obj = path_obj["get"]
        
        responses = method_obj.get("responses", {})
        expected_responses = ["200", "422"]
        
        for expected_code in expected_responses:
            assert expected_code in responses, (
                f"Response code '{expected_code}' not documented for GET /api/v1/teams. "
                f"Documented responses: {list(responses.keys())}"
            )

    def test_security_scheme_present(self):
        """Valida que security HTTPBearer está presente para GET /api/v1/teams"""
        openapi_spec = self._load_openapi_spec()
        
        path_obj = openapi_spec["paths"]["/api/v1/teams"]
        method_obj = path_obj["get"]
        
        security = method_obj.get("security", [])
        assert len(security) > 0, (
            f"No security defined for GET /api/v1/teams. Expected HTTPBearer."
        )
        
        # Extract security scheme names
        security_schemes = []
        for sec_obj in security:
            if isinstance(sec_obj, dict):
                security_schemes.extend(sec_obj.keys())
        
        assert "HTTPBearer" in security_schemes, (
            f"HTTPBearer not found in security schemes for GET /api/v1/teams. "
            f"Found: {security_schemes}"
        )
