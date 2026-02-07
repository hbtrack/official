<!-- STATUS: NEEDS_REVIEW -->

# 🔧 HOTFIX: Aplicar Migrations no Render

**Data:** 2025-12-25
**Problema:** Pre-Deploy Command não executou migrations
**Status:** 🔴 MIGRATIONS PENDENTES

---

## ⚠️ SITUAÇÃO ATUAL

### Deploy Status: ✅ Aplicação rodando
- **URL:** https://hbtrack.onrender.com
- **Health Check:** ✅ 200 OK
- **Workers:** 2 gunicorn workers ativos

### Problema: ❌ Migrations não aplicadas
**Evidência nos logs:**
- Nenhum log do Alembic durante deploy
- Pre-Deploy Command não foi executado

**Impacto:**
- Banco de dados no Render **NÃO** tem as migrations aplicadas
- Endpoints de relatórios podem falhar ao buscar dados
- Views materializadas **NÃO** existem no DB do Render

---

## 🎯 SOLUÇÃO: Aplicar Migrations Manualmente

### Opção 1: Via Render Shell (RECOMENDADO)

1. **Acessar Render Dashboard:**
   - https://dashboard.render.com
   - Selecione o serviço "HbTrack"

2. **Abrir Shell:**
   - Clique em **"Shell"** no menu lateral
   - Aguarde terminal carregar

3. **Executar Migrations:**
   ```bash
   cd backend
   alembic -c db/alembic.ini current
   # Deve mostrar: 4af09f9d46a0 (antes das nossas migrations)

   alembic -c db/alembic.ini upgrade head
   # Aplica todas as 6 migrations

   alembic -c db/alembic.ini current
   # Deve mostrar: b4b136a1af44 (head)
   ```

4. **Validar:**
   ```bash
   python verify_production_rag.py --database-url "$DATABASE_URL"
   # Deve retornar: CONFORMIDADE RAG: APROVADO
   ```

### Opção 2: Via Pre-Deploy Command (Configuração)

**Configurar no Render Dashboard:**

1. Acesse: Settings → Build & Deploy
2. **Pre-Deploy Command:**
   ```bash
   cd backend && alembic -c db/alembic.ini upgrade head
   ```

   ⚠️ **IMPORTANTE:** Adicione `cd backend &&` antes do comando!

3. Salvar e fazer redeploy:
   - Manual Deploy → Deploy latest commit

### Opção 3: Trigger Deploy com Commit

Criar arquivo `.render-buildpacks.json` na raiz:

```bash
# No seu terminal local
echo '{}' > .render-buildpacks.json
git add .render-buildpacks.json
git commit -m "chore: trigger redeploy with migrations"
git push origin main
```

Depois configurar Pre-Deploy Command conforme Opção 2.

---

## 📋 VERIFICAÇÃO PÓS-MIGRATIONS

### 1. Verificar Revision

```bash
# Via Render Shell
cd backend
alembic -c db/alembic.ini current
```

**Resultado esperado:**
```
b4b136a1af44 (head)
```

### 2. Verificar Materialized Views

```bash
# Via Render Shell
python -c "
import os
import psycopg2

conn = psycopg2.connect(os.environ['DATABASE_URL'])
cur = conn.cursor()

cur.execute('''
    SELECT matviewname
    FROM pg_matviews
    WHERE schemaname = 'public'
    ORDER BY matviewname
''')

views = cur.fetchall()
print(f'Materialized Views: {len(views)}')
for v in views:
    print(f'  - {v[0]}')

cur.close()
conn.close()
"
```

**Resultado esperado:**
```
Materialized Views: 4
  - mv_athlete_training_summary
  - mv_medical_cases_summary
  - mv_training_performance
  - mv_wellness_summary
```

### 3. Verificar Colunas

```bash
# Via Render Shell
python -c "
import os
import psycopg2

conn = psycopg2.connect(os.environ['DATABASE_URL'])
cur = conn.cursor()

cur.execute('''
    SELECT column_name, data_type, is_nullable
    FROM information_schema.columns
    WHERE table_name = 'training_sessions'
      AND column_name IN ('season_id', 'team_id')
''')

for row in cur.fetchall():
    print(f'{row[0]}: {row[1]} {\"NOT NULL\" if row[2] == \"NO\" else \"NULL\"}')

cur.close()
conn.close()
"
```

**Resultado esperado:**
```
season_id: uuid NOT NULL
team_id: uuid NOT NULL
```

---

## 🔄 REFRESH DE MATERIALIZED VIEWS

### Após Aplicar Migrations

As views estarão vazias (0 rows). Execute refresh:

```bash
# Via Render Shell
cd backend
python -c "
import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()
DATABASE_URL = os.environ['DATABASE_URL']

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

views = [
    'mv_training_performance',
    'mv_athlete_training_summary',
    'mv_wellness_summary',
    'mv_medical_cases_summary'
]

for view in views:
    try:
        cur.execute(f'REFRESH MATERIALIZED VIEW {view}')
        conn.commit()
        print(f'✓ {view} refreshed')
    except Exception as e:
        print(f'✗ {view}: {e}')
        conn.rollback()

cur.close()
conn.close()
"
```

---

## 🐛 CORREÇÃO: Endpoints de Refresh (405 Error)

### Problema nos Logs:
```
→ GET /api/v1/reports/refresh-all - 405
```

### Causa:
Os endpoints de refresh são **POST**, não **GET**!

### Solução:

Use **POST** ao testar:

```bash
# Correto (POST)
curl -X POST "https://hbtrack.onrender.com/api/v1/reports/refresh-all" \
  -H "Authorization: Bearer $JWT_TOKEN"

# Errado (GET) - retorna 405
curl "https://hbtrack.onrender.com/api/v1/reports/refresh-all"
```

### Via API Docs (Swagger):
1. Acesse: https://hbtrack.onrender.com/api/v1/docs
2. Encontre endpoints de refresh
3. Clique em **"Try it out"**
4. Autentique (se necessário)
5. Execute

---

## ✅ CHECKLIST DE VALIDAÇÃO

Após aplicar migrations:

- [ ] `alembic current` mostra `b4b136a1af44`
- [ ] 4 materialized views existem
- [ ] season_id e team_id são NOT NULL
- [ ] `verify_production_rag.py` retorna APROVADO (100%)
- [ ] Endpoints de relatórios funcionam (GET)
- [ ] Endpoints de refresh funcionam (POST)
- [ ] API Docs acessível: https://hbtrack.onrender.com/api/v1/docs

---

## 🎯 PRÓXIMOS PASSOS

### 1. Aplicar Migrations (URGENTE)
Use Opção 1 (Render Shell) para aplicar imediatamente

### 2. Configurar Pre-Deploy Command
Para futuros deploys automáticos

### 3. Testar Endpoints
- GET /api/v1/reports/training-performance ✅
- POST /api/v1/reports/refresh-all ✅

### 4. Configurar Refresh Automático
Cron job para refresh diário das views

---

## 📞 COMANDOS RÁPIDOS

```bash
# 1. Verificar revision atual
alembic -c db/alembic.ini current

# 2. Aplicar todas migrations
alembic -c db/alembic.ini upgrade head

# 3. Validar RAG
python verify_production_rag.py --database-url "$DATABASE_URL"

# 4. Refresh todas views
python -c "from app.services.reports.refresh_service import RefreshService; from app.core.db import get_db; db=next(get_db()); RefreshService.refresh_all(db)"
```

---

**Preparado por:** Claude Sonnet 4.5
**Data:** 2025-12-25
**Prioridade:** 🔴 ALTA - Migrations pendentes