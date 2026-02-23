# SPEC_HB_CLI — scripts/run/hb_cli.py (HB CLI) — v1.1.0

Este documento especifica o comportamento exigido do CLI (hb_cli.py). Ele é a implementação do contrato:
- docs/_canon/contratos/Dev Flow.md

## 1. Versão do protocolo (obrigatório)
hb_cli.py MUST ter:
- HB_PROTOCOL_VERSION = "1.1.0"
- AR_CONTRACT_SCHEMA_VERSION (schema_version): deve ler de ar_contract.schema.json e validar planos contra ele

hb_cli.py MUST reportar versão em:
1) `python scripts/run/hb_cli.py version`
   Saída determinística:
   - "HB Track Protocol v1.1.0"
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
- DB_SSOT_FILES (subconjunto indicando alteração de banco):
  - docs/ssot/schema.sql
  - docs/ssot/alembic_state.txt
- SCHEMA_PATH:
  - docs/_canon/contratos/ar_contract.schema.json

## 3. Governed roots (config de enforcement)
hb_cli.py contém:
- GOVERNED_ROOTS = [ ... ]

Padrão recomendado (ajuste para o repo real):
- "backend/"
- "Hb Track - Frontend/"

Mudança de GOVERNED_ROOTS é mudança de governança => AR + bump de versão.

## 4. Comandos suportados
- hb version
- hb plan <plan_json_path> [--force|--skip-existing] [--dry-run]
- hb report <id> "<command>"
- hb verify <id> (Testador)
- hb seal <id> ["<reason>"] (Humano - último gate)
- hb check --mode {manual|pre-commit}

## 5. hb plan — validação e materialização
Assinatura:
- hb plan docs/_canon/planos/<arquivo>.json [--force|--skip-existing] [--dry-run]

Flags:
- --force: sobrescreve ARs existentes com mesmo ID (remove e recria)
- --skip-existing: pula ARs que já existem no disco sem erro
- --dry-run: simula materialização sem criar arquivos (validação completa do pipeline)

Pipeline de validação (ordem exata):
P1) plan_json_path MUST estar dentro de docs/_canon/planos/
    Senão: FAIL E_PLAN_PATH

P2) JSON MUST parsear
    Senão: FAIL E_PLAN_JSON

P3) JSON MUST validar contra JSON Schema canônico (Draft 2020-12)
    Senão: FAIL E_PLAN_SCHEMA (mensagem determinística: 1ª violação com path)

P4) plan.version MUST == HB_PROTOCOL_VERSION
    Senão: FAIL E_PLAN_VERSION_MISMATCH

P3.5) validation_command MUST ser não-trivial: não pode ser echo|true|exit 0|noop OU (len<30 chars sem keywords assert/pytest/check/verify/validate).
    Senão: FAIL E_TRIVIAL_CMD (exit 2)

GATE 2) IDs únicos: todos os task.id no plano MUST ser únicos.
    Senão: FAIL E_DUPLICATE_IDS (exit 2)

GATE 2.5) Rollback obrigatório para tasks de banco:
    Uma task é considerada "de banco" se:
    - ssot_touches contém DB_SSOT_FILES (schema.sql ou alembic_state.txt), OU
    - validation_command menciona keywords de banco (alembic, migration, psql, sql), OU
    - description menciona keywords DDL (migration, add column, drop column, alter table, create table, etc.)
    Se task de banco não tem rollback_plan: FAIL E_ROLLBACK_MISSING (exit 2)
    Se rollback_plan não contém comando válido: FAIL E_ROLLBACK_INVALID (exit 2)
    Padrões aceitos: alembic downgrade, git revert, drop index, drop constraint, drop column, drop table, alter table, delete from, update, drop foreign key, rollback

P6) Coerência id ↔ evidence_file MUST ser checada:
    evidence_file MUST conter "AR_<id>" (ex.: id=007 => "AR_007")
    Senão: FAIL E_TASK_EVIDENCE_ID_MISMATCH

GATE 3) Colisão com disco:
    Se AR com mesmo ID já existe em AR_DIR:
    - modo default: FAIL E_AR_COLLISION (exit 2) com instruções de --force/--skip-existing
    - modo --force: remove AR existente e recria
    - modo --skip-existing: pula sem erro
    - modo --dry-run + --force: simula sobrescrita sem deletar

GATE 4+5) Escrita atômica + pós-validação:
    P5) Para cada task:
    - construir conteúdo completo do AR em memória
    - escrever em .tmp/ (diretório temporário dentro de AR_DIR)
    - validar tamanho mínimo (MIN_AR_SIZE_BYTES = 200 bytes, anti-zero-bytes)
    - validar header obrigatório ("# AR_<id>")
    - validar encoding UTF-8 (leitura completa)
    - mover atomicamente (.tmp/ → destino final)
    Se falhar: FAIL E_AR_MATERIALIZE (exit 2) + rollback de todos ARs já criados
    Se zero bytes: FAIL E_AR_ZERO_BYTES
    Inserir no .md:
      - Validation Command (contrato)
      - Evidence File (contrato)
      - SSOT Touches (lista com [ ])
      - Rollback Plan (contrato) — se presente, com aviso de DB
      - Notas/Riscos do Arquiteto (task.notes/task.risks) se existirem
      - Notes/Assumptions do plano (plan.notes/plan.assumptions) em seção própria

