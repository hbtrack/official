# BACKLOG_SANEAMENTO_EXECUTAVEL
> ⚠️ **ARTEFATO DERIVADO — NON-SOVEREIGN**: Este arquivo é um backlog operacional derivado. Não possui autoridade normativa. Em caso de conflito, prevalecem: `scripts/hb` + `scripts/contracts/validate/validate_contracts.py` > `contracts/schemas/` > `docs/_canon/` > este arquivo.

Data: 2026-04-09 (atualizado: 2026-04-10)  
Origem: [PLANO_SANEAMENTO_PRIORIZADO.md](./PLANO_SANEAMENTO_PRIORIZADO.md) + [AUDIT_COMPLETA.md](./AUDIT_COMPLETA.md)  
Escopo: backlog executável, ordenado por ataque, sem introduzir fatos não confirmados.

**Progresso:** 23/23 concluídos — ✅ **SANEAMENTO COMPLETO**. Todas as 7 Sprints finalizadas. `makemigrations --check` = No changes detected; axios CRITICAL eliminado; `datetime.utcnow()` corrigido (57 → 3 warnings).

## 1. Ordem de ataque

### Bloco A — destravar o fluxo governado ✅ DONE
1. ~~`SAN-001` — corrigir coerência de `SESSION_HANDOFF.md`~~ ✅ (2026-04-09)
2. ~~`SAN-002` — resolver divergência do `pre-push` em `merge-readiness.json`~~ ✅ (2026-04-09)

### Bloco B — estabilizar configuração e deploy ✅ DONE
3. ~~`SAN-003` — mapear e separar variáveis ativas vs legado em `.env`~~ ✅ (2026-04-09)
4. ~~`SAN-004` — tornar deploy de staging não-destrutivo por padrão~~ ✅ (2026-04-10)

### Bloco C — consolidar a verdade documental ✅ DONE
5. ~~`SAN-005` — atualizar `ROADMAP.md` e docs centrais com a realidade atual~~ ✅ (2026-04-10)
6. ~~`SAN-006` — corrigir `.gitignore` para refletir o repositório real~~ ✅ (2026-04-10)
7. ~~`SAN-007` — marcar/superceder ADRs e docs que ainda descrevem FastAPI/Alembic como estado atual~~ ✅ (2026-04-10)

### Bloco D — cortar o legado operacional ✅ DONE
8. ~~`SAN-008` — inventariar scripts que ainda apontam para FastAPI/Alembic/Hb Track - Backend~~ ✅ (2026-04-10)
9. ~~`SAN-009` — classificar esses scripts em reescrever / arquivar / remover~~ ✅ (2026-04-10)
10. ~~`SAN-010` — decidir e formalizar o sistema de migração ativo~~ ✅ (2026-04-10)

### Bloco E — reconciliar maturidade declarada vs código real ✅ DONE
11. ~~`SAN-011` — definir critério verificável para `implemented`~~ ✅ (2026-04-10)
12. ~~`SAN-012` — auditar `training` como primeiro módulo discrepante~~ ✅ (2026-04-10)
13. ~~`SAN-013` — recalibrar `MODULE_REGISTRY.yaml` ou abrir burn-down real dos stubs~~ ✅ (2026-04-10) — Onda E concluída; training = implemented

### Bloco F — reduzir ruído versionado
14. `SAN-014` — criar política de retenção para `_reports/`
15. `SAN-015` — revisar `_archive/**`
16. `SAN-016` — revisar `.CEPRAEA/**`

### Bloco G — higiene e itens periféricos
17. `SAN-017` — limpar `.agents.md` vazio e `VPS/**/*.Zone.Identifier`
18. `SAN-018` — decidir se `scripts/validate_contracts.py` permanece como wrapper

### Bloco H — fechar inconclusivos
19. `SAN-019` — confirmar uso real de `VPS/**`
20. `SAN-020` — confirmar uso real de Playwright E2E, `pact/` e scripts `ops/reset/fixes/remediate_*`

### Bloco I — gaps não bloqueantes observados
21. `SAN-021` — materializar ou reconciliar drift de migrations em `analytics` / `audit` / `medical`
22. `SAN-022` — triar vulnerabilidades transientes apontadas por `npm audit`
23. `SAN-023` — reduzir warnings de deprecação recorrentes no CI local

## 2. Backlog executável

