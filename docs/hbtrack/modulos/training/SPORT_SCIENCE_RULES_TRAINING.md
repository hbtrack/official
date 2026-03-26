---
module: "training"
system_scope_ref: "../../../_canon/SYSTEM_SCOPE.md"
handball_rules_ref: "../../../_canon/HANDBALL_RULES_DOMAIN.md"
handball_semantic_applicability: true
contract_path_ref: "../../../../contracts/openapi/paths/training.yaml"
schemas_ref: "../../../../contracts/schemas/training/"
type: "sport-science-rules"
---

# SPORT_SCIENCE_RULES_TRAINING.md

## Objetivo
Registrar métodos, protocolos, cálculos, thresholds e critérios técnico-científicos aplicados ao módulo `training`.

## Boundary (SSOT)
Este artefato:
- NÃO substitui `.contract_driven/DOMAIN_AXIOMS.json` (axiomas estruturais)
- NÃO substitui `DOMAIN_RULES_TRAINING.md` (regras funcionais do módulo)
- NÃO substitui `docs/_canon/HANDBALL_RULES_DOMAIN.md` (regra oficial da modalidade)
- NÃO substitui `docs/_canon/DOMAIN_GLOSSARY.md` (semântica de termos)

## Autoridade de fontes
- Governado por: `docs/_canon/MODULE_SOURCE_AUTHORITY_MATRIX.yaml`
- Regra: toda afirmação técnico-científica registrada aqui deve declarar fonte permitida (ex.: `ACSM`, `ASPETAR`, `EHF`) e evidência mínima rastreável.

## Registro técnico-científico

| ID | Categoria | Item (método/protocolo/cálculo/threshold) | Inputs | Output | Unidade | Critério/Threshold | Fonte | Evidência | Observações |
|---|---|---|---|---|---|---|---|---|---|
| SS-TRAIN-001 | Carga interna | sRPE — Session Rating of Perceived Exertion (Foster method) | `minutes_effective` (min), `session_rpe` [0–10] | `internal_load` | UA (unidades arbitrárias) | `internal_load = minutes_effective × session_rpe` | ACSM | Foster C, et al. "A new approach to monitoring exercise training." J Strength Cond Res. 2001;15(1):109–115. | Implementado em INV-TRAIN-021. Não aplicar sem coleta de RPE válida (ver SS-TRAIN-002). |
| SS-TRAIN-002 | Esforço percebido | Escala de RPE CR-10 (Borg / Foster modified) — percepção subjetiva de esforço pós-sessão | Percepção subjetiva do atleta, coletada 20–30 min após término da sessão | `session_rpe` | adimensional [0–10] | 0 = nenhum esforço; 10 = esforço máximo absoluto. Domínio válido: inteiro ou decimal em [0, 10]. Fora do domínio → dado inválido. | ACSM | Borg GA. "Psychophysical bases of perceived exertion." Med Sci Sports Exerc. 1982;14(5):377–381; Foster C et al. 2001. | Implementado em INV-TRAIN-032. Janela de coleta: 20–30 min pós-sessão (prática de monitoramento; não há janela hard-coded no sistema além de 24h de INV-TRAIN-003). |
| SS-TRAIN-003 | Bem-estar / readiness | Janela de coleta de wellness pré-treino | `timestamp_submissão`, `session_at` | wellness_pre válido ou inválido | horas | Submissão deve ocorrer ≥ 2h antes de `session_at` (não-inclusivo). Fora da janela → registro bloqueado. | Regra de produto HB Track | INV-TRAIN-002; DR-TRAIN-004. Baseado em prática de AMS: coleta pré-sessão deve refletir estado recente sem ser simultânea à chegada. | Implementado em INV-TRAIN-002. Fontes científicas (ACSM, Aspetar) suportam janela pré-sessão; valor exato de 2h é decisão de produto. |
| SS-TRAIN-004 | Bem-estar / carga percebida | Janela de edição de wellness pós-treino | `created_at`, `timestamp_edição` | wellness_post editável ou somente leitura | horas | Editável enquanto `NOW < created_at + 24h` (não-inclusivo). Após janela → dado imutável. | Regra de produto HB Track | INV-TRAIN-003; DR-TRAIN-005. | Implementado em INV-TRAIN-003. Janela de 24h permite correção sem permitir revisão retrospectiva tardia. |
| SS-TRAIN-005 | Recuperação / sono | Escala de qualidade do sono (Likert 1–5) | Percepção subjetiva do atleta (pré-treino) | `sleep_quality` | adimensional [1–5] | 1 = muito ruim; 5 = excelente. Domínio válido: inteiro em [1, 5]. | ACSM | Hooper SL, Mackinnon LT. "Monitoring overtraining in athletes." Sports Med. 1995;20(5):321–327. (escala de bem-estar 1–5 amplamente adotada em AMS esportivos). | Implementado em INV-TRAIN-034. Alinhado com escala de Hooper e prática de wellness em esportes coletivos. Não prescreve qualidade mínima de sono — dado informativo. |
| SS-TRAIN-006 | Recuperação / sono | Duração de sono registrada | Relato do atleta (horas) | `sleep_hours` | horas [0–24] | Domínio válido: [0, 24] (inclusivo). Fora do domínio → dado inválido. Não há threshold de qualidade prescrito nesta regra. | Regra de produto HB Track | INV-TRAIN-033. | Validação de domínio. Recomendações de duração ideal de sono (ex.: ≥ 8h para atletas de alta performance per ACSM) são informativas e não implementadas como threshold operacional. OPEN — revisar quando evidência longitudinal estiver disponível. |
| SS-TRAIN-007 | Monitoramento de carga / prevenção | Multiplicador de threshold de alerta de sobrecarga semanal por categoria | `threshold_base` (UA), `teams.alert_threshold_multiplier` (adimensional) | `threshold_critical` (UA) | UA | `threshold_critical = threshold_base × alert_threshold_multiplier`. Referência de produto: juvenis = 1.5, padrão = 2.0, adultos = 2.5. | Regra de produto HB Track | INV-TRAIN-014. NOTA: multiplicadores de referência são heurísticas de produto — não derivados de estudo publicado específico para handebol. | Implementado em INV-TRAIN-014. Multiplicador é configurável por equipe (`teams.alert_threshold_multiplier`). OPEN — revisão recomendada quando dados longitudinais de carga interna estiverem disponíveis (mínimo 1 temporada completa). |

