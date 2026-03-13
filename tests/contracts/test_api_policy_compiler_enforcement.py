import pathlib
import shutil

import pytest
import yaml

from scripts.contracts.validate.api.policy_compiler import PolicyCompilerError, compile_expected


def _copy_file(repo_root: pathlib.Path, tmp_root: pathlib.Path, relpath: str) -> None:
    src = repo_root / relpath
    dst = tmp_root / relpath
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dst)


def _make_min_repo(tmp_path: pathlib.Path) -> pathlib.Path:
    repo_root = pathlib.Path(__file__).resolve().parents[2]
    # inputs obrigatórios do compiler
    for rel in [
        ".contract_driven/DOMAIN_AXIOMS.json",
        ".contract_driven/templates/api/ARCHITECTURE_MATRIX.yaml",
        ".contract_driven/templates/api/MODULE_PROFILE_REGISTRY.yaml",
        ".contract_driven/templates/api/CANONICAL_TYPE_REGISTRY.yaml",
        ".contract_driven/templates/api/api_rules.yaml",
    ]:
        _copy_file(repo_root, tmp_path, rel)

    # subset AsyncAPI (surface=event, módulo training)
    for rel in [
        "contracts/asyncapi/asyncapi.yaml",
        "contracts/asyncapi/channels/training_attendance_marked.yaml",
        "contracts/asyncapi/messages/training_attendance_marked.yaml",
        "contracts/asyncapi/components/schemas/training_attendance_marked_payload.yaml",
    ]:
        _copy_file(repo_root, tmp_path, rel)

    return tmp_path


def test_compile_training_event_ok(tmp_path: pathlib.Path):
    root = _make_min_repo(tmp_path)
    expected = compile_expected(root, module="training", surface="event")
    # deve incluir manifesto + policy resolvida
    rels = {e.relpath for e in expected}
    assert "generated/resolved_policy/training.event.resolved.yaml" in rels
    assert "generated/manifests/training.event.traceability.yaml" in rels


def test_compile_blocks_uuid_suffix_violation(tmp_path: pathlib.Path):
    root = _make_min_repo(tmp_path)
    payload_path = root / "contracts/asyncapi/components/schemas/training_attendance_marked_payload.yaml"
    doc = yaml.safe_load(payload_path.read_text(encoding="utf-8"))
    props = doc["properties"]
    # renomear userId -> userUuid (mesma semântica/uuid-v4, sufixo proibido)
    props["userUuid"] = props.pop("userId")
    payload_path.write_text(yaml.safe_dump(doc, sort_keys=True, allow_unicode=True), encoding="utf-8")

    with pytest.raises(PolicyCompilerError) as exc:
        compile_expected(root, module="training", surface="event")
    assert "sufixo proibido `Uuid`" in str(exc.value)


def test_compile_blocks_missing_semantic_id_binding(tmp_path: pathlib.Path):
    root = _make_min_repo(tmp_path)
    payload_path = root / "contracts/asyncapi/components/schemas/training_attendance_marked_payload.yaml"
    doc = yaml.safe_load(payload_path.read_text(encoding="utf-8"))
    # remover x-semantic-id de um campo que está em field_bindings
    doc["properties"]["trainingSessionId"].pop("x-semantic-id", None)
    payload_path.write_text(yaml.safe_dump(doc, sort_keys=True, allow_unicode=True), encoding="utf-8")

    with pytest.raises(PolicyCompilerError) as exc:
        compile_expected(root, module="training", surface="event")
    assert "x-semantic-id obrigatório" in str(exc.value)