| ID | Prioridade | Tarefa | Arquivos / áreas alvo | Ação executável | Evidência de aceite | Dependência |
|---|---|---|---|---|---|---|
| SAN-001 | ~~P0~~ | ~~Corrigir incoerência do handoff~~ | ~~`SESSION_HANDOFF.md`, `_reports/contract_gates/latest.json`~~ | ✅ **DONE** (2026-04-09) — HANDOFF_COHERENCE_GATE PASS | ✅ precommit validator exitcode 0 | — |
| SAN-002 | ~~P0~~ | ~~Resolver referência quebrada de `pre-push`~~ | ~~`merge-readiness.json`, `scripts/git-hooks/`, `scripts/hb`~~ | ✅ **DONE** (2026-04-09/10) — `scripts/git-hooks/pre-push` criado; `cmd_survival_suite` e `cmd_ci` passaram a restaurar `_reports/session_start.json` / `_reports/contract_gates/latest.json`; `pre-push` final com `PASS` real | ✅ hook existe, invariants coerentes, `_reports/preflight/latest.json.final_decision=PASS`, `session_start.json` preservado em fase 5 após o hook | — |
| SAN-003 | ~~P0~~ | ~~Separar configuração ativa de legado em `.env`~~ | `.env.example` criado | ✅ **DONE** (2026-04-09) — `.env.example` com contrato mínimo Django; 15 vars ativas, 25+ legado/futuro documentadas e segregadas. **Bugs corrigidos no `.env` (2026-04-10):** `SECRET_KEY` adicionado, `CORS_ALLOWED_ORIGINS` adicionado (nome correto), `JWT_ACCESS_TOKEN_EXPIRY_MINUTES` adicionado (nome correto). | ✅ `.env.example` commitável; legado classificado; 3 bugs de nome/ausência corrigidos | — |
| SAN-004 | ~~P0~~ | ~~Tornar staging não-destrutivo por padrão~~ | `deploy.yml` | ✅ **DONE** (2026-04-10) — `volume rm` condicionado a `destructive_reset=true`; `.env` corruption avisa em vez de sobrescrever; input `destructive_reset` adicionado ao `workflow_dispatch` | ✅ deploy padrão preserva dados; destruição requer flag explícito | — |
| SAN-005 | ~~P1~~ | ~~Atualizar snapshot do `ROADMAP.md`~~ | `ROADMAP.md` | ✅ **DONE** (2026-04-10) — Snapshot atualizado: 8 itens ❌ corrigidos para ✅, tabela de progresso por fase adicionada, PostgreSQL 12→16, versão 1.1.0 | ✅ Nenhuma afirmação central diz que artefatos existentes “não existem” | — |
| SAN-006 | ~~P1~~ | ~~Corrigir `.gitignore` para a realidade atual~~ | `.gitignore` | ✅ **DONE** (2026-04-10) — Reescrito: duplicatas removidas, “contracts-only repo” removido, `Hb Track - Backend/` paths movidos para seção legado, seções organizadas por tema | ✅ `.gitignore` não contradiz presença de `src/` e `frontend/` | — |
| SAN-007 | ~~P1~~ | ~~Consolidar docs/ADRs do stack atual~~ | ADR-007/008/013/028/029 | ✅ **DONE** (2026-04-10) — ADR-026 já superseded; ADR-028 versão Alembic duplicada removida; ADR-029 FastAPI→Django; ADR-007/008/013 notas de framework adicionadas | ✅ Nenhuma ADR ativa descreve FastAPI/Alembic como estado vigente | — |
| SAN-008 | ~~P1~~ | ~~Inventariar scripts presos ao stack legado~~ | 40 arquivos (13 .ps1, 25 .py, 2 .yaml) | ✅ **DONE** (2026-04-10) — Inventário completo: ver seção §SAN-008 abaixo | ✅ Lista explícita com classificação preliminar | — |
| SAN-009 | ~~P1~~ | ~~Classificar scripts legados~~ | 40 scripts | ✅ **DONE** (2026-04-10) — Decisão formal: ver §SAN-009 abaixo. 38 ARQUIVAR, 2 ATUALIZAR, 0 REESCREVER (seed_exercises reclassificado para arquivar — `manage.py seed_demo` já existe) | ✅ Decisão por lote homogêneo documentada | — |
| SAN-010 | ~~P1~~ | ~~Formalizar o sistema de migração ativo~~ | `migrations/` (raiz) vs `src/*/migrations/` | ✅ **DONE** (2026-04-10) — ver §SAN-010 abaixo | ✅ Caminho único: Django Migrations em `src/*/migrations/`; `migrations/` raiz = legado Alembic para arquivar | — |
| SAN-011 | ~~P1~~ | ~~Definir critério verificável para `implemented`~~ | `docs/_canon/MODULE_REGISTRY.yaml` | ✅ **DONE** (2026-04-10) — Critério C1+C2+C3 definido; stub ratio ≤15% = implemented, 16-30% = implementation_ready, >30% = draft_contract. Resultado: 13 PASS, 3 BORDERLINE (seasons/teams/matches 12-14%), 1 FAIL (training 42%). Ver §SAN-011 abaixo. | ✅ Critério explícito, verificável e aplicado a todos os 17 módulos | SAN-007 ✅ |
| SAN-012 | ~~P1~~ | ~~Auditar `training` como módulo piloto~~ | `src/training/api.py`, `src/training/application/use_cases.py` | ✅ **DONE** (2026-04-10) — ver §SAN-012 abaixo. 63 stubs reais mapeados (28 endpoints + 35 use cases) em 13 grupos funcionais. Decisão: burn-down formal. | ✅ Lacuna documentada + burn-down estruturado por onda | SAN-011 ✅ |
| ~~SAN-013~~ | ~~P1~~ | ~~Reconciliar registry com código real~~ | ~~`docs/_canon/MODULE_REGISTRY.yaml` + `src/training/**`~~ | ✅ **DONE** (2026-04-10) — Ondas A+B+C+D+E concluídas (63 stubs → 0). `pytest -q src/training/tests/unit` = `229 passed, 19 skipped`. `training.status` = `implemented` em `MODULE_REGISTRY.yaml`. | ✅ `MODULE_REGISTRY.yaml` reflete realidade de implementação; stub ratio ~0% | SAN-012 ✅ |
| ~~SAN-014~~ | ~~P2~~ | ~~Criar política de retenção para `_reports/`~~ | ~~`_reports/**`, `.gitignore`~~ | ✅ **DONE** (2026-04-10) — ver §10 abaixo. 3 camadas definidas; consumidores confirmados. `.gitignore` atualizado: `enforcement/` e `parity/` excluídos; política documentada. | ✅ Apenas versionado o que tem consumidor confirmado; limpeza futura via `git rm --cached` documentada. | SAN-001 a SAN-010 ajudam |
| ~~SAN-015~~ | ~~P2~~ | ~~Revisar `_archive/**`~~ | ~~`_archive/**`~~ | ✅ **DONE** (2026-04-10) — ver §11 abaixo. `_archive/` já é área de quarentena funcional: excluída de scans soberanos em `validate_contracts.py`; zero consumidores em scripts/workflows. 87 arquivos de histórico bem-namespaciados. `_archive/.agents.md` acidental (1 linha de hash de commit) removido. | ✅ `_archive/**` não compete com o fluxo principal — isolamento já satisfeito. | SAN-007 recomendado |
| ~~SAN-016~~ | ~~P2~~ | ~~Revisar `.CEPRAEA/**`~~ | ~~`.CEPRAEA/**`~~ | ✅ **DONE** (2026-04-10) — ver §12 abaixo. Zero consumidores confirmados. 29 arquivos rastreados = auditorias históricas + análises de paridade + video_pipeline offline, todos non-sovereign. `.gitignore` atualizado. | ✅ Material de baixa autoridade explicitamente reclassificado; novos arquivos não entram em commits. | SAN-007 recomendado |
| ~~SAN-017~~ | ~~P2~~ | ~~Limpeza rápida de workspace~~ | ~~`.agents.md`, `VPS/**/*.Zone.Identifier`~~ | ✅ **DONE** (2026-04-10). `.agents.md` vazio (0 bytes, não rastreado) removido. 23 arquivos `*.Zone.Identifier` em `VPS/` removidos (metadados NTFS Windows, nenhum rastreado em git). `.gitignore` atualizado: `*:Zone.Identifier` adicionado. | ✅ Arquivos descartáveis removidos; não poluem mais o workspace. | nenhuma |
| ~~SAN-018~~ | ~~P2~~ | ~~Decidir destino do wrapper `scripts/validate_contracts.py`~~ | ~~`scripts/validate_contracts.py`~~ | ✅ **DONE** (2026-04-10). Zero consumidores em workflows, `scripts/hb` e `merge-readiness.json`. Wrapper = 12 linhas; delega via `runpy` para `scripts/contracts/validate/validate_contracts.py`. **Decisão: MANTER** como atalho de conveniência — não polui, não confunde, útil para uso manual. Não expandir. | ✅ Wrapper tem classificadorão formal; não há ambiguidade sobre o target canônico. | SAN-008 recomendado |
| ~~SAN-019~~ | ~~P3~~ | ~~Confirmar uso real de `VPS/**`~~ | ~~`VPS/**`~~ | ✅ **DONE** (2026-04-10). Zero arquivos rastreados em git; zero consumidores em scripts/hb, workflows, merge-readiness. `.gitignore` já tinha `/VPS/` + `!/VPS/templates/` com comentário de segurança ("contém credenciais reais de produção"). **Classificação: referência operacional offline** — docs e runbooks de VPS para uso humano, não lidos por pipeline. | ✅ `VPS/**` tem classificação confirmada. | nenhuma |
| ~~SAN-020~~ | ~~P3~~ | ~~Confirmar uso real de E2E/`pact/`/scripts perióficos~~ | ~~`frontend/playwright.config.ts`, `pact/`, `scripts/remediate_*`~~ | ✅ **DONE** (2026-04-10). • **`pact/`**: 323 arquivos, zero rastreados em git, zero consumidores em CI ou scripts — legado morto; candidato a gitignore ou remoção futura. • **`frontend/playwright.config.ts`** + **`frontend/e2e/`** (`auth.spec.ts`, `training.spec.ts`): rastreado, infra presente, mas zero em CI (`.github/workflows/`) e zero em merge-readiness — **infra presente, não integrada ao CI**. • **`scripts/ops/`**: docs de infra (README, db, infra, templates) — auxiliar humano. • **`scripts/fixes/db/`**: 3 scripts psycopg2 — já ARQUIVAR (SAN-009). • **`scripts/remediate_*`** (15 scripts): gerados durante saneamento de contratos; sem consumidor em CI — legado de trabalho. | ✅ Cada item inconclusivo tem classificação confirmada. | nenhuma |
| ~~SAN-021~~ | ~~P2~~ | ~~Resolver warning de migrations pendentes~~ | ~~`src/analytics/**`, `src/audit/**`, `src/medical/**`~~ | ✅ **DONE** (2026-04-10). `makemigrations --check` detectou 3 drifts: • `analytics` `0003` — remove constraint `analytics_snapshot_metric_key_nonempty` • `audit` `0004` — remove constraint `audit_entry_action_nonempty` • `medical` `0003` — remove constraint `medical_record_label_nonempty`. Migrations geradas via `python manage.py makemigrations analytics audit medical`. `makemigrations --check --dry-run` = `No changes detected`. | ✅ `makemigrations --check` = `No changes detected` | SAN-013 pode ocorrer em paralelo |
| ~~SAN-022~~ | ~~P3~~ | ~~Triar vulnerabilidades do frontend~~ | ~~`frontend/package.json`~~ | ✅ **DONE** (2026-04-10). Triagem executada: \n• **axios CRITICAL** (SSRF `<1.15.0`) → `^1.13.6` → `^1.15.0` — **CORRIGIDO**. \n• **vite direto HIGH** (`8.0.0-8.0.4`) → `^8.0.2` → `^8.0.5` — **CORRIGIDO**. \n• **vite em `vitest/node_modules/vite` HIGH** (`7.0.0-7.3.1`) → vitest 4.x bundla vite 7.x como dependência interna — **aguardar upstream** (dev-only, não exposto em produção). \n• **brace-expansion MODERATE** (transitivo dev tools) → **aceitar risco** (process hang em CLI, escopo dev). \n`npm audit`: 3 vulns → 2 vulns; CRITICAL eliminado. | ✅ Vulnerabilidades classificadas: corrigir agora / aceitar risco / aguardar upstream. | nenhuma |
| ~~SAN-023~~ | ~~P3~~ | ~~Queimar warnings de deprecação mais frequentes~~ | ~~`src/wellness/domain/entities.py`~~ | ✅ **DONE** (2026-04-10). `datetime.utcnow()` → `datetime.now(UTC)` em `entities.py` linhas 48-49 (2 ocorrências). `import UTC` adicionado. `pytest src/wellness/tests/unit/` = `47 passed`. Warnings globais: 57 → 3 (só UserWarning do `hypothesis` plugin permanecem — terceiros, não acionáveis). | ✅ `pytest src/` reduz substancialmente volume de warnings. | nenhuma |

