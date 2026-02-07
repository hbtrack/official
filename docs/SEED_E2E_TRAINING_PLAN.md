<!-- STATUS: NEEDS_REVIEW -->

# 🌱 Plano de Seed E2E - Módulo Training

**Data:** 2026-01-18  
**Status:** ✅ COMPLETO  
**Objetivo:** Criar dados necessários para executar 20 test cases E2E do módulo Training

---

## 📋 Checklist de Implementação

### ✅ PASSO 1: VERIFICAR CONFIGURAÇÃO
- [x] Ler documentação completa (_PLANO_TRAINING.md, TRAINING_LOG.md, FECHAMENTO_TRAINING.md, FECHAMENTO_LOG.md)
- [x] Confirmar código implementado (não deduzir)
- [x] Analisar estrutura atual do banco de dados
- [x] Identificar funcionalidades presentes no sistema

### ✅ PASSO 2: PLANEJAR SEED
- [x] Identificar dados necessários para testes E2E
  - 4 templates padrão (para testes CRUD)
  - 6 sessões de treino (3 passadas + 3 futuras)
  - 2 macrociclos + 2 mesociclos (para testes de planejamento)
  - Dados wellness pré/pós (para testes de integração)
- [x] Verificar dados JÁ disponíveis no banco
  - Org E2E: `88888888-8888-8888-8888-000000000001`
  - Team Dirigente: `88888888-8888-8888-8884-000000000001`
  - 10 atletas equipe coordenador já existem
- [x] Verificar scripts de seed existentes (`seed_e2e.py`)
- [x] Documentar plano de seed (ESTE ARQUIVO)
- [x] APLICAR SEED antes de rodar testes

### ✅ PASSO 3: IMPLEMENTAR SEED

#### 3.1 Templates (session_templates)
**Função:** `seed_e2e_templates()`  
**Localização:** `scripts/seed_e2e.py` linhas 1057-1134  
**Dados criados:**
- ✅ Template 1: "Treino Tático Ofensivo" (45/10/25/5/10/0/5%)
- ✅ Template 2: "Treino Físico" (5/5/5/5/10/10/60%)
- ✅ Template 3: "Treino Equilibrado" (15/15/15/15/10/10/20%)
- ✅ Template 4: "Treino de Defesa" (5/50/5/30/0/5/5%)

**Schema real:**
```sql
session_templates (
  id UUID,
  org_id UUID,  -- ATENÇÃO: não é organization_id
  name VARCHAR,
  description TEXT,
  icon VARCHAR(20),
  focus_attack_positional_pct NUMERIC,
  focus_defense_positional_pct NUMERIC,
  focus_transition_offense_pct NUMERIC,
  focus_transition_defense_pct NUMERIC,
  focus_attack_technical_pct NUMERIC,
  focus_defense_technical_pct NUMERIC,
  focus_physical_pct NUMERIC,
  is_favorite BOOLEAN,
  is_active BOOLEAN,
  created_by_membership_id UUID,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
)
```

#### 3.2 Ciclos de Treinamento (training_cycles)
**Função:** `seed_e2e_training_cycles()`  
**Localização:** `scripts/seed_e2e.py` linhas 1137-1234  
**Dados criados:**
- ✅ Macrociclo 1: "Preparatório" (ativo, 120 dias)
- ✅ Macrociclo 2: "Competitivo" (ativo, 90 dias futuro)
- ✅ Mesociclo 1: "Fase 1" (dentro Preparatório, 4 semanas)
- ✅ Mesociclo 2: "Fase 2" (dentro Preparatório, 4 semanas após Fase 1)

**Schema real:**
```sql
training_cycles (
  id UUID,
  organization_id UUID,
  team_id UUID,
  type VARCHAR,  -- ATENÇÃO: não é cycle_type
  start_date DATE,
  end_date DATE,
  objective TEXT,  -- ATENÇÃO: não há coluna name separada
  notes TEXT,
  status VARCHAR,  -- VALORES: active, completed, cancelled (não planned)
  parent_cycle_id UUID,
  created_by_user_id UUID,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
)
```

