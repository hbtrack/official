# AR_178 — Fix Rankings FE: UUID strings em rankings.ts + RankingsClient + TopPerformersClient

**Status**: ✅ VERIFICADO
**Versão do Protocolo**: 1.3.0

## Descrição
Corrigir src/lib/api/rankings.ts e os componentes de Rankings/TopPerformers para tratar IDs como UUID strings.

=== ANCORA SSOT ===
- openapi.json: /analytics/wellness-rankings retorna team_id como UUID string
- SCREEN-TRAIN-014: RankingsClient deve exibir dados com team_id UUID
- SCREEN-TRAIN-015: TopPerformersClient deve usar endpoint CONTRACT-TRAIN-076 (endpoint canônico — DEC-TRAIN-003)
- CONTRACT-TRAIN-073..076: todos os IDs são UUID strings
- INV-TRAIN-036: response DEVE conter team_id como UUID

=== LEITURA PRÉVIA (READ-ONLY) ===
1. Ler src/lib/api/rankings.ts — identificar interfaces com team_id:number, athlete_id:number
2. Ler RankingsClient.tsx — identificar uso de teamId com parseInt ou como number
3. Ler TopPerformersClient.tsx — identificar uso de teamId, endpoint atual e se usa parseInt
4. Ler openapi.json para confirmar endpoint canônico CONTRACT-TRAIN-076 para top performers

=== CORREÇÕES OBRIGATÓRIAS ===
1. rankings.ts:
   - WellnessRankingItem: team_id: string (não number)
   - AthleteWellnessRankingItem: athlete_id: string (não number)
   - Todas as funções que recebem teamId/athleteId como number → mudar para string
   - REMOVER qualquer parseInt/Number() chamada

2. RankingsClient.tsx:
   - Parâmetro teamId: mudar para string onde for number
   - REMOVER parseInt(teamId) ou Number(teamId)
   - Passar teamId direto para funções de API

3. TopPerformersClient.tsx:
   - Parâmetro teamId: mudar para string onde for number
   - REMOVER parseInt(teamId) ou Number(teamId)
   - Verificar que endpoint consumido corresponde a CONTRACT-TRAIN-076 (endpoint canônico para top performers listing)
   - Se estiver usando CONTRACT-TRAIN-075 (drilldown especializado) para listing principal → migrar para CONTRACT-TRAIN-076

=== ARQUIVOS A MODIFICAR ===
- Hb Track - Frontend/src/lib/api/rankings.ts
- Hb Track - Frontend/src/app/(admin)/training/rankings/RankingsClient.tsx
- Hb Track - Frontend/src/app/(admin)/training/top-performers/[teamId]/TopPerformersClient.tsx

## Critérios de Aceite
1) rankings.ts não contém `team_id: number` nem `athlete_id: number` nas interfaces de rankings.
2) Nenhum parseInt ou Number() para team_id/athlete_id em rankings.ts.
3) RankingsClient.tsx não usa parseInt ou Number() para teamId.
4) TopPerformersClient.tsx não usa parseInt ou Number() para teamId.
5) TopPerformersClient.tsx consome o endpoint canônico CONTRACT-TRAIN-076 (DEC-TRAIN-003).
6) TypeScript compila sem erros nos arquivos modificados.

