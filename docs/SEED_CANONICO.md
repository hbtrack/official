<!-- STATUS: NEEDS_REVIEW -->

# SEED CANÔNICO - Mapeamento Completo UUIDs Determinísticos

## 📋 Status da Implementação

**Versão:** 3.1.0-canonical  
**Script:** `Hb Track - Backend/scripts/seed_e2e_canonical.py`  
**Status:** ✅ IMPLEMENTADO + team_memberships  
**Função Geradora:** `deterministic_uuid(namespace, name)` usando `uuid.uuid5(NAMESPACE_DNS, "namespace:name")`  
**Pipeline:** `Hb Track - Backend/reset-hb-track-dev.ps1` (integrado)

---

## 🗺️ Tabela de Mapeamento UUIDs Determinísticos

### 1. Organizations

| Entidade | Namespace | Name | Usado em Testes | Contagem |
|----------|-----------|------|----------------|----------|
| E2E Org | organizations | e2e-hbtrack-test-org | Todos os testes training | 1 |

**Asserções:** `expect(response.organization_id).toBe(CanonicalIds.ORG_E2E)`

### 2. Users (32 total)

| Entidade | Namespace | Name | Role | Usado em Testes |
|----------|-----------|------|------|----------------|
| Dirigente | users | dirigente@e2e.teste | dirigente | training-navigation.spec.ts (TC-A1) |
| Coordenador | users | coordenador@e2e.teste | coordenador | training-templates.spec.ts (TC-B1 a B5) |
| Treinador | users | treinador@e2e.teste | treinador | training-sessions.spec.ts (TC-E1, E2) |
| João Silva | users | joao.silva@e2e.teste | atleta | training-wellness-athlete.spec.ts (TC-21 a TC-26) |
| Maria Santos | users | maria.santos@e2e.teste | atleta | training-gamification.spec.ts (TC-31) |
| Atleta 3-28 | users | atleta{N}@e2e.teste | atleta | training-sessions.spec.ts (attendance) |

**Asserções:** 
- `expect(wellnessPre.athlete_id).toBe(CanonicalIds.USER_ATLETA_JOAO)`
- `expect(badge.athlete_id).toBe(CanonicalIds.USER_ATLETA_MARIA)`

### 3. Teams (16 total - 4 categorias × 2 gêneros × 2 teams)

| Entidade | Namespace | Name | Categoria | Gênero | Usado em Testes |
|----------|-----------|------|-----------|--------|----------------|
| SUB20 Masculino 01 | teams | sub20-m-01 | Sub-20 | Masculino | training-templates.spec.ts |
| SUB20 Feminino 01 | teams | sub20-f-01 | Sub-20 | Feminino | training-analytics.spec.ts |
| SUB17 Masculino 01 | teams | sub17-m-01 | Sub-17 | Masculino | training-planning.spec.ts |
| (13 teams adicionais) | teams | {categoria}-{genero}-{num} | Variado | M/F | Diversos testes |

**Asserções:** `expect(team.category_id).toBe(4)` // Sub-20

### 3.5. Team Memberships (~272 total)

| Tipo | Estratégia de Vinculação | Quantidade | Usado em Testes |
|------|-------------------------|------------|----------------|
| Staff - Coordenador | TODOS os 16 teams | 16 | training-templates.spec.ts, training-sessions.spec.ts |
| Staff - Treinador 1 | 8 teams masculinos | 8 | training-sessions.spec.ts |
| Staff - Treinador 2 | 8 teams femininos | 8 | training-sessions.spec.ts |
| Atletas | 240 athletes → seus teams | 240 | Todos testes training |

**Estrutura:**
- `person_id` → FK para persons (staff ou atleta)
- `team_id` → FK para teams
- `org_membership_id` → FK para org_memberships
- `status` → 'ativo' (todos)
- `start_at` → '2026-01-01'
- UUIDs determinísticos: `deterministic_uuid("team_memberships", f"{person_id}-{team_id}")`

**Asserções:**
- `expect(teamMemberships.filter(tm => tm.team_id === TEAM_SUB20_M).length).toBeGreaterThan(0)`
- `expect(coordenadorMemberships.length).toBe(16)` // Coordenador em todos teams

### 4. Athletes (240 total - 15 por team)

