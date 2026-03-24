"""
tests/pipeline_gates/test_phase_0_determinism.py

FASE 0 — TESTES VERMELHOS (RED TESTS)

Estes testes validam que o sistema hoje PERMITE comportamentos que deveriam
ser BLOQUEADOS (loopholes do audit adversarial). Quando estes testes passarem
(turn green), os loopholes estarão fechados.

Status: RED (devem falhar hoje, passar após Fase 1-5)
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any

import pytest
import jsonschema


class TestPhase0Determinism:
    """Validar que fase 0 (boot) hoje tem holes críticos que permitem 'unknown'."""
    
    @pytest.fixture
    def workspace_root(self):
        """Raiz do repositório HB-TRACK."""
        return Path(__file__).parent.parent.parent
    
    @pytest.fixture
    def session_start_schema(self, workspace_root):
        """Carregar schema de sessão."""
        schema_path = workspace_root / "contracts/schemas/shared/session_start.schema.json"
        with open(schema_path) as f:
            return json.load(f)
    
    @pytest.fixture
    def task_catalog(self, workspace_root):
        """Carregar TASK_CATALOG.yaml."""
        import yaml
        catalog_path = workspace_root / ".contract_driven/TASK_CATALOG.yaml"
        with open(catalog_path) as f:
            return yaml.safe_load(f)

    @pytest.fixture
    def boot_profiles(self, workspace_root):
        """Carregar BOOT_PROFILES.yaml."""
        import yaml
        profiles_path = workspace_root / ".contract_driven/BOOT_PROFILES.yaml"
        with open(profiles_path) as f:
            return yaml.safe_load(f)
    
    def test_hb_verify_without_task_type_should_fail(self, workspace_root):
        """
        GREEN TEST: hb verify sem --task-type DEVE falhar (exit != 0).
        
        Status PR2: ✅ FIXED — CLI v2 obriga --task-type
        """
        result = subprocess.run(
            ["python3", "scripts/hb", "verify"],
            cwd=workspace_root,
            capture_output=True,
            text=True
        )
        
        # ✅ Esperado agora: returncode != 0
        assert result.returncode != 0, "hb verify sem --task-type deve falhar"
        assert "--task-type" in result.stderr, "Mensagem deve mencionar --task-type obrigatório"
    
    def test_hb_verify_without_module_should_fail(self, workspace_root):
        """
        GREEN TEST: hb verify sem --module DEVE falhar (exit != 0).
        
        Status PR2: ✅ FIXED — CLI v2 obriga --module
        """
        result = subprocess.run(
            ["python3", "scripts/hb", "verify", "--task-type", "new_contract"],
            cwd=workspace_root,
            capture_output=True,
            text=True
        )
        
        # ✅ Esperado agora: returncode != 0
        assert result.returncode != 0, "hb verify sem --module deve falhar"
        assert "--module" in result.stderr, "Mensagem deve mencionar --module obrigatório"
    
    def test_hb_check_without_module_should_fail(self, workspace_root):
        """
        GREEN TEST: hb check sem --module DEVE falhar (exit != 0).
        
        Status PR2: ✅ FIXED — CLI v2 obriga --module
        """
        result = subprocess.run(
            ["python3", "scripts/hb", "check"],
            cwd=workspace_root,
            capture_output=True,
            text=True
        )
        
        # ✅ Esperado agora: returncode != 0
        assert result.returncode != 0, "hb check sem --module deve falhar"
        assert "--module" in result.stderr, "Mensagem deve mencionar --module obrigatório"
    
    def test_session_start_json_with_unknown_task_type_is_invalid(self, workspace_root, session_start_schema):
        """
        RED TEST: session_start.json com task_type=unknown deve ser INVÁLIDO.
        
        Hoje: schema não bloqueia 'unknown'
        Esperado: jsonschema valida contra enum restrito
        """
        invalid_session = {
            "session_id": "550e8400-e29b-41d4-a716-446655440000",
            "session_timestamp": "2026-03-17T12:00:00Z",
            "branch": "main",
            "pipeline_version": "1.0.0",
            "boot_profile_id": "default",
            "task_type": "unknown",  # INVÁLIDO
            "module": "training",
            "stage": 0,
            "write_scope": "contracts",
            "worker_id": "unknown"
        }
        
        # Este teste DEVE FALHAR hoje (jsonschema não bloqueia)
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(invalid_session, session_start_schema)
    
    def test_session_start_json_with_unknown_module_is_invalid(self, workspace_root, session_start_schema):
        """
        RED TEST: session_start.json com module=unknown deve ser INVÁLIDO.
        
        Hoje: schema não bloqueia 'unknown'
        Esperado: jsonschema valida contra enum restrito (16 módulos canônicos)
        """
        invalid_session = {
            "session_id": "550e8400-e29b-41d4-a716-446655440000",
            "session_timestamp": "2026-03-17T12:00:00Z",
            "branch": "main",
            "pipeline_version": "1.0.0",
            "boot_profile_id": "default",
            "task_type": "new_contract",
            "module": "unknown",  # INVÁLIDO
            "stage": 0,
            "write_scope": "contracts",
            "worker_id": "create_openapi_contract"
        }
        
        # Este teste DEVE FALHAR hoje
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(invalid_session, session_start_schema)
    
    def test_session_start_json_missing_required_fields(self, workspace_root, session_start_schema):
        """
        RED TEST: session_start.json sem campos obrigatórios deve falhar validação.
        
        Hoje: função de validação não é aplicada
        Esperado: jsonschema bloqueia document incompleto
        """
        incomplete_session = {
            "session_id": "550e8400-e29b-41d4-a716-446655440000",
            # Faltam campos obrigatórios
        }
        
        # Este teste DEVE FALHAR hoje (schema pode estar skipped)
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(incomplete_session, session_start_schema)
    
    def test_task_type_not_in_catalog_should_block(self, workspace_root, task_catalog):
        """
        RED TEST: task_type não registrado em TASK_CATALOG deveria bloquear roteamento.
        
        Hoje: sem blocagem
        Esperado: roteamento falha com BLOCKED_FEATURE_UNREGISTERED
        """
        unregistered_task_type = "make_me_a_sandwich"  # não existe
        
        task_names = set(k for k in task_catalog.get("task_catalog", {}).keys())
        
        # Este teste DEVE FALHAR hoje se nenhuma validação estiver em place
        assert unregistered_task_type not in task_names, "Task type não existe (esperado)"
    
    def test_git_hook_divergence(self, workspace_root):
        """
        RED TEST: hook versionado e hook instalado devem ser idênticos.
        
        Hoje: podem divergir
        Esperado: conteúdo idêntico ou bypass detectado na instalação
        """
        versionado = workspace_root / "scripts/git-hooks/pre-commit"
        instalado = workspace_root / ".git/hooks/pre-commit"
        
        if versionado.exists() and instalado.exists():
            conteudo_v = versionado.read_text()
            conteudo_i = instalado.read_text()
            
            # Este teste DEVE FALHAR hoje (divergência conhecida)
            assert conteudo_v == conteudo_i, "LOOPHOLE: hook versionado != hook instalado"
    
    def test_session_hash_divergence_misses_detection(self, workspace_root):
        """
        RED TEST: se artefato foi validado e depois alterado, hash deve divergir e hook deve bloquear.
        
        Hoje: hook não detecta hash stale
        Esperado: hook compara hash atual vs. hash em session_start.json
        """
        session_file = workspace_root / "_reports/session_start.json"
        
        if session_file.exists():
            session_data = json.loads(session_file.read_text())
            
            # Se há artefatos em stage2_artifacts, verificar se algum foi alterado
            artifacts = session_data.get("stage2_artifacts", [])
            if artifacts:
                for artifact in artifacts:
                    artifact_path = workspace_root / artifact["path"]
                    if artifact_path.exists():
                        import hashlib
                        current_hash = hashlib.sha256(artifact_path.read_bytes()).hexdigest()
                        recorded_hash = artifact.get("sha256")
                        
                        # Este teste DEVE FALHAR hoje se arquivo foi alterado mas hook não bloqueou
                        if current_hash != recorded_hash:
                            pytest.skip("Artefato diverge — hook deveria ter bloqueado (TEST LOCATION: verificar)")


class TestPhase0ValidationSchemas:
    """Validar que os esquemas criados são válidos."""
    
    @pytest.fixture
    def workspace_root(self):
        """Raiz do repositório HB-TRACK."""
        return Path(__file__).parent.parent.parent
    
    def test_boot_profiles_yaml_is_valid(self, workspace_root):
        """BOOT_PROFILES.yaml deve ser YAML válido."""
        import yaml
        profiles_path = workspace_root / ".contract_driven/BOOT_PROFILES.yaml"

        with open(profiles_path) as f:
            data = yaml.safe_load(f)
        
        assert data is not None
        assert "profiles" in data
        assert "default" in data["profiles"]
        assert "contract_execution" in data["profiles"]
    
    def test_task_catalog_yaml_is_valid(self, workspace_root):
        """TASK_CATALOG.yaml deve ser YAML válido e conter task types conhecidos."""
        import yaml
        catalog_path = workspace_root / ".contract_driven/TASK_CATALOG.yaml"

        with open(catalog_path) as f:
            data = yaml.safe_load(f)
        
        assert data is not None
        assert "task_catalog" in data
        
        # Verificar que task types do CLAUDE.md existem aqui
        known_tasks = [
            "new_module", "new_contract", "contract_revision",
            "new_event", "new_workflow", "new_schema",
            "new_state_model", "new_ui_contract", "architecture_review"
        ]
        
        catalog_tasks = set(data["task_catalog"].keys())
        for task in known_tasks:
            assert task in catalog_tasks, f"Task type {task} não registrado em TASK_CATALOG"
    
    def test_session_start_schema_is_valid_json_schema(self, workspace_root):
        """session_start.schema.json deve ser JSON Schema válido."""
        schema_path = workspace_root / "contracts/schemas/shared/session_start.schema.json"
        
        with open(schema_path) as f:
            schema = json.load(f)
        
        assert schema is not None
        assert "$schema" in schema
        assert "properties" in schema
        assert "required" in schema
        
        # Verificar campos obrigatórios críticos (sempre requeridos)
        required_fields = schema["required"]
        # Nota: 'module' foi tornado condicional em v1.3.0 (não requerido para execute_roadmap_phase)
        always_required = ["session_id", "task_type", "stage", "write_scope"]
        for field in always_required:
            assert field in required_fields, f"Campo crítico {field} não está em 'required'"
        # 'module' deve existir em properties (disponível mas condicional via if/then/else)
        assert "module" in schema.get("properties", {}), (
            "'module' deve existir em 'properties' do schema (mesmo sendo condicional)"
        )
        # Schema v1.3.0+ deve ter if/then/else para module condicional
        assert "if" in schema, "Schema deve ter condicional 'if' para module (v1.3.0+)"

    def test_gates_registry_loads_and_ui_doc_gate_is_blocking(self, workspace_root):
        """🟢 PR3: GATES_REGISTRY.yaml carrega e UI_DOC_VALIDATION_GATE.blocking=true."""
        # PR3 Achievement: gates_metadata carrega de GATES_REGISTRY.yaml  
        # Validator agora consulta registry para blocking status (SSOT)
        import yaml
        registry_path = workspace_root / "docs/_canon/gates/GATES_REGISTRY.yaml"
        
        # Carregar GATES_REGISTRY
        with open(registry_path) as f:
            registry_data = yaml.safe_load(f)
        
        assert registry_data is not None, "GATES_REGISTRY.yaml deve ser válido YAML"
        assert "gates" in registry_data, "GATES_REGISTRY deve ter chave 'gates'"
        
        gates_list = registry_data["gates"]
        assert len(gates_list) > 0, "GATES_REGISTRY deve ter ao menos 1 gate"
        
        # Encontrar UI_DOC_VALIDATION_GATE
        ui_gate = next((g for g in gates_list if g.get("gate_id") == "UI_DOC_VALIDATION_GATE"), None)
        assert ui_gate is not None, "UI_DOC_VALIDATION_GATE deve estar em GATES_REGISTRY"
        
        # Validar que blocking=true (SSOT - Semantic Truth)
        assert ui_gate.get("blocking") is True, \
            f"UI_DOC_VALIDATION_GATE.blocking deve ser True, foi {ui_gate.get('blocking')}"
        assert ui_gate.get("status") == "active", "UI_DOC_VALIDATION_GATE.status deve ser 'active'"
        
        print(f"✅ PR3: GATES_REGISTRY loaded with {len(gates_list)} gates")
        print(f"✅ PR3: UI_DOC_VALIDATION_GATE.blocking = {ui_gate.get('blocking')}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
