<!--
DERIVED FILE — DO NOT EDIT BY HAND

This Markdown is derived from the SSOT:
- scripts/scripts_roadmap.yaml

Edits MUST be applied to scripts_roadmap.yaml, then re-run:
  python scripts/generate/docs/gen_scripts_roadmap.py
-->

# Scripts Inventory — HB Track

> Inventário operacional completo. Cada script documentado com interface operacional: entradas, saídas/evidência e pré-requisitos.
> Este arquivo serve para o humano nunca esquecer o que cada script faz e como executá-lo corretamente.


## Convenções do projeto

| Convenção | Valor |
|-----------|-------|
| Exit codes | 0 = OK, 2 = VIOLATION/DRIFT, 3 = HARNESS_ERROR, 4 = BLOCKED_INPUT |
| Side effects | Declarados por script: DB_READ, DB_WRITE, FS_READ, FS_WRITE, ENV_WRITE, PROC_START_STOP, DESTRUCTIVE |
| Prefixos | check_ (validação), diag_ (diagnóstico), fix_ (correção), gen_ (geração), mig_ (migração), ops_ (operação), run_ (orquestrador), seed_ (dados), reset_ (reset) |
| Headers | Todo script deve ter header padronizado; templates em <pasta>/templates/header_template.* (um por pasta) |
| Policy | Todos os scripts validados contra _policy/scripts.policy.yaml |
| **Python runtime** | Python 3.11.9 — pinado em Hb Track - Backend/.python-version (local e VPS) |

---

## 1. _policy/

Sistema de policy que garante que todos os scripts seguem convenções de naming, placement, headers e side-effects. Fonte de verdade (SSOT) é o arquivo scripts.policy.yaml.

### 1.1 Scripts executáveis

| Arquivo | Descrição | Side-effects | Entradas | Saídas/Evidência | Pré-requisitos |
|---|---|---|---|---|---|
| `policy_lib.py` | Biblioteca central de governança: valida scripts contra regras HB001-HB014, gera/valida manifests SHA256, renderiza MD derivado | FS_READ; FS_WRITE (quando chamado via generate/render) | Nenhum arg CLI como __main__; lê scripts.policy.yaml e side_effects_heuristics.yaml | stdout: relatório de violações; exit 0/2/3 | scripts.policy.yaml e side_effects_heuristics.yaml existentes |
| `check_path_constants.py` | Imprime constantes canônicas de paths como JSON para consumo por PowerShell | FS_READ | Nenhum arg CLI | stdout: JSON com SSOT_YAML, DERIVED_MD, MANIFEST_JSON, HEURISTICS_YAML; exit 0/3 | Nenhum (paths derivados de __file__) |
| `check_python_layout.py` | Valida que todos os arquivos .py rastreados pelo git estão em roots aprovados | FS_READ | --policy <path> (default: python_layout.policy.yaml) | stdout: lista de violações ou 'OK'; exit 0/2/3 | git no PATH; python_layout.policy.yaml existente |
| `generate_manifest.py` | Gera policy.manifest.json com hashes SHA256 dos arquivos SSOT | FS_READ; FS_WRITE | Nenhum arg CLI | scripts/_policy/policy.manifest.json; exit 0/3 | scripts.policy.yaml, side_effects_heuristics.yaml, SCRIPTS_classification.md existentes |
| `render_policy_md.py` | Gerador canônico SSOT→DERIVED: lê scripts.policy.yaml e escreve SCRIPTS_classification.md | FS_READ; FS_WRITE | --out <path> (opcional, override destino) | docs/_canon/_agent/SCRIPTS_classification.md; exit 0/2/3 | scripts/_policy/scripts.policy.yaml existente |
| `check_scripts_policy.ps1` | Gate principal de governança: valida todos os scripts em scripts/ contra a Scripts Policy SSOT (HB001-HB009) | FS_READ | Nenhum argumento; -Verbose opcional | stdout: violations ou OK; exit 0/2/3 | policy_lib.py existente; Python 3.11.9 disponível |
| `check_policy_manifest.ps1` | Valida hashes SHA256 do policy.manifest.json contra arquivos SSOT canônicos | FS_READ | Nenhum argumento; -Verbose opcional; lê policy.manifest.json | stdout: OK ou MISMATCH com detalhes; exit 0/2/3 | policy.manifest.json e os 3 arquivos referenciados existentes |
| `check_policy_md_is_derived.ps1` | Gate anti-drift: verifica que SCRIPTS_classification.md é idêntico ao gerado por render_policy_md.py | FS_READ | Nenhum argumento; -Verbose opcional | stdout: OK ou DRIFT_DETECTED com diff; exit 0/2/3 | render_policy_md.py, SCRIPTS_classification.md existentes; Python disponível |


### 1.2 Arquivos de dados/config

| Arquivo | Descrição |
|---|---|
| `scripts.policy.yaml` | **SSOT**: definição de todos os scripts, categorias, side-effects e regras |
| `scripts.policy.schema.json` | JSON Schema para validar scripts.policy.yaml |
| `python_layout.policy.yaml` | Policy de layout: define roots aprovados para arquivos Python |
| `side_effects_heuristics.yaml` | Heurísticas para detecção automática de side-effects em scripts |
| `policy.manifest.json` | Manifest gerado com hashes SHA256 para detecção de drift |
| `CONTRACT.md` | Contrato normativo da policy de scripts |
| `requirements.txt` | Dependências Python da policy (PyYAML, jsonschema) |
| `README.md` | Documentação da pasta |


## 2. _lib/

Módulos Python reutilizáveis por múltiplos scripts.

### Arquivos

| Arquivo | Descrição | Side-effects | Entradas | Saídas/Evidência | Pré-requisitos |
|---|---|---|---|---|---|
| `docs_index_lib.py` | Biblioteca + executável: valida docs/_INDEX.yaml contra JSON Schema, IDs únicos, existência de paths e enum de categorias | FS_READ | Nenhum arg CLI (paths hardcoded); pode ser importado como lib | stdout: lista de erros ou 'VALID'; exit 0/2/3 | docs/_INDEX.yaml; docs/_canon/SCHEMAS/index.schema.json existentes |
| `README.md` | Documentação da pasta | — | — | — | — |


## 3. audit/

Scripts para orquestração e execução de gates de auditoria baseados em capabilities. Geram Evidence Packs estruturados em docs/hbtrack/evidence/AR_<id>/.

### Arquivos

| Arquivo | Descrição | Side-effects | Entradas | Saídas/Evidência | Pré-requisitos |
|---|---|---|---|---|---|
| `audit_runner.py` | Orquestrador mestre de audit packs: lê registry de gates, verifica env vars obrigatórias por gate, executa cada gate via subprocess, normaliza exit codes e consolida resultados | FS_READ; FS_WRITE | Posicionais: <RUN_ID> <GATE_ID>...; --root <path> (legacy); env HB_AUDIT_BASE_URL (opcional) | docs/hbtrack/evidence/AR_<id>/context.json; .../summary.json; .../checks/<GATE_ID>/{stdout.log, stderr.log, result.json}; exit 0/2/3/4 | docs/_canon/_agent/GATES_REGISTRY.yaml existente e válido; RUN_ID e ao menos 1 GATE_ID fornecidos; env vars exigidas pelo gate presentes |
| `gate_stub_blocked.py` | Stub de gate placeholder: retorna exit 4 (BLOCKED_INPUT) para gates ainda não implementados | nenhum | Posicional: <GATE_ID> (opcional, para mensagem) | stdout: BLOCKED_INPUT: gate '<ID>' not implemented; exit 4 | Nenhum |
| `run_gate_via_capability.py` | Wrapper que executa um gate específico por capability e RUN_ID, lendo resultado de result.json gerado | FS_READ; FS_WRITE | Posicionais: <GATE_ID> <CAPABILITY> <RUN_ID>; config.py opcional | docs/hbtrack/evidence/AR_<id>/checks/<GATE_ID>/result.json (via delegação); stdout: erros se result.json ausente; exit 0/2/3/4 | scripts/gates/run_capability_gates.py executável; evidence pack root criável |