| Entidade | Namespace | Name | Team | Posição | Usado em Testes |
|----------|-----------|------|------|---------|----------------|
| João Silva | athletes | joao-silva | SUB20-M-01 | Ponta Esq | training-wellness-athlete.spec.ts (TC-21 a TC-26) |
| Maria Santos | athletes | maria-santos | SUB20-F-01 | Central | training-gamification.spec.ts (TC-31, TC-33) |
| Pedro Oliveira | athletes | pedro-oliveira | SUB20-M-01 | Ponta Dir | training-wellness-athlete.spec.ts (TC-23) |
| (237 atletas adicionais) | athletes | {nome}-{sobrenome}-{team[:8]}-{i} | Todos | Variado | training-sessions.spec.ts |

**Asserções:** 
- `expect(athlete.main_defensive_position_id).toBe(2)` // Ponta Esquerda
- `expect(badge.athlete_name).toBe("Maria Santos")`

### 5. Templates (4 padrão)

| Entidade | Namespace | Name | Foco Principal | Icon | Usado em Testes |
|----------|-----------|------|----------------|------|----------------|
| Tático Ofensivo | templates | tatico-ofensivo | Attack Positional 45% | target | training-templates.spec.ts (TC-B1, B2, B5) |
| Físico Intensivo | templates | fisico-intensivo | Physical 60% | flame | training-templates.spec.ts (TC-B3) |
| Equilibrado | templates | equilibrado | Uniforme 15% cada | activity | training-templates.spec.ts (TC-B4) |
| Defesa Posicional | templates | defesa-posicional | Defense Positional 50% | shield | training-validation.spec.ts (TC-G1) |

**Asserções:** 
- `expect(template.focus_attack_positional_pct).toBe(45)`
- `expect(template.focus_physical_pct).toBe(60)`

### 6. Training Cycles (2 macro + 4 meso)

| Entidade | Namespace | Name | Type | Período | Usado em Testes |
|----------|-----------|------|------|---------|----------------|
| Preparatório 2026 | cycles | macro-preparatorio-2026 | macro | 2026-01 a 2026-06 | training-planning.spec.ts (TC-F1) |
| Fase 1 | cycles | meso-fase1-2026 | meso | 2026-01 a 2026-02 | training-planning.spec.ts (TC-F1) |

**Asserções:** 
- `expect(macro.objectives).toContain("Preparação")`
- `expect(meso.parent_cycle_id).toBe(CanonicalIds.MACRO_PREPARATORIO)`

### 7. Training Sessions (320 total - 20 por team × 16 teams, simplificado para 3 teams = 60 sessions)

| Entidade | Namespace | Name | Team | Data | Status | Usado em Testes |
|----------|-----------|------|------|------|--------|----------------|
| Session SUB20 20/01 Tático | sessions | {team[:8]}-2026-01-20-tatico | SUB20-M | 2026-01-20 | closed | training-sessions.spec.ts (TC-E1) |
| Session SUB20 22/01 Físico | sessions | {team[:8]}-2026-01-22-fisico | SUB20-M | 2026-01-22 | draft | training-sessions.spec.ts (TC-E2) |
| (318 sessions adicionais) | sessions | {team[:8]}-{date}-{type} | Todos teams | Últimos/próximos 30d | closed/draft | 10 passadas + 10 futuras |

**Asserções:** 
- `expect(attendance.length).toBe(15)` // 15 atletas
- `expect(session.status).toBe("draft")`

### 8. Wellness Data (60 total - 30 pre + 30 post para primeiras 30 sessions closed)

| Entidade | Usado em Testes | Session | Athlete | Valores Padrão |
|----------|----------------|---------|---------|----------------|
| Wellness Pre João | training-wellness-athlete.spec.ts (TC-21) | SESSION_SUB20_2026_01_20_TATICO | ATHLETE_JOAO_SILVA | sleep_hours:7.5, quality:4, fatigue:3 |
| Wellness Post João | training-wellness-athlete.spec.ts (TC-22) | SESSION_SUB20_2026_01_20_TATICO | ATHLETE_JOAO_SILVA | rpe:6, minutes:90, fatigue_after:5 |
| (58 wellness adicionais) | training-wellness-coach.spec.ts (TC-27, TC-28) | 30 sessions | 15 athletes/session | Gera dados rankings |

