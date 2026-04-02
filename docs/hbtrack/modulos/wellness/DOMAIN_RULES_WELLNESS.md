---
module: "wellness"
system_scope_ref: "../../../_canon/SYSTEM_SCOPE.md"
handball_rules_ref: "../../../_canon/HANDBALL_RULES_DOMAIN.md"
handball_semantic_applicability: false
contract_path_ref: "../../../../contracts/openapi/paths/wellness.yaml"
schemas_ref: "../../../../contracts/schemas/wellness/"
type: "domain-rules"
updated: "2026-03-16"
---

# DOMAIN_RULES_WELLNESS.md

## Objetivo
Registrar as regras de negócio do módulo `wellness`.

## Fonte do domínio
- `docs/_canon/MODULE_SOURCE_AUTHORITY_MATRIX.yaml`
- `contracts/schemas/wellness/wellness_entry.schema.json`
- `docs/hbtrack/modulos/wellness/INVARIANTS_WELLNESS.md`
- Fontes técnico-científicas permitidas via authority matrix (`ASPETAR`, `ACSM`)
- `docs/hbtrack/modulos/wellness/graph/entities.yaml`
- `docs/hbtrack/modulos/wellness/graph/errors.yaml`
- `docs/hbtrack/modulos/wellness/graph/endpoints.yaml`

## Regras de negócio
| ID | Regra | Entidades afetadas | Fonte | Observações |
|---|---|---|---|---|
| DR-WELL-001 | `wellness` é soberano de readiness, fadiga, sono, dor autorreferida, recuperação e questionários diários. | `WellnessEntry` | Authority matrix `wellness` | Escopo de auto-relato |
| DR-WELL-002 | Dados de `wellness` são percepção autorreferida e insumo consultivo para `training` e `analytics`; não equivalem a diagnóstico, tratamento ou liberação clínica. | `WellnessEntry` | Boundary `wellness`/`medical` | Separação obrigatória |
| DR-WELL-003 | `trainingSessionId`, quando presente, apenas contextualiza a coleta em torno de uma sessão; não representa presença, execução ou autorização para treinar. | `WellnessEntry` | Schema local | Boundary com `training` |
| DR-WELL-004 | `questionnaireLabel` identifica o protocolo de coleta aplicado ao auto-relato e deve ser explícito quando múltiplos questionários coexistirem. | `WellnessEntry` | Authority matrix `daily_questionnaires` | Evita mistura de protocolos |
| DR-WELL-005 | `notes` é contexto subjetivo do atleta/staff e não pode ser tratado como prontuário clínico, prescrição ou decisão médica formal. | `WellnessEntry` | Boundary gate | Texto livre com limite semântico |

## Limites de inferência
- Não inferir diagnóstico, tratamento, procedimento, prontuário ou retorno ao jogo a partir de `wellness`.
- Não transformar score de wellness em decisão médica automática.
- Não deduzir política de acesso a partir da UI; acesso sensível depende de `identity_access` e trilha em `audit`.

## Âncoras estruturadas
- As entidades soberanas e seus campos mapeados para runtime estão em `docs/hbtrack/modulos/wellness/graph/entities.yaml`.
- O mapa mínimo de operações e permissões publicadas está em `docs/hbtrack/modulos/wellness/graph/endpoints.yaml`.
- O mapa mínimo de erros transport/domain do módulo está em `docs/hbtrack/modulos/wellness/graph/errors.yaml`.
