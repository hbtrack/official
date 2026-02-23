# Ambiente HB Track — Especificação Canônica

> **SSOT**: Este arquivo é a fonte canônica de verdade sobre o ambiente de execução do HB Track.
> Todo agente (Arquiteto, Executor, Testador) DEVE ler este arquivo antes de qualquer tarefa
> que envolva ambiente, banco, runtime ou infra.
>
> **Implementação**: AR_031
> **Última atualização**: 2026-02-21

---

## 1. Runtime Python — Canônico

| Componente        | Versão Canônica | Fonte                       |
|-------------------|-----------------|-----------------------------|
| **Python**        | **3.11.9**      | `api.md` (SSOT operacional) |
| FastAPI           | 0.127.0         | `requirements.txt`          |
| SQLAlchemy        | 2.0.45          | `requirements.txt`          |
| Alembic           | 1.17.2          | `requirements.txt`          |
| Celery            | 5.3.4           | `requirements.txt`          |
| psycopg (async)   | 3.3.2           | `requirements.txt`          |
| psycopg2-binary   | 2.9.11          | `requirements.txt`          |
| redis (py client) | 5.0.1           | `requirements.txt`          |

> **REGRA**: Python 3.11.9 é mandatório em local e VPS. Qualquer outra versão => BLOCKED_INPUT (4).

---

## 2. Ambiente LOCAL (Desenvolvimento)

| Serviço    | Imagem/Versão      | Porta host→container | Container            |
|------------|--------------------|-----------------------|----------------------|
| PostgreSQL | **postgres:12**    | **5433 → 5432**       | hbtrack-postgres-dev |
| Redis      | **redis:7-alpine** | 6379 → 6379           | hbtrack-redis-dev    |

**Credenciais locais** (dev only — NUNCA usar em VPS):
- Database: `hb_track_dev`
- User: `hbtrack_dev`
- Password: ver `.env.local` ou `.env.example`
- Host: `localhost:5433`

**Como iniciar serviços locais**:
```bash
docker-compose -f infra/docker-compose.yml up -d
```

**Fonte**: `infra/docker-compose.yml`

---

## 3. Ambiente VPS (Produção / Homologação)

> **Estado em 2026-02-21**: PostgreSQL upgrade 12 → 15 concluído via Docker (AR implícita, log em `VPS/runbooks/UPGRADE_PG15_EXECUTION_LOG.md`).

| Serviço    | Imagem/Versão         | Porta  | Container    | Volume                              |
|------------|-----------------------|--------|--------------|--------------------------------------|
| PostgreSQL | **postgres:15.16**    | **5432** | `postgres15` | `/var/lib/postgresql/docker/15`     |
| Redis      | **[A PREENCHER]**     | —      | —            | —                                    |

**OS VPS**: Ubuntu 20.04.6 LTS (focal)
**Docker VPS**: 26.1.3 (ativo, restart habilitado)

**Bancos disponíveis (PostgreSQL 15.16):**
| Banco            | Ambiente   | Tamanho | Tabelas | Última migration |
|------------------|------------|---------|---------|------------------|
| `hb_track`       | staging    | 12 MB   | 67      | 0055 (soft delete) |
| `hb_track_prod`  | produção   | 12 MB   | 67      | 0055 (soft delete) |

**Credenciais VPS**: ver `.env.production` ou `VPS/infra/POSTGRESQL_CONNECTIONS.md`
- Host: `191.252.185.34`
- Port: `5432`
- User: `hbtrack_app`
- Password: **NUNCA hardcodar — usar variável de ambiente**

> **REGRA PARA AGENTES**: Se Redis VPS ainda contiver `[A PREENCHER]`,
> BLOQUEIE qualquer tarefa de Celery/Redis na VPS e retorne BLOCKED_INPUT (4).
> Exija que o Arquiteto preencha esta seção com a versão real.

**Playbooks e diagnósticos VPS**:
- Verificação de runtime Python: `docs/playbooks/pb_vps_python_runtime.md`
- Script diagnóstico: `scripts/diagnostics/runtime/diag_vps_python_runtime.sh`
- Log do upgrade PostgreSQL: `VPS/runbooks/UPGRADE_PG15_EXECUTION_LOG.md`

---

## 4. Regras Críticas para Todos os Agentes

1. **Python 3.11.9 mandatório** — local e VPS. Verificar antes de qualquer execução.
2. **PostgreSQL local = 12** (docker porta **5433**). Migrations MUST ser compatíveis com pg12+.
3. **PostgreSQL VPS = 15.16** (docker porta **5432** — padrão). Deploy e migrations apontam para este.
4. **Porta local ≠ porta VPS**: local=5433, VPS=5432. Nunca trocar as duas.
5. **psycopg2 e psycopg3 coexistem** no `requirements.txt` — NUNCA remover nenhum deles.
6. **Alembic migrations**: sempre rodar com o Python do venv, não o Python do sistema.
7. **Backup**: PROIBIDO fazer backup VPS sem confirmar que o container `postgres15` está ativo.
8. **Credenciais**: NUNCA hardcodar senha em docs ou código. Usar `.env` sempre.
9. **PostgreSQL 12 VPS**: parado e desabilitado (cluster em `/var/lib/postgresql/12/main`). NÃO reativar sem autorização do Arquiteto.

---

## 5. Self-Check de Ambiente (rodar antes de tarefas de DB/infra)

```bash
# Verificar Python canônico
python --version
# Expected: Python 3.11.x

# Verificar drivers de banco
python -c "import psycopg; print('psycopg:', psycopg.__version__)"
python -c "import psycopg2; print('psycopg2:', psycopg2.__version__)"

# Verificar SQLAlchemy
python -c "import sqlalchemy; print('sqlalchemy:', sqlalchemy.__version__)"

# Verificar conexão LOCAL (requer docker-compose up)
python -c "import psycopg; conn=psycopg.connect('host=localhost port=5433 dbname=hb_track_dev user=hbtrack_dev password=hbtrack_dev_pwd'); print('DB LOCAL OK'); conn.close()"

# Verificar container VPS PostgreSQL ativo (rodar na VPS)
sudo docker ps --filter name=postgres15 --format "{{.Status}}"
# Expected: Up X hours
```

---

## 6. Changelog

| Versão | Data       | Descrição                                                       |
|--------|------------|-----------------------------------------------------------------|
| 1.0.0  | 2026-02-20 | Criação inicial — AR_031 (local env)                           |
| 1.1.0  | 2026-02-21 | VPS atualizado: PostgreSQL 15.16 (Docker) confirmado via runbook |
