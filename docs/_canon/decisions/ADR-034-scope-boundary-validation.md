---
adr_id: ADR-034
title: "Scope Boundary Validation — Detectar Referências Cross-Module"
status: proposed
date: "2026-03-18"
deciders: [tech-lead, platform-architect]
decision: D5.3
state_semantics: governance
supersedes: []
superseded_by: []
related_adrs: [ADR-031]
tags: [governance, pipeline, validation, scope, cdd]
---

# ADR-034 — Validação de Boundary entre Módulos

## Contexto

Durante a auditoria red team do pipeline (`audit_red_team_pipeline.prompt.md`), foi identificada uma vulnerabilidade **A8 — Cross-Module Scope Overflow**:

- Um contrato do módulo `users` pode referenciar endpoints de `identity_access` sem bloqueio em Fase 0 ou Fase 1.
- O bloqueio atual só ocorreria em Fase 2 (validação semântica), não em Fase 1 (validação estrutural).
- Isso viola a regra de **determinismo precoce** do CDD: boundary violations devem ser detectadas tão cedo quanto possível.

### Boundary Canônico

Conforme `docs/_canon/SYSTEM_SCOPE.md` e `CONTRACT_SYSTEM_RULES.md §2C`:

- **`users`** (módulo): person/profile domain (dados de identidade funcional pessoal)
- **`identity_access`** (módulo): authentication, authorization, credentials, sessions, MFA, JWT, RBAC

Nenhum artefato sob `users` deve definir política de autenticação ou autorização.  
Nenhum artefato sob `identity_access` deve redefinir profile ou dados de identidade pessoal.

### Problema Atual

No orchestrador pré-contrato:
- **Fase 0**: Valida `task_type`, `module`, worker path, session
- **Fase 1**: Valida artefatos obrigatórios, ADRs abertas, DOD
- **Fase 2**: Valida conteúdo semântico (por worker especializado)

Não existe validação estrutural de scope boundary entre módulos.

## Decisão

### Adicionar SCOPE_BOUNDARY_GATE ao pipeline

Criar um novo gate bloqueante em **Fase 1** (após carregamento de módulo, antes de passar para Fase 2):

1. **Gate metadata** (GATES_REGISTRY.yaml):
   - Nome: `SCOPE_BOUNDARY_GATE`
   - Ordem: 1.5 (entre PATH_CANONICALITY_GATE e REQUIRED_ARTIFACT_PRESENCE_GATE)
   - Tipo: blocker
   - Fase: 1

2. **Validação**: Detectar todas as referências em um artefato (paths, events, schemas) e verificar:
   - Estão dentro do módulo atual? ✓ PASS
   - Estão em módulo transitivo permitido (por ADR)? ✓ PASS  
   - Estão em módulo não permitido? → BLOCKED_SCOPE_OVERFLOW

3. **Código de bloqueio**: `BLOCKED_SCOPE_OVERFLOW` (novo, adicionado a RULES §9 e docs/_canon/AGENT_INSTRUCTIONS.md §5)

4. **Artifact normativo**: `docs/_canon/SCOPE_BOUNDARY_POLICY.md` (novo)
   - Define regras de boundary entre pares de módulos
   - Identifica transitividades permitidas (ex: `users` → `sessions` é permitido via identity_access)
   - Lista ADRs que autorizam crossing de boundary

### Implementação

#### 1. Adicionar código de bloqueio (docs/_canon/AGENT_INSTRUCTIONS.md §5)

Adicionar `BLOCKED_SCOPE_OVERFLOW` à lista de 19 códigos canônicos.

#### 2. Criar SCOPE_BOUNDARY_POLICY.md

Novo artefato canônico em `docs/_canon/SCOPE_BOUNDARY_POLICY.md`:

```yaml
version: "1.0.0"
canonical_modules: [16 modules]
scope_rules:
  users:
    allowed_references: [seasons, teams, wellness, medical, analytics, reports]
    forbidden_references: [identity_access, audit, notifications]
    exceptions: []
  
  identity_access:
    allowed_references: []
    forbidden_references: [users, teams, seasons, ...]
    exceptions: []
  
  # ... um por cada módulo ou pares problemáticos
```

#### 3. Registrar gate em GATES_REGISTRY.yaml

```yaml
SCOPE_BOUNDARY_GATE:
  order: 1.5
  type: blocker
  phase: 1
  description: "Detectar referências cross-module sem boundary ADR"
  validation_script: scripts/gates/check_scope_boundary.py
  failure_code: BLOCKED_SCOPE_OVERFLOW
  applies_to: [new_contract, contract_revision, new_event, new_workflow]
```

#### 4. Criar validator script

**File**: `scripts/gates/check_scope_boundary.py`

Pseudocódigo:
```python
def check_scope_boundary(artifact_path: str, module_name: str) -> tuple[bool, str | None]:
    """
    Valida que artefato não referencia recursos fora do scope do módulo
    sem ADR explícita de exception.
    
    Args:
        artifact_path: path ao contrato (ex: contracts/openapi/paths/users.yaml)
        module_name: módulo canônico (ex: 'users')
    
    Returns:
        (is_valid, blocking_code_or_none)
    """
    artifact_content = read_file(artifact_path)
    
    # Extrair todas as referências (operationIds, $ref, paths, etc.)
    references = extract_references(artifact_content)
    
    # Carregar policy
    policy = load_yaml('docs/_canon/SCOPE_BOUNDARY_POLICY.md')
    allowed = policy['scope_rules'][module_name]['allowed_references']
    forbidden = policy['scope_rules'][module_name]['forbidden_references']
    exceptions = policy['scope_rules'][module_name]['exceptions']
    
    for ref in references:
        ref_module = parse_module_from_reference(ref)
        
        if ref_module == module_name:
            continue  # Intra-module é sempre OK
        
        if ref_module in allowed:
            continue  # Permitido por política
        
        if ref_module in exceptions:
            # Verificar se existe ADR explícita
            adr_exists = check_adr_for_boundary_exception(
                source_module=module_name,
                target_module=ref_module,
                reference=ref
            )
            if adr_exists:
                continue
        
        # Violação de boundary
        return (False, "BLOCKED_SCOPE_OVERFLOW")
    
    return (True, None)
```

