# AI Agent Documentation Index (Router Central)

> **Natureza deste documento**: Mapa de navegação e roteamento para agents (humanos ou IA) no monorepo HB Track.
> **NÃO é fonte canônica**: em caso de conflito com docs canônicos (`docs\_canon\03_WORKFLOWS.md`, `05_MODELS_PIPELINE.md`, `08_APPROVED_COMMANDS.md`), **o canon vence sempre**.
> 
> **Paths Canônicos:**
> - **Repo root**: `C:\HB TRACK\` (Windows) | `<repo>` (portável)
> - **Backend root**: `C:\HB TRACK\Hb Track - Backend\` (Windows) | `<repo>/Hb Track - Backend` (portável)
> - Paths indicados como `docs\...` são relativos ao repo root
> - Paths indicados como `Hb Track - Backend\...` são relativos ao repo root
> 
> **Regra de Ouro**: qualquer resposta técnica deve citar:
> - (a) um documento canônico obrigatório por tipo de tarefa (ver "Quick Start Routing"), OU
> - (a-alt) para conceito único minor (ex: significado de exit code 4), citar só `exit_codes.md` + evidência
> - (b) uma evidência (código, `schema.sql`, `openapi.json`, `parity_report.json`, ADR, ou git diff)
> 
> **Exemplos de evidência mínima:**
> - Model↔schema: trecho de `schema.sql` (DDL + constraints) + item de `parity_report.json` + `git diff app/models/<table>.py`
> - Requirements violation: trecho do log/CSV + referência a `model_requirements_guide.md` + exit code 4

---

## Glossário de Termos Técnicos

| Termo | Definição | Onde Ver Mais |
|-------|-----------|---------------|
| **SSOT** | Single Source of Truth — artefatos gerados (schema.sql, openapi.json) que definem estado autoritativo | `01_AUTHORITY_SSOT.md` |
| **Parity** | Conformidade estrutural entre model (SQLAlchemy) e schema (PostgreSQL DDL) | `05_MODELS_PIPELINE.md` |
| **Requirements** | Validação de regras de negócio/constraints em models (vs schema.sql) | `model_requirements_guide.md` |
| **Guard** | Proteção contra modificação não autorizada de arquivos críticos (ML/API/tests) | `INVARIANTS_AGENT_GUARDRAILS.md` |
| **Baseline** | Snapshot de estado conformante (usado por guard para detectar diffs) | `08_APPROVED_COMMANDS.md` |
| **Manifest** | Rastreabilidade de geração (git commit, checksums, timestamps) | `04_SOURCES_GENERATED.md` |
| **Gate** | Comando atomicamente composto (ex: parity → requirements → guard) | `05_MODELS_PIPELINE.md` |
| **Canon** | Documentação autoritativa (precedência sobre este Index) | `docs\_canon\` |
| **Exit Code** | Código de retorno de comando (0=pass, 2=parity, 3=guard, 4=requirements, 1=crash) | `exit_codes.md` |

---

## Quick Start Routing (Caminho Feliz — 5 Passos)

**Antes de QUALQUER tarefa operacional:**

1. **SSOT Fresh** (executar na raiz `C:\HB TRACK`):
   ```powershell
   .\scripts\inv.ps1 refresh
   ```
   Regenera: `schema.sql`, `openapi.json`, `alembic_state.txt`, `manifest.json`
   
   **Regra para `-SkipDocsRegeneration`**: só usar quando:
   - `docs\_generated\manifest.json` acabou de ser regenerado nesta mesma execução (timestamp < 5min), OU
   - você está no POST-parity do mesmo gate que já rodou PRE-parity com refresh
   - **Se tiver dúvida → não use; sempre prefira refresh completo**

2. **Diagnosis** (executar no backend root `C:\HB TRACK\Hb Track - Backend`):
   ```powershell
   .\scripts\parity_scan.ps1 -TableFilter <TABLE>
   ```
   Gera: `docs\_generated\parity_report.json`

3. **Entender Gap**: consultar `docs\_canon\05_MODELS_PIPELINE.md` (autoridade do pipeline model↔schema)

4. **Checar Guardrails**: se exit code ≠ 0 → `docs\_canon\09_TROUBLESHOOTING_GUARD_PARITY.md`

5. **Editar + Gate** (executar no backend root):
   - Editar `app\models\<table>.py`
   - Rodar gate (cobre: PRE parity + autogen + POST parity + requirements):
     ```powershell
     .\scripts\models_autogen_gate.ps1 -Table <TABLE> -Profile strict
     ```
   - Se aprovado (EXIT 0): snapshot baseline (só quando autorizado explicitamente)

**Triagem rápida (opcional)**: antes do gate, rode `model_requirements.py` para diagnóstico read-only (exit 0/4).

---

**Documentos obrigatórios por tipo de tarefa:**

| Tipo de Tarefa | Docs Obrigatórios | Artefato Obrigatório | Quando Consultar |
|---|---|---|---|
| Diagnosticar parity/requirements | `05_MODELS_PIPELINE.md` + `09_TROUBLESHOOTING_GUARD_PARITY.md` | `parity_report.json`, `schema.sql` | Sempre que exit code ≠ 0 |
| Corrigir model | `05_MODELS_PIPELINE.md` + `08_APPROVED_COMMANDS.md` | gate log + baseline snapshot | Antes de editar models |
| Adicionar invariante | `06_AGENT-PROMPTS.md` + `INV_TASK_TEMPLATE.md` + `INVARIANTS_AGENT_PROTOCOL.md` | invariant.md + testes + UAT | Antes de instalar nova invariante |
| Entender arquitetura | `SYSTEM_DESIGN.md` + `01_AUTHORITY_SSOT.md` | openapi.json, schema.sql, code review | Antes de escrever código |

---

## Guardrail: Current Working Directory (CWD)

**Regra objetiva por tipo de comando:**

| Comando | CWD Esperado | Como Validar |
|---------|-------------|--------------|
| `.\scripts\inv.ps1 *` | Repo root (`C:\HB TRACK`) | `Get-Location` deve retornar `C:\HB TRACK` |
| `.\scripts\parity_scan.ps1` | Backend root (`C:\HB TRACK\Hb Track - Backend`) | `Get-Location` deve retornar `...\Hb Track - Backend` |
| `.\scripts\models_autogen_gate.ps1` | Backend root | Idem acima |
| `venv\Scripts\python.exe scripts\model_requirements.py` | Backend root | Idem acima |

**Checklist antes de rodar qualquer comando:**
1. `Get-Location` → validar CWD correto
2. `git status --porcelain` → validar repo limpo (se aplicável)
3. Executar comando
4. Capturar `$LASTEXITCODE` imediatamente

---

## Contrato de Exit Codes

**Semântica operacional (fonte autoritativa: `docs\references\exit_codes.md`):**

| Exit Code | Significado | Ação Obrigatória | Proibido |
|-----------|-------------|------------------|----------|
| **0** | PASS (conformidade total) | Prosseguir para próximo passo | Ignorar warnings no log |
| **2** | Parity diffs (estrutura difere de schema.sql) | Consultar `09_TROUBLESHOOTING_GUARD_PARITY.md` + `parity_report.json` | Snapshot baseline; commitar |
| **3** | Guard violation (arquivo protegido modificado) | Verificar baseline stale OU arquivo fora de allowlist | Ignorar; forçar commit |
| **4** | Requirements violation (model viola regras) | Consultar `model_requirements_guide.md` + corrigir model | Snapshot baseline; bypassar |
| **1** | Internal crash (erro de execução) | Reportar: comando + output + CWD + git status | Retry sem diagnóstico |

**Regra de propagação**: sempre propagar código específico (não flatten para 1); usar pattern:
```powershell
& $comando @args
$ec = $LASTEXITCODE
if ($ec -ne 0) { exit $ec }  # NÃO flatten
```

**Nota**: esta tabela é resumo. Para detalhes completos: `docs\references\exit_codes.md` (fonte canônica).

---

## Regras de Snapshot Baseline

**Comando canônico** (só rodar após gates OK):
```powershell
# Primário (Python direto)
.\venv\Scripts\python.exe scripts\agent_guard.py snapshot baseline

