---
# TEMPLATE: module-doc-template
# DEST: docs/hbtrack/modulos/exercises/MODULE_SCOPE_EXERCISES.md
# SOURCE: .contract_driven/templates/modulos/MODULE_SCOPE_{{MODULE_NAME_UPPER}}.md
module: "exercises"
system_scope_ref: "../../../_canon/SYSTEM_SCOPE.md"
handball_rules_ref: "../../../_canon/HANDBALL_RULES_DOMAIN.md"
handball_semantic_applicability: true
contract_path_ref: "../../../../contracts/openapi/paths/exercises.yaml"
schemas_ref: "../../../../contracts/schemas/exercises/"
type: "module-scope"
decisions_ref: "../../../../docs/hbtrack/decisoes/ARCH_DECISIONS_TRAINING.md (TRAIN-DEC-047, TRAIN-DEC-048)"
updated: "2026-03-16"
---

# MODULE_SCOPE_EXERCISES.md

## Objetivo
Definir claramente o que o módulo `exercises` faz e o que não faz.

## Missão do módulo
`exercises` existe para ser a **fonte soberana da biblioteca de exercícios de handebol do HB Track** — definindo, criando, versionando e governando exercícios como objetos de domínio ricos, classificados e relacionados semanticamente.

## Responsabilidades

- Definir, criar e manter exercícios como objetos de domínio ricos e versionados.
- Classificar exercícios por atributos pedagógicos e operacionais: fase de sessão, objetivo primário, fase de jogo, categoria etária, nível de habilidade, carga física, espaço necessário, número de atletas, materiais, complexidade.
- Manter relações semânticas entre exercícios: progressão, regressão, variação, contraindicação.
- Versionar exercícios de forma append-only: cada edição cria uma nova versão imutável (TRAIN-DEC-048).
- Governar escopo de conteúdo (SYSTEM vs ORG) e visibilidade (org_wide vs restricted) com ACL por usuário.
- Servir como fonte soberana de exercícios para o módulo `training` e qualquer outro módulo consumidor (TRAIN-DEC-047).
- Expor representações otimizadas por contexto de uso: preview DTO (listagem/scan) e full DTO (detalhe/edição).

## Atores

| Ator | Papel |
|---|---|
| Treinador (usuário ORG) | Cria, edita e gerencia exercícios ORG; configura ACL e visibilidade |
| Curador HB Track (usuário SYSTEM) | Cria e mantém exercícios SYSTEM disponíveis a todos os usuários autenticados |
| Módulo `training` | Consome `exercises` como lookup soberano; referencia `exercise_id + exercise_version_id` |
| Módulo `analytics` | Consome `exercises` read-only para métricas de uso e recomendação contextual |
| Módulo `audit` | Observa operações de criação, edição e exclusão de exercícios |

## Entidades principais

| Entidade | Papel |
|---|---|
| `Exercise` | Agregado principal — representa um exercício de handebol com atributos pedagógicos e operacionais |
| `ExerciseVersion` | Fato append-only — snapshot imutável de todos os atributos do exercício em uma edição |
| `ExerciseACL` | Controle de acesso por usuário para exercícios ORG com `visibility_mode = RESTRICTED` |
| `ExerciseRelation` | Relação semântica direcional e tipada entre dois exercícios (PROGRESSION, REGRESSION, VARIATION, CONTRAINDICATION) |

## Entradas
- Requests HTTP definidos em `contracts/openapi/paths/exercises.yaml`
- Dados persistidos/consultados definidos em schemas de `contracts/openapi/components/schemas/exercises/`
- Identidade e permissões do usuário via JWT (módulo `identity_access`)
- Eventos, quando aplicável

## Saídas
- Responses HTTP (preview DTO em listagem; full DTO em detalhe)
- Mudanças de estado do domínio (criação de exercício, nova versão, configuração de ACL, relação semântica)
- Eventos, quando aplicável
- Dados soberanos consumidos por `training` via `exercise_id + exercise_version_id`

## Dentro do escopo

- Criação, edição (via nova versão) e soft-delete de exercícios ORG e SYSTEM
- Classificação pedagógica completa de exercícios (todos os atributos de domínio)
- Versionamento append-only com histórico completo de versões acessível
- Relações semânticas entre exercícios (progressão, regressão, variação, contraindicação)
- Governança de escopo SYSTEM vs ORG e visibilidade RESTRICTED vs ORG_WIDE
- ACL por usuário para exercícios RESTRICTED
- Endpoint de cópia `POST /exercises/{id}/copy` para adaptar exercício SYSTEM como exercício ORG editável
- Exposição de preview DTO (listagem) e full DTO (detalhe)

## Fora do escopo

- **Sessões de treino, blocos, execução**: escopo exclusivo do módulo `training`.
- **Analytics de uso de exercícios**: escopo do módulo `analytics`. `exercises` não calcula métricas de uso.
- **Delivery de assets de mídia**: exercício referencia `asset_id` / URL; não armazena binário. Media delivery é responsabilidade de camada desacoplada (ADR pendente).
- **Hierarquia federativa / conteúdo institucional**: escopo INSTITUTIONAL explicitamente diferido. O modelo atual é SYSTEM + ORG. Parceiros e federações requerem ADR próprio de governança editorial e modelo comercial.
- **Recomendação de exercícios**: responsabilidade do módulo `analytics` (Fase 2). `exercises` expõe filtros estruturados; `analytics` produz recomendação contextual.

## Dependências
- Módulos upstream: `identity_access` (autenticação JWT, RBAC, scopes de permissão)
- Módulos downstream: `training`, `analytics`, `audit`
- Artefatos globais:
  - `SYSTEM_SCOPE.md`
  - `HANDBALL_RULES_DOMAIN.md`

| Módulo | Direção | Papel |
|---|---|---|
| `identity_access` | `exercises` consome | Autenticação JWT, RBAC, scopes de permissão |
| `training` | `training` consome `exercises` | `training` referencia `exercise_id + exercise_version_id` como lookup; não persiste exercício |
| `analytics` | `analytics` consome `exercises` | métricas de uso, recomendação contextual — read-only |
| `audit` | `audit` observa `exercises` | operações de criação, edição, exclusão de exercícios são auditáveis |

## Regras de fronteira
1. O módulo não deve assumir responsabilidades de outro módulo sem decisão explícita.
2. O módulo não deve expor comportamento fora do seu contrato.
3. Toda exceção de escopo deve ser registrada formalmente.
4. **`training` NÃO PODE** criar, editar ou excluir exercícios; armazenar atributos de exercício fora de `exercise_id + exercise_version_id`; expor endpoints de biblioteca de exercícios. (TRAIN-DEC-047)
5. **`training` PODE** referenciar `exercise_id + exercise_version_id` em `session_exercise`; ler exercício via GET /exercises/{id} e GET /exercises/{id}/versions/{versionId}; filtrar via GET /exercises.
6. Usuário ORG não pode criar, editar nem excluir exercício SYSTEM → 403. Para adaptar exercício SYSTEM, usa `POST /exercises/{id}/copy` (DR-EXB-009).

## Conteúdo e escopos

| Scope | Criador | Visibilidade padrão | Edição |
|---|---|---|---|
| `SYSTEM` | Plataforma HB Track (curador) | Todos os usuários autenticados | Somente curador; usuário ORG não pode editar |
| `ORG` | Treinador da organização | `RESTRICTED` (apenas criador) por default | Criador; compartilhar exige ação explícita (ACL ou org_wide) |
