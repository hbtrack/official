---
module: "training"
topic: "coach-athlete-interaction-3-layers"
related_files:
  - "UI_CONTRACT_TRAINING.md (D-UI-20, D-UI-21)"
  - "COACH_FEATURE_ENGINEERING_TRAINING.md"
  - "MODULE_SCOPE_TRAINING.md"
date_created: "2026-03-17"
version: "3.0.0 (3-layer: IA→Trainer→Athlete)"
type: "architecture-flow"
---

# COACH_INTERACTION_FLOW_TRAINING.md

## Propósito
Documentar as **3 camadas de interação** do HB Pro Coach:

1. **IA ↔ Treinador:** IA sugere exercício (com dados) → Treinador aprova
2. **Treinador ↔ Atleta:** Treinador envia treino aprovado
3. **IA ↔ Atleta:** IA explica exercício (técnica, tática, física)

---

## Arquitetura: 3 Camadas

```
┌─────────────────────────────────────────────────────────────┐
│ CAMADA 1: IA ↔ TREINADOR (Decision Support)                │
│ ────────────────────────────────────────────────────────────│
│ IA consulta Feature Store                                  │
│ ↓                                                           │
│ IA identifica: necessidades + gaps + restrições            │
│ ↓                                                           │
│ IA SUGERE exercício ao treinador (com justificativa)       │
│ ↓                                                           │
│ Treinador APROVA / NEGA / EDITA                            │
│ └─→ AsyncAPI event: training.suggested.approved            │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ CAMADA 2: TREINADOR ↔ ATLETA (Prescription)                │
│ ────────────────────────────────────────────────────────────│
│ Treinador envia treino APROVADO pra equipe                 │
│ (ou notifica atleta diretamente)                           │
│ └─→ TrainingSession.status = PUBLISHED                     │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ CAMADA 3: IA ↔ ATLETA (Explanation)                        │
│ ────────────────────────────────────────────────────────────│
│ Atleta vê treino aprovado e pergunta:                      │
│ "Por que treino agachamento?"                              │
│ ↓                                                           │
│ IA EXPLICA exercício (técnica + tática + física)           │
│ ("Vi que você treina FORÇA porque sua velocidade...")      │
│ └─→ IA acessa: exercício já aprovado + feature store       │
└─────────────────────────────────────────────────────────────┘
```

---

## CAMADA 1: IA → TREINADOR (Sugestão de Exercício)

### Flow Completo

