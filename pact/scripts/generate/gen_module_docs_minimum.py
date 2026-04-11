from __future__ import annotations

import argparse
import pathlib
import re


def _repo_root() -> pathlib.Path:
    return pathlib.Path(__file__).resolve().parents[2]


def _read_text(path: pathlib.Path) -> str:
    return path.read_text(encoding="utf-8")


def _layout_path(root: pathlib.Path) -> pathlib.Path:
    return root / ".contract_driven" / "CONTRACT_SYSTEM_LAYOUT.md"


def _load_canonical_modules_from_layout(root: pathlib.Path) -> list[str]:
    """
    SSOT de módulos: `.contract_driven/CONTRACT_SYSTEM_LAYOUT.md` seção 2.
    Extrai os módulos listados em 2.1 e 2.2 (bullets `- <module>`).
    """
    lp = _layout_path(root)
    if not lp.exists():
        raise FileNotFoundError(str(lp))
    text = _read_text(lp)
    modules: list[str] = []
    in_taxonomy = False
    for line in text.splitlines():
        if line.startswith("### 2.1 "):
            in_taxonomy = True
            continue
        if line.startswith("### 2.2 "):
            in_taxonomy = True
            continue
        if line.startswith("### 2.3 "):
            break
        if not in_taxonomy:
            continue
        m = re.match(r"^\s*-\s*`?([a-z0-9]+(?:_[a-z0-9]+)*)`?\s*$", line)
        if m:
            modules.append(m.group(1))

    seen: set[str] = set()
    out: list[str] = []
    for mod in modules:
        if mod in seen:
            continue
        seen.add(mod)
        out.append(mod)
    if not out:
        raise RuntimeError("Nenhum módulo encontrado no LAYOUT (seção 2.1/2.2).")
    return out


def _handball_applicability(module: str) -> bool:
    # Conservador: marca como aplicável apenas quando o módulo tipicamente incorpora
    # semântica derivada de regra esportiva (gatilho RULES seção 12).
    return module in {"matches", "competitions", "scout"}


def _front_matter(module: str) -> str:
    return (
        "---\n"
        f"module: \"{module}\"\n"
        "system_scope_ref: \"../../../_canon/SYSTEM_SCOPE.md\"\n"
        "handball_rules_ref: \"../../../_canon/HANDBALL_RULES_DOMAIN.md\"\n"
        f"handball_semantic_applicability: {'true' if _handball_applicability(module) else 'false'}\n"
        f"contract_path_ref: \"../../../../contracts/openapi/paths/{module}.yaml\"\n"
        f"schemas_ref: \"../../../../contracts/schemas/{module}/\"\n"
        "---\n\n"
    )


def _readme(module: str) -> str:
    return _front_matter(module) + (
        f"# {module}\n\n"
        "## Objetivo\n"
        f"Documentar o escopo normativo do módulo `{module}` e suas superfícies soberanas.\n\n"
        "## Superfícies soberanas (referências)\n"
        f"- HTTP (OpenAPI paths): `contracts/openapi/paths/{module}.yaml`\n"
        f"- Schemas de domínio: `contracts/schemas/{module}/`\n"
        f"- Workflows (Arazzo): `contracts/workflows/{module}/` (quando aplicável)\n"
        "- Eventos (AsyncAPI): `contracts/asyncapi/` (quando aplicável)\n\n"
        "## Fontes globais vinculantes\n"
        "- `docs/_canon/SYSTEM_SCOPE.md`\n"
        "- `docs/_canon/HANDBALL_RULES_DOMAIN.md` (quando o gatilho de handebol aplicar)\n"
        "- SSOT de convenções/templates de API HTTP: `.contract_driven/templates/api/api_rules.yaml`\n"
    )


