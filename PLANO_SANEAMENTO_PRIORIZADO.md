# PLANO_SANEAMENTO_PRIORIZADO
> ⚠️ **ARTEFATO DERIVADO — NON-SOVEREIGN**: Este arquivo é um plano operacional derivado do laudo forense. Não possui autoridade normativa. Em caso de conflito, prevalecem: `scripts/hb` + `scripts/contracts/validate/validate_contracts.py` > `contracts/schemas/` > `docs/_canon/` > este arquivo.

Data: 2026-04-09 (atualizado: 2026-04-10)  
Base exclusiva: `AUDIT_COMPLETA.md` + evidências executadas e confirmadas durante a auditoria.  
Objetivo: transformar os achados forenses em um plano de saneamento executável, priorizado por risco e esforço, sem introduzir hipóteses não comprovadas como fato.

**Progresso geral:** ✅ **SANEAMENTO COMPLETO (2026-04-10) — 23/23 concluídos. Sprints 1–7 finalizadas.** Ondas 0 ✅ + 1 ✅ + 2 ✅ + 3 ✅. P0-01→P3-03 todos DONE. `training.status: implemented`. 229 unit tests passing.

## 1. Regra de priorização

### Escala de risco
- `crítico`: bloqueia governança, pode mascarar estado real, expõe segredo/configuração sensível ou pode causar dano operacional relevante.
- `alto`: pode induzir operação errada, degradar confiabilidade do fluxo principal ou manter fonte de verdade falsa.
- `médio`: gera ruído, manutenção cara, drift documental ou ambiguidade operacional, mas não bloqueia o fluxo central de imediato.
- `baixo`: higiene, ruído local ou artefato descartável.

### Escala de esforço
- `P`: pequeno, normalmente ajuste localizado em 1 dia ou menos.
- `M`: médio, exige mapeamento e mudanças coordenadas em múltiplos arquivos.
- `G`: grande, exige corte de legado, revisão ampla ou decisão arquitetural/processual.

### Regra de execução
- `P0`: executar antes de retomar evolução normal do sistema.
- `P1`: executar logo após P0; reduz risco estrutural real.
- `P2`: limpeza e consolidação relevantes, mas não bloqueantes.
- `P3`: investigar apenas após P0-P2 ou quando houver necessidade operacional real.

## 2. Resumo executivo

O saneamento deve começar por quatro pontos que hoje afetam diretamente a confiabilidade do processo:

1. recolocar a governança em estado coerente (`SESSION_HANDOFF.md` vs relatório canônico);
2. alinhar a estratégia local de `merge-readiness` com a realidade do repositório;
3. separar configuração ativa do backend/deploy do legado FastAPI/Alembic ainda presente em `.env` e scripts;
4. reduzir o risco de deploy destrutivo ou enganoso em staging.

Depois disso, o repositório precisa de um corte formal do legado e de uma consolidação documental, porque hoje há divergência objetiva entre o runtime verificável (Django + React + CI + Docker) e partes do canon/ROADMAP/scripts ainda presas ao stack anterior.

## 3. Matriz priorizada