**Asserções:** 
- `expect(wellnessPre.sleep_hours).toBe(7.5)`
- `expect(wellnessPost.session_rpe).toBe(6)`

### 9. Gamification (Badges & Rankings - placeholders)

| Entidade | Usado em Testes | Athlete | Month | Criteria |
|----------|----------------|---------|-------|----------|
| Badge Maria Jan/2026 | training-gamification.spec.ts (TC-31) | MARIA_SANTOS | 2026-01 | ≥90% response_rate |
| Streak Maria 3 meses | training-gamification.spec.ts (TC-33) | MARIA_SANTOS | 2026-03 | 3 meses ≥90% |
| Team Ranking SUB20-M | training-analytics.spec.ts | TEAM_SUB20_M | 2026-01 | avg_rate DESC |

**Asserções:** 
- `expect(badge.type).toBe("wellness_champion_monthly")`
- `expect(badge.response_rate).toBeGreaterThanOrEqual(90)`

---

## 📊 Resumo de Contagens Esperadas

| Categoria | Contagem | Determinístico | Auto-increment |
|-----------|----------|----------------|----------------|
| Organizations | 1 | ✅ | - |
| Users | 32 | ✅ | - |
| Teams | 16 | ✅ | - |
| Seasons | 16 | ✅ | - |
| Team Memberships | ~272 | ✅ | - |
| Athletes | 240 | ✅ | - |
| Team Registrations | 240 | - | ✅ |
| Templates | 4 | ✅ | - |
| Cycles (Macro) | 2 | ✅ | - |
| Cycles (Meso) | 4 | ✅ | - |
| Training Sessions | 60 (implementado) | ✅ | - |
| Wellness Pre | 30 | - | ✅ |
| Wellness Post | 30 | - | ✅ |
| Badges | ~10 (placeholder) | Parcial | ✅ |
| Team Rankings | ~16 (placeholder) | - | ✅ |
| Notifications | ~50 (placeholder) | Parcial | ✅ |
| **TOTAL** | **~982** | **~622 (63%)** | **~360 (37%)** |

---

## 🧪 Uso nos Testes TypeScript

### Criar arquivo: `tests/e2e/training/helpers/canonical-ids.ts`

```typescript
/**
 * IDs Canônicos Determinísticos - Sincronizado com seed_e2e_canonical.py
 */

import { UUID } from 'crypto';

// Função auxiliar Python para referência
// deterministic_uuid(namespace, name) = uuid.uuid5(NAMESPACE_DNS, f"{namespace}:{name}")

export const CanonicalIds = {
  // Organizations
  ORG_E2E: '88888888-8888-8888-8888-000000000001' as UUID, // Temporário - será substituído por deterministic_uuid
  
  // Users
  USER_DIRIGENTE: 'user-dirigente-uuid' as UUID,
  USER_COORDENADOR: 'user-coordenador-uuid' as UUID,
  USER_TREINADOR: 'user-treinador-uuid' as UUID,
  USER_ATLETA_JOAO: 'user-joao-uuid' as UUID,
  USER_ATLETA_MARIA: 'user-maria-uuid' as UUID,
  
  // Teams
  TEAM_SUB20_M: 'team-sub20-m-uuid' as UUID,
  TEAM_SUB20_F: 'team-sub20-f-uuid' as UUID,
  TEAM_SUB17_M: 'team-sub17-m-uuid' as UUID,
  
  // Athletes
  ATHLETE_JOAO_SILVA: 'athlete-joao-uuid' as UUID,
  ATHLETE_MARIA_SANTOS: 'athlete-maria-uuid' as UUID,
  ATHLETE_PEDRO_OLIVEIRA: 'athlete-pedro-uuid' as UUID,
  
  // Templates
  TEMPLATE_TATICO: 'template-tatico-uuid' as UUID,
  TEMPLATE_FISICO: 'template-fisico-uuid' as UUID,
  TEMPLATE_EQUILIBRADO: 'template-equilibrado-uuid' as UUID,
  TEMPLATE_DEFESA: 'template-defesa-uuid' as UUID,
  
  // Cycles
  MACRO_PREPARATORIO: 'macro-prep-uuid' as UUID,
  MESO_FASE1: 'meso-fase1-uuid' as UUID,
  
  // Sessions (samples)
  SESSION_SUB20_2026_01_20_TATICO: 'session-sub20-01-20-uuid' as UUID,
  SESSION_SUB20_2026_01_22_FISICO: 'session-sub20-01-22-uuid' as UUID,
} as const;

// TODO: Gerar UUIDs reais após executar seed_e2e_canonical.py
// Script Python deve exportar JSON com UUIDs reais para importar aqui
```