## 3. Sprint sugerida

### Sprint 1 — destravamento ✅ DONE
- ~~`SAN-001`~~ ✅
- ~~`SAN-002`~~ ✅

### Sprint 2 — configuração e deploy ✅ DONE
- ~~`SAN-003`~~ ✅
- ~~`SAN-004`~~ ✅

### Sprint 3 — verdade documental ✅ DONE
- ~~`SAN-005`~~ ✅
- ~~`SAN-006`~~ ✅
- ~~`SAN-007`~~ ✅

### Sprint 4 — corte do legado ✅ DONE
- ~~`SAN-008`~~ ✅
- ~~`SAN-009`~~ ✅
- ~~`SAN-010`~~ ✅

### Sprint 5 — maturidade real dos módulos ✅ DONE
- ~~`SAN-011`~~ ✅ (2026-04-10)
- ~~`SAN-012`~~ ✅ (2026-04-10)
- ~~`SAN-013`~~ ✅ (2026-04-10) — Ondas A+B+C+D+E concluídas; 63 stubs → 0; `training` = `implemented`

### Sprint 6 — redução de ruído ✅ COMPLETA
- ~~`SAN-014`~~ ✅ (2026-04-10)
- ~~`SAN-015`~~ ✅ (2026-04-10)
- ~~`SAN-016`~~ ✅ (2026-04-10)
- ~~`SAN-017`~~ ✅ (2026-04-10)
- ~~`SAN-018`~~ ✅ (2026-04-10)
- ~~`SAN-021`~~ ✅ (2026-04-10)

