<!-- STATUS: NEEDS_REVIEW -->

# 🚀 INSTRUÇÕES DE DEPLOY NO RENDER

**Data:** 2025-12-25
**Serviço:** HB Track Backend (https://hbtrack.onrender.com)

---

## 📋 CONFIGURAÇÕES DO RENDER

### 1. Build & Deploy Settings

#### Repository
- **Repository:** `https://github.com/Davisermenho/Hb-Traking---Backend`
- **Branch:** `main`

#### Root Directory
```
backend
```

#### Build Command
```bash
pip install --upgrade pip && pip install -r requirements.txt
```

#### Pre-Deploy Command (ATUALIZADO - Migrations Automáticas)
```bash
alembic -c db/alembic.ini upgrade head
```

**IMPORTANTE:** Este comando aplicará automaticamente todas as migrations antes do deploy, incluindo:
- FASE 1: season_id/team_id (NULLABLE)
- R1-R4: Materialized views
- FASE 2: NOT NULL constraints

#### Start Command
```bash
gunicorn -w 2 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:$PORT
```

---

### 2. Environment Variables

**Variáveis Obrigatórias:**

```bash
DATABASE_URL=postgresql://neondb_owner:npg_fmT3ctPrD8pW@ep-soft-cake-ad07z2ue-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require

JWT_SECRET=your-secret-key-here

PYTHON_VERSION=3.14

PYTHONUNBUFFERED=1
```

**Nota:** As variáveis já devem estar configuradas no Render.

---

### 3. Auto-Deploy

- **Auto-Deploy:** `On Commit` ✅
- Quando houver push para `main`, o Render fará deploy automaticamente

---

## 🎯 PROCESSO DE DEPLOY

### Deploy Automático (Recomendado)

Quando você faz push para `main`, o Render:

1. ✅ Detecta mudanças no repositório
2. ✅ Executa Build Command (instala dependências)
3. ✅ Executa Pre-Deploy Command (aplica migrations)
4. ✅ Inicia aplicação com Start Command
5. ✅ Faz health check e atualiza serviço

### Deploy Manual

Se precisar forçar deploy:

1. Acesse Render Dashboard: https://dashboard.render.com
2. Selecione o serviço "HbTrack"
3. Clique em **"Manual Deploy"** → **"Deploy latest commit"**

---

## ✅ VERIFICAÇÕES PÓS-DEPLOY

### 1. Health Check
```bash
curl https://hbtrack.onrender.com/health
```

Resposta esperada:
```json
{
  "status": "healthy",
  "database": "connected"
}
```

### 2. API Docs
Acessar: https://hbtrack.onrender.com/api/v1/docs

### 3. Endpoints de Relatórios (12 endpoints)

**Reports:**
- GET `/api/v1/reports/training-performance`
- GET `/api/v1/reports/training-trends`
- GET `/api/v1/reports/athletes`
- GET `/api/v1/reports/athletes/{id}`
- GET `/api/v1/reports/wellness-summary`
- GET `/api/v1/reports/wellness-trends`
- GET `/api/v1/reports/medical-summary`
- GET `/api/v1/reports/athletes/{id}/medical-history`

**Maintenance:**
- POST `/api/v1/reports/refresh/{view_name}`
- POST `/api/v1/reports/refresh-all`
- GET `/api/v1/reports/stats`

### 4. Verificar Migrations

```bash
# Via logs do Render, procurar por:
"INFO alembic.runtime.migration Running upgrade ... -> b4b136a1af44"
```

Deve mostrar que aplicou até `b4b136a1af44` (FASE 2 - NOT NULL).

---

## 🔧 TROUBLESHOOTING

### Problema: Migration Falha

**Sintoma:** Pre-Deploy Command retorna erro

**Solução:**
```bash
# 1. Verificar logs do Render
# 2. Se houver dados com NULL, executar backfill:
python db/scripts/backfill_simple.py --database-url "$DATABASE_URL"

# 3. Re-executar deploy
```

### Problema: Aplicação Não Inicia

**Verificar:**
1. `DATABASE_URL` está correto?
2. `JWT_SECRET` está definido?
3. Logs mostram erro de importação?

**Solução:**
- Verificar environment variables no Render
- Verificar requirements.txt tem todas dependências
- Checar logs para erro específico

### Problema: Endpoints 404

**Verificar:**
1. Router está registrado em `backend/app/api/v1/__init__.py`?
2. Prefix correto (`/api/v1/reports`)?

**Solução:**
- Verificar que PR #3 foi mergeado
- Verificar branch `main` tem código atualizado

---

## 📊 MONITORAMENTO

### Logs do Render

Acessar logs em tempo real:
```
https://dashboard.render.com/web/{service-id}/logs
```

### Métricas

- **Response Time:** < 500ms (p95)
- **Uptime:** 99.9%
- **Errors:** < 1%

### Alertas

Configurar notificações no Render para:
- Deploy failed
- Service down
- High error rate

---

## 🔄 REFRESH DE MATERIALIZED VIEWS

### Manual (via API)

```bash
# Refresh todas as views
curl -X POST "https://hbtrack.onrender.com/api/v1/reports/refresh-all" \
  -H "Authorization: Bearer $JWT_TOKEN"

# Refresh view específica
curl -X POST "https://hbtrack.onrender.com/api/v1/reports/refresh/training_performance" \
  -H "Authorization: Bearer $JWT_TOKEN"
```

### Automático (Recomendado)

Configurar cron job (via Render Cron Jobs ou externa):

```bash
# A cada hora: training_performance
0 * * * * curl -X POST "https://hbtrack.onrender.com/api/v1/reports/refresh/training_performance" -H "Authorization: Bearer $JWT_TOKEN"

# Diário (2am): demais views
0 2 * * * curl -X POST "https://hbtrack.onrender.com/api/v1/reports/refresh-all" -H "Authorization: Bearer $JWT_TOKEN"
```

---

## 🎉 STATUS ATUAL

- ✅ Código sincronizado com GitHub (main)
- ✅ Migrations no repositório (6 migrations)
- ✅ Router registrado no FastAPI
- ✅ Requirements.txt atualizado
- ✅ Database em produção atualizada (Neon)
- ⏳ **PRÓXIMO:** Trigger deploy no Render

---

## 📞 SUPORTE

**GitHub Issues:** https://github.com/Davisermenho/Hb-Traking---Backend/issues
**Render Support:** https://render.com/docs
**Neon Support:** https://neon.tech/docs

---

**Preparado por:** Claude Sonnet 4.5
**Data:** 2025-12-25
**Versão:** 1.0
