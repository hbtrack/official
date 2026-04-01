from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


ALLOWED_FRESHNESS_MODES = {
    "template_parity",
    "contract_driven_parity",
    "schema_guarded",
    "runtime_audited",
    "adr_bound",
    "registry_guarded",
    "decision_trace",
    "domain_governed",
}


def _load_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise ValueError(f"{path} deve conter objeto YAML no topo.")
    return data


def _looks_like_glob(value: str) -> bool:
    return any(token in value for token in ("*", "?", "["))


def _expand_pattern(root: Path, pattern: str) -> set[str]:
    return {
        path.relative_to(root).as_posix()
        for path in root.glob(pattern)
        if path.is_file()
    }


def _resolve_reference(root: Path, ref: str) -> list[str]:
    if ref == "self":
        return ["self"]
    if _looks_like_glob(ref):
        return sorted(_expand_pattern(root, ref))
    target = root / ref
    if target.exists():
        return [ref]
    return []


def _expand_scope(root: Path, scope: dict[str, Any]) -> set[str]:
    include = scope.get("include") or []
    exclude = scope.get("exclude") or []
    if not isinstance(include, list) or not include:
        raise ValueError("scope.include deve ser uma lista não vazia.")
    if not isinstance(exclude, list):
        raise ValueError("scope.exclude deve ser uma lista.")

    included: set[str] = set()
    for pattern in include:
        if not isinstance(pattern, str) or not pattern.strip():
            raise ValueError("scope.include contém pattern inválido.")
        included |= _expand_pattern(root, pattern)

    excluded: set[str] = set()
    for pattern in exclude:
        if not isinstance(pattern, str) or not pattern.strip():
            raise ValueError("scope.exclude contém pattern inválido.")
        excluded |= _expand_pattern(root, pattern)

    return included - excluded


def _expand_entry_paths(root: Path, entry: dict[str, Any]) -> tuple[set[str], list[dict[str, Any]]]:
    violations: list[dict[str, Any]] = []
    matched: set[str] = set()

    paths = entry.get("paths") or []
    if paths is not None and not isinstance(paths, list):
        violations.append({
            "blocking_code": "BLOCKED_DOC_USAGE_INVALID",
            "artifact": entry.get("rule_id", "<unknown>"),
            "message": "Campo 'paths' deve ser lista.",
            "severity": "error",
        })
        paths = []

    path_globs = entry.get("path_globs") or []
    if path_globs is not None and not isinstance(path_globs, list):
        violations.append({
            "blocking_code": "BLOCKED_DOC_USAGE_INVALID",
            "artifact": entry.get("rule_id", "<unknown>"),
            "message": "Campo 'path_globs' deve ser lista.",
            "severity": "error",
        })
        path_globs = []

    for path_str in paths:
        if not isinstance(path_str, str) or not path_str.strip():
            violations.append({
                "blocking_code": "BLOCKED_DOC_USAGE_INVALID",
                "artifact": entry.get("rule_id", "<unknown>"),
                "message": "Campo 'paths' contém valor inválido.",
                "severity": "error",
            })
            continue
        target = root / path_str
        if not target.is_file():
            violations.append({
                "blocking_code": "BLOCKED_DOC_USAGE_INVALID",
                "artifact": entry.get("rule_id", "<unknown>"),
                "message": f"Path literal ausente no manifesto: {path_str}",
                "severity": "error",
            })
            continue
        matched.add(path_str)

    for pattern in path_globs:
        if not isinstance(pattern, str) or not pattern.strip():
            violations.append({
                "blocking_code": "BLOCKED_DOC_USAGE_INVALID",
                "artifact": entry.get("rule_id", "<unknown>"),
                "message": "Campo 'path_globs' contém pattern inválido.",
                "severity": "error",
            })
            continue
        expanded = _expand_pattern(root, pattern)
        if not expanded:
            violations.append({
                "blocking_code": "BLOCKED_DOC_USAGE_INVALID",
                "artifact": entry.get("rule_id", "<unknown>"),
                "message": f"Pattern sem match no repositório: {pattern}",
                "severity": "error",
            })
            continue
        matched |= expanded

    return matched, violations


