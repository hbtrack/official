<!-- STATUS: NEEDS_REVIEW | verificar contra openapi.json -->

# Training Analytics API - Endpoints para Teste

## Step 16: Backend Analytics com Cache Híbrido

**Base URL:** `http://localhost:8000/api/v1`

**Autenticação:** Bearer Token (JWT)

---

## 1. GET /analytics/team/{team_id}/summary

Retorna métricas agregadas para uma equipe em um período.

**Permissão:** `view_training_analytics` (Dirigente, Coordenador, Treinador)

**Path Parameters:**
- `team_id` (UUID) - ID da equipe

**Query Parameters:**
- `start_date` (date, opcional) - Data inicial YYYY-MM-DD (default: início do mês corrente)
- `end_date` (date, opcional) - Data final YYYY-MM-DD (default: hoje)

**Exemplo Request:**
```http
GET /api/v1/analytics/team/123e4567-e89b-12d3-a456-426614174000/summary?start_date=2024-01-01&end_date=2024-01-31
Authorization: Bearer {token}
```

**Response 200:**
```json
{
  "team_id": "123e4567-e89b-12d3-a456-426614174000",
  "period": {
    "start": "2024-01-01",
    "end": "2024-01-31"
  },
  "metrics": {
    "total_sessions": 12,
    "avg_focus_attack_positional_pct": 35.5,
    "avg_focus_defense_positional_pct": 25.0,
    "avg_focus_transition_offense_pct": 15.0,
    "avg_focus_transition_defense_pct": 10.0,
    "avg_focus_attack_technical_pct": 8.0,
    "avg_focus_defense_technical_pct": 6.5,
    "avg_focus_physical_pct": 0.0,
    "avg_rpe": 6.5,
    "avg_internal_load": 650.0,
    "total_internal_load": 7800.0,
    "attendance_rate": 92.5,
    "wellness_response_rate_pre": 85.0,
    "wellness_response_rate_post": 78.0,
    "athletes_with_badges_count": 8,
    "deviation_count": 2,
    "threshold_mean": 1.8,
    "threshold_stddev": 0.6
  },
  "calculated_at": "2024-01-31T14:30:00Z"
}
```

**Errors:**
- `404` - Team not found
- `403` - Permission denied

---

## 2. GET /analytics/team/{team_id}/weekly-load

Retorna carga semanal das últimas N semanas.

**Permissão:** `view_training_analytics`

**Path Parameters:**
- `team_id` (UUID) - ID da equipe

**Query Parameters:**
- `weeks` (int, opcional) - Quantidade de semanas (1-52, default: 4)

**Exemplo Request:**
```http
GET /api/v1/analytics/team/123e4567-e89b-12d3-a456-426614174000/weekly-load?weeks=4
Authorization: Bearer {token}
```

**Response 200:**
```json
{
  "team_id": "123e4567-e89b-12d3-a456-426614174000",
  "weeks": 4,
  "data": [
    {
      "week_start": "2024-01-22",
      "week_end": "2024-01-28",
      "microcycle_id": "abc123-def456-ghi789",
      "total_sessions": 3,
      "total_internal_load": 1950.0,
      "avg_rpe": 6.5,
      "attendance_rate": 93.0
    },
    {
      "week_start": "2024-01-15",
      "week_end": "2024-01-21",
      "microcycle_id": "xyz789-uvw456-rst123",
      "total_sessions": 4,
      "total_internal_load": 2600.0,
      "avg_rpe": 6.8,
      "attendance_rate": 89.0
    }
  ]
}
```

**Errors:**
- `404` - Team not found
- `403` - Permission denied
- `422` - Invalid weeks parameter

---

## 3. GET /analytics/team/{team_id}/deviation-analysis

Análise de desvios usando threshold dinâmico da equipe (Step 15).

**Permissão:** `view_training_analytics`

**Path Parameters:**
- `team_id` (UUID) - ID da equipe

**Query Parameters:**
- `start_date` (date, opcional) - Data inicial YYYY-MM-DD (default: início do mês corrente)
- `end_date` (date, opcional) - Data final YYYY-MM-DD (default: hoje)

**Exemplo Request:**
```http
GET /api/v1/analytics/team/123e4567-e89b-12d3-a456-426614174000/deviation-analysis?start_date=2024-01-01&end_date=2024-01-31
Authorization: Bearer {token}
```

**Response 200:**
```json
{
  "team_id": "123e4567-e89b-12d3-a456-426614174000",
  "threshold_multiplier": 2.0,
  "period": {
    "start": "2024-01-01",
    "end": "2024-01-31"
  },
  "total_sessions": 12,
  "deviation_count": 2,
  "deviations": [
    {
      "session_id": "xyz789-abc123",
      "session_at": "2024-01-15",
      "planned_rpe": 5.0,
      "actual_rpe": 8.0,
      "deviation": 6.0,
      "exceeded_threshold": true
    },
    {
      "session_id": "def456-ghi789",
      "session_at": "2024-01-22",
      "planned_rpe": 6.0,
      "actual_rpe": 9.5,
      "deviation": 7.0,
      "exceeded_threshold": true
    }
  ]
}
```

