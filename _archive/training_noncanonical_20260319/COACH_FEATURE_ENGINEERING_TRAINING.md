---
module: "training"
sport_science_ref: "./SPORT_SCIENCE_RULES_TRAINING.md"
domain_rules_ref: "./DOMAIN_RULES_TRAINING.md"
ui_contract_ref: "./UI_CONTRACT_TRAINING.md"
handball_rules_ref: "../../../_canon/HANDBALL_RULES_DOMAIN.md"
feature_store_arch: "Coach Feature Store (Opção 2 — Internal + ai_ingestion)"
version: "1.0.0"
date_created: "2026-03-17"
type: "coach-feature-engineering"
sources_integrated:
  - "SPORT_SCIENCE_RULES_TRAINING.md (SS-TRAIN-001..007)"
  - "EHF Activities & Learn Handball (categorias etárias, exercícios por posição)"
  - "GLKPR + Vanja Radic (especialização goleiro)"
  - "Hancock.ai (performance metrics)"
  - "Sideline Sports / XPS Network (readiness + wellness monitoring)"
---

# COACH_FEATURE_ENGINEERING_TRAINING.md

**Objetivo:** Documentar como o HB Pro Coach transforma dados históricos (via `ai_ingestion`) em **features** (métricas derivadas) e depois aplica **regras determinísticas** para gerar sugestões de treino especializadas.

**Escopo:** Opção 2 — Coach Interno (Feature Store), não LLM externo.

---

## Parte 1: Feature Engineering (Inputs → Métricas Derivadas)

### 1.1 Feature: `fatigue_score` (0-10)

**Fonte científica:** SS-TRAIN-001 (sRPE), SS-TRAIN-002 (RPE CR-10), SS-TRAIN-005 (Qualidade de sono), SS-TRAIN-006 (Horas de sono)

**Inputs (consultados via `ai_ingestion`):**
- `sleep_quality` [1–5] (Likert, pré-treino)
- `sleep_hours` [0–24] (pré-treino, últimas 24h)
- `resting_hr` (bpm, pré-treino)
- `internal_load` últimos 3 treinos (sRPE = min × RPE)
- `days_since_last_rest` (dias desde repouso completo)

**Cálculo:**
```
fatigue_score = 0
IF sleep_quality < 3 AND sleep_hours < 6:
    fatigue_score += 3.0  # Sono ruim = muita fadiga
ELSE IF sleep_quality >= 4 AND sleep_hours >= 8:
    fatigue_score -= 1.5   # Sono excelente = recuperação

IF resting_hr > 70:
    fatigue_score += 2.0   # HR elevada = fadiga cardiovascular
ELSE IF resting_hr <= 60:
    fatigue_score -= 1.0   # HR normal/baixa = boa recuperação

IF internal_load (últimos 3 treinos) > threshold_semanal × 1.2:
    fatigue_score += 2.5   # Carga acumulada elevada = risco de sobrecarga

IF days_since_last_rest >= 7:
    fatigue_score += 1.0   # Sem descanso prolongado = acumulação

fatigue_score = MAX(0, MIN(10, fatigue_score))  # Clamp [0, 10]
```

**Aplicação:**
- `fatigue_score >= 7` → Recomenda recuperação, mobilidade, técnica leve
- `fatigue_score [5-7)` → Treino moderado (força sem sobrecarga)
- `fatigue_score < 5` → Treino intenso permitido (força, velocidade)

---

### 1.2 Feature: `performance_gap` (0-100, percentual de progresso)

**Fonte científica:** Handball.ai (performance metrics), XPS Network (readiness monitoring)

**Inputs (consultados via `ai_ingestion`):**
- Últimas 5 sessões: `focus_technical`, `focus_velocity`, `focus_strength`, `focus_tactical`
- Histórico de feedback do treinador (se existe)
- Sinais de desempenho de `analytics` módulo (se integrado)

**Cálculo por dimensão:**
```
FOR each dimension IN [velocity, technical, strength, tactical]:
    recent_avg = mean(dimension FROM last_5_sessions)
    
    IF recent_avg < team_baseline[position][dimension]:
        gap = ((team_baseline - recent_avg) / team_baseline) × 100
    ELSE:
        gap = 0  # Não há gap se está acima da baseline
    
performance_gap[dimension] = gap
```

