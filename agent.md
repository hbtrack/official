## Protocolo de boot do agente

Seguir o protocolo de boot para garantir o determinismo (OBRIGATÓRIO) e a eficiência (RECOMENDADO) do agente, evitando inferências arriscadas e leituras desnecessárias.

### Ordem obrigatória de boot
1. `.contract_driven/CONTRACT_SYSTEM_LAYOUT.md`
2. `.contract_driven/CONTRACT_SYSTEM_RULES.md`
3. `.contract_driven/GLOBAL_TEMPLATES.md`
4. `.contract_driven/templates/README.md` (estrutura e contrato de uso de templates)
5. `.contract_driven/templates/api/api_rules.yaml`
6. `docs/_canon/SYSTEM_SCOPE.md`
7. `docs/_canon/API_CONVENTIONS.md`
8. `docs/_canon/DATA_CONVENTIONS.md`
9. `docs/_canon/CHANGE_POLICY.md`
10. `docs/_canon/HANDBALL_RULES_DOMAIN.md`
11. `docs/_canon/DOMAIN_GLOSSARY.md`
12. `docs/_canon/MODULE_SOURCE_AUTHORITY_MATRIX.yaml`
13. `docs/_canon/MODULE_MAP.md`
14. `docs/_canon/ARCHITECTURE.md`
15. artefatos de contrato relevantes
16. docs de módulo relevantes

# Modo de boot
O agente deve usar:
- boot mínimo obrigatório
- loading condicional sob demanda
- bloquear em vez de inferir quando um artefato crítico estiver ausente

# Condição de bloqueio no boot
Se o agente não conseguir carregar a sequência de boot necessária para a tarefa atual, ele deve se declarar bloqueado usando um código de bloqueio válido, em vez de continuar por inferência.

# Perfis de leitura por tarefa (contexto mínimo suficiente)
O boot mínimo continua obrigatório, mas o agente **DEVE** reduzir a leitura ao mínimo necessário para a tarefa (carregar sob demanda).

Perfis recomendados:
- **Gerar/alterar contrato de API (OpenAPI paths)**:
  - LAYOUT + RULES + `api_rules.yaml`
  - `docs/_canon/SYSTEM_SCOPE.md`
  - docs do módulo (mínimo): README / MODULE_SCOPE / DOMAIN_RULES / INVARIANTS / TEST_MATRIX
  - contratos do módulo: `contracts/openapi/openapi.yaml` + `contracts/openapi/paths/<module>.yaml` + `contracts/openapi/components/`

- **Gerar docs mínimas de módulo**:
  - LAYOUT + RULES + `GLOBAL_TEMPLATES.md` (índice/regras)
  - templates: `.contract_driven/templates/modulos/*`
  - `docs/_canon/SYSTEM_SCOPE.md`
  - `docs/_canon/HANDBALL_RULES_DOMAIN.md` quando o gatilho aplicar

- **Gerar schema de domínio (contracts/schemas)**:
  - LAYOUT + RULES + `.contract_driven/DOMAIN_AXIOMS.json`
  - template: `.contract_driven/templates/modulos/schemas/{{DOMAIN_ENTITY_SNAKE}}.schema.json`
  - docs do módulo (DOMAIN_RULES + INVARIANTS)

Prompts operacionais (checklists) vivem em:`.contract_driven/agent_prompts/`

Regras:
- [CONTRACT_SYSTEM_LAYOUT.md](./CONTRACT_SYSTEM_LAYOUT.md)
- [CONTRACT_SYSTEM_RULES.md](./CONTRACT_SYSTEM_RULES.md)
- [GLOBAL_TEMPLATES.md](./GLOBAL_TEMPLATES.md)

- `.contract_driven/templates/agent_prompts/pre_contract_orchestrator.prompt.md` 
- `.contract_driven/templates/agent_prompts/decision_discovery.prompt.md`