---

## 📝 Checklist PASSO 2

- [x] Script seed_e2e_canonical.py criado (730+ linhas)
- [x] Função deterministic_uuid() implementada
- [x] CanonicalIds class com constantes
- [x] 32 users com IDs determinísticos
- [x] 16 teams (4 categorias × 2 gêneros × 2)
- [x] ~272 team_memberships (staff + atletas vinculados)
- [x] 240 athletes (15 por team)
- [x] 4 templates padrão
- [x] 2 macrociclos + 2 mesociclos (simplificado)
- [x] 60 training sessions (3 teams × 20, simplificado)
- [x] 60 wellness records (30 pre + 30 post)
- [x] Tabela de mapeamento em SEED_CANONICO.md
- [x] Pipeline reset-and-start.ps1 atualizado para seed canônico
- [ ] **PRÓXIMO:** Executar seed e validar UUIDs
- [ ] **PRÓXIMO:** Gerar canonical-ids.ts com UUIDs reais
- [ ] **PRÓXIMO:** Atualizar training-CONTRACT.md com cenários TC-21 a TC-50
- [ ] **PRÓXIMO:** Documentar em FECHAMENTO_LOG.md

---

## Plan: Seed E2E Canônico Completo - Implementação Final Consolidada (VERSÃO ORIGINAL)

Criar seed E2E idempotente cobrindo TODAS as tabelas do banco hb_track_dev com commits parciais por fase e rollback isolado: 32 usuários com dados pessoais completos (contatos, CPF válido via algoritmo Luhn sequencial base 111111001, endereços CEP brasileiro, fotos DiceBear), 16 equipes (2 por categoria Infantil/Cadete/Juvenil/Adulto M/F) com comissão técnica, 240 atletas realistas (posições handebol, escolaridade por idade, medidas antropométricas), 320 treinos com wellness/attendance completos (4800 registros wellness_pre/post), 160 jogos com estatísticas realistas (4000+ match_events distribuídos conforme placar final), competições estruturadas com fases/standings calculados, notificações/emails, audit_logs append-only, usando nomes brasileiros reais, campo seed_version para tracking, TEST_FIXTURES constantes para compatibilidade com testes E2E e métricas de performance por fase.

### Steps

1. **Refatorar [seed_e2e.py](c:\HB TRACK\Hb Track - Backend\scripts\seed_e2e.py) com arquitetura modular, constantes TEST_FIXTURES e gerador CPF inline**  
   Criar constantes no topo: `TEST_FIXTURES = {"team_dirigente_uuid": "88888888-8888-8888-8884-000000000001", "team_dirigente_trainings": [{"uuid": "...", "name": "E2E-Treino-Tático", "days_offset": +2, "time": "10:00", "duration": 90, "location": "Campo Principal"}, ...], "team_dirigente_matches": [{"uuid": "...", "days_offset": -4, "status": "finished", "score_home": 3, "score_away": 1, "opponent": "E2E-Adversário-A"}, ...]}`, `SEED_VERSION = "2.0.0"`. Criar classe `E2ESeeder` com métodos: `__init__(conn, seed_version)`, `seed_phase_auxiliary()`, `seed_phase_users()`, `seed_phase_teams()`, `seed_phase_athletes()`, `seed_phase_trainings()`, `seed_phase_matches()`, `seed_phase_competitions()`, `seed_phase_notifications()`, `seed_phase_audit()`, `cleanup_and_validate()`. Cada fase com try/except: `try: execute_phase(); conn.commit(); except Exception as e: logger.error(f"Fase {name} falhou"); conn.rollback(); raise`. Implementar `def gerar_cpf_valido(base: int) -> str` usando algoritmo Luhn: calcular 2 dígitos verificadores, retornar 11 dígitos string. Adicionar listas hardcoded: `NOMES_MASCULINOS`, `NOMES_FEMININOS`, `CIDADES_BRASIL` (25 tuplas cidade/estado/CEP).