Rollback atômico: se qualquer AR falhar na materialização, todos os ARs já criados no batch são removidos.

Dependência:
- hb plan usa biblioteca `jsonschema`.
- Se `jsonschema` não estiver disponível: FAIL E_DEP_JSONSCHEMA com instrução objetiva.

Concorrência:
- hb plan usa HBLock (file-based lock em .hb_lock) para operações de escrita atômica.
- Se lock retido por outro processo: FAIL E_CLI_LOCKED (exit 3) após MAX_RETRIES=10 tentativas.

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

Evidence Integrity (AR_029):
- Antes de gravar: captura governed_checksums (SHA-256 hex[:16] de arquivos em GOVERNED_ROOTS staged/modified via git diff HEAD).
- Captura workspace_status (git status --porcelain).
- Grava no evidence pack (`docs/hbtrack/evidence/AR_<id>/executor_main.log`):
    Governed Checksums: {json}
    Workspace Status: clean|dirty_files=N
- hb report usa HBLock para escrita concorrente segura.

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

Códigos mínimos (originais v1.0.5):
- E_DEP_JSONSCHEMA
- E_PLAN_PATH
- E_PLAN_JSON
- E_PLAN_SCHEMA
- E_PLAN_VERSION_MISMATCH
- E_TASK_EVIDENCE_ID_MISMATCH
- E_AR_NOT_FOUND
- E_CMD_MISMATCH

Códigos adicionais (v1.0.6 — novos gates):
- E_DUPLICATE_IDS (GATE 2: IDs não-únicos no plan)
- E_AR_COLLISION (GATE 3: AR já existe no disco)
- E_ROLLBACK_MISSING (GATE 2.5: task de banco sem rollback_plan)
- E_ROLLBACK_INVALID (GATE 2.5: rollback_plan sem comando válido)
- E_AR_MATERIALIZE (GATE 4+5: falha na escrita atômica)
- E_AR_ZERO_BYTES (GATE 4+5: AR com tamanho abaixo do mínimo)

Códigos adicionais (v1.1.0 — triple-run + anti-trivial):
- E_TRIVIAL_CMD (GATE P3.5: validation_command trivialmente passável)
- E_TRIPLE_FAIL (hb verify: algum run exit!=0)
- E_CLI_LOCKED (HBLock: lock file retido após MAX_RETRIES tentativas)

## 9. Observação: staging obrigatório
Para o commit passar, o usuário MUST dar stage em:
- AR(s) relevantes em docs/hbtrack/ars/
- Evidence File(s) relevantes em docs/hbtrack/evidence/
- (quando aplicável) SSOTs em docs/ssot/

## 10. hb verify — Testador independente

Assinatura:
- hb verify <id>

Função: re-executa o validation_command da AR de forma independente e gera TESTADOR_REPORT.

hb seal (humano - último gate):
- hb seal <id> ["<reason>"] promove AR de ✅ SUCESSO para ✅ VERIFICADO.
- Pré-condições: evidence canônico staged, TESTADOR_REPORT staged, workspace limpo.
- MUST ser o último gate antes do commit.

Pipeline (ordem exata):

V1) Localizar AR_<id>_*.md em AR_DIR
    Se não encontrar: FAIL E_AR_NOT_FOUND (exit 2)

V2) Verificar que AR contém '✅ SUCESSO'
    Se não: FAIL E_VERIFY_NOT_READY com mensagem 'AR must have ✅ SUCESSO before verify' (exit 4)

