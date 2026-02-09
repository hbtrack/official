# 004-ADR-TRAIN — Invariantes como Contrato Testável do Domínio

**Status:** Aceita
**Data:** 2026-02-08
**Autor:** Equipe HB Track
**Fase:** F2
**Módulos Afetados:** backend | database | docs

---

## Contexto

Regras críticas do domínio Training não podem depender apenas de interpretação humana ou documentação narrativa. Quando uma regra existe apenas em texto (TRD/PRD), ela não é executável, não é testável e está sujeita a regressão silenciosa.

O módulo Training possui 51 invariantes (INV-TRAIN-001 a INV-TRAIN-051) que expressam restrições de negócio verificáveis.

**Componentes Relacionados:**
- Documentação: `INVARIANTS_TRAINING.md` (51 invariantes com SPEC blocks)
- Testing canon: `INVARIANTS_TESTING_CANON.md`
- Artefatos: `schema.sql` (constraints), `openapi.json` (contratos)
- Testes: `tests/invariants/` (1 arquivo por invariante)

---

## Decisão

Toda regra estrutural ou comportamental crítica do módulo Training **deve** ser expressa como:

1. **Invariante formal** com ID único (INV-TRAIN-NNN)
2. **SPEC block** machine-parseable (YAML v1.0)
3. **Teste automatizado** em `tests/invariants/test_inv_train_NNN_<slug>.py`
4. **Evidência rastreável** ancorada em artefato real (`constraint_name`, `operationId`, `file:line`)

### Detalhes Técnicos

```yaml
# Exemplo de SPEC block (INVARIANTS_TRAINING.md)
# SPEC:
#   id: INV-TRAIN-037
#   class: A
#   evidence:
#     - schema.sql: ck_training_sessions_focus_total_sum
#   test: tests/invariants/test_inv_train_037_focus_total.py
```

### Classificação por classe:
| Classe | Descrição | Camada de teste |
|--------|-----------|-----------------|
| A | DB Constraint | Runtime Integration |
| B | Trigger/Function | Runtime Integration |
| C1 | Service puro | Unit sem IO |
| C2 | Service + DB | Integration |
| D | Router/RBAC | API test |
| E1/E2 | Celery | Chamada direta |
| F | OpenAPI | Contract test |

---

## Alternativas Consideradas

### Alternativa 1: Regras apenas em documentação narrativa

**Prós:**
- Mais fácil de escrever e ler
- Sem overhead de testes

**Contras:**
- Não verificável automaticamente
- Regressões silenciosas
- Agentes IA interpretam em vez de validar

**Razão da rejeição:** Documentação narrativa não impede regressão. Regras não testadas são regras que eventualmente se quebram.

### Alternativa 2: Testes sem formalização de invariantes

**Prós:**
- Testes já existem no repositório
- Sem burocracia documental

**Contras:**
- Sem mapeamento claro entre regra de negócio e teste
- Difícil auditar cobertura de regras
- Sem SPEC machine-parseable para gates

**Razão da rejeição:** Testes sem invariantes formais são difíceis de rastrear e auditar. O mapeamento 1:1 (invariante → teste) é essencial para governança.

---

## Consequências

### Positivas
- ✅ Gates automáticos podem bloquear regressões antes do merge
- ✅ O agente valida regras contra evidências, não interpreta texto
- ✅ Documentação de regras passa a ser executável
- ✅ Mapeamento 1:1 invariante → teste facilita auditoria

### Negativas
- ⚠️ Overhead de manutenção: cada nova regra exige INV + SPEC + teste
- ⚠️ Curva de aprendizado para o protocolo de testing canon

### Neutras
- ℹ️ Invariantes são documentação derivada (SSOT permanece no DB/service per ADR-TRAIN-001)

---

## Validação

### Critérios de Conformidade
- [x] 51 invariantes formalizadas em `INVARIANTS_TRAINING.md`
- [x] SPEC blocks em formato YAML v1.0
- [x] Testing canon documentado em `INVARIANTS_TESTING_CANON.md`
- [x] Diretório `tests/invariants/` designado para testes 1:1

---

## Referências

- `docs/INVARIANTS_TRAINING.md`: 51 invariantes com SPEC blocks
- `docs/INVARIANTS_TESTING_CANON.md`: protocolo de testes
- `docs/TRD_TRAINING.md`: referências cruzadas a invariantes
- ADRs relacionados: ADR-TRAIN-001 (SSOT), ADR-TRAIN-008 (governança por artefatos)

---

## Revisões

| Data | Autor | Mudança | Versão |
|------|-------|---------|--------|
| 2026-02-08 | Equipe HB Track | Criação inicial | 1.0 |
| 2026-02-08 | Equipe HB Track | Adequação ao template padrão ADR | 1.1 |
