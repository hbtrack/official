# AR_031 — Ambiente SSOT: docs/_canon/contratos/Ambiente.md + gemini.md update

**Status**: ⛔ SUPERSEDED — gemini.md removido do repositório; conteúdo de SSOT absorvido por equivalentes atuais
**Versão do Protocolo**: 1.1.0

## Descrição
ARQUIVOS ALVO:
  (A) CRIAR: docs/_canon/contratos/Ambiente.md
  (B) ATUALIZAR: gemini.md

### Problema
Agentes (Claude, Gemini/Testador, futuros) operam sem saber as versões corretas de Python, PostgreSQL e Redis para local vs VPS. Isso causa:
- Migrations rodando contra PostgreSQL de versão errada
- Testes locais exigindo versão diferente da VPS
- Backups feitos à toa por falta de contexto de ambiente
- Retrabalho recorrente

### Implementação

(A1) CRIAR docs/_canon/contratos/Ambiente.md com o seguinte conteúdo EXATO:

```
# Ambiente HB Track — Especificação Canônica

> **SSOT**: Este arquivo é a fonte canônica de verdade sobre o ambiente de execução do HB Track.
> Todo agente (Arquiteto, Executor, Testador) DEVE ler este arquivo antes de qualquer tarefa
> que envolva ambiente, banco, runtime ou infra.
>
> **Implementação**: AR_031
> **Última atualização**: 2026-02-20

---

## 1. Runtime Python — Canônico

| Componente        | Versão Canônica | Fonte                      |
|-------------------|-----------------|----------------------------|
| **Python**        | **3.11.9**      | `api.md` (SSOT operacional)|
| FastAPI           | 0.127.0         | `requirements.txt`         |
| SQLAlchemy        | 2.0.45          | `requirements.txt`         |
| Alembic           | 1.17.2          | `requirements.txt`         |
| Celery            | 5.3.4           | `requirements.txt`         |
| psycopg (async)   | 3.3.2           | `requirements.txt`         |
| psycopg2-binary   | 2.9.11          | `requirements.txt`         |
| redis (py client) | 5.0.1           | `requirements.txt`         |

> **REGRA**: Python 3.11.9 é mandatório em local e VPS. Qualquer outra versão => BLOCKED_INPUT (4).

---

## 2. Ambiente LOCAL (Desenvolvimento)

| Serviço    | Imagem/Versão      | Porta host→container | Container              |
|------------|--------------------|-----------------------|------------------------|
| PostgreSQL | **postgres:12**    | **5433 → 5432**       | hbtrack-postgres-dev   |
| Redis      | **redis:7-alpine** | 6379 → 6379           | hbtrack-redis-dev      |

**Credenciais locais** (dev only, nunca usar em VPS):
- Database: `hb_track_dev`
- User: `hbtrack_dev`
- Password: `hbtrack_dev_pwd`
- Host: `localhost:5433`

**Como iniciar serviços locais**:
```bash
docker-compose -f infra/docker-compose.yml up -d
```

**Fonte**: `infra/docker-compose.yml`

---

## 3. Ambiente VPS (Produção / Homologação)

| Serviço    | Versão          | Status                              |
|------------|-----------------|--------------------------------------|
| Python     | 3.11.x (apt)    | Playbook: `docs/playbooks/pb_vps_python_runtime.md` |
| PostgreSQL | **[A PREENCHER pelo Arquiteto após verificação na VPS]** | PENDENTE |
| Redis      | **[A PREENCHER pelo Arquiteto após verificação na VPS]** | PENDENTE |

> **REGRA PARA AGENTES**: Se qualquer campo acima ainda contiver `[A PREENCHER]`,
> BLOQUEIE qualquer tarefa de migration VPS / deploy / backup e retorne BLOCKED_INPUT (4).
> Exija que o Arquiteto preencha esta seção com as versões reais da VPS.

**Playbooks e diagnósticos VPS**:
- Verificação de runtime Python: `docs/playbooks/pb_vps_python_runtime.md`
- Script diagnóstico: `scripts/diagnostics/runtime/diag_vps_python_runtime.sh`

---

## 4. Regras Críticas para Todos os Agentes

1. **Python 3.11.9 mandatório** — local e VPS. Verificar antes de qualquer execução.
2. **PostgreSQL local = 12** (docker porta 5433). Migrations MUST ser compatíveis com pg12+.
3. **psycopg2 e psycopg3 coexistem** no `requirements.txt` — NUNCA remover nenhum deles.
4. **Porta local PostgreSQL = 5433** — não é a porta padrão 5432. Configurar corretamente no `.env`.
5. **Alembic migrations**: sempre rodar com o Python do venv, não o Python do sistema.
6. **Backup**: PROIBIDO fazer backup sem confirmar a versão do PostgreSQL (local ≠ VPS).
7. **VPS deploy**: PROIBIDO sem preencher a seção §3 deste documento.

---

## 5. Self-Check de Ambiente (Agentes devem rodar antes de tarefas de DB/infra)

```bash
# Verificar Python canônico
python --version
# Expected: Python 3.11.x

# Verificar drivers de banco
python -c "import psycopg; print('psycopg:', psycopg.__version__)"
python -c "import psycopg2; print('psycopg2:', psycopg2.__version__)"

