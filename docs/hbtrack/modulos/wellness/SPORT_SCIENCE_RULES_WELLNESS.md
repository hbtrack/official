---
module: "wellness"
system_scope_ref: "../../../_canon/SYSTEM_SCOPE.md"
handball_rules_ref: "../../../_canon/HANDBALL_RULES_DOMAIN.md"
handball_semantic_applicability: false
type: "sport-science-rules"
contract_path_ref: "../../../../contracts/openapi/paths/wellness.yaml"
schemas_ref: "../../../../contracts/schemas/wellness/"
---
# SPORT_SCIENCE_RULES_WELLNESS.md

## Objetivo
Registrar métodos, protocolos, cálculos, thresholds e critérios técnico-científicos aplicados ao módulo `wellness`.

## Boundary (SSOT)
Este artefato:
- NÃO substitui `.contract_driven/DOMAIN_AXIOMS.json` (axiomas estruturais)
- NÃO substitui `DOMAIN_RULES_WELLNESS.md` (regras funcionais do módulo)
- NÃO substitui `docs/_canon/HANDBALL_RULES_DOMAIN.md` (regra oficial da modalidade)
- NÃO substitui `docs/_canon/DOMAIN_GLOSSARY.md` (semântica de termos)

## Autoridade de fontes
- Governado por: `docs/_canon/MODULE_SOURCE_AUTHORITY_MATRIX.yaml`
- Regra: toda afirmação técnico-científica DEVE declarar `Fonte` como `source_id` permitido para o módulo (ex: `ACSM`, `ASPETAR`).

## Registro técnico-científico
| ID | Categoria | Item (método/protocolo/cálculo/threshold) | Inputs | Output | Unidade | Critério/Threshold | Fonte | Evidência | Observações |
|---|---|---|---|---|---|---|---|---|---|
| SSR-WELL-001 | Questionário | Escala de Hooper (readiness diária) | sono, estresse, fadiga, dor muscular (1–7 cada) | score composto | pontos (4–28) | > 22 = atenção ao treinador | ASPETAR | Hooper & Mackinnon, 1995 | Protocolo de auto-relato; não substitui avaliação clínica |
| SSR-WELL-002 | Monitoramento | Percepção subjetiva de esforço (PSE sessão) | escala CR-10 de Borg ou modificada | carga interna estimada | UA (unidades arbitrárias) | PSE × duração (min) = carga interna | ACSM | Foster et al., 2001 | Exclusivo para contextualização com `training`; não diagnóstico |

## Regras de uso (classificação)
1. Se a afirmação for regra funcional do produto → registrar em `DOMAIN_RULES_WELLNESS.md`.
2. Se for definição de termo → registrar em `docs/_canon/DOMAIN_GLOSSARY.md`.
3. Se for regra oficial do handebol → registrar em `docs/_canon/HANDBALL_RULES_DOMAIN.md` (ou ADR linkado).
4. Se for axioma estrutural do domínio → registrar em `.contract_driven/DOMAIN_AXIOMS.json`.