**Errors:**
- `404` - Team not found
- `403` - Permission denied

---

## Postman Collection Setup

### 1. Criar Environment

```json
{
  "name": "HB Track Analytics",
  "values": [
    {
      "key": "base_url",
      "value": "http://localhost:8000/api/v1",
      "enabled": true
    },
    {
      "key": "token",
      "value": "seu_jwt_token_aqui",
      "enabled": true
    },
    {
      "key": "team_id",
      "value": "85b5a651-6677-4a6a-a08f-60e657a624a2",
      "enabled": true
    }
  ]
}
```

### 2. Authorization Header (para todas as requests)

```
Authorization: Bearer {{token}}
```

### 3. Obter Token

```http
POST {{base_url}}/auth/login
Content-Type: application/json

{
  "email": "coordenador@hbtracking.com",
  "password": "Coord@123"
}
```

Copiar o `access_token` da resposta para a variável `{{token}}`.

---

## Testes Manuais Sugeridos

### Cenário 1: Summary Mês Corrente
- Endpoint: `/analytics/team/{team_id}/summary`
- Sem query params
- Validar: retorna métricas do mês corrente

### Cenário 2: Summary Período Específico
- Endpoint: `/analytics/team/{team_id}/summary?start_date=2024-01-01&end_date=2024-03-31`
- Validar: combina cache weekly + monthly

### Cenário 3: Weekly Load 4 Semanas
- Endpoint: `/analytics/team/{team_id}/weekly-load?weeks=4`
- Validar: retorna array com 4 itens ordenados DESC

### Cenário 4: Weekly Load 12 Semanas
- Endpoint: `/analytics/team/{team_id}/weekly-load?weeks=12`
- Validar: retorna até 12 itens (ou menos se não houver dados)

### Cenário 5: Deviation Analysis
- Endpoint: `/analytics/team/{team_id}/deviation-analysis`
- Validar: threshold_multiplier correto (do team.alert_threshold_multiplier)
- Validar: lista apenas sessões que excedem threshold

### Cenário 6: Permissões
- Login como atleta
- Tentar acessar qualquer endpoint
- Validar: retorna 403 Forbidden

### Cenário 7: Team Inexistente
- Usar UUID inválido
- Validar: retorna 404 Not Found

---

## Cache Behavior Tests

### Teste 1: Cache Dirty = False
1. GET `/analytics/team/{team_id}/summary`
2. Verificar `calculated_at` timestamp
3. Fazer mesma request novamente
4. Validar: mesmo `calculated_at` (usou cache)

### Teste 2: Cache Dirty = True
1. Criar/editar uma training session
2. GET `/analytics/team/{team_id}/summary`
3. Validar: novo `calculated_at` (recalculou)

### Teste 3: Granularidade
1. GET summary para mês atual → cache weekly
2. GET summary para 3 meses atrás → cache monthly
3. Comparar performance (weekly deve ser mais lento)

---

## Integração com Step 15 (Threshold)

### Teste: Threshold Dinâmico

**Setup:**
1. PATCH `/teams/{team_id}/settings` → `alert_threshold_multiplier: 1.5` (juvenis)
2. GET `/analytics/team/{team_id}/deviation-analysis`
3. Validar: `threshold_multiplier: 1.5` na resposta
4. Validar: mais sessões em `deviations` (threshold mais sensível)

**Setup 2:**
1. PATCH `/teams/{team_id}/settings` → `alert_threshold_multiplier: 2.5` (tolerante)
2. GET `/analytics/team/{team_id}/deviation-analysis`
3. Validar: `threshold_multiplier: 2.5` na resposta
4. Validar: menos sessões em `deviations` (threshold mais tolerante)

---

## SQL para Teste Manual

```sql
-- Ver cache existente
SELECT 
  team_id, 
  granularity, 
  cache_dirty, 
  calculated_at,
  total_sessions,
  wellness_response_rate_pre,
  wellness_response_rate_post
FROM training_analytics_cache
WHERE team_id = '85b5a651-6677-4a6a-a08f-60e657a624a2'
ORDER BY calculated_at DESC;

-- Forçar recálculo (marcar como dirty)
UPDATE training_analytics_cache
SET cache_dirty = true
WHERE team_id = '85b5a651-6677-4a6a-a08f-60e657a624a2';

-- Ver threshold da equipe
SELECT id, name, alert_threshold_multiplier
FROM teams
WHERE id = '85b5a651-6677-4a6a-a08f-60e657a624a2';
```

---

## Status Checklist

**Backend:**
- [x] Model TrainingAnalyticsCache criado
- [x] Service TrainingAnalyticsService criado (960 linhas)
- [x] Router training_analytics.py criado (3 endpoints)
- [x] Schemas criados (7 schemas Pydantic)
- [ ] Permissão SQL executada (aguardando banco disponível)
- [ ] Testes com Postman

**Frontend (Step 17 - Próximo):**
- [ ] Dashboard Analytics
- [ ] Gráficos Recharts
- [ ] Integração com API
