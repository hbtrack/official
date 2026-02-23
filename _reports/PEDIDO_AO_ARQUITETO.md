# Pedido ao Arquiteto — PostgreSQL Upgrade Bloqueado

**Documento:** `_reports/PEDIDO_AO_ARQUITETO.md`  
**Data:** 2026-02-21 06:15 BRT  
**Agente:** Executor  
**Status:** ⚠️ BLOCKED_INPUT (Exit Code 4)  
**Contexto:** AR_008 bloqueado por requisito PostgreSQL 15+, tentativa de upgrade VPS falhou

---

## SUMÁRIO EXECUTIVO

**Bloqueio:** Impossível instalar PostgreSQL 15 no VPS via método APT (repositório oficial PostgreSQL descontinuou Ubuntu 20.04).

**Impacto:** 
- AR_008 permanece em 🏗️ EM_EXECUCAO (exit code 1)
- BATCH_004 (AR_028/029/030) ✅ VERIFICADO mas não pode ser commitado
- `hb check --mode manual` falha por E_SSOT_NO_VALID_AR (schema.sql staged sem AR válida)

**Decisão Requerida:** Escolher estratégia entre 4 opções (A/B/C/D) para desbloquear AR_008.

---

## CONTEXTO COMPLETO

### Estado Atual

**VPS (vps63621):**
- OS: Ubuntu 20.04.6 LTS (focal)
- PostgreSQL atual: 12.22 (port 5432, cluster "main" online)
- PostgreSQL alvo: 15.x (não instalado)
- Aplicação: hbtrack-backend **PARADA** desde 2026-02-21 02:42
- Backup: ✅ Seguro em `/backups/hbtrack/upgrade_pg15_20260221_0259/` (356KB dump validado)

**AR_008 (Migration 0055):**
- Status: 🏗️ EM_EXECUCAO
- Exit Code: 1 (FAILED)
- Teste falhando: `test_rdb1_postgresql_version` (espera PG 15+, obtém 12.22)
- SSOT touched: `docs/ssot/schema.sql` (12 alterações STAGED, não marcadas `[x]`)

**BATCH_004:**
- AR_028 (HBLock): ✅ VERIFICADO (hash: 0c16f109)
- AR_029 (Evidence Integrity): ✅ VERIFICADO (hash: c391adbb)
- AR_030 (Dev Flow v1.1.0): ✅ VERIFICADO (hash: 9f9549ed)
- Commit: ❌ BLOQUEADO por `hb check` (E_SSOT_NO_VALID_AR devido AR_008)

### Histórico da Tentativa de Upgrade

**Fase 1 (Backup):** ✅ COMPLETO (02:42-02:59)
- Aplicação parada
- Dump criado: 356,019 bytes
- Configs salvos: postgresql.conf, pg_hba.conf

**Fase 2 (Instalação PG 15):** ❌ BLOQUEADO (02:59-06:15)
- Script automatizado falhou: `sudo apt install postgresql-15` → 404 Not Found
- Diagnóstico executado (10 comandos):
  - ✅ Verificado: Ubuntu 20.04.6 LTS (focal)
  - ✅ Removido: `/etc/apt/sources.list.d/pgdg.list` (config antiga)
  - ✅ Removido: `/usr/share/keyrings/postgresql-keyring.gpg` (keyring antiga)
  - ✅ Adicionado: GPG key PostgreSQL oficial
  - ✅ Criado: `/etc/apt/sources.list.d/pgdg.list` com `deb http://apt.postgresql.org/pub/repos/apt/ focal-pgdg main`
  - ❌ `sudo apt update` → **404 Not Found: focal-pgdg Release file**
  - ✅ Verificado: Repositório PostgreSQL acessível (HTTP 200)
  - ❌ Confirmado: `focal-pgdg` **não existe** (removed from official repository)
  - ✅ Listado: Distribuições disponíveis (jammy, noble, bookworm, bullseye) — **focal ausente**
  - ⚠️ Verificado: Repositório Ubuntu padrão oferece **apenas PostgreSQL 12**

**Causa Raiz:** PostgreSQL descontinuou suporte APT ao Ubuntu 20.04 (focal). Apenas versões LTS mais recentes são suportadas (22.04+).

---

## OPÇÕES DISPONÍVEIS

### Opção A: Compilar PostgreSQL 15 do Fonte ⏱️ 60-90 min

**Descrição:** Build manual do PostgreSQL 15.6 a partir do tarball oficial.

**Prós:**
- ✅ Controle total sobre instalação
- ✅ Versão exata (15.6 latest stable)
- ✅ Não requer upgrade do OS