# Alternativo (wrapper PowerShell, se disponível)
.\scripts\agent_guard.ps1 snapshot baseline
```

**Quando é OBRIGATÓRIO:**
- Após `models_autogen_gate.ps1` com EXIT 0 + repo limpo (nenhum arquivo staged)
- Após commit que altera arquivos protegidos/SSOT monitorados por guard
- Quando autorizado explicitamente pelo usuário

**Quando é PROIBIDO:**
- Se EXIT 2/3/4 (primeiro corrigir causa raiz)
- Se `git status --porcelain` retorna algo (repo sujo)
- Se parity ainda falha (structural diffs não resolvidos)
- Se requirements ainda falha (model viola regras)

**Regra de ouro**: snapshot = "registrar estado conformante e testado"; nunca snapshot de repo quebrado.

---

## Do and Don't (Verificável)

| O que fazer (Do) | O que evitar (Don't) |
|------------------|---------------------|
| Citar docs obrigatórios do tipo de tarefa (Quick Start Routing acima) | Ignorar documentos canônicos ou inventar referências |
| Para conceitos minor (ex: exit code 4): citar só `exit_codes.md` + evidência | Citar 5 docs para resposta de 2 linhas |
| Usar artefatos gerados como evidência (parity_report.json, schema.sql, openapi.json) | Fornecer respostas sem validar contra SSOT |
| Rodar SSOT refresh **antes** de parity/gate (salvo `-SkipDocsRegeneration` conforme regra) | Rodar gates com schema.sql desatualizado |
| Não editar artefatos gerados manualmente | Editar schema.sql ou parity_report.json à mão |
| Seguir pipeline: SSOT refresh → parity → requirements → gate → snapshot (em ordem) | Pular etapas ou rodar em ordem errada |
| Citar exit code + output + git status como evidência | Reportar "falhou" sem contexto diagnóstico |
| Commitar ou fazer snapshot baseline após gates OK | Deixar repo "sujo" ou artefatos gerados uncommitted |
| Consultar `.github\instructions\*.instructions.md` para context de tarefa | Ignorar diretivas de shell/quoting/safety |
| Validar CWD antes de rodar comando (ver tabela "Guardrail: CWD") | Rodar de diretórios arbitrários; assumir CWD |
| Usar PowerShell 5.1 call operator `&` com array de args (não Invoke-Expression) | Usar bash pipes, sed, grep, heredoc, ou iex |
| Validar venv antes de python/pip no EXEC_TASK | Assumir venv existe ou usar python global |
| Propagar exit codes específicos (0/2/3/4) | Flatten todos erros para 1 (perde diagnóstico) |
| Se SSOT mudou (schema.sql/openapi.json) → considerar snapshot baseline (após gates OK) | Ignorar que novos artefatos podem afetar guard |
| Consultar "Exit Codes" sempre que ec ≠ 0 | Interpretar exit codes de forma criativa |
| Consultar "Approved Commands" antes de rodar comando não listado | Inventar comandos sem validação |
| Um comando por interação (exceto gates atomicamente compostos) | Múltiplos comandos sem fail-fast |

* Antes de escrever código, **analisar** `docs\_ai\SYSTEM_DESIGN.md` para entender arquitetura, stack, padrões e convenções.
* Respostas técnicas: sempre citar doc + evidência, nunca suposições.
* **Comandos listados neste Index são subconjunto de `08_APPROVED_COMMANDS.md`**. Se houver divergência, `08_APPROVED_COMMANDS.md` vence.

---

## Hierarquia de Autoridade (Quando Doc Manda)

**Regra de decisão por contexto:**

| Contexto | Doc que Manda | Quando Consultar |
|----------|---------------|------------------|
| Models, parity, guard, requirements | `05_MODELS_PIPELINE.md` | Trabalho em `app/models/` ou gates |
| Invariantes, protocolos, SSOT refresh | `03_WORKFLOWS.md` | Trabalho em `INVARIANTS/` ou instalar nova |
| Precedência, SSOT, autoridade | `01_AUTHORITY_SSOT.md` | Dúvida sobre fonte de verdade |
| Exit codes, diagnóstico | `09_TROUBLESHOOTING_GUARD_PARITY.md` + `exit_codes.md` | Qualquer comando com ec ≠ 0 |
| Comandos permitidos/proibidos | `08_APPROVED_COMMANDS.md` | Antes de rodar comando não listado |

---

## Template de Resposta Técnica (Obrigatório)

**Estrutura mínima para qualquer resposta:**

1. **Doc citado**: path do documento canônico consultado (ex: `05_MODELS_PIPELINE.md`) OU, para conceito minor, só `exit_codes.md`
2. **Evidência citada**: artefato/comando usado (ex: `parity_report.json` linha 42 + `schema.sql` linha 150)
3. **Próximo comando**: único comando executável (não múltiplos; fail-fast) OU comando gate atomicamente composto

**Exemplo:**
```
Doc: docs/_canon/05_MODELS_PIPELINE.md (seção "PRE-parity")
Evidência: parity_report.json mostra structural diff em `attendance.athlete_id`
          + schema.sql linha 150: `FOREIGN KEY (athlete_id) REFERENCES athletes(id)`