# Verificar SQLAlchemy
python -c "import sqlalchemy; print('sqlalchemy:', sqlalchemy.__version__)"

# Verificar conexão local (requer docker-compose up)
python -c "import psycopg; conn=psycopg.connect('host=localhost port=5433 dbname=hb_track_dev user=hbtrack_dev password=hbtrack_dev_pwd'); print('DB OK'); conn.close()"
```

---

## 6. Changelog

| Versão | Data       | Descrição                                      |
|--------|------------|------------------------------------------------|
| 1.0.0  | 2026-02-20 | Criação inicial — AR_031                       |
```

(B1) ATUALIZAR gemini.md — ADICIONAR a seguinte linha ANTES da última linha existente (`**LER** DOCS/HBTRACK/MANUAIS/...`):

**LER** `DOCS/_CANON/CONTRATOS/Ambiente.md` ANTES de qualquer teste que envolva banco, runtime ou infra. Se VPS_PG_VERSION contiver '[A PREENCHER]', retorne BLOCKED.

NÃO remover nenhuma linha existente do gemini.md.

## Critérios de Aceite
1) docs/_canon/contratos/Ambiente.md existe. 2) Contém 'Python' e '3.11.9'. 3) Contém 'postgres:12'. 4) Contém 'redis:7-alpine'. 5) Contém porta '5433'. 6) Contém 'SSOT'. 7) Contém 'A PREENCHER' (placeholder VPS ativo). 8) Contém 'BLOCKED_INPUT' ou 'BLOCKED'. 9) gemini.md contém referência a 'Ambiente.md'.

## Validation Command (Contrato)
```
python -c "import pathlib; a=pathlib.Path('docs/_canon/contratos/Ambiente.md'); assert a.exists(),'FAIL: Ambiente.md nao existe'; c=a.read_text(encoding='utf-8'); assert '3.11.9' in c,'FAIL: Python 3.11.9 nao documentado'; assert 'postgres:12' in c,'FAIL: postgres:12 nao documentado'; assert 'redis:7-alpine' in c,'FAIL: redis:7-alpine nao documentado'; assert '5433' in c,'FAIL: porta 5433 nao documentada'; assert 'SSOT' in c,'FAIL: nao marcado como SSOT'; assert 'A PREENCHER' in c,'FAIL: placeholder VPS ausente'; gm=pathlib.Path('gemini.md'); assert gm.exists(),'FAIL: gemini.md nao existe'; gmc=gm.read_text(encoding='utf-8'); assert 'Ambiente' in gmc,'FAIL: gemini.md nao referencia Ambiente.md'; print('PASS: Ambiente SSOT criado corretamente e gemini.md atualizado')"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_031_ambiente_ssot.log`

## Rollback Plan (Contrato)
```
git revert HEAD (se já commitado) ou: git restore gemini.md && git rm docs/_canon/contratos/Ambiente.md
```
⚠️ **ATENÇÃO**: Este AR modifica banco. Execute rollback em caso de falha.

## Riscos
- Seção §3 VPS ficará com placeholders até Arquiteto preencher após verificação na VPS — isso é INTENCIONAL
- gemini.md é instrução do agente Testador (Gemini 2.5 Flash) — adicionar apenas UMA linha sem remover nada
- O documento NÃO deve conter credenciais de VPS — apenas estrutura e placeholders
- Porta 5433 é crítica: documentar claramente que não é a porta padrão 5432
- psycopg2 e psycopg3 coexistência é intencional — documentar para evitar que agentes removam um deles

## Análise de Impacto
_(A ser preenchido pelo Executor)_

---
## Carimbo de Execução
_(Gerado por hb report)_


### Execução em b2e7523
**Status Final**: ✅ SUCESSO
**Comando**: `python -c "import pathlib; a=pathlib.Path('docs/_canon/contratos/Ambiente.md'); assert a.exists(),'FAIL: Ambiente.md nao existe'; c=a.read_text(encoding='utf-8'); assert '3.11.9' in c,'FAIL: Python 3.11.9 nao documentado'; assert 'postgres:12' in c,'FAIL: postgres:12 nao documentado'; assert 'redis:7-alpine' in c,'FAIL: redis:7-alpine nao documentado'; assert '5433' in c,'FAIL: porta 5433 nao documentada'; assert 'SSOT' in c,'FAIL: nao marcado como SSOT'; assert 'A PREENCHER' in c,'FAIL: placeholder VPS ausente'; gm=pathlib.Path('gemini.md'); assert gm.exists(),'FAIL: gemini.md nao existe'; gmc=gm.read_text(encoding='utf-8'); assert 'Ambiente' in gmc,'FAIL: gemini.md nao referencia Ambiente.md'; print('PASS: Ambiente SSOT criado corretamente e gemini.md atualizado')"`
**Exit Code**: 0
**Evidence File**: `docs/hbtrack/evidence/AR_031_ambiente_ssot.log`
**Python Version**: 3.11.9


### Verificacao Testador em b2e7523
**Status Testador**: 🔴 REJEITADO
**Consistency**: AH_DIVERGENCE
**Triple-Run**: TRIPLE_FAIL (3x)
**Exit Testador**: 1 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_031_b2e7523/result.json`
