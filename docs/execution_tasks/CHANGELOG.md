# Changelog - HB Track
Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]
### Adicionado
* **Pipeline P0-P5 Hardening** (2026-02-10): Conjunto de melhorias no pipeline de integrid. Model ↔ DB:
  - **P0-A**: Fix crítico de encoding em `parity_scan.ps1` — substituído `Tee-Object` (UTF-16LE) por captura em variável + escrita UTF-8 via `[System.IO.File]::WriteAllText`. Corrige bug onde **todos** os items do `parity_report.json` tinham `table: null, column: null`.
  - **P0-B**: Defesa em profundidade em `parity_classify.py` — strip de NUL bytes residuais + warning no stderr.
  - **P1**: Melhoria de `extract_table_col()` em `parity_classify.py` — adicionados 4 novos patterns de extração (NULL on column, server_default, for 'table.col', sequence name), + fix de `classify()` para `server_default` (underscore).
  - **P2**: Parâmetro `-SkipDocsRegeneration` em `parity_scan.ps1` e `parity_gate.ps1` — evita double SSOT refresh (~50% menos I/O por gate invocation).
  - **P3**: Refatoração de `models_autogen_gate.ps1` — 4 blocos if/else duplicados substituídos por **hashtable splatting** (`@parityParams`). POST parity agora usa `-SkipDocsRegeneration`. Fix de bug onde array splatting causava erro de binding posicional em PS 5.1.
  - **P3-B**: Fix de splatting em `parity_gate.ps1` — chamada a `parity_scan.ps1` convertida de array splatting para hashtable splatting (mesma causa raiz: PS 5.1 não reconhecia `-TableFilter` como parâmetro via array splat).
  - **P4**: Robustez de `models_batch.ps1` — flag `-DryRun`, fix de `$LASTEXITCODE` mascarado por `Tee-Object` em `Run-Gate`, summary stats com timing no final.
  - **P5**: `parity-scan.log` adicionado ao `Restore-GeneratedArtifacts`.

### Corrigido
* **Bug Crítico `table: null`**: O `parity_report.json` gerado pelo pipeline tinha **todas** as entradas com `table: null` e `column: null` devido a `Tee-Object` do PowerShell 5.1 escrevendo o log Alembic em UTF-16LE sem BOM explícito, causando truncamento de mensagens no parser Python.
* **`$LASTEXITCODE` mascarado**: Em `models_batch.ps1`, `Run-Gate` usava pipeline com `Tee-Object | Out-Null`, o que podia mascarar o exit code real do gate. Corrigido para captura em variável.
* **`classify()` server_default**: A função `classify()` não reconhecia mensagens com `server_default` (underscore), apenas `server default` (espaço). Corrigido.

* **Governança de Execução**: Inclusão, em `.clinerules`, de blueprint obrigatório para atualização de `docs/adr/architecture/CHANGELOG.md` e `docs/adr/architecture/EXECUTIONLOG.md` ao fim de cada tarefa.
* **Gate de Validação ADR-MODELS-001**: Implementação completa do sistema de validação em 3 camadas (guardrails → parity → requirements) para Models SQLAlchemy.
  - **FASE 1:** `model_requirements.py` (1155 linhas) com parsers DDL/AST, validador (3 perfis: strict/fk/lenient), e CLI wrapper
  - **FASE 2:** Integração STEP 4 no `models_autogen_gate.ps1` com propagação correta de exit code 4
  - **FASE 3:** Verificação e correção de propagação de exit codes específicos (0/2/3/4)
  - **FASE 4:** Smoke tests executados (5 cenários): conformidade total (exit=0), detecção de alucinação (exit=4), crash path (exit=1), guard violation real (exit=3), perfis de validação (fk) — resultado: 5/5 testes passaram (100%)
  - **FASE 5:** Documentação executável criada:
    - `docs/references/exit_codes.md` (guia completo de exit codes 0/1/2/3/4)
    - `docs/workflows/model_requirements_guide.md` (guia de uso, troubleshooting, perfis)
    - `docs/architecture/CHECKLIST-CANONICA-MODELS.md` (checklist passo-a-passo)

### Corrigido
* **Exit Code 3 Implementation**: Restaurada semântica canônica dos exit codes para desambiguar parity de guard violations:
  - **agent_guard.py linha 225**: Alterado `return 2` → `return 3` para violations (baseline mismatches)
  - **Exit Code 2**: Agora usado EXCLUSIVAMENTE para parity violations (structural diffs DB ↔ Model via alembic)
  - **Exit Code 3**: Agora usado EXCLUSIVAMENTE para guard violations (baseline drift via agent_guard.py)
  - **Motivação de engenharia**: Exit=2 estava ambíguo (parity OR guard), dificultando debugging em CI/CD
  - **Smoke Test validado**: TEST 3B confirmou exit=3 para guard violation após patch
  - **Impacto**: Melhoria em debuggabilidade do gate; cada camada agora tem exit code específico (guard=3, parity=2, requirements=4)
* **Terminal/PowerShell**: Ajustada a abordagem de execução para comandos incrementais (1 check por comando) após `ParserError` de quoting no wrapper canônico.
* **Pré-requisitos EXEC_TASK**: Documentado bloqueio por ausência de `.hb_guard/baseline.json` no CHECK 5, mantendo política fail-fast sem auto-correção.
* **Exit Code Propagation**: Confirmada propagação correta de exit codes específicos (0/2/3/4) em `models_autogen_gate.ps1` e `model_requirements.py`.
* **Models**: Correção de duplicações em `athlete.py` e `attendance.py` que sobrescreviam HB-AUTOGEN blocks (remoção de imports/columns/`__table_args__` duplicados)
* **Gate Performance**: Fix em `parity_gate.ps1` para calcular `$ROOT` a partir de `$PSScriptRoot` (não CWD), eliminando scan de workspace inteiro e reduzindo tempo de guard de 60s+ para <5s
* **Autogen Bug**: Correção crítica em `autogen_model_from_db.py` para detectar `relationship()` no model e preservar import de `relationship` em `sqlalchemy.orm`, evitando `NameError` em models com relationships block
* **Coverage**: Aplicação de fix de relationship import em todos os 35 models que usam relationships (athlete, attendance, person, user, season, team, etc.)

---

## [0.1.0] - 2024-02-08
### Adicionado
* Estrutura inicial do projeto com FastAPI e PostgreSQL.
* Configuração do Alembic para migrações.
* Documentação de Baseline (PRD/TRD/Invariants).