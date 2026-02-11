# Changelog - HB Track
Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]
### Adicionado
* **Reorganização docs/_ai/** (2026-02-11): Estruturação sistemática de documentação para agentes:
  - **7 Subdirectórios Temáticos**: `_context/`, `_specs/`, `_prompts/`, `_maps/`, `_guardrails/`, `_checklists/`, `_docs_arch/`
  - **20 Arquivos Novos com Placeholders**:
    - **_context/** (4 files): AGENT_INITIAL_CONTEXT, AGENT_RULES_ENGINE, AGENT_GUARDRAILS, AGENT_CONSTRAINTS
    - **_specs/** (4 files): SPEC_AGENT_MODELS.json, SPEC_AGENT_GATES.yaml, SPEC_AGENT_GUARDRAILS.xml, SPEC_AGENT_ROUTING.json
    - **_prompts/** (3 files): PROMPT_TEMPLATE_CODE_REVIEW, PROMPT_TEMPLATE_DOCUMENTATION, PROMPT_TEMPLATE_TESTING
    - **_maps/** (3 files): MAP_ROUTING_AGENT_MODELS, MAP_ROUTING_AGENT_GATES, MAP_ROUTING_AGENT_DOCUMENTATION
    - **_guardrails/** (3 files): GUARDRAIL_POLICY_BASELINE, GUARDRAIL_POLICY_PARITY, GUARDRAIL_POLICY_REQUIREMENTS
    - **_checklists/** (3 files): CHECKLIST_AGENT_DEPLOYMENT, CHECKLIST_AGENT_VALIDATION, CHECKLIST_AGENT_DOCUMENTATION
    - **_docs_arch/** (1 file): DOCS_ARCH_MASTER.md
  - **Padrão Embedded**: Cada arquivo contém descrição no header + estrutura de placeholder + TODO sections
  - **Integração de Documentação**: Nova arquitetura melhora navegação e acesso a guardrails/specs/prompts para agentes AI

* **Canon Baseline Alignment** (2026-02-11): Alinhamento da documentação canônica com a realidade do repositório:
  - **Baseline é Local**: Removidas todas as instruções "commit baseline" do canon. `.hb_guard/baseline.json` está em `.gitignore:141` (nunca versionado).
  - **Phase 0: Bootstrap Baseline**: Adicionada seção obrigatória em `05_MODELS_PIPELINE.md` para regenerar baseline antes de gates (garante comparação válida).
  - **Documentação Atualizada**: 5 arquivos canônicos corrigidos:
    1. `08_APPROVED_COMMANDS.md` CMD-6.1: Baseline marcado "LOCAL" com regra de ouro + justificativa (multi-env risks)
    2. `05_MODELS_PIPELINE.md`: Phase 0 Bootstrap + remoção de "commit separado"
    3. `03_WORKFLOWS.md`: Removido "Passo 4: Commit Baseline" completo
    4. `09_TROUBLESHOOTING_GUARD_PARITY.md`: Removidas linhas `git add/commit baseline`
    5. `10_GIT_PR_MERGE_WORKFLOW.md`: Mudado para "Baseline é local (não versionado)"
  - **Design 1.5 (Allowlist Acumulativa)**: Confirmado plano para implementação em `models_batch.ps1` — guard protege, batch acumula paths de modelos já corrigidos, reduz re-validação.

* **Autogen Model Hardening** (2026-02-11): Melhorias críticas no `autogen_model_from_db.py` para correção automática de models:
  - **Multiline Import Removal**: Detecção e remoção de imports multilinha (`from sqlalchemy import (\n    Boolean,\n    ...)`). Implementado tracking de `open_parens` para identificar continuação de imports.
  - **Orphan Line Detection**: Remoção de linhas órfãs de import (ex: `    Boolean,`) que ficavam após remoção parcial de imports multilinha.
  - **ARRAY Type Handling**: Geração correta de `sa.ARRAY(item_type)` para colunas PostgreSQL do tipo ARRAY. Adicionado check `isinstance(t, sa.ARRAY)` com recursão para `item_type`.
  - **Bare Mapped[] Removal**: Pattern 3 para detectar e remover anotações `Mapped[...]` sem atribuição (`= mapped_column(...)` ou `= relationship(...)`).
  - **__table_args__ Unconditional Removal**: Sempre remove `__table_args__` fora do HB-AUTOGEN block (não apenas quando autogen tem um), evitando duplicações.
  - **Import Dedup Function**: Nova função `_remove_duplicate_imports_outside_autogen()` para remover imports redundantes fora do bloco HB-AUTOGEN-IMPORTS.
  - **TYPE_CHECKING Detection**: Detecta uso de `TYPE_CHECKING` no arquivo e adiciona ao import `from typing import TYPE_CHECKING`.
  - **Typing Extras Detection**: Detecta uso de `List[`, `Dict[`, `Set[`, `Tuple[`, `Any` e adiciona aos imports de typing.
  - **UUID→PG_UUID Legacy Fix**: Nova função `_fix_legacy_patterns()` converte `UUID(as_uuid=` para `PG_UUID(as_uuid=` fora do HB-AUTOGEN.
  - **text() Import Detection**: Detecta uso de `text()` e adiciona ao import `from sqlalchemy import text`.
  - **Functional Index Skip**: Skip de indexes com `None` em `col_names` (índices funcionais sem colunas explícitas).

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
* **IndentationError após autogen**: Imports multilinha (`from sqlalchemy import (...)`) não eram removidos completamente, deixando linhas órfãs indentadas que causavam `IndentationError` ao importar o model.
* **TypeError em ARRAY columns**: `_sa_type_expr()` não tratava `sa.ARRAY` corretamente, causando `TypeError` durante autogen. Corrigido com recursão para extrair `item_type`.
* **Duplicação de __table_args__**: Autogen só removia `__table_args__` fora do HB-AUTOGEN quando o bloco autogen também tinha um. Agora remove incondicionalmente.
* **Bare Mapped annotations**: Linhas como `    athlete_id: Mapped[int]` (sem `= mapped_column()`) não eram detectadas/removidas, causando erros de sintaxe.
* **SyntaxError from __future__**: Imports `from __future__` duplicados (dentro e fora do HB-AUTOGEN) causavam SyntaxError. Corrigido via `_remove_duplicate_imports_outside_autogen()`.
* **NameError TYPE_CHECKING**: Uso de `TYPE_CHECKING` em models sem import correspondente causava `NameError`. Corrigido com detecção automática.
* **NameError List/Dict/Set/Tuple/Any**: Uso de typing extras sem import causava `NameError`. Corrigido com detecção automática.
* **TypeError UUID(as_uuid=)**: Código legado usando `UUID(as_uuid=True)` falhava porque `UUID` do SQLAlchemy 2.x não aceita esse kwarg. Corrigido convertendo para `PG_UUID`.
* **NameError text**: Uso de `text()` sem import causava `NameError`. Corrigido com detecção de `sa_extras`.
* **ArgumentError functional indexes**: Indexes funcionais (ex: `lower(email)`) tinham `None` em `col_names`, causando crash. Corrigido com skip.

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