## 4. checks/

Validações (não destrutivas, read-only). Todos retornam exit code 0 (OK) ou 2/4 (VIOLATION/BLOCKED).

### 4.1 checks/db/ — Checks de banco de dados

| Arquivo | Descrição | Side-effects | Entradas | Saídas/Evidência | Pré-requisitos |
|---|---|---|---|---|---|
| `check_agent_guard.py` | Guardião de integridade via SHA256: cria baselines (snapshot) e compara contra baseline (check) para detectar mudanças não autorizadas | FS_READ; FS_WRITE (subcomando snapshot) | Subcomandos: snapshot (--root, --out, --exclude) | check (--root, --baseline, --allow, --forbid-new, --forbid-delete); env HB_DOCS_GENERATED_DIR | baseline JSON (snapshot); stdout: diff report (check); exit 0/3 | Diretório --root existente; baseline JSON existente para subcomando check |
| `check_athletes_columns.py` | Consulta information_schema.columns para tabela athletes e lista colunas e tipos | DB_READ; FS_READ | Nenhum arg CLI; env DATABASE_URL (ou .env em backend/) | stdout: column_name + data_type; exit 0/1 | PostgreSQL rodando; tabela athletes existente; DATABASE_URL configurado |
| `check_coord_train.py` | Verifica se e2e.coordenador e e2e.treinador pertencem à mesma organização via memberships | DB_READ | Nenhum arg CLI; DB URL hardcoded (localhost:5433/hb_track_dev) | stdout: rows de membership + resultado do check; exit 0/1 | PostgreSQL local na porta 5433; seed E2E executado |
| `check_coordenador.py` | Exibe resumo do time E2E-Equipe-Coordenador (atletas, treinos, partidas) | DB_READ; FS_READ | Nenhum arg CLI; env DATABASE_URL (ou .env) | stdout: relatório formatado com contagens por categoria; exit 0/1 | PostgreSQL rodando; seed E2E executado; time E2E-Equipe-Coordenador existente |
| `check_exercises_data.py` | Conta exercise_tags e exercises via async SQLAlchemy usando engine da aplicação | DB_READ | Nenhum arg CLI; executado a partir do backend root | stdout: contagens + sample de tags; exit 0/1 | PostgreSQL rodando; venv backend ativado; app.core.db importável |
| `check_membr_perms.py` | Lê ROLE_PERMISSIONS['membro'] de permissions_map.py e imprime lista de permissões habilitadas | FS_READ | Nenhum arg CLI; importa app.core.permissions_map (sem DB) | stdout: lista numerada de permissões do papel membro; exit 0/1 | venv backend ativado; app.core.permissions_map importável |
| `check_migration.py` | Lê versão atual do Alembic (alembic_version) do banco de dados local | DB_READ | Nenhum arg CLI; DB URL hardcoded (localhost:5433/hb_track_dev) | stdout: string da versão Alembic atual; exit 0/1 | PostgreSQL local na porta 5433; tabela alembic_version existente |
| `check_schema_drift.py` | Compara docs/ssot/schema.sql contra banco live (pg_dump) para detectar drift; suporta --fix para regenerar | DB_READ; FS_READ; FS_WRITE (--fix); PROC_START_STOP | --verbose (flag); --fix (flag); env DATABASE_URL (ou .env) | stdout: linhas de diff ou 'No drift'; docs/ssot/schema.sql (se --fix); exit 0/5/3 | PostgreSQL rodando; pg_dump no PATH; docs/ssot/schema.sql existente; DATABASE_URL configurado |
| `check_seed_data.py` | Verifica presença de UUIDs específicos de seed E2E (memberships, orgs, usuários) no banco | DB_READ | Nenhum arg CLI; DB URL hardcoded (localhost:5433/hb_track_dev) | stdout: rows encontrados por tabela + status; exit 0/1 | PostgreSQL local na porta 5433; seed E2E executado com UUIDs hardcoded |
| `check_team_registrations_columns.py` | Consulta information_schema.columns para tabela team_registrations e lista colunas e tipos | DB_READ; FS_READ | Nenhum arg CLI; env DATABASE_URL (ou .env) | stdout: column_name + data_type; exit 0/1 | PostgreSQL rodando; tabela team_registrations existente; DATABASE_URL configurado |
| `check_users_temp.py` | Lista os primeiros 10 usuários não-deletados com email, superadmin status e roles | DB_READ | Nenhum arg CLI; executado a partir do backend root | stdout: email + nome + role/superadmin por usuário; exit 0/1 | PostgreSQL rodando; venv backend ativado; app.core.db importável |


### 4.2 checks/docs/ — Checks de documentação

| Arquivo | Descrição | Side-effects | Entradas | Saídas/Evidência | Pré-requisitos |
|---|---|---|---|---|---|
| `check_docs_index.ps1` | Valida docs/_INDEX.yaml contra index.schema.json delegando para docs_index_lib.py | FS_READ | Nenhum argumento | stdout; exit 0/2/3 | scripts/_lib/docs_index_lib.py existente; Python disponível |
| `check_policy_determinism.ps1` | Valida determinismo do gate check_scripts_policy.ps1 executando-o 3 vezes e comparando outputs em memória | NONE | Nenhum argumento; caminho do gate hardcoded | stdout: DETERMINISMO PROVADO ou FAIL; exit 0/2/3 | scripts/_policy/check_scripts_policy.ps1 executável |


### 4.3 checks/lint/ — Checks de layout e lint

| Arquivo | Descrição | Side-effects | Entradas | Saídas/Evidência | Pré-requisitos |
|---|---|---|---|---|---|
| `check_python_layout.ps1` | Valida que arquivos Python só existem em roots aprovados; delega para _policy/check_python_layout.py | FS_READ | Nenhum argumento; usa python_layout.policy.yaml como config | stdout: OK, violações ou erro; exit 0/2/3 | check_python_layout.py e python_layout.policy.yaml existentes; Python disponível |


### 4.4 checks/models/ — Checks de modelos ORM

| Arquivo | Descrição | Side-effects | Entradas | Saídas/Evidência | Pré-requisitos |
|---|---|---|---|---|---|
| `check_models_requirements.py` | Valida FKs, colunas e constraints de modelos SQLAlchemy contra docs/_generated/schema.sql em 3 perfis | FS_READ | --table <nome> (obrigatório); --profile fk|strict|lenient (default: fk); lê model_requirements_exceptions.json | stdout: lista de violações ou 'OK'; exit 0/4 | docs/_generated/schema.sql existente; modelo SQLAlchemy importável; venv backend ativado |


### 4.5 checks/openapi/ — Checks de contrato API

