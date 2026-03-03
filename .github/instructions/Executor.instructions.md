---
applyTo: "{Hb Track - Backend/**,Hb Track - Frontend/**,docs/hbtrack/evidence/**,docs/hbtrack/ars/**,_reports/EXECUTOR.md}"
---

Quando o agente selecionado for EXECUTOR:
- Implementar apenas dentro do write_scope da AR.
- Preencher “Análise de Impacto” antes do código.
- Rodar hb_cli.py report <id> "<validation_command>".
- Evidência canônica obrigatória: docs/hbtrack/evidence/AR_<id>/executor_main.log.
- Não executar verify/seal.
- Workspace clean pré-verify é responsabilidade do Executor (sem comandos destrutivos).
- Escrever _reports/EXECUTOR.md (não commit).