| ID | Frente | Problema confirmado | Risco | Esforço | Prioridade | Evidência-base |
|---|---|---|---|---|---|---|
| P0-01 | ~~Estado governado~~ | ~~`validate_contracts.py --profile precommit` falha por incoerência~~ | ~~crítico~~ | ~~P~~ | ~~P0~~ | ✅ DONE 2026-04-09 — HANDOFF_COHERENCE_GATE PASS |
| P0-02 | ~~Merge-readiness local~~ | ~~`merge-readiness.json` aponta hook ausente~~ | ~~alto~~ | ~~P/M~~ | ~~P0~~ | ✅ DONE 2026-04-09 — `scripts/git-hooks/pre-push` criado |
| P0-03 | ~~Configuração ativa~~ | ~~`.env` mistura variáveis ativas e legado~~ | ~~crítico~~ | ~~M~~ | ~~P0~~ | ✅ DONE 2026-04-09/10 — `.env.example` criado + 3 bugs de config corrigidos |
| P0-04 | ~~Segurança operacional de deploy~~ | ~~`deploy.yml` reseta volumes e regenera `.env` destrutivamente~~ | ~~alto~~ | ~~M~~ | ~~P0~~ | ✅ DONE 2026-04-10 — `destructive_reset` flag + `.env` corruption warn-only |
| P1-01 | ~~Verdade documental~~ | ~~ROADMAP, .gitignore, ADRs corrigidos~~ | ~~alto~~ | ~~M~~ | ~~P1~~ | ✅ DONE 2026-04-10 — SAN-005/006/007 |
| P1-02 | ~~Corte formal do legado~~ | ~~scripts inventariados + classificados + migração formalizada~~ | ~~alto~~ | ~~G~~ | ~~P1~~ | ✅ DONE 2026-04-10 — SAN-008/009/010 |
| ~~P1-03~~ | ~~Verdade do status de módulos~~ | ~~`MODULE_REGISTRY.yaml` marca 17 módulos como `implemented`, mas código contém `NotImplementedError`~~ | ~~alto~~ | ~~G~~ | ~~P1~~ | ✅ DONE 2026-04-10 — SAN-011 critério; SAN-012 auditoria; SAN-013 burn-down completo (63→0 stubs); `training.status: implemented` |
| ~~P2-01~~ | ~~Retenção de relatórios~~ | ~~`_reports/` versiona grande volume histórico; consumo direto confirmado só para um subconjunto.~~ | ~~médio~~ | ~~M~~ | ~~P2~~ | ✅ DONE 2026-04-10 — SAN-014: política de retenção definida; `.gitignore` atualizado (`_reports/enforcement/`, `_reports/parity/`); §10 adicionado ao BACKLOG |
| ~~P2-02~~ | ~~Material de baixa autoridade~~ | ~~`_archive/**` e `.CEPRAEA/**` convivem com o fluxo atual e ampliam o ruído.~~ | ~~médio~~ | ~~M~~ | ~~P2~~ | ✅ DONE 2026-04-10 — SAN-015/016: `_archive/` = quarentena funcional confirmada; `.agents.md` acidental removido; `.CEPRAEA/` no `.gitignore` |
| ~~P2-03~~ | ~~Higiene local~~ | ~~`.agents.md` vazio, `VPS/**/*.Zone.Identifier`, wrapper fino `scripts/validate_contracts.py`.~~ | ~~baixo~~ | ~~P~~ | ~~P2~~ | ✅ DONE 2026-04-10 — SAN-017/018: `.agents.md` + 23 `Zone.Identifier` removidos; `*:Zone.Identifier` no `.gitignore`; wrapper mantido (SAN-018) |
| ~~P2-04~~ | ~~Drift de migrations~~ | ~~`manage.py migrate --noinput` passa, mas avisa que `analytics`, `audit` e `medical` têm mudanças de model ainda não refletidas em migrations.~~ | ~~médio~~ | ~~P/M~~ | ~~P2~~ | ✅ DONE 2026-04-10 — SAN-021: 3 migrations geradas (analytics/0003, audit/0004, medical/0003); `makemigrations --check` = No changes detected |
| ~~P3-01~~ | ~~Itens inconclusivos~~ | ~~uso real de `VPS/**`, Playwright E2E, `pact/`, parte dos scripts `ops/reset/fixes/remediate_*` não foi confirmado.~~ | ~~variável~~ | ~~M~~ | ~~P3~~ | ✅ DONE 2026-04-10 — SAN-019/020: `VPS/**` = referência offline (`.gitignore` OK); `pact/` = legado morto; playwright = infra não integrada ao CI; `remediate_*` = legado de trabalho |
| ~~P3-02~~ | ~~Dependências frontend~~ | ~~`npm audit` reporta 3 vulnerabilidades transitivas (1 moderate, 1 high, 1 critical) durante o `pre-push`, sem bloqueio atual.~~ | ~~baixo/médio~~ | ~~M~~ | ~~P3~~ | ✅ DONE 2026-04-10 — SAN-022: axios CRITICAL→corrigido (`^1.15.0`); vite HIGH→corrigido (`^8.0.5`); 3→2 vulns; 2 restantes aceitos (vitest transitivo = aguardar upstream; brace-expansion = risco baixo) |
| ~~P3-03~~ | ~~Débito de compatibilidade~~ | ~~`hb ci --profile pr` ainda emite warnings recorrentes de Pydantic, Django Ninja e `datetime.utcnow()`.~~ | ~~baixo~~ | ~~M~~ | ~~P3~~ | ✅ DONE 2026-04-10 — SAN-023: `datetime.utcnow()` → `datetime.now(UTC)` em `src/wellness/domain/entities.py`; 57→3 warnings; 3 remanescentes = terceiros ou upstream |

