---
# TEMPLATE: module-doc-template
# DEST: docs/hbtrack/modulos/<module>/SPORT_SCIENCE_RULES_{{MODULE_NAME_UPPER}}.md
# SOURCE: .contract_driven/templates/modulos/SPORT_SCIENCE_RULES_{{MODULE_NAME_UPPER}}.md
module: "{{MODULE_NAME}}"
system_scope_ref: "../../../_canon/SYSTEM_SCOPE.md"
handball_rules_ref: "../../../_canon/HANDBALL_RULES_DOMAIN.md"
handball_semantic_applicability: {{HANDBALL_SEMANTIC_APPLICABILITY}}
contract_path_ref: "../../../../contracts/openapi/paths/{{MODULE_NAME}}.yaml"
schemas_ref: "../../../../contracts/schemas/{{MODULE_NAME}}/"
type: "sport-science-rules"
---

# SPORT_SCIENCE_RULES_{{MODULE_NAME_UPPER}}.md

## Objetivo
Registrar métodos, protocolos, cálculos, thresholds e critérios técnico-científicos aplicados ao módulo `{{MODULE_NAME}}`.

## Boundary (SSOT)
Este artefato:
- NÃO substitui `.contract_driven/DOMAIN_AXIOMS.json` (axiomas estruturais)
- NÃO substitui `DOMAIN_RULES_{{MODULE_NAME_UPPER}}.md` (regras funcionais do módulo)
- NÃO substitui `docs/_canon/HANDBALL_RULES_DOMAIN.md` (regra oficial da modalidade)
- NÃO substitui `docs/_canon/DOMAIN_GLOSSARY.md` (semântica de termos)

## Autoridade de fontes
- Governado por: `docs/_canon/MODULE_SOURCE_AUTHORITY_MATRIX.yaml`
- Regra: toda afirmação técnico-científica DEVE declarar `Fonte` como `source_id` permitido para o módulo (ex: `ACSM`, `ASPETAR`, `EHF`).

## Registro técnico-científico
| ID | Categoria | Item (método/protocolo/cálculo/threshold) | Inputs | Output | Unidade | Critério/Threshold | Fonte | Evidência | Observações |
|---|---|---|---|---|---|---|---|---|---|
{{SPORT_SCIENCE_RULES_TABLE_ROWS}}

## Regras de uso (classificação)
1. Se a afirmação for regra funcional do produto → registrar em `DOMAIN_RULES_{{MODULE_NAME_UPPER}}.md`.
2. Se for definição de termo → registrar em `docs/_canon/DOMAIN_GLOSSARY.md`.
3. Se for regra oficial do handebol → registrar em `docs/_canon/HANDBALL_RULES_DOMAIN.md` (ou ADR linkado).
4. Se for axioma estrutural do domínio → registrar em `.contract_driven/DOMAIN_AXIOMS.json`.