| Arquivo | Descrição | Side-effects | Entradas | Saídas/Evidência | Pré-requisitos |
|---|---|---|---|---|---|
| `check_contract_drift.py` | Compara docs/ssot/openapi.json contra app.openapi() live para detectar drift de contrato; suporta --fix | FS_READ; FS_WRITE (--fix) | --verbose (flag); --fix (flag); env JWT_SECRET, DATABASE_URL (ou .env) | stdout: diff de paths/schemas ou 'No drift'; docs/ssot/openapi.json (se --fix); exit 0/20/3 | venv backend ativado; app.main importável; docs/ssot/openapi.json existente; JWT_SECRET configurado |


### 4.6 checks/policy/ — Checks de policy compliance

| Arquivo | Descrição | Side-effects | Entradas | Saídas/Evidência | Pré-requisitos |
|---|---|---|---|---|---|
| `check_policy_manifest.ps1` | Wrapper de integridade: delega para scripts/_policy/check_policy_manifest.ps1 | FS_READ | Nenhum argumento | stdout; exit 0/2/3 | scripts/_policy/check_policy_manifest.ps1 existente |
| `check_policy_md_is_derived.ps1` | Wrapper anti-drift: delega para scripts/_policy/check_policy_md_is_derived.ps1 | FS_READ | Nenhum argumento | stdout; exit 0/2/3 | scripts/_policy/check_policy_md_is_derived.ps1 existente |
| `check_scripts_policy.ps1` | Wrapper de governança: delega para scripts/_policy/check_scripts_policy.ps1 | FS_READ | Nenhum argumento | stdout; exit 0/2/3 | scripts/_policy/check_scripts_policy.ps1 existente |


### 4.7 checks/schema/ — Checks de dados canônicos

| Arquivo | Descrição | Side-effects | Entradas | Saídas/Evidência | Pré-requisitos |
|---|---|---|---|---|---|
| `check_canonical_data.py` | Conta registros de tabelas canônicas (roles, permissions, positions) e compara counts com valores esperados hardcoded | DB_READ; FS_READ | Nenhum arg CLI; env DATABASE_URL_SYNC (ou .env) | stdout: status por tabela (OK/FAIL) com contagem real vs esperada; exit 0/1 | PostgreSQL rodando; tabelas canônicas populadas (seed executado); DATABASE_URL_SYNC configurado |
| `check_routes_list.py` | Importa app.api.v1.routers.exercises e lista todas as rotas registradas | FS_READ | Nenhum arg CLI; executado a partir do backend root | stdout: path + métodos HTTP por rota; exit 0/1 | venv backend ativado; app.api.v1.routers.exercises importável |


### 4.8 Raiz de checks/ — Validação de audit packs e protocolo de correção

| Arquivo | Descrição | Side-effects | Entradas | Saídas/Evidência | Pré-requisitos |
|---|---|---|---|---|---|
| `check_audit_pack.py` | Valida estrutura completa de audit pack: summary.json, context.json, checks/<GATE_ID>/, campos obrigatórios e coerência de exit_code vs status | FS_READ | Posicionais: <RUN_ID>; --root <path> (legacy) | stdout: 'SUCCESS: audit pack verified' ou 'ERROR: <motivo>'; exit 0/4 | evidence pack root com summary.json existente; checks/ com ≥1 gate folder; result.json por gate com campos id, command, exit_code, status, duration_ms, artifacts |
| `check_audit_pack_env.py` | Wrapper de check_audit_pack.py via variáveis de ambiente | FS_READ | env HB_AUDIT_RUN_ID (obrigatório); HB_REPORTS_ROOT (default: _reports) | stdout: delegado de check_audit_pack.py; exit propagado ou 4 se RUN_ID ausente | HB_AUDIT_RUN_ID definido; audit pack existente |
| `check_correction_protocol.py` | Valida protocolo de correção: gates obrigatórios por capability (FAILURE_TO_GATES + BUILD_LOCK_INTEGRITY), estado YAML de case files, e integridade dos audit packs referenciados | FS_READ | Posicionais: <CORR_ID>; --root <path> (default: _reports) | stdout: 'SUCCESS: protocol compliant' ou 'ERROR: <motivo>'; exit 0/4 | PyYAML instalado; docs/_canon/_agent/GATES_REGISTRY.yaml e FAILURE_TO_GATES.yaml existentes; _reports/cases/<CORR_ID>/ com state.yaml, facts.yaml, repro.yaml, patch_plan.yaml, evidence_manifest.json, links.yaml |
| `test_check_correction_protocol.py` | Suíte de testes unitários (pytest) para check_correction_protocol.py | nenhum | Executado via pytest scripts/checks/test_check_correction_protocol.py | stdout: pytest report; exit 0 (pass) / 1 (fail) | Python 3.11.9 + pytest instalado |


### 4.9 Pastas reservadas

## 5. diagnostics/

Diagnóstico (read-only, sem side-effects destrutivos). Apenas leem dados e emitem relatórios.

### 5.1 diagnostics/auth/ — Diagnóstico de autenticação

| Arquivo | Descrição | Side-effects | Entradas | Saídas/Evidência | Pré-requisitos |
|---|---|---|---|---|---|
| `diag_analyze_permissions.py` | Analisa ROLE_PERMISSIONS de permissions_map.py e compara contagens por papel contra valores esperados hardcoded | FS_READ | Nenhum arg CLI; importa app.core.permissions_map (sem DB) | stdout: matriz de permissões por papel + tabela expected vs actual; exit 0/1 | venv backend ativado; app.core.permissions_map importável |


### 5.2 diagnostics/db/ — Diagnóstico de banco

| Arquivo | Descrição | Side-effects | Entradas | Saídas/Evidência | Pré-requisitos |
|---|---|---|---|---|---|
| `diag_check_alembic_version.py` | Lê alembic_version via SQLAlchemy síncrono e emite versão atual ou exit code 2/3 se erro | DB_READ; FS_READ | Nenhum arg CLI; env DATABASE_URL_SYNC (ou .env) | stdout: string da versão Alembic; exit 0/2/3 | PostgreSQL rodando; tabela alembic_version existente; DATABASE_URL_SYNC configurado |
| `diag_decode_token.py` | Decodifica JWT do arquivo de autenticação Playwright (coordenador.json) sem verificar assinatura, usando PyJWT | FS_READ | Nenhum arg CLI; path hardcoded (Hb Track - Fronted/playwright/.auth/coordenador.json) | stdout: payload JWT decodificado como JSON; exit 0/1 | PyJWT instalado; coordenador.json existente (gerado pelo Playwright após login) |
| `diag_decode_token_manual.py` | Decodifica JWT do arquivo Playwright manualmente via base64, sem biblioteca jwt | FS_READ | Nenhum arg CLI; path hardcoded (Hb Track - Fronted/playwright/.auth/coordenador.json) | stdout: payload JWT decodificado como JSON; exit 0/1 | coordenador.json existente (gerado pelo Playwright após login) |
| `diag_parity_classify.py` | Parseia log do Alembic autogenerate e classifica mudanças em categorias (table/column/type/etc.); emite relatório JSON | FS_READ; FS_WRITE | --log <path> (obrigatório, arquivo de log Alembic); --out <path> (obrigatório, destino JSON) | <path>.json com classificação por categoria; exit 0/1 | Arquivo de log Alembic existente (gerado por alembic autogenerate ou check) |


### 5.3 diagnostics/runtime/ — Diagnóstico de runtime Python