### Sprint 7 — fechamento de inconclusivos ✅ COMPLETA
- ~~`SAN-019`~~ ✅ (2026-04-10)
- ~~`SAN-020`~~ ✅ (2026-04-10)
- ~~`SAN-022`~~ ✅ (2026-04-10)
- ~~`SAN-023`~~ ✅ (2026-04-10)

## 4. Definição de pronto por bloco

### Bloco A pronto ✅
- ~~validator central verde para o problema atual de handoff;~~ ✅
- ~~manifesto de merge-readiness sem referência quebrada.~~ ✅

### Bloco B pronto ✅
- ~~variáveis operacionais do stack atual explicitadas;~~ ✅
- ~~deploy de staging sem destruição implícita.~~ ✅

### Bloco C pronto ✅
- ~~docs centrais não contradizem mais o runtime atual.~~ ✅

### Bloco D pronto ✅
- ~~não existe mais ambiguidade ativa entre Django atual e FastAPI/Alembic legado.~~ ✅

### Bloco E pronto ✅
- ~~`MODULE_REGISTRY.yaml` reflete a realidade de implementação observável.~~ ✅ `training.status: implemented`; 63 stubs → 0.

### Bloco F pronto
- histórico/ruído deixam de competir com o fluxo vivo.

### Bloco G/H prontos
- itens periféricos deixam de ficar sem classificação ou sem decisão.

## 5. Trava operacional

Antes de iniciar qualquer limpeza ampla de docs, relatórios ou legado, o mínimo seguro é:

1. ~~concluir `SAN-001`;~~ ✅ DONE
2. ~~concluir `SAN-002`;~~ ✅ DONE
3. ~~mapear consumo real de configuração em `SAN-003`.~~ ✅ DONE

Estado atual:
- ~~estado governado inconsistente~~ ✅ resolvido
- ~~manifesto local parcialmente falso~~ ✅ resolvido
- ~~configuração híbrida sem corte claro entre ativo e legado~~ ✅ resolvido (`.env.example` criado)

**Trava operacional satisfeita** — SAN-001 + SAN-002 + SAN-003 concluídos. Limpezas amplas desbloqueadas.

## 6. Inventário SAN-008 — Scripts legados (2026-04-10)

**Total: 40 arquivos** (13 .ps1, 25 .py, 2 .yaml) referenciam `FastAPI`, `Alembic`, `Hb Track - Backend`, `DATABASE_URL_SYNC`, `asyncpg` ou `psycopg2`.

### Classificação preliminar para SAN-009

