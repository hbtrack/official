<!-- STATUS: NEEDS_REVIEW -->

# 🧪 TESTES DE API - RENDER DEPLOYMENT

**URL Base:** https://hbtrack.onrender.com
**Data:** 2025-12-25
**Status:** ✅ Aplicação rodando

---

## 🎯 TESTES BÁSICOS

### 1. Health Check ✅
```bash
curl https://hbtrack.onrender.com/health
```

**Resultado esperado:**
```json
{
  "status": "healthy",
  "database": "connected"
}
```

**Status:** ✅ Funcionando (confirmado nos logs)

### 2. Root Endpoint ✅
```bash
curl https://hbtrack.onrender.com/
```

**Resultado esperado:**
```json
{
  "message": "HB Tracking API",
  "version": "1.0.0"
}
```

**Status:** ✅ Funcionando (200 OK nos logs)

### 3. API Documentation ✅
```bash
# Acessar no browser:
https://hbtrack.onrender.com/api/v1/docs
```

**Status:** ✅ Disponível

---

## 📊 ENDPOINTS DE RELATÓRIOS

### GET Endpoints (Leitura)

#### Training Performance
```bash
curl "https://hbtrack.onrender.com/api/v1/reports/training-performance" \
  -H "Authorization: Bearer $JWT_TOKEN"
```

#### Training Trends
```bash
curl "https://hbtrack.onrender.com/api/v1/reports/training-trends?season_id=UUID" \
  -H "Authorization: Bearer $JWT_TOKEN"
```

#### Athlete Reports
```bash
curl "https://hbtrack.onrender.com/api/v1/reports/athletes" \
  -H "Authorization: Bearer $JWT_TOKEN"

curl "https://hbtrack.onrender.com/api/v1/reports/athletes/{athlete_id}" \
  -H "Authorization: Bearer $JWT_TOKEN"
```

#### Wellness Reports
```bash
curl "https://hbtrack.onrender.com/api/v1/reports/wellness-summary" \
  -H "Authorization: Bearer $JWT_TOKEN"

curl "https://hbtrack.onrender.com/api/v1/reports/wellness-trends?period=weekly" \
  -H "Authorization: Bearer $JWT_TOKEN"
```

#### Medical Reports
```bash
curl "https://hbtrack.onrender.com/api/v1/reports/medical-summary" \
  -H "Authorization: Bearer $JWT_TOKEN"

curl "https://hbtrack.onrender.com/api/v1/reports/athletes/{athlete_id}/medical-history" \
  -H "Authorization: Bearer $JWT_TOKEN"
```

---

## 🔄 ENDPOINTS DE MANUTENÇÃO (POST)

### ⚠️ IMPORTANTE: Use POST, não GET!

#### Refresh View Específica
```bash
curl -X POST "https://hbtrack.onrender.com/api/v1/reports/refresh/training_performance" \
  -H "Authorization: Bearer $JWT_TOKEN"
```

**Views disponíveis:**
- `training_performance`
- `athlete_training_summary`
- `wellness_summary`
- `medical_cases_summary`

#### Refresh Todas as Views
```bash
curl -X POST "https://hbtrack.onrender.com/api/v1/reports/refresh-all" \
  -H "Authorization: Bearer $JWT_TOKEN"
```

**Resposta esperada:**
```json
{
  "status": "success",
  "total_views": 4,
  "success_count": 4,
  "error_count": 0,
  "results": {
    "training_performance": {
      "status": "success",
      "view": "mv_training_performance",
      "rows": 0
    },
    ...
  }
}
```

#### View Statistics
```bash
curl "https://hbtrack.onrender.com/api/v1/reports/stats" \
  -H "Authorization: Bearer $JWT_TOKEN"
```

**Resposta esperada:**
```json
{
  "training_performance": {
    "view_name": "mv_training_performance",
    "rows": 0,
    "schema": "public"
  },
  ...
}
```

---

## 🔐 AUTENTICAÇÃO

