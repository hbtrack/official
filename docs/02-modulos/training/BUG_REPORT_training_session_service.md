<!-- STATUS: NEEDS_REVIEW -->

# 🐛 BUG REPORT: Training Session Service - Missing await keywords

**Data**: 2026-01-13
**Severidade**: 🔴 **CRÍTICA**
**Arquivo**: `app/services/training_session_service.py`
**Status**: ❌ **QUEBRADO**

---

## 📋 Resumo Executivo

O serviço `TrainingSessionService` está usando `AsyncSession` mas **esqueceu de adicionar `await` em 6 chamadas ao banco de dados**, causando erro `'NoneType' object can't be awaited` em runtime.

---

## 🔍 Root Cause

**Problema**: Chamadas a `self.db.execute()` e `self.db.scalar()` retornam **coroutines** que devem ser aguardadas com `await`. Sem `await`, o código recebe uma coroutine não resolvida em vez do resultado.

**Erro em Produção**:
```json
{
  "error_code": "INTERNAL_SERVER_ERROR",
  "message": "Erro interno: 'NoneType' object can't be awaited"
}
```

---

## 🎯 Linhas Afetadas

### 1. `get_all()` - Listagem Paginada
**Linhas**: 85, 91

```python
# ❌ ANTES (QUEBRADO)
total = self.db.scalar(count_query) or 0
result = self.db.execute(query)

# ✅ DEPOIS (CORRETO)
total = await self.db.scalar(count_query) or 0
result = await self.db.execute(query)
```

### 2. `get_by_id()` - Buscar por ID
**Linha**: 118

```python
# ❌ ANTES (QUEBRADO)
result = self.db.execute(query)

# ✅ DEPOIS (CORRETO)
result = await self.db.execute(query)
```

### 3. `create()` - Criar Sessão
**Linha**: 133

```python
# ❌ ANTES (QUEBRADO)
team_result = self.db.execute(team_query)

# ✅ DEPOIS (CORRETO)
team_result = await self.db.execute(team_query)
```

### 4. `get_by_team_and_date()` - Buscar por Time e Data
**Linha**: 304

```python
# ❌ ANTES (QUEBRADO)
result = self.db.execute(query)

# ✅ DEPOIS (CORRETO)
result = await self.db.execute(query)
```

### 5. `calculate_deviation()` - Calcular Desvio
**Linha**: 430

```python
# ❌ ANTES (QUEBRADO)
result = self.db.execute(query)

# ✅ DEPOIS (CORRETO)
result = await self.db.execute(query)
```

---

## 🔧 Correção Completa

### Método `get_all()` (linhas 49-97)

```python
async def get_all(
    self,
    *,
    team_id: Optional[UUID] = None,
    season_id: Optional[UUID] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    include_deleted: bool = False,
    page: int = 1,
    size: int = 20,
) -> tuple[list[TrainingSession], int]:
    """Lista sessões de treino com filtros."""
    query = select(TrainingSession).where(
        TrainingSession.organization_id == self.context.organization_id
    )

    if not include_deleted:
        query = query.where(TrainingSession.deleted_at.is_(None))

    if team_id:
        query = query.where(TrainingSession.team_id == team_id)

    if season_id:
        query = query.where(TrainingSession.season_id == season_id)

    if start_date:
        query = query.where(TrainingSession.session_at >= start_date)

    if end_date:
        query = query.where(TrainingSession.session_at <= end_date)

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total = await self.db.scalar(count_query) or 0  # ✅ ADICIONADO await

    # Paginate
    query = query.order_by(TrainingSession.session_at.desc())
    query = query.offset((page - 1) * size).limit(size)

    result = await self.db.execute(query)  # ✅ ADICIONADO await
    sessions = list(result.scalars().all())

    logger.info(
        f"Listed {len(sessions)} training sessions for org {self.context.organization_id}"
    )
    return sessions, total
```

### Método `get_by_id()` (linhas 99-124)

```python
async def get_by_id(
    self,
    session_id: UUID,
    *,
    include_deleted: bool = False,
) -> TrainingSession:
    """Busca sessão de treino por ID."""
    query = select(TrainingSession).where(
        and_(
            TrainingSession.id == session_id,
            TrainingSession.organization_id == self.context.organization_id,
        )
    )

    if not include_deleted:
        query = query.where(TrainingSession.deleted_at.is_(None))

    result = await self.db.execute(query)  # ✅ ADICIONADO await
    session = result.scalar_one_or_none()

    if not session:
        raise NotFoundError(f"Training session {session_id} not found")

    return session
```

### Método `create()` (linhas 126-166)

```python
async def create(self, data: TrainingSessionCreate) -> TrainingSession:
    """Cria nova sessão de treino."""
    # Buscar team para obter organization_id
    team_query = select(Team).where(Team.id == data.team_id)
    team_result = await self.db.execute(team_query)  # ✅ ADICIONADO await
    team = team_result.scalar_one_or_none()

    if not team:
        raise NotFoundError(f"Team {data.team_id} not found")

    if team.organization_id != self.context.organization_id:
        raise ForbiddenError("Team belongs to another organization")

    # ... resto do código permanece igual
```