```
GATILHO #1 — Atleta faltou treino:
  Atleta: (não apareceu no treino de velocidade ontem)
  
  ↓
  
GATILHO #2 — IA detecta necessidade:
  IA consulta Feature Store:
  ├─ Último treino concluído: 2 dias atrás
  ├─ Fadiga: 5.8/10 (baixa — pode treinar hoje)
  ├─ Performance gap: velocidade = 11% abaixo meta
  ├─ Injury status: nenhuma restrição
  └─ Recommended focus: velocidade + técnica
  
  ↓
  
ACTION #1 — IA SUGERE ao Treinador:
  Sistema backend: POST /hb-pro-coach/trainer-suggestions
  
  Payload:
  {
    "athlete_id": "ath-001",
    "suggestion_type": "compensatory_training",
    "features": {
      "fatigue_score": 5.8,
      "performance_gap": {
        "velocity": 11,
        "technical": -2
      },
      "recommended_focus": ["velocity", "technique"]
    },
    "suggested_session": {
      "name": "VELOCIDADE COMPENSATÓRIA — PONTA",
      "duration_min": 45,
      "objectives": ["velocity", "explosive_movement"],
      "blocks": [
        {
          "phase": "warmup",
          "duration_min": 5,
          "exercise_id": "ex-002",  // Aquecimento dinâmico
          "description": "Mobilidade de ombro + core"
        },
        {
          "phase": "main",
          "duration_min": 25,
          "exercise_id": "ex-045",  // Sprint em transição
          "description": "Sprint 0-10m contra defesa lenta"
        },
        {
          "phase": "main",
          "duration_min": 10,
          "exercise_id": "ex-067",  // Arremesso de velocidade
          "description": "Arremesso rápido em movimento"
        },
        {
          "phase": "cool_down",
          "duration_min": 5,
          "exercise_id": "ex-101",  // Recuperação
          "description": "Alongamento + respiração"
        }
      ]
    },
    "rationale": "Atleta perdeu sessão de velocidade quando fadiga estava baixa. Compensação hoje = ganho pedagógico real.",
    "created_at": "2026-03-17T14:30:00Z"
  }
  
  ↓
  
ACTION #2 — Treinador vê sugestão via UI:
  Dashboard do Treinador:
  ┌──────────────────────────────────────────┐
  │ SUGESTÃO DO COACH                        │
  ├──────────────────────────────────────────┤
  │ Atleta:        João Silva (PONTA)        │
  │ Sugestão:      VELOCIDADE COMPENSATÓRIA  │
  │ Duração:       45min                     │
  │ Status fadiga: 5.8/10 (VERDE — OK!)     │
  │ Gap velocity:  -11% (CRÍTICO)            │
  │                                          │
  │ Blocos:                                  │
  │ 1. Aquecimento (5min)                    │
  │ 2. Sprint 0-10m (25min)                  │
  │ 3. Arremesso rápido (10min)              │
  │ 4. Recuperação (5min)                    │
  │                                          │
  │ [Aprovar] [Recusar] [Editar & Aprovar]  │
  └──────────────────────────────────────────┘
  
  ↓
  
ACTION #3 — Treinador APROVA:
  Backend: POST /training/suggestions/{id}/approve
  
  AsyncAPI event (emit):
  {
    "event_type": "training.suggestion.approved",
    "athlete_id": "ath-001",
    "session_id": "sess-new-123",
    "session_data": { ...full session },
    "approved_at": "2026-03-17T14:35:00Z",
    "approved_by": "trainer-001"
  }
  
  ↓
  
RESULTADO: TrainingSession criada + status = PUBLISHED
```

### Quando IA Sugere

**Cenário 1: Atleta faltou treino**
```
Resultado:
- IA detecta: faltou velocidade, fadiga baixa (5.8), gap = -11%
- IA sugere: "VELOCIDADE PONTA 45min" com blocos
- Treinador aprova
- Atleta recebe notificação: "Seu treino foi atualizado!"
```

**Cenário 2: Performance gap crescente**
```
Resultado:
- IA detecta: força caiu 15% em 2 semanas, recomendado = força
- IA sugere: "FORÇA EXPLOSIVA PONTA 50min"
- Treinador aprova (ou modifica carga)
- Atleta treina com aprovação presencial
```

**Cenário 3: Atleta será notificado automaticamente**
```
Resultado:
- IA sugere repouso/mobilidade (fadiga = 8.5)
- Treinador aprova
- Atleta recebe: "Hoje é dia leve! Foco em recuperação 💚"
```

---

## CAMADA 2: TREINADOR → ATLETA (Prescrição)

O treinador envia o treino aprovado via app/email/SMS:

```
📱 Notificação para João Silva:

"Seu treino para amanhã foi atualizado! ⚡

VELOCIDADE COMPENSATÓRIA — PONTA
Data: 18 de março, 19:30
Local: Quadra Principal

Detalhes: [ver no app]

Seu treinador preparou isso especialmente pra você!"
```

---

## CAMADA 3: IA ↔ ATLETA (Explicação de Exercício)

Agora o atleta vê o treino aprovado E PERGUNTA SOBRE OS EXERCÍCIOS.

### 3.1 Pergunta #1: "Por quê ESTE exercício?"

