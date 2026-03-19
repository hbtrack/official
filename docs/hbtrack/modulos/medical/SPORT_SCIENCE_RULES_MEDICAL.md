---
module: "medical"
system_scope_ref: "../../../_canon/SYSTEM_SCOPE.md"
handball_rules_ref: "../../../_canon/HANDBALL_RULES_DOMAIN.md"
handball_semantic_applicability: false
type: "sport-science-rules"
contract_path_ref: "../../../../contracts/openapi/paths/medical.yaml"
schemas_ref: "../../../../contracts/schemas/medical/"
---
# SPORT_SCIENCE_RULES_MEDICAL.md

## Objetivo
Registrar métodos, protocolos, cálculos, thresholds e critérios técnico-científicos aplicados ao módulo `medical`.

## Boundary (SSOT)
Este artefato:
- NÃO substitui `.contract_driven/DOMAIN_AXIOMS.json` (axiomas estruturais)
- NÃO substitui `DOMAIN_RULES_MEDICAL.md` (regras funcionais do módulo)
- NÃO substitui `docs/_canon/HANDBALL_RULES_DOMAIN.md` (regra oficial da modalidade)
- NÃO substitui `docs/_canon/DOMAIN_GLOSSARY.md` (semântica de termos)

## Autoridade de fontes
- Governado por: `docs/_canon/MODULE_SOURCE_AUTHORITY_MATRIX.yaml`
- Regra: toda afirmação técnico-científica DEVE declarar `Fonte` como `source_id` permitido para o módulo (ex: `ASPETAR`, `ACSM`, `IHF`).

## Registro técnico-científico
| ID | Categoria | Item (método/protocolo/cálculo/threshold) | Inputs | Output | Unidade | Critério/Threshold | Fonte | Evidência | Observações |
|---|---|---|---|---|---|---|---|---|---|
| SSR-MED-001 | Retorno ao treino | Protocolo de retorno progressivo ao treino pós-lesão | avaliação clínica documentada, tipo de lesão, dias de afastamento | `returnToTrainingAuthorized` | booleano | autorização só após avaliação clínica explícita | ASPETAR | Aspetar Orthopedic & Sports Medicine Hospital guidelines | Nunca inferir a partir de wellness ou treinos anteriores |
| SSR-MED-002 | Retorno ao jogo | Distinção clínica entre retorno ao treino e retorno ao jogo | clearance de treino + avaliação funcional esportiva | `returnToPlayAuthorized` | booleano | clearance de jogo pressupõe raciocínio clínico adicional | ASPETAR | IOC return-to-play consensus | Autorizar jogo ≠ autorizar treino |

## Regras de uso (classificação)
1. Se a afirmação for regra funcional do produto → registrar em `DOMAIN_RULES_MEDICAL.md`.
2. Se for definição de termo → registrar em `docs/_canon/DOMAIN_GLOSSARY.md`.
3. Se for regra oficial do handebol → registrar em `docs/_canon/HANDBALL_RULES_DOMAIN.md` (ou ADR linkado).
4. Se for axioma estrutural do domínio → registrar em `.contract_driven/DOMAIN_AXIOMS.json`.