def evaluate_doc_usage(root: Path) -> dict[str, Any]:
    manifest_path = root / "docs" / "_canon" / "DOC_USAGE_MANIFEST.yaml"
    checked: list[str] = [str(manifest_path)]

    if not manifest_path.exists():
        return {
            "status": "SKIP_NOT_APPLICABLE",
            "summary": "DOC_USAGE_MANIFEST.yaml ausente.",
            "checked": checked,
            "violations": [],
        }

    try:
        manifest = _load_yaml(manifest_path)
    except Exception as exc:
        return {
            "status": "FAIL",
            "summary": f"Manifesto inválido: {exc}",
            "checked": checked,
            "violations": [{
                "blocking_code": "BLOCKED_DOC_USAGE_INVALID",
                "artifact": "docs/_canon/DOC_USAGE_MANIFEST.yaml",
                "message": f"Falha ao carregar manifesto: {exc}",
                "severity": "error",
            }],
        }

    violations: list[dict[str, Any]] = []

    scope = manifest.get("scope") or {}
    if not isinstance(scope, dict):
        scope = {}
        violations.append({
            "blocking_code": "BLOCKED_DOC_USAGE_INVALID",
            "artifact": "docs/_canon/DOC_USAGE_MANIFEST.yaml",
            "message": "Campo 'scope' deve ser objeto.",
            "severity": "error",
        })

    try:
        target_docs = _expand_scope(root, scope)
    except Exception as exc:
        return {
            "status": "FAIL",
            "summary": f"Escopo do manifesto inválido: {exc}",
            "checked": checked,
            "violations": [{
                "blocking_code": "BLOCKED_DOC_USAGE_INVALID",
                "artifact": "docs/_canon/DOC_USAGE_MANIFEST.yaml",
                "message": str(exc),
                "severity": "error",
            }],
        }

    checked.extend(sorted(target_docs))

    entries = manifest.get("entries") or []
    if not isinstance(entries, list) or not entries:
        return {
            "status": "FAIL",
            "summary": "Manifesto sem entradas.",
            "checked": checked,
            "violations": [{
                "blocking_code": "BLOCKED_DOC_USAGE_INVALID",
                "artifact": "docs/_canon/DOC_USAGE_MANIFEST.yaml",
                "message": "Campo 'entries' deve ser lista não vazia.",
                "severity": "error",
            }],
        }

    coverage: dict[str, list[str]] = {path: [] for path in target_docs}

    for entry in entries:
        if not isinstance(entry, dict):
            violations.append({
                "blocking_code": "BLOCKED_DOC_USAGE_INVALID",
                "artifact": "docs/_canon/DOC_USAGE_MANIFEST.yaml",
                "message": "Toda entry deve ser objeto.",
                "severity": "error",
            })
            continue

        rule_id = entry.get("rule_id")
        doc_class = entry.get("class")
        owner_source = entry.get("owner_source")
        consumers = entry.get("consumers")
        freshness_mode = entry.get("freshness_mode")
        update_triggers = entry.get("update_triggers")
        generated_by = entry.get("generated_by")

        if not isinstance(rule_id, str) or not rule_id.strip():
            violations.append({
                "blocking_code": "BLOCKED_DOC_USAGE_INVALID",
                "artifact": "docs/_canon/DOC_USAGE_MANIFEST.yaml",
                "message": "Toda entry deve declarar rule_id.",
                "severity": "error",
            })
            continue

        if not isinstance(doc_class, str) or not doc_class.strip():
            violations.append({
                "blocking_code": "BLOCKED_DOC_USAGE_INVALID",
                "artifact": rule_id,
                "message": "Campo 'class' é obrigatório.",
                "severity": "error",
            })

        if not isinstance(owner_source, str) or not owner_source.strip():
            violations.append({
                "blocking_code": "BLOCKED_DOC_USAGE_INVALID",
                "artifact": rule_id,
                "message": "Campo 'owner_source' é obrigatório.",
                "severity": "error",
            })
        else:
            resolved_owner = _resolve_reference(root, owner_source)
            if not resolved_owner:
                violations.append({
                    "blocking_code": "BLOCKED_DOC_USAGE_INVALID",
                    "artifact": rule_id,
                    "message": f"owner_source não resolve: {owner_source}",
                    "severity": "error",
                })
            else:
                checked.extend(ref for ref in resolved_owner if ref != "self")

        if not isinstance(consumers, list) or not consumers:
            violations.append({
                "blocking_code": "BLOCKED_DOC_USAGE_INVALID",
                "artifact": rule_id,
                "message": "Campo 'consumers' deve ser lista não vazia.",
                "severity": "error",
            })
        else:
            for consumer in consumers:
                if not isinstance(consumer, str) or not consumer.strip():
                    violations.append({
                        "blocking_code": "BLOCKED_DOC_USAGE_INVALID",
                        "artifact": rule_id,
                        "message": "Campo 'consumers' contém valor inválido.",
                        "severity": "error",
                    })
                    continue
                resolved = _resolve_reference(root, consumer)
                if not resolved:
                    violations.append({
                        "blocking_code": "BLOCKED_DOC_USAGE_INVALID",
                        "artifact": rule_id,
                        "message": f"Consumer não resolve: {consumer}",
                        "severity": "error",
                    })
                    continue
                checked.extend(ref for ref in resolved if ref != "self")

        if not isinstance(freshness_mode, str) or freshness_mode not in ALLOWED_FRESHNESS_MODES:
            violations.append({
                "blocking_code": "BLOCKED_DOC_USAGE_INVALID",
                "artifact": rule_id,
                "message": (
                    "Campo 'freshness_mode' inválido. "
                    f"Esperado um de: {sorted(ALLOWED_FRESHNESS_MODES)}"
                ),
                "severity": "error",
            })

        if not isinstance(update_triggers, list) or not update_triggers:
            violations.append({
                "blocking_code": "BLOCKED_DOC_USAGE_INVALID",
                "artifact": rule_id,
                "message": "Campo 'update_triggers' deve ser lista não vazia.",
                "severity": "error",
            })
        else:
            for trigger in update_triggers:
                if not isinstance(trigger, str) or not trigger.strip():
                    violations.append({
                        "blocking_code": "BLOCKED_DOC_USAGE_INVALID",
                        "artifact": rule_id,
                        "message": "Campo 'update_triggers' contém valor inválido.",
                        "severity": "error",
                    })
                    continue
                resolved = _resolve_reference(root, trigger)
                if not resolved:
                    violations.append({
                        "blocking_code": "BLOCKED_DOC_USAGE_INVALID",
                        "artifact": rule_id,
                        "message": f"Update trigger não resolve: {trigger}",
                        "severity": "error",
                    })
                    continue
                checked.extend(ref for ref in resolved if ref != "self")

        if generated_by is not None:
            if not isinstance(generated_by, str) or not generated_by.strip():
                violations.append({
                    "blocking_code": "BLOCKED_DOC_USAGE_INVALID",
                    "artifact": rule_id,
                    "message": "Campo 'generated_by', quando presente, deve ser string não vazia.",
                    "severity": "error",
                })
            else:
                resolved_generator = _resolve_reference(root, generated_by)
                if not resolved_generator:
                    violations.append({
                        "blocking_code": "BLOCKED_DOC_USAGE_INVALID",
                        "artifact": rule_id,
                        "message": f"generated_by não resolve: {generated_by}",
                        "severity": "error",
                    })
                else:
                    checked.extend(ref for ref in resolved_generator if ref != "self")

        matched_paths, path_violations = _expand_entry_paths(root, entry)
        violations.extend(path_violations)
        if not matched_paths:
            violations.append({
                "blocking_code": "BLOCKED_DOC_USAGE_INVALID",
                "artifact": rule_id,
                "message": "Entry não cobre nenhum documento real.",
                "severity": "error",
            })
            continue

        outside_scope = sorted(path for path in matched_paths if path not in target_docs)
        if outside_scope:
            violations.append({
                "blocking_code": "BLOCKED_DOC_USAGE_INVALID",
                "artifact": rule_id,
                "message": "Entry cobre documentos fora do escopo declarado.",
                "severity": "error",
                "details": {"outside_scope": outside_scope[:20]},
            })

        for path in sorted(matched_paths & target_docs):
            coverage[path].append(rule_id)

    for doc_path, matches in sorted(coverage.items()):
        if not matches:
            violations.append({
                "blocking_code": "BLOCKED_DOC_USAGE_INVALID",
                "artifact": doc_path,
                "message": "Documento fora do manifesto de uso/freshness.",
                "severity": "error",
            })
        elif len(matches) > 1:
            violations.append({
                "blocking_code": "BLOCKED_DOC_USAGE_INVALID",
                "artifact": doc_path,
                "message": "Documento mapeado por múltiplas regras do manifesto.",
                "severity": "error",
                "details": {"matching_rules": sorted(matches)},
            })

    status = "FAIL" if violations else "PASS"
    summary = (
        f"Cobertura de documentação válida para {len(target_docs)} documento(s)."
        if not violations
        else f"{len(violations)} violação(ões) no manifesto de uso/freshness da documentação."
    )
    return {
        "status": status,
        "summary": summary,
        "checked": sorted(dict.fromkeys(checked)),
        "violations": violations,
    }
