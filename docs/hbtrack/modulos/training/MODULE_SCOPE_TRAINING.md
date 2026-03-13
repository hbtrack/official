---
module: "training"
system_scope_ref: "../../../_canon/SYSTEM_SCOPE.md"
handball_rules_ref: "../../../_canon/HANDBALL_RULES_DOMAIN.md"
handball_semantic_applicability: true
contract_path_ref: "../../../../contracts/openapi/paths/training.yaml"
schemas_ref: "../../../../contracts/schemas/training/"
type: "module-scope"
---

# MODULE_SCOPE_TRAINING.md

## Objetivo
Definir claramente o que o módulo `training` faz e o que não faz.

## Missão do módulo
O módulo `training` existe para suportar o ciclo completo de planejamento, execução, registro e análise de sessões de treinamento de handebol, respeitando a periodização, categorias, posições e fases do jogo da modalidade.

## Responsabilidades
- Planejamento de sessões de treino com exercícios, objetivos, carga e foco
- Registro de execução de treinos (horário real, duração, presença de atletas)
- Coleta de dados de wellness pré-treino (disposição, sono, dor muscular)
- Coleta de dados de wellness pós-treino (RPE, fadiga, sensação pós-treino)
- Vínculo de sessões a equipes, temporadas e categorias
- Suporte a periodização em 4 níveis: macrociclo (temporada) → mesociclo → microciclo (semana) → sessão
- Classificação de exercícios por posição-alvo (conforme HBR-014) e fase do jogo
- Fornecimento de dados de carga interna/externa para o módulo `analytics`

## Atores
- **Treinador**: planeja e executa sessões, registra detalhes e wellness
- **Coordenador**: aprova planos, revisa sessões executadas, ajusta periodização
- **Atleta**: visualiza próprio histórico de treinos e wellness
- **Dirigente**: acessa relatórios executivos derivados de treinos

## Entidades principais
- `TrainingSession` — sessão de treino planejada ou executada
- `Exercise` — exercício individual dentro de uma sessão
- `WellnessPre` — dados de wellness pré-treino
- `WellnessPost` — dados de wellness pós-treino (RPE, fadiga)
- `Periodization` — estrutura de macrociclo, mesociclo, microciclo

## Entradas
- Requests HTTP definidos em `contracts/openapi/paths/training.yaml`
- Dados de equipes e atletas (upstream: módulo `teams`)
- Dados de temporadas (upstream: módulo `seasons`)
- Dados de exercícios catalogados (upstream: módulo `exercises`)

## Saídas
- Responses HTTP (sessões criadas, atualizadas, listadas)
- Mudanças de estado de sessões (draft → scheduled → in_progress → pending_review → readonly)
- Dados de carga e volume consumidos por `analytics`
- Histórico de wellness para análise de sobrecarga

## Dentro do escopo
- Planejamento de sessões de treino
- Registro de execução e presença
- Coleta de wellness (pré e pós)
- Periodização de treinos
- Classificação de exercícios por posição e fase do jogo (conforme HBR-014)
- Histórico de treinos para analytics

## Fora do escopo
- Registro de partidas oficiais ou amistosos (módulo `matches`)
- Scout de eventos de jogo (módulo `scout`)
- Gestão de lesões, consultas e tratamentos médicos (módulo `medical`)
- Cálculo de métricas, KPIs e dashboards (módulo `analytics`)
- Cadastro de exercícios no catálogo global (módulo `exercises`)
- Notificações push/email sobre treinos (módulo `notifications`)

## Dependências
- Módulos upstream: `teams`, `seasons`, `exercises`
- Módulos downstream: `analytics`, `wellness`
- Artefatos globais:
  - `SYSTEM_SCOPE.md`
  - `HANDBALL_RULES_DOMAIN.md` (HBR-014: Treino Orientado à Modalidade)

## Regras de fronteira
1. O módulo não deve assumir responsabilidades de outro módulo sem decisão explícita.
2. O módulo não deve expor comportamento fora do seu contrato.
3. Toda exceção de escopo deve ser registrada formalmente.
