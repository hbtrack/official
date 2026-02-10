---
description: HB Track project context and mandatory execution rules for Agent/Copilot
applyTo: 'Hb Track/**'
---

## PORTA ÚNICA: Camada Canônica Docs

**Para QUALQUER consulta técnica, comece AQUI:** `docs/_canon/00_START_HERE.md`

Execute a tarefa exatamente como definida no arquivo `C:\HB TRACK\docs\_ai\EXEC_TASK_ADR_MODELS_001.md`. Não desvie do escopo, ordem, ou regras definidas. Siga todas as instruções rigorosamente.

Esta camada orienta para documentação correta conforme sua intenção:
- **O que confiar (precedência):** → `docs/_canon/01_AUTHORITY_SSOT.md` (DB > Service > OpenAPI > Docs)
- **Quero fazer X, por onde?: → `docs/_canon/02_CONTEXT_MAP.md` (intenção → docs → evidência)
- **Workflow/checklist:** → `docs/_canon/03_WORKFLOWS.md` (passo-a-passo operacional)
- **Arquivos gerados:** → `docs/_canon/04_SOURCES_GENERATED.md` (schema.sql, openapi.json, reports)

**Regra obrigatória:** Toda resposta técnica deve citar (a) um documento canônico e (b) uma evidência (código, schema.sql, openapi.json, parity_report.json ou ADR).

---

## Execução de Tarefas ADR/EXEC_TASK
1. PREENCHER PRÉ-REQUISITOS: rode TODOS os checklist de pré-requisitos definidos em .clinerules seção "EXEC_TASK PREREQUISITES VALIDATION" e ABORTE se qualquer um falhar
2. ORDEM ESTRITA: siga as Fases em ordem sequencial conforme documento
3. ESCOPO RESTRITO: não altere arquivos fora da lista do checklist do EXEC_TASK
4. EVIDÊNCIA OBRIGATÓRIA: após cada comando, mostre output completo e $LASTEXITCODE
5. SHELL CANÔNICO: use APENAS PowerShell 5.1 com wrapper canônico de .clinerules (nunca bash/WSL)
6. VENV OBRIGATÓRIO: use sempre "C:\HB TRACK\Hb Track - Backend\venv\Scripts\python.exe" (validar existência antes)
7. SEM INVOKE-EXPRESSION: use call operator & com array de args (ver .clinerules seção "INVOKE-EXPRESSION: PROIBIDO")
8. EXIT CODE PRESERVADO: propague códigos específicos (0/2/3/4), nunca flatten para 1
9. TESTE FINAL: entregue ao final os testes globais (Smoke Test Final) com evidência completa

**Integração STEP 4 (model_requirements.py):**
- NÃO usar Invoke-Expression conforme linha 376 antiga do EXEC_TASK
- Implementar como: `& $venvPy @requirementsArgs` (já corrigido no documento)
- Usar call operator & com argumentos explícitos para evitar quebra de quoting em PowerShell 5.1

**Abortar imediatamente se:**
- PowerShell não é versão 5.1
- Venv não existe ou está corrompido
- Python não é 3.11+
- Dependências (sqlalchemy/alembic) não instaladas
- Baseline (.hb_guard/baseline.json) não existe
- Schema.sql desatualizado ou ausente

# Guia de Requisitos para Modelos
C:\HB TRACK\docs\workflows\model_requirements_guide.md

# Checklist Canônica para Modelos
C:\HB TRACK\Hb Track - Backend\docs\architecture\CHECKLIST-CANONICA-MODELS.md

# Guia de referência para os códigos de saída dos script de validação
C:\HB TRACK\docs\references\exit_codes.md

---

## Workspace Prompts & Docs Organization

### Prompt Files (Slash Commands)

Use `/` no Copilot Chat para acessar prompts acionáveis:

- `/parity-fix` — Corrigir divergências Model↔DB (parity_report.json + schema.sql)
- `/models-gate` — Avaliar gate de modelos e guiar correção
- `/install-invariant` — Instalar invariante de training com SSOT
- `/generate-exec-task` — Gerar EXEC_TASK de ADR/workflow

Todos em: `.github/prompts/*.prompt.md`

### Docs Organization

**Canonical Authority:**
- `docs/_canon/` — autoridade + navegação (START_HERE, SSOT, workflows, troubleshooting)
- `docs/_ai/` — guidelines operacionais para agente + protocol + guardrails

**SSOT Artifacts (Protected):**
- `docs/_generated/_core/` — schema.sql, openapi.json, parity_report.json, alembic_state.txt, manifest.json
- **Use env var:** `HB_DOCS_GENERATED_DIR` para customizar (default: `_generated`)

**Debug/Scratch (Excluded from Index):**
- `docs/_generated/_scratch/` — debug artifacts (excluded via .gitignore)
- `docs/scripts/_archive/` — archived/legacy scripts (excluded via .gitignore)

**Reference:**
- `docs/ADR/` — architecture decisions (decisões importantes, não executáveis)
- `docs/execution_tasks/` — EXEC_TASK files (tarefas executáveis com gates)
- `docs/02_modulos/` — módulos por feature (athletes, training, teams, etc)

**Observação:** VS Code workspace context (`@workspace #codebase`) automaticamente exclui arquivos em `.gitignore`. Isso melhora busca e reduz ruído para Copilot (~50% menos artefatos debug indexados).