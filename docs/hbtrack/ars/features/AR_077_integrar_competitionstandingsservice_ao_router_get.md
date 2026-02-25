# AR_077 — Integrar CompetitionStandingsService ao router: GET /standings + POST /standings/recalculate

**Status**: 🔴 REJEITADO
**Versão do Protocolo**: 1.3.0

## Descrição
Modificar Hb Track - Backend/app/api/v1/routers/competitions_v2.py.

=== MUDANCA 1: get_standings (GET /competitions/{id}/standings) ===
REMOVER logica inline: cache-read competition_standings via stats.get() + JSONB fallback.
SUBSTITUIR por:
  1) from app.services.competition_standings_service import CompetitionStandingsService
  2) service = CompetitionStandingsService(db)
  3) standings = await service.recalculate_standings(competition_id, db, phase_id=phase_id)
  4) Se group_name fornecido: filtrar lista por standing.group_name == group_name
  5) return [CompetitionStandingResponse.model_validate(s) for s in standings]

=== MUDANCA 2: POST /competitions/{id}/standings/recalculate ===
ADICIONAR endpoint (documentado no header do router linha 32, nunca implementado):
  @router.post('/competitions/{competition_id}/standings/recalculate',
    status_code=200, operation_id='recalculateStandings',
    response_model=List[CompetitionStandingResponse])
  async def recalculate_standings_endpoint(competition_id: UUID,
    phase_id: Optional[UUID]=Query(None), db=Depends(get_db),
    context=Depends(get_current_context)) -> List[CompetitionStandingResponse]:
  Logica identica GET: instancia service, chama recalculate_standings, retorna lista serializada.

Criar Hb Track - Backend/tests/api/test_standings_router_integration.py
Classe TestStandingsRouterIntegration:

  test_get_standings_requires_auth (fixture: client):
    response = client.get(f'/api/v1/competitions/{uuid4()}/standings')
    assert response.status_code == 401

  test_post_recalculate_requires_auth (fixture: client):
    response = client.post(f'/api/v1/competitions/{uuid4()}/standings/recalculate')
    assert response.status_code == 401

  test_get_standings_uses_dynamic_scoring_inv_comp_008 (fixtures: auth_client, db):
    1) POST /v1/competitions/v2 com {name: AR077-uuid4, points_per_win: 3}
       -> competition_id; se status nao in (200,201): pytest.skip
    2) POST /competitions/{id}/opponent-teams x3 (TeamA, TeamB, TeamC)
       -> ta, tb, tc IDs; se falhar: pytest.skip
    3) POST /competitions/{id}/matches x3:
       M1: home_team_id=ta away_team_id=tb
       M2: home_team_id=ta away_team_id=tc
       M3: home_team_id=tb away_team_id=tc
       -> m1, m2, m3 IDs; se falhar: pytest.skip
    4) PATCH /competitions/{id}/matches/{mid}/result x3:
       M1: home_score=3 away_score=1 status=finished -> TeamA vence (2W total)
       M2: home_score=2 away_score=1 status=finished -> TeamA vence
       M3: home_score=0 away_score=2 status=finished -> TeamC vence (1W)
       Esperado ppw=3: TeamA 2W=6pts, TeamC 1W=3pts, TeamB 0W=0pts; se falhar: pytest.skip
    5) response = auth_client.get(f'/api/v1/competitions/{competition_id}/standings')
       assert response.status_code == 200
       standings = sorted(response.json(), key=lambda x: x['position'])
       assert len(standings) >= 3
       pts = [s['points'] for s in standings]
       assert pts[0] >= pts[1] >= pts[2], f'Wrong order: {pts}'
       assert pts[0] == 6, f'Expected 6pts (ppw=3*2W), got {pts[0]} hardcoded ppw=2 daria 4'

  test_post_recalculate_returns_200 (fixtures: auth_client, db):
    Cria competition minima; POST /standings/recalculate -> assert 200 e lista

## Critérios de Aceite
1) competitions_v2.py: get_standings NAO contem mais stats.get() nem JSONB fallback.
2) competitions_v2.py: get_standings chama CompetitionStandingsService.recalculate_standings.
3) competitions_v2.py: recalculateStandings (POST) implementado retorna 200 com lista.
4) test_get_standings_uses_dynamic_scoring_inv_comp_008: pts[0]==6 (ppw=3 do banco).
5) pytest exit_code=0 para test_standings_router_integration.py.

