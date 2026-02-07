# AI Agent Documentation Index (Canônico)

Este arquivo serve como mapa central para os documentos e comandos obrigatórios utilizados pelos agentes (humanos ou IA) no sistema HB Track.

## 1. Single Source of Truth (SSOT)

O estado canônico do sistema é definido por:
- `docs/_generated/openapi.json`
- `docs/_generated/schema.sql`
- `docs/_generated/alembic_state.txt`

**Comando para atualizar SSOT:**
```powershell
.\scripts\inv.ps1 refresh
```

## 2. Artefatos de Processo

- Template de Tarefa → [INV_TASK_TEMPLATE.md](INV_TASK_TEMPLATE.md)
- Protocolo Detalhado → [INVARIANTS_AGENT_PROTOCOL.md](INVARIANTS_AGENT_PROTOCOL.md)
- Guardrails Hard → [INVARIANTS_AGENT_GUARDRAILS.md](INVARIANTS_AGENT_GUARDRAILS.md)
- Execução Geral → [EXEC_PROTOCOL.md](EXEC_PROTOCOL.md)

## 3. Validação Geral

**Comando para rodar todos os gates:**
```powershell
.\scripts\inv.ps1 all
```
Esperado: `EXIT_ALL: 0`