## 4. Plano por ondas

## Onda 0 — Restabelecer coerência operacional ✅ COMPLETA

### P0-01 — Reconciliar `SESSION_HANDOFF.md` com o estado canônico ✅ DONE (2026-04-09)

> **Resultado:** HANDOFF_COHERENCE_GATE PASS. Front matter corrigido, validator precommit exitcode 0.

### P0-02 — Alinhar `merge-readiness.json` com a estratégia real de hook local ✅ DONE (2026-04-09)

> **Resultado:** Saída A escolhida — `scripts/git-hooks/pre-push` criado.  
> **Hardening adicional (2026-04-10):** `scripts/hb` passou a restaurar `_reports/session_start.json` e `_reports/contract_gates/latest.json` após `cmd_survival_suite` e `cmd_ci`, eliminando a contaminação tardia dos artefatos canônicos. `pre-push` final: PASS.

### P0-03 — Separar configuração ativa do legado em `.env` ✅ DONE (2026-04-09/10)

> **Resultado:** `.env.example` criado como contrato mínimo (15 vars ativas, 25+ legado/futuro documentadas).  
> **Bugs corrigidos em `.env` (2026-04-10):**  
> - `SECRET_KEY` adicionado (Django usava chave insegura hardcoded)  
> - `CORS_ALLOWED_ORIGINS` adicionado (`.env` usava nome errado `CORS_ORIGINS`)  
> - `JWT_ACCESS_TOKEN_EXPIRY_MINUTES` adicionado (`.env` usava nome errado `JWT_EXPIRES_MINUTES`)

### P0-04 — Tornar o deploy de staging não-destrutivo por padrão ✅ DONE (2026-04-10)

> **Resultado:** 3 mudanças em `deploy.yml`:
> 1. `docker volume rm` condicionado a input `destructive_reset=true` (default: false)  
> 2. `.env` corruption: avisa e mostra linhas inválidas em vez de sobrescrever com credenciais novas  
> 3. Input `destructive_reset` adicionado ao `workflow_dispatch` com descrição explícita de perda de dados  
> Deploy por `push` a main e `workflow_dispatch` padrão agora preservam dados.

## Onda 1 — Consolidar verdade documental e cortar o legado ativo

### P1-01 — Consolidar a verdade documental do stack atual ✅ DONE (2026-04-10)

> **Resultado (SAN-005/006/007):**
> - `ROADMAP.md` snapshot atualizado: 8 itens ❌→✅, tabela de progresso por fase adicionada
> - `.gitignore` reescrito: duplicatas removidas, “contracts-only repo” removido, seções organizadas
> - ADRs: ADR-026 já superseded; ADR-028 versão Alembic duplicada removida; ADR-029 FastAPI→Django; ADR-007/008/013 notas de framework adicionadas

### P1-02 — Fazer o corte formal entre o stack Django atual e o legado FastAPI/Alembic ✅ DONE (2026-04-10)

> **Resultado (SAN-008/009/010):**
> - **SAN-008:** 40 scripts legados inventariados (13 .ps1, 25 .py, 2 .yaml)
> - **SAN-009:** Classificação formal: 38 ARQUIVAR, 2 ATUALIZAR (policy YAMLs corrigidos)
> - **SAN-010:** Sistema de migração formalizado: Django Migrations em `src/*/migrations/` (71 arquivos); árvore Alembic raiz (21 arquivos) classificada como legado para arquivar
> - Nenhum script legado tem consumidor em CI ou `scripts/hb`