```
Atleta: "Por que treino agachamento amanhã?"

IA PROCESSA:
  1. Query: qual exercício? → "agachamento" (ex-045)
  2. Query: status aprovação? → APPROVED (treinador autorizou)
  3. Query Feature Store:
     ├─ performance_gap.velocity = -11%
     ├─ position = PONTA
     ├─ fatigue_score = 5.8
     └─ session_context = "compensatório velocidade"
  4. Query HANDBALL_RULES: padrão técnico/tático para PONTA

RESPOSTA:
  "Ótima pergunta! Seu treinador escalou agachamento porque:
  
   [TÉCNICO] Agachamento treina saída explosiva 
   (0-5m em < 0.5s) — base do seu jogo como PONTA.
   
   [TÁTICO] Você está fraco em velocidade (-11%).
   Agachamento reforça as pernas que você precisa.
   
   [CONTEXTO] Você faltou o treino de velocidade ontem.
   Seu treinador montou hoje especialmente pra compensar.
   
   [PRÓXIMAS SEMANAS] Agachamento vai aumentando em carga
   conforme corpo fica mais rápido.
   
   Executa bem! 💪"
```

### 3.2 Pergunta #2: "Como faço esse exercício certo?"

```
Atleta: "Eu faço agachamento como? Qual é a técnica?"

IA NÃO responde.
(Ou responde: "Seu treinador vai ensinar no início da sessão!")

POR QUÊ? Porque:
- Feedback em tempo real exige presença
- Risco de lesão se mal executado
- Treinador corrige postura/profundidade/velocidade

IA pode fornecer:
- ✅ Vídeo do catálogo (se existe asset)
- ✅ Referência: "Ele é uma variação do 'polichinelo'"
- ✅ Direcionar: "Seu treinador vai detalhar!"
```

### 3.3 Pergunta #3: "Por que meu colega não treina agachamento?"

```
Atleta 1 (PONTA): "Por que eu treino agachamento?"
Atleta 2 (ARMADOR): "E por que EU NÃO treino agachamento?"

IA PROCESSA:
  Atleta 1 (PONTA):
  ├─ velocity gap = -11%
  └─ forma corporal = explosão (FORÇA)
  
  Atleta 2 (ARMADOR):
  ├─ technical gap = -8% (leitura de jogo)
  └─ forma corporal = decision (TÁTICA)

RESPOSTA ATLETA 1:
  "Agachamento treina explosividade.
   Como PONTA, você precisa SAIR RÁPIDO.
   Seu colega (ARMADOR) precisa DECIDIR RÁPIDO.
   Posições diferentes → exercícios diferentes!"

RESPOSTA ATLETA 2:
  "Seu treino today foca em LEITURA DE JOGO.
   Você está treinando 3x3 (defesa contra pressão).
   Sua estrutura corporal precisa de técnica + cognição,
   não explosividade pura.
   
   Agachamento é pra PONTAS que saem rápido.
   Você treina o que precisa! 📚"
```

---

## Exemplo Completo: História de João (PONTA)

### Dia 1 — Segunda, 17/3 (Falta)

```
CAMADA 1: IA → Treinador
──────────────────────────
João faltou treino de velocidade segunda

Terça (hoje):
IA: "João precisa compensar. Fadiga = 5.8 (verde).
     Sugiro VELOCIDADE PONTA 45min, com esses blocos:"
     [Sprint, Arremesso rápido, Recuperação]

Treinador: 👍 Aprova
```

### Dia 2 — Terça, 18/3 (Compensação Aprovada)

```
CAMADA 2: Treinador → João
─────────────────────────────
João recebe notificação:
"Seu treino para hoje foi preparado! 
 VELOCIDADE COMPENSATÓRIA — 45min"

CAMADA 3: João ↔ IA
──────────────────────
João pergunta no chat:
  "Por quê esses exercícios?"

IA responde:
  "Vi que faltou você segunda em velocidade.
   Hoje seu treinador montou compensação:
   
   1. Sprint (0-10m) — treina saída explosiva
      Para sua posição (PONTA), é crítico!
   
   2. Arremesso rápido — integra velocidade + técnica
      Você está fraco em velocidade (-11%)
   
   3. Recuperação — evita lesão
   
   Foco em QUALIDADE na execução! 💪"

João pergunta:
  "Como eu faço sprint certo?"

IA responde:
  "Seu treinador vai ensinar no início da sessão.
   (Eu posso orientar DEPOIS via vídeo, se quiser)"
```

