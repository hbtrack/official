# SENSITIVE_DOMAIN_GOVERNANCE.md

version: 1.0.0
status: PROPOSTO
decision_type: politica_de_governanca
scope: hb_track
owners:
  - arquitetura
  - backend
  - dados
  - analytics
  - ia
  - seguranca
  - conformidade
related_decisions:
  - HB_TRACK_ARCHITECTURE_DECISION.md
  - HB_TRACK_PERSISTENCE_POLICY.md
  - INGESTION_PROVIDER_CONTRACT.md
  - DTO_VIEWMODEL_BOUNDARY_RULES.md
related_modules:
  - wellbeing
  - psychology_support_ai
  - medical_health_adjacent
  - athletes
  - analytics
  - reports
  - audit
  - notifications
  - identity_access
related_artifacts:
  - docs/_ssot/openapi.json
  - docs/_ssot/schema.sql
  - docs/_canon/MANUAL_BACKEND_CANONICO.md
  - docs/_canon/REGRAS_SISTEMAS.md

---

## 1. Objetivo

Definir as regras canônicas de governança para qualquer capacidade do HB Track que manipule, derive, armazene, exponha ou operacionalize informações de domínio sensível.

Esta política existe para prevenir:

- mistura de inferências sensíveis com telemetria esportiva comum
- coleta excessiva de dados pessoais de alto risco
- promoção silenciosa de inferência probabilística para verdade autoritativa
- vazamento de dados restritos em dashboards, relatórios, exportações ou notificações
- uso indevido de outputs de IA em contextos de alto impacto
- ambiguidade arquitetural sobre limites de acesso, retenção, proveniência e revisão

---

## 2. Decisão Principal

O HB Track DEVE tratar os seguintes como contextos de domínio sensível sempre que forem individualmente identificáveis ou razoavelmente vinculáveis a um atleta, membro da equipe ou menor específico:

- observações psicológicas / de bem-estar
- avaliações de estado emocional
- observações de saúde adjacente
- indicadores de prontidão mental ou sofrimento
- flags de risco comportamental
- interpretações individualizadas derivadas de IA relacionadas a bem-estar, psicologia ou status de saúde adjacente
- qualquer pontuação, categoria, alerta ou tendência que possa afetar materialmente como uma pessoa é avaliada, selecionada, restringida, escalada ou monitorada

Esses contextos DEVEM ser governados como domínios de alto controle.

NÃO DEVEM ser tratados como analytics ordinário, metadados de conveniência ou enriquecimento genérico de perfil de atleta.

---

## 3. Definições de Domínio Sensível

### 3.1 Dados de domínio sensível

Dados de domínio sensível incluem qualquer registro, sinal, rótulo, flag, inferência, comentário, anotação, pontuação, tendência ou output derivado que revele ou sugira fortemente:

- condição mental ou emocional
- vulnerabilidade psicológica
- preocupação de saúde adjacente
- sofrimento, esgotamento, sobrecarga, instabilidade ou risco comportamental
- contexto pessoal protegido com risco elevado de uso indevido
- classificação de risco individualmente atribuível

Dados de domínio sensível podem ser:
- autorais humanos
- derivados do sistema
- derivados de IA
- importados
- inferidos de combinação de múltiplos sinais

---

### 3.2 Inferência de domínio sensível

Inferência de domínio sensível significa qualquer output do sistema que transforma entradas em uma interpretação individualizada como:

- "em risco"
- "emocionalmente instável"
- "probabilidade de esgotamento"
- "prontidão psicológica baixa"
- "declínio de atenção"
- "estresse elevado"
- "precisa de intervenção"
- "atleta de alta preocupação"

Uma inferência de domínio sensível permanece sensível mesmo se for probabilística, aproximada, consultiva ou de baixa confiança.

---

### 3.3 Uso de alto impacto

Um uso de alto impacto existe quando dados de domínio sensível poderiam influenciar:

- seleção ou exclusão de atleta
- tempo de jogo ou restrição de participação
- seguimento disciplinar
- escalamento para guardiões/responsáveis
- encaminhamento para suporte
- intervenção de treinador ou equipe
- categorização reputacional
- perfilamento longitudinal

Qualquer funcionalidade que suporte esses resultados deve usar os controles mais rigorosos desta política.

---

## 4. Princípios de Governança

### 4.1 Necessidade de conhecer apenas
Acesso a dados de domínio sensível deve ser baseado em necessidade operacional explícita, não em conveniência ampla de papel.

### 4.2 Coleta mínima
Colete apenas a menor quantidade de dados sensíveis necessária para o caso de uso declarado do produto.

