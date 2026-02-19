"""
Invariant: INV-TRAIN-040
Classe F - OpenAPI Contract Validation

Obrigação B:
  Validar contrato OpenAPI para GET /api/v1/health sem usar fixtures de DB.
  
  - operationId: health_api_v1_health_get
  - method: GET
  - path: /api/v1/health
  - responses: 200
  - security: none (endpoint público)
  
  Evidência: docs/ssot/openapi.json (FastAPI auto-generated schema)
  
  O teste valida que o contrato declarado no SPEC corresponde ao OpenAPI real:
    - operationId existe
    - method/path combinam
    - response codes estão documentados
  
  Este teste NÃO usa fixtures de DB (db, async_db).
  Valida apenas o contrato da API contra docs/ssot/openapi.json.
"""

import json
from pathlib import Path

import pytest


class TestInvTrain040HealthContract:
    """
    INV-TRAIN-040: Contrato OpenAPI para endpoint health

    **SPEC**:
    ```yaml
    spec_version: "1.0"
    id: "INV-TRAIN-040"
    status: "CONFIRMADA"
    test_required: true

    units:
      - unit_key: "main"
        class: "F"
        required: true
        description: "Contrato OpenAPI para endpoint health - validação contra openapi.json"
        anchors:
          api.operation_id: "health_api_v1_health_get"
          api.method: "GET"
          api.path: "/api/v1/health"
          api.responses:
            - "200"
          api.security: "none"

    tests:
      primary: "tests/training/invariants/test_inv_train_040_health_contract.py"
      node: "TestInvTrain040HealthContract"
    ```
    """

    @staticmethod
    def _load_openapi_spec() -> dict:
        """Load OpenAPI JSON from generated schema"""
        openapi_path = Path(__file__).parents[3] / "docs" / "_generated" / "openapi.json"
        with open(openapi_path, encoding="utf-8") as f:
            return json.load(f)

    def test_operation_id_exists_in_openapi(self):
        """Valida que o operationId health_check_api_v1_health_get existe no openapi.json"""
        openapi_spec = self._load_openapi_spec()
        
        # Find all operationIds in the spec
        operation_ids = []
        for path_obj in openapi_spec.get("paths", {}).values():
            for method_obj in path_obj.values():
                if isinstance(method_obj, dict) and "operationId" in method_obj:
                    operation_ids.append(method_obj["operationId"])
        
        expected_operation_id = "health_api_v1_health_get"
        assert expected_operation_id in operation_ids, (
            f"operationId '{expected_operation_id}' not found in openapi.json. "
            f"Found: {operation_ids}"
        )

    def test_method_and_path_match_spec(self):
        """Valida que GET /api/v1/health existe no openapi.json"""
        openapi_spec = self._load_openapi_spec()
        
        expected_path = "/api/v1/health"
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

    def test_response_200_documented(self):
        """Valida que resposta 200 está documentada para GET /api/v1/health"""
        openapi_spec = self._load_openapi_spec()
        
        path_obj = openapi_spec["paths"]["/api/v1/health"]
        method_obj = path_obj["get"]
        
        responses = method_obj.get("responses", {})
        assert "200" in responses, (
            f"Response code '200' not documented for GET /api/v1/health. "
            f"Documented responses: {list(responses.keys())}"
        )
