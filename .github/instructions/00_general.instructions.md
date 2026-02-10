---
description: "Carregar para qualquer tarefa no repositório HB Track. Sempre iniciar pela documentação canônica (00_START_HERE.md) e respeitar SSOT/Authority."
applyTo: "**"
---

Regras globais:
- Porta única: ler primeiro `docs/_canon/00_START_HERE.md`.
- SSOT estrutural de DB: `Hb Track - Backend/docs/_generated/schema.sql` (gerado por `scripts/inv.ps1 refresh`).
- Não inventar: decisões devem citar paths/outputs reais.
- Não criar arquivos temporários/backups dentro do repo.
- Capturar `$LASTEXITCODE` imediatamente após comandos (sem pipeline antes).

Regras críticas: CWD, stop-on-first-failure, sem temporários, capturar $LASTEXITCODE, snapshot só com autorização.