# Changelog - HB Track
Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]
### Adicionado
* **Governança de Execução**: Inclusão, em `.clinerules`, de blueprint obrigatório para atualização de `docs/adr/architecture/CHANGELOG.md` e `docs/adr/architecture/EXECUTIONLOG.md` ao fim de cada tarefa.
* **Gate de Validação ADR-MODELS-001**: Implementação completa do sistema de validação em 3 camadas (guardrails → parity → requirements) para Models SQLAlchemy.
  - **FASE 1:** `model_requirements.py` (1155 linhas) com parsers DDL/AST, validador (3 perfis: strict/fk/lenient), e CLI wrapper
  - **FASE 2:** Integração STEP 4 no `models_autogen_gate.ps1` com propagação correta de exit code 4
  - **FASE 3:** Verificação e correção de propagação de exit codes específicos (0/2/3/4)
  - **FASE 4:** Smoke tests executados (4 cenários): conformidade total (exit=0), detecção de alucinação (exit=4), propagação de exit codes, perfis de validação (strict/fk) — resultado: 3/4 testes passaram (75%)
  - **FASE 5:** Documentação executável criada:
    - `docs/references/exit_codes.md` (guia completo de exit codes 0/1/2/3/4)
    - `docs/workflows/model_requirements_guide.md` (guia de uso, troubleshooting, perfis)
    - `docs/architecture/CHECKLIST-CANONICA-MODELS.md` (checklist passo-a-passo)

### Corrigido
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