Próximo: .\scripts\parity_scan.ps1 -TableFilter attendance
```

**Proibido:**
- Respostas sem doc citado
- Evidência baseada em "suposição" ou "geralmente"
- Múltiplos comandos sem fail-fast (exceto gates atomicamente compostos como `models_autogen_gate.ps1`)

---

## Perguntas Permitidas vs Proibidas

**Quando o agent PODE pedir clarificação:**
- Comando não existe em `08_APPROVED_COMMANDS.md` (pedir aprovação antes)
- Snapshot baseline após gates OK (confirmar autorização)
- Exit code ambíguo sem contexto em `exit_codes.md`
- CWD não está claro (repo root vs backend root)

**Quando o agent NÃO DEVE perguntar (comando canônico já existe):**
- Qual comando usar para parity (já definido: `parity_scan.ps1`)
- Qual comando usar para refresh (já definido: `inv.ps1 refresh`)
- Como corrigir model (já definido: `models_autogen_gate.ps1`)
- Formato de evidência (já definido: exit code + output + git status)

**Regra de ouro**: se o doc canônico já responde, não pergunte; siga o doc.

---

## 1. Single Source of Truth — Artefatos Gerados

**Root**: `Hb Track - Backend\docs\_generated\`

Os artefatos abaixo são gerados automaticamente e constituem a fonte autoritativa do estado do sistema.

| Artefato | Path (relativo ao backend root) | Descrição | Como Gerar | Atualizar Quando |
|----------|------|-----------|-----------|------------------|
| **schema.sql** | `docs\_generated\schema.sql` | DDL PostgreSQL (tabelas, constraints, enums, COMMENT ON COLUMN) | `.\scripts\inv.ps1 refresh` (repo root) | Antes de parity/requirements; após migrations |
| **openapi.json** | `docs\_generated\openapi.json` | Especificação OpenAPI 3.1 FastAPI (operationIds, schemas, paths) | `.\scripts\inv.ps1 refresh` (repo root) | Após mudanças em API routes/models |
| **alembic_state.txt** | `docs\_generated\alembic_state.txt` | Estado atual das migrations (head + versão corrente) | `.\scripts\inv.ps1 refresh` (repo root) | Após rodar `alembic upgrade head` |
| **parity_report.json** | `docs\_generated\parity_report.json` | Relatório model↔schema (structural + field diffs) | `.\scripts\parity_scan.ps1 -TableFilter <TABLE>` (backend root) | Diagnóstico antes de editar models |
| **manifest.json** | `docs\_generated\manifest.json` | Rastreabilidade (git commit, checksums, timestamps) | `.\scripts\inv.ps1 refresh` (repo root) | Automático; verificar para auditoria |

**Regras de Pureza do SSOT:**
- ⚠️ **Não editar artefatos gerados manualmente**. Se schema.sql está errado, a fonte (DB/migrations) está errada.
- ✅ **Refresh antes de gates**: sempre rodar `inv.ps1 refresh` antes de parity/requirements (salvo flag `-SkipDocsRegeneration` conforme regra).
- ✅ **Snapshot após SSOT change**: se schema.sql/openapi.json mudou e afetou guard → considerar `snapshot baseline` (após gates OK).

**Comando canônico** (executar na raiz do monorepo `C:\HB TRACK`):
```powershell
.\scripts\inv.ps1 refresh
```

**Detalhes técnicos de geração**: ver `docs\_canon\04_SOURCES_GENERATED.md` e `docs\_canon\03_WORKFLOWS.md`.

---

## 2. Referências Operacionais

| Documento | Path | Descrição | Quando Consultar |
|-----------|------|-----------|------------------|
| **CHANGELOG** | `docs\execution_tasks\CHANGELOG.md` | Registro de mudanças notáveis (pipeline, scripts, models, features) | Após cada lote de mudanças |
| **EXECUTIONLOG** | `docs\execution_tasks\EXECUTIONLOG.md` | Log técnico: execuções, gates, auditorias, sessões de trabalho | Após cada sessão |
| **Exit Codes** | `docs\references\exit_codes.md` | Guia: 0 (pass), 1 (crash), 2 (parity), 3 (guard), 4 (requirements) | **Sempre que ec ≠ 0** |
| **Model Requirements Guide** | `docs\references\model_requirements_guide.md` | Uso do validador `model_requirements.py` (perfis, violations, troubleshooting) | Exit code 4 |
| **Troubleshooting Guard/Parity** | `docs\_canon\09_TROUBLESHOOTING_GUARD_PARITY.md` | Diagnóstico: exit codes 2/3/4, causas raiz, resolução passo-a-passo | Exit code 2/3/4 |
| **Approved Commands** | `docs\_canon\08_APPROVED_COMMANDS.md` | Whitelist: comandos seguros para agents; proibidos (rm -rf, git reset --hard, etc) | **Antes de rodar comando não listado** |

---

## 3. Single Source of Truth — Requisitos

| Documento | Path | Descrição |
|-----------|------|-----------|
| **PRD** | `docs\00_product\PRD_HB_TRACK.md` | v2.1 — Requisitos do produto, user stories, MoSCoW, SLAs, modelo de negócio |
| **PRD Review** | `docs\00_product\PRD_REVIEW.md` | Revisão técnica — scorecard, lacunas, oportunidades |
| **Análise de Coerência** | `docs\00_product\analise_coerencia_documentacao.md` | Validação PRD↔TRD↔INVARIANTS (escopo Training) |

---

## 4. Hierarquia Documental

```
docs\00_product\PRD_HB_TRACK.md                                   (SSOT — requisitos, v2.1)
├── docs\02_modulos\training\PRD_BASELINE_ASIS_TRAINING.md        (estado implementado, v1.2)
│   ├── docs\02_modulos\training\TRD_TRAINING.md                  (referência técnica, v1.6)
│   │   ├── docs\02_modulos\training\INVARIANTS\INVARIANTS_TRAINING.md        (confirmadas/pretendidas/inativas)
│   │   └── docs\02_modulos\training\INVARIANTS\INVARIANTS_TESTING_CANON.md  (Rule of Law — DoD + classes A-F)
│   └── docs\02_modulos\training\UAT_PLAN_TRAINING.md             (25 cenários, v1.0)
├── docs\00_product\analise_coerencia_documentacao.md
└── docs\00_product\PRD_REVIEW.md