### 4.3 Limitação de propósito
Dados de domínio sensível só podem ser processados para propósitos explicitamente definidos.

### 4.4 Proveniência sobre suposição
Nenhum registro de domínio sensível pode existir sem proveniência, classificação de origem e atribuição de autor/fonte.

### 4.5 Revisão antes de autoridade
Outputs sensíveis probabilísticos ou derivados de IA não devem se tornar verdade autoritativa sem política de revisão definida.

### 4.6 Separação de contexto
Dados de domínio sensível devem permanecer arquiteturalmente e semanticamente separados de dashboards gerais de performance, a menos que política explícita permita exposição limitada.

### 4.7 Honestidade temporal
O sistema deve distinguir:
- fato observado
- interpretação autorada
- inferência candidata derivada de IA
- conclusão revisada

### 4.8 Responsabilidade humana
Onde outputs podem afetar materialmente uma pessoa, o limite de revisão e o papel humano responsável devem ser explícitos.

---

## 5. Classes Sensíveis Canônicas

Todo registro de domínio sensível DEVE declarar uma `sensitivity_class`.

Valores canônicos permitidos:

- `sensitive_health_adjacent`
- `sensitive_psychological`
- `sensitive_minor_related`
- `regulated_high_control`

Nenhuma classificação mais fraca é permitida para este domínio.

Além disso, todo registro deve declarar um `access_classification`.

Valores canônicos permitidos:

- `restricted_medical`
- `restricted_sensitive`
- `system_only`

---

## 6. Tipos de Registro de Domínio Sensível Permitidos

Registros de domínio sensível PODEM incluir apenas tipos explicitamente modelados como:

- `wellbeing_checkin_response`
- `psychological_observation_note`
- `health_adjacent_flag`
- `ai_wellbeing_candidate_inference`
- `reviewed_sensitive_alert`
- `sensitive_followup_recommendation`
- `guardian_contact_escalation_record`
- `sensitive_access_audit_event`

Não deve existir nenhum compartimento de armazenamento ad hoc de forma livre para dados sensíveis arbitrários.

---

## 7. Categorias de Dados por Nível de Autoridade

### 7.1 Fato observado
Exemplos:
- atleta enviou um check-in de bem-estar
- treinador registrou que atleta saiu da sessão mais cedo
- atleta reportou sono ruim em entrada estruturada

Autoridade:
- ocorrência factual apenas
- não autoriza conclusão interpretiva por si só

---

### 7.2 Interpretação autorada por humano
Exemplos:
- nota de psicólogo/equipe
- preocupação profissional revisada
- recomendação estruturada de acompanhamento

Autoridade:
- interpretativa mas atribuível
- deve incluir papel do autor, timestamp e contexto de revisão

---

### 7.3 Inferência candidata derivada de IA
Exemplos:
- "candidato de sofrimento elevado"
- "possível padrão de sobrecarga"
- "candidato de queda de atenção"

Autoridade:
- apenas consultiva
- nunca autoritativa por padrão
- requer proveniência, metadados do modelo e status de revisão

---

### 7.4 Conclusão operacional revisada
Exemplos:
- recomendação revisada para acompanhamento
- alerta aprovado para fluxo de trabalho restrito
- sinal revisado aceito

Autoridade:
- depende da política de fluxo de trabalho e papel
- deve preservar a trilha de revisão que levou à conclusão

---

## 8. Requisitos de Fonte e Proveniência

Todo registro de domínio sensível DEVE carregar no mínimo:

- `record_id`
- `record_type`
- `source_type`
- `source_system`
- `source_record_id` quando disponível
- `actor_type`
- `actor_id` quando disponível
- `created_at`
- `observed_at` ou `occurred_at` quando relevante
- `sensitivity_class`
- `access_classification`
- `review_status`
- `provenance_summary`

Se derivado de IA, DEVE adicionalmente carregar:

- `model_name`
- `model_version`
- `confidence_level` se disponível
- `confidence_label` se disponível
- `input_scope_summary`
- `review_required`

---

## 9. Contrato de Status de Revisão

Todo registro de domínio sensível DEVE declarar `review_status`.

Valores permitidos:

- `not_required`
- `pending_human_review`
- `reviewed_accepted`
- `reviewed_rejected`
- `reviewed_corrected`
- `expired_unreviewed`

Regras:

1. Registros sensíveis derivados de IA têm padrão `pending_human_review`.
2. Registros de alto impacto não podem ser operacionalizados enquanto estiverem `pending_human_review`, a menos que uma política de emergência separada explicitamente exista.
3. `reviewed_corrected` deve preservar tanto a interpretação original quanto a corrigida.
4. Registros `expired_unreviewed` não devem permanecer silenciosamente ativos em dashboards ou alertas.