### P1-03 — Reconciliar `MODULE_REGISTRY.yaml` com a realidade de implementação ✅ DONE (2026-04-10)

**Objetivo**  
Remover a divergência entre status canônico e evidência de código/stubs.

**Ações**
- ~~definir um critério verificável para `implemented`;~~ ✅ DONE — SAN-011: critério C1+C2+C3 definido; 13 PASS, 3 BORDERLINE, 1 FAIL (`training` 42% stub ratio)
- ~~auditar módulo por módulo, começando pelos mais discrepantes;~~ ✅ DONE — SAN-012: 63 stubs em 13 grupos; burn-down formal aberto
- ~~executar burn-down por ondas A→E até stub ratio ≤15%~~ ✅ DONE — SAN-013: Ondas A+B+C+D+E concluídas; 63 stubs → 0; stub ratio ~0%

**Evidência executada (SAN-013)**
- `pytest -q src/training/tests/unit` = `229 passed, 19 skipped` ✅
- `grep -c "raise NotImplementedError" src/training/application/use_cases.py` = 1 (apenas comentário) ✅
- `docs/_canon/MODULE_REGISTRY.yaml` → `training.status: implemented` ✅
- Ondas implementadas: A (core CRUD), B (tracking), C (planejamento), D (features avançadas), E (analytics/comunicação)

**Critério de done** ✅ atingido
- `MODULE_REGISTRY.yaml` deixa de superestimar maturidade ✅
- código fechou a lacuna validada por evidência ✅
- `training` classificado como `implemented` por evidência defensável ✅

**Dependências**
- P1-02 ✅

## Onda 2 — Reduzir ruído e custo de manutenção

### P2-01 — Criar política de retenção para `_reports/` ✅ DONE (2026-04-10)

> **Resultado (SAN-014):**
> - Política de retenção definida em 3 camadas (canônicos correntes / histórico útil / descartável)
> - `.gitignore` atualizado: `_reports/enforcement/` e `_reports/parity/` excluídos
> - §10 adicionado ao BACKLOG com decisão formal
> - Consumidores ativos confirmados: `latest.json`, `contract_gates/latest.json`, `session_start.json`

### P2-02 — Reclassificar `_archive/**` e `.CEPRAEA/**` ✅ DONE (2026-04-10)

> **Resultado (SAN-015/016):**
> - `_archive/` confirmado como quarentena funcional: contém handoffs históricos e context compilado — não compete com o canon atual
> - `.agents.md` acidental encontrado e removido de `_archive/`
> - `.CEPRAEA/` auditado: zero consumidores em scripts, CI ou `scripts/hb`; adicionado ao `.gitignore`
> - Marcação de baixa autoridade já presente nos documentos via header NON-SOVEREIGN

### P2-03 — Higiene rápida de workspace e wrappers periféricos ✅ DONE (2026-04-10)

> **Resultado (SAN-017/018):**
> - `.agents.md` vazio (raiz) removido
> - 23 arquivos `*.Zone.Identifier` removidos de `VPS/**`; `*:Zone.Identifier` adicionado ao `.gitignore`
> - `scripts/validate_contracts.py` auditado: zero callers em CI ou `scripts/hb`; DECISÃO = MANTER como wrapper de conveniência (custo zero, facilita onboarding)

### P2-04 — Resolver drift de migrations não bloqueante ✅ DONE (2026-04-10)

> **Resultado (SAN-021):**
> - `makemigrations analytics` → `0003_remove_analyticssnapshotmodel_analytics_snapshot_metric_key_nonempty.py`
> - `makemigrations audit` → `0004_remove_auditentrymodel_audit_entry_action_nonempty.py`
> - `makemigrations medical` → `0003_remove_medicalrecordmodel_medical_record_label_nonempty.py`
> - `manage.py makemigrations --check` = `No changes detected` ✅

## Onda 3 — Investigar só o que ainda está inconclusivo

### P3-01 — Fechar lacunas de evidência antes de novas limpezas agressivas ✅ DONE (2026-04-10)

