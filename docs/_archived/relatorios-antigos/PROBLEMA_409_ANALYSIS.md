<!-- STATUS: DEPRECATED | arquivado -->

# Análise Completa: Erro 409 DATABASE_CONSTRAINT_VIOLATION

**Data**: 2026-01-12
**Status**: 🔍 DIAGNOSTICADO - SOLUÇÃO IDENTIFICADA

---

## Resumo Executivo

**Erro**: `409 - DATABASE_CONSTRAINT_VIOLATION` ao criar training sessions via API
**Causa Raiz**: Team base E2E (ID: `88888888-8888-8888-8888-888888888888`) **NÃO EXISTE** no banco
**Evidência**: GET `/api/v1/teams/88888888-8888-8888-8888-888888888888` retorna **404 NOT_FOUND**

---

## Cronologia do Problema

### 1. Problema Original (Run 5 - 18:02)
- **Erro**: 409 ao criar training session
- **Hipótese**: Faltavam team_memberships no seed
- **Ação**: Adicionada função `seed_e2e_team_memberships()` ao seed_e2e.py
- **Resultado**: Seed rodou com sucesso, criou 6 team_memberships

### 2. Problema Persistente (Run 6 - 18:13)
- **Erro**: 409 continua mesmo após seed corrigido
- **Hipótese**: Backend não reconhece mudanças (cache)
- **Investigação**: Teste direto na API

### 3. Descoberta (Análise Atual)
- **GET** `/api/v1/teams/88888888-8888-8888-8888-888888888888` → **404**
- **Seed Output**: "OK Equipe base E2E: **e2e00000-0000-0000-0004-000000000001**"
- **Conclusão**: O seed está criando team com ID **DIFERENTE** do esperado pelos testes!

---

## IDs Esperados vs IDs Reais

### IDs Esperados pelos Testes

**Arquivo**: `tests/e2e/shared-data.ts`

```typescript
export const SEED_TEAM_ID = '88888888-8888-8888-8888-888888888888'
export const SEED_ORG_ID = '88888888-8888-8888-8888-888888888888'
```

### IDs Gerados pelo Seed

**Arquivo**: `scripts/seed_e2e.py`

```python
# Organização E2E
E2E_ORG_ID = uuid.UUID('e2e00000-0000-0000-0000-000000000001')

# Team base E2E
E2E_TEAM_BASE_ID = uuid.UUID('e2e00000-0000-0000-0004-000000000001')
```

### ❌ MISMATCH CRÍTICO

| Recurso | Esperado pelo Teste | Gerado pelo Seed | Match? |
|---------|-------------------|------------------|--------|
| **Organization** | `88888888-8888-8888-8888-888888888888` | `e2e00000-0000-0000-0000-000000000001` | ❌ |
| **Team** | `88888888-8888-8888-8888-888888888888` | `e2e00000-0000-0000-0004-000000000001` | ❌ |

---

## Por Que o Erro é 409 (Conflict) e Não 404 (Not Found)?

### Fluxo do Erro

1. **Teste chama**: `createSessionViaAPI({ team_id: '88888888-...' })`
2. **Helper busca team**: `getTeamViaAPI('88888888-...')` → **404**
3. **Helper falha silenciosamente**: `organizationId` fica `undefined`
4. **POST** `/training-sessions` com:
   ```json
   {
     "team_id": "88888888-8888-8888-8888-888888888888",  // ❌ Não existe
     "organization_id": null,                              // ❌ Undefined virou null
     "session_at": "2026-01-13T10:00:00Z",
     "session_type": "tecnico",
     "main_objective": "Treino E2E"
   }
   ```
5. **Backend valida**: Foreign Key `team_id` → `teams.id` **INVÁLIDA**
6. **PostgreSQL error**: `23503` (Foreign Key Violation)
7. **Handler mapeia**: 23503 → **422 ou 409** dependendo do handler

**Por que 409?**
O handler global em `main.py:203-250` captura `IntegrityError` e retorna **409 CONFLICT** genérico para todas as violações de integridade, sem distinguir entre FK (que deveria ser 422) e UNIQUE (que deveria ser 409).

---

## Arquivos com IDs Hardcoded

### Frontend (Testes E2E)

1. **tests/e2e/shared-data.ts** (linhas 22-23)
   ```typescript
   export const SEED_TEAM_ID = '88888888-8888-8888-8888-888888888888'
   export const SEED_ORG_ID = '88888888-8888-8888-8888-888888888888'
   ```

2. **tests/e2e/teams/teams.contract.spec.ts** (linha 50)
   ```typescript
   const teamId = '88888888-8888-8888-8888-888888888888';
   ```

3. **tests/e2e/teams/teams.trainings.spec.ts** (linha 48)
   ```typescript
   const teamId = '88888888-8888-8888-8888-888888888888';
   ```

4. **tests/e2e/smoke-tests.spec.ts** (linha 67)
   ```typescript
   const teamId = '88888888-8888-8888-8888-888888888888';
   ```

### Backend (Seed E2E)