---

## 10. Regras de Controle de Acesso

### 10.1 Privilégio mínimo
Apenas papéis explicitamente autorizados podem acessar registros de domínio sensível.

### 10.2 Acesso de dupla dimensão
O acesso deve ser avaliado por:
- capacidade de papel
- escopo contextual

Exemplos de escopo contextual:
- membership de organização
- atribuição de equipe
- atribuição de suporte
- relacionamento com atleta
- responsabilidade de caso ativo

### 10.3 Acesso segmentado
Papéis genéricos de coaching não devem herdar automaticamente acesso a detalhes psicológicos ou de saúde adjacente.

### 10.4 Redação por endpoint
Diferentes endpoints podem expor:
- detalhe completo
- detalhe parcial
- apenas alert booleano
- apenas contagem agregada
- sem acesso

### 10.5 Restrição de exportação
Exportação de domínio sensível deve ser desabilitada por padrão e habilitada apenas sob política controlada explícita.

---

## 11. Regras de Separação Arquitetural

### 11.1 Contexto delimitado separado
Registros de domínio sensível devem residir em um contexto delimitado separado ou limite lógico estrito equivalente.

### 11.2 Nenhuma junção silenciosa em perfil genérico de atleta
Detalhes de domínio sensível não devem ser mesclados em respostas genéricas de perfil de atleta por conveniência.

### 11.3 Nenhuma contaminação de dashboard genérico
Dashboards gerais de performance não devem incluir silenciosamente pontuações, flags ou categorias inferidas de domínio sensível.

### 11.4 Apenas endpoints de ponte explícitos
Se qualquer dashboard ou fluxo de trabalho precisar de um resumo sensível, deve usar um endpoint projetado para aquele nível específico de exposição.

---

## 12. Regras de Exposição de DTO e ViewModel

### 12.1 Apenas DTO explícito
Campos sensíveis podem aparecer apenas em DTOs explicitamente projetados e documentados para acesso sensível.

### 12.2 Nenhum vazamento em reutilização genérica de DTO
Um `AthleteProfileDto`, `TrainingSessionDto` ou `DashboardDto` genérico não deve ganhar campos sensíveis oportunisticamente.

### 12.3 ViewModels devem preservar limites de acesso
ViewModels de frontend não devem mesclar detalhes sensíveis restritos em visões não sensíveis, a menos que o endpoint e a política de acesso de UI explicitamente autorizem.

### 12.4 Rótulos não devem amplificar autoridade
Rótulos de UI como:
- "instável"
- "atleta problemático"
- "alto risco"
- "atleta com bandeira vermelha"

são proibidos, a menos que explicitamente revisados e justificados pela política de domínio.

Prefira linguagem neutra e limitada como:
- "revisão recomendada"
- "acompanhamento pendente"
- "status sensível disponível para equipe autorizada"

---

## 13. Regras de Retenção

Todo registro de domínio sensível DEVE definir semânticas de retenção.

Campos obrigatórios:
- `retained_until` ou referência de política equivalente
- `retention_basis`
- `deletion_mode`
- `legal_hold_flag` quando aplicável

Modos de exclusão permitidos:
- `hard_delete_allowed`
- `soft_delete_with_audit`
- `immutable_record_with_access_revocation`

Regras:
1. Nenhuma retenção indefinida por acidente.
2. Candidatos sensíveis de IA rejeitados devem ter retenção mais curta, a menos que a política exija o contrário.
3. Conclusões revisadas devem preservar rastreabilidade onde operacionalmente necessário.
4. Exclusão não deve apagar evidências obrigatórias de auditoria de ações de acesso e revisão.

---

## 14. Regras de Notificação

### 14.1 Nenhum payload sensível bruto em notificações
Notificações nunca devem incluir detalhes sensíveis brutos, a menos que o canal de entrega e a política de acesso explicitamente permitam.

### 14.2 Padrão de notificação mais seguro
Notificações devem carregar prompts mínimos como:
- "Um item de acompanhamento restrito requer sua revisão."
- "Uma atualização de caso sensível está disponível."

### 14.3 Restrição de canal
Notificações de domínio sensível devem respeitar a política de canal.
Canais não controlados não devem receber conteúdo sensível.

### 14.4 Restrição de destinatário
Notificações devem ser entregues apenas a destinatários autorizados com escopo contextual.

---

## 15. Regras de Relatórios e Analytics