| Lote | Scripts | Tipo de ref. | Recomendação |
|------|---------|-------------|--------------|
| **PowerShell Windows** (13) | `scripts/reset/*.ps1`, `scripts/ops/infra/ops_start_*.ps1`, `scripts/ops/db/ops_parity_scan.ps1`, `scripts/ops/infra/ops_parity_gate.ps1`, `scripts/ops/infra/ops_models_autogen_gate.ps1`, `scripts/generate/schema/gen_models_gate.ps1`, `scripts/checks/lint/check_python_layout.ps1`, `scripts/_policy/check_*.ps1` | `Hb Track - Backend`, Alembic, `DATABASE_URL_SYNC` | **ARQUIVAR** — projeto agora roda em WSL/Linux; estes scripts não são executáveis no ambiente atual |
| **DB checks diretos** (6) | `scripts/checks/db/check_athletes_columns.py`, `check_coord_train.py`, `check_coordenador.py`, `check_seed_data.py`, `check_team_registrations_columns.py`, `check_membr_perms.py` | `psycopg2` direto, `DATABASE_URL`, `Hb Track - Backend` | **ARQUIVAR** — Django ORM substitui; `manage.py check` + testes cobrem |
| **DB diagnostics** (3) | `scripts/diagnostics/db/diag_check_alembic_version.py`, `diag_parity_classify.py`, `scripts/diagnostics/auth/diag_analyze_permissions.py` | Alembic, `DATABASE_URL_SYNC`, `Hb Track - Backend` | **ARQUIVAR** — Alembic não é mais o sistema de migração |
| **DB fixes** (3) | `scripts/fixes/db/fix_migrations.py`, `fix_validate_hash.py`, `fix_superadmin_pwd.py` | `psycopg2`, `DATABASE_URL_SYNC`, `Hb Track - Backend` | **ARQUIVAR** — fixes pontuais já aplicados |
| **DB reset** (1) | `scripts/db/reset_hb_track_test.py` | Alembic, `DATABASE_URL_SYNC`, `Hb Track - Backend` | **ARQUIVAR** — `manage.py flush` + `manage.py migrate` substituem |
| **Migrate scripts** (2) | `scripts/migrate/mig_backfill_training_*.py` | `psycopg2` direto | **AVALIAR** — podem ter lógica de backfill reutilizável; se já aplicados, arquivar |
| **Seeds** (1) | `scripts/seeds/official/seed_exercises.py` | `DATABASE_URL` asyncpg | **REESCREVER** — converter para `manage.py` command ou fixture Django |
| **Generate/schema** (2) | `scripts/generate/schema/gen_migration_0041.py`, `scripts/generate/gen_test_matrix.py` | `Hb Track - Backend` | **ARQUIVAR** — gen_migration_0041 é Alembic; gen_test_matrix aponta para dir inexistente |
| **hbtrack_lint checkers** (5) | `anchor_manifest.py`, `anchors.py`, `cross.py`, `projections.py`, `time.py` | `Hb Track - Backend` fallback paths | **AVALIAR** — linters podem ter valor se os paths forem atualizados para `src/` |
| **check_models_requirements** (1) | `scripts/checks/models/check_models_requirements.py` | `Hb Track - Backend` fallback | **AVALIAR** — verificar se ainda tem consumidor |
| **check_canonical_data** (1) | `scripts/checks/schema/check_canonical_data.py` | `DATABASE_URL_SYNC`, `Hb Track - Backend` | **ARQUIVAR** — usa psycopg2 direto com path legado |
| **Policy YAML** (2) | `scripts/_policy/side_effects_heuristics.yaml`, `python_layout.policy.yaml` | SQLAlchemy/Alembic patterns, `Hb Track - Backend` paths | **ATUALIZAR** — manter os YAMLs mas corrigir paths e patterns para Django |

## 7. Decisão SAN-009 — Classificação formal (2026-04-10)

| Decisão | Lote | Qtd | Justificativa |
|---------|------|-----|---------------|
| **ARQUIVAR** | PowerShell Windows (.ps1) | 13 | Projeto roda em WSL/Linux; scripts PS1 inoperáveis |
| **ARQUIVAR** | DB checks diretos (psycopg2) | 6 | Django ORM + testes substituem |
| **ARQUIVAR** | DB diagnostics (Alembic) | 3 | Alembic não é mais sistema de migração |
| **ARQUIVAR** | DB fixes (pontuais) | 3 | Fixes já aplicados, não reutilizáveis |
| **ARQUIVAR** | DB reset (Alembic) | 1 | `manage.py flush` + `manage.py migrate` substituem |
| **ARQUIVAR** | Migrate backfills (psycopg2) | 2 | Backfills pontuais já aplicados |
| **ARQUIVAR** | Seeds (asyncpg) | 1 | `manage.py seed_demo` já existe como substituto |
| **ARQUIVAR** | Generate/schema (Alembic) | 2 | gen_migration_0041 é Alembic; gen_test_matrix aponta dir inexistente |
| **ARQUIVAR** | hbtrack_lint checkers | 5 | Pacote explicitamente `DEPRECATED` no `__init__.py`; substituído por `validate_contracts.py` |
| **ARQUIVAR** | check_models_requirements | 1 | Fallback `Hb Track - Backend/` sem consumidor em CI ou hb |
| **ARQUIVAR** | check_canonical_data | 1 | psycopg2 direto + path legado |
| **ATUALIZAR** | Policy YAMLs | 2 | Corrigir paths de `Hb Track - Backend/` para `src/` e patterns SQLAlchemy→Django |
| **Total** | | **40** | 38 arquivar, 2 atualizar |

