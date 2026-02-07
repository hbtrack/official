<!-- STATUS: DEPRECATED | implementacao concluida -->

# Integração teams_gaps → Estrutura Canônica

## Status: ✅ COMPLETO

Data: 2026-01-11

## Resumo Executivo

A pasta `teams_gaps` foi **eliminada** e seu conteúdo integrado à estrutura canônica conforme ordem:

```
GATE → SETUP → CONTRATO → FUNCIONAIS
```

## Arquivos Criados (Novos Specs Funcionais)

| Origem (gap) | Destino (canônico) | Motivo |
|--------------|-------------------|--------|
| `01.trainings.spec.ts` | `teams/teams.trainings.spec.ts` | ✅ Aba trainings não existia |
| `02.stats.spec.ts` | `teams/teams.stats.spec.ts` | ✅ Aba stats não existia |
| `09.athletes-registrations.spec.ts` | `teams/teams.athletes.spec.ts` | ✅ Registrations não existiam |

## Arquivos Não Migrados (Duplicados ou Supérfluos)

| Arquivo gap | Razão para NÃO migrar |
|-------------|----------------------|
| `03.members-management.spec.ts` | Cobertura já existe em `teams.crud.spec.ts` (seção Members) e `teams.rbac.spec.ts` |
| `04.empty-states.spec.ts` | Cobertura já existe em `teams.states.spec.ts` |
| `05.testids-coverage.spec.ts` | Cobertura já existe em `teams.contract.spec.ts` (seção E: Marcadores estáveis) |
| `06.rbac-extended.spec.ts` | Cobertura já existe em `teams.rbac.spec.ts` |
| `07.team-card-actions.spec.ts` | Cobertura já existe em `teams.crud.spec.ts` (Read, Delete) e `teams.contract.spec.ts` |
| `08.navigation-deep.spec.ts` | Cobertura parcial existe em `teams.contract.spec.ts` (redirects, 404, deep links overview/members/settings). Deep links trainings/stats foram criados nos novos specs. |

## Análise de Duplicatas

### Testes Duplicados (Mantidos no Canônico)

| Teste | Gap | Canônico |
|-------|-----|----------|
| team-card-${id} visível | 05.testids-coverage | teams.crud.spec.ts (Read) |
| view-team-${id} navegação | 07.team-card-actions | teams.crud.spec.ts (Read) |
| create-team-modal abre | 05.testids-coverage | teams.crud.spec.ts (Create) |
| invite-member-modal abre | 05.testids-coverage | teams.crud.spec.ts (Members) |
| Empty state treinos | 04.empty-states | teams.trainings.spec.ts |
| Admin vê botão convidar | 06.rbac-extended | teams.rbac.spec.ts |
| Deep link /teams/:id/overview | 08.navigation-deep | teams.contract.spec.ts |
| Deep link /teams/:id/members | 08.navigation-deep | teams.contract.spec.ts |
| Deep link /teams/:id/settings | 08.navigation-deep | teams.contract.spec.ts |
| F5 preserva URL | 08.navigation-deep | **NÃO COBERTO** (decisão: não crítico) |
| Browser back/forward | 08.navigation-deep | **NÃO COBERTO** (decisão: não crítico) |

### Testes Novos (Adicionados)

| Teste | Spec Canônico | Origem |
|-------|---------------|--------|
| Aba trainings root testid | teams.trainings.spec.ts | 01.trainings.spec.ts |
| Treino criado via API aparece | teams.trainings.spec.ts | 01.trainings.spec.ts |
| Aba stats root testid | teams.stats.spec.ts | 02.stats.spec.ts |
| Stats: navegação Overview ↔ Stats | teams.stats.spec.ts | 02.stats.spec.ts |
| Athletes: GET registrations | teams.athletes.spec.ts | 09.athletes-registrations.spec.ts |
| Athletes: POST registration | teams.athletes.spec.ts | 09.athletes-registrations.spec.ts |
| Athletes: UI lista atletas | teams.athletes.spec.ts | 09.athletes-registrations.spec.ts |

## Estrutura Final (Ordem Canônica)

### GATE
- `health.gate.spec.ts`

### SETUP
- `setup/auth.setup.ts`

### CONTRATO
- `teams/teams.contract.spec.ts`