### 15.1 Analytics sensível é separado por padrão
Analytics de domínio sensível não devem ser mesclados em analytics de performance comum, a menos que explicitamente governado.

### 15.2 Limite de agregação
Estatísticas sensíveis agregadas só devem ser mostradas onde o risco de re-identificação é adequadamente controlado.

### 15.3 Nenhuma pontuação encoberta
Não derive pontuações compostas encobertas que combinem silenciosamente sinais de bem-estar/psicológicos com métricas de performance esportiva.

### 15.4 Segregação de revisados vs não revisados
Analytics deve distinguir:
- registros sensíveis revisados
- candidatos de IA não revisados
- registros rejeitados
- registros expirados

Nunca devem ser misturados silenciosamente.

---

## 16. Regras de Governança de IA

### 16.1 Outputs de IA são consultivos por padrão
Outputs de IA de domínio sensível são candidatos ou recomendações, não verdade autoritativa.

### 16.2 Metadados obrigatórios de IA
Todo output sensível derivado de IA DEVE incluir:
- nome do modelo
- versão do modelo
- timestamp de geração
- resumo do escopo de entrada
- metadados de confiança quando aplicável
- requisito de revisão
- resumo de explicação se disponível e seguro para expor

### 16.3 Nenhum gatilho de fluxo de trabalho irreversível apenas por IA
Output de IA não deve por si só:
- restringir participação
- rotular uma pessoa negativamente
- criar status permanente
- desencadear ação disciplinar
- notificar guardiões com detalhe sensível
- alterar classificação de perfil de atleta permanentemente

a menos que uma política revisada explicitamente autorize esse fluxo de trabalho e preserve a responsabilidade.

### 16.4 Firewall de dados de treinamento
Outputs de domínio sensível não devem ser reutilizados como telemetria genérica de produto sem governança explícita.

---

## 17. Regras de Proteção de Menores

Se o sujeito é um menor ou existe contexto relacionado a menores, o sistema DEVE aplicar controle mais rigoroso.

Considerações obrigatórias:
- escopo de acesso mais estreito
- política de notificação mais rigorosa
- controles de fluxo de trabalho de guardião/escalamento
- revisão de retenção mais rigorosa
- expectativas de auditoria mais fortes

Dados sensíveis relacionados a menores nunca devem ser expostos em dashboards de conveniência, exportações amplas ou fluxos de mensagens com controle frouxo.

---

## 18. Requisitos de Auditoria

Toda ação do ciclo de vida de domínio sensível DEVE ser auditável.

Ações auditáveis incluem:
- criar
- ler
- atualizar
- revisar
- rejeitar
- corrigir
- tentativa de exportação
- envio de notificação
- ação de escalamento
- exclusão ou revogação de acesso

Registros de auditoria devem incluir:
- identidade do ator
- papel do ator
- timestamp
- tipo de ação
- registro alvo
- resultado
- razão contextual quando disponível

Os próprios logs de auditoria sensível podem requerer acesso restrito, mas devem existir.

---

## 19. Estados Canônicos de Fluxo de Trabalho

Fluxo de trabalho canônico recomendado para registros de domínio sensível:

1. recebido
2. classificado
3. validado
4. com-escopo-de-acesso
5. revisao_pendente
6. revisado_aceito / revisado_rejeitado / revisado_corrigido
7. operacionalizado se permitido
8. retido / arquivado / excluído de acordo com política

Nenhum registro deve pular de ingestão para uso operacionalizado de alto impacto sem passar pelo gate de revisão obrigatório.

---

## 20. Padrões Proibidos

Os seguintes padrões são proibidos.

### 20.1 Sensível por inferência mas rotulado inseguramente como normal
Não armazene interpretação individualizada de sofrimento ou psicológica como metadados comuns de analytics.

### 20.2 Promoção de verdade de IA sem revisão
Não trate inferência sensível de IA como fato autoritativo sem política de revisão definida.

### 20.3 Detalhes sensíveis em DTOs genéricos
Não vaze campos sensíveis em contratos de transporte genéricos de atleta, partida, treino ou dashboard.

### 20.4 Visibilidade de papel amplo
Não exponha detalhes sensíveis a todos os treinadores, toda a equipe ou todos os administradores por conveniência.

### 20.5 Excesso de compartilhamento em notificação
Não envie conteúdo sensível detalhado por canais de notificação não controlados.

### 20.6 Pontuação opaca composta
Não compute pontuações ocultas de atleta misturando sinais psicológicos/de bem-estar com métricas de performance sem governança explícita e divulgação.