**Nota:** nenhum script legado tem consumidor confirmado em CI (`.github/workflows/`), no `scripts/hb`, ou no fluxo CDD atual. A decisão de arquivar (não remover) preserva histórico sem poluir o workspace ativo.

## 8. Decisão SAN-010 — Sistema de migração ativo (2026-04-10)

**Sistema ativo:** Django Migrations (`python manage.py makemigrations` / `python manage.py migrate`)  
**Localização:** `src/<module>/migrations/` (71 arquivos em 17 módulos)  
**Executor em CI:** `deploy.yml` → `python manage.py migrate --noinput`  
**Documentação:** ADR-028 (atualizado em SAN-007) + ADR-031

**Árvore legada:** `migrations/` na raiz (21 arquivos — Alembic `env.py`, `alembic.ini`, `script.py.mako`, 17 dirs de módulos com `versions/`)  
**Status:** nenhum consumidor em CI, `scripts/hb`, ou código ativo  
**Decisão:** ARQUIVAR — mover para `_archive/migrations_alembic/` quando conveniente  
**Não remover antes:** confirmar que nenhum script em SAN-009 depende dela (confirmado: todos os consumidores são eles próprios legados)

---

## 10. Política de retenção SAN-014 — `_reports/` (2026-04-10)

### Consumidores ativos confirmados (CAMADA 1 — state canônico corrente)

| Path | Consumidor | Evidência |
|------|-----------|-----------|
| `_reports/contract_gates/latest.json` | `scripts/hb` (linha 93), `validate_contracts.py` (linha 9939), `merge-readiness.json` (linha 128) | leitura + escrita obrigatória na pipeline |
| `_reports/contract_gates/*.latest.json` | `validate_contracts.py` (scoped runs por profile/stage) | gerado em cada execução parcial |
| `_reports/preflight/latest.json` | `validate_contracts.py` (linha 1232), `merge-readiness.json` (linha 115) | gate de readiness |
| `_reports/session_start.json` | `scripts/hb` (linha 44), `validate_contracts.py` (linha 44/92) | state de sessão corrente |
| `_reports/adversarial/` | `validate_contracts.py` — ADVERSARIAL_GATE (linhas 169-223) | evidência por módulo |
| `_reports/agent_execution/*.json` | `validate_contracts.py` — PRE_CONTRACT_EVIDENCE_GATE (linhas 4656, 7523) | evidência de registro de artefato |
| `_reports/compliance/agent_operability_latest.json` | pre-push / SESSION_HANDOFF | operabilidade do agente |
| `_reports/evidence/boot_resolution_report.json` | `validate_contracts.py` (linha 8636) | legado confirmado |
| `_reports/legacy/` | `scripts/hb` (linha 45) — migração de sessões obsoletas | estado de sessão histórica |

### Histórico CI-gerado (CAMADA 2 — histórico congelado, manter existentes)

| Path | Origem | Decisão |
|------|--------|---------|
| `_reports/DOMAIN_COMPLETENESS_*.json/md` | workflow `domain-completeness-audit.yml` | manter existentes como registro; novos commits do workflow continuam sem restrição |

### Sem consumidor ativo (CAMADA 3 — ignorar novos, untracking adiado)

| Path | Volume | Decisão |
|------|--------|---------|
| `_reports/enforcement/` (8 arquivos) | Snapshots de branch protection rules | `_reports/enforcement/` adicionado ao `.gitignore` |
| `_reports/parity/` (2 arquivos) | Relatórios de paridade obsoletos | `_reports/parity/` adicionado ao `.gitignore` |
| `_reports/runs/` (6039 dirs, 10142 arquivos) | Histórico append-only de cada execução | já no `.gitignore`; 6039 dirs commitados = untracking opcional via `git rm --cached -r _reports/runs/` |
| `_reports/dispatch/` | Sinais efêmeros de dispatch | já no `.gitignore` ✅ |
| 118 arquivos raiz (`AUDIT_*`, `BACKLOG_2C_*`, `C4_*`, etc.) | Histórico de sessões de agente (março 2026) | congelados — sem novos arquivos similares; `git rm --cached _reports/*.md _reports/*.txt` quando conveniente |

### Ação executada (2026-04-10)
- `.gitignore` atualizado: adicionados `_reports/enforcement/` e `_reports/parity/`; comentário de política adicionado à seção `_reports/`
- Nenhum arquivo deletado ou movido do disco

### Critério de done ✅
- Arquivos sem consumidor confirmado não entram em novos commits ✅ (`.gitignore` atualizado)
- Archivos canônicos correntes documentados explicitamente ✅
- Caminho de limpeza futura documentado (`git rm --cached`) ✅

---

## 9. Auditoria SAN-012 — Módulo `training` (2026-04-10)

### Inventário de stubs

| Camada | Arquivo | Total funções/classes | Stubs | % Stub |
|--------|---------|----------------------|-------|--------|
| API handlers | `src/training/api.py` | ~58 funções | 28 | ~48% |
| Use Cases | `src/training/application/use_cases.py` | 65 classes | 35 | 54% |
| **Total não-gerado** | | | **63** | **~42%** |
| Scaffolding gerado | `src/training/generated/api.py` | — | 40 | — (gerado, não trabalho manual) |