| Arquivo | Descrição | Side-effects | Entradas | Saídas/Evidência | Pré-requisitos |
|---|---|---|---|---|---|
| `diag_vps_python_runtime.sh` | Verifica objetivamente qual Python a VPS está usando e compatibilidade do código HB Track (5 níveis: venv, systemd, /proc, compile, import) | FS_READ; DB_READ (teste de conexão postgres) | Nenhum arg CLI; service name hardcoded (hbtrack-backend.service); venv path hardcoded (/home/deploy/hbtrack-backend/current/venv) | stdout: resultado por nível de verificação com cores; exit 0/1/2 | Executar na VPS via scp + chmod +x; systemctl disponível |
| `README.md` | Documentação completa com instruções de uso e troubleshooting | — | — | — | — |


### 5.4 Pastas reservadas

## 6. fixes/

Correções pontuais (DB_WRITE). Usar com cuidado — fazem escrita.

### 6.1 fixes/db/ — Correções de banco

| Arquivo | Descrição | Side-effects | Entradas | Saídas/Evidência | Pré-requisitos |
|---|---|---|---|---|---|
| `fix_migrations.py` | Reescreve revision e down_revision em arquivos de migração Alembic para corresponder ao prefixo numérico do nome do arquivo | FS_READ; FS_WRITE | Nenhum arg CLI; path hardcoded para diretório de versions Alembic em Hb Track - Backend/ | arquivos .py de migração com revision/down_revision corrigidos; stdout: log de alterações; exit 0/1 | Diretório de versions Alembic existente; arquivos .py com prefixo numérico no nome |
| `fix_superadmin_pwd.py` | Gera novo hash bcrypt para Admin@123! e atualiza password_hash do superadmin no banco | DB_READ; DB_WRITE; FS_READ | Nenhum arg CLI; env DATABASE_URL_SYNC (ou .env) | stdout: confirmação de atualização; DB: users.password_hash atualizado para adm@handballtrack.app; exit 0/1 | PostgreSQL rodando; usuário adm@handballtrack.app existente; bcrypt instalado; DATABASE_URL_SYNC configurado |
| `fix_validate_hash.py` | Valida hash bcrypt do superadmin; se inválido, gera novo hash e atualiza o banco | DB_READ; DB_WRITE (condicional); FS_READ | Nenhum arg CLI; env DATABASE_URL_SYNC (ou .env) | stdout: VALID/INVALID + ação tomada; DB: users.password_hash (se inválido); exit 0/1 | PostgreSQL rodando; usuário adm@handballtrack.app existente; bcrypt instalado; DATABASE_URL_SYNC configurado |


### 6.2 Pastas reservadas

## 7. gates/

Gates de CI (orquestradores de checks). Orquestram múltiplos checks e emitem resultado consolidado.

### 7.1 gates/SSOT/ — Gates de SSOT e governança

| Arquivo | Descrição | Side-effects | Entradas | Saídas/Evidência | Pré-requisitos |
|---|---|---|---|---|---|
| `check_hb_profile.ps1` | Wrapper PS1: executa check_hb_track_profile.py e grava log em _reports/gates/ | FS_WRITE | -ProfilePath (default: docs/_canon/HB_TRACK_PROFILE.yaml); -OutDir (default: docs/_generated/_reports/gates) | docs/_generated/_reports/gates/gate_profile.log; exit propagado do Python | check_hb_track_profile.py; Python disponível; arquivo de profile YAML |
| `check_hb_track_profile.py` | Gate L0/L1/L2: valida parse, chaves obrigatórias e existência de todos os artefatos SSOT listados em HB_TRACK_PROFILE.yaml | FS_READ | --profile <path> (default: docs/_canon/HB_TRACK_PROFILE.yaml) | stdout: resultado de cada check com PASS/FAIL; exit 0/1 | HB_TRACK_PROFILE.yaml existente e válido YAML; PyYAML instalado |
| `check_uds_consistency.py` | Gate L2: valida consistência cross-referencial (root index, runtime index, profile refs, diretório _generated/) | FS_READ | Nenhum arg CLI | stdout: resultado de cada cross-ref com PASS/FAIL; exit 0/1 | docs/_INDEX.yaml; docs/product/runtime/_INDEX.yaml; docs/_canon/HB_TRACK_PROFILE.yaml; dirs docs/_generated/ e docs/ssot/ existentes |
| `check_ci_gates_local.ps1` | Orquestrador master: roda 8 gates de CI local (policy, language, manifest, drift, path constants, schema, contract, docs index) replicando GitHub Actions | FS_READ | Switches: -SkipScriptsPolicy, -SkipLanguageLinter, -SkipManifest, -SkipDrift, -SkipPathConstants, -SkipSchemaDrift, -SkipContractDrift, -SkipDocsIndex, -FailFast | stdout: tabela de resultados (PASS/FAIL/SKIP por gate); exit 0/1/3 | Python disponível; DATABASE_URL (para Schema Drift); FastAPI importável (para Contract Drift); todos os sub-gates existentes |


### 7.2 Raiz de gates/ — Geração de Evidence Packs por capability

| Arquivo | Descrição | Side-effects | Entradas | Saídas/Evidência | Pré-requisitos |
|---|---|---|---|---|---|
| `run_capability_gates.py` | Orquestrador de gates por capability: executa suites pytest/alembic para AUTH/RBAC/ATHLETES/TEAMS/TRAINING/DB_MIGRATIONS e gera Evidence Packs estruturados | DB_READ; FS_WRITE; PROC_START_STOP | --capability ALL|AUTH|RBAC|ATHLETES|TEAMS|TRAINING|DB_MIGRATIONS (default: ALL); --run-id <id> (opcional, auto-gerado se omitido); lê Hb Track - Backend/.env para FRONTEND_URL | docs/hbtrack/evidence/AR_<id>/<CAPABILITY>/{context.json, summary.json, *_stdout.log, *_stderr.log}; stdout: tabela de resultados; exit 0/2/3 | venv backend ativado; PostgreSQL rodando; pytest e alembic disponíveis; Hb Track - Backend/.env configurado |


### 7.3 Pastas reservadas

## 8. generate/

Geradores de artefatos derivados a partir de fontes canônicas. Output é sempre em docs/ ou _generated/.

### 8.1 generate/docs/ — Geradores de documentação