### Método `get_by_team_and_date()` (linhas 284-305)

```python
async def get_by_team_and_date(
    self,
    team_id: UUID,
    session_date: datetime,
) -> Optional[TrainingSession]:
    """Busca sessão por time e data."""
    # Busca sessões no mesmo dia
    start_of_day = session_date.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = start_of_day + timedelta(days=1)

    query = select(TrainingSession).where(
        and_(
            TrainingSession.team_id == team_id,
            TrainingSession.session_at >= start_of_day,
            TrainingSession.session_at < end_of_day,
            TrainingSession.deleted_at.is_(None),
        )
    )
    result = await self.db.execute(query)  # ✅ ADICIONADO await
    return result.scalar_one_or_none()
```

### Método `calculate_deviation()` (linhas 404-494)

```python
async def calculate_deviation(
    self,
    session_id: UUID,
) -> Optional[dict]:
    """Calcula desvio entre planejado e executado."""
    from app.models.training_microcycle import TrainingMicrocycle

    session = await self.get_by_id(session_id)

    if not session.microcycle_id:
        return None

    # Buscar microciclo
    query = select(TrainingMicrocycle).where(
        TrainingMicrocycle.id == session.microcycle_id
    )
    result = await self.db.execute(query)  # ✅ ADICIONADO await
    microcycle = result.scalar_one_or_none()

    # ... resto do código permanece igual
```

---

## 📊 Impacto

### ❌ Funcionalidades Quebradas
- **Listar sessões** (`GET /training-sessions`)
- **Buscar sessão por ID** (`GET /training-sessions/{id}`)
- **Criar sessão** (`POST /training-sessions`)
- **Deletar sessão** (`DELETE /training-sessions/{id}`) ← **Erro reportado no E2E**
- **Calcular desvio** (`GET /training-sessions/{id}/deviation`)

### ✅ Funcionalidades que Funcionam
- **Update** (`PATCH /training-sessions/{id}`) - usa `flush()`
- **Soft delete** (método em si) - usa `flush()`
- **Restore** - usa `flush()`

### 🧪 Evidência do Bug
**Teste E2E Falhando**:
```typescript
// tests/e2e/teams/teams.trainings.spec.ts:203
test('treino deletado via API não deve aparecer na lista', async ({ page }) => {
  await deleteSessionViaAPI(trainingId, sessionToDelete.id);
  // ❌ Falha com: 500 - "Erro interno: 'NoneType' object can't be awaited"
});
```

**Traceback do Erro**:
```
Error: deleteSessionViaAPI failed: 500 - {
  "error_code":"INTERNAL_SERVER_ERROR",
  "message":"Erro interno: 'NoneType' object can't be awaited",
  "request_id":"unknown"
}
```

---

## 🚨 Por Que Este Bug Passou Despercebido?

1. **Testes Unitários**: Provavelmente usando mocks ou `Session` síncrona
2. **Type Hints**: Python não valida `await` em tempo de compilação
3. **IDE Warnings**: Podem ter sido ignorados
4. **Código Parcialmente Funcional**: Métodos com `flush()` funcionam

---

## ✅ Validação da Correção

### Antes de Aplicar
```bash
# Teste E2E falha
npm run test:e2e -- --grep "treino deletado"
# Resultado: ❌ 500 Internal Server Error
```

### Depois de Aplicar
```bash
# Teste E2E passa
npm run test:e2e -- --grep "treino deletado"
# Resultado: ✅ ok (< 1s)
```

---

## 📝 Checklist de Correção

- [ ] Adicionar `await` em linha 85 (`total = await self.db.scalar...`)
- [ ] Adicionar `await` em linha 91 (`result = await self.db.execute...`)
- [ ] Adicionar `await` em linha 118 (`result = await self.db.execute...`)
- [ ] Adicionar `await` em linha 133 (`team_result = await self.db.execute...`)
- [ ] Adicionar `await` em linha 304 (`result = await self.db.execute...`)
- [ ] Adicionar `await` em linha 430 (`result = await self.db.execute...`)
- [ ] Rodar testes unitários
- [ ] Rodar testes E2E
- [ ] Verificar outras services com `AsyncSession`

---

## 🔍 Auditoria Recomendada

Verificar outros serviços que podem ter o mesmo problema:

```bash
# Buscar por AsyncSession sem await
cd "C:\HB TRACK\Hb Track - Backend"
grep -r "self.db.execute(" app/services/ | grep -v "await"
grep -r "self.db.scalar(" app/services/ | grep -v "await"
```

---

## 📚 Referências

- **SQLAlchemy AsyncSession**: https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html
- **Python Coroutines**: https://docs.python.org/3/library/asyncio-task.html
- **Arquivo Afetado**: `app/services/training_session_service.py`
- **Teste E2E**: `tests/e2e/teams/teams.trainings.spec.ts:203`

---

*Gerado por Claude Code - 2026-01-13*
*Reportado durante análise de falha de teste E2E*
