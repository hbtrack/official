<!-- STATUS: NEEDS_REVIEW | verificar contra schema.sql -->

# 🗄️ Estrutura de Banco de Dados - HB Track

## 📊 Banco Único de Desenvolvimento

**Todas as operações apontam para:**

```
Host: localhost
Port: 5433
Database: hb_track_dev
User: hbtrack_dev
Password: hbtrack_dev_pwd
```

### ✅ Visível no DBeaver

Abra o DBeaver e conecte em `localhost:5433/hb_track_dev` para ver todas as alterações em tempo real.

---

## 🔧 Configuração (.env)

```dotenv
# APP (FastAPI - asyncpg)
DATABASE_URL=postgresql+asyncpg://hbtrack_dev:hbtrack_dev_pwd@localhost:5433/hb_track_dev

# MIGRATIONS / SEED (Alembic + psycopg2)
DATABASE_URL_SYNC=postgresql+psycopg2://hbtrack_dev:hbtrack_dev_pwd@localhost:5433/hb_track_dev
```

---

## 🚀 Scripts Disponíveis

### 1️⃣ **Reset do Banco** (desenvolvimento)

```powershell
cd "c:\HB TRACK\Hb Track - Backend"
.\reset-hb-track-dev.ps1
```

**O que faz:**
1. Dropa e recria o schema `public` (limpa todas as tabelas)
2. Aplica migrations via Alembic
3. Executa seeds (dados iniciais)

**Quando usar:**
- Banco está inconsistente
- Quer começar do zero
- Mudanças nas migrations/seeds

**✅ CORRIGIDO:** Erro "relation 'competitions' does not exist" resolvido via migração 0031

---

### 2️⃣ **Reset + Start (Backend + Frontend)**

```powershell
cd "c:\HB TRACK"
.\reset-and-start.ps1
```

**O que faz:**
1. Executa `reset-hb-track-dev.ps1`
2. Inicia backend na porta 8000
3. Inicia frontend na porta 3000

**Quando usar:**
- Testes manuais do zero
- Desenvolvimento de features
- Validação end-to-end

---

### 3️⃣ **Apenas Iniciar Backend**

```powershell
cd "c:\HB TRACK\Hb Track - Backend"
python -m uvicorn app.main:app --reload --port 8000
```

**Quando usar:**
- Banco já está OK
- Apenas codificando
- Debug rápido

---

## 🧪 Testes

### Testes Unitários/Integração

```powershell
cd "c:\HB TRACK\Hb Track - Backend"
pytest tests/ -v
```

**Banco usado:** `hb_track_dev` (via `.env`)

### Testes E2E (Frontend)

```powershell
cd "c:\HB TRACK\Hb Track - Fronted"
npm run test:e2e
```

**Banco usado:** `hb_track_dev` (via backend)

---

## 📁 Arquivos Importantes

| Arquivo | Propósito |
|---------|-----------|
| [`Hb Track - Backend\.env`](c:\HB TRACK\Hb Track - Backend\.env) | Configuração do banco (DATABASE_URL, DATABASE_URL_SYNC) |
| [`Hb Track - Backend\reset-hb-track-dev.ps1`](c:\HB TRACK\Hb Track - Backend\reset-hb-track-dev.ps1) | Reset completo do banco |
| [`reset-and-start.ps1`](c:\HB TRACK\reset-and-start.ps1) | Reset + iniciar backend/frontend |
| [`Hb Track - Backend\db\alembic\env.py`](c:\HB TRACK\Hb Track - Backend\db\alembic\env.py) | Configuração do Alembic (usa DATABASE_URL_SYNC) |
| [`Hb Track - Backend\_archived_e2e\`](c:\HB TRACK\Hb Track - Backend\_archived_e2e) | Scripts E2E obsoletos (ignorar) |

---

## ⚠️ Importante

### ✅ SIM - Use Sempre

- **Banco:** `hb_track_dev` (porta 5433)
- **Scripts:** `reset-hb-track-dev.ps1`, `reset-and-start.ps1`
- **DBeaver:** Sempre conectado em `hb_track_dev`

### ❌ NÃO - Evite

- ~~Criar novos bancos (e2e, test, etc.)~~
- ~~Scripts na pasta `_archived_e2e`~~
- ~~Hardcoded DATABASE_URL nos scripts~~

---

## 🔍 Troubleshooting

### Problema: "Tabelas não aparecem no DBeaver"

```powershell
# Resetar banco
.\reset-hb-track-dev.ps1

# Refresh no DBeaver (F5)
```

### Problema: "Migrations falharam"

```powershell
# Verificar .env
Get-Content .env | Select-String "DATABASE_URL"

# Deve mostrar:
# DATABASE_URL_SYNC=postgresql+psycopg2://...hb_track_dev
```

### Problema: "Backend não conecta"

```powershell
# Verificar se PostgreSQL está rodando
docker ps | Select-String "postgres"

# Se não estiver, iniciar
cd "c:\HB TRACK\infra"
docker-compose up -d
```

---

## 📚 Fluxo de Trabalho Recomendado

```mermaid
graph TD
    A[Iniciar Desenvolvimento] --> B{Banco OK?}
    B -->|Sim| C[Iniciar Backend]
    B -->|Não| D[./reset-hb-track-dev.ps1]
    D --> C
    C --> E[Codificar/Testar]
    E --> F{Precisa Resetar?}
    F -->|Sim| D
    F -->|Não| E
```

---

## 🎯 Resultado

**Um único banco, visível no DBeaver, usado por:**
- ✅ Backend (desenvolvimento)
- ✅ Migrations (Alembic)
- ✅ Seeds (dados iniciais)
- ✅ Testes (pytest)
- ✅ Frontend (via backend)

**Sem confusão de múltiplos bancos!** 🚀