> Critério SAN-011: >30% = `draft_contract`. Decisão: manter como `implementation_ready` (core implementado — domain, migrations, 24 arquivos de teste, 30+ use cases live) e abrir burn-down formal até atingir ≤15%.

### Burn-down formal — 13 grupos funcionais

**Regra:** cada grupo = 1 tarefa atômica. Cada tarefa fecha quando use cases + endpoint estiverem implementados e cobertos por teste.

#### Onda A — Core CRUD (desbloqueio de operações básicas)

| Grupo | Use Cases | Endpoints | Stubs |
|-------|-----------|-----------|-------|
| A1. Training Session update/delete | `UpdateTrainingSessionUseCase`, `DeleteTrainingSessionUseCase` | `update_training_session`, `delete_training_session` | 4 |
| A2. Session Blocks get/reorder | `GetSessionBlockUseCase`, `ReorderSessionBlocksUseCase` | `reorder_session_blocks` | 3 |

**Subtotal onda A: 7 stubs**

#### Onda B — Tracking core (presença + wellness)

| Grupo | Use Cases | Endpoints | Stubs |
|-------|-----------|-----------|-------|
| B1. Attendance | `ListSessionAttendanceUseCase`, `RecordSessionAttendanceUseCase` | `list_session_attendance`, `record_session_attendance` | 4 |
| B2. Wellness GET/UPDATE | `GetWellnessPreUseCase`, `UpdateWellnessPreUseCase`, `GetWellnessPostUseCase`, `UpdateWellnessPostUseCase` | `get_wellness_pre`, `update_wellness_pre`, `get_wellness_post`, `update_wellness_post` | 8 |

**Subtotal onda B: 12 stubs**
**Status:** ✅ concluída em 2026-04-10.

#### Onda C — Planejamento (mesociclo/microciclo/execução)

| Grupo | Use Cases | Endpoints | Stubs |
|-------|-----------|-----------|-------|
| C1. Mesocycle list/get/update | `ListMesocyclesUseCase`, `GetMesocycleUseCase`, `UpdateMesocycleUseCase` | `update_mesocycle` | 4 |
| C2. Microcycle list/get/update | `ListMicrocyclesUseCase`, `GetMicrocycleUseCase`, `UpdateMicrocycleUseCase` | `update_microcycle` | 4 |
| C3. Execution records list/get | `ListExecutionRecordsUseCase`, `GetExecutionRecordUseCase` | `get_execution_record` | 3 |
| C4. Session Objectives list | `ListSessionObjectivesUseCase` | — | 1 |

**Subtotal onda C: 12 stubs**
**Status:** ✅ concluída em 2026-04-10.

#### Onda D — Features avançadas

| Grupo | Use Cases | Endpoints | Stubs |
|-------|-----------|-----------|-------|
| D1. Feedback Threads | `ListFeedbackThreadsUseCase`, `CreateFeedbackThreadUseCase`, `CloseFeedbackThreadUseCase` | `list_feedback_threads`, `create_feedback_thread`, `close_feedback_thread` | 6 |
| D2. Attention Queue | `ListAttentionQueueItemsUseCase`, `ResolveAttentionQueueItemUseCase`, `DismissAttentionQueueItemUseCase`, `EscalateAttentionQueueItemUseCase` | `list_attention_queue_items`, `resolve_attention_queue_item`, `dismiss_attention_queue_item`, `escalate_attention_queue_item` | 8 |
| D3. Recommendations | `ListRecommendationsUseCase`, `AcceptRecommendationUseCase`, `DismissRecommendationUseCase` | `list_recommendations`, `accept_recommendation`, `dismiss_recommendation` | 6 |
| D4. Ineligibility | `GetIneligibilityStatusUseCase`, `SubmitIneligibilityDeclarationUseCase` | `get_ineligibility_status`, `submit_ineligibility_declaration` | 4 |

**Subtotal onda D: 24 stubs**

#### Onda E — Analytics e comunicação

| Grupo | Use Cases | Endpoints | Stubs |
|-------|-----------|-----------|-------|
| E1. Load Chart | `GetLoadChartUseCase` | `get_load_chart` | 2 |
| E2. Chat/Sugestões | `ListChatMessagesUseCase`, `SubmitTrainingSuggestionUseCase` | `list_chat_messages`, `submit_training_suggestion` | 4 |

**Subtotal onda E: 6 stubs**

### Resumo do burn-down

| Onda | Grupos | Stubs | Acumulado após onda | Stub ratio após |
|------|--------|-------|---------------------|----------------|
| A — Core CRUD | 2 | 7 | 56 | ~35% |
| B — Tracking | 2 | 12 | 44 | ~27% ← cruza limiar `implementation_ready` |
| C — Planejamento | 4 | 12 | 32 | ~20% |
| D — Avançadas | 4 | 24 | 8 | ~5% ← cruza limiar `implemented` |
| E — Analytics | 2 | 6 | 2 | ~1% |
| **Total** | **14** | **61** | — | — |

> Nota: 2 stubs residuais (`get_microcycle` em api.py já funcional parcialmente + 1 endpoint em generated) podem ser fechados durante onda D ou descartados se o endpoint gerado substituir.

### Critério de done do burn-down completo

- stub ratio ≤ 15% em `src/training/application/use_cases.py` + `src/training/api.py`
- `MODULE_REGISTRY.yaml` → `training.status: implemented`
- todos os grupos A–D cobertos por ao menos 1 teste de integração

---