**Contras:**
- ❌ Tempo de compilação: 60-90 minutos
- ❌ ~30 dependências de build necessárias
- ❌ Complexidade: systemd unit custom, gerenciamento manual
- ❌ Atualizações futuras: manuais (não via APT)

**Impacto:**
- Downtime adicional: ~2 horas (compilação + migração)
- Aplicação PARADA: já 4h, seriam +2h (total ~6h)
- Risco: Médio (compilação pode falhar por dependências)

**Passos:** Documentados em `VPS/runbooks/POSTGRESQL_UPGRADE.md` seção "Compilação Manual".

---

### Opção B: Upgrade Ubuntu 20.04 → 22.04 (jammy) ⚠️ ARRISCADO

**Descrição:** Upgrade completo do OS para Ubuntu 22.04 LTS (jammy), então instalar PG 15 via APT.

**Prós:**
- ✅ Resolve permanentemente (jammy-pgdg existe)
- ✅ Acesso oficial a PostgreSQL 15+
- ✅ Futuras atualizações via APT (automático)
- ✅ Mantém VPS atualizado long-term

**Contras:**
- ❌ Risco **ALTO**: upgrade OS pode quebrar sistema
- ❌ Downtime extenso: 1-2 horas (upgrade + testes)
- ❌ Requer backup **COMPLETO** do VPS (não só banco)
- ❌ Pode quebrar outras dependências (Python 3.11, Uvicorn, etc)
- ❌ Irreversível (rollback complexo)

**Impacto:**
- Downtime adicional: ~2-3 horas
- Aplicação PARADA: já 4h, seriam +3h (total ~7h)
- Risco: **ALTO** (ambiente de teste, mas pode inviabilizar VPS)

**Pré-requisitos:**
- Backup completo VPS (não só banco)
- Plano de contingência se VPS ficar inacessível
- Validação de compatibilidade: Python 3.11, dependências backend

**Comando:** `sudo do-release-upgrade`

---

### Opção C: Docker PostgreSQL 15 🐳 (se disponível)

**Descrição:** Rodar PostgreSQL 15 em container Docker, preservar PG 12 nativo como fallback.

**Prós:**
- ✅ Rápido: ~20 minutos (se Docker já instalado)
- ✅ Isolado: não afeta OS nem PG 12
- ✅ Reproduzível (docker-compose)
- ✅ Rollback fácil: parar container

**Contras:**
- ❌ Requer Docker instalado no VPS (verificar)
- ❌ Configuração adicional: volumes, network, migração
- ❌ Persistência: volumes Docker vs diretórios tradicionais
- ❌ Mais complexidade operacional (Docker + PG 12 nativo)

**Impacto:**
- Downtime adicional: ~30-60 minutos (se Docker disponível)
- Aplicação PARADA: já 4h, seria +1h (total ~5h)
- Risco: Baixo (container isolado, PG 12 preservado)

**Pré-requisito:** Verificar se Docker está instalado no VPS.

**Comando:**
```bash
docker run -d --name postgres15 \
  -e POSTGRES_USER=hbtrack_app \
  -e POSTGRES_PASSWORD=13Lyb6DDelb7y16ZFPcdkCQi \
  -e POSTGRES_DB=hb_track \
  -p 5432:5432 \
  -v /var/lib/postgresql/docker/15:/var/lib/postgresql/data \
  postgres:15
```

---

### Opção D: Ajustar Teste (Reverter Decisão) ⚡ 5 min

**Descrição:** Modificar `test_rdb1_postgresql_version` para aceitar PostgreSQL 12 temporariamente, documentar como dívida técnica.

**Prós:**
- ✅ Desbloqueia AR_008 **imediatamente** (5 minutos)
- ✅ Permite commit de BATCH_004 (trabalho já completo)
- ✅ Zero downtime adicional
- ✅ Aplicação pode ser reiniciada (já 4h parada)
- ✅ Risco zero (mudança local, reversível)

**Contras:**
- ❌ Não resolve requisito real de PostgreSQL 15+
- ❌ Cria dívida técnica (produção precisará PG 15+ eventualmente)
- ❌ Divergência ambiente teste vs requisito real
- ❌ Pode mascarar problemas de compatibilidade PG 12 ↔ 15

**Impacto:**
- Downtime adicional: 0 minutos (aplicação pode voltar imediatamente)
- Aplicação PARADA: já 4h, voltaria agora
- Risco: **Nenhum** (mudança local, reversível via git)