| Arquivo | Descrição | Side-effects | Entradas | Saídas/Evidência | Pré-requisitos |
|---|---|---|---|---|---|
| `gen_archive_task.py` | Cria pacote de artefatos de tarefa em docs/execution_tasks/artifacts/<task_id>/ com summary.json, execution_log.txt e evidence_index.md | FS_READ; FS_WRITE | --task-id (obrigatório); --status PASS|FAIL|DRIFT (obrigatório); --description (max 120 chars); --timestamp; --commit; --log-file <path> (opcional) | docs/execution_tasks/artifacts/<task_id>/summary.json; .../execution_log.txt; .../evidence_index.md; exit 0/1 | docs/execution_tasks/artifacts/ existente ou criável |
| `gen_from_approved_commands_registry.py` | Renderiza docs/_canon/08_APPROVED_COMMANDS.md a partir de approved_commands_registry.yaml | FS_READ; FS_WRITE | --check (valida sem escrever); --dry-run; --verbose | docs/_canon/08_APPROVED_COMMANDS.md; exit 0/2/3 | docs/_ai/_specs/approved_commands_registry.yaml existente |
| `gen_from_exit_codes_registry.py` | Renderiza docs/references/exit_codes.md e troubleshooting-map.json a partir de exit_codes_registry.yaml | FS_READ; FS_WRITE | --check; --dry-run; --verbose | docs/references/exit_codes.md; docs/_ai/_maps/troubleshooting-map.json; exit 0/2/3 | docs/_ai/_specs/exit_codes_registry.yaml existente |
| `gen_refresh_task_index.py` | Lê todos os artefatos de tarefas (event.json ou summary.json) e gera INDEX.md e TIMELINE.md consolidados | FS_READ; FS_WRITE | Nenhum arg CLI; usa Path.cwd() como base (executar da raiz do workspace) | docs/execution_tasks/INDEX.md; docs/execution_tasks/TIMELINE.md; exit 0/2/3 | docs/execution_tasks/artifacts/ existente com subdiretórios |
| `gen_scripts_policy_md.py` | DEPRECATED — wrapper que delega para scripts/_policy/render_policy_md.py via subprocess | FS_READ; FS_WRITE (--write) | --check (verifica sem escrever) | --write (gera o MD) | docs/_canon/_agent/SCRIPTS_classification.md (via render_policy_md.py); exit 0/2/3 | scripts/_policy/render_policy_md.py existente; scripts.policy.yaml existente |
| `gen_sync_exit_codes.py` | Sincronização bidirecional: extrai exit codes de exit_codes.md e 09_TROUBLESHOOTING_GUARD_PARITY.md, mescla e gera troubleshooting-map.json | FS_READ; FS_WRITE | --check; --dry-run; --verbose | docs/_ai/_maps/troubleshooting-map.json; exit 0/2/3 | docs/references/exit_codes.md; docs/_canon/09_TROUBLESHOOTING_GUARD_PARITY.md existentes |


### 8.2 generate/schema/ — Geradores de schema e modelos

| Arquivo | Descrição | Side-effects | Entradas | Saídas/Evidência | Pré-requisitos |
|---|---|---|---|---|---|
| `gen_autogen_model_from_db.py` | Auto-gera blocos HB-AUTOGEN em arquivos de modelo SQLAlchemy a partir do schema live do DB via Inspector, preservando customizações | DB_READ; FS_READ; FS_WRITE (subcomando apply) | Subcomandos: preview | apply; --table (obrigatório); --schema (default: public); --db-env; --models-dir; --out; --create; --model-file; --class-name; lê docs/ssot/schema.sql para FK ondelete | stdout (preview) ou modelo SQLAlchemy com bloco HB-AUTOGEN atualizado (apply); exit 0/1/2/3 | PostgreSQL rodando; DATABASE_URL_SYNC configurado; docs/ssot/schema.sql existente; venv backend ativado |
| `gen_migration_0041.py` | Gera statements SQL INSERT para permissions e role_permissions lendo ROLE_PERMISSIONS de permissions_map.py | FS_READ | Nenhum arg CLI; importa app.core.permissions_map (sem DB) | stdout: SQL INSERT statements prontos para uso em migração Alembic; exit 0/1 | venv backend ativado; app.core.permissions_map importável |
| `gen_migration_hash.py` | Gera hash bcrypt para a senha Admin@123! usando salt aleatório e verifica o resultado | NONE | Nenhum arg CLI; sem DB; sem env vars | stdout: hash bcrypt gerado + resultado de verificação; exit 0/1 | bcrypt instalado no ambiente Python |
| `gen_models_gate.ps1` | Gate completo de autogeneration: PRE-parity check → autogen model a partir do DB → POST-parity check → validação de requirements | DB_READ; FS_WRITE | -Table (obrigatório); -Create (switch); -Profile fk|strict|lenient; -AllowCycleWarning; -ModelFile; -ClassName; -Allow; -DbUrl | model file gerado/atualizado em app/models/; .hb_guard/baseline.json (se -Create); stdout; exit 0 ou exit code do sub-gate que falhou | DATABASE_URL_SYNC ou DATABASE_URL ou .env; venv Python; gen_autogen_model_from_db.py; ops_parity_gate.ps1; check_agent_guard.py; check_models_requirements.py |


## 9. migrate/

Migrações e backfills de dados. Scripts one-off executados uma vez e mantidos como registro.

### Arquivos

| Arquivo | Descrição | Side-effects | Entradas | Saídas/Evidência | Pré-requisitos |
|---|---|---|---|---|---|
| `migrate_audit_pack_to_canonical.py` | Migra audit packs do formato capability-based (AUTH/, RBAC/, etc.) para estrutura canônica SSOT com checks/ e result.json por gate | FS_READ; FS_WRITE | Posicional: <RUN_ID> (ex: HB-AUDIT-20260218-005); --dry-run (flag); --root <path> (legacy) | <audit_dir>/checks/<gate_id>/{result.json, stdout.log, stderr.log}; <audit_dir>/context.json; <audit_dir>/summary.json; <audit_dir>/_backup_capability_structure/; exit 0/2/3/4 | legacy evidence pack existente com pastas de capability; NÃO idempotente |
| `mig_backfill_training_season_team.py` | Backfill de season_id (via membership) e team_id (via team_registrations) em training_sessions em batches | DB_READ; DB_WRITE | --database-url <url> (obrigatório); --batch-size (default: 100); --dry-run; --only-season; --only-team | stdout: progresso por batch + contagem de registros atualizados; exit 0/1 | PostgreSQL rodando; tabelas training_sessions, memberships, team_registrations existentes; NÃO idempotente |
| `mig_backfill_training_simple.py` | Versão simplificada do backfill de training_sessions (passagem única sem offsets de batch) | DB_READ; DB_WRITE | --database-url <url> (obrigatório); --batch-size (default: 100); --dry-run | stdout: contagem de registros atualizados; exit 0/1 | PostgreSQL rodando; tabelas existentes; NÃO idempotente |
| `mig_import_legacy_training.py` | Importa dados legados de treino de CSVs (sessions.csv + attendance.csv) para o banco via async SQLAlchemy | DB_READ; DB_WRITE; FS_READ; FS_WRITE | --sessions <path> (obrigatório); --org-id <uuid> (obrigatório); --attendance <path> (opcional); --output <path> (default: import_summary.json) | import_summary.json com estatísticas de importação; DB: registros em training_sessions e training_attendances; exit 0/1 | PostgreSQL rodando; venv backend ativado; arquivos CSV existentes; org-id válido no DB; NÃO idempotente |
| `README.md` | Documentação da pasta | — | — | — | — |


## 10. ops/

Operações de infraestrutura para o dia-a-dia: start de serviços, scans de paridade, carga de env.

### Raiz ops/

| Arquivo | Descrição | Side-effects | Entradas | Saídas/Evidência | Pré-requisitos |
|---|---|---|---|---|---|
| `ops_inv.ps1` | Wrapper unificado para invariantes: gate (individual), all (todos), drift (WhatIf), promote (bulk), refresh/ssot (artefatos canônicos) | PROC_START_STOP; FS_WRITE (refresh) | $Command posicional (gate/all/drift/promote/refresh/ssot); $InvId posicional (obrigatório para 'gate') | stdout; artefatos em docs/_generated/ e docs/ssot/; exit propagado | AGENTS.md na raiz; run_invariant_gate.ps1; run_invariant_gate_all.ps1; gen_docs_ssot.py (para refresh) |
| `README.md` | Documentação da pasta | — | — | — | — |


### 10.1 ops/db/ — Operações de banco