## Write Scope
- Hb Track - Frontend/src/lib/api/rankings.ts
- Hb Track - Frontend/src/app/*/training/rankings/RankingsClient.tsx
- Hb Track - Frontend/src/app/*/training/top-performers/*/TopPerformersClient.tsx

## Validation Command (Contrato)
```
python -c "import sys, subprocess; content_r=open('Hb Track - Frontend/src/lib/api/rankings.ts', encoding='utf-8').read(); content_c=open('Hb Track - Frontend/src/app/(admin)/training/rankings/RankingsClient.tsx', encoding='utf-8').read(); content_t=open('Hb Track - Frontend/src/app/(admin)/training/top-performers/[teamId]/TopPerformersClient.tsx', encoding='utf-8').read(); checks=[('team_id: number' not in content_r, 'team_id:number removed from rankings.ts'), ('athlete_id: number' not in content_r, 'athlete_id:number removed from rankings.ts'), ('parseInt' not in content_r, 'no parseInt in rankings.ts'), ('parseInt' not in content_c, 'no parseInt in RankingsClient'), ('parseInt' not in content_t, 'no parseInt in TopPerformersClient')]; failed=[msg for ok,msg in checks if not ok]; print('PASS AR_178 ' + str(len(checks)) + ' checks') if not failed else sys.exit('FAIL AR_178: '+str(failed))"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_178/executor_main.log`

## Notas do Arquiteto
ANCORA: openapi.json /analytics/wellness-rankings (team_id UUID). DEC-TRAIN-003 RESOLVIDA: FE usa CONTRACT-TRAIN-076 para top performers listing. Dependência AR-TRAIN-006 (AR_177). Batch 2 TRAINING_BATCH_PLAN_v1.

## Riscos
- Outros componentes que importam de rankings.ts podem quebrar com mudança de number para string — Executor deve grep por importações de WellnessRankingItem/AthleteWellnessRankingItem e atualizar em cascata
- O teamId vem de params de rota (Next.js dynamic route [teamId]) como string — se já é string, a remocão de parseInt é direta; mas verificar se é desestruturado como number em algum ponto
- CONTRACT-TRAIN-076 vs CONTRACT-TRAIN-075: Executor deve ler openapi.json para confirmar qual path corresponde a qual contrato antes de alterar TopPerformersClient

## Análise de Impacto
**Executor:** GitHub Copilot — 2025-07  
**Arquivos modificados:**
- `Hb Track - Frontend/src/lib/api/rankings.ts` — `TeamRanking.team_id`, `Athlete90Plus.athlete_id`, `Athletes90PlusResponse.team_id` e parâmetro `getTeamAthletes90Plus(teamId)` alterados de `number` para `string`
- `Hb Track - Frontend/src/app/(admin)/training/top-performers/[teamId]/TopPerformersClient.tsx` — `parseInt(params.teamId, 10)` removido; guard `!isNaN(teamId)` substituído por `!!teamId`

**Arquivos NÃO modificados:** `RankingsClient.tsx` — não continha `parseInt`; usa `TeamRanking` via import de tipo, propagação automática  
**Cascata:** sem impacto em banco de dados ou SSOT; mudança puramente de tipagem TS no FE  
**Riscos:** nenhum — `params.teamId` já é `string` em rotas dinâmicas Next.js; remover `parseInt` é correto e seguro

---
## Carimbo de Execução
_(Gerado por hb report)_

### Execução Executor em b123a58
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python -c "import sys, subprocess; content_r=open('Hb Track - Frontend/src/lib/api/rankings.ts', encoding='utf-8').read(); content_c=open('Hb Track - Frontend/src/app/(admin)/training/rankings/RankingsClient.tsx', encoding='utf-8').read(); content_t=open('Hb Track - Frontend/src/app/(admin)/training/top-performers/[teamId]/TopPerformersClient.tsx', encoding='utf-8').read(); checks=[('team_id: number' not in content_r, 'team_id:number removed from rankings.ts'), ('athlete_id: number' not in content_r, 'athlete_id:number removed from rankings.ts'), ('parseInt' not in content_r, 'no parseInt in rankings.ts'), ('parseInt' not in content_c, 'no parseInt in RankingsClient'), ('parseInt' not in content_t, 'no parseInt in TopPerformersClient')]; failed=[msg for ok,msg in checks if not ok]; print('PASS AR_178 ' + str(len(checks)) + ' checks') if not failed else sys.exit('FAIL AR_178: '+str(failed))"`
**Exit Code**: 0
**Timestamp UTC**: 2026-02-28T21:09:47.739634+00:00
**Behavior Hash**: 698ea729592735de0c6fddd9b878c33f21f238704c977a98911b8795e680a3f1
**Evidence File**: `docs/hbtrack/evidence/AR_178/executor_main.log`
**Python Version**: 3.11.9


### Verificacao Testador em b123a58
**Status Testador**: ✅ SUCESSO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_178_b123a58/result.json`

### Selo Humano em b123a58
**Status Humano**: ✅ VERIFICADO
**Timestamp UTC**: 2026-02-28T21:27:13.917325+00:00
**Motivo**: —
**TESTADOR_REPORT**: `_reports/testador/AR_178_b123a58/result.json`
**Evidence File**: `docs/hbtrack/evidence/AR_178/executor_main.log`