## Write Scope
- Hb Track - Backend/app/api/v1/routers/competitions_v2.py
- Hb Track - Backend/tests/api/test_standings_router_integration.py

## Validation Command (Contrato)
```
python -m pytest "Hb Track - Backend/tests/api/test_standings_router_integration.py" -v --tb=short -x
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_077/executor_main.log`

## Notas do Arquiteto
DESIGN: GET /standings sempre recalcula - dados frescos. O assert pts[0]==6 e prova antifragil INV-COMP-008: ppw=2 hardcoded daria 4pts, ppw=3 do banco da 6pts. POST /recalculate e endpoint explicito para clientes.

## Riscos
- recalculate_standings lanca NotFoundError se competition nao existir - router deve retornar 404
- GET /standings agora e operacao de escrita (upsert via recalculate) - aceitavel no escopo atual
- openapi.json vai derivar com recalculateStandings - follow-up AR_078 deve regenerar SSOT
- updateMatchResult pode nao aceitar campo status diretamente - Executor verifica e adapta
- Executor NAO deve tocar competition_standings_service.py (AR_076) - apenas router + teste

## Análise de Impacto

**Tipo**: Modificação (router) + Criação (testes)

**Arquivos Modificados**:
- `Hb Track - Backend/app/api/v1/routers/competitions_v2.py` (~50 linhas alteradas)
  - **GET /competitions/{id}/standings**: remover JSONB fallback, integrar `CompetitionStandingsService.recalculate_standings()`
  - **POST /competitions/{id}/standings/recalculate**: adicionar endpoint (operação documentada no header mas não implementada)

**Arquivos Criados**:
- `Hb Track - Backend/tests/api/test_standings_router_integration.py` (~200 linhas)
  - 4 testes: autenticação (401) + INV-COMP-008 antifrágil (ppw=3→6pts) + recalculate básico

**Dependências**:
- `CompetitionStandingsService` (AR_076 VERIFICADO)
- INV-COMP-005/006/008 (standings + soft delete + dynamic scoring)

**Impacto Runtime**:
- GET /standings muda de "cache-read JSONB" para "recalculate sempre" → dados frescos, operação write
- POST /standings/recalculate expõe recalcular manualmente (útil para corrigir estado)

**Riscos**:
- LOW: NotFoundError se competition inexistente (router deve tratar → 404)
- MEDIUM: openapi.json vai derivar com novo endpoint → follow-up AR_078 regenerar SSOT
- LOW: updateMatchResult pode não aceitar campo `status` diretamente (adaptar no teste se necessário)

**Validação Antifrágil**:
- Cria competition com **ppw=3** (não-padrão)
- TeamA vence 2 partidas → esperado **6pts** (ppw=3 × 2W)
- **PROVA**: Se service usar ppw=2 hardcoded, daria 4pts → assert falha
- Garante INV-COMP-008: scoring values vêm do DB

**Impacto Governança**: 
- Router: Governed Root (HB Track Backend)
- Testes: Governed Root
- Não toca SSOT contracts/specs

---
## Carimbo de Execução
_(Gerado por hb report)_

### Execução Executor em dff987f
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python -m pytest "Hb Track - Backend/tests/api/test_standings_router_integration.py" -v --tb=short -x`
**Exit Code**: 0
**Timestamp UTC**: 2026-02-25T03:30:23.521710+00:00
**Behavior Hash**: df2aa6579d707e2e7c0f8cedcb3258207011dc8d4bbc759a9f2ae00201e6d58f
**Evidence File**: `docs/hbtrack/evidence/AR_077/executor_main.log`
**Python Version**: 3.11.9

> 📋 Kanban routing: Arquiteto: Output não-determinístico: behavior_hash diverge nos 3 runs (exit 0 em todos, mas hash diferente)

### Verificacao Testador em dff987f
**Status Testador**: 🔴 REJEITADO
**Consistency**: AH_DIVERGENCE
**Triple-Run**: FLAKY_OUTPUT (3x)
**Exit Testador**: 2 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_077_dff987f/result.json`