## 11. Decisão SAN-015 — `_archive/**` (2026-04-10)

### Diagnóstico

| Critério | Resultado |
|----------|-----------|
| Consumidores em `scripts/hb` | **zero** |
| Consumidores em `validate_contracts.py` | **excluído do scan** (linha 4710 — `_ROOT_SOVEREIGN_PREFIXES`) |
| Consumidores em `.github/workflows/` | **zero** |
| Consumidores em `.contract_driven/` | **zero** |
| Arquivos rastreados em git | 88 (histórico de sessões, transição, análises) |
| Conteúdo | SESSION_HANDOFFs históricos, ADRs de transição, análises de treinamento, dev_transition_2026_03_18, training_noncanonical_20260319 |

### Classificação

| Subdiretório | Conteúdo | Decisão |
|---|---|---|
| `_archive/*.md` (raiz) | SESSION_HANDOFFs históricos, análises, handoffs pré-CDD | **MANTER** — histórico de decisão legítimo |
| `_archive/boot_resolution_report.json` | Cópia antiga do boot report (ativo está em `_reports/evidence/`) | **MANTER** — snapshot histórico; não confundir com o ativo |
| `_archive/dev_transition_2026_03_18/` | Documentação de transição FastAPI→Django (decisões, arquitetura, checklists, planejamentos) | **MANTER** — contexto de decisão de migração de stack |
| `_archive/training_noncanonical_20260319/` | Docs de treinamento não-canônicos (v1.1.0) — explicitamente marcados como noncanonical | **MANTER** — histórico de iteração pré-CDD |
| `_archive/.agents.md` | Linha única com hash de commit (`dce9117e fix: renomear...`) — conteúdo acidental | **REMOVIDO** (2026-04-10) |

### Conclusão

`_archive/` já satisfaz o critério de done: **não compete com o fluxo principal**.
- Excluída de scans soberanos por design (`_ROOT_SOVEREIGN_PREFIXES` em `validate_contracts.py`)
- Zero consumidores ativos — é área de leitura humana, não pipeline
- Conteúdo bem-namespaciado (datas no nome, prefixo `_archive/`)
- Não requer `.gitignore` adicional — o histórico de decisão deve ser retido

### Ação executada
- `_archive/.agents.md` removido (conteúdo: 1 linha com hash de commit — arquivo acidental)
- Nenhum outro arquivo alterado ou movido

---

## 12. Decisão SAN-016 — `.CEPRAEA/**` (2026-04-10)

### Diagnóstico

| Critério | Resultado |
|----------|-----------|
| Consumidores em `scripts/hb` | **zero** |
| Consumidores em `validate_contracts.py` | **zero** (diretórios ocultos excluídos automaticamente do layout scan na linha 2963) |
| Consumidores em `.github/workflows/` | **zero** |
| Consumidores em `.contract_driven/` | **zero** |
| Consumidores em `merge-readiness.json` | **zero** |
| Arquivos rastreados em git | 29 |
| Já no `.gitignore` antes do SAN-016 | **não** |

### Inventário de conteúdo

| Arquivo / subdir | Natureza | Decisão |
|---|---|---|
| `ADVERSARIAL.md`, `AGENT.md`, `AGENT_COMPLIANCE_EXECUTION_PLAN.md` | Auditorias derivadas com disclaimer non-sovereign explícito | Histórico — MANTER existentes |
| `ANALISEARQUITETURA.md`, `DEVCONT.md`, `cdd.md`, `conformance_analysis.md` | Análises técnicas históricas | Histórico — MANTER existentes |
| `PARIDADE.md` a `PARIDADE4.md`, `PARIDADETOTAL.md`, `PARIDADE_CORRECT.md` | Análises de paridade de PRs históricos (pré-CDD estável) | Histórico — MANTER existentes |
| `compliance.md`, `compliance1.md`, `audit2.md` | Snapshots de compliance histórico | Histórico — MANTER existentes |
| `HISTORICO.md`, `design.md`, `plano1.md`, `plano de correcao.md`, `PIPELINEFINAL.md`, `RELATÓRIO.md` | Planejamento histórico pré-CDD | Histórico — MANTER existentes |
| `GEMINI.md` | Rascunho de guideline para agente Gemini | Histórico — MANTER existentes |
| `MANUAL_DE_CRIAÇÃO_DE_VIDEOS.md` | Manual de criação de vídeos (produto externo ao HB Track) | Histórico — MANTER existentes |
| `video_pipeline/` | Scripts Python offline para geração de vídeo (sem consumidor no projeto) | Histórico — MANTER existentes |

### Classificação final

**`.CEPRAEA/` = área de rascunho/pesquisa histórica** — similar ao papel do `_archive/`, mas com escopo mais amplo (planejamento de produto, análises ad-hoc, video pipeline offline).

Diferença de `_archive/`: `.CEPRAEA/` não é uma área de quarentena formal; é um diretório de trabalho histórico que cresceu organicamente. Como é prefixado com `.`, nunca interferiu em scans canônicos.

### Ação executada (2026-04-10)
- `.gitignore` atualizado: `.CEPRAEA/` adicionado com bloco de comentário explicativo
- Nenhum arquivo deletado ou movido do disco
- 29 arquivos rastreados permanecem (histórico legítimo); novos arquivos não entrarão em commits

### Critério de done ✅
- Material de baixa autoridade explicitamente reclassificado ✅
- Novos arquivos em `.CEPRAEA/` não entram em commits (`.gitignore`) ✅