#### 3.3 Sessões de Treino (training_sessions)
**Função:** `seed_e2e_training_sessions_dirigente()`  
**Localização:** `scripts/seed_e2e.py` linhas 1237-1349  
**Dados criados:**
- ✅ Sessão 1: -10 dias, status=closed, Tático
- ✅ Sessão 2: -7 dias, status=closed, Físico
- ✅ Sessão 3: -3 dias, status=closed, Equilibrado
- ✅ Sessão 4: hoje, status=draft, Tático
- ✅ Sessão 5: +3 dias, status=draft, Defesa
- ✅ Sessão 6: +7 dias, status=draft, Físico

**Schema real:**
```sql
training_sessions (
  id UUID,
  organization_id UUID,
  team_id UUID,
  session_at TIMESTAMP,
  main_objective TEXT,
  session_type VARCHAR,
  duration_planned_minutes INT,
  status VARCHAR,  -- VALORES: draft, in_progress, closed, readonly (não planned)
  -- NÃO TEM template_id
  focus_attack_positional_pct NUMERIC,
  focus_defense_positional_pct NUMERIC,
  focus_transition_offense_pct NUMERIC,
  focus_transition_defense_pct NUMERIC,
  focus_attack_technical_pct NUMERIC,
  focus_defense_technical_pct NUMERIC,
  focus_physical_pct NUMERIC,
  deviation_justification TEXT,
  created_by_user_id UUID,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
)
```

#### 3.4 Dados Wellness (wellness_pre + wellness_post)
**Função:** `seed_e2e_wellness_data()`  
**Localização:** `scripts/seed_e2e.py` linhas 1352-1476  
**Dados criados:**
- ✅ 3 registros wellness_pre (para sessões passadas)
- ✅ 3 registros wellness_post (para sessões passadas)
- ✅ Usa atleta dinâmico da equipe coordenador (busca via query)

**Schema real wellness_pre:**
```sql
wellness_pre (
  id UUID,
  organization_id UUID,
  training_session_id UUID,
  athlete_id UUID,  -- ATENÇÃO: referencia athletes.id (não person_id)
  sleep_hours NUMERIC,
  sleep_quality SMALLINT,  -- NUMÉRICO 1-5 (não texto 'boa/regular')
  fatigue_pre SMALLINT,
  stress_level SMALLINT,
  muscle_soreness SMALLINT,
  notes TEXT,
  menstrual_cycle_phase VARCHAR,
  readiness_score SMALLINT,
  created_by_user_id UUID,
  filled_at TIMESTAMP,
  created_at TIMESTAMP
)
```

**Schema real wellness_post:**
```sql
wellness_post (
  id UUID,
  organization_id UUID,
  training_session_id UUID,
  athlete_id UUID,  -- ATENÇÃO: athletes.id
  session_rpe SMALLINT,
  fatigue_after SMALLINT,
  mood_after SMALLINT,
  muscle_soreness_after SMALLINT,
  notes TEXT,
  perceived_intensity SMALLINT,  -- NUMÉRICO 1-5 (não 'alta/media/baixa')
  flag_medical_followup BOOLEAN,
  minutes_effective INT,
  created_by_user_id UUID,
  filled_at TIMESTAMP,
  created_at TIMESTAMP
)
```

### ✅ PASSO 4: DOCUMENTAR
- [x] Registrar ações em FECHAMENTO_TRAINING.md (Step 14 marcado como EM PROGRESSO)
- [x] Criar SEED_E2E_TRAINING_PLAN.md (este arquivo)
- [ ] Validar checklist STEP 15 (após rodar testes)

### ⏳ PASSO 5: PIPELINE
- [x] Script reset-and-start.ps1 disponível
- [x] Seed aplicado com sucesso (0 erros)
- [ ] Rodar testes E2E: `npx playwright test tests/e2e/training/training-module.spec.ts --project=chromium --workers=1`
- [ ] Analisar resultados
- [ ] Resolver falhas
- [ ] Atualizar documentação final