### Dias 3+ — Próximos Treinos

```
IA continua monitorando:
- Como João respondeu ao treino de compensação?
- Velocidade melhorou?
- Fadiga aumentou (precisa descanso)?

Se melhora: semana que vem IA sugere FORÇA
Se não melhora: mês que vem IA sugere treino de velocidade NOVAMENTE
```

---

## Resumo de Responsabilidades

### IA Sugere (CAMADA 1)
✅ Identifica necessidade (performance_gap, restrições, fadiga)  
✅ Monta sessão sugerida (blocos, duração, objetivo)  
✅ Apresenta ao treinador (com dados + justificativa)  
✅ Registra para auditoria  

### Treinador Aprova (CAMADA 1 → 2)
✅ Valida sugestão  
✅ Aprova / Nega / Edita  
✅ Envia treino pra equipe (PUBLISHED)  
✅ Conduz execução presencial  

### IA Explica (CAMADA 3)
✅ Responde "por que ESTE exercício?"  
✅ Contextualiza com dados pessoais (gap, posição, fadiga)  
✅ Explica técnica/tática/física integrada  
✅ Direciona pra treinador para "COMO" treinar  

### Atleta Executa
✅ Recebe treino aprovado  
✅ Entende POR QUÊ cada exercício  
✅ Faz com orientação presencial do treinador  
✅ Pergunta ao coach sobre confusões  
✅ Confia no processo  

---

## Arquitetura de Dados (3 Camadas)

```
┌─────────────────────────────────────────┐
│ CAMADA 1: IA → TRAINER                  │
├─────────────────────────────────────────┤
│ POST /trainer-suggestions                │
│ {                                       │
│   athlete_id,                           │
│   features: {fatigue, gap, perf...},   │
│   suggested_blocks: {...},              │
│   rationale: string,                    │
│   created_at                            │
│ }                                       │
│                                         │
│ Response: approved | rejected | edited  │
│ Event: training.suggestion.{status}    │
└─────────────────────────────────────────┘
         ↓ (AsyncAPI approval event)
┌─────────────────────────────────────────┐
│ CAMADA 2: TRAINER → ATHLETE             │
├─────────────────────────────────────────┤
│ TrainingSession created + PUBLISHED     │
│ Notification sent to athlete            │
│ Event: training.session.published       │
└─────────────────────────────────────────┘
         ↓ (athlete sees session)
┌─────────────────────────────────────────┐
│ CAMADA 3: IA ↔ ATHLETE                  │
├─────────────────────────────────────────┤
│ POST /hb-pro-coach/message              │
│ {                                       │
│   athlete_id,                           │
│   session_id (published),               │
│   message: "por que agachamento?",      │
│   context: approved_session_data        │
│ }                                       │
│                                         │
│ Response: explanation with features     │
└─────────────────────────────────────────┘
```

---

## Latency SLA

| Camada | operation | Target | Cache |
|--------|-----------|--------|-------|
| 1 (IA→Trainer) | Sugestão gerada | 500ms | Redis (calc + session blocks) |
| 2 (Trainer→Athlete) | Notificação enviada | 100ms | Notifications service |
| 3 (IA↔Athlete) | Explicação | 500ms | Redis (session + features) |

---

## Conclusão

**A lógica correta é:**

1. **IA observa + sugere** (com dados) → Treinador aprova
2. **Treinador prescreve** → Atleta recebe
3. **IA explica** (exercício aprovado) → Atleta executa

**Resultado:**
- ✅ Atleta motivado ("por quê faz sense")
- ✅ Seguro ("treinador aprovou + vai supervisionar")
- ✅ Informado ("ia explica técnica + tática + física")
- ✅ Qualidade ("supervision presencial")

**"Vi que você precisa compensar velocidade.  
Seu treinador aprovou este treino especial.  
Explico cada exercício...  
Você executa com qualidade! 💪"**

← Isso é HB Pro Coach em 3 camadas.