**Aplicação (exemplo para Ponta):**
- Se `performance_gap.velocity > 20%` → Recomenda treino de velocidade (prioridade 1)
- Se `performance_gap.technical > 15%` → Recomenda técnica (prioridade 2)
- Se `performance_gap.strength > 10%` → Recomenda força (prioridade 3)

---

### 1.3 Feature: `injury_status` (active_restrictions array)

**Fonte científica:** SPORT_SCIENCE_RULES_TRAINING.md (integração com `medical` módulo)

**Inputs (consultados via `ai_ingestion`):**
- `medical.medicalRestriction` (estado ativo)
- `medical.returnToPlayGuard` (restrições de retorno)

**Estrutura:**
```json
{
  "active_restrictions": ["return_to_play_19days", "full_contact_cleared"],
  "severity": "partial_restriction",
  "adapt_focus": ["mobilidade", "técnica_sem_impacto"],
  "risky_focus": ["força_explosiva", "velocidade_máxima"]
}
```

**Aplicação:**
- Se `return_to_play_guard` ativo → Coach reduz intensidade, recomenda recuperação
- Se `no_contact_restriction` → Treino técnico e mobilidade apenas

---

### 1.4 Feature: `recommended_focus` (output de regra determinística)

**Fonte:** Combinação de todas as features acima + posição + categoria etária

**Exemplo de regra combinada (Ponta + U18):**
```
IF fatigue_score >= 7:
    focus = "recuperação, mobilidade"
ELSE IF fatigue_score < 5 AND performance_gap.velocity > 20%:
    focus = "velocidade, explosividade"
ELSE IF fatigue_score < 5 AND performance_gap.technical > 15%:
    focus = "técnica, arremesso"
ELSE IF days_since_training > 2:
    focus = "força, resistência anaeróbica"
ELSE:
    focus = "manutenção, técnica"
```

---

## Parte 2: Posições & Especialização

### 2.1 Ponta (Ala)

**Características Sport Science** (basado em EHF + Learn Handball):
- Foco primário: **Velocidade** (sprints, transição)
- Foco secundário: **Força de tiro** (arremesso de longe)
- Foco terciário: **Agilidade** (mudança de direção rápida)

**Regra de fadiga para Ponta:**
```
IF fatigue_score >= 7:
    THEN focus = ["mobilidade_inferior", "técnica_leve"]
    REASON = "Ponta precisa de velocidade; fadiga elimina explosividade"

IF fatigue_score < 5 AND performance_gap.velocity > 15%:
    THEN focus = ["aceleração", "velocidade_máxima"]
    REASON = "Treino de velocidade é 70% da progressão de Ponta"
```

**Treinos compensatórios por defasagem:**
- `velocity_gap > 20%` → "SPRINT TRAINING — Velocidade máxima + explosividade"
- `technical_gap > 15%` → "TECHNIQUE SESSION — Arremesso de distância"
- `strength_gap > 10%` → "UPPER BODY — Força de tiro"

---

### 2.2 Armador (Centro)

**Características Sport Science:**
- Foco primário: **Técnica de passe** (distribuição)
- Foco secundário: **Visão tática** (leitura do jogo)
- Foco terciário: **Força de tiro** (arremesso de distância)

**Regra de fadiga para Armador:**
```
IF fatigue_score >= 7:
    THEN focus = ["técnica_estática", "tomada_de_decisão"]
    REASON = "Armador depende de cognição; cansaço degrada passes"

IF fatigue_score < 5 AND performance_gap.technical > 20%:
    THEN focus = ["passe_preciso", "distribuição", "movimento_com_bola"]
    REASON = "Técnica é 60% da progressão do Armador"
```

**Treinos compensatórios:**
- `technical_gap > 20%` → "PASS ACCURACY — Passe preciso em diferentes ângulos"
- `tactical_gap > 15%` → "GAME READING — Táticas e transições"
- `strength_gap > 12%` → "THROWING POWER — Força de tiro"

---

### 2.3 Goleiro (GK / Golaço)