---

## 🔧 Correções de Schema Aplicadas

Durante a implementação, foram identificadas e corrigidas as seguintes divergências entre schema esperado e real:

| Tabela | Campo Esperado | Campo Real | Correção |
|--------|---------------|-----------|----------|
| session_templates | organization_id | org_id | ✅ Alterado para org_id |
| training_cycles | cycle_type | type | ✅ Alterado para type |
| training_cycles | name | - | ✅ Removido, texto vai em objective |
| training_cycles | status=planned | status=active/completed/cancelled | ✅ Trocado planned → active |
| training_sessions | status=planned | status=draft/in_progress/closed/readonly | ✅ Trocado planned → draft |
| training_sessions | template_id | - | ✅ Removido (coluna não existe) |
| wellness_pre | sleep_quality TEXT | sleep_quality SMALLINT | ✅ Valores numéricos 1-5 |
| wellness_post | perceived_intensity TEXT | perceived_intensity SMALLINT | ✅ Valores numéricos 1-5 |
| wellness_* | athlete_id (person_id) | athlete_id (athletes.id) | ✅ Busca athletes.id via query |

---

## 📊 Dados Disponíveis Após Seed

```
✅ 4 templates padrão (Tático, Físico, Equilibrado, Defesa)
✅ 2 macrociclos (Preparatório ativo, Competitivo ativo)
✅ 2 mesociclos (Fase 1/2 dentro do Preparatório)
✅ 6 sessões de treino (3 passadas closed + 3 futuras draft)
✅ 6 registros wellness (3 pré + 3 pós para sessões passadas)
```

**Comando para verificar:**
```bash
cd "C:\HB TRACK\Hb Track - Backend"
.\.venv\Scripts\python.exe scripts\seed_e2e.py
```

**Saída esperada:**
```
=> Criando session_templates E2E...
   OK 4 templates E2E criados
=> Criando training_cycles E2E...
   OK 4 cycles E2E criados (2 macros + 2 mesos)
=> Criando training_sessions E2E (equipe dirigente)...
   OK 6 sessions E2E criadas (3 passadas closed + 3 futuras planned)
=> Criando wellness_pre/post E2E...
   OK Wellness data criada (3 pré + 3 pós)
```

---

## 🧪 Cobertura de Testes E2E

Os dados do seed suportam os seguintes testes:

1. **Navegação 8 tabs** - Dados não necessários
2. **CRUD Templates** - ✅ 4 templates padrão criados
3. **Limite 50 templates** - ✅ Pode criar 46 adicionais via API
4. **Preview template** - ✅ Templates têm focos válidos
5. **Modal UX mobile** - ✅ Templates disponíveis para testar
6. **Agenda** - ✅ 6 sessões de treino disponíveis
7. **Calendário** - ✅ Sessões distribuídas no tempo
8. **Planejamento** - ✅ 4 ciclos (2 macro + 2 meso) criados
9. **Analytics** - ✅ Sessões passadas + wellness data
10. **Wellness API** - ✅ 6 registros wellness criados

---

## 🎯 Próximos Passos

1. ⏳ **Executar testes E2E**
   ```bash
   cd "C:\HB TRACK\Hb Track - Fronted"
   npx playwright test tests/e2e/training/training-module.spec.ts --project=chromium --workers=1
   ```

2. ⏳ **Analisar relatório HTML**
   ```bash
   npx playwright show-report
   ```

3. ⏳ **Documentar resultados em FECHAMENTO_LOG.md**
   - Registrar X/20 testes passaram
   - Listar falhas identificadas
   - Documentar correções aplicadas

4. ⏳ **Validar checklist STEP 15 FECHAMENTO_TRAINING.md**
   - Marcar itens concluídos
   - Capturar screenshots de evidências
   - Gerar relatório final

---

**Status:** ✅ Seed implementado e testado com sucesso  
**Próximo:** Executar pipeline de testes E2E  
**Responsável:** Sistema automatizado + validação manual  
**Data conclusão seed:** 2026-01-18 18:04