### Obter JWT Token

```bash
curl -X POST "https://hbtrack.onrender.com/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "senha_admin"
  }'
```

**Resposta:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

### Usar Token

```bash
# Exportar token
export JWT_TOKEN="eyJhbGciOiJIUzI1NiIs..."

# Usar em requests
curl "https://hbtrack.onrender.com/api/v1/reports/training-performance" \
  -H "Authorization: Bearer $JWT_TOKEN"
```

---

## 🐛 ERROS COMUNS

### 405 Method Not Allowed

**Causa:** Usando GET em endpoint POST

**Solução:**
```bash
# Errado
curl "https://hbtrack.onrender.com/api/v1/reports/refresh-all"

# Correto
curl -X POST "https://hbtrack.onrender.com/api/v1/reports/refresh-all"
```

### 401 Unauthorized

**Causa:** Token JWT ausente ou inválido

**Solução:**
```bash
# 1. Fazer login
curl -X POST "https://hbtrack.onrender.com/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password"}'

# 2. Usar token obtido
```

### 404 Not Found

**Causa:** Endpoint ou recurso não existe

**Solução:**
- Verificar URL está correta
- Verificar router está registrado
- Conferir em /api/v1/docs

### 500 Internal Server Error

**Causa:** Erro no servidor (migrations não aplicadas, DB erro, etc.)

**Solução:**
```bash
# 1. Verificar logs do Render
# 2. Verificar migrations foram aplicadas
# 3. Verificar DATABASE_URL está correto
```

---

## 📋 CHECKLIST DE TESTES

### Pré-Migrations (Atual)
- [x] Health check funcionando
- [x] Root endpoint funcionando
- [x] API Docs acessível
- [ ] Endpoints de relatórios (podem falhar se views não existem)
- [ ] Endpoints de refresh (405 porque usou GET ao invés de POST)

### Pós-Migrations (Após aplicar hotfix)
- [ ] `GET /api/v1/reports/training-performance` → 200 OK
- [ ] `GET /api/v1/reports/athletes` → 200 OK
- [ ] `GET /api/v1/reports/wellness-summary` → 200 OK
- [ ] `GET /api/v1/reports/medical-summary` → 200 OK
- [ ] `POST /api/v1/reports/refresh-all` → 200 OK
- [ ] `POST /api/v1/reports/refresh/training_performance` → 200 OK
- [ ] `GET /api/v1/reports/stats` → 200 OK

---

## 🎯 SCRIPT DE TESTE AUTOMATIZADO

```bash
#!/bin/bash
# test_render_api.sh

BASE_URL="https://hbtrack.onrender.com"
echo "Testing Render API: $BASE_URL"
echo ""

# 1. Health check
echo "1. Health Check:"
curl -s "$BASE_URL/health" | jq '.'
echo ""

# 2. Root
echo "2. Root Endpoint:"
curl -s "$BASE_URL/" | jq '.'
echo ""

# 3. Login (ajuste credenciais)
echo "3. Login:"
TOKEN=$(curl -s -X POST "$BASE_URL/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"password"}' | jq -r '.access_token')
echo "Token: ${TOKEN:0:20}..."
echo ""

# 4. Test reports
echo "4. Training Performance:"
curl -s "$BASE_URL/api/v1/reports/training-performance" \
  -H "Authorization: Bearer $TOKEN" | jq '.'
echo ""

# 5. Refresh all
echo "5. Refresh All Views:"
curl -s -X POST "$BASE_URL/api/v1/reports/refresh-all" \
  -H "Authorization: Bearer $TOKEN" | jq '.'
echo ""

# 6. View stats
echo "6. View Statistics:"
curl -s "$BASE_URL/api/v1/reports/stats" \
  -H "Authorization: Bearer $TOKEN" | jq '.'
echo ""

echo "Tests completed!"
```

---

**Preparado por:** Claude Sonnet 4.5
**Data:** 2025-12-25