V3) Extrair validation_command (entre ``` de ## Validation Command (Contrato))
    Se ausente: FAIL E_VERIFY_NO_CMD (exit 4)

V4) Re-executar validation_command TRIPLE_RUN_COUNT=3 vezes (independente).
    Para cada run: capturar exit code e behavior_hash = sha256(exit_code + "\n" + stdout_norm + "\n---STDERR---\n" + stderr_norm).
    - Se qualquer run exit != 0: triple_consistency = 'FAIL'
    - Se todos exit 0 MAS behavior_hash diferente entre runs: triple_consistency = 'FLAKY_OUTPUT'
    - Se todos exit 0 E behavior_hash idêntico: triple_consistency = 'OK'
    FLAKY_OUTPUT => REJEITADO (output não-determinístico).

Pre-check workspace (antes do triple-run):
    check_workspace_clean() via git status --porcelain.
    Se dirty: WARNING impresso (não bloqueia, mas registrado no TESTADOR_REPORT).

Post-check checksums (após o triple-run):
    compare governed_checksums pre vs post verify.
    Se pre != post: WARNING 'checksum_drift' no TESTADOR_REPORT.

V5) Ler Evidence Pack (caminho de ## Evidence File (Contrato)):
    - Extrair 'Exit Code: N' do Evidence Pack
    - Se Evidence Pack ausente: registrar evidence_pack_complete=false

V6) Determinar consistency:
    - executor_exit extraído do Evidence Pack
    - testador_exit = exit code da re-execução
    - consistency = 'OK' se iguais; 'AH_DIVERGENCE' se executor=0 mas testador!=0

V7) Gerar TESTADOR_REPORT em _reports/testador/AR_<id>_<git_hash_7>/:
    - context.json (run_id, timestamp, git.commit, environment.python_version)
    - result.json (ar_id, validation_command, testador_exit_code, executor_exit_code, consistency, status, ah_flags, evidence_pack_complete, rejection_reason)
    - stdout.log (stdout da re-execução)
    - stderr.log (stderr da re-execução)

V8) Atualizar **Status** header da AR via re.sub:
    - testador_exit == 0 AND consistency == 'OK': '✅ VERIFICADO'
    - testador_exit != 0 OR consistency == 'AH_DIVERGENCE': '🔴 REJEITADO'
    - ERROR_INFRA (exit 3): '⏸️ BLOQUEADO_INFRA'

V9) Append stamp de verificação à AR:
    ### Verificação Testador em <hash_7>
    **Status Testador**: <✅ VERIFICADO | 🔴 REJEITADO | ⏸️ BLOQUEADO_INFRA>
    **Consistency**: <OK | AH_DIVERGENCE>
    **Exit Testador**: <n> | **Exit Executor**: <n>
    **TESTADOR_REPORT**: `_reports/testador/AR_<id>_<hash>/result.json`

Exit codes do hb verify:
- 0: VERIFICADO (re-execução exit 0 + consistency OK)
- 2: REJEITADO (re-execução exit != 0 OU AH_DIVERGENCE)
- 3: BLOCKED_INFRA (ERROR_INFRA na re-execução)
- 4: BLOCKED_INPUT (AR não pronta ou sem validation command)

## 11. Novos Status de AR (v1.0.8)

Status válidos (completo):
- 🔲 PENDENTE
- 🏗️ EM_EXECUCAO
- ✅ SUCESSO (Executor claims success — NÃO final em v1.0.8+)
- 🔍 NEEDS_REVIEW (AR aguardando revisão humana — intermediário entre SUCESSO e VERIFICADO)
- ✅ VERIFICADO (Testador confirmou — FINAL, permite commit)
- ❌ FALHA (Executor encontrou falha)
- 🔴 REJEITADO (Testador rejeitou — Executor deve corrigir e rodar hb report novamente)
- ⏸️ BLOQUEADO_INFRA (Testador encontrou ERROR_INFRA — waiver necessário)
- ⛔ SUPERSEDED (AR obsoleta, substituída por outra)

Regra: hb check (v1.0.8+) aceita APENAS ✅ VERIFICADO para ARs com Versão do Protocolo >= 1.0.8.

## 12. hb check atualizado — C3 com VERIFICADO

C3 atualizado (substitui regra anterior):

C3) Se SSOT STAGED => MUST existir AR STAGED que:
  a) marcou [x] o SSOT em SSOT Touches
  b) tem status final válido:
     - Se AR tem 'Versão do Protocolo': 1.0.8 ou superior: MUST ter '✅ VERIFICADO'
     - Se AR tem protocolo anterior: aceita '✅ SUCESSO' (migração)
  c) Evidence File existe e está STAGED com 'Exit Code: 0'

Novos error codes:
- E_VERIFY_NOT_READY: AR não tem ✅ SUCESSO — Executor não terminou
- E_VERIFY_NO_CMD: AR não tem Validation Command — não verificável
- E_VERIFY_REQUIRES_VERIFIED: AR v1.0.8+ staged sem ✅ VERIFICADO (Testador não rodou)

## 13. HBLock — Concorrência entre agentes (v1.1.0)

Implementação: AR_028.

O hb_cli.py usa um file-based lock (`.hb_lock`) para garantir atomicidade de escrita quando
múltiplos agentes (Arquiteto, Executor, Testador) operam em paralelo.

Comandos que usam HBLock:
- hb plan (materialização de ARs)
- hb report (gravação de evidence + carimbo na AR)
- hb verify (gravação de TESTADOR_REPORT + carimbo na AR)

Parâmetros:
- MAX_RETRIES = 10 (tentativas com backoff aleatório 100-500ms)
- Lock file: .hb_lock (deve estar no .gitignore)
- Em caso de lock órfão: remover manualmente o arquivo .hb_lock
- Em caso de exceder MAX_RETRIES: FAIL E_CLI_LOCKED (exit 3)

## 14. Changelog

| Versão | Data       | Descrição                                                              |
|--------|------------|------------------------------------------------------------------------|
| 1.0.5  | —          | Versão original (schema, plan, report, check)                          |
| 1.0.6  | —          | Novos gates: E_DUPLICATE_IDS, E_AR_COLLISION, E_ROLLBACK_MISSING/INVALID |
| 1.0.8  | —          | hb verify (Testador), novos status, C3 version-aware                   |
| 1.1.0  | 2026-02-21 | GATE P3.5, HBLock, SHA-256 evidence integrity, triple-run FLAKY_OUTPUT |
| 1.1.1  | 2026-02-21 | Novo status 🔍 NEEDS_REVIEW (revisão humana intermediária)               |