| Arquivo | Descrição | Side-effects | Entradas | Saídas/Evidência | Pré-requisitos |
|---|---|---|---|---|---|
| `ops_parity_scan.ps1` | Executa Alembic --autogenerate em modo scan-only para detectar diffs entre models e DB; gera parity_report.json | DB_READ; FS_WRITE | -RepoRoot; -ScriptsRoot; -Message; -TableFilter; -FailOnStructuralDiffs; -SkipDocsRegeneration | docs/_generated/parity-scan.log; docs/_generated/parity_report.json; exit 0/1/2 | Python/venv; DATABASE_URL no .env; Alembic instalado; docs/_generated/ criável |
| `refresh/ops_load_env.ps1` | dot-source: carrega variáveis de um arquivo .env para o processo PowerShell atual, removendo aspas | ENV_WRITE | -EnvPath (default: .env no CWD) | variáveis de ambiente injetadas no processo atual; nenhum arquivo escrito | arquivo .env deve existir |


### 10.2 ops/infra/ — Operações de infraestrutura

| Arquivo | Descrição | Side-effects | Entradas | Saídas/Evidência | Pré-requisitos |
|---|---|---|---|---|---|
| `ops_models_autogen_gate.ps1` | Gate de autogeneration para uso a partir de ops/: PRE-parity → autogen model → POST-parity → requirements validation | FS_WRITE; DB_READ | -Table (obrigatório); -Create; -Profile; -AllowCycleWarning; -ModelFile; -ClassName; -Allow; -DbUrl | model file gerado/atualizado; .hb_guard/baseline.json (se -Create); exit propagado | app/models/ localizável; DATABASE_URL_SYNC ou .env; venv Python; scripts de geração e parity existentes |
| `ops_models_batch.ps1` | Batch runner: refresh SSOT → extrai tabelas do schema.sql → requirements scan em lote → gate apenas nas FAIL | DB_READ; FS_READ; FS_WRITE | -AutoTables FromSSOT|None; -ExcludeTables; -Tables; -TablesFile; -DefaultProfile; -SkipRefresh; -SkipGate; -DryRun; -NoFailFast; -AllowBaselineSnapshot; CWD deve ser backend root | log em %TEMP%; CSV em %TEMP%; model files modificados; exit 0 ou exit code da falha | CWD = 'Hb Track - Backend'; venv; check_models_requirements.py; ops_models_autogen_gate.ps1; docs/ssot/schema.sql; .hb_guard/baseline.json |
| `ops_parity_gate.ps1` | Gate de paridade para uma tabela: verifica agent_guard (baseline vs estado atual) → parity_scan → valida ciclos FK | DB_READ; FS_READ | -Table (obrigatório); -Allow; -AllowEnvPy; -AllowCycleWarning; -ParityReportPath; -SkipDocsRegeneration | stdout; lê/valida parity_report.json; exit 0/2 | .hb_guard/baseline.json; check_agent_guard.py; venv Python; parity_report.json |
| `ops_start_celery_beat.ps1` | Inicia Celery Beat scheduler para jobs periódicos (weekly overload, wellness, cleanup), verificando/iniciando Redis antes | PROC_START_STOP | Nenhum argumento; usa app.core.celery_app | processo Celery Beat em foreground (bloqueante); stdout | CWD em backend ou raiz; Python + Celery instalados; Redis rodando (ou Docker) |
| `ops_start_celery_beat_backup.ps1` | Cópia de backup de ops_start_celery_beat.ps1; usa binário celery direto (legacy/backup) | PROC_START_STOP | Nenhum argumento; CWD deve ser raiz do repo | processo Celery Beat em foreground; stdout | subpasta 'Hb Track - Backend' no CWD; binário celery no PATH; Redis disponível |
| `ops_start_celery_worker.ps1` | Inicia Celery Worker (pool=solo, concurrency=4) para processar tasks assíncronas, verificando/iniciando Redis | PROC_START_STOP | Nenhum argumento; usa app.core.celery_app | processo Celery Worker em foreground; stdout | CWD em backend ou raiz; Python + Celery instalados; Redis rodando (ou Docker) |
| `ops_start_flower.ps1` | Inicia Flower (UI de monitoramento do Celery) na porta 5555 com basic auth admin:hbtrack2026 | PROC_START_STOP | Nenhum argumento; usa app.core.celery_app | processo Flower em foreground em http://localhost:5555; stdout | CWD em backend ou raiz; Flower instalado; Redis rodando (ou Docker) |


## 11. plans/

Sistema de execução de planos com suporte a DAG, locks, snapshots de contexto e métricas. Usado para orquestrar tarefas complexas de forma controlada.

### Arquivos

| Arquivo | Descrição | Side-effects | Entradas | Saídas/Evidência | Pré-requisitos |
|---|---|---|---|---|---|
| `config.py` | Configuração centralizada de paths absolutos (via pathlib.Path); exporta constantes para todos os scripts do subsistema | nenhum | Nenhum arg CLI (módulo importável) | Constantes: SCRIPTS_PLANS_ROOT, PROJECT_ROOT, DOCS_ROOT, PLANS_DIR, IMPLEMENTED_DIR, LOCKS_FILE, METRICS_FILE, HB_BACKEND_DIR | Nenhum |
| `check_locks.py` | Gerencia file locks para Plans: verifica/adquire/libera locks exclusivos e compartilhados em locks.yaml para evitar conflitos entre Plans paralelos | FS_WRITE | Posicional: path do Plan .md; flags --acquire, --release, --list | scripts/plans/locks.yaml criado/atualizado; stdout: conflitos ou locks ativos; exit 0/1 | config.py em scripts/plans/; yaml instalado; arquivo Plan .md existente |
| `executor_workflow.py` | Orquestrador interativo do fluxo Architect-Executor: pré-checks → dry-run → execução com locks → validação pós (pytest/ruff/mypy/invariants) → homologação manual → finalização | FS_WRITE; ENV_WRITE | Posicional: path do Plan .md; --dry-run; --skip-dry-run; interação via input() em cada fase | Plan movido para implemented/; locks gerenciados; stdout com progresso; exit 0/1 | generate_context_snapshot.py, validate_plan_adherence.py, check_locks.py, plan_status.py em scripts/plans/; pytest, ruff, mypy no PATH ou venv; Plan com TASK-ID, Status, Contrato de Entrada, Critérios de Conclusão |
| `generate_context_snapshot.py` | Gera snapshot do estado atual do repo para o Architect AI: git state, backend health, schema DB, estrutura de diretórios, estatísticas de testes, dependências, invariantes, migrações recentes | DB_READ (alembic current) | Nenhum arg CLI; saída para stdout; lê config.py para paths | stdout: snapshot formatado por seções ##; inclui SNAPSHOT DIAGNOSTICS com ERRORS/WARNINGS/BLOCKING CONDITIONS; exit 0 | config.py em scripts/plans/; Alembic e pytest opcionais (graceful degradation); backend em 'Hb Track - Backend/' |
| `plan_status.py` | Gerencia ciclo de vida dos Plans: lê/define status (RASCUNHO/EM_REVISAO/APROVADO/EXECUTADO/OBSOLETO), move Plan para implemented/ ao executar | FS_WRITE | Posicional: path do Plan .md; flags --set STATUS, --executed, --list | stdout: status e elegibilidade; arquivo .md atualizado com Status: e timestamp; Plan movido para implemented/ se --executed; exit 0/1 | config.py (PLANS_DIR, IMPLEMENTED_DIR); Plan .md com campos TASK-ID e Status: |
| `record_metrics.py` | Coleta e reporta métricas de ROI do fluxo Architect-Executor: tempo planejamento/execução/homologação, bugs, rollbacks, rework | FS_WRITE | Posicional: TASK-ID; flags --plan-time, --exec-time, --homolog-time, --bugs, --rollbacks, --rework, --baseline, --report, --compare | config.METRICS_FILE (JSON) criado/atualizado; stdout: métricas/relatório/comparação; exit 0/1 | config.py (METRICS_FILE); nenhum DB necessário |
| `validate_context_snapshot.py` | Valida arquivo de snapshot gerado por generate_context_snapshot.py contra schema v2.0: seções obrigatórias, campos requeridos, valores enum | FS_READ | Posicional: path do arquivo snapshot .txt | stdout: PASS com detalhes ou FAIL com lista de erros; exit 0 (PASS) / 1 (FAIL) | config.py; arquivo snapshot existente gerado por generate_context_snapshot.py |
| `validate_dag.py` | Valida DAG de dependências entre Plans (YAML): detecta ciclos, ordena topologicamente (Kahn), verifica executabilidade | FS_READ | Posicional: path do arquivo DAG .yaml; flags --order, --can-execute PLAN-ID | stdout: validação / ordem de execução / elegibilidade; exit 0/1 | config.py (IMPLEMENTED_DIR); yaml instalado; arquivo DAG com chave plans[] |
| `validate_plan_adherence.py` | Verifica se o Executor seguiu o Plan exatamente: compara arquivos e test IDs implementados (via git diff) contra especificado no Plan | FS_READ | Posicional: path do Plan .md; opcional: base_branch (default: main) | stdout: relatório de conformidade (arquivos/testes extras ou faltando); exit 0 (compliant) / 1 (deviations) | config.py (PROJECT_ROOT, BACKEND_TESTS_DIR); git no PATH; Plan .md com seções 2.4.1, 2.4.2, 2.7 |
| `test_snapshot_negative.py` | Testes negativos (pytest) para validação de snapshots | nenhum | Executado via pytest scripts/plans/test_snapshot_negative.py | stdout: pytest report; exit 0/1 | Python 3.11.9 + pytest instalado |
| `__init__.py` | Inicializador do pacote | — | — | — | — |
| `README.md` | Documentação da pasta | — | — | — | — |