> **Resultado (SAN-019/020):**
> - `VPS/**`: referência operacional offline (zero arquivos rastreados, `.gitignore` já correto) — MANTER
> - `pact/` (323 arquivos): legado morto — zero callers em CI; decisão = candidato a arquivamento formal numa próxima sessão
> - Playwright E2E (`frontend/e2e/`): infra presente mas não integrada ao CI — candidato a integração futura
> - `scripts/ops/reset/fixes/remediate_*`: legado de trabalho sem caller confirmado — candidato a arquivamento

### P3-02 — Triar vulnerabilidades transitivas do frontend ✅ DONE (2026-04-10)

> **Resultado (SAN-022):**
> - axios `^1.13.6` → `^1.15.0` (CRITICAL ReDoS corrigido)
> - vite `^8.0.2` → `^8.0.5` (HIGH XSS corrigido)
> - `npm install --legacy-peer-deps` aplicado; 3 → 2 vulns
> - vitest transitivo HIGH: aguardar upstream (não explorado no bundle de produção)
> - brace-expansion MODERATE: risco operacional baixo; aceito temporariamente

### P3-03 — Reduzir warnings de deprecação ✅ DONE (2026-04-10)

> **Resultado (SAN-023):**
> - `datetime.utcnow()` → `datetime.now(UTC)` em `src/wellness/domain/entities.py` (linhas 48-49)
> - `from datetime import UTC, date, datetime` atualizado
> - 57 → 3 warnings; redução material confirmada via `pytest src/wellness/tests/unit/`
> - 3 remanescentes: warnings de terceiros (Django Ninja / Pydantic) — classificados como backlog upstream

## 5. Ordem recomendada de execução

### Bloco A — 1 a 2 dias ✅ DONE
- ~~P0-01~~ ✅
- ~~P0-02~~ ✅

### Bloco B — 2 a 4 dias ✅ DONE
- ~~P0-03~~ ✅
- ~~P0-04~~ ✅
- ~~início de P1-01~~ ✅

### Bloco C — 1 semana ✅ DONE
- ~~P1-01~~ ✅
- ~~P1-02~~ ✅

### Bloco D — 1 semana ou mais ✅ DONE
- ~~P1-03~~ ✅ (SAN-011 ✅; SAN-012 ✅; SAN-013 Ondas A+B+C+D+E ✅ — 63→0 stubs; `training.status: implemented`)

### Bloco E — 2 a 5 dias ✅ DONE
- ~~P2-01~~ ✅ (SAN-014)
- ~~P2-02~~ ✅ (SAN-015/016)
- ~~P2-03~~ ✅ (SAN-017/018)
- ~~P2-04~~ ✅ (SAN-021)

### Bloco F — sob demanda ✅ DONE
- ~~P3-01~~ ✅ (SAN-019/020)
- ~~P3-02~~ ✅ (SAN-022)
- ~~P3-03~~ ✅ (SAN-023)

## 6. Dependências críticas

- ~~P0 inteiro deve ser tratado antes de qualquer expansão séria de funcionalidade~~ — concluído.
- P1-02 depende materialmente de P0-03 ✅ (concluído) — desbloqueado.
- P1-03 depende de uma decisão de governança: ou o registry desce para refletir o código, ou o código sobe para sustentar o registry.
- P2-01 não deve começar antes de ficar claro quais relatórios continuam sendo exigidos por gates e estado operacional.

## 7. Itens que não devem ser deletados antes da hora

- `.env`: não remover sem mapeamento de consumo e substituto seguro.
- `migrations/**`: não remover antes de classificar consumidores legados remanescentes.
- `scripts/ops/**`, `scripts/reset/**`, `scripts/checks/**`: não limpar em lote sem separar o que ainda tem caller real.
- `_reports/**`: não apagar indiscriminadamente antes de fechar a política de retenção.

## 8. Critério de sucesso do saneamento

O saneamento deve ser considerado bem-sucedido quando, ao mesmo tempo:

- o fluxo governado local estiver verde;
- a documentação central não contradisser mais o runtime atual;
- não existir mais ambiguidade operacional entre Django atual e FastAPI/Alembic legado;
- as configurações ativas estiverem explicitadas e separadas do legado;
- o repositório tiver menos ruído histórico e menos fonte falsa de verdade.
