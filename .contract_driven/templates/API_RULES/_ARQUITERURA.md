# ARCHITECTURE_MATRIX v2.1.1 — Matriz de Validação Arquitetural

**Versão**: 2.1.1  
**SSOT**: `.contract_driven/templates/api/ARCHITECTURE_MATRIX.v2.1.1.yaml`  
**Status**: `VALIDATION_ONLY_LOCKED`  
**Última atualização**: 2026-03-12

---

## ⚠️ AVISO CRÍTICO: Propósito de Validação

Este artefato é **VALIDATION_ONLY** e **NÃO deve ser usado como fonte primária** de perfis de módulos.

### Contrato de Validação

```yaml
validation_contract:
  primary_module_source: MODULE_PROFILE_REGISTRY.yaml
  forbidden_agent_behavior:
    - read_module_class_from_this_file_instead_of_registry
```

**Fonte Primária**: `MODULE_PROFILE_REGISTRY.yaml`  
**Propósito desta Matriz**: Validar o registry contra **restrições arquiteturais** permitidas

---

## 1. Objetivo

Esta matriz define os **limites arquiteturais permitidos** para cada módulo. Ela **valida**, mas **não define** o perfil operacional real.

### Fluxo de Uso

```
MODULE_PROFILE_REGISTRY.yaml (SSOT operacional)
    ↓
    validado por
    ↓
ARCHITECTURE_MATRIX.v2.1.1.yaml (limites permitidos)
```

---

## 2. Classes de Módulo Permitidas

Apenas as seguintes classes são válidas no HB Track:

| Classe | Descrição |
|--------|-----------|
| **CRUD** | Operações síncronas puras — sem eventos de domínio |
| **HYBRID** | CRUD + eventos de domínio opcionais |
| **EVENT_FIRST** | Event sourcing — estado derivado de eventos, CRUD secundário |

---

## 3. Matriz de Validação por Módulo

### 3.1. Identidade e Acesso

#### identity_access
- **Classes permitidas**: `CRUD`
- **Superfícies**: `sync`
- **Sensível**: ✅ **SIM** (autenticação/autorização)

---

### 3.2. Gestão de Entidades Core

#### users
- **Classes permitidas**: `CRUD`
- **Superfícies**: `sync`
- **Sensível**: ❌ Não

#### seasons
- **Classes permitidas**: `CRUD`
- **Superfícies**: `sync`
- **Sensível**: ❌ Não

#### teams
- **Classes permitidas**: `CRUD`
- **Superfícies**: `sync`
- **Sensível**: ❌ Não

#### exercises
- **Classes permitidas**: `CRUD`
- **Superfícies**: `sync`
- **Sensível**: ❌ Não

---

### 3.3. Treino e Performance

#### training
- **Classes permitidas**: `HYBRID`
- **Superfícies**: `sync`, `event`
- **Sensível**: ❌ Não
- **Nota**: Apenas HYBRID permitido (não pode ser CRUD puro)

---

### 3.4. Saúde e Bem-estar (⚠️ SENSÍVEL)

#### wellness
- **Classes permitidas**: `HYBRID`
- **Superfícies**: `sync`, `event`
- **Sensível**: ✅ **SIM** (dados de saúde)
- **Nota**: HYBRID obrigatório → ambas superfícies (sync **e** event) devem estar habilitadas

#### medical
- **Classes permitidas**: `CRUD`
- **Superfícies**: `sync`
- **Sensível**: ✅ **SIM** (dados médicos/lesões)
- **Nota**: Restrito a CRUD síncrono (sem eventos)

---

### 3.5. Competições e Partidas

#### competitions
- **Classes permitidas**: `CRUD`
- **Superfícies**: `sync`
- **Sensível**: ❌ Não

#### matches
- **Classes permitidas**: `EVENT_FIRST`
- **Superfícies**: `sync`, `event`
- **Sensível**: ❌ Não
- **Nota**: Apenas EVENT_FIRST (não pode ser CRUD)

#### scout
- **Classes permitidas**: `EVENT_FIRST`
- **Superfícies**: `sync`, `event`
- **Sensível**: ❌ Não
- **Nota**: Apenas EVENT_FIRST (não pode ser CRUD)

---

### 3.6. Analytics e Relatórios

#### analytics
- **Classes permitidas**: `EVENT_FIRST`
- **Superfícies**: `sync`, `event`
- **Sensível**: ❌ Não
- **Nota**: Apenas EVENT_FIRST (derivado de eventos)

#### reports
- **Classes permitidas**: `HYBRID`
- **Superfícies**: `sync`, `event`
- **Sensível**: ❌ Não
- **Nota**: HYBRID permite geração sob demanda + subscrição a eventos

---

### 3.7. Automação e IA

#### ai_ingestion
- **Classes permitidas**: `CRUD`
- **Superfícies**: `sync`
- **Sensível**: ✅ **SIM** (processa dados sensíveis)
- **⚠️ Nota Arquitetural**: Intencionalmente restrito a CRUD/sync neste baseline de release. Reclassificar apenas via decisão arquitetural explícita se fact streams replay-safe tornarem-se necessários.

---

### 3.8. Infraestrutura e Governança

#### audit
- **Classes permitidas**: `EVENT_FIRST`
- **Superfícies**: `sync`, `event`
- **Sensível**: ❌ Não
- **Nota**: Apenas EVENT_FIRST (log de eventos imutável)

#### notifications
- **Classes permitidas**: `EVENT_FIRST`
- **Superfícies**: `sync`, `event`
- **Sensível**: ❌ Não
- **Nota**: Apenas EVENT_FIRST (reage a eventos do sistema)

---

## 4. Tabela Resumida

| Módulo | Classes Permitidas | Superfícies | Sensível | Mudanças vs v1.0.0 |
|--------|-------------------|-------------|----------|-------------------|
| **identity_access** | CRUD | sync | ✅ | Sem mudanças |
| **users** | CRUD | sync | ❌ | Sem mudanças |
| **seasons** | CRUD | sync | ❌ | Sem mudanças |
| **teams** | CRUD | sync | ❌ | Sem mudanças |
| **training** | HYBRID | sync, event | ❌ | ⚠️ Removido CRUD (agora apenas HYBRID) |
| **wellness** | HYBRID | sync, event | ✅ | ⚠️ Removido CRUD (agora apenas HYBRID) |
| **medical** | CRUD | sync | ✅ | ⚠️ Removido HYBRID (agora apenas CRUD) |
| **competitions** | CRUD | sync | ❌ | Sem mudanças |
| **matches** | EVENT_FIRST | sync, event | ❌ | ⚠️ Removido CRUD (agora apenas EVENT_FIRST) |
| **scout** | EVENT_FIRST | sync, event | ❌ | ⚠️ Removido CRUD (agora apenas EVENT_FIRST) |
| **exercises** | CRUD | sync | ❌ | Sem mudanças |
| **analytics** | EVENT_FIRST | sync, event | ❌ | ⚠️ Mudou de CRUD para EVENT_FIRST |
| **reports** | HYBRID | sync, event | ❌ | ⚠️ Mudou de CRUD para HYBRID |
| **ai_ingestion** | CRUD | sync | ✅ | ⚠️ Removido EVENT_FIRST (agora apenas CRUD) |
| **audit** | EVENT_FIRST | sync, event | ❌ | ⚠️ Removido CRUD (agora apenas EVENT_FIRST) |
| **notifications** | EVENT_FIRST | sync, event | ❌ | ⚠️ Removido CRUD (agora apenas EVENT_FIRST) |

---

## 5. Módulos Sensíveis (4 total)

| Módulo | Razão | Classe na v2.1.1 |
|--------|-------|------------------|
| **identity_access** | Credenciais e permissões | CRUD |
| **wellness** | Dados de saúde (fadiga, sono, nutrição) | HYBRID (obrigatório) |
| **medical** | Dados médicos e lesões | CRUD (restrito) |
| **ai_ingestion** | Processa dados de múltiplos domínios sensíveis | CRUD (restrito) |

---

## 6. Notas Arquiteturais Específicas

### 6.1. ai_ingestion — Restrição Intencional

> **Nota canônica do YAML**:  
> "ai_ingestion is intentionally constrained to CRUD/sync in this release baseline. Reclassify only via explicit architecture decision if replay-safe fact streams become required."

**Tradução**: `ai_ingestion` está intencionalmente restrito a CRUD/sync neste baseline de release. Reclassificar apenas via **decisão arquitetural explícita** (ADR) se fact streams replay-safe tornarem-se necessários.

### 6.2. wellness — HYBRID Obrigatório

> **Nota canônica do YAML**:  
> "wellness is HYBRID and therefore must keep both sync and event surfaces enabled."

**Tradução**: `wellness` é HYBRID e portanto **deve manter ambas superfícies** (sync **e** event) habilitadas simultaneamente.