## 12. reset/

Reset de ambientes. Scripts destrutivos para resetar banco, ambiente e serviços.

### 12.1 reset/db/

| Arquivo | Descrição | Side-effects | Entradas | Saídas/Evidência | Pré-requisitos |
|---|---|---|---|---|---|
| `reset_db_e2e.ps1` | Pipeline completo de reset E2E: derruba Docker (remove volume) → sobe PostgreSQL → aplica Alembic migrations → executa seed_e2e.py | DB_WRITE; DESTRUCTIVE | -SkipReset; -SkipMigration; -SkipSeed; -Verbose; -PostgresWaitSeconds (default 10) | stdout; banco hb_track_dev populado com dados E2E; exit 0/1 | Docker e docker-compose em c:\HB TRACK\infra\docker-compose.yml; Python/venv no backend; scripts/seed_e2e.py; Alembic |


### 12.2 reset/env/

| Arquivo | Descrição | Side-effects | Entradas | Saídas/Evidência | Pré-requisitos |
|---|---|---|---|---|---|
| `reset_hb_track_dev.ps1` | Reset do banco hb_track_dev: DROP+CREATE schema public → Alembic upgrade head → SQL migration 0053 → seed canônico determinístico (32 users, 16 teams, 240 athletes) | FS_WRITE; DESTRUCTIVE; PROC_START_STOP | Nenhum argumento; lê DATABASE_URL_SYNC do .env no backend | stdout; banco hb_track_dev resetado e populado; exit 0/1 | .env com DATABASE_URL_SYNC; PostgreSQL em localhost:5433; psql no PATH; venv Python; db/migrations/0053_training_sessions_review_flow.sql; scripts/seed_e2e_canonical.py --deterministic |


### 12.3 reset/services/

| Arquivo | Descrição | Side-effects | Entradas | Saídas/Evidência | Pré-requisitos |
|---|---|---|---|---|---|
| `reset_and_start.ps1` | Pipeline completo: chama reset-hb-track-dev.ps1 → mata porta 8000 → inicia uvicorn em nova janela PS → mata porta 3000 → inicia Next.js em nova janela PS | PROC_START_STOP; DESTRUCTIVE | Nenhum argumento; paths hardcoded C:\HB TRACK | 2 novas janelas PowerShell (backend em :8000, frontend em :3000); exit 0/1 | reset-hb-track-dev.ps1 no backend; package.json em 'Hb Track - Fronted'; PostgreSQL ativo; npm disponível |


## 13. run/

Runners master (orquestradores) que chamam scripts de outras categorias em ordem controlada.

### Arquivos