**Características Sport Science** (baseado em GLKPR + Vanja Radic):
- Foco primário: **Reação** (reflexo, antecipação)
- Foco secundário: **Posicionamento** (ângulos de tiro)
- Foco terciário: **Força de tiro** (distribuição para contra-ataque)

**Regra de fadiga para Goleiro:**
```
IF fatigue_score >= 7:
    THEN focus = ["técnica_salvamento_estática", "leitura_ofensiva"]
    REASON = "Goleiro em fadiga perde reflexo; focar em técnica e antecipação"

IF fatigue_score < 5 AND performance_gap.technical > 15%:
    THEN focus = ["técnica_salvamento", "saídas_altas", "distribuição"]
    REASON = "Goleiro precisa de reflexo-treino 3x/semana mínimo"
```

**Treinos compensatórios:**
- `technical_gap > 15%` → "GOALKEEPING TECHNIQUE — Saves, footwork, positioning (per Vanja Radic)"
- `reaction_gap > 20%` → "REACTION DRILLS — High shots, quick reactions"
- `strength_gap > 10%` → "THROWING POWER — Distribution to fast breaks"

---

### 2.4 Recetor Lateral (Ala)

**Características Sport Science:**
- Foco primário: **Força & Resistência** (potência de tiro, duração)
- Foco secundário: **Mobilidade** (flexibilidade, movimento ofensivo)
- Foco terciário: **Tática defensiva** (posicionamento)

**Regra de fadiga para Ala:**
```
IF fatigue_score >= 7:
    THEN focus = ["mobilidade", "técnica_sem_intensidade"]
    REASON = "Ala precisa de força; fadiga mata produtividade"

IF fatigue_score < 5 AND performance_gap.strength > 18%:
    THEN focus = ["força_explosiva", "resistência_anaeróbica"]
    REASON = "Ala tem saques de 10-15 tiros; resistência é crítica"
```

---

## Parte 3: Categorias Etárias & Adaptação Linguística

**Fonte:** Learn Handball + EHF Activities (adaptação por idade)

### 3.1 U10-U12 (Mini Handebol)

**Características Psicológicas (EHF):**
- Linguagem **simples**, sem jargão técnico
- Incentivos **lúdicos** ("Você é rápido como um flash!")
- Foco em **diversão** e **aderência**

**Adaptação de Feature Engineering:**
- `fatigue_score` segue mesma lógica, mas **threshold reduzido** (fadiga percebida em U10 é > 6, não > 7)
- `recommended_focus` simplificado: apenas 2-3 opções (não 8+)
- Mensagens: "**Seu braço está forçando demais. Deixe descansar!**" (não: "sRPE está alta")

**Exemplo de resposta do Coach (U12):**
```
Coach: "Vejo que você está cansado. Que tal fazer um treino leve de passes hoje?
Você vai relaxar e ficar pronto para amanhã! 💪"
```

---

### 3.2 U14-U16 (Cadetes)

**Características Psicológicas:**
- Linguagem **técnica emergente** (posso introduzir "fadiga", "explosividade")
- Incentivos **baseados em progresso** ("Sua velocidade vai melhorar 15%!")
- Foco em **periodização** (ciclos de treino)

**Adaptação:**
- `fatigue_score >= 7` e `performance_gap.velocity > 15%` → Sugerir "SPRINT TRAINING"
- Explicação técnica pode ser mais profunda

**Exemplo:**
```
Coach: "Vi que você ficou mais rápido nos últimos 3 treinos! 
Vamos focar em força agora para manter essa velocidade mesmo cansado. 
Pronto?"
```

---

### 3.3 U18+ (Juniores/Adultos)

**Características Psicológicas:**
- Linguagem **técnica completa** (sRPE, features, análise)
- Incentivos **baseados em dados** ("Seu resting HR subiu 8%, você precisa recuperar")
- Foco em **performance máxima** e **preventing injury**

**Adaptação:**
- Feature names explícitos: "Seu `fatigue_score = 7.8`, recomendo recuperação"
- Explicação científica: "Seu sono foi ruim; recomendo técnica estática hoje"

**Exemplo:**
```
Coach: "Seu `fatigue_score` está em 7.8 (sono ruim + carga acumulada). 
Recomendo TÉCNICA + MOBILIDADE — sem explosividade hoje. 
Seu corpo agradece, e você volta 100% amanhã."
```