### FUNCIONAIS
1. `teams/teams.auth.spec.ts`
2. `teams/teams.crud.spec.ts`
3. `teams/teams.states.spec.ts`
4. `teams/teams.rbac.spec.ts`
5. `teams/teams.welcome.spec.ts`
6. `teams/teams.routing.spec.ts`
7. `teams/teams.invites.spec.ts`
8. `teams/teams.trainings.spec.ts` ← **NOVO**
9. `teams/teams.stats.spec.ts` ← **NOVO**
10. `teams/teams.athletes.spec.ts` ← **NOVO**

## Comandos de Execução (Ordem Correta)

```powershell
# 1. GATE
npx playwright test tests/e2e/health.gate.spec.ts --project=chromium --workers=1 --retries=0

# 2. SETUP
npx playwright test tests/e2e/setup/auth.setup.ts --project=setup --workers=1 --retries=0

# 3. CONTRATO
npx playwright test tests/e2e/teams/teams.contract.spec.ts --project=chromium --workers=1 --retries=0

# 4. FUNCIONAIS (um por vez, na ordem)
npx playwright test tests/e2e/teams/teams.auth.spec.ts --project=chromium --workers=1 --retries=0
npx playwright test tests/e2e/teams/teams.crud.spec.ts --project=chromium --workers=1 --retries=0
npx playwright test tests/e2e/teams/teams.states.spec.ts --project=chromium --workers=1 --retries=0
npx playwright test tests/e2e/teams/teams.rbac.spec.ts --project=chromium --workers=1 --retries=0
npx playwright test tests/e2e/teams/teams.welcome.spec.ts --project=chromium --workers=1 --retries=0
npx playwright test tests/e2e/teams/teams.routing.spec.ts --project=chromium --workers=1 --retries=0
npx playwright test tests/e2e/teams/teams.invites.spec.ts --project=chromium --workers=1 --retries=0
npx playwright test tests/e2e/teams/teams.trainings.spec.ts --project=chromium --workers=1 --retries=0
npx playwright test tests/e2e/teams/teams.stats.spec.ts --project=chromium --workers=1 --retries=0
npx playwright test tests/e2e/teams/teams.athletes.spec.ts --project=chromium --workers=1 --retries=0
```

## Decisões Tomadas

### ✅ Mantidas (Boas práticas)

1. **1 comportamento = 1 teste canônico**: Eliminou duplicatas
2. **Ordem canônica imutável**: GATE → SETUP → CONTRATO → FUNCIONAIS
3. **Specs por responsabilidade**: Contract (navegação), CRUD (operações), States (visuais), RBAC (permissões)
4. **Novos specs para novas features**: trainings, stats, athletes

### ❌ Descartadas (Excesso de cobertura)

1. **Testes de F5/Reload**: Não críticos para E2E
2. **Browser history (back/forward)**: Comportamento nativo do navegador
3. **Testes de performance (<5s, <10s)**: Regra 45 - sem testes de performance em E2E
4. **TestIDs exaustivos**: Mantidos apenas os críticos (root, botões principais)

## Impacto

### Antes
- **387 testes** (incluindo duplicados em teams_gaps)
- 2 suítes paralelas (teams + teams_gaps)
- Confusão sobre qual rodar

### Depois
- **~150 testes únicos** (eliminando duplicatas)
- 1 suíte canônica única (`tests/e2e/teams`)
- Ordem clara documentada em [INDEX_E2E.md](../INDEX_E2E.md)

## Manutenção Futura

### Quando adicionar novos testes?

Use este fluxo de decisão:

```
Novo teste?
├─ Valida navegação/redirect/404/root testid?
│  └─ SIM → teams.contract.spec.ts
├─ Valida CRUD (create/read/update/delete)?
│  └─ SIM → teams.crud.spec.ts
├─ Valida estados visuais (empty/loading/error/success)?
│  └─ SIM → teams.states.spec.ts
├─ Valida permissões por role?
│  └─ SIM → teams.rbac.spec.ts
├─ Valida fluxo de convite/aceite?
│  └─ SIM → teams.invites.spec.ts ou teams.welcome.spec.ts
├─ Valida aba trainings?
│  └─ SIM → teams.trainings.spec.ts
├─ Valida aba stats?
│  └─ SIM → teams.stats.spec.ts
└─ Valida atletas/registrations?
   └─ SIM → teams.athletes.spec.ts
```

## Referências

- [INDEX_E2E.md](../INDEX_E2E.md) - Índice completo com comandos
- [REGRAS_TESTES.md](REGRAS_TESTES.md) - 51 regras para E2E
- [RODAR_TEAMS.md](RODAR_TEAMS.md) - Este documento que você leu no início
