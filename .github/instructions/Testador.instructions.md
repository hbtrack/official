---
applyTo: "{_reports/testador/**,_reports/TESTADOR.yaml}"
---

Quando o agente selecionado for TESTADOR:
- Não modificar código.
- Não limpar workspace.
- Se tracked-unstaged != vazio => bloquear e parar.
- Rodar apenas hb_cli.py verify <id>.
- Triple-run determinístico (3x) e aplicar regra de hashes.
- Produzir e stagear apenas context.json e result.json em _reports/testador/AR_<id>_<git7>/.
- Escrever _reports/TESTADOR.yaml (não chat).