# MITIGATION PLAN — VULNERABILIDADES RED TEAM

**Data**: 2026-03-17  
**Status**: Em elaboração (requer ADR para implementação)  
**Prioridade**: Moderada (ambas vulnerabilidades são mitigáveis, não críticas)

---

## Vulnerabilidade A8 — Cross-Module Scope Overflow

### Análise

**Problema**: Contrato do módulo `users` pode referenciar endpoints de `identity_access` sem bloqueio em F0/F1.

**Risco**: False clearance — contrato com violação de escopo avança até F2+ (validação semântica) antes de ser detectado.

**Condição adversária**: 
```
task_type=new_contract
module=users  
resource={reference to identity_access endpoint}
```

**Comportamento atual**: PASS F0 e F1 (nenhuma validação de boundary)  
**Comportamento esperado**: BLOCKED_SCOPE_OVERFLOW em F1

### Raiz Causa

Não existe gate de validação de boundary entre módulos. RULES §2C (Boundary crítico) define:
- `users` = person/profile domain
- `identity_access` = authentication, authorization, credentials

Mas não há enforcement técnico em pipeline.

### Mitigation (Opção Recomendada)

#### Passo 1: Adicionar código de bloqueio a RULES §9

**Arquivo**: `.contract_driven/CONTRACT_SYSTEM_RULES.md`  
**Seção**: § 9 (Códigos de bloqueio)

Adicionar entrada:
```yaml
- `BLOCKED_SCOPE_OVERFLOW`
  - Emitir quando: artefato contém referência fora do módulo designado sem boundary ADR explícito
  - Fase: F1 (pós-carregamento de módulo, pré-validação semântica)
  - Exemplo: users.yaml referencia identity_access paths
```

#### Passo 2: Registrar a regra em RULES §23 (novo)

Criar nova seção:

**§23. SCOPE BOUNDARY VALIDATION**
```
Para cada módulo M:
- Artefatos de M podem referenciar apenas recursos em M ou em módulos transitivos permitidos
- Boundary de MODULE_SOURCE_AUTHORITY_MATRIX.yaml é a fonte canônica
- Se cross-module reference encontrada:
  - Verificar se existe ADR explícita permitindo
  - Se não: emitir BLOCKED_SCOPE_OVERFLOW em F1
```

#### Passo 3: Criar gate SCOPE_BOUNDARY_GATE

**Arquivo**: `docs/_canon/gates/GATES_REGISTRY.yaml`

Adicionar entrada (`order: 1.5`, entre PATH_CANONICALITY e REQUIRED_ARTIFACT):
```yaml
SCOPE_BOUNDARY_GATE:
  order: 1.5
  type: blocker
  phase: 1
  description: "Detectar referências fora do escopo do módulo"
  validation_script: scripts/gates/check_scope_boundary.py
  failure_code: BLOCKED_SCOPE_OVERFLOW
```

#### Passo 4: Criar validator script

**Arquivo**: `scripts/gates/check_scope_boundary.py`

Pseudocódigo:
```python
def check_scope_boundary(artifact_path, module_name):
    """
    Valida que artefato não referencia recursos fora do módulo
    sem ADR explícita.
    
    Returns: (is_valid, blocking_code)
    """
    artifact_content = read_file(artifact_path)
    
    # Extrair todas as referências (operationIds, paths, eventos, etc.)
    references = extract_references(artifact_content)
    
    # Para cada referência, validar se está no módulo authorizado
    for ref in references:
        ref_module = parse_module_from_reference(ref)
        if ref_module != module_name:
            # Verificar se existe ADR permitindo cross-module
            adr_exists = check_adr_for_boundary_exception(
                source_module=module_name,
                target_module=ref_module
            )
            if not adr_exists:
                return (False, "BLOCKED_SCOPE_OVERFLOW")
    
    return (True, None)
```

#### Passo 5: Atualizar orchestrator

**Arquivo**: `.contract_driven/agent_prompts/pre_contract_orchestrator.prompt.md`

Adicionar check em F1 (após MODULE_REGISTRY validation):
```
F1 — Validação de Artifact obrigatório

  6. Validar escopo do módulo:
     - Carregar artefato do módulo
     - Executar SCOPE_BOUNDARY_GATE
     - Se FAIL → emitir BLOCKED_SCOPE_OVERFLOW
```

### Estimativa

- **Passo 1**: +5 linhas em RULES §9
- **Passo 2**: +20 linhas em RULES (nova seção §23)
- **Passo 3**: +15 linhas em GATES_REGISTRY.yaml
- **Passo 4**: +50 linhas em check_scope_boundary.py (novo)
- **Passo 5**: +4 linhas em orchestrator.prompt.md

**Total**: ~100 linhas de código/config  
**Tempo estimado**: 1-2h com testes

### Decisão Necessária

Esta mudança requer ADR porque:
- Define novo boundary validation (nova regra operacional)
- Promove novo código de bloqueio (RULES §9)
- Afeta pipeline de F1

**Recomendação**: Criar ADR-031 (Scope Boundary Validation) antes de implementar.

---

## Vulnerabilidade B2/C3 — Audit-Only Tasks

### Status

✅ **JÁ CORRIGIDO** em TASK_CATALOG.yaml (versão atual)

#### Evidência

Todos os 5 prompt de auditoria já estão registrados:

| Task | Status | Worker Path | Exception |
|------|--------|-------------|-----------|
| audit_sovereign_integrity | active | audit_sovereign_integrity.prompt.md | PRE_CONTRACT_SKIPPED |
| audit_context_efficiency | active | audit_context_efficiency.prompt.md | PRE_CONTRACT_SKIPPED |
| audit_red_team_pipeline | active | audit_red_team_pipeline.prompt.md | PRE_CONTRACT_SKIPPED |
| audit_gate_coverage | active | audit_gate_coverage.prompt.md | PRE_CONTRACT_SKIPPED |
| audit_domain_completeness | active | audit_domain_completeness.prompt.md | PRE_CONTRACT_SKIPPED |

Com a flag `pre_contract_exception: "PRE_CONTRACT_SKIPPED: audit-only, no artifact produced"`, o orchestrator sabe que:
- Essas tasks não precisam passar por Fase 0–3
- Nenhum artefato normativo é produzido
- São "gate-only" tasks (pura diagnóstico/validação)

**Conclusão**: B2/C3 não precisa de mitigation adicional. O design current é correto.

---

## Resumo de Ações

| Vulnerabilidade | Status | Ação |
|-----------------|--------|------|
| **A8 — Cross-Module Scope** | Open | Requer ADR-031 + 100 linhas de mudança |
| **B2/C3 — Audit-Only Tasks** | ✅ FIXED | Nenhuma ação necessária |

---

## Próximos Passos

1. **Humano aprova mitigation plan para A8?** → proceder com ADR-031
2. **Ou: Aceitar risco de A8** (baixa criticidade — detectado apenas em F2 semântica)?

Recomendação: Proceder com ADR-031 para cobertura completa, mas priorizar após sign-off de UI Contract v1.1.0 (SESSION_HANDOFF.md).
