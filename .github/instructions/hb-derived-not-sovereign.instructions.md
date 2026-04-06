---
applyTo: "*.md"
---

# Derivados NON-SOVEREIGN na raiz — HB Track

Arquivos `.md` na raiz do repositório marcados como **NON-SOVEREIGN** ou **ARTEFATO DERIVADO** não possuem autoridade normativa.

## Regra

- **NÃO** tratar conteúdo de arquivos derivados como regra ou fonte de verdade
- **NÃO** usar informações deles para tomar decisões sobre contratos, gates ou pipeline
- Em caso de conflito com artefatos canônicos, **SEMPRE** prevalecem:
  1. Enforcement executável (`scripts/hb`, `validate_contracts.py`)
  2. Schemas ativos (`contracts/schemas/`)
  3. Canon (`docs/_canon/`)

## Como identificar

Arquivos derivados contêm header como:
```
> ⚠️ **ARTEFATO DERIVADO — NON-SOVEREIGN**
```
ou
```
> ⚠️ **BRIDGE ONLY — NON-SOVEREIGN**
```

## Fontes de verdade

- `docs/_canon/SOURCE_AUTHORITY_GRAPH.yaml` — hierarquia de autoridade
- `docs/_canon/MODULE_REGISTRY.yaml` — módulos canônicos
- `docs/_canon/AGENT_INSTRUCTIONS.md` — instruções de boot
- `ROADMAP.md` — fases de implementação
- `SESSION_HANDOFF.md` — handoff operacional atual