SSOT Artifacts:
  Hb Track - Backend\docs\_generated\schema.sql
  Hb Track - Backend\docs\_generated\openapi.json
  Hb Track - Backend\docs\_generated\alembic_state.txt
  Hb Track - Backend\docs\_generated\parity_report.json
  Hb Track - Backend\docs\_generated\manifest.json
```

---

## 5. Governança AI — Monorepo (`docs\_ai\`)

| Documento | Path | Descrição |
|-----------|------|-----------|
| **Index** (este) | `docs\_ai\_INDEX.md` | Router central + Quick Start Routing. Começar sempre aqui. |
| **Agent Prompts** | `docs\_ai\06_AGENT-PROMPTS.md` | Copy/paste prompts prontos para validação/correção models |
| **Agent Protocol** | `docs\_ai\INVARIANTS_AGENT_PROTOCOL.md` | Local-first: SSOT refresh, validação, workflow obrigatório |
| **Agent Guardrails** | `docs\_ai\INVARIANTS_AGENT_GUARDRAILS.md` | Anti-alucinação: fontes canônicas, gates, stop rules |
| **Task Template** | `docs\_ai\INV_TASK_TEMPLATE.md` | Template: instalar 1 invariante com zero alucinação |
| **System Design** | `docs\_ai\SYSTEM_DESIGN.md` | Arquitetura backend (stack, camadas, padrões, convenções) |
| **Agent Routing Map** | `docs\_ai\07_AGENT_ROUTING_MAP.md` | Mapa: ação → instruções → docs canônicos → comandos |

---

## 6. Documentação Canônica para Governança AI (`docs\_canon\`)

| Documento | Path | Descrição |
|-----------|------|-----------|
| **Authority & SSOT** | `docs\_canon\01_AUTHORITY_SSOT.md` | Precedência: DB schema > Service models > OpenAPI > Docs |
| **Context Map** | `docs\_canon\02_CONTEXT_MAP.md` | Fluxos por intenção: entender, fazer, corrigir |
| **Workflows** | `docs\_canon\03_WORKFLOWS.md` | Protocolos: adicionar invariante, corrigir parity, validar conformidade |
| **Sources & Generated** | `docs\_canon\04_SOURCES_GENERATED.md` | Detalhes de geração e interpretação de artefatos |
| **Pipeline de Models** | `docs\_canon\05_MODELS_PIPELINE.md` | **Autoridade**: validação/correção (parity → requirements → guard) |
| **Approved Commands** | `docs\_canon\08_APPROVED_COMMANDS.md` | Whitelist + proibidos. Consultar antes de rodar. |
| **Troubleshooting** | `docs\_canon\09_TROUBLESHOOTING_GUARD_PARITY.md` | Exit code 2/3/4: causas, diagnóstico, resolução |
| **Quality Metrics** | `docs\_canon\QUALITY_MATRICS.md` | Métricas de qualidade, padrões de código e critérios de sucesso para reviews/refactoring |
| **GitHub Instructions** | `.github\instructions\*.instructions.md` | Carregamento condicional (git, commands, docs, etc) |

---

## 7. Governança AI — Frontend (`Hb Track - Frontend\docs\_ai\`)

| Documento | Path | Descrição |
|-----------|------|----------|
| **Canon** | `Hb Track - Frontend\docs\_ai\CANON.md` | Fontes de verdade, stack, invariantes |
| **Router** | `Hb Track - Frontend\docs\_ai\ROUTER.md` | Classificação de tarefas (bugfix/endpoint/refactor) |
| **Checks** | `Hb Track - Frontend\docs\_ai\CHECKS.md` | Verificação local (lint, test, type-check) |
| **Playbook Bugfix** | `Hb Track - Frontend\docs\_ai\PLAYBOOK_bugfix.md` | Playbook para bugfixes |
| **Playbook Endpoint** | `Hb Track - Frontend\docs\_ai\PLAYBOOK_endpoint.md` | Playbook para nova API |
| **Playbook Refactor** | `Hb Track - Frontend\docs\_ai\PLAYBOOK_refactor.md` | Playbook para refactoring |

---

## 8. Módulo Training — Documentação Principal

| Documento | Path | Descrição |
|-----------|------|-----------|
| **PRD Baseline AS-IS** | `docs\02_modulos\training\PRD_BASELINE_ASIS_TRAINING.md` | Estado implementado (v1.2, evidência snapshot) |
| **TRD** | `docs\02_modulos\training\TRD_TRAINING.md` | Referência técnica (v1.6): API contracts, regras negócio, evidências, gaps |
| **Invariantes** | `docs\02_modulos\training\INVARIANTS\INVARIANTS_TRAINING.md` | Confirmadas, pretendidas, inativas |
| **Canon de Testes** | `docs\02_modulos\training\INVARIANTS\INVARIANTS_TESTING_CANON.md` | Rule of Law: DoD, classes A-F, anti-alucinação |
| **UAT Plan** | `docs\02_modulos\training\UAT_PLAN_TRAINING.md` | 25 cenários de aceitação (v1.0) |

---

## 9. Módulo Training — Documentação de Suporte

| Documento | Path | Descrição |
|-----------|------|-----------|
| **Candidates** | `docs\02_modulos\training\INVARIANTS\training_invariants_candidates.md` | Worklist: promoção de candidatas |
| **Backlog** | `docs\02_modulos\training\INVARIANTS\training_invariants_backlog.md` | Backlog: pendentes de análise |
| **Parity Scan Protocol** | `docs\02_modulos\training\PROTOCOLS\PARITY_SCAN_PROTOCOL.md` | Protocolo: verificação model↔schema |
| **Validação de Testes** | `docs\02_modulos\training\INVARIANTS\VALIDAR_INVARIANTS_TESTS.md` | Checklist: validação dos testes |

---

## 10. Comandos de Validação (Approved)

**Nota**: Todos os comandos abaixo são **subconjunto de `docs\_canon\08_APPROVED_COMMANDS.md`**. Se houver divergência, `08_APPROVED_COMMANDS.md` vence.

**Executar conforme CWD na tabela "Guardrail: CWD"**:

| Comando | Onde Rodar | Finalidade | Exit Codes |
|---------|------------|-----------|-----------|
| `.\scripts\inv.ps1 refresh` | Repo root | Regenerar SSOT (schema.sql, openapi.json, alembic_state.txt, manifest.json) | 0 = success, 1 = crash |
| `.\scripts\parity_scan.ps1 -TableFilter <TABLE>` | Backend root | Gerar parity_report.json para tabela específica | 0 = match, 2 = diff, 3/4 = violations |
| `.\scripts\models_autogen_gate.ps1 -Table <TABLE> -Profile strict` | Backend root | Validar + autogen model; snapshot baseline se aprovado | 0 = pass, 1 = crash, 4 = requirements violations |
| `venv\Scripts\python.exe scripts\model_requirements.py --table <TABLE> --profile strict` | Backend root | Validar conformidade model vs schema.sql (read-only) | 0 = pass, 1 = crash, 4 = violations |
| `.\scripts\inv.ps1 gate INV-TRAIN-XXX` | Repo root | Validar gate de invariante específica | 0 = pass, 1/2/3/4 = fail |
| `.\scripts\inv.ps1 all` | Repo root | Rodar todos os gates | 0 = all pass, >0 = flag failed gates |
| `.\scripts\inv.ps1 promote` | Repo root | Promover candidatas confirmadas para invariantes | 0 = success, 1 = crash |

**Guia Completo**: ver `docs\_canon\08_APPROVED_COMMANDS.md` (fonte canônica).

---

## Notas Finais

* **Paths roots**:
  - Repo: `C:\HB TRACK` (Windows) | `<repo>` (portável)
  - Backend: `C:\HB TRACK\Hb Track - Backend` (Windows) | `<repo>/Hb Track - Backend` (portável)
* **Não editar artefatos gerados**: se schema.sql está errado, rodar migrations/inv.ps1 refresh
* **Commit vs Snapshot**: commit = VCS, snapshot = baseline. Ambos podem ser necessários.
* **Sempre com evidência**: exit code + output + git status
* **Venv validado**: antes de Python/pip, testar `venv\Scripts\python.exe --version`
* **Precedência**: em caso de conflito, docs canônicos (`05_MODELS_PIPELINE.md`, `03_WORKFLOWS.md`, `08_APPROVED_COMMANDS.md`) vencem este Index
* **CWD obrigatório**: validar antes de rodar qualquer comando (ver tabela "Guardrail: CWD")
* **Exit codes**: sempre propagar específicos (0/2/3/4); nunca flatten para 1; fonte autoritativa: `exit_codes.md`
* **Snapshot**: só após gates OK + repo limpo; nunca com EXIT 2/3/4
* **Este Index é router, não canon**: serve para navegar; quando conflitar com canon, canon vence