---

## 7. Diferenças Principais vs v1.0.0

### 7.1. Mudanças Restritivas (mais estreitas)

| Módulo | v1.0.0 | v2.1.1 | Impacto |
|--------|--------|--------|---------|
| training | CRUD, HYBRID | HYBRID | Força uso de eventos |
| wellness | CRUD, HYBRID | HYBRID | Força uso de eventos |
| medical | CRUD, HYBRID | CRUD | Remove eventos (restrição de compliance) |
| ai_ingestion | CRUD, EVENT_FIRST | CRUD | Remove eventos (restrição de segurança) |

### 7.2. Mudanças de Modelo (reclassificação)

| Módulo | v1.0.0 | v2.1.1 | Razão |
|--------|--------|--------|-------|
| analytics | CRUD | EVENT_FIRST | Analytics deve ser derivado de eventos |
| reports | CRUD | HYBRID | Relatórios precisam de eventos + síncronos |
| matches | CRUD, EVENT_FIRST | EVENT_FIRST | Match data é event-sourced |
| scout | CRUD, EVENT_FIRST | EVENT_FIRST | Scout data é event-sourced |
| audit | CRUD, EVENT_FIRST | EVENT_FIRST | Audit log é imutável (eventos) |
| notifications | CRUD, EVENT_FIRST | EVENT_FIRST | Notificações reagem a eventos |

---

## 8. Como Usar Esta Matriz

### 8.1. ✅ Uso Correto (Validação)

```python
# Validar se módulo está dentro dos limites permitidos
module_profile = read_from("MODULE_PROFILE_REGISTRY.yaml")
architecture_matrix = read_from("ARCHITECTURE_MATRIX.v2.1.1.yaml")

if module_profile.module_class not in architecture_matrix.allowed_classes:
    raise ValidationError("Module class not allowed by architecture")
```

### 8.2. ❌ Uso Incorreto (Fonte Primária)

```python
# PROIBIDO: Ler perfil de módulo diretamente desta matriz
module_class = architecture_matrix.modules["training"].allowed_module_classes[0]
# ↑ ERRADO: Usar MODULE_PROFILE_REGISTRY.yaml como fonte
```

### 8.3. Para Agentes de IA

**Comportamento Proibido**:
- ❌ Ler `module_class` deste arquivo em vez do registry
- ❌ Usar como fonte de verdade operacional
- ❌ Inferir comportamento de módulo a partir desta matriz

**Comportamento Permitido**:
- ✅ Validar registry contra limites arquiteturais
- ✅ Reportar violações de restrições
- ✅ Bloquear operações se registry estiver fora dos limites

---

## 9. Procedimento de Evolução

### 9.1. Ampliar Restrições de Módulo Existente

1. Criar ADR (Architecture Decision Record)
2. Atualizar `ARCHITECTURE_MATRIX.v2.x.x.yaml`
3. Atualizar `MODULE_PROFILE_REGISTRY.yaml`
4. Validar com gates de CI
5. Atualizar este documento

### 9.2. Adicionar Novo Módulo

1. Definir classes permitidas nesta matriz
2. Adicionar perfil operacional no registry
3. Criar contratos (OpenAPI/AsyncAPI) conforme superfícies
4. Atualizar documentação (`MODULE_MAP.md`)

---

## 10. Referências Normativas

- **Fonte operacional primária**: `MODULE_PROFILE_REGISTRY.yaml`
- **Contrato de validação**: Este arquivo (`ARCHITECTURE_MATRIX.v2.1.1.yaml`)
- **Legacy**: `ARCHITECTURE_MATRIX.yaml` (v1.0.0) — baseline histórico
- **Decisões**: `docs/_canon/decisions/ADR-*.md`
- **Taxonomia**: `docs/_canon/MODULE_MAP.md`

---

## 11. Status e Governança

| Campo | Valor |
|-------|-------|
| **Versão** | 2.1.1 |
| **Status** | VALIDATION_ONLY_LOCKED |
| **Autoridade** | Arquiteto-chefe HB Track |
| **Mudanças** | Requerem ADR + aprovação |
| **Última revisão** | 2026-03-12 |

---

**Assinatura**: GitHub Copilot (Claude Sonnet 4.5)  
**Evidência**: Tradução canônica de ARCHITECTURE_MATRIX.v2.1.1.yaml  
**Propósito**: Validação arquitetural — **NÃO usar como fonte primária de perfis**
