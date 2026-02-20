# 🚀 HB Track: Manual de Desenvolvimento com IA (Determinístico) — v1.0.2

## 📖 Índice

1. [Filosofia e Conceitos](#filosofia)
2. [Estrutura do Projeto](#estrutura)
3. [Instalação e Configuração](#instalacao)
4. [Código-Fonte Completo](#codigo)
5. [Ciclo de Vida (Workflow)](#workflow)
6. [Integração com Cline/IA](#integracao)
7. [Conceitos Avançados](#avancados)
8. [Checklist de Adoção](#checklist)
9. [BÔNUS: JSON de Teste](#bonus)

---

## <a name="filosofia"></a>📜 1. FILOSOFIA E CONCEITOS

O **HB Track** é um sistema de desenvolvimento orientado a **evidências e contratos**. Aqui, o código é um subproduto de um plano rigoroso e auditável.

### Princípios Fundamentais

* **Determinismo Real (auditável):** toda mudança “governada” passa por AR e gera evidência executável.
* **Evidência Obrigatória:** nenhuma AR é “✅ CONCLUÍDA” sem evidence pack com comando + exit code + stdout/stderr + contexto mínimo.
* **SSOT (Single Source of Truth):** os SSOTs vivem em `docs/ssot/` e o guardião detecta drift (staged e unstaged).

### Os 3 Pilares SSOT (já existentes em `docs/ssot/`)

| Arquivo                       | Função                                   | Importância |
| ----------------------------- | ---------------------------------------- | ----------- |
| `docs/ssot/schema.sql`        | Definição atual do banco de dados (SSOT) | ⭐⭐⭐ Crítico |
| `docs/ssot/openapi.json`      | Contrato das APIs (SSOT)                 | ⭐⭐⭐ Crítico |
| `docs/ssot/alembic_state.txt` | Estado das migrações (SSOT)              | ⭐⭐ Alta     |

---

## <a name="estrutura"></a>🗂️ 2. ESTRUTURA DO PROJETO (CANON)

A partir de agora, **não existe mais ambiguidade**: `docs/` é padronizado assim.

```
HB TRACK/
├── docs/
│   ├── _canon/                      # 🔒 Lei do repo (governança canônica)
│   │   ├── _agent/                  # Regras canônicas para agentes
│   │   └── UDS_TEMPLATES/           # Templates canônicos
│   │
│   ├── hbtrack/                     # 🎯 Tudo específico do HB Track (execução + rastreio)
│   │   ├── _generated/              # 🧪 DERIVED (gerado por scripts; não editar manualmente)
│   │   ├── ars/                     # 📋 ARs (tarefas governadas)
│   │   ├── contratos/               # 🧾 Contratos (AR CONTRACT, gates mínimos, formatos)
│   │   ├── evidence/                # 🔬 Evidence packs (logs auditáveis)
│   │   ├── modules/                 # 📦 Docs por módulo (técnico)
│   │   └── specs/                   # 📐 Specs (produto/arquitetura por feature)
│   │
│   ├── playbooks/                   # 🧭 Guias operacionais
│   ├── product/                     # 🧩 Produto/visão/escopo
│   └── ssot/                        # 🧱 SSOTs (já existem)
│       ├── schema.sql
│       ├── openapi.json
│       └── alembic_state.txt
│
├── scripts/                         # ⚙️ Apenas Python (.py)
│   ├── run/
│   │   └── hb.py                    # CLI “hb” (entrypoint)
│   └── git-hooks/
│       └── pre-commit               # Hook determinístico (Python)
│
└── src/                             # 💻 Código-fonte (ou ajuste GOVERNED_ROOTS para seus roots reais)
```

Regras de path (canon):

* Scripts sempre em `scripts/`
* ARs e evidências sempre em `docs/hbtrack/`
* SSOTs sempre em `docs/ssot/`
* `docs/hbtrack/_generated/` é DERIVED (gerado por script; não editar manualmente)
* `docs/_canon/` é lei (mudança só via AR de governança)

---

## <a name="instalacao"></a>⚙️ 3. INSTALAÇÃO E CONFIGURAÇÃO

### Passo 1: Criar a Estrutura de Pastas (somente o que não existe)

Linux/Mac/Git Bash:

```bash
mkdir -p docs/hbtrack/{_generated,ars,contratos,evidence,modules,specs}
mkdir -p scripts/{run,git-hooks}
```

Windows (cmd / PowerShell, equivalente):

* crie as pastas conforme a árvore (ou use Git Bash acima).

### Passo 2: Dependências

A CLI usa apenas:

* Python (biblioteca padrão)
* Git instalado e disponível no PATH

Não existe `pip install argparse` nem `pip install difflib`.

### Passo 3: Alias Global da CLI (opcional)

Você pode rodar direto:

* `python scripts/run/hb.py check`

Se quiser o comando `hb`:

Linux/Mac:

```bash
alias hb='python3 scripts/run/hb.py'
```

Windows PowerShell (recomendado usar caminho relativo dentro do repo):

```powershell
function hb { python scripts\run\hb.py @args }
```

### Passo 4: Ativar Hooks

```bash
git config core.hooksPath scripts/git-hooks
```

---

## <a name="codigo"></a>💻 4. CÓDIGO-FONTE COMPLETO

### 4.1 Script Principal: `scripts/run/hb.py`

Copie e cole como `scripts/run/hb.py`:

````python
#!/usr/bin/env python3
"""
HB Track CLI - Desenvolvimento Determinístico por AR + Evidência
Versão: 1.0.2
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


# -----------------------------
# CANON (paths)
# -----------------------------
AR_DIR = "docs/hbtrack/ars"
EV_DIR = "docs/hbtrack/evidence"
INDEX_FILE = "docs/hbtrack/_INDEX.md"

CONTRACTS_DIR = "docs/hbtrack/contratos"
GENERATED_DIR = "docs/hbtrack/_generated"

SSOT_FILES = [
    "docs/ssot/schema.sql",
    "docs/ssot/openapi.json",
    "docs/ssot/alembic_state.txt",
]

# -----------------------------
# GOVERNED ROOTS (IMPORTANTE)
# -----------------------------
# Ajuste esta lista para refletir ONDE seu código realmente vive.
# Se o seu repo não usa `src/`, substitua por `backend/`, `Ftonted/`, etc.
GOVERNED_ROOTS = [
    "src/",
]


# -----------------------------
# Helpers
# -----------------------------
def _now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _safe_slug(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r"\s+", "_", s)
    s = re.sub(r"[^a-z0-9_]+", "", s)
    return s or "untitled"


def _run(cmd: List[str], check: bool = False, capture: bool = True, text: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, check=check, capture_output=capture, text=text)


def _git(args: List[str]) -> subprocess.CompletedProcess:
    return _run(["git"] + args)


def _ensure_dirs() -> None:
    for p in [AR_DIR, EV_DIR, CONTRACTS_DIR, GENERATED_DIR]:
        os.makedirs(p, exist_ok=True)
    if not os.path.exists(INDEX_FILE):
        with open(INDEX_FILE, "w", encoding="utf-8") as f:
            f.write("# 📑 Índice de Architectural Records (ARs)\n\n")


def _is_git_repo() -> bool:
    r = _git(["rev-parse", "--is-inside-work-tree"])
    return r.returncode == 0 and (r.stdout or "").strip() == "true"


def _staged_files() -> List[str]:
    r = _git(["diff", "--cached", "--name-only"])
    if r.returncode != 0:
        return []
    return [line.strip() for line in (r.stdout or "").splitlines() if line.strip()]


def _has_prefix(path: str, prefixes: List[str]) -> bool:
    return any(path.startswith(p) for p in prefixes)


def _read_index_version(path: str) -> str:
    """
    Lê o conteúdo staged (index) do arquivo. Falha se não estiver staged.
    """
    r = _git(["show", f":{path}"])
    if r.returncode != 0:
        raise RuntimeError(f"Não foi possível ler versão staged de: {path}")
    return r.stdout or ""


def _find_ar_file_by_id(ar_id: str) -> Optional[str]:
    if not os.path.isdir(AR_DIR):
        return None
    for name in os.listdir(AR_DIR):
        if name.startswith(f"AR_{ar_id}_") and name.endswith(".md"):
            return os.path.join(AR_DIR, name)
    return None


def _replace_status_line(ar_text: str, new_status: str) -> str:
    """
    Substitui APENAS a linha: '## Status: ...'
    """
    pattern = r"^## Status:\s*.*$"
    if not re.search(pattern, ar_text, flags=re.MULTILINE):
        # fallback: adiciona após o título (sem inventar estrutura demais)
        lines = ar_text.splitlines(True)
        out = []
        inserted = False
        for line in lines:
            out.append(line)
            if not inserted and line.startswith("# "):
                out.append(f"## Status: {new_status}\n")
                inserted = True
        return "".join(out)
    return re.sub(pattern, f"## Status: {new_status}", ar_text, flags=re.MULTILINE)


def _extract_field(ar_text: str, field_name: str) -> Optional[str]:
    """
    Extrai campos do tipo:
    ## Evidence File: `...`
    ## Validation Command: `...`
    ## Gate: ...
    Retorna valor sem backticks.
    """
    pattern = rf"^## {re.escape(field_name)}:\s*(.*)\s*$"
    m = re.search(pattern, ar_text, flags=re.MULTILINE)
    if not m:
        return None
    val = m.group(1).strip().strip("`").strip()
    return val or None


def _extract_ssot_touches(ar_text: str, only_checked: bool) -> List[str]:
    """
    Lê a seção:
    ## SSOT Touches:
    - [ ] docs/ssot/schema.sql
    - [x] docs/ssot/openapi.json
    Se only_checked=True, só retorna os marcados [x].
    """
    touches: List[str] = []
    m = re.search(r"^## SSOT Touches:\s*$([\s\S]*?)(?=^##\s|\Z)", ar_text, flags=re.MULTILINE)
    if not m:
        return touches
    block = m.group(1)
    for line in block.splitlines():
        line = line.strip()
        mm = re.match(r"^- \[( |x|X)\]\s+(.+)$", line)
        if mm:
            checked = (mm.group(1).lower() == "x")
            path = mm.group(2).strip()
            if only_checked and not checked:
                continue
            touches.append(path)
    return touches


def _has_success_marker(ar_text: str) -> bool:
    return "Status Final:** ✅ SUCESSO" in ar_text


def _python_version() -> str:
    return sys.version.replace("\n", " ")


def _git_head() -> str:
    r = _git(["rev-parse", "HEAD"])
    if r.returncode != 0:
        return "UNKNOWN"
    return (r.stdout or "").strip()


def _git_status_porcelain() -> str:
    r = _git(["status", "--porcelain"])
    if r.returncode != 0:
        return ""
    return r.stdout or ""


def _is_path_staged(path: str, staged_list: List[str]) -> bool:
    return path in staged_list


def _read_evidence_staged(evidence_path: str) -> Optional[str]:
    try:
        return _read_index_version(evidence_path)
    except Exception:
        return None


# -----------------------------
# Core models
# -----------------------------
@dataclass
class HBTask:
    id: str
    title: str
    description: str
    criteria: str
    evidence_file: Optional[str] = None
    gate: Optional[str] = None
    validation_command: Optional[str] = None
    ssot_touches: Optional[List[str]] = None


class HBTrack:
    def __init__(self) -> None:
        _ensure_dirs()

    # -----------------------------
    # hb check
    # -----------------------------
    def check_integrity(self, mode: str = "manual") -> bool:
        """
        [GUARDIÃO] Valida integridade determinística do commit.

        Regras:
        R1) SSOT MUST existir. Se faltar, FAIL.
        R2) SSOT com mudanças UNSTAGED => FAIL.
        R3) Se SSOT estiver STAGED => MUST existir AR STAGED que:
            - marque [x] o SSOT em "## SSOT Touches:" (semântica forte)
            - tenha marcador de sucesso (gerado por hb report)
            - tenha Evidence File existente E STAGED, com Exit Code: 0
        R4) Se existir arquivo governado em GOVERNED_ROOTS no staged => MUST existir ao menos 1 AR STAGED.
        R5) Se existir AR STAGED com sucesso => Evidence File MUST existir e estar STAGED (anti-forja).
        """
        if not _is_git_repo():
            print("❌ Erro: este diretório não parece ser um repositório Git.")
            return False

        print("🛡️  HB Track: Verificação de Integridade (hb check)")
        print(f"🕒 {_now()}  |  mode={mode}")
        print("")

        ok = True

        # R1: SSOT existe
        missing = [p for p in SSOT_FILES if not os.path.exists(p)]
        if missing:
            ok = False
            print("🚨 FAIL (R1): SSOT ausente:")
            for p in missing:
                print(f" - {p}")
            print("")
        else:
            print("✅ SSOT presentes.")
            print("")

        # R2: SSOT UNSTAGED + detectar SSOT STAGED
        unstaged_changed: List[str] = []
        staged_changed: List[str] = []

        for ssot in SSOT_FILES:
            r_un = _git(["diff", "--", ssot])
            if (r_un.stdout or "").strip():
                unstaged_changed.append(ssot)

            r_st = _git(["diff", "--cached", "--", ssot])
            if (r_st.stdout or "").strip():
                staged_changed.append(ssot)

        if unstaged_changed:
            ok = False
            print("🚨 FAIL (R2): SSOT com alterações UNSTAGED (drift local / commit parcial):")
            for p in unstaged_changed:
                print(f" - {p}")
            print("➡️  Ação: faça stage dessas mudanças ou reverta antes de commitar.")
            print("")
        else:
            print("✅ SSOT sem alterações UNSTAGED.")
            print("")

        staged = _staged_files()
        staged_ars = [p for p in staged if p.startswith(f"{AR_DIR}/AR_") and p.endswith(".md")]

        # R4: governed roots require at least one AR staged
        governed_staged = [p for p in staged if _has_prefix(p, GOVERNED_ROOTS)]
        if governed_staged and not staged_ars:
            ok = False
            print("🚨 FAIL (R4): alterações em código governado sem AR staged no commit.")
            print("Arquivos governados staged (amostra):")
            for p in governed_staged[:50]:
                print(f" - {p}")
            if len(governed_staged) > 50:
                print(" - ...")
            print("➡️  Ação: crie/stage uma AR em docs/hbtrack/ars antes do commit.")
            print("")
        else:
            if governed_staged:
                print("✅ R4 OK: código governado com AR staged presente.")
                print("")

        # R5: AR com sucesso exige Evidence File staged (anti-forja)
        # (checamos todas as ARs staged; se alguma tem sucesso, ela tem que cumprir)
        r5_reasons: List[str] = []
        for ar_path in staged_ars:
            try:
                ar_text = _read_index_version(ar_path)
                if not _has_success_marker(ar_text):
                    continue
                ev_path = _extract_field(ar_text, "Evidence File")
                if not ev_path:
                    ok = False
                    r5_reasons.append(f"{ar_path}: sucesso sem 'Evidence File'")
                    continue
                if not os.path.exists(ev_path):
                    ok = False
                    r5_reasons.append(f"{ar_path}: Evidence File não existe no disco: {ev_path}")
                    continue
                if not _is_path_staged(ev_path, staged):
                    ok = False
                    r5_reasons.append(f"{ar_path}: Evidence File existe mas NÃO está staged: {ev_path}")
                    continue
                ev_text = _read_evidence_staged(ev_path)
                if not ev_text:
                    ok = False
                    r5_reasons.append(f"{ar_path}: Evidence File staged não pôde ser lido: {ev_path}")
                    continue
                if "Exit Code: 0" not in ev_text:
                    ok = False
                    r5_reasons.append(f"{ar_path}: Evidence File staged não comprova Exit Code: 0: {ev_path}")
            except Exception as e:
                ok = False
                r5_reasons.append(f"{ar_path}: erro validando R5 ({e})")

        if r5_reasons:
            print("🚨 FAIL (R5): anti-forja de evidência falhou:")
            for r in r5_reasons[:30]:
                print(f" - {r}")
            if len(r5_reasons) > 30:
                print(" - ...")
            print("")

        # R3: SSOT staged exige AR staged que marca [x] e tem evidência válida
        if staged_changed:
            if not staged_ars:
                ok = False
                print("🚨 FAIL (R3): SSOT staged sem AR staged.")
                print("SSOT staged:")
                for p in staged_changed:
                    print(f" - {p}")
                print("")
            else:
                ar_ok_for_ssot = False
                reasons: List[str] = []

                for ar_path in staged_ars:
                    try:
                        ar_text = _read_index_version(ar_path)

                        # Semântica forte: somente [x]
                        checked_touches = _extract_ssot_touches(ar_text, only_checked=True)
                        if not any(ssot in checked_touches for ssot in staged_changed):
                            reasons.append(f"{ar_path}: não marcou [x] o SSOT em 'SSOT Touches'")
                            continue

                        if not _has_success_marker(ar_text):
                            reasons.append(f"{ar_path}: não tem marcador ✅ SUCESSO (hb report)")
                            continue

                        ev_path = _extract_field(ar_text, "Evidence File")
                        if not ev_path:
                            reasons.append(f"{ar_path}: sem Evidence File")
                            continue
                        if not os.path.exists(ev_path):
                            reasons.append(f"{ar_path}: Evidence File não existe no disco: {ev_path}")
                            continue
                        if not _is_path_staged(ev_path, staged):
                            reasons.append(f"{ar_path}: Evidence File não está staged: {ev_path}")
                            continue
                        ev_text = _read_evidence_staged(ev_path)
                        if not ev_text or "Exit Code: 0" not in ev_text:
                            reasons.append(f"{ar_path}: Evidence File não comprova Exit Code: 0: {ev_path}")
                            continue

                        ar_ok_for_ssot = True
                        break

                    except Exception as e:
                        reasons.append(f"{ar_path}: erro lendo staged ({e})")

                if not ar_ok_for_ssot:
                    ok = False
                    print("🚨 FAIL (R3): SSOT staged exige AR staged com:")
                    print("  - SSOT marcado [x] em '## SSOT Touches:'")
                    print("  - Evidência ✅ SUCESSO (hb report)")
                    print("  - Evidence File existente e STAGED com Exit Code: 0")
                    print("")
                    print("Diagnóstico (amostra):")
                    for r in reasons[:25]:
                        print(f" - {r}")
                    if len(reasons) > 25:
                        print(" - ...")
                    print("")
                else:
                    print("✅ R3 OK: SSOT staged com AR staged + evidência válida.")
                    print("")

        if ok:
            print("✅ Integridade confirmada. Commit permitido.")
        else:
            print("❌ Bloqueio: regras determinísticas falharam. Corrija antes de commitar.")
        return ok

    # -----------------------------
    # hb plan
    # -----------------------------
    def explode(self, json_path: str) -> None:
        """
        [EXPLODIDOR] Converte JSON do Arquiteto em ARs.
        """
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            tasks_raw = data.get("tasks", [])
            if not isinstance(tasks_raw, list) or not tasks_raw:
                raise ValueError("JSON não contém 'tasks' como lista não-vazia.")

            tasks: List[HBTask] = []
            for t in tasks_raw:
                task = HBTask(
                    id=str(t["id"]).zfill(3),
                    title=str(t["title"]).strip(),
                    description=str(t["description"]).strip(),
                    criteria=str(t["criteria"]).strip(),
                    evidence_file=str(t.get("evidence_file")).strip() if t.get("evidence_file") else None,
                    gate=str(t.get("gate")).strip() if t.get("gate") else None,
                    validation_command=str(t.get("validation_command")).strip() if t.get("validation_command") else None,
                    ssot_touches=t.get("ssot_touches") if isinstance(t.get("ssot_touches"), list) else None,
                )
                tasks.append(task)

            for task in tasks:
                safe_title = _safe_slug(task.title)
                filepath = os.path.join(AR_DIR, f"AR_{task.id}_{safe_title}.md")

                evidence_file = task.evidence_file or os.path.join(EV_DIR, f"AR_{task.id}_{safe_title}.log")

                # ssot_touches: se vier inválido, cai no default completo (determinístico)
                ssot_touches = task.ssot_touches
                if not ssot_touches or not all(isinstance(x, str) and x.strip() for x in ssot_touches):
                    ssot_touches = SSOT_FILES

                # Renderiza SSOT Touches com [ ] (executor marca [x] quando tocar)
                ssot_lines = "\n".join([f"- [ ] {p}" for p in ssot_touches])

                content = f"""# AR_{task.id}: {task.title}
## Status: 🔲 PENDENTE

## Gate: {task.gate or "UNSPECIFIED"}
## Validation Command: `{task.validation_command or ""}`
## Evidence File: `{evidence_file}`

## SSOT Touches:
{ssot_lines}

### 🛠️ Especificação Técnica (Arquiteto)
{task.description}

### 🔍 Análise de Impacto (EXECUTOR: PREENCHA ANTES DE CODAR)
- **Arquivos afetados:** [Liste paths]
- **SSOT afetado:** marque [x] acima se tocar SSOT
- **Risco de Regressão?** [Baixo/Médio/Alto]

### ✅ Critérios de Sucesso (testáveis)
- [ ] {task.criteria}
- [ ] Evidência gerada em: `{evidence_file}`

### 📝 Notas de Implementação
(Descreva o que foi feito, com precisão. Sem “ajustado conforme solicitado”.)

---
*Gerado via HB Track CLI em {datetime.now().strftime('%d/%m/%Y')}*
"""
                with open(filepath, "w", encoding="utf-8") as ar:
                    ar.write(content)
                print(f"✅ Gerada: {filepath}")

            self._update_index(tasks)
            print(f"\n🎉 Sucesso! {len(tasks)} ARs criadas.")

        except FileNotFoundError:
            print(f"❌ Erro: arquivo '{json_path}' não encontrado.")
        except json.JSONDecodeError:
            print(f"❌ Erro: JSON inválido em '{json_path}'.")
        except Exception as e:
            print(f"❌ Erro inesperado: {e}")

    def _update_index(self, tasks: List[HBTask]) -> None:
        with open(INDEX_FILE, "a", encoding="utf-8") as idx:
            idx.write(f"\n### Lote de {datetime.now().date()}\n")
            for t in tasks:
                idx.write(f"- [ ] AR_{t.id}: {t.title}\n")
        print("🚀 Index atualizado.")

    # -----------------------------
    # hb report
    # -----------------------------
    def report(self, ar_id: str, test_command: str) -> int:
        """
        [VALIDADOR] Executa comando e anexa evidência na AR + salva evidence pack no caminho contratado.

        Regras:
        - Se AR define 'Validation Command' (não-vazio), o comando passado MUST bater exatamente.
        """
        ar_id = str(ar_id).zfill(3)
        ar_path = _find_ar_file_by_id(ar_id)
        if not ar_path:
            print(f"❌ Erro: AR_{ar_id} não encontrada em {AR_DIR}/")
            return 2

        with open(ar_path, "r", encoding="utf-8") as f:
            ar_text = f.read()

        contract_cmd = _extract_field(ar_text, "Validation Command") or ""
        evidence_file = _extract_field(ar_text, "Evidence File")

        if contract_cmd.strip() and test_command.strip() != contract_cmd.strip():
            print("❌ Bloqueio: comando não corresponde ao contrato da AR.")
            print(f"Contrato: {contract_cmd}")
            print(f"Recebido: {test_command}")
            print("➡️  Ação: rode exatamente o Validation Command declarado na AR.")
            return 3

        if not evidence_file:
            # fallback determinístico
            safe_title = _safe_slug(f"ar_{ar_id}")
            evidence_file = os.path.join(EV_DIR, f"AR_{ar_id}_{safe_title}.log")

        os.makedirs(os.path.dirname(evidence_file), exist_ok=True)

        print(f"🚀 Validando AR_{ar_id}...")
        print(f"🧪 Comando: {test_command}")

        result = subprocess.run(test_command, shell=True, capture_output=True, text=True)

        timestamp = _now()
        status_final = "✅ SUCESSO" if result.returncode == 0 else "❌ FALHA"
        new_ar_status = "✅ CONCLUÍDO" if result.returncode == 0 else "❌ FALHA"

        commit = _git_head()
        porcelain = _git_status_porcelain()
        pyver = _python_version()

        evidence_block = []
        evidence_block.append(f"## 🏁 Evidência de Execução ({timestamp})\n")
        evidence_block.append(f"**Status Final:** {status_final}\n")
        evidence_block.append(f"**Comando de Validação:** `{test_command}`\n")
        evidence_block.append(f"**Exit Code:** {result.returncode}\n")
        evidence_block.append(f"**Git HEAD:** `{commit}`\n")
        evidence_block.append(f"**Python:** `{pyver}`\n")
        evidence_block.append("\n### 📋 Log Output:\n```text\n")
        evidence_block.append(result.stdout or "")
        if result.stderr:
            evidence_block.append("\n[STDERR]\n")
            evidence_block.append(result.stderr)
        evidence_block.append("\n```\n\n")
        if porcelain.strip():
            evidence_block.append("### 📌 Git Status (porcelain)\n```text\n")
            evidence_block.append(porcelain)
            evidence_block.append("\n```\n\n")
        evidence_block.append("---\n")

        updated_ar_text = ar_text + "\n\n" + "".join(evidence_block)
        updated_ar_text = _replace_status_line(updated_ar_text, new_ar_status)

        with open(ar_path, "w", encoding="utf-8") as f:
            f.write(updated_ar_text)

        # Evidence pack (conteúdo mínimo verificável pelo hb check)
        with open(evidence_file, "w", encoding="utf-8") as log:
            log.write(f"[{timestamp}] {test_command}\n")
            log.write(f"Exit Code: {result.returncode}\n")
            log.write(f"Git HEAD: {commit}\n")
            log.write(f"Python: {pyver}\n\n")
            log.write(result.stdout or "")
            if result.stderr:
                log.write("\n[STDERR]\n")
                log.write(result.stderr)
            if porcelain.strip():
                log.write("\n\n[Git Status --porcelain]\n")
                log.write(porcelain)

        print(f"\n{status_final}: Evidência anexada em {ar_path}")
        print(f"📁 Evidence pack salvo em: {evidence_file}")
        print("➡️  Lembrete: para o commit passar, faça stage da AR e do Evidence File.")

        return 0 if result.returncode == 0 else 1


def main() -> None:
    parser = argparse.ArgumentParser(
        description="HB Track CLI - Gestão Determinística por AR + Evidência",
        epilog='Exemplos: hb plan raw_plan.json | hb report 001 "pytest -q" | hb check',
    )
    subparsers = parser.add_subparsers(dest="command", help="Comandos disponíveis")

    plan_parser = subparsers.add_parser("plan", help="Explode JSON do Arquiteto em ARs")
    plan_parser.add_argument("file", help="Caminho do JSON (ex: raw_plan.json)")

    report_parser = subparsers.add_parser("report", help="Executa teste e gera evidência para AR")
    report_parser.add_argument("id", help="ID da AR (ex: 001)")
    report_parser.add_argument("cmd", help="Comando de validação (entre aspas)")

    check_parser = subparsers.add_parser("check", help="Valida integridade determinística (pre-commit friendly)")
    check_parser.add_argument("--mode", default="manual", choices=["manual", "pre-commit"], help="Modo de execução")

    args = parser.parse_args()
    hb = HBTrack()

    if args.command == "plan":
        hb.explode(args.file)
        return

    if args.command == "report":
        rc = hb.report(args.id, args.cmd)
        sys.exit(rc)

    if args.command == "check":
        ok = hb.check_integrity(mode=args.mode)
        sys.exit(0 if ok else 1)

    parser.print_help()


if __name__ == "__main__":
    main()
````

O que esta versão garante “de verdade” (mecanizado):

* SSOT = 3 arquivos (e `hb check` cobre os 3).
* `hb check` valida UNSTAGED e STAGED.
* SSOT STAGED exige AR STAGED que **marca [x]** o SSOT em `SSOT Touches`, com evidência ✅ SUCESSO.
* Evidência não é “texto forjável”: `hb check` exige **Evidence File existente e staged com Exit Code: 0**.
* Mudança em código governado exige AR staged (para os roots definidos em `GOVERNED_ROOTS`).

---

### 4.2 Git Hook Determinístico: `scripts/git-hooks/pre-commit`

Crie `scripts/git-hooks/pre-commit` (sem extensão), como **Python**:

```python
#!/usr/bin/env python3
import subprocess
import sys

cmd = [sys.executable, "scripts/run/hb.py", "check", "--mode", "pre-commit"]
r = subprocess.run(cmd)
sys.exit(r.returncode)
```

Observação: esse hook é “cross-plataforma” no sentido de que é Python. No Windows, o Git precisa conseguir chamar Python (PATH) ou `sys.executable` resolver.

---

### 4.3 Template de AR Contract (JSON)

Sugestão de arquivo de referência: `docs/hbtrack/contratos/ar_contract.template.json`

Campos obrigatórios: `id, title, description, criteria`
Campos recomendados para determinismo: `gate, validation_command, evidence_file, ssot_touches`

```json
{
  "project": "HB Track",
  "version": "1.0.2",
  "tasks": [
    {
      "id": "001",
      "title": "Endpoint de Listagem de Atletas",
      "description": "Implementar GET /api/v1/athletes com paginação e filtros.",
      "criteria": "Teste de integração passando com 200 OK e JSON válido",
      "gate": "PYTEST_INTEGRATION",
      "validation_command": "pytest -q tests/test_athletes_api.py",
      "evidence_file": "docs/hbtrack/evidence/AR_001_athletes_endpoint.log",
      "ssot_touches": [
        "docs/ssot/openapi.json",
        "docs/ssot/schema.sql",
        "docs/ssot/alembic_state.txt"
      ]
    }
  ]
}
```

---

## <a name="workflow"></a>🔄 5. CICLO DE VIDA (WORKFLOW)

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐      ┌──────────┐
│  ARQUITETO  │─────▶│  EXPLODIDOR  │─────▶│  EXECUTOR   │─────▶│ VALIDADOR│
│   (IA/GPT)  │ JSON │  (hb plan)   │ ARs  │ (IA/humano) │ Code │(hb report)│
└─────────────┘      └──────────────┘      └─────────────┘      └──────────┘
                                                                       │
                                                                       ▼
┌─────────────┐      ┌──────────────┐
│   COMMIT    │◀─────│   GUARDIÃO   │
│    (Git)    │      │  (hb check)  │
└─────────────┘      └──────────────┘
```

### Fase 1: Arquitetura (Plano)

Prompt do Arquiteto:

```
Você é o Arquiteto do HB Track. Gere um JSON no formato AR CONTRACT.
Para cada tarefa:
- ID (001, 002...)
- Título
- Descrição técnica
- Critério de sucesso testável
- gate + validation_command + evidence_file
- Se tocar SSOT: ssot_touches com paths em docs/ssot
```

Execução:

```bash
python scripts/run/hb.py plan raw_plan.json
```

Resultado: ARs em `docs/hbtrack/ars/` com status `🔲 PENDENTE`.

### Fase 2: Execução (Código)

Regras mecanizadas pelo guardião:

* Se você alterou “código governado” (roots em `GOVERNED_ROOTS`), o commit só passa se existir AR staged.
* Se você alterou SSOT (`docs/ssot/*`), o commit só passa se existir AR staged que marcou [x] o SSOT e tem evidência válida.

Executor:

1. Ler a AR
2. Preencher “Análise de Impacto”
3. Implementar
4. Se tocar SSOT: marcar [x] em `SSOT Touches`
5. Rodar `hb report` com o comando do contrato

### Fase 3: Evidência (Prova)

```bash
python scripts/run/hb.py report 001 "pytest -q tests/test_athletes_api.py"
```

### Fase 4: Commit (Trava)

```bash
git add .
git commit -m "feat: implementa AR_001 athletes list"
```

O hook roda `hb check --mode pre-commit` e aplica R1–R5.

---

## <a name="integracao"></a>🤖 6. INTEGRAÇÃO COM CLINE/IA

Antes de iniciar a sessão, diga ao executor (IA ou humano):

> “Você opera sob o protocolo HB Track.
> Regras obrigatórias:
>
> 1. Nunca altere código governado sem AR em `docs/hbtrack/ars/`
> 2. Se tocar SSOT em `docs/ssot/`, você MUST marcar [x] em `SSOT Touches` e MUST gerar evidência ✅ SUCESSO via `hb report`
> 3. Se a AR define `Validation Command`, você MUST rodar exatamente esse comando
> 4. Para o commit passar, AR e Evidence File precisam estar staged.”

### `.clinerules` (ajustado ao canon)

Crie `.clinerules` na raiz:

```markdown
# HB TRACK PROTOCOL v1.0.2
Você é o "Executor HB Track", agente de alta precisão.

## CANON PATHS
- CLI: scripts/run/hb.py
- ARs: docs/hbtrack/ars/
- Evidence: docs/hbtrack/evidence/
- Contratos: docs/hbtrack/contratos/
- Generated (DERIVED): docs/hbtrack/_generated/
- SSOT: docs/ssot/{schema.sql,openapi.json,alembic_state.txt}

## FLUXO OBRIGATÓRIO
1) Receber plano (JSON)
2) Rodar: python scripts/run/hb.py plan raw_plan.json
3) Trabalhar AR por vez
4) Se tocar SSOT: marcar [x] em "SSOT Touches" na AR
5) Rodar validação: python scripts/run/hb.py report <id> "<comando>"
6) Antes do commit: python scripts/run/hb.py check --mode pre-commit
7) No commit, AR e Evidence File devem estar staged.

## REGRAS DE OURO
- Se alterar roots governados: MUST existir AR staged.
- Se alterar SSOT: MUST existir AR staged com SSOT [x] + evidência válida (Exit Code 0) e Evidence File staged.
- Proibido: “ajustado conforme solicitado” sem detalhar mudanças.

Você está pronto. Aguarde o primeiro plano.
```

---

## <a name="avancados"></a>🎓 7. CONCEITOS AVANÇADOS

### 7.1 SSOT vs DERIVED (para evitar drift estrutural)

* SSOT: somente `docs/ssot/**` (editável, governado por AR + evidência).
* DERIVED: somente `docs/hbtrack/_generated/**` (gerado por scripts; não editar manualmente).

### 7.2 Por que `SSOT Touches` agora é “forte”

O guardião só aceita SSOT staged quando o SSOT foi **marcado [x]** na AR. Isso evita “SSOT mudou sem intenção declarada”.

### 7.3 O que este protocolo garante (sem exageros)

Garante, de forma mecanizada:

* drift de SSOT é bloqueado (unstaged) e governado (staged)
* SSOT só entra com AR + evidência válida + evidence file staged
* código governado só entra com pelo menos 1 AR staged (para os roots configurados)

O que ainda é “processual” (se você quiser travar, vira evolução futura):

* mapear exatamente “quais arquivos pertencem a qual AR” (exigiria um manifest por AR e checagem diff→manifest)

### 7.4 Perguntas não feitas (mas críticas) e respostas

1. “Onde vivem os contratos do processo?”
   Em `docs/hbtrack/contratos/`. Se não estiver lá, não é contrato — é opinião.

2. “Como eu evito que o arquiteto gere JSON inválido?”
   Defina o AR CONTRACT oficial em `docs/hbtrack/contratos/` e trate o template como referência obrigatória. (Evolução: validar JSON via schema.)

3. “E se meu código não fica em `src/`?”
   Você deve ajustar `GOVERNED_ROOTS` no `scripts/run/hb.py` para seus roots reais; caso contrário, a promessa “sem código sem AR” não é mecanizada.

---

✅ 8. Checklist de Adoção (coerente com o canon)

### Fase 1: Setup Inicial

* [ ] Pastas canon existem (docs/hbtrack/** e docs/ssot/**)
* [ ] `scripts/run/hb.py` existe
* [ ] `git config core.hooksPath scripts/git-hooks` aplicado
* [ ] hook `scripts/git-hooks/pre-commit` existe e é executável no seu ambiente Git
* [ ] `GOVERNED_ROOTS` reflete seus roots reais (ex.: `src/`, `backend/`, `Ftonted/`…)

### Fase 2: Primeiro Ciclo

* [ ] `hb plan raw_plan.json` cria ARs em `docs/hbtrack/ars/`
* [ ] `hb report 001 "<cmd>"` grava evidência em `docs/hbtrack/evidence/`
* [ ] você faz stage de **AR + Evidence File**
* [ ] `hb check --mode pre-commit` passa
* [ ] commit passa sem bypass

---

## <a name="bonus"></a>🎁 9. BÔNUS: Seu Primeiro JSON de Teste

Salve como `raw_plan.json`:

```json
{
  "project": "HB Track",
  "version": "1.0.2",
  "tasks": [
    {
      "id": "001",
      "title": "Setup HB Track Determinístico",
      "description": "Garantir estrutura docs/hbtrack e hook pre-commit em Python, com hb check passando.",
      "criteria": "hb check --mode pre-commit passa e AR tem evidência ✅ SUCESSO com Evidence File staged",
      "gate": "SMOKE",
      "validation_command": "python scripts/run/hb.py check --mode pre-commit",
      "evidence_file": "docs/hbtrack/evidence/AR_001_setup_smoke.log",
      "ssot_touches": [
        "docs/ssot/schema.sql",
        "docs/ssot/openapi.json",
        "docs/ssot/alembic_state.txt"
      ]
    }
  ]
}
```

Execução:

```bash
python scripts/run/hb.py plan raw_plan.json
python scripts/run/hb.py report 001 "python scripts/run/hb.py check --mode pre-commit"
git add docs/hbtrack/ars docs/hbtrack/evidence
git commit -m "feat: setup HB Track determinístico (AR_001)"
```

---

Abaixo está uma lista enxuta e “plugável” de prompts, cobrindo exatamente o fluxo do contrato (PRD+SSOT → plano JSON em `docs/hbtrack/planos/` → `hb plan` → AR → impacto → código → `hb report` → commit + `hb check`). Você pode anexar como um capítulo “PROMPTS OFICIAIS v1.0.4”.

---

## PROMPTS OFICIAIS — HB Track Dev Flow v1.0.4

### 0) Prompt de inicialização do Arquiteto (contexto + fontes)

Use antes de pedir qualquer plano.

```
ROLE: ARQUITETO HB TRACK (determinístico)

SCOPE:
- Produzir APENAS um Plan JSON (AR Contract) válido pelo schema v1.0.4.
- NÃO produzir ARs em Markdown. NÃO produzir código.

FONTES (obrigatório considerar):
1) PRD: docs/hbtrack/PRD Hb Track.md
2) SSOT:
   - docs/ssot/schema.sql
   - docs/ssot/openapi.json
   - docs/ssot/alembic_state.txt

OUTPUT:
- Retorne SOMENTE o JSON final (sem texto fora do JSON).
- O JSON MUST validar contra: docs/_canon/contratos/ar_contract.schema.json
- plan.version MUST = "1.0.4"
- evidence_file MUST começar com: "docs/hbtrack/evidence/AR_<id>_... .log"
- validation_command MUST ser um comando executável (gate real).
- Use notes/assumptions/risks se necessário (não invente campos fora do schema).

TEMA/DEMANDA:
[cole aqui o pedido de feature / bug / ajuste]
```

---

### 1) Prompt para gerar o plano (Plan JSON) a partir do PRD+SSOT

Use quando você já tem a demanda clara.

```
TAREFA:
Com base no PRD e nos SSOT, gere um Plan JSON (AR Contract) com tarefas atômicas. 

REGRAS:
- tasks[*].id: "001", "002", ...
- Cada task MUST ter:
  - title (<=100)
  - description (>=20 chars)
  - criteria (>=10 chars)
  - validation_command (comando real)
  - evidence_file (docs/hbtrack/evidence/AR_<id>_*.log)
- ssot_touches (opcional): use apenas se realmente for tocar SSOT (schema/openapi/alembic_state).
- Inclua notes/assumptions/risks SOMENTE se forem necessários para execução.
- Toda regra de negócio precisa de confirmação humana.

RESTRIÇÕES:
- Não crie mais de 7 tasks no primeiro plano.
- Cada task deve ser validável de forma independente.

OUTPUT:
- Crie o aquivo .json, SOMENTE com o JSON final, válido no schema v1.0.4 em `docs/_canon/planos`
-VALIDAÇÃO: rode 'hb plan docs/_canon/planos/<nome_do_plano>.json'
✅ Plan materialized successfully: docs/hbtrack/ars/AR_0**_*.md, docs/hbtrack/ars/AR_0**_*.md, ...
- Arqvuivos etão gerados em docs/hbtrack/ars/
DEMANDA:
[cole aqui]
```

---

### 2) Prompt “Gate-first” (força comando de validação real, não genérico)

Use quando o Arquiteto estiver inventando validação fraca.

```
TAREFA:
Reescreva APENAS os campos validation_command e criteria das tasks do plano, tornando os gates fortes e executáveis.

REGRAS:
- Mantenha IDs e evidence_file.
- Cada validation_command MUST ser:
  - reprodutível
  - específico (não "rodar testes" genérico)
  - com escopo mínimo
- criteria MUST refletir o resultado esperado do comando.

OUTPUT:
- Retorne SOMENTE o JSON atualizado e válido no schema v1.0.4.

PLANO ATUAL (JSON):
[cole o JSON aqui]
```

---

### 3) Prompt de revisão de integridade do plano (antes de salvar em `docs/hbtrack/planos/`)

Use para “auditar” o JSON antes de você salvar.

```
TAREFA:
Audite o Plan JSON contra as regras do protocolo v1.0.4 e aponte violações OBJETIVAS.

CHECKLIST (responda PASS/FAIL por item):
- project == "HB Track"
- version == "1.0.4"
- tasks não vazia
- cada task tem: id/title/description/criteria/validation_command/evidence_file
- evidence_file contém "AR_<id>" e começa com "docs/hbtrack/evidence/"
- nenhum campo fora do schema (additionalProperties=false)
- validation_command é executável (não placeholder)

OUTPUT:
- Lista de FAILs com motivo e o path do campo (ex.: tasks[2].evidence_file).
- Se tudo PASS, responda apenas: "PASS: plano pronto para docs/hbtrack/planos/"

PLANO (JSON):
[cole o JSON]
```

---

### 4) Prompt do Executor: “Análise de Impacto” (preencher na AR antes de codar)

Use dentro do Cline/Executor após `hb plan` gerar a AR.

```
ROLE: EXECUTOR HB TRACK

TAREFA:
Preencher a seção "Análise de Impacto" da AR abaixo, ANTES de implementar.

REGRAS:
- Liste paths reais que serão modificados.
- Se tocar SSOT: marque [x] em SSOT Touches na AR e explique por quê.
- Declare risco (Baixo/Médio/Alto) com 1 frase objetiva.
- Não implemente nada ainda, apenas análise.

AR (conteúdo):
[cole o conteúdo da AR gerada]
```

---

### 5) Prompt do Executor: “Plano de implementação” (sem código ainda)

Use para o Executor propor passos antes de editar arquivos.

```
ROLE: EXECUTOR HB TRACK

TAREFA:
Criar um plano de implementação em 5–10 passos para cumprir exatamente a AR, respeitando o validation_command.

REGRAS:
- Cada passo deve referenciar arquivos e mudanças concretas.
- Não escrever código ainda.
- Garantir que o validation_command será executável ao final.

AR:
[cole a AR]
```

---

### 6) Prompt do Executor: “Implementar e manter rastreabilidade” (com guardrails)

Use quando for autorizar a implementação.

```
ROLE: EXECUTOR HB TRACK

TAREFA:
Implementar a AR exatamente como descrita.

REGRAS (obrigatórias):
1) Só alterar arquivos necessários para cumprir a AR.
2) Se tocar SSOT, marcar [x] na AR em SSOT Touches.
3) Após implementação, rodar exatamente:
   python scripts/run/hb.py report <id> "<validation_command>"
4) Não declarar concluído se hb report retornar falha.
5) No final, listar:
   - arquivos modificados
   - comando executado
   - onde ficou o evidence_file

AR:
[cole a AR]
```

---

### 7) Prompt de pós-validação: “Resumo determinístico” (para colar na AR)

Use depois de `hb report` ter dado sucesso, para registrar “o que mudou” sem texto vago.

```
TAREFA:
Gerar um resumo técnico determinístico (máx. 12 linhas) para a seção "Notas de Implementação" da AR.

REGRAS:
- Cite os principais arquivos alterados (paths).
- Cite o comportamento entregue (1–3 bullets).
- Não usar frases vagas ("ajustado conforme solicitado").
- Não inventar nada fora do que está evidenciado.

ENTRADAS:
1) AR (após hb report):
[cole a AR com a evidência anexada]
2) Lista de arquivos modificados (git diff --name-only):
[cole aqui]
```

---

### 8) Prompt de auditoria final do commit (antes de commitar)

Use se quiser uma checagem “humana + IA” antes de rodar o commit.

```
TAREFA:
Auditar se o commit vai passar no hb check (pre-commit) com base nos artefatos.

VERIFICAR:
- AR e Evidence File estão prontos para stage.
- Se SSOT mudou: existe AR com SSOT [x] + evidence_file staged com Exit Code: 0.
- Se código em GOVERNED_ROOTS mudou: existe ao menos 1 AR staged.

OUTPUT:
- PASS: pronto para git add / commit
OU
- FAIL: lista objetiva do que falta (paths).

ENTRADAS:
- staged files (git diff --cached --name-only):
[cole]
- AR relevante:
[cole]
- evidence file (conteúdo):
[cole]
```

---

## Perguntas não feitas (mas você deveria anexar junto dos prompts)

1. “Qual é o gate mínimo aceitável por tipo de mudança?”
   Resposta: sem isso, o Arquiteto pode escolher validação fraca. Recomenda-se uma tabela mínima (AUTH, DB, API, UI) → comando recomendado.

2. “Quem cria o plano: humano ou IA?”
   Resposta: IA cria, humano decide se aceita. Se o humano editar JSON, continua válido, mas a autoria muda.

3. “Qual é o limite de tarefas por plano?”
   Resposta: se passar de ~7–10, o executor tende a se perder. Quebre em múltiplos planos.

Se você quiser, eu adapto esses prompts para os seus roots reais (`backend/` e `Hb Track - Fronted/`) e já deixo um “Prompt do Arquiteto” que obriga o Arquiteto a declarar explicitamente quais roots serão tocados em cada task (sem violar o schema).


*Framework HB Track v1.0.2 — “Código é subproduto. Evidência é realidade.”*