2. **Fase 1: Popular tabelas auxiliares, adversários E2E fixos e adicionar seed_version às tabelas core**  
   Executar `seed_phase_auxiliary()` com métricas: `start = time.time()`. Inserir [defensive_positions](c:\HB TRACK\Hb Track - Backend\scripts\seed_v1_2_initial.py) (5 posições IDs 1-5), [offensive_positions](c:\HB TRACK\Hb Track - Backend\scripts\seed_v1_2_initial.py) (6 posições IDs 1-6), [schooling_levels](c:\HB TRACK\Hb Track - Backend\scripts\seed_v1_2_initial.py) (6 níveis IDs 1-6), [phases_of_play](c:\HB TRACK\Hb Track - Backend\scripts\seed_v1_2_initial.py) (4 fases), [advantage_states](c:\HB TRACK\Hb Track - Backend\scripts\seed_v1_2_initial.py) (3 estados), [event_types](c:\HB TRACK\Hb Track - Backend\scripts\seed_v1_2_initial.py)+[event_subtypes](c:\HB TRACK\Hb Track - Backend\scripts\seed_v1_2_initial.py) (11+11 tipos) usando `ON CONFLICT (id) DO NOTHING`. Criar [competition_opponent_teams](c:\HB TRACK\Hb Track - Backend\app\models\competition.py) (23 clubes: E2E-Adversário-A/B/C com UUIDs fixos de TEST_FIXTURES + 20 clubes brasileiros "EC Pinheiros", "Metodista", "Unisul", etc.) via `executemany()`. Adicionar coluna `seed_version VARCHAR(10)` às tabelas: persons, users, teams, athletes, training_sessions, matches (via ALTER TABLE ou migration futura). Logar `print(f"✅ Fase 1: {time.time()-start:.1f}s | {counts}")`. Commit parcial.

3. **Fase 2: Criar 32 usuários (6 fixos + 26 novos) com dados pessoais COMPLETOS via execute_batch()**  
   Executar `seed_phase_users()` com progress bar: `for i in tqdm(range(32), desc="Criando usuários")`. Manter 6 usuários E2E existentes (UUIDs fixos 88888888-8888-8888-8882-00000000X) com `ON CONFLICT (id) DO UPDATE SET seed_version = EXCLUDED.seed_version`. Criar 26 novos usuários com UUIDs sequenciais (uuid.uuid4()). Para cada pessoa: atribuir nome de `NOMES_MASCULINOS` ou `NOMES_FEMININOS` baseado em gênero, gerar CPF via `gerar_cpf_valido(111111001 + i)`, criar [person_contacts](c:\HB TRACK\Hb Track - Backend\app\models\person.py) (telefone formato `119{str(i).zfill(8)}`, email `e2e.{role}.{i}@teste.com`, `contact_type='telefone'/'email'`, `is_primary=true`), [person_documents](c:\HB TRACK\Hb Track - Backend\app\models\person.py) (CPF gerado + RG `MG{random.randint(10000000,99999999)}`, `document_type='cpf'/'rg'`, `is_verified=true`), [person_addresses](c:\HB TRACK\Hb Track - Backend\app\models\person.py) (ciclando `CIDADES_BRASIL[i % 25]`, `address_type='residencial_1'`, `postal_code` sem hífen, `is_primary=true`), [person_media](c:\HB TRACK\Hb Track - Backend\app\models\person.py) (URL DiceBear, `media_type='foto_perfil'`, `is_primary=true`). Usar `psycopg2.extras.execute_batch(cursor, sql, data, page_size=100)`. Logar métricas. Commit parcial.

