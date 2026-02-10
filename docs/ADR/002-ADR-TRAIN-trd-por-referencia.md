# 002-ADR-TRAIN — TRD por Referência, Não por Duplicação

**Status:** Aceita
**Data:** 2026-02-08
**Autor:** Equipe HB Track
**Fase:** F2
**Módulos Afetados:** docs | backend

---

## Contexto

Duplicar schemas de banco ou contratos OpenAPI em documentação gera inconsistência e dificulta validação automática. Quando o TRD copia estruturas de tabelas ou payloads de endpoints, qualquer alteração no código cria drift imediato no documento.

O TRD do módulo Training já adota referências indiretas como padrão, mas esta decisão precisa ser formalizada para evitar regressão.

**Componentes Relacionados:**
- Documentação: `TRD_TRAINING.md` (80 operationIds referenciados)
- Artefatos gerados: `schema.sql`, `openapi.json`
- Modelo de dados: todas as tabelas do módulo Training

---

## Decisão

O TRD **não deve duplicar**:
- Estrutura de tabelas (DDL, colunas, tipos)
- Contratos OpenAPI (request/response bodies)
- Enums ou CHECK constraints

Toda referência deve ocorrer via:
- **`constraint_name`** para regras de banco (ex: `ck_training_sessions_focus_total_sum`)
- **`operationId`** para endpoints (ex: `createTrainingSession`)
- **JSON Pointer** para campos específicos de OpenAPI quando necessário

### Detalhes Técnicos

```markdown
# Exemplo de referência CORRETA no TRD:
"O total de focus não pode exceder 120% — ver `ck_training_sessions_focus_total_sum` em schema.sql"

# Exemplo de referência INCORRETA (duplicação):
"A tabela training_sessions tem as colunas: id UUID, status VARCHAR..."
```

---

## Alternativas Consideradas

### Alternativa 1: TRD como cópia integral do schema

**Prós:**
- Leitura standalone (sem precisar consultar outros arquivos)
- Mais acessível para quem não lê SQL

**Contras:**
- Drift garantido a cada migration
- Duplicação massiva (schema.sql tem 6000+ linhas)
- Impossível manter sincronizado manualmente

**Razão da rejeição:** O custo de manutenção é proibitivo e o drift é inevitável.

### Alternativa 2: Geração automática do TRD a partir do schema

**Prós:**
- Zero drift por construção
- Sempre atualizado

**Contras:**
- Perde contexto de negócio e justificativas
- TRD gerado não comunica "por quê", apenas "o quê"
- Complexidade tooling adicional

**Razão da rejeição:** TRD precisa de contexto humano; geração automática perde a dimensão explicativa.

---

## Consequências

### Positivas
- ✅ Redução de drift documental (TRD nunca desatualiza por mudança de schema)
- ✅ Possibilidade de verificação automática TRD ↔ OpenAPI ↔ DB via gates
- ✅ Menor risco de alucinação por IA (referências verificáveis, não texto copiado)

### Negativas
- ⚠️ Leitura do TRD requer acesso aos artefatos `_generated` para contexto completo
- ⚠️ Novos contribuidores precisam entender o padrão de referência indireta

### Neutras
- ℹ️ TRD passa a ser um documento de "por quê" e "como", não de "o quê está no banco"

---

## Validação

### Critérios de Conformidade
- [x] TRD usa `operationId` para referenciar endpoints (80 referenciados)
- [x] TRD usa `constraint_name` para referenciar regras de banco
- [x] Nenhuma DDL duplicada no TRD

---

## Referências

- `docs/TRD_TRAINING.md`: referências explícitas por `operationId`
- `docs/PRD_BASELINE_ASIS_TRAINING.md`: dependência de artefatos `_generated`
- ADRs relacionados: ADR-TRAIN-001 (SSOT), ADR-TRAIN-008 (governança por artefatos)

---

## Revisões

| Data | Autor | Mudança | Versão |
|------|-------|---------|--------|
| 2026-02-08 | Equipe HB Track | Criação inicial | 1.0 |
| 2026-02-08 | Equipe HB Track | Adequação ao template padrão ADR | 1.1 |