### 20.7 Retenção silenciosa
Não mantenha candidatos sensíveis rejeitados, expirados ou de baixo valor indefinidamente sem política.

### 20.8 Sobrescrita destrutiva do histórico interpretativo
Não sobrescreva conclusões revisadas ou notas autorais sem preservar o histórico de correção.

---

## 21. Checklist de Revisão para Novas Funcionalidades Sensíveis

Toda nova funcionalidade de domínio sensível deve responder:

1. Qual categoria exata de dados sensíveis está envolvida?
2. A funcionalidade é observacional, interpretativa ou inferencial?
3. IA está envolvida?
4. Qual é o propósito operacional?
5. Qual é o resultado de maior impacto possível?
6. Quem pode acessá-la e sob qual escopo contextual?
7. Quais DTOs a expõem?
8. Quais notificações podem mencioná-la?
9. Qual é o gate de revisão?
10. Qual é a política de retenção?
11. Quais eventos de auditoria são emitidos?
12. O mesmo objetivo pode ser alcançado com menos dados sensíveis?

Se essas respostas estiverem incompletas, a funcionalidade não está pronta para governança.

---

## 22. Exemplos de Níveis de Exposição

### 22.1 Endpoint de detalhe restrito completo
Público:
- papel de suporte explicitamente autorizado

Conteúdo possível:
- nota revisada
- proveniência
- histórico de revisão
- recomendações restritas

### 22.2 Endpoint de alerta limitado de coaching
Público:
- treinador autorizado com necessidade de conhecer

Conteúdo possível:
- `followUpRecommended = true`
- `reviewStatus = reviewed_accepted`
- sem corpo de nota detalhada
- sem justificativa bruta de inferência

### 22.3 Dashboard genérico
Público:
- conjunto amplo de usuários operacionais

Conteúdo possível:
- nenhum por padrão

Se explicitamente permitido:
- contagem de itens restritos pendentes apenas para revisor autorizado

---

## 23. Exemplo de Formato de Registro

```yaml
sensitive_record:
  record_id: "sens_001"
  record_type: "ai_wellbeing_candidate_inference"
  subject_type: "athlete"
  subject_id: "ath_123"

  source_type: "ai_cv_extraction"
  source_system: "hb_wellbeing_model"
  source_record_id: "pred_889"

  created_at: "2026-03-11T18:30:00Z"
  observed_at: "2026-03-11T18:20:00Z"

  sensitivity_class: "sensitive_psychological"
  access_classification: "restricted_sensitive"

  review_status: "pending_human_review"
  review_required: true

  model_name: "hb_wellbeing_model"
  model_version: "1.2.0"
  confidence_level: 0.77
  confidence_label: "medium"

  provenance_summary:
    input_scope: "checkin_estruturado + indicadores recentes de carga de trabalho"
    generation_context: "triagem pre-treino"

  payload:
    candidate_label: "follow_up_recommended"
    rationale_summary: "padrão indica possível preocupação relacionada a sobrecarga"

  retained_until: "2026-06-11T00:00:00Z"
  retention_basis: "candidate_sensitive_inference_policy_v1"
```

---

## 24. Regras de Integração com Outros Contratos

### 24.1 Com o contrato de ingestão
Registros de domínio sensível devem herdar:
- proveniência
- classificação de fonte
- status de normalização
- semânticas de revisão

### 24.2 Com as regras de limite DTO/ViewModel
Exposição sensível deve usar apenas DTOs dedicados e ViewModels limitados.

### 24.3 Com a política de persistência
Módulos sensíveis são tipicamente HYBRID / RESTRITO:
- estado transacional de fluxo de trabalho atual onde necessário
- fatos revisados append-only e trilha de auditoria onde o histórico importa

### 24.4 Com notificações
Notificações devem carregar apenas prompts mínimos de ação, a menos que um canal aprovado mais rigoroso exista.

---

## 25. Definição de Pronto

Esta política está PRONTA apenas quando:
- toda funcionalidade de domínio sensível declara classe de sensibilidade e classificação de acesso
- registros sensíveis derivados de IA sempre carregam status de revisão e proveniência do modelo
- campos sensíveis são expostos apenas por meio de DTOs explícitos
- dashboards genéricos não incluem silenciosamente sinais sensíveis
- templates de notificação não vazam conteúdo sensível bruto
- semânticas de retenção e exclusão existem para registros sensíveis
- todas as leituras e ações de revisão são auditáveis
- tratamento sensível relacionado a menores aplica controles mais rigorosos
- nenhuma ação operacional de alto impacto ocorre apenas a partir de output de IA não revisado