5. **scripts/seed_e2e.py** (linhas 30-36)
   ```python
   E2E_ORG_ID = uuid.UUID('e2e00000-0000-0000-0000-000000000001')
   E2E_ORG_NAME = 'Org E2E'
   E2E_TEAM_BASE_ID = uuid.UUID('e2e00000-0000-0000-0004-000000000001')
   E2E_TEAM_BASE_NAME = 'Team Base E2E'
   ```

---

## Soluções Possíveis

### Opção 1: Atualizar Seed para Usar IDs dos Testes ✅ RECOMENDADO

**Vantagem**: Menos mudanças, apenas 1 arquivo
**Desvantagem**: IDs "88888888-..." são menos semânticos

**Mudança no seed_e2e.py**:
```python
# ANTES
E2E_ORG_ID = uuid.UUID('e2e00000-0000-0000-0000-000000000001')
E2E_TEAM_BASE_ID = uuid.UUID('e2e00000-0000-0000-0004-000000000001')

# DEPOIS
E2E_ORG_ID = uuid.UUID('88888888-8888-8888-8888-888888888888')
E2E_TEAM_BASE_ID = uuid.UUID('88888888-8888-8888-8888-888888888888')
```

**PROBLEMA**: Org e Team com **MESMO ID** causará conflito de FK!

### Opção 2: Atualizar Testes para Usar IDs do Seed ⚠️ ALTERNATIVA

**Vantagem**: IDs "e2e00000-..." são mais semânticos
**Desvantagem**: Precisa mudar 4 arquivos de teste

**Mudança em shared-data.ts**:
```typescript
// ANTES
export const SEED_TEAM_ID = '88888888-8888-8888-8888-888888888888'
export const SEED_ORG_ID = '88888888-8888-8888-8888-888888888888'

// DEPOIS
export const SEED_TEAM_ID = 'e2e00000-0000-0000-0004-000000000001'
export const SEED_ORG_ID = 'e2e00000-0000-0000-0000-000000000001'
```

### Opção 3: Usar IDs Distintos para Org e Team ✅✅ MELHOR SOLUÇÃO

**Seed E2E**:
```python
E2E_ORG_ID = uuid.UUID('88888888-8888-8888-8888-000000000001')  # Org
E2E_TEAM_BASE_ID = uuid.UUID('88888888-8888-8888-8888-000000000002')  # Team
```

**Testes (shared-data.ts)**:
```typescript
export const SEED_ORG_ID = '88888888-8888-8888-8888-000000000001'
export const SEED_TEAM_ID = '88888888-8888-8888-8888-000000000002'
```

**Vantagens**:
- IDs consistentes entre seed e testes
- IDs distintos para Org e Team (evita conflitos)
- Padrão "88888888-..." é reconhecível como E2E
- Sufixos diferentes (001, 002) identificam cada recurso

---

## Ações Imediatas

### 1. Corrigir IDs no Seed E2E

**Arquivo**: `scripts/seed_e2e.py`

```python
# Linha 30-36: SUBSTITUIR
E2E_ORG_ID = uuid.UUID('88888888-8888-8888-8888-000000000001')
E2E_ORG_NAME = 'Org E2E'

E2E_TEAM_BASE_ID = uuid.UUID('88888888-8888-8888-8888-000000000002')
E2E_TEAM_BASE_NAME = 'Team Base E2E'
```

### 2. Atualizar IDs nos Testes

**Arquivo**: `tests/e2e/shared-data.ts`

```typescript
// Linha 22-23: SUBSTITUIR
export const SEED_ORG_ID = '88888888-8888-8888-8888-000000000001'
export const SEED_TEAM_ID = '88888888-8888-8888-8888-000000000002'
```

### 3. Re-executar Seed e Testes

```powershell
# 1. Reset + Seed E2E
cd "c:\HB TRACK\Hb Track - Backend"
.\reset-db-e2e.ps1

# 2. Verificar team criado
curl http://localhost:8000/api/v1/teams/88888888-8888-8888-8888-000000000002

# 3. Re-executar testes
cd "c:\HB TRACK\Hb Track - Fronted"
npx playwright test tests/e2e/teams/teams.trainings.spec.ts --project=chromium --workers=1
```

---

## Validação Final

### Checklist de Correção

- [ ] IDs corrigidos no seed_e2e.py
- [ ] IDs corrigidos no shared-data.ts
- [ ] Seed E2E executado com sucesso
- [ ] GET `/api/v1/teams/88888888-8888-8888-8888-000000000002` retorna 200
- [ ] Testes de training sessions passam (3/3)
- [ ] Run 7 documentado no RUN_LOG.md

---

## Lições Aprendidas

1. **Sempre verificar consistência de IDs** entre seed e testes
2. **Hardcoded IDs devem estar centralizados** (shared-data.ts)
3. **Mensagens de erro genéricas (409)** dificultam debug - melhorar handlers
4. **Seed deve logar IDs gerados** para facilitar troubleshooting
5. **Testes devem validar pré-requisitos** (team existe?) antes de criar recursos

---

**Status**: 🎯 SOLUÇÃO PRONTA PARA IMPLEMENTAÇÃO
