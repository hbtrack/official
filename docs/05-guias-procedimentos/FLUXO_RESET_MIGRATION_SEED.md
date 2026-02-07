<!-- STATUS: NEEDS_REVIEW -->

# 🔄 FLUXO DE RESET + MIGRATION + SEED - CONFIRMAÇÃO DE ENTENDIMENTO

## ✅ ARQUIVOS DA REPO PARA RESET + MIGRATION + SEED

### ESTRUTURA ENCONTRADA:

```
HB Track - Backend/
├── db/
│   ├── alembic/                          ← Migrações do banco
│   │   ├── alembic.ini                   ← Config Alembic
│   │   ├── env.py                        ← Runtime config
│   │   └── versions/
│   │       ├── 0001_prepare_database_extensions.py
│   │       ├── 0002_create_core_tables.py
│   │       ├── ...
│   │       └── 0029_add_athlete_org_id.py  ← ÚLTIMA MIGRAÇÃO
│   │
│   ├── migrations/                       ← SQL manuais (fallback)
│   ├── seeds/                            ← Seed SQL antigos
│   │
│   ├── seed_minimo_oficial.sql           ← ⭐ SEED MÍNIMO (roles, perms, admin)
│   └── seed_test_users.sql               ← ⭐ SEED TESTES (usuários E2E)
│
├── scripts/
│   ├── seed_e2e.py                       ← ⭐ SEED E2E (Python - recomendado)
│   ├── seed_v1_2_initial.py              ← Seed completo V1.2
│   ├── setup_test_user.py                ← Setup usuário teste
│   ├── set_superadmin_password.py        ← Ajusta senha admin
│   └── ... (40+ scripts de validação)
│
└── docker-compose.yml                    ← PostgreSQL config

```

---

## 📋 O FLUXO COMPLETO (3 ETAPAS)

### **ETAPA 1: RESET NO BANCO** 🔴
**Objetivo**: Limpar completamente o banco de dados

**Arquivos envolvidos**:
- `docker-compose.yml` - Define container PostgreSQL
- SQL direto via `psql` ou ORM

**Como executar**:
```bash
# Opção A: Via Docker (mais seguro)
docker-compose down -v  # Remove volume (deleta dados)
docker-compose up -d    # Recria container vazio

# Opção B: Via SQL direto
psql -U hbtrack_dev -d postgres -c "DROP DATABASE IF EXISTS hb_track_e2e CASCADE;"
psql -U hbtrack_dev -d postgres -c "CREATE DATABASE hb_track_e2e;"

# Opção C: Via SQLAlchemy
alembic downgrade base  # Volta para 0 (remove tudo)
```

---

### **ETAPA 2: MIGRATION VIA ALEMBIC** 📊
**Objetivo**: Criar schema do banco (tabelas, índices, triggers)

**Arquivos envolvidos**:
- `db/alembic/alembic.ini` - Configuração Alembic
- `db/alembic/env.py` - Runtime environment
- `db/alembic/versions/*.py` - Todas as 29 migrações

**Como executar**:
```bash
# Subir para a última migração (0029)
cd "HB Track - Backend"
alembic upgrade head

# Ou versão específica
alembic upgrade 0029_add_athlete_org_id

# Verificar status
alembic current
```

**Migrações incluem**:
- 0001-0003: Core tables (users, persons, roles, permissions)
- 0004-0005: Teams, seasons, athletes
- 0006-0007: Training, wellness, matches
- 0008: Triggers e functions
- 0009-0029: Updates, fixes, performance

---

### **ETAPA 3: APLICAÇÃO DE SEED MÍNIMO** 🌱
**Objetivo**: Popular dados mínimos para testes

**Arquivos envolvidos**:

#### **Opção A: SQL (mais rápido)**
- `db/seed_minimo_oficial.sql` - Roles, permissions, superadmin
- `db/seed_test_users.sql` - Usuários E2E (6 users)

```bash
# Aplicar seed SQL
psql -U hbtrack_dev -d hb_track_e2e -f db/seed_minimo_oficial.sql
psql -U hbtrack_dev -d hb_track_e2e -f db/seed_test_users.sql
```

#### **Opção B: Python (mais flexível - RECOMENDADO)**
- `scripts/seed_e2e.py` - Seed idempotente completo (cria usuarios, org, team, season)

```bash
# Aplicar seed Python
python scripts/seed_e2e.py
```

**seed_e2e.py faz**:
- ✅ Cria organização E2E
- ✅ Cria temporada
- ✅ Cria 6 usuários (admin, dirigente, coordenador, coach, atleta, membro)
- ✅ Vincula roles/permissions
- ✅ Idempotente (pode rodar 10x sem duplicar)

---

## 🎯 RESUMO - ARQUIVOS CHAVE

| Etapa | Arquivo | Tipo | Descrição |
|-------|---------|------|-----------|
| **1. RESET** | `docker-compose.yml` | YAML | Infra PostgreSQL |
| **1. RESET** | - | SQL | `DROP DATABASE` |
| **2. MIGRATION** | `db/alembic/alembic.ini` | INI | Config Alembic |
| **2. MIGRATION** | `db/alembic/versions/*.py` | Python | 29 migrações SQL |
| **2. MIGRATION** | `db/alembic/env.py` | Python | Runtime config |
| **3. SEED (SQL)** | `db/seed_minimo_oficial.sql` | SQL | Roles, perms, admin |
| **3. SEED (SQL)** | `db/seed_test_users.sql` | SQL | Usuários E2E |
| **3. SEED (Python)** | `scripts/seed_e2e.py` | Python | Seed completo E2E ⭐ |

---

## 🚀 SCRIPT RECOMENDADO (ALL-IN-ONE)

```bash
#!/bin/bash
# reset-db-e2e.sh

echo "=== ETAPA 1: RESET ==="
docker-compose down -v
docker-compose up -d postgres
sleep 5  # Aguarda postgres iniciar

echo "=== ETAPA 2: MIGRATION ==="
alembic upgrade head

echo "=== ETAPA 3: SEED ==="
python scripts/seed_e2e.py

echo "✅ Banco E2E pronto!"
```

---

## ✅ CONFIRMAÇÃO DE ENTENDIMENTO

**O fluxo é**:

1. **RESET**: Limpa banco completamente
   - Via Docker: `docker-compose down -v && docker-compose up -d`
   - Via SQL: `DROP DATABASE` + `CREATE DATABASE`

2. **MIGRATION**: Cria schema via Alembic
   - `alembic upgrade head` (executa todas as 29 migrações em `db/alembic/versions/`)

3. **SEED**: Popula dados mínimos
   - **Recomendado**: `python scripts/seed_e2e.py` (idempotente, Python)
   - **Alternativa**: `psql -f db/seed_minimo_oficial.sql` + `seed_test_users.sql`

---

## 📝 PRÓXIMOS PASSOS

[ ] Confirmar este entendimento
[ ] Criar script PowerShell que automatiza RESET + MIGRATION + SEED
[ ] Integrar no `test-maestro.ps1` (chamar antes de auth.setup)
[ ] Testar no seu ambiente

**Quer que eu crie o script PowerShell agora?**