#### 5. Atualizar orchestrador

**File**: `.contract_driven/agent_prompts/pre_contract_orchestrator.prompt.md`

Adicionar em **Fase 1** (após MODULE_REGISTRY_GATE, antes de REQUIRED_ARTIFACT_PRESENCE_GATE):

```
Fase 1 — Descoberta de Artefatos

6. Executar SCOPE_BOUNDARY_GATE:
   - Se artefato existe do módulo:
     - Rodar check_scope_boundary.py
     - Se FAIL → emitir BLOCKED_SCOPE_OVERFLOW
   - Se artefato não existe → skippar este check (será capturado por REQUIRED_ARTIFACT)
```

## Consequências

### Positivas
- **Determinismo precoce**: violations de boundary são detectadas em F1, não F2
- **Governança clara**: SCOPE_BOUNDARY_POLICY.md é SSOT legível de regras de módulo
- **Red team mitigado**: Vulnerabilidade A8 agora bloqueada cedo
- **Extensível**: policy permite ADRs que autorizam crossing (ex: para domínios transversais)

### Negativas
- **Overhead inicial**: necessário preencher SCOPE_BOUNDARY_POLICY.md com todos os pares (16×15/2 = 120 pares)
- **Manutenção**: novos módulos exigem atualizar policy
- **Latência em pipeline**: check_scope_boundary.py executa para cada novo contrato (mitigado por cache)

## Alternativas Consideradas

### 1. **Ignorar A8 até Fase 2**
- Pro: nenhuma mudança necessária
- Con: violações de boundary não são detectadas determinísticamente em F1; agente pode aprovar contrato inválido

### 2. **Bloquear ALL cross-module references (whitelist vazia)**
- Pro: máxima segurança de boundary
- Con: muito restritivo — alguns cross-module são legítimos (ex: training → exercise references)

### 3. **Usar comments de bypass na policy (inline ADR)**
- Pro: rápido, sem novos artefatos
- Con: code escatterd, não centralizável, não rastreável

### **Opção Recomendada: #ADR-034 (proposta above)**
- Oferece balanço entre segurança (block early) e flexibilidade (policy + ADR exceptions)

## Artefato Normativo

### Arquivos a criar/modificar:

1. **docs/_canon/SCOPE_BOUNDARY_POLICY.md** (novo)
   - SSOT de rules de boundary entre módulos
   - Especifica transitividades permitidas
   - Registra ADRs que autorizam crossing

2. **scripts/gates/check_scope_boundary.py** (novo)
   - Implementação do validator
   - Carrega policy, extrai references, valida

3. **.contract_driven/CONTRACT_SYSTEM_RULES.md**
   - Adicionar `BLOCKED_SCOPE_OVERFLOW` a §9

4. **docs/_canon/AGENT_INSTRUCTIONS.md**
   - Adicionar `BLOCKED_SCOPE_OVERFLOW` a §5 (bloqueios canônicos)

5. **docs/_canon/gates/GATES_REGISTRY.yaml**
   - Registrar SCOPE_BOUNDARY_GATE com order 1.5

6. **.contract_driven/agent_prompts/pre_contract_orchestrator.prompt.md**
   - Adicionar check em Fase 1

## Dependências e Ordem de Implementação

1. **Pré-requisito**: ADR-034 discussão e aprovação
2. **Passo 1**: Criar SCOPE_BOUNDARY_POLICY.md (16 módulos × allowed/forbidden/exceptions)
3. **Passo 2**: Criar check_scope_boundary.py validator
3. **Passo 3**: Atualizar RULES §9 + docs/_canon/AGENT_INSTRUCTIONS.md §5
5. **Passo 4**: Registrar gate em GATES_REGISTRY.yaml (ordem 1.5)
6. **Passo 5**: Atualizar orchestrator.prompt.md (Fase 1, step 6)
7. **Passo 6**: Validar com `hb verify` (nenhum bloqueio indevido)
8. **Passo 7**: Re-executar red team (A8 deve PASS agora)

## Referências

- **Related ADRs**: ADR-001 (CDD), ADR-004 (API Policy Compiler)
- **Related Docs**: 
  - `docs/_canon/SYSTEM_SCOPE.md` (boundary canônico)
  - `docs/_canon/MODULE_SOURCE_AUTHORITY_MATRIX.yaml` (autoridade por módulo)
  - `CONTRACT_SYSTEM_RULES.md §2C` (boundary crítico)
- **Red Team Report**: `_reports/AUDIT_RED_TEAM_PIPELINE_20260317.md§A8`
- **Mitigation Plan**: `_reports/MITIGATION_PLAN_RED_TEAM_20260317.md`

---

**Status da Decisão**: ⏳ Proposta (awaiting approval)

Se aprovada: iniciar Passo 1 (SCOPE_BOUNDARY_POLICY.md) em nova sprint.
