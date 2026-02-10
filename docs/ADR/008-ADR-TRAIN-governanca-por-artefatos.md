# 008-ADR-TRAIN — Governança por Artefatos Gerados

**Status:** Aceita
**Data:** 2026-02-08
**Autor:** Equipe HB Track
**Fase:** F2
**Módulos Afetados:** backend | database | docs

---

## Contexto

A verdade do sistema não está nos textos documentais, mas nos artefatos reais produzidos pelo código. Quando documentação é atualizada sem regenerar artefatos, surge drift entre o que o código faz e o que a documentação diz.

O projeto possui scripts de gate (`parity_gate.ps1`, `agent_guard.py`, `models_autogen_gate.ps1`) que validam alinhamento entre código e artefatos.

**Componentes Relacionados:**
- Artefatos gerados: `schema.sql`, `openapi.json`, `alembic_state.txt`, `manifest.json`
- Scripts de gate: `scripts/parity_gate.ps1`, `scripts/agent_guard.py`, `scripts/models_autogen_gate.ps1`
- Documentação: `TRD_TRAINING.md`, `INVARIANTS_TRAINING.md`, `PRD_BASELINE_ASIS_TRAINING.md`

---

## Decisão

Artefatos `_generated` são **obrigatórios** antes de:
- Atualizar documentação (TRD, PRD, Invariantes)
- Aceitar PRs que modifiquem schema, models ou endpoints
- Promover invariantes para status "accepted"

### Artefatos mínimos obrigatórios:
| Artefato | Fonte | Conteúdo |
|----------|-------|----------|
| `schema.sql` | `pg_dump --schema-only` | DDL completo do banco |
| `openapi.json` | FastAPI auto-generated | Contrato de API |
| `alembic_state.txt` | `alembic heads` / `alembic history` | Estado das migrations |
| `manifest.json` | Script de geração | Checksums e metadata |

### Detalhes Técnicos

```
Fluxo de governança:

  1. Desenvolvedor altera código (model, router, migration)
  2. Roda scripts de geração → atualiza _generated/
  3. Roda gates de validação → verifica alinhamento
  4. Se gates passam → pode atualizar docs e abrir PR
  5. Se gates falham → corrige código antes de prosseguir
```

```powershell
# Exemplo: parity_gate.ps1 valida schema ↔ models
# Exemplo: agent_guard.py impede operações sem artefatos atualizados
```

---

## Alternativas Consideradas

### Alternativa 1: Documentação manual sem gates

**Prós:**
- Fluxo mais simples
- Sem dependência de scripts

**Contras:**
- Drift inevitável e silencioso
- Sem garantia de alinhamento
- Agentes IA trabalham com informação desatualizada

**Razão da rejeição:** O drift silencioso já causou problemas. A governança automatizada é necessária.

### Alternativa 2: Geração automática em CI/CD (sem gates locais)

**Prós:**
- Artefatos sempre atualizados no pipeline
- Sem fricção local para o desenvolvedor

**Contras:**
- Feedback tardio (só descobre drift no CI, não localmente)
- PR já foi aberto quando o gate falha
- Sem proteção para agentes que rodam localmente

**Razão da rejeição:** Gates locais dão feedback imediato. CI/CD complementa, mas não substitui validação local.

---

## Consequências

### Positivas
- ✅ Fluxo determinístico: código → artefatos → docs → PR
- ✅ Documentação sempre alinhada ao código real
- ✅ Base confiável para agentes IA (artefatos são ground truth)
- ✅ Gates bloqueiam PRs com drift antes do review humano

### Negativas
- ⚠️ Fricção adicional no fluxo de desenvolvimento (rodar scripts antes de PR)
- ⚠️ Scripts de gate precisam de manutenção quando schema evolui

### Neutras
- ℹ️ Artefatos `_generated/` são commitados no repositório (versionados junto com código)

---

## Validação

### Critérios de Conformidade
- [x] 4 artefatos mínimos presentes em `_generated/`
- [x] Scripts de gate funcionais: `parity_gate.ps1`, `agent_guard.py`, `models_autogen_gate.ps1`
- [x] Fluxo documentado: código → artefatos → docs → PR

---

## Referências

- `docs/PRD_BASELINE_ASIS_TRAINING.md`: checksums e governança
- `docs/_MAPA_DE_CONTEXTO.md`: instrução explícita sobre artefatos
- `Hb Track - Backend/scripts/parity_gate.ps1`: gate de paridade schema ↔ models
- `Hb Track - Backend/scripts/agent_guard.py`: guard para agentes IA
- `Hb Track - Backend/scripts/models_autogen_gate.ps1`: gate de autogen
- ADRs relacionados: ADR-TRAIN-001 (SSOT), ADR-TRAIN-002 (referência, não duplicação)

---

## Revisões

| Data | Autor | Mudança | Versão |
|------|-------|---------|--------|
| 2026-02-08 | Equipe HB Track | Criação inicial | 1.0 |
| 2026-02-08 | Equipe HB Track | Adequação ao template padrão ADR com evidências de scripts | 1.1 |
