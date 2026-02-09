# 001-ADR-TRAIN — Fonte de Verdade e Precedência de Regras (SSOT)

**Status:** Aceita
**Data:** 2026-02-08
**Autor:** Equipe HB Track
**Fase:** F2
**Módulos Afetados:** backend | database | docs

---

## Contexto

O módulo Training possui múltiplas representações do domínio: banco de dados (constraints, triggers, enums), camada de serviços (validações Python), contratos OpenAPI e documentação manual (TRD, PRD, Invariantes).

Sem uma hierarquia explícita de precedência, surgem inconsistências, drift documental e alucinação por agentes automatizados. O risco principal é que uma regra exista apenas em texto e nunca seja imposta por código.

**Componentes Relacionados:**
- Modelo de dados: Training Sessions, Athletes, Teams, Attendance
- Artefatos gerados: `schema.sql`, `openapi.json`, `alembic_state.txt`, `manifest.json`
- Documentação: `TRD_TRAINING.md`, `PRD_BASELINE_ASIS_TRAINING.md`, `INVARIANTS_TRAINING.md`

---

## Decisão

Definir a seguinte ordem de precedência como **fonte de verdade canônica (SSOT)**:

1. **Database constraints** (CHECK, FK, UNIQUE, triggers) — verdade absoluta
2. **Service validations** (Python/FastAPI) — regras de negócio não expressáveis em DB
3. **OpenAPI contracts** (schema, endpoints) — contrato de interface
4. **Documentação manual** (TRD, PRD, Invariantes) — descrição derivada

Se houver conflito entre camadas, a camada superior prevalece.

### Detalhes Técnicos

```
Hierarquia de resolução de conflitos:

  DB constraint  →  prevalece sobre tudo
       ↑
  Service logic  →  prevalece sobre OpenAPI e docs
       ↑
  OpenAPI schema →  prevalece sobre docs
       ↑
  Docs (TRD/PRD) →  derivados, nunca autoritativos sozinhos
```

**Stack envolvida:**
- Database: PostgreSQL (Neon) — constraints como `ck_*`, triggers como `tr_*`
- Backend: FastAPI, SQLAlchemy — validações de serviço
- Docs: Markdown com referências por `constraint_name` e `operationId`

---

## Alternativas Consideradas

### Alternativa 1: Documentação como fonte primária

**Prós:**
- Mais acessível para stakeholders não-técnicos
- Mais fácil de editar

**Contras:**
- Drift inevitável entre docs e código real
- Impossível de validar automaticamente
- Agentes IA alucinam regras baseados em texto desatualizado

**Razão da rejeição:** O drift documental já causou inconsistências. Regras não impostas por código são regras que não existem.

### Alternativa 2: Código como única fonte (sem docs)

**Prós:**
- Zero drift por definição
- Tudo verificável

**Contras:**
- Dificulta onboarding e comunicação
- Regras de negócio complexas ficam opacas
- Sem contrato explícito para agentes

**Razão da rejeição:** Documentação é necessária como descrição derivada, desde que não seja autoritativa.

---

## Consequências

### Positivas
- ✅ Nenhuma regra pode existir apenas em documentação sem enforcement real
- ✅ Mudanças reais refletem primeiro no DB ou no serviço
- ✅ Agentes IA validam contra artefatos gerados, não contra texto livre
- ✅ Verificação automática de alinhamento TRD ↔ schema ↔ OpenAPI

### Negativas
- ⚠️ Exige disciplina: toda mudança documental deve ser precedida por mudança de código
- ⚠️ Complexidade adicional no fluxo de atualização

### Neutras
- ℹ️ Documentação passa a ser "read-only derivada" em vez de "fonte editável"

---

## Validação

### Critérios de Conformidade
- [x] Alinhamento com PRD (`PRD_BASELINE_ASIS_TRAINING.md`: governança por artefatos)
- [x] Artefatos `_generated` exigidos antes de mudanças documentais
- [x] Gates automáticos validam schema ↔ models (scripts `parity_gate.ps1`, `agent_guard.py`)

---

## Referências

- `docs/_MAPA_DE_CONTEXTO.md`: definição explícita das fontes canônicas
- `docs/TRD_TRAINING.md`: uso de `constraint_name` e `operationId` como âncoras
- `docs/PRD_BASELINE_ASIS_TRAINING.md`: governança baseada em artefatos gerados
- ADRs relacionados: ADR-TRAIN-002, ADR-TRAIN-008

---

## Revisões

| Data | Autor | Mudança | Versão |
|------|-------|---------|--------|
| 2026-02-08 | Equipe HB Track | Criação inicial | 1.0 |
| 2026-02-08 | Equipe HB Track | Adequação ao template padrão ADR | 1.1 |
