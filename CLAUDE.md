# HB TRACK — Claude Instructions

> Instruções canônicas em `docs/_canon/AGENT_INSTRUCTIONS.md` — ler esse arquivo primeiro.

## Boot mínimo
1. Ler `docs/_canon/AGENT_INSTRUCTIONS.md` (este arquivo é apenas um ponteiro)
2. Se existir `SESSION_HANDOFF.md` na raiz → ler ANTES de qualquer outra coisa
3. Regras detalhadas: `.contract_driven/CONTRACT_SYSTEM_RULES.md`

## Resumo rápido
- **Produto:** HB Track — plataforma de gestão esportiva para handebol
- **Metodologia:** CDD (Contract-Driven Development) — contratos são SSOT antes de código
- **Humano:** leigo em desenvolvimento — comunicar em linguagem de produto, nunca jargão
- **16 módulos canônicos** → ver `docs/_canon/MODULE_REGISTRY.yaml`
- **9 task types → workers** → ver `.contract_driven/TASK_CATALOG.yaml`
- **Pipeline obrigatório:** `hb verify` antes de tarefas de contrato; `hb artifact <path>` após artefato canônico