| Arquivo | Descrição | Side-effects | Entradas | Saídas/Evidência | Pré-requisitos |
|---|---|---|---|---|---|
| `run_checks.ps1` | **Stub** (implementação pendente) para executar checks em lote | NONE | Nenhum | stdout: 'Runner: run_checks.ps1 - Implementacao pendente' | Nenhum |
| `run_fixes.ps1` | **Stub** (implementação pendente) para executar fixes em lote | NONE | Nenhum | stdout: 'Runner: run_fixes.ps1 - Implementacao pendente' | Nenhum |
| `run_generate.ps1` | **Stub** (implementação pendente) para executar geradores em lote | NONE | Nenhum | stdout: 'Runner: run_generate.ps1 - Implementacao pendente' | Nenhum |
| `run_invariant_gate.ps1` | Gate runner canônico para uma invariante: parseia SPEC do INVARIANTS_TRAINING.md → executa verify_invariants_tests.py --inv → pytest no node → gera hashes/meta → verifica golden drift | FS_WRITE | -InvId (obrigatório, ex: INV-TRAIN-002); -Root (default: C:\HB TRACK); -Backend (default: C:\HB TRACK\Hb Track - Backend) | docs/_generated/_reports/{InvId}/{timestamp}/{verify,verify_inv,pytest,hashes,meta}.txt; stdout; exit 0/1/3 | INVARIANTS_TRAINING.md; verify_invariants_tests.py; arquivo de teste referenciado no SPEC; venv Python |
| `run_invariant_gate_all.ps1` | Executa gate runner para todos os invariantes com golden baselines; agrega resultados; suporta promoção e dry-run | FS_WRITE (se -Promote) | -Verbose; -Promote (promove golden baselines com drift); -WhatIf (dry-run da promoção) | stdout: tabela de resultados (PASS/FAIL/DRIFT por INV-ID); golden baselines atualizados se -Promote; exit 0/1/3 | docs/_generated/_reports/ existente; run_invariant_gate.ps1 existente; invariantes com golden baselines |
| `run_migrate.ps1` | **Stub** (implementação pendente) para executar migrações | NONE | Nenhum | stdout: 'Runner: run_migrate.ps1 - Implementacao pendente' | Nenhum |
| `run_new_script.ps1` | Scaffold determinístico de novos scripts: cria arquivo no folder/prefixo correto, injeta header HB_SCRIPT_* canônico | FS_WRITE | -Kind (CHECK/DIAGNOSTIC/FIX/GENERATE/MIGRATE/OPS/RESET/SEED/RUNNER/TEMP); -Scope; -Action; -Ext py|ps1|sql; -Qualifier; -Force (obrigatório para RESET/MIGRATE/OPS); -OpenAfter; -RegisterInScriptsReadme | arquivo criado em scripts/{category}/{scope}/{prefix}{scope}__{action}.{ext}; exit 0/2/3 | CWD deve ser repo root; arquivo alvo não deve existir |
| `run_ops.ps1` | **Stub** (implementação pendente) para executar ops em lote | NONE | Nenhum | stdout: 'Runner: run_ops.ps1 - Implementacao pendente' | Nenhum |
| `run_reset.ps1` | **Stub** (implementação pendente) para executar resets | PROC_START_STOP; DESTRUCTIVE (quando implementado) | Nenhum | stdout: 'Runner: run_reset.ps1 - Implementacao pendente' | Nenhum |
| `run_security.ps1` | **Stub** (implementação pendente) para executar checks de segurança | NONE | Nenhum | stdout: 'Runner: run_security.ps1 - Implementacao pendente' | Nenhum |
| `run_seeds.ps1` | **Stub** (implementação pendente) para executar seeds | NONE | Nenhum | stdout: 'Runner: run_seeds.ps1 - Implementacao pendente' | Nenhum |
| `run_test_login.ps1` | Smoke test de login: faz POST /api/v1/auth/login com credenciais do super admin hardcoded e reporta sucesso/falha | NET | Nenhum; endpoint hardcoded http://localhost:8000 | stdout: token parcial (sucesso) ou erro HTTP; sem exit code explícito | backend FastAPI rodando em localhost:8000; super admin populado no banco |
| `run_test_seeds.py` | Executa seeds de teste em ordem: organização IDEC + temporada 2026 → usuários de teste 1 por papel | DB_WRITE | Nenhum arg CLI; importa seed_test_organization e seed_test_users | stdout: progresso; sys.exit(1) em caso de erro | DATABASE_URL configurado; seeds/test/*.py; banco com schema aplicado |
| `run_validate_implementation.py` | Valida implementação do Training Module: lista triggers tr_*, verifica 13 tabelas esperadas, índices, colunas (Step 2) e testa trigger de internal_load | DB_READ | Nenhum arg CLI; env DATABASE_URL (converte asyncpg→psycopg2 automaticamente) | stdout: relatório de triggers/tabelas/índices/colunas/trigger test; sem exit code explícito | DATABASE_URL definido; banco com schema do Training Module aplicado; psycopg2 e SQLAlchemy instalados |
| `README.md` | Documentação da pasta | — | — | — | — |


## 14. seeds/

Dados canônicos e de teste. Divididos em official/ (produção) e test/ (desenvolvimento/E2E).

### 14.1 seeds/official/ — Seeds canônicos (produção)

| Arquivo | Descrição | Side-effects | Entradas | Saídas/Evidência | Pré-requisitos |
|---|---|---|---|---|---|
| `seed_exercises.py` | Seed de exercise_tags (hierárquicos) e exercises de exemplo no banco | DB_READ; DB_WRITE | Nenhum arg CLI; DB URL hardcoded (localhost:5433/hb_track_dev) | stdout: confirmação de registros inseridos; DB: exercise_tags + exercises populados; exit 0/1 | PostgreSQL local na porta 5433; asyncpg instalado; NÃO idempotente (falha se registros já existem) |
| `seed_organization.py` | Seed da organização inicial 'Clube HB Tracking'; pula se qualquer organização já existir | DB_READ; DB_WRITE | Nenhum arg CLI; usa app.core.db.db_context (DATABASE_URL via venv/env) | stdout: confirmação de inserção ou skip; DB: registro em organizations; exit 0/1 | PostgreSQL rodando; venv backend ativado com DATABASE_URL; app.core.db importável; condicionalmente idempotente |
| `seed_roles.py` | Seed dos 5 papéis canônicos (membro/atleta/treinador/coordenador/dirigente) com ON CONFLICT DO NOTHING | DB_WRITE | Nenhum arg CLI; DB URL hardcoded (URL Neon production) | stdout: confirmação de inserção; DB: registros em roles; exit 0/1 | Acesso à URL Neon production hardcoded; psycopg2 instalado; efetivamente idempotente (ON CONFLICT DO NOTHING) |


### 14.2 seeds/test/ — Seeds de teste (E2E/dev)

| Arquivo | Descrição | Side-effects | Entradas | Saídas/Evidência | Pré-requisitos |
|---|---|---|---|---|---|
| `seed_test_organization.py` | Seed da organização de teste 'IDEC' + time opcional + temporada 2026; pula se IDEC já existir | DB_READ; DB_WRITE | Nenhum arg CLI; usa app.core.db.db_context (DATABASE_URL via venv/env) | stdout: confirmação por entidade inserida ou skip; DB: organizations + teams + seasons; exit 0/1 | PostgreSQL rodando; venv backend ativado; app.core.db importável; condicionalmente idempotente |
| `seed_test_users.py` | Seed de 5 usuários de teste (dirigente/coordenador/treinador/atleta/membro) com memberships para a org IDEC; pula emails existentes | DB_READ; DB_WRITE | Nenhum arg CLI; usa app.core.db.db_context | stdout: confirmação por usuário inserido ou skip; DB: users + memberships para org IDEC; exit 0/1 | PostgreSQL rodando; org IDEC existente (seed_test_organization.py executado antes); venv backend ativado; passlib+bcrypt instalados; condicionalmente idempotente |


## 15. ssot/

Geradores dos artefatos Single Source of Truth derivados do banco e app live.

### Arquivos

| Arquivo | Descrição | Side-effects | Entradas | Saídas/Evidência | Pré-requisitos |
|---|---|---|---|---|---|
| `gen_docs_ssot.py` | Gerador mestre de SSOT: produz openapi.json, schema.sql, alembic_state.txt e manifest.json para docs/_generated/ e docs/ssot/ | DB_READ; FS_READ; FS_WRITE; PROC_START_STOP | --all (todos os artefatos); --openapi; --schema; --alembic; --output <dir> (override destino); env DATABASE_URL, DATABASE_URL_SYNC, JWT_SECRET, BASE_URL, HB_DOCS_GENERATED_DIR (ou .env) | docs/ssot/openapi.json; docs/ssot/schema.sql; docs/ssot/alembic_state.txt; docs/_generated/manifest.json; exit 0/1 | PostgreSQL rodando; pg_dump no PATH; venv backend ativado; app.main importável; alembic configurado; DATABASE_URL e JWT_SECRET configurados |
| `gen_docs_ssot.ps1` | Wrapper PowerShell para o gerador Python de SSOT | FS_WRITE; DB_READ | Nenhum argumento; delega para gen_docs_ssot.py | Idem gen_docs_ssot.py | Idem gen_docs_ssot.py; Python disponível |


## 16. temp/

Área de trabalho para scripts temporários. Conteúdo excluído via .gitignore.

### Arquivos

| Arquivo | Descrição |
|---|---|
| `.gitignore` | Ignora tudo exceto templates e README |
| `README.md` | Documentação da pasta |


## 17. Arquivos raiz

Arquivos na raiz da pasta scripts/

### Arquivos

| Arquivo | Descrição | Side-effects |
|---|---|---|
| `__init__.py` | Inicializador do pacote scripts (permite imports) | nenhum |
| `README.md` | Documentação geral da pasta scripts | — |
| `artifacts/` | Diretório para outputs de scripts (protegido por .gitignore) | — |
