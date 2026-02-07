<!-- STATUS: NEEDS_REVIEW -->

# 🆓 SOLUÇÃO PARA RENDER FREE TIER - Migrations

**Problema:** Render Free Tier não tem Shell nem Pre-Deploy Command
**Solução:** Migrations via Start Command + Endpoint de Setup

---

## 🎯 SOLUÇÃO: Aplicar Migrations no Start Command

### Opção 1: Modificar Start Command (RECOMENDADO)

**No Render Dashboard → Settings → Build & Deploy:**

**Start Command atual:**
```bash
gunicorn -w 2 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:$PORT
```

**Modificar para:**
```bash
alembic -c db/alembic.ini upgrade head && gunicorn -w 2 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:$PORT
```

**O que faz:**
1. Executa migrations (`alembic upgrade head`)
2. **E então** (`&&`) inicia o servidor
3. Se migrations falharem, servidor não inicia (segurança!)

**Aplicar mudança:**
1. Salvar configuração no Render
2. Render fará redeploy automático
3. Migrations serão aplicadas na inicialização

---

## ⚠️ IMPORTANTE: Root Directory

Certifique-se que **Root Directory** está configurado como:
```
backend
```

Se não estiver, o comando `alembic -c db/alembic.ini` não encontrará o arquivo!

---

## 📋 PASSO A PASSO

### 1. Acessar Render Dashboard
https://dashboard.render.com

### 2. Selecionar Serviço "HbTrack"

### 3. Ir em Settings → Build & Deploy

### 4. Modificar Start Command

**Colar:**
```bash
alembic -c db/alembic.ini upgrade head && gunicorn -w 2 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:$PORT
```

### 5. Salvar

Clique em **"Save Changes"**

### 6. Aguardar Redeploy

Render fará redeploy automático. Aguarde ~2-3 minutos.

### 7. Verificar Logs

Procure por:
```
INFO alembic.runtime.migration Running upgrade ... -> b4b136a1af44
```

Se aparecer, migrations foram aplicadas! ✅

---

## 🔄 Opção 2: Endpoint de Setup (Alternativa)

Se não quiser rodar migrations toda vez que o servidor inicia, podemos criar um endpoint de setup que você chama manualmente.

### Criar Endpoint de Setup

Arquivo: `backend/app/api/v1/routers/setup.py`

```python
"""
Router para setup inicial (migrations, etc.)
ATENÇÃO: Proteger em produção!
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.db import get_db
import subprocess
import os

router = APIRouter(prefix="/setup", tags=["Setup"])

@router.post("/migrate")
async def run_migrations():
    """
    Executa migrations do Alembic.

    ATENÇÃO: Este endpoint deve ser protegido em produção!
    Use apenas em deploy inicial ou manutenção.
    """
    try:
        # Mudar para diretório backend se necessário
        original_dir = os.getcwd()

        # Executar alembic upgrade
        result = subprocess.run(
            ["alembic", "-c", "db/alembic.ini", "upgrade", "head"],
            capture_output=True,
            text=True,
            timeout=300  # 5 minutos timeout
        )

        if result.returncode == 0:
            return {
                "status": "success",
                "message": "Migrations aplicadas com sucesso",
                "output": result.stdout
            }
        else:
            return {
                "status": "error",
                "message": "Erro ao aplicar migrations",
                "error": result.stderr
            }

    except subprocess.TimeoutExpired:
        return {
            "status": "error",
            "message": "Timeout ao executar migrations"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Erro inesperado: {str(e)}"
        }

@router.get("/current")
async def get_current_revision():
    """Retorna revision atual do banco."""
    try:
        result = subprocess.run(
            ["alembic", "-c", "db/alembic.ini", "current"],
            capture_output=True,
            text=True
        )

        return {
            "revision": result.stdout.strip(),
            "output": result.stdout
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
```

**Registrar no `__init__.py`:**
```python
from app.api.v1.routers import setup

api_router.include_router(setup.router)
```

**Usar:**
```bash
# Aplicar migrations
curl -X POST "https://hbtrack.onrender.com/api/v1/setup/migrate"

# Verificar revision
curl "https://hbtrack.onrender.com/api/v1/setup/current"
```

⚠️ **IMPORTANTE:** Proteja este endpoint em produção com autenticação!

---

## ✅ RECOMENDAÇÃO: Use Opção 1 (Start Command)

**Por quê?**
- ✅ Mais simples
- ✅ Não requer código adicional
- ✅ Migrations sempre aplicadas antes do servidor iniciar
- ✅ Seguro (servidor não inicia se migration falhar)
- ✅ Funciona em Free Tier