4. **Fase 3: Criar 16 equipes (1 fixa E2E-Equipe-Dirigente + 15 novas) com comissão técnica de 3 membros e seasons**  
   Executar `seed_phase_teams()`. Criar/atualizar equipe fixa via `ON CONFLICT (id) DO UPDATE` (UUID de TEST_FIXTURES["team_dirigente_uuid"], categoria Infantil ID=2, gênero masculino, nome "E2E-Equipe-Dirigente"). Criar 15 equipes novas: loop sobre `categories = [2,3,4,6]` (Infantil/Cadete/Juvenil/Adulto), `genders = ['masculino', 'feminino']`, `nums = [1,2]`, nome `f"E2E-{category_name}-{gender[0].upper()}-{num:02d}"`. Para cada equipe: criar [season](c:\HB TRACK\Hb Track - Backend\app\models\team.py) (year=2026, name="Temporada 2026", starts_at="2026-01-01", ends_at="2026-12-31", `is_active=true`, `seed_version`), criar 3 [team_memberships](c:\HB TRACK\Hb Track - Backend\app\models\team.py) via loop sobre roles [1,2,3] (dirigente/coordenador/treinador), atribuir person_id ciclando pelos 32 usuários, executar `UPDATE teams SET coach_membership_id = {org_membership_id_treinador} WHERE id = {team_id}`. Logar métricas. Commit parcial.

5. **Fase 4: Gerar 240 atletas (15 por equipe) com posições handebol, escolaridade por idade e team_registrations**  
   Executar `seed_phase_athletes()` com progress bar: `for team in tqdm(teams, desc="Criando atletas")`. Para cada equipe criar 15 atletas: calcular `birth_date = datetime.now() - timedelta(days=365 * (category.max_age - random.randint(0,2)))`. Primeiro atleta é goleira: [athletes](c:\HB TRACK\Hb Track - Backend\app\models\athlete.py) com `athlete_name` de `NOMES_FEMININOS` se team.gender=="feminino" senão `NOMES_MASCULINOS`, `main_defensive_position_id=5` (GOL), `main_offensive_position_id=NULL` (per RD13), `shirt_number=1`, `height=random.randint(170,185)`, `weight=random.randint(65,80)`, `schooling_id` calculado (birth_date < 14 anos → random 1-2, 14-17 → 3-4, 18+ → 5-6), `state='ativa'`, `injured=false`, `seed_version`. Demais 14 atletas: `main_defensive_position_id=random.choice([1,2,3,4])`, `main_offensive_position_id=random.choice([1,2,3,4,5,6])`, `shirt_number` único (2-99). Criar [team_registrations](c:\HB TRACK\Hb Track - Backend\app\models\athlete.py) via `executemany()` com `start_at=season.starts_at`, `role='titular'/'reserva'` (7 titulares, 8 reservas), `seed_version`. Usar `execute_batch(page_size=100)` para 240×5 inserts (athlete + registration + 3 person_data). Logar métricas. Commit parcial.

6. **Fase 5: Popular 320 treinos (3 fixos E2E-Equipe-Dirigente + 317 novos) com attendance e wellness completos**  
   Executar `seed_phase_trainings()`. Para E2E-Equipe-Dirigente criar EXATAMENTE 3 treinos de TEST_FIXTURES usando UUIDs fixos: `session_at = datetime.now() + timedelta(days=fixture["days_offset"]) + time(hour=fixture["time"])`, `session_name = fixture["name"]`, `duration_planned_minutes = fixture["duration"]`, `location = fixture["location"]`, `session_type='quadra'`, `status='planned'`, `seed_version`. Para demais 15 equipes criar 20 treinos cada: 10 passados (`session_at` entre now()-30d e now()-1d, intervalos ~3 dias, `status='closed'`, `closed_at=session_at + duration`, `closed_by_user_id`), 10 futuros (`session_at` entre now()+1d e now()+30d, `status='planned'`). Para CADA treino passado criar [attendance](c:\HB TRACK\Hb Track - Backend\app\models\training.py) para os 15 atletas da equipe via team_registration_id: 80% `presence_status='present'` + `minutes_effective=duration`, 15% `presence_status='absent'` + `reason_absence=random.choice(['medico','escola','opcional'])`, 5% `presence_status='absent'` sem reason. Criar [wellness_pre](c:\HB TRACK\Hb Track - Backend\app\models\wellness.py) para presentes (random `sleep_hours` 6-9, `sleep_quality` 1-5, `fatigue` 0-10, `stress` 0-10, `muscle_soreness` 0-10), [wellness_post](c:\HB TRACK\Hb Track - Backend\app\models\wellness.py) (random `rpe` 5-9, `minutes=duration`, trigger calcula `internal_load`, `fatigue_after` 0-10). Total ~160 treinos passados × 15 atletas × 3 tabelas = ~7200 wellness/attendance inserts via `execute_batch(page_size=100)`. Logar métricas detalhadas. Commit parcial.