**Alteração:**
```python
# Hb Track - Backend/tests/api/test_fase8_conformance.py
def test_rdb1_postgresql_version(self):
    """RDB-1: PostgreSQL versão 12+ (temporário: 15+ em produção)"""
    # TODO: Upgrade VPS para PostgreSQL 15+ (ref: VPS/runbooks/POSTGRESQL_UPGRADE.md)
    result = self.cursor.fetchone()
    assert version_major >= 12, f"PostgreSQL 12+ required (got {version_major})"
    # Produção MUST: version_major >= 15
```

**Documentação:**
- Adicionar AR_008 com waiver: "Teste aceita PG 12 temporariamente, produção requer PG 15+"
- Atualizar TRD/PRD com nota sobre versão mínima real

---

## ANÁLISE RECOMENDADA

### Matriz de Decisão

| Opção | Tempo | Downtime | Risco | Resolve Long-term | Complexidade |
|-------|-------|----------|-------|-------------------|--------------|
| **A (Compilar)** | 90 min | +2h (total 6h) | Médio | Sim (manual) | Alta |
| **B (Upgrade OS)** | 2-3h | +3h (total 7h) | **ALTO** | Sim (APT) | Muito Alta |
| **C (Docker)** | 30 min | +1h (total 5h) | Baixo | Sim (container) | Média |
| **D (Ajustar teste)** | 5 min | 0 (+0h, volta agora) | **Nenhum** | Não (dívida) | Baixa |

### Contexto do Usuário

Comentário do usuário durante diagnóstico:
> "NAO ESTAMOS EM PROD"  
> "Qual o motivo de ter que atualizar o banco?"

**Interpretação:** Usuário questionou necessidade do upgrade ao saber que é ambiente de teste.

**Resposta do Executor (anterior):** "Teste exige intencionalmente PG 15+ (requisito real do projeto)."

**Contra-argumento:** Se ambiente é teste e requisito PG 15+ é para produção futura, **Opção D** seria pragmática:
- Desbloqueia desenvolvimento (BATCH_004 commitável)
- Documenta requisito real (PG 15+ para produção)
- Permite resolver upgrade VPS posteriormente (sem pressão, aplicação rodando)
- Zero risco, downtime zero

### Recomendação do Executor

**Opção D (Ajustar Teste)** é a mais pragmática considerando:
1. Ambiente é **teste** (comentário do usuário)
2. Aplicação está **PARADA há 4 horas** (impacto operacional)
3. BATCH_004 está **pronto** mas bloqueado (governança travada)
4. Upgrade pode ser feito **posteriormente** sem pressão
5. Opções A/B/C têm risco/complexidade/tempo não justificados para ambiente teste

**Alternativa:** Se requisito PG 15+ for **real e urgente** (não apenas "futuro"):
- **Opção C (Docker)** seria a 2ª melhor (rápida, isolada, baixo risco)

---

## AÇÃO SOLICITADA AO ARQUITETO/HUMANO

**Decisão Requerida:** Escolher entre Opções A / B / C / D.

**Inputs Necessários:**
1. **Urgência:** PostgreSQL 15+ é requisito **imediato** ou **futuro** (produção)?
2. **Ambiente:** VPS é **teste puro** ou **homologação crítica**?
3. **Downtime:** 4h já decorridas, quanto tempo adicional é aceitável?
4. **Risco:** Level de risco aceitável (ALTO para Opção B, vs NENHUM para Opção D)?

**Recomendação:** 
- **Se ambiente teste:** Opção D (desbloqueia agora, upgrade depois)
- **Se requisito urgente:** Opção C (Docker, se disponível) ou Opção A (compilar)
- **Se infra precisa modernizar:** Opção B (upgrade OS, planejado com backup completo VPS)

**Aguardando:** Input humano para prosseguir.

---

## REFERÊNCIAS

- **Runbook:** `VPS/runbooks/POSTGRESQL_UPGRADE.md` (atualizado com troubleshooting)
- **Backup:** `/backups/hbtrack/upgrade_pg15_20260221_0259/` (356KB, validado)
- **AR_008:** `docs/hbtrack/ars/AR_008_migration_0055_soft_delete_comp-db-001_em_5_tabela.md`
- **Evidence:** `docs/hbtrack/evidence/AR_008_comp_db_001_soft_delete_migration.log`
- **BATCH_004:** AR_028/029/030 (todos ✅ VERIFICADO)

---

**RUN_ID:** PEDIDO_ARQUITETO_20260221_0615  
**CORR_ID:** N/A (não é correção, é bloqueio de infraestrutura)  
**SSOT_BINDINGS:** `docs/hbtrack/manuais/Manual Deterministico.md`  
**STATUS_NEXT:** BLOCKED_INPUT (Exit Code 4) — Aguardando decisão humana