---

## Parte 4: Integração com `ai_ingestion`

### 4.1 Dados Consultados pelo Coach (Feature Store)

O Coach consulta Feature Store **a cada mensagem** para:
1. Calcular `fatigue_score` em tempo real
2. Calcular `performance_gap` da última semana
3. Verificar `injury_status` atual
4. Determinar `recommended_focus`

**Latência esperada:** < 500ms (Redis cache ou PostgreSQL computed field)

### 4.2 Auditoria & Rastreamento

Cada sugestão de treino é registrada em `ai_ingestion`:
```json
{
  "suggestion_id": "uuid",
  "athlete_id": "uuid",
  "suggested_at": "2026-03-17T14:30:00Z",
  "features_used": {
    "fatigue_score": 7.8,
    "performance_gap_velocity": 18,
    "performance_gap_technical": 5,
    "injury_status": "no_restrictions"
  },
  "recommended_focus": "técnica, mobilidade",
  "trainer_decision": "approved|rejected",
  "trainer_reason": "...",
  "success_outcome": "athlete_completed|athlete_skipped"
}
```

**Uso:** Medir aderência + refinar regras à medida que dados acumulam.

---

## Parte 5: Decisão Heurística — Coach Response

### 5.1 Template de Resposta (Versão Base)

```
Coach: "[Contextualização com Feature Store] 
Recomendo: [TIPO_TREINO] — [MOTIVO científico]
[Incentivo genuíno baseado em dados do atleta]"
```

**Exemplo (Ponta, U18, fatiga_score=6.5, performance_gap.velocity=18%):**
```
Coach: "Vi que você dormiu bem mas a carga da semana está pesada. 
Seu `fatigue_score` é 6.5 — você está no limite. 
Vou sugerir: SPRINT TRAINING (30min) — foco em velocidade máxima 
+ mobilidade posterior para recuperar.
Você progrediu 18% em velocidade essa semana! Vamos manter isso."
```

### 5.2 Rejeição de Off-Topic

Se atleta pergunta: "Qual é seu time de futebol?"
```
Coach: "Sou seu treinador de handebol! 
Posso ajudar com técnica, treino, wellness ou feedback. O que quer?  😊"
```

### 5.3 Feature Store Indisponível (Fallback)

Se `ai_ingestion` não responder em 500ms:
```
Coach: "Desculpa, não consegui acessar seus dados agora. Tente novamente!"
```

---

## Parte 6: Open Questions & Calibration (Futures)

1. **Quantos dias de histórico usar?**
   - Proposta: últimos 30 dias (suficiente para padrões; não tão velho que é irrelevante)
   - Review quando dados acumularem 1 temporada completa

2. **Como ajustar thresholds por nível?**
   - U10: `fatigue_score_threshold = 6`
   - U14: `fatigue_score_threshold = 6.5`
   - U18+: `fatigue_score_threshold = 7`
   - Data: Learn Handball + EHF categorias

3. **Performance_gap — qual baseline usar?**
   - `team_baseline[position][dimension]` (competindo no seu time atual)
   - Ou `regional_baseline` (comparar com região)?
   - Decisão: Por enquanto usar team_baseline (mais controlado)

4. **Regras por posição — completar para outras posições?**
   - Hoje: Ponta, Armador, Goleiro, Ala
   - Faltam: Pivo (centro defensivo), Lateral (se diferente de Ala)
   - Timeline: Depois de v1.1 com dados reais

---

## Referências

- `SPORT_SCIENCE_RULES_TRAINING.md` (SS-TRAIN-001..007)
- `DOMAIN_RULES_TRAINING.md` (DR-TRAIN-COACH-01..09)
- `UI_CONTRACT_TRAINING.md` v1.2.0 (UIF-TRAINING-006, D-UI-20/21)
- EHF Activities (categories, exercises per position)
- Learn Handball (age-group adaptation)
- GLKPR + Vanja Radic (goalkeeper specialization)
- Sideline Sports / XPS Network (readiness monitoring)
- Handball.ai (performance analytics)

---

**Versão:** 1.0.0  
**Data:** 2026-03-17  
**Status:** ✅ Pronto para Review & Sign-off (antes de implementação de Feature Store)