7. **Fase 6: Criar 160 jogos (3 fixos + 157 novos) com roster, periods e events distribuídos EXATAMENTE conforme placar**  

   Executar `seed_phase_matches()`. Para E2E-Equipe-Dirigente criar 3 jogos de TEST_FIXTURES (UUIDs fixos): 1 passado finished (days_offset=-4, `final_score_home=3`, `final_score_away=1`, `notes='E2E-Adversário-A'`, `venue='Campo E2E'`, `status='finished'`), 2 futuros scheduled (days_offset=+6/+30, adversários B/C, `status='scheduled'`). Para demais equipes criar 10 jogos cada: 5 passados finished (`match_date` entre now()-30d e now()-1d, intervalos ~7 dias, `start_time` entre 14:00-20:00, `final_score_home=random.randint(18,35)`, `final_score_away=random.randint(15,32)`, `notes={opponent_team.name}`, `phase='friendly'`, `status='finished'`), 5 futuros scheduled. Para CADA jogo finalizado (81 total) criar [match_roster](c:\HB TRACK\Hb Track - Backend\app\models\match.py) (12 atletas convocados, 7 `is_starter=true`), [match_periods](c:\HB TRACK\Hb Track - Backend\app\models\match.py) (2 períodos com `score_home_p1 = int(final_score_home * 0.45)`, `score_away_p1 = int(final_score_away * 0.45)`, período 2 com restante), [match_events](c:\HB TRACK\Hb Track - Backend\app\models\match.py) distribuídos: criar EXATAMENTE `final_score_home` eventos `event_type='goal'` para atletas home (top 4 fazem 60% dos gols, demais 40%), `final_score_away` gols para away, ~`int(final_score_home * 1.7)` eventos `'goalkeeper_save'` para goleira away, 1-2 `'yellow_card'`, 0-1 `'red_card'`, distribuir `minute` 0-60 uniforme, `period='1st'/'2nd'` proporcional a scores. Total ~81 jogos × 50 events avg = 4000+ inserts via `execute_batch(page_size=100)`. Logar métricas. Commit parcial.

8. **Fase 7: Estruturar competições (Copa E2E + Liga E2E) com fases, vinculação jogos, standings e cycles/microcycles**  

   Executar `seed_phase_competitions()`. Criar 2 [competitions](c:\HB TRACK\Hb Track - Backend\app\models\competition.py) ("Copa E2E 2026" `competition_type='grupos_mata_mata'` year=2026, "Liga E2E 2026" `competition_type='turno_unico'`), criar [competition_seasons](c:\HB TRACK\Hb Track - Backend\app\models\competition.py) vinculando às 16 seasons via `executemany()`. Para Copa criar [competition_phases](c:\HB TRACK\Hb Track - Backend\app\models\competition.py): Fase de Grupos (`phase_type='group'`, 2 grupos de 4 equipes cada, `start_date=2026-02-01`, `end_date=2026-03-31`), Semifinal (`phase_type='semifinal'`, `start_date=2026-04-05`), Final (`phase_type='final'`, `start_date=2026-04-12`). Vincular 40 jogos passados (50%) via [competition_matches](c:\HB TRACK\Hb Track - Backend\app\models\competition.py). Calcular [competition_standings](c:\HB TRACK\Hb Track - Backend\app\models\competition.py): loop sobre equipes na fase, contar wins/losses via jogos vinculados, `points = wins * 2`, `goals_for = SUM(final_score)`, `goal_difference = goals_for - goals_against`, inserir standings ordenados. Criar [training_cycles](c:\HB TRACK\Hb Track - Backend\app\models\training.py) (1 por season, duração 120 dias, `start_date=season.starts_at`, `objectives='Preparação física e tática'`) + [training_microcycles](c:\HB TRACK\Hb Track - Backend\app\models\training.py) (4 microciclos de 7 dias, `focus='Ataque posicional'/'Defesa 6-0'/'Transições'/'Finalizações'`), vincular treinos futuros via `UPDATE training_sessions SET microcycle_id = {id} WHERE session_at BETWEEN {micro.start} AND {micro.end}`. Logar métricas. Commit parcial.