**Desvantagem:**
- Migrations rodadas toda vez que servidor reinicia
- Para evitar, podemos adicionar check no Alembic

---

## 🔍 VERIFICAR SE FUNCIONOU

Após modificar Start Command e redeploy, verifique logs:

### 1. Logs do Render

Procurar por:
```
INFO alembic.runtime.migration Context impl PostgresqlImpl.
INFO alembic.runtime.migration Will assume transactional DDL.
INFO alembic.runtime.migration Running upgrade 4af09f9d46a0 -> 5c90cfd7e291
INFO alembic.runtime.migration Running upgrade 5c90cfd7e291 -> 92365c111182
...
INFO alembic.runtime.migration Running upgrade 8fba6a22b58c -> b4b136a1af44
```

### 2. Testar Endpoint

```bash
# Verificar views existem
curl "https://hbtrack.onrender.com/api/v1/reports/stats"
```

Se retornar 4 views, migrations foram aplicadas! ✅

---

## 🐛 TROUBLESHOOTING

### Problema: Alembic não encontrado

**Erro:**
```
alembic: command not found
```

**Solução:**
Usar caminho completo do Python:
```bash
python -m alembic -c db/alembic.ini upgrade head && gunicorn ...
```

### Problema: Arquivo alembic.ini não encontrado

**Erro:**
```
FileNotFoundError: db/alembic.ini
```

**Solução:**
Verificar Root Directory está como `backend`:
- Render Dashboard → Settings → Root Directory: `backend`

### Problema: DATABASE_URL não está definida

**Erro:**
```
sqlalchemy.exc.ArgumentError: Could not parse database URL
```

**Solução:**
Verificar Environment Variables:
- Render Dashboard → Environment → DATABASE_URL

---

## 📊 COMPARAÇÃO DE OPÇÕES

| Método | Pros | Cons | Recomendado |
|--------|------|------|-------------|
| **Start Command** | ✅ Simples<br>✅ Free tier<br>✅ Seguro | ⚠️ Roda toda vez | ⭐ **SIM** |
| **Endpoint Setup** | ✅ Controle manual<br>✅ Roda 1x | ⚠️ Precisa proteger<br>⚠️ Código extra | Não |
| **Pre-Deploy** | ✅ Ideal | ❌ Pago | Não (free tier) |
| **Shell** | ✅ Flexível | ❌ Pago | Não (free tier) |

---

## 🎯 AÇÃO IMEDIATA

### Passo a Passo Rápido:

1. Acesse: https://dashboard.render.com
2. Selecione "HbTrack"
3. Settings → Build & Deploy → Start Command
4. Cole:
   ```bash
   alembic -c db/alembic.ini upgrade head && gunicorn -w 2 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:$PORT
   ```
5. Save Changes
6. Aguarde redeploy (~2 min)
7. Verifique logs por: `Running upgrade ... -> b4b136a1af44`
8. Teste: `curl https://hbtrack.onrender.com/api/v1/reports/stats`

---

## ✅ RESULTADO ESPERADO

Após aplicar:

**Logs do Render:**
```
INFO alembic.runtime.migration Running upgrade 4af09f9d46a0 -> 5c90cfd7e291
INFO alembic.runtime.migration Running upgrade 5c90cfd7e291 -> 92365c111182
INFO alembic.runtime.migration Running upgrade 92365c111182 -> 6086f19465e1
INFO alembic.runtime.migration Running upgrade 6086f19465e1 -> bb97d068b643
INFO alembic.runtime.migration Running upgrade bb97d068b643 -> 8fba6a22b58c
INFO alembic.runtime.migration Running upgrade 8fba6a22b58c -> b4b136a1af44
[INFO] Starting gunicorn 21.2.0
[INFO] Listening at: http://0.0.0.0:10000
```

**Teste de API:**
```bash
curl "https://hbtrack.onrender.com/api/v1/reports/stats"
```

**Resposta esperada:**
```json
{
  "training_performance": {
    "view_name": "mv_training_performance",
    "rows": 0
  },
  "athlete_training_summary": {
    "view_name": "mv_athlete_training_summary",
    "rows": 0
  },
  "wellness_summary": {
    "view_name": "mv_wellness_summary",
    "rows": 0
  },
  "medical_cases_summary": {
    "view_name": "mv_medical_cases_summary",
    "rows": 0
  }
}
```

---

**Preparado por:** Claude Sonnet 4.5
**Data:** 2025-12-25
**Versão:** Free Tier Solution v1.0