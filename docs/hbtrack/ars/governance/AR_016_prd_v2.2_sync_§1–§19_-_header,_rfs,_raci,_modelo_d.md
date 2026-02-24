# AR_016 — PRD v2.2: sync §1–§19 — header, RFs, RACI, modelo dados, stack, gates

**Status**: ⛔ SUPERSEDED — PRD v2.2 sync concluído; validação .ps1 overfit em regra proibitiva — absorvida pelo protocolo atual
**Versão do Protocolo**: 1.0.6

## Descrição
PROBLEMA: PRD v2.1 está desatualizado em 8 pontos críticos. O Executor deve aplicar EXATAMENTE as mudanças descritas abaixo, sem adicionar nem remover conteúdo além do especificado.

---
MUDANÇA 1 — Cabeçalho (linha 1–8):
- Versão: 2.1 → 2.2
- Última atualização: 07 de fevereiro de 2026 → 20 de fevereiro de 2026
- Status: manter '✅ V1.0 em produção | 🚧 V1.1 em desenvolvimento | 🔮 V2.0+ planejado'
- Adicionar linha no Histórico de Versões:
  | 2.2 | 20/02/2026 | Equipe HB Track | Sync: RACI+Preparador Físico, RFs novos (009–014), §8.2 modelo completo (65 tabelas), §11 stack Celery/Redis, §13.3 gate corrigido (.py), §20 Governança IA |

---
MUDANÇA 2 — §4.1 In Scope V1 (Banco de Exercícios):
Substituir a linha:
  '- 🚧 **Banco de Exercícios:** Catálogo de atividades com tags hierárquicas, favoritos, drag-and-drop para sessões (em desenvolvimento)'
Por:
  '- ✅ **Banco de Exercícios:** Catálogo de atividades com tags hierárquicas, favoritos, drag-and-drop para sessões (backend + frontend completos)'
E no grafo de dependências, a linha '5. ~~Banco de Exercícios~~  → ✅ COMPLETO...' já está correta — manter.

---
MUDANÇA 3 — §4.2 In Scope V1.1 (Módulo de Competições):
Após a Matriz de Priorização V1.1, adicionar a seguinte subseção:

**Estado Atual do Domínio Competitions (20/02/2026):**

| Card | Título | Status | Dependência |
|------|--------|--------|-------------|
| COMP-DB-001 | Soft delete (5 tabelas) — migration 0055 | EXECUTING (infra bloqueada) | — |
| COMP-DB-002 | competition_standings.team_id — FK → teams | BACKLOG | COMP-DB-001 |
| COMP-DB-003 | competitions.scoring rules (points_per_draw/loss) | BACKLOG | COMP-DB-002 |
| COMP-DB-004 | Índices únicos + constraints de integridade | BACKLOG | COMP-DB-003 |

---
MUDANÇA 4 — §6: Adicionar RFs novos após RF-008 (sem renumerar os existentes).

Adicionar blocos RF-009 a RF-014 ao final da seção §6 (antes da subseção 6.1):

### **RF-009: Módulo de Competições**

**Descrição:** Gerenciamento de campeonatos, fases, adversários e classificação. Base para scout de partidas.

**Critérios de Aceitação:**
- 🚧 Criação de competições com regras de pontuação configuráveis (points_per_win, points_per_draw, points_per_loss)
- 🚧 Fases de competição (competition_phases) com datas e status
- 🚧 Adversários (competition_opponent_teams) com soft delete
- 🚧 Classificação automática (competition_standings) vinculada a teams.id via FK
- 🚧 Soft delete em todas as 5 tabelas do domínio (deleted_at + deleted_reason + trigger de bloqueio físico)

**Status:** 🚧 Em Desenvolvimento (COMP-DB-001..004 em execução)

---

### **RF-010: Partidas e Scout**

**Descrição:** Registro de partidas com scout de eventos em tempo real (gols, defesas, faltas, assistências, posse de bola).

**Critérios de Aceitação:**
- 🚧 Entidade matches com períodos (match_periods), escalação (match_roster), times (match_teams)
- 🚧 Eventos de scout por jogador, tipo, subtype, minuto, período, fase de jogo
- 🚧 Posse de bola (match_possessions) com vantagem de estado (advantage_states)
- 🚧 Soft delete em match_events e match_roster

**Status:** 🚧 Em Desenvolvimento (depende de RF-009)

---

### **RF-011: Ciclos e Microciclos de Treino**

**Descrição:** Estrutura hierárquica de planejamento de treino: Macrociclo → Ciclo (training_cycles) → Microciclo semanal (training_microcycles) → Sessão.

**Critérios de Aceitação:**
- ✅ training_cycles: período, objetivo, fase (preparatória/competitiva/transição)
- ✅ training_microcycles: semana específica com carga alvo, horas planejadas vs executadas
- ✅ Sessões vinculadas a microciclo via microcycle_id
- ✅ Cache de analytics invalidado automaticamente ao alterar sessão do microciclo (trigger fn_invalidate_analytics_cache)

**Status:** ✅ Implementado (tabelas training_cycles + training_microcycles no schema)

---

### **RF-012: Exportação e Jobs Assíncronos**

**Descrição:** Geração assíncrona de relatórios PDF e outros exports via fila de jobs (Celery + Redis).

**Critérios de Aceitação:**
- 🚧 export_jobs: rastreamento de jobs com status (pending/processing/completed/failed)
- 🚧 export_rate_limits: controle de taxa por usuário
- 🚧 email_queue: fila de e-mails transacionais
- 🚧 idempotency_keys: prevenção de duplo envio/processamento

**Status:** 🚧 Estrutura de BD implementada; lógica de geração em desenvolvimento

---

### **RF-013: Notificações**

**Descrição:** Sistema de notificações push/in-app para alertas de sobrecarga, wellness e eventos do sistema.

**Critérios de Aceitação:**
- ⚠️ Tabela notifications implementada no BD
- ⚠️ Backend de alertas implementado; badge monthly job INATIVO (comentado em celery_app.py)

**Status:** ⚠️ Parcialmente implementado (backend sem frontend ativo)

---

### **RF-014: Perfil Estendido de Pessoa**

**Descrição:** Dados pessoais enriquecidos além do campo básico: endereços, contatos, documentos, mídia, escolaridade.

**Critérios de Aceitação:**
- ✅ person_addresses: endereços com tipo (residencial/comercial)
- ✅ person_contacts: telefones e e-mails secundários
- ✅ person_documents: CPF, RG, passaporte
- ✅ person_media: fotos e mídia pessoal
- ✅ schooling_levels: nível de escolaridade do atleta

**Status:** ✅ Implementado

---
MUDANÇA 5 — §8.2 Modelo de Dados (Entidades Principais):
Substituir a tabela de entidades existente por uma versão expandida que cubra os 3 domínios:

Manter o Diagrama Mermaid (§8.1) existente, MAS adicionar APÓS a tabela de entidades existente os seguintes sub-grupos:

**Domínio COMPETITIONS (V1.1):**
| Entidade | Descrição | Campos Chave |
|----------|-----------|---------------|
| **Competition** | Campeonato/torneio | name, season_id, scoring_rules (JSONB) |
| **CompetitionPhase** | Fase do campeonato | competition_id, name, start_date, end_date, deleted_at |
| **CompetitionOpponentTeam** | Adversário cadastrado | competition_id, name, aliases, deleted_at |
| **CompetitionSeason** | Temporada de competição | competition_id, season_id |
| **CompetitionStanding** | Linha na tabela de classificação | competition_phase_id, team_id (FK→teams), points, wins, draws, losses |
| **Match** | Partida oficial | competition_phase_id, match_date, venue, home_score, away_score |
| **MatchTeam** | Time participante da partida | match_id, team_id ou opponent_id, is_home |
| **MatchPeriod** | Período da partida (1º tempo, 2º tempo, prorrogação) | match_id, period_number, score |
| **MatchRoster** | Escalação da partida | match_id, athlete_id, position, is_starter, deleted_at |
| **MatchEvent** | Evento de scout | match_id, athlete_id, event_type_id, event_subtype_id, minute, period, phase_of_play_id, deleted_at |
| **MatchPossession** | Posse de bola | match_id, team_id, advantage_state_id, duration_ms |

**Domínio TRAINING PLANNING (V1):**
| Entidade | Descrição | Campos Chave |
|----------|-----------|---------------|
| **TrainingCycle** | Ciclo de treinamento (macro) | team_id, season_id, start_date, end_date, phase_type |
| **TrainingMicrocycle** | Semana de treino | cycle_id, week_number, planned_load, effective_load |
| **SessionTemplate** | Template reutilizável de sessão | team_id, name, type, default_exercises |
| **Exercise** | Exercício do banco de exercícios | name, description, tags, category |
| **TrainingSessionExercise** | Exercício vinculado à sessão | session_id, exercise_id, duration, notes |
| **TrainingAlert** | Alerta de sobrecarga/wellness | athlete_id, session_id, alert_type, threshold |
| **TeamWellnessRanking** | Ranking de wellness da equipe | team_id, week, score |
| **AthleteBadge** | Conquistas/gamificação do atleta | athlete_id, badge_type, earned_at |

**Domínio PESSOA ENRIQUECIDA (V1):**
| Entidade | Descrição | Campos Chave |
|----------|-----------|---------------|
| **PersonAddress** | Endereço | person_id, type, street, city, state |
| **PersonContact** | Contato adicional | person_id, type (phone/email), value |
| **PersonDocument** | Documento de identidade | person_id, doc_type (CPF/RG), number, expiry |
| **PersonMedia** | Foto/mídia | person_id, media_type, url |
| **SchoolingLevel** | Lookup: nível de escolaridade | code, name |

---
MUDANÇA 6 — §9 RACI:
Adicionar coluna 'Preparador Físico' na tabela RACI. Hierarquia real: Dirigente → Coordenador → Treinador → Preparador Físico → Atleta.

Substituir o cabeçalho da tabela RACI de:
  '| Funcionalidade | Dirigente | Coordenador | Treinador | Atleta |'
Por:
  '| Funcionalidade | Dirigente | Coordenador | Treinador | Preparador Físico | Atleta |'

Adicionar a coluna 'Preparador Físico' com valores:
- Criar organização: -
- Criar temporada: -
- Criar equipe: -
- Cadastrar coordenador: -
- Cadastrar treinador: -
- Cadastrar atleta: - 
- Definir responsável de equipe: -
- Criar treino: A,R (o Preparador Físico pode criar treinos físicos)
- Marcar presença: A,R
- Preencher wellness pré: -
- Preencher wellness pós: -
- Registrar caso médico: A,R (papel principal do Preparador Físico)
- Ver relatório de equipe: A,R
- Ver próprio histórico: -
- Exportar relatório: R
- Gerenciar permissões: -
- Acessar logs de auditoria: -
- Criar competição: -
- Registrar scout de jogo: C

---
MUDANÇA 7 — §11.1 Backend Stack:
Adicionar 2 linhas na tabela de backend após a linha 'Testing':
  | **Task Queue** | Celery | 5.0+ | Jobs assíncronos (exports PDF, notificações, analytics) |
  | **Message Broker** | Redis | 7.0+ | Backend Celery; cache de sessões |

---
MUDANÇA 8 — §13.3 Gates de Regressão:
Substituir:
  'Gate 1: Invariantes de Banco (models_autogen_gate.ps1)'
Por:
  'Gate 1: Invariantes de Banco (scripts/checks/check_models_sync.py)'

Justificativa: Política de governança proíbe .ps1/.sh — todos os scripts MUST ser Python (.py).

## Critérios de Aceite
1) PRD header reporta Versão 2.2 e data 20/02/2026. 2) §6 contém RF-009 a RF-014 com status correto. 3) §8.2 contém sub-grupo 'Domínio COMPETITIONS' com pelo menos 8 entidades. 4) §9 RACI contém coluna 'Preparador Físico'. 5) §11.1 contém Celery e Redis na tabela de backend. 6) §13.3 não contém '.ps1' — referencia '.py'. 7) §4.1 marca Banco de Exercícios como ✅ (não 🚧). 8) §4.2 contém tabela COMP-DB-001..004.

## Validation Command (Contrato)
```
python -c "import pathlib; prd=pathlib.Path('docs/hbtrack/PRD Hb Track.md').read_text(encoding='utf-8'); checks={'v2.2':'2.2' in prd,'data_20_02':'20/02/2026' in prd or '20 de fevereiro' in prd,'rf009':'RF-009' in prd,'rf014':'RF-014' in prd,'raci_prep':'Preparador F' in prd and 'Preparador F' in prd[prd.find('##'+ ' 9. Matriz RACI'):prd.find('##'+ ' 9. Matriz RACI')+3000] if '9. Matriz RACI' in prd else 'Preparador F' in prd,'celery':'Celery' in prd,'no_ps1':'.ps1' not in prd,'competitions_domain':'Domínio COMPETITIONS' in prd or 'COMPETITIONS' in prd,'banco_exercicios_done':'Banco de Exercícios' in prd and '🚧' not in prd[prd.find('Banco de Exercícios')-5:prd.find('Banco de Exercícios')+5] if 'Banco de Exercícios' in prd else False}; failed=[k for k,v in checks.items() if not v]; [print(f'FAIL: {k}') for k in failed]; exit(len(failed)) if failed else print(f'PASS: PRD v2.2 — {len(checks)} checks OK')"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_016_prd_v22_content_sync.log`

## Rollback Plan (Contrato)
```
git revert HEAD
# OU: git restore "docs/hbtrack/PRD Hb Track.md"
# Verifica rollback: python -c "import pathlib; prd=pathlib.Path('docs/hbtrack/PRD Hb Track.md').read_text(encoding='utf-8'); assert '2.1' in prd and '07 de fevereiro' in prd, 'rollback falhou'; print('PASS rollback: PRD voltou para v2.1')"
```
⚠️ **ATENÇÃO**: Este AR modifica banco. Execute rollback em caso de falha.

## Riscos
- O PRD é um documento longo (1250+ linhas) — o Executor deve localizar cada seção com precisão usando âncoras de texto únicas antes de editar.
- A tabela RACI tem 19 linhas — ao adicionar a coluna Preparador Físico, todos os separadores de pipe devem ser mantidos alinhados.
- §6 tem uma inconsistência de numeração legada (RF-005 aparece como 'Registro de Casos Médicos' mas também referenciado como 'Partidas e Scout' no roadmap) — NÃO renumerar RFs existentes, apenas adicionar 009–014.
- A Mudança 4 (RF-009 a RF-014) deve ser inserida ANTES da subseção '### 6.1 Módulo de Ingestão Inteligente' para manter a estrutura numerada.
- Mudança 5 (§8.2): adicionar os sub-grupos APÓS a tabela existente de entidades (não substituir — expandir).

## Análise de Impacto
_(A ser preenchido pelo Executor)_

---
## Carimbo de Execução
_(Gerado por hb report)_


### Execução em b2e7523
**Status Final**: ✅ SUCESSO
**Comando**: `python -c "import pathlib; prd=pathlib.Path('docs/hbtrack/PRD Hb Track.md').read_text(encoding='utf-8'); checks={'v2.2':'2.2' in prd,'data_20_02':'20/02/2026' in prd or '20 de fevereiro' in prd,'rf009':'RF-009' in prd,'rf014':'RF-014' in prd,'raci_prep':'Preparador F' in prd and 'Preparador F' in prd[prd.find('##'+ ' 9. Matriz RACI'):prd.find('##'+ ' 9. Matriz RACI')+3000] if '9. Matriz RACI' in prd else 'Preparador F' in prd,'celery':'Celery' in prd,'no_ps1':'.ps1' not in prd,'competitions_domain':'Domínio COMPETITIONS' in prd or 'COMPETITIONS' in prd,'banco_exercicios_done':'Banco de Exercícios' in prd and '🚧' not in prd[prd.find('Banco de Exercícios')-5:prd.find('Banco de Exercícios')+5] if 'Banco de Exercícios' in prd else False}; failed=[k for k,v in checks.items() if not v]; [print(f'FAIL: {k}') for k in failed]; exit(len(failed)) if failed else print(f'PASS: PRD v2.2 — {len(checks)} checks OK')"`
**Exit Code**: 0
**Evidence File**: `docs/hbtrack/evidence/AR_016_prd_v22_content_sync.log`
**Python Version**: 3.11.9


### Verificacao Testador em b2e7523
**Status Testador**: 🔴 REJEITADO
**Consistency**: AH_DIVERGENCE
**Triple-Run**: TRIPLE_FAIL (3x)
**Exit Testador**: 1 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_016_b2e7523/result.json`