9. **Fase 8: Popular medical_cases (24 atletas lesionados), notificações em tempo real, emails queue e audit_logs append-only**  
   Executar `seed_phase_notifications()`. Selecionar 24 atletas (10% de 240) random e criar [medical_cases](c:\HB TRACK\Hb Track - Backend\app\models\medical.py) (status `'ativo'`, `reason=random.choice(['Entorse no joelho', 'Contusão muscular', 'Tendinite ombro', 'Fratura dedo'])`, `started_at` entre now()-15d e now()-1d, `ended_at=NULL`), executar `UPDATE athletes SET injured=true, medical_restriction=true WHERE id IN ({lesionados})`. Criar [notifications](c:\HB TRACK\Hb Track - Backend\app\models\notification.py) via `executemany()`: 16 `type='team_assignment'` para treinadores com `notification_data = json.dumps({"team_id": team.id, "team_name": team.name, "assigned_at": iso_timestamp, "assigned_by": dirigente.user_id})`, 3 `type='coach_removal'` para treinadores removidos historicamente, 15 `type='game'` para próximos jogos futuros, `read_at=NULL` para não lidas. Criar [email_queue](c:\HB TRACK\Hb Track - Backend\app\models\email_queue.py): 5 emails `template_type='invite'` status `'pending'` to_email de org_memberships pendentes, 10 emails `'game_reminder'` status `'sent'` `sent_at` últimos 7 dias, 3 emails `'reset_password'` status `'failed'` `error='SMTP timeout'` `max_attempts=3`. Criar [audit_logs](c:\HB TRACK\Hb Track - Backend\app\models\audit.py) append-only (50 registros distribuídos últimos 30 dias): 16 `entity='team'` `action='create'` para equipes, 24 `entity='athlete'` `action='update'` para lesões com `old_value={"injured": false}`, `new_value={"injured": true}`, 10 `entity='user'` `action='login'`, `actor_id` variando entre 32 usuários. Logar métricas. Commit parcial.

10. **Fase 9: Cleanup stale data, validação de integridade com assertions rigorosas e logging final com estatísticas completas**  

   Executar `cleanup_and_validate()`. Soft delete dados E2E obsoletos: `protected_uuids = [TEST_FIXTURES["team_dirigente_uuid"], *fixture_training_uuids, *fixture_match_uuids, *opponent_abc_uuids]`, executar `UPDATE {table} SET deleted_at=NOW(), deleted_reason='E2E cleanup v{SEED_VERSION} {timestamp}' WHERE (name LIKE 'E2E-%' OR notes LIKE 'E2E-%') AND id NOT IN ({protected_uuids}) AND seed_version != '{SEED_VERSION}'` para tabelas: teams, persons, training_sessions, matches, competition_opponent_teams. Executar `validate_seed_integrity()` com assertions: `assert (SELECT COUNT(*) FROM teams WHERE deleted_at IS NULL AND name LIKE 'E2E-%') == 16`, `assert count_athletes == 240`, `assert count_team_registrations == 240`, `assert count_trainings == 323`, `assert count_matches == 163`, `assert count_attendance >= (160 treinos passados × 15 atletas × 0.75)`, `assert count_wellness_pre >= (160 × 15 × 0.75)`, `assert count_match_events >= (81 jogos × 40 events)`, validar FKs órfãs: `assert (SELECT COUNT(*) FROM team_registrations tr LEFT JOIN athletes a ON tr.athlete_id = a.id WHERE a.id IS NULL) == 0`, repetir para attendance→team_registrations, match_events→athletes, etc. Calcular estatísticas finais por tabela: `stats = {table: count for table, count in counts.items()}`. Logar resultado: `logger.info(f"✅✅✅ Seed E2E v{SEED_VERSION} completo em {total_duration:.1f}s")`, `logger.info(f"Estatísticas: {json.dumps(stats, indent=2)}")`, `logger.info(f"Performance: {sum(counts.values())/total_duration:.0f} inserts/s")`. Commit final.