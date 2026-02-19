# Sistema de Planos HB Track - Architect-Executor Flow

## Visão Geral

Este sistema implementa o fluxo **Architect-Executor** para desenvolvimento determinístico. O Arquiteto (IA) cria planos detalhados que o Executor (IA ou Humano) implementa com zero ambiguidade.

### Princípios

- **Determinismo**: Todo plano é executável sem decisões adicionais
- **Rastreabilidade**: Métricas, locks e status garantem visibilidade total
- **Segurança**: Validações pré/pós execução impedem regressões
- **Encapsulamento**: Estrutura auto-contida em `scripts/plans/`

---

## Estrutura de Diretórios

```
scripts/plans/
├── config.py                          # Constantes de caminhos (TODAS absolutas)
├── check_locks.py                     # Gerenciador de locks de arquivo
├── executor_workflow.py               # Orquestrador principal
├── generate_context_snapshot.py       # Gera snapshot do repo para o Arquiteto
├── plan_status.py                     # Gerenciador de status de planos
├── record_metrics.py                  # Coletor de métricas de execução
├── validate_dag.py                    # Validador de dependências entre planos
├── validate_plan_adherence.py         # Valida se execução seguiu o plano
└── docs/
    ├── file_locks.yaml                # Locks ativos
    ├── context/                       # Snapshots de contexto
    ├── implemented/                   # Planos já executados
    ├── metrics/
    │   └── executor_metrics.json      # Histórico de métricas
    └── plans/                         # Planos aprovados aguardando execução
```

---

## Como Usar

### 🎯 Executar da Raiz do Projeto

**IMPORTANTE:** Todos os comandos devem ser executados da raiz `C:\HB TRACK` (ou `/home/user/HB TRACK` no Linux).

```powershell
# ✅ CORRETO (Windows)
PS C:\HB TRACK> python scripts\plans\plan_status.py scripts\plans\docs\plans\FASE-5-3.md

# ✅ CORRETO (Linux/VPS)
$ python scripts/plans/plan_status.py scripts/plans/docs/plans/FASE-5-3.md

# ❌ ERRADO (vai falhar)
PS C:\HB TRACK\scripts\plans> python plan_status.py docs\plans\FASE-5-3.md
```

**Por quê?** O `config.py` usa caminhos absolutos calculados a partir de `__file__`, garantindo que funcionem independentemente do diretório de execução. Mas o ambiente virtual (venv) e o Git exigem que você esteja na raiz.

---

## Workflow Completo

### 1. Gerar Contexto (Arquiteto)

Antes de criar um plano, o Arquiteto precisa conhecer o estado atual do repositório:

```powershell
python scripts\plans\generate_context_snapshot.py > scripts\plans\docs\context\context-2026-02-17.txt
```

**Saída:** Snapshot com:
- Estado do Git (branch, último commit, uncommitted files)
- Schema do banco (migrations, models)
- Estrutura de arquivos (app/models, routers, etc.)
- Dependências (requirements.txt)
- Invariantes documentadas
- Variáveis de ambiente necessárias

**Envie este arquivo junto com seu pedido ao Arquiteto.**

---

### 2. Criar Plano (Arquiteto)

O Arquiteto cria um arquivo Markdown seguindo o template:

```markdown
## 2.1 Cabeçalho do Plano
TASK-ID: FASE-5-3-ATHLETE-REGISTRATION
Status: RASCUNHO
...
```

Salvar em: `scripts/plans/docs/plans/FASE-5-3.md`

---

### 3. Aprovar Plano (Humano)

```powershell
# Ver status atual
python scripts\plans\plan_status.py scripts\plans\docs\plans\FASE-5-3.md

# Aprovar para execução
python scripts\plans\plan_status.py scripts\plans\docs\plans\FASE-5-3.md --set APROVADO
```

Status válidos: `RASCUNHO → EM_REVISAO → APROVADO → EXECUTADO`

---

### 4. Verificar Dependências (Opcional)

Se o plano faz parte de um DAG (grafo de dependências):

```powershell
# Validar o DAG
python scripts\plans\validate_dag.py scripts\plans\docs\fase-5-3-dag.yaml

# Verificar se pode executar agora
python scripts\plans\validate_dag.py scripts\plans\docs\fase-5-3-dag.yaml --can-execute FASE-5-3-B
```

---

### 5. Executar Workflow (Executor)

```powershell
# Workflow completo (dry-run → execute → validate → homolog)
python scripts\plans\executor_workflow.py scripts\plans\docs\plans\FASE-5-3.md
```

**O que acontece:**
1. **Pre-execution checks:**
   - Status do plano = `APROVADO`?
   - Arquivos livres de locks?
   - Git limpo ou esperado?
2. **Execution:**
   - Cria arquivos conforme seção 2.4.1
   - Modifica arquivos conforme seção 2.4.2
   - Gera migrations conforme seção 2.4.3
3. **Post-execution validation:**
   - `pytest` – todos os testes passam?
   - `ruff check .` – zero violations?
   - `mypy app/` – sem novos erros?
4. **Homologation:**
   - Manual: testar endpoints/funcionalidades
5. **Commit:**
   - Se tudo passou, commita automaticamente

---

### 6. Marcar como Executado (Humano)

Após validação e commit:

```powershell
python scripts\plans\plan_status.py scripts\plans\docs\plans\FASE-5-3.md --executed
```

Isso move o plano para `scripts/plans/docs/implemented/` e libera locks.

---

### 7. Registrar Métricas (Opcional)

Para medir ROI do fluxo:

```powershell
python scripts\plans\record_metrics.py FASE-5-3 `
    --plan-time 1.5 `
    --exec-time 0.5 `
    --homolog-time 0.3 `
    --bugs 0 `
    --rollbacks 0 `
    --rework 0

# Ver relatório
python scripts\plans\record_metrics.py --report
```

---

## Gerenciamento de Locks

Locks impedem conflitos quando múltiplos planos modificam os mesmos arquivos.

```powershell
# Listar todos os locks ativos
python scripts\plans\check_locks.py --list

# Adquirir locks para um plano
python scripts\plans\check_locks.py scripts\plans\docs\plans\FASE-5-3.md --acquire

# Liberar locks após execução
python scripts\plans\check_locks.py scripts\plans\docs\plans\FASE-5-3.md --release
```

**Locks no Plano:**
- **Exclusivo:** Somente 1 plano pode modificar o arquivo
- **Compartilhado:** Múltiplos planos podem ler

---

## Troubleshooting

### Erro: `ModuleNotFoundError: No module named 'config'`

**Causa:** Você tentou rodar o script de dentro de `scripts/plans/` ou seu `PYTHONPATH` está incorreto.

**Solução:**
```powershell
# Volte para a raiz
cd C:\HB TRACK

# Execute novamente
python scripts\plans\plan_status.py --list
```

---

### Erro: `FileNotFoundError: [Errno 2] No such file or directory: 'docs/plans'`

**Causa:** Script tentou acessar caminho relativo antigo (antes da refatoração).

**Solução:** Todos os scripts foram atualizados para usar `config.py`. Se ainda vê este erro, reporte o bug.

---

### Erro: `git: not a valid command` na VPS Linux

**Causa:** Git não está configurado com `user.email` e `user.name`.

**Solução:**
```bash
git config --global user.email "executor@hbtrack.com"
git config --global user.name "HB Track Executor"
```

---

### Comando funciona no Windows mas falha no Linux

**Causa:** Diferença de comandos shell (PowerShell vs Bash).

**Solução:** O `pathlib.Path` já cuida das barras (`\` vs `/`). Mas comandos shell precisam ser adaptados:
- Windows: `Get-ChildItem`
- Linux: `ls`

Para compatibilidade, use comandos Python puros quando possível.

---

## Portabilidade Windows ↔ Linux

Este sistema foi projetado para funcionar em ambos:

| Aspecto | Windows | Linux/VPS |
|---------|---------|-----------|
| **Caminhos** | `C:\HB TRACK\...` | `/home/user/HB TRACK/...` |
| **Conversão** | Automática via `pathlib.Path` | ✅ |
| **Comandos shell** | PowerShell | Bash |
| **Git** | `git.exe` | `git` |
| **Python** | `python` ou `py` | `python3` |

**Dica:** Na VPS, use `python3` explicitamente e crie um alias se necessário:
```bash
alias python=python3
```

---

## Comandos Principais (Referência Rápida)

```powershell
# Gerar contexto
python scripts\plans\generate_context_snapshot.py > scripts\plans\docs\context\context.txt

# Ver status de plano
python scripts\plans\plan_status.py scripts\plans\docs\plans\FASE-5-3.md

# Aprovar plano
python scripts\plans\plan_status.py scripts\plans\docs\plans\FASE-5-3.md --set APROVADO

# Executar workflow
python scripts\plans\executor_workflow.py scripts\plans\docs\plans\FASE-5-3.md

# Marcar como executado
python scripts\plans\plan_status.py scripts\plans\docs\plans\FASE-5-3.md --executed

# Listar locks
python scripts\plans\check_locks.py --list

# Validar DAG
python scripts\plans\validate_dag.py scripts\plans\docs\fase-5-3-dag.yaml --order

# Métricas
python scripts\plans\record_metrics.py --report
```

---

## Próximos Passos

1. **Criar primeiro plano:** Use `generate_context_snapshot.py` e envie ao Arquiteto
2. **Testar workflow:** Execute um plano simples end-to-end
3. **Automatizar CI/CD:** Integrar com GitHub Actions (futuro)
4. **Dashboard de métricas:** Visualizar ROI do fluxo (futuro)

---

## Manutenção

### Adicionar Novo Script

1. Crie em `scripts/plans/novo_script.py`
2. Importe de `config.py`:
   ```python
   from config import PROJECT_ROOT, PLANS_DIR, ...
   ```
3. Use caminhos absolutos: `PROJECT_ROOT / "caminho/relativo"`
4. Teste rodando da raiz: `python scripts\plans\novo_script.py`
5. Documente no README

### Modificar Estrutura de Diretórios

1. Edite `config.py` PRIMEIRO
2. Modifique os scripts que usam as constantes alteradas
3. Atualize este README
4. Crie migration guide se quebrar compatibilidade

---

**Documentação:** `scripts/plans/README.md`  
**Versão:** 1.0 (2026-02-17)  
**Autor:** HB Track Team
