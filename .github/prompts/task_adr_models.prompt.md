Execute a tarefa exatamente como definida no arquivo [EXEC_TASK_ADR_MODELS_001.md](docs/execution_tasks/EXEC_TASK_ADR_MODELS_001.md). 

Regras obrigatórias:

1. PREENCHER PRÉ-REQUISITOS: rode TODOS os checklist de pré-requisitos definidos em `.clinerules` seção "EXEC_TASK PREREQUISITES VALIDATION" e ABORTE se qualquer um falhar
2. ORDEM ESTRITA: siga as Fases em ordem sequencial conforme documento
3. ESCOPO RESTRITO: não altere arquivos fora da lista do checklist do EXEC_TASK
4. EVIDÊNCIA OBRIGATÓRIA: após cada comando, mostre output completo e $LASTEXITCODE
5. SHELL CANÔNICO: use APENAS PowerShell 5.1 com wrapper canônico de `.clinerules` (nunca bash/WSL)
6. VENV OBRIGATÓRIO: use sempre `Hb Track - Backend/venv/Scripts/python.exe` (validar existência antes)
7. SEM INVOKE-EXPRESSION: use call operator & com array de args (ver `.clinerules` seção "INVOKE-EXPRESSION: PROIBIDO")
8. EXIT CODE PRESERVADO: propague códigos específicos (0/2/3/4), nunca flatten para 1
9. TESTE FINAL: entregue ao final os testes globais (Smoke Test Final) com evidência completa

**Integração STEP 4 (model_requirements.py):**
- NÃO usar Invoke-Expression conforme linha 376 antiga do EXEC_TASK
- Implementar como: `& $venvPy @requirementsArgs` (já corrigido no documento)
- Usar call operator `&` com argumentos explícitos para evitar quebra de quoting em PowerShell 5.1

**Abortar imediatamente se:**
- PowerShell não é versão 5.1
- Venv não existe ou está corrompido
- Python não é 3.11+
- Dependências (sqlalchemy/alembic) não instaladas
- Baseline (`.hb_guard/baseline.json`) não existe
- Schema.sql desatualizado ou ausente