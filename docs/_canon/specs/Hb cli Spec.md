# SPEC_HB_CLI — scripts/run/hb.py (HB CLI) — v1.0.5

Este documento especifica o comportamento exigido do CLI (hb.py). Ele é a implementação do contrato:
- docs/_canon/contratos/HBTRACK_DEV_FLOW_CONTRACT.md

## 1. Versão do protocolo (obrigatório)
hb.py MUST ter:
- HB_PROTOCOL_VERSION = "1.0.5"

hb.py MUST reportar versão em:
1) `python scripts/run/hb.py version`
   Saída determinística:
   - "HB Track Protocol v1.0.5"
2) header do `hb check` (primeiras linhas)

## 2. Canon paths (hard-coded)
- PLANS_DIR: docs/_canon/planos
- AR_DIR: docs/hbtrack/ars
- EV_DIR: docs/hbtrack/evidence
- INDEX_FILE (opcional): docs/hbtrack/_INDEX.md
- PRD (referência): docs/hbtrack/PRD Hb Track.md
- SSOT_FILES:
  - docs/ssot/schema.sql
  - docs/ssot/openapi.json
  - docs/ssot/alembic_state.txt
- SCHEMA_PATH:
  - docs/_canon/contratos/ar_contract.schema.json

## 3. Governed roots (config de enforcement)
hb.py contém:
- GOVERNED_ROOTS = [ ... ]

Padrão recomendado (ajuste para o repo real):
- "backend/"
- "Hb Track - Fronted/"

Mudança de GOVERNED_ROOTS é mudança de governança => AR + bump de versão.

## 4. Comandos suportados
- hb version
- hb plan <plan_json_path>
- hb report <id> "<command>"
- hb check --mode {manual|pre-commit}

## 5. hb plan — validação e materialização
Assinatura:
- hb plan docs/_canon/planos/<arquivo>.json

Regras determinísticas:
P1) plan_json_path MUST estar dentro de docs/_canon/planos/
    Senão: FAIL E_PLAN_PATH

P2) JSON MUST parsear
    Senão: FAIL E_PLAN_JSON

P3) JSON MUST validar contra JSON Schema canônico (Draft 2020-12)
    Senão: FAIL E_PLAN_SCHEMA (mensagem determinística: 1ª violação com path)

P4) plan.version MUST == HB_PROTOCOL_VERSION
    Senão: FAIL E_PLAN_VERSION_MISMATCH

P5) Para cada task:
- criar AR em docs/hbtrack/ars/AR_<id>_<slug>.md
- inserir no .md:
  - Validation Command (contrato)
  - Evidence File (contrato)
  - SSOT Touches (lista com [ ])
  - Notas/Riscos do Arquiteto (task.notes/task.risks) se existirem
  - Notes/Assumptions do plano (plan.notes/plan.assumptions) em seção própria (no topo ou em seção dedicada)

P6) Coerência id ↔ evidence_file MUST ser checada pelo hb plan:
- evidence_file MUST conter "AR_<id>" (ex.: id=007 => "AR_007")
  Senão: FAIL E_TASK_EVIDENCE_ID_MISMATCH

Dependência:
- hb plan usa biblioteca `jsonschema`.
- Se `jsonschema` não estiver disponível: FAIL E_DEP_JSONSCHEMA com instrução objetiva.

## 6. hb report — execução e evidência
Assinatura:
- hb report <id> "<command>"

Regras determinísticas:
R1) localizar AR por prefixo "AR_<id>_" em docs/hbtrack/ars/
    Se não encontrar: FAIL E_AR_NOT_FOUND (exit 2)

R2) se AR define Validation Command não-vazio, o command recebido MUST bater exatamente
    Se não: FAIL E_CMD_MISMATCH (exit 3)

R3) executar comando e gravar:
- carimbo na AR (append), contendo:
  - Status Final (✅ SUCESSO / ❌ FALHA)
  - Comando
  - Exit Code
  - Git HEAD
  - Python version
  - stdout + stderr
- evidence pack no caminho Evidence File do contrato, contendo linha:
  - "Exit Code: <n>"

Exit codes do hb report:
- 0: sucesso (exit do comando == 0)
- 1: falha (exit do comando != 0)
- 2: AR não encontrada
- 3: command mismatch

## 7. hb check — integridade do commit
Assinatura:
- hb check --mode manual|pre-commit

Regras mínimas (alinhadas ao contrato):
C1) SSOT MUST existir (se faltar: FAIL)
C2) SSOT com mudanças UNSTAGED => FAIL
C3) Se SSOT STAGED => MUST existir AR STAGED que:
  - marcou [x] o SSOT em SSOT Touches
  - tem marcador ✅ SUCESSO
  - Evidence File existe e está STAGED com "Exit Code: 0"
C4) Se mudanças em GOVERNED_ROOTS estão STAGED => MUST existir ao menos 1 AR STAGED
C5) Anti-forja mínima: AR STAGED com sucesso exige Evidence File STAGED com "Exit Code: 0"

Exit code do hb check:
- 0: PASS
- 1: FAIL

## 8. Mensagens e códigos de erro determinísticos (mínimo)
Toda falha MUST imprimir: "❌ <CODE>: <mensagem>"

Códigos mínimos:
- E_DEP_JSONSCHEMA
- E_PLAN_PATH
- E_PLAN_JSON
- E_PLAN_SCHEMA
- E_PLAN_VERSION_MISMATCH
- E_TASK_EVIDENCE_ID_MISMATCH
- E_AR_NOT_FOUND
- E_CMD_MISMATCH

## 9. Observação: staging obrigatório
Para o commit passar, o usuário MUST dar stage em:
- AR(s) relevantes em docs/hbtrack/ars/
- Evidence File(s) relevantes em docs/hbtrack/evidence/
- (quando aplicável) SSOTs em docs/ssot/