## Regras de uso (classificação)
1. Se a afirmação for regra funcional do produto → registrar em `DOMAIN_RULES_TRAINING.md`.
2. Se for definição de termo → registrar em `docs/_canon/DOMAIN_GLOSSARY.md`.
3. Se for regra oficial do handebol → registrar em `docs/_canon/HANDBALL_RULES_DOMAIN.md` (ou ADR linkado).
4. Se for axioma estrutural do domínio → registrar em `.contract_driven/DOMAIN_AXIOMS.json`.

## Política de fontes autorizadas

Toda regra adicionada neste artefato **DEVE**:
- Declarar `Fonte` com `source_id` permitido para o módulo `training` conforme `docs/_canon/MODULE_SOURCE_AUTHORITY_MATRIX.yaml` (`EHF`, `ASPETAR`, `ACSM`).
- Declarar `Evidência` com referência rastreável (publicação, seção, URL canônica).
- Não declarar threshold universal sem escopo de população, posição, faixa etária e fase.

Gates que enforcement esta política:
- `MODULE_SOURCE_AUTHORITY_MATRIX_GATE` (ordem 2D) — valida autoridade de fonte por módulo.
- `EXTERNAL_SOURCE_AUTHORITY_GATE` (ordem 2I) — bloqueia fonte externa tratada como SSOT soberana.

## Background arquitetural

As decisões arquiteturais que embasam este artefato foram desenvolvidas em:
- `.dev/politicas/CIENCIA_HBTRACK.md` — análise completa de sport science rules para AMS (não-canônico, referência de background)
- `.dev/arquitetura/ARCH-DEC-TRAIN.md` — registro de decisões arquiteturais do módulo training (promovido para `docs/hbtrack/modulos/training/ARCH_DECISIONS_TRAINING.md`)

## Periodicidade de revisão

Regras neste artefato devem ser revisadas quando:
- A fonte original (ACSM, Aspetar, EHF) publicar atualização relevante.
- Uma regra for contestada com evidência contrária de nível igual ou superior.
- A aplicabilidade (população, fase, posição) mudar por decisão de produto.

Revisão deve seguir `docs/_canon/CHANGE_POLICY.md §11` (revisão científica periódica).

## Regra operacional de bloqueio
Se a tarefa exigir método/protocolo/cálculo/threshold técnico-científico e ele não estiver registrado neste artefato, **não inferir**. Emitir `BLOCKED_MISSING_SPORT_SCIENCE_RULES` e promover via `CHANGE_POLICY.md` e/ou bloquear conforme `CONTRACT_SYSTEM_RULES.md`.