def _module_scope(module: str) -> str:
    up = module.upper()
    return _front_matter(module) + (
        f"# MODULE_SCOPE_{up}.md\n\n"
        "## Responsabilidades\n"
        f"- Definir as responsabilidades do módulo `{module}`.\n"
        "- Declarar limites e boundaries com outros módulos quando houver risco de sobreposição.\n\n"
        "## Fora do escopo\n"
        "- Qualquer responsabilidade fora da taxonomia canônica deve ser formalizada via ADR antes de existir.\n\n"
        "## Dependências e integrações\n"
        "- Descrever integrações relevantes quando existirem (sem inferência).\n"
    )


def _domain_rules(module: str) -> str:
    up = module.upper()
    return _front_matter(module) + (
        f"# DOMAIN_RULES_{up}.md\n\n"
        "## Regras de domínio\n"
        "Ainda não há regras específicas registradas para este módulo.\n\n"
        "Regra operacional:\n"
        "- Quando uma regra existir, registrá-la aqui e refletir a implicação nos contratos (OpenAPI/Schema/Workflow/Eventos) da superfície correta.\n"
    )


def _invariants(module: str) -> str:
    up = module.upper()
    return _front_matter(module) + (
        f"# INVARIANTS_{up}.md\n\n"
        "## Invariantes locais\n"
        "Nenhum invariante local adicional está registrado neste módulo no momento.\n\n"
        "## Invariantes globais vinculantes\n"
        "- `.contract_driven/DOMAIN_AXIOMS.json`\n"
        "- `docs/_canon/GLOBAL_INVARIANTS.md`\n"
    )


def _test_matrix(module: str) -> str:
    up = module.upper()
    return _front_matter(module) + (
        f"# TEST_MATRIX_{up}.md\n\n"
        "## Objetivo\n"
        "Definir a matriz mínima de testes e evidências que sustentam os contratos do módulo.\n\n"
        "## Matriz (mínimo)\n"
        "| ID | Artefato | Tipo de verificação | Obrigatório | Evidência |\n"
        "|---|---|---|:---:|---|\n"
        f"| TM-001 | `contracts/openapi/paths/{module}.yaml` | Lint OpenAPI (Redocly/Spectral) | Sim | `_reports/contract_gates/latest.json` |\n"
        f"| TM-002 | `contracts/schemas/{module}/` | Validação JSON Schema | Sim | `_reports/contract_gates/latest.json` |\n"
        f"| TM-003 | `DOMAIN_RULES_{up}.md` | Revisão normativa + testes de regra (quando existir) | Condicional | `_reports/contract_gates/latest.json` |\n"
        f"| TM-004 | `INVARIANTS_{up}.md` | Teste de invariantes (quando existir) | Condicional | `_reports/contract_gates/latest.json` |\n"
    )


def _write_if_needed(path: pathlib.Path, content: str, force: bool) -> bool:
    if path.exists() and not force:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return True


def main() -> int:
    ap = argparse.ArgumentParser(description="Gera docs mínimas por módulo (idempotente).")
    ap.add_argument("--force", action="store_true", help="Sobrescreve arquivos existentes.")
    args = ap.parse_args()

    root = _repo_root()
    modules = _load_canonical_modules_from_layout(root)

    created = 0
    for mod in modules:
        base = root / "docs" / "hbtrack" / "modulos" / mod
        created += int(_write_if_needed(base / "README.md", _readme(mod), args.force))
        created += int(_write_if_needed(base / f"MODULE_SCOPE_{mod.upper()}.md", _module_scope(mod), args.force))
        created += int(_write_if_needed(base / f"DOMAIN_RULES_{mod.upper()}.md", _domain_rules(mod), args.force))
        created += int(_write_if_needed(base / f"INVARIANTS_{mod.upper()}.md", _invariants(mod), args.force))
        created += int(_write_if_needed(base / f"TEST_MATRIX_{mod.upper()}.md", _test_matrix(mod), args.force))

    print(f"OK: {created} arquivo(s) criado(s)/atualizado(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
