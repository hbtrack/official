<!-- STATUS: NEEDS_REVIEW -->

Plano: Atualização do Contrato Real e Testes E2E do Módulo Training
Objetivo
Analisar o módulo training e atualizar:

O contrato real em Hb Track - Fronted\tests\e2e\training\training-CONTRACT.md (arquivo novo)
Os testes e2e em Hb Track - Fronted\tests\e2e\training\training-e2e.test.ts (arquivo novo)
Contexto Descoberto
Estrutura Atual
Contrato existente: docs\modules\training-CONTRACT.md (697 linhas, bem documentado)
Testes existentes: tests\e2e\teams\teams.trainings.spec.ts (testa via aba /teams/[teamId]/trainings)
Diretório alvo: tests\e2e\training\ (existe mas está vazio)
Arquivos Analisados
Arquivo	Conteúdo
src/app/(admin)/training/layout.tsx	Server Component, valida sessão
src/app/(admin)/training/page.tsx	Redirect → /training/agenda
middleware.ts	Proteção via cookie hb_access_token
src/lib/api/trainings.ts	720 linhas, API completa
app/models/training_session.py	SQLAlchemy model (backend)
app/models/training_cycle.py	SQLAlchemy model (backend)
system_rules.md	Regras R17-R40 aplicáveis
Implementação
Etapa 1: Criar training-CONTRACT.md
Arquivo: c:\HB TRACK\Hb Track - Fronted\tests\e2e\training\training-CONTRACT.md

Baseado na análise do código, o contrato incluirá:

Rotas e Navegação
Rota principal: /training (redirect para /training/agenda)
Subrotas:
/training/agenda - Agenda semanal (API REAL)
/training/calendario - Calendário mensal (API REAL)
/training/planejamento - Ciclos e microciclos (API REAL)
/training/banco - Banco de exercícios (MOCK DATA)
/training/avaliacoes - Métricas (MOCK DATA)
Redirects: /training → /training/agenda
404: Rotas inexistentes dentro de /training/*
Autenticação e Autorização
Middleware: Cookie hb_access_token obrigatório
Roles permitidos: Todos autenticados (sem restrição por role no módulo)
Sem auth: Redirect → /signin?callbackUrl=...
Role errado: N/A (não há restrição de role)
Server Components e Data Fetching
layout.tsx - Server Component (getSession)
page.tsx (todas subrotas) - Server Components que validam sessão
APIs via trainingsService (client-side fetch)
Cache: no-store (client-side)
Client Components e Interações
Formulários: CreateSessionModal (criação de sessão)
Ações: CRUD de sessões, ciclos, microciclos
Estados: loading via hooks, error handling
Feedback: Refetch após mutações
Fluxos CRUD
Entidade	CREATE	READ	UPDATE	DELETE
Sessions	POST /training-sessions	GET /training-sessions	PATCH /training-sessions/:id	DELETE /training-sessions/:id
Cycles	POST /training-cycles	GET /training-cycles	PATCH /training-cycles/:id	DELETE /training-cycles/:id
Microcycles	POST /training-microcycles	GET /training-microcycles	PATCH /training-microcycles/:id	DELETE /training-microcycles/:id
Regras de Negócio
Soma de focos ≤ 120%
Status: draft → in_progress → closed → readonly
Reabertura: até 24h após fechamento
Edição pelo autor: 10 minutos
Edição por superior: até 24h
Dependências
teams (via TrainingContext)
auth (via getSession)
seasons (opcional)
Edge Cases
/training/banco e /training/avaliacoes usam MOCK DATA
Endpoints de exercícios e analytics não existem
Etapa 2: Criar training-e2e.test.ts
Arquivo: c:\HB TRACK\Hb Track - Fronted\tests\e2e\training\training-e2e.test.ts

Seções planejadas:

A. Navegação e Rotas
test: /training redireciona para /training/agenda
test: Todas subrotas carregam sem erro (agenda, calendario, planejamento, banco, avaliacoes)
test: Rota inexistente retorna 404
B. Autenticação
test: Acesso sem auth redireciona para /signin
test: Callback URL preservada no redirect
C. Agenda (API Real)
test: Lista sessões da equipe selecionada
test: Navegação entre semanas funciona
test: Criar sessão via modal
test: Sessão criada aparece na lista
D. Calendário (API Real)
test: Visualização mensal carrega
test: Navegação entre meses
test: Click em dia abre detalhes/modal
E. Planejamento (API Real)
test: Lista ciclos (macro e meso)
test: Lista microciclos dentro de ciclo
test: Criar ciclo via API aparece na lista
F. Banco de Exercícios (Mock)
test: Página carrega com dados mock
test: Filtro por categoria funciona
G. Avaliações (Mock)
test: Página carrega com métricas mock
test: Dashboard exibe números
H. CRUD de Sessões via API
test: Criar sessão via API
test: Buscar sessão por ID
test: Atualizar sessão
test: Deletar sessão (soft delete)
test: Fechar sessão (POST /close)
test: Reabrir sessão (POST /reopen) - se dentro de 24h
I. Validações
test: Soma de focos > 120% impede fechamento
test: Sessão sem focos não pode ser fechada
Arquivos a Criar/Modificar
Arquivo	Ação
tests/e2e/training/training-CONTRACT.md	CRIAR (~150 linhas) - Versão resumida para testes
tests/e2e/training/training-e2e.test.ts	CRIAR (~400 linhas)
docs/modules/training-CONTRACT.md	ATUALIZAR - Versão completa (já existe, 697 linhas)
Verificação
Executar testes: npx playwright test tests/e2e/training/training-e2e.test.ts --project=chromium
Verificar que contrato reflete código real (não inventar funcionalidades)
Marcar explicitamente o que é MOCK vs API REAL
Observações Importantes
NÃO INVENTAR: O contrato existente em docs/modules/training-CONTRACT.md é preciso e bem documentado
MOCK DATA: /training/banco e /training/avaliacoes não têm backend implementado
Endpoints reais: cycles, microcycles, sessions funcionam via backend Python/FastAPI
Sem Prisma: O backend usa SQLAlchemy, não Prisma
Helpers Necessários
Reutilizar helpers de tests/e2e/helpers/api.ts:

createSessionViaAPI
deleteSessionViaAPI
getSessionViaAPI
Criar novos se necessário:

createCycleViaAPI
createMicrocycleViaAPI

Plano: Atualização do Contrato Real e Testes E2E do Módulo Training
Objetivo
Analisar o módulo training e atualizar:

tests/e2e/training/training-CONTRACT.md - Versão resumida para testes (CRIAR)
tests/e2e/training/training-e2e.test.ts - Testes E2E (CRIAR)
docs/modules/training-CONTRACT.md - Versão completa (ATUALIZAR)
ANÁLISE COMPLETA REALIZADA
1. ROTAS DO MÓDULO TRAINING
Rota	Arquivo	Status	Descrição
/training	page.tsx	Redirect	→ /training/agenda
/training/agenda	AgendaClient.tsx	API REAL	Agenda semanal
/training/calendario	CalendarioClient.tsx	API REAL	Calendário mensal
/training/planejamento	PlanejamentoClient.tsx	API REAL	Ciclos/microciclos
/training/banco	BancoClient.tsx	MOCK	Banco de exercícios
/training/avaliacoes	AvaliacoesClient.tsx	MOCK	Métricas/relatórios
/training/presencas	page.tsx	TODO	Presenças (placeholder)
/teams/[teamId]/trainings	TrainingsTab.tsx	API REAL	Aba treinos da equipe
2. TABELAS DO BANCO DE DADOS
2.1 training_sessions (Principal)
Coluna	Tipo	Descrição
id	UUID	PK
organization_id	UUID	FK → organizations
team_id	UUID	FK → teams (opcional)
season_id	UUID	FK → seasons (opcional)
microcycle_id	UUID	FK → training_microcycles (opcional)
created_by_user_id	UUID	FK → users
closed_by_user_id	UUID	FK → users (opcional)
session_at	TIMESTAMP(TZ)	Data/hora do treino
session_type	VARCHAR	'quadra', 'fisico', 'video', 'reuniao', 'teste'
main_objective	TEXT	Objetivo principal
secondary_objective	TEXT	Objetivo secundário
notes	TEXT	Notas
planned_load	SMALLINT	Carga planejada (0-10)
group_climate	SMALLINT	Clima do grupo (1-5)
intensity_target	SMALLINT	Intensidade alvo (1-5)
duration_planned_minutes	SMALLINT	Duração planejada
location	VARCHAR	Local
session_block	VARCHAR	Bloco (base_fisica, pre_competitivo, etc.)
status	VARCHAR	'draft', 'in_progress', 'closed', 'readonly'
closed_at	TIMESTAMP(TZ)	Data de fechamento
planning_deviation_flag	BOOLEAN	Flag de desvio (≥20pts ou ≥30%)
deviation_justification	TEXT	Justificativa do desvio
7 Focos de Treino (%):		
focus_attack_positional_pct	NUMERIC(5,2)	Ataque posicionado
focus_defense_positional_pct	NUMERIC(5,2)	Defesa posicionada
focus_transition_offense_pct	NUMERIC(5,2)	Transição ofensiva
focus_transition_defense_pct	NUMERIC(5,2)	Transição defensiva
focus_attack_technical_pct	NUMERIC(5,2)	Técnico ataque
focus_defense_technical_pct	NUMERIC(5,2)	Técnico defesa
focus_physical_pct	NUMERIC(5,2)	Físico
deleted_at	TIMESTAMP(TZ)	Soft delete
deleted_reason	TEXT	Razão do delete
created_at, updated_at	TIMESTAMP(TZ)	Auditoria
2.2 training_cycles (Macrociclos/Mesociclos)
Coluna	Tipo	Descrição
id	UUID	PK
organization_id	UUID	FK → organizations
team_id	UUID	FK → teams
type	VARCHAR	'macro' ou 'meso'
start_date	DATE	Início
end_date	DATE	Fim
objective	TEXT	Objetivo estratégico
notes	TEXT	Notas
status	VARCHAR	'active', 'completed', 'cancelled'
parent_cycle_id	UUID	FK → training_cycles (para mesociclos)
created_by_user_id	UUID	FK → users
Soft delete + timestamps		
2.3 training_microcycles (Planejamento Semanal)
Coluna	Tipo	Descrição
id	UUID	PK
organization_id	UUID	FK → organizations
team_id	UUID	FK → teams
cycle_id	UUID	FK → training_cycles (opcional)
week_start	DATE	Segunda-feira
week_end	DATE	Domingo
microcycle_type	VARCHAR	carga_alta, recuperacao, pre_jogo, etc.
planned_weekly_load	INTEGER	Carga semanal planejada
notes	TEXT	Notas
7 Focos Planejados (%):		
planned_focus_attack_positional_pct	NUMERIC(5,2)	
planned_focus_defense_positional_pct	NUMERIC(5,2)	
planned_focus_transition_offense_pct	NUMERIC(5,2)	
planned_focus_transition_defense_pct	NUMERIC(5,2)	
planned_focus_attack_technical_pct	NUMERIC(5,2)	
planned_focus_defense_technical_pct	NUMERIC(5,2)	
planned_focus_physical_pct	NUMERIC(5,2)	
Soft delete + timestamps		
2.4 attendance (Presenças)
Coluna	Tipo	Descrição
id	UUID	PK
training_session_id	UUID	FK → training_sessions
athlete_id	UUID	FK → athletes
team_registration_id	UUID	FK → team_registrations
presence_status	VARCHAR	'present', 'absent'
minutes_effective	SMALLINT	Minutos efetivos
participation_type	VARCHAR	'full', 'partial', 'adapted', 'did_not_train'
reason_absence	VARCHAR	'medico', 'escola', 'familiar', 'opcional', 'outro'
is_medical_restriction	BOOLEAN	Restrição médica
comment	TEXT	Comentário
source	VARCHAR	'manual', 'import', 'correction'
Soft delete + timestamps		
UNIQUE: training_session_id + athlete_id

2.5 wellness_pre (Bem-estar Pré-Treino)
Coluna	Tipo	Descrição
id	UUID	PK
organization_id	UUID	FK
training_session_id	UUID	FK → training_sessions
athlete_id	UUID	FK → athletes
sleep_hours	NUMERIC(4,1)	Horas de sono (0-24)
sleep_quality	SMALLINT	Qualidade do sono (1-5)
fatigue_pre	SMALLINT	Fadiga pré (0-10)
stress_level	SMALLINT	Nível de stress (0-10)
muscle_soreness	SMALLINT	Dor muscular (0-10)
menstrual_cycle_phase	VARCHAR	'folicular', 'lutea', 'menstruacao', 'nao_informa'
readiness_score	SMALLINT	Score de prontidão (0-10)
notes	TEXT	Notas
filled_at	TIMESTAMP(TZ)	Quando preenchido
Soft delete + timestamps		
UNIQUE: training_session_id + athlete_id

2.6 wellness_post (Bem-estar Pós-Treino)
Coluna	Tipo	Descrição
id	UUID	PK
organization_id	UUID	FK
training_session_id	UUID	FK → training_sessions
athlete_id	UUID	FK → athletes
session_rpe	SMALLINT	PSE geral (0-10)
fatigue_after	SMALLINT	Fadiga pós (0-10)
mood_after	SMALLINT	Humor pós (0-10)
muscle_soreness_after	SMALLINT	Dor muscular (0-10)
perceived_intensity	SMALLINT	Intensidade percebida (1-5)
notes	TEXT	Notas
flag_medical_followup	BOOLEAN	Flag médica
filled_at	TIMESTAMP(TZ)	Quando preenchido
Soft delete + timestamps		
UNIQUE: training_session_id + athlete_id
TRIGGER: internal_load = minutes_effective × session_rpe

3. FLUXOS COMPLETOS
3.1 Criação de Sessão de Treino

UI (CreateSessionModal)
  ├─ Formulário: data, hora, tipo, objetivo, duração, 7 focos
  ├─ Validação: soma dos focos ≤ 120%
  └─ Submit
      ↓
API Client (trainings.ts)
  └─ POST /training-sessions
      ↓
Backend Router (training_sessions.py)
  ├─ @scoped_endpoint: permission "can_view_training_schedule"
  └─ Organization scoping
      ↓
Backend Service (training_session_service.py)
  ├─ Valida team existe e pertence à org
  ├─ Cria TrainingSession com status='draft'
  └─ Salva no DB
      ↓
Database (training_sessions)
  └─ INSERT com todos os campos
3.2 Ciclo de Vida da Sessão

draft → in_progress → closed → readonly (após 24h)

Regras de Edição (R40):
- Autor: 10 minutos para correções
- Superior: até 24 horas
- Após 24h: somente leitura (admin com nota pode editar)

Para Fechar:
- Soma dos focos > 0 e ≤ 120%
- Status deve ser 'draft' ou 'in_progress'

Para Reabrir:
- Apenas dentro de 24h do fechamento
3.3 Planejamento (Ciclos e Microciclos)

Macrociclo (temporada/fase)
  └─ Mesociclo (4-6 semanas) - parent_cycle_id aponta para macro
      └─ Microciclo (semana) - cycle_id aponta para meso
          └─ Sessões - microcycle_id aponta para micro
              └─ Wellness Pre/Post + Attendance por atleta
3.4 Análise de Desvio

Microciclo (planned_focus_*) vs Sessão (focus_*)
  ↓
Se diferença ≥ 20pts em qualquer foco OU ≥ 30% agregado:
  → planning_deviation_flag = true
  → Usuário pode preencher deviation_justification
3.5 Sugestões Inteligentes

TrainingSuggestionService analisa:
- Últimos 90 dias de microciclos similares
- Mínimo 3 microciclos para análise
- Desvio mínimo: 10 pontos

Retorna:
- focus_field: qual foco ajustar
- suggested_adjustment: quanto ajustar
- reason: explicação
- confidence: 'high', 'medium', 'low'
4. O QUE NÃO ESTÁ IMPLEMENTADO
Funcionalidade	Status
Banco de Exercícios	MOCK DATA - Sem backend
Avaliações/Analytics	MOCK DATA - Sem backend
Presenças	Backend retorna 501 NOT_IMPLEMENTED
Wellness Pre	Backend retorna 501 NOT_IMPLEMENTED
Wellness Post	Backend retorna 501 NOT_IMPLEMENTED
Exportar PDF	TODO no código
Favoritar exercício	TODO no código
Duplicar sessão	NÃO IMPLEMENTADO
Copiar semana	NÃO IMPLEMENTADO
5. ENDPOINTS DA API
Training Sessions
Método	Endpoint	Descrição
GET	/training-sessions	Lista sessões (paginado)
GET	/training-sessions/:id	Busca sessão
POST	/training-sessions	Cria sessão
PATCH	/training-sessions/:id	Atualiza sessão
DELETE	/training-sessions/:id	Soft delete
POST	/training-sessions/:id/close	Fecha sessão
POST	/training-sessions/:id/reopen	Reabre (24h)
GET	/training-sessions/:id/deviation	Análise de desvio
Training Cycles
Método	Endpoint	Descrição
GET	/training-cycles	Lista ciclos
GET	/training-cycles/:id	Busca ciclo + microciclos
POST	/training-cycles	Cria ciclo
PATCH	/training-cycles/:id	Atualiza ciclo
DELETE	/training-cycles/:id	Soft delete
GET	/training-cycles/teams/:teamId/active	Ciclos ativos
Training Microcycles
Método	Endpoint	Descrição
GET	/training-microcycles	Lista microciclos
GET	/training-microcycles/:id	Busca + sessões
POST	/training-microcycles	Cria microciclo
PATCH	/training-microcycles/:id	Atualiza
DELETE	/training-microcycles/:id	Soft delete
GET	/training-microcycles/teams/:teamId/current	Microciclo atual
GET	/training-microcycles/:id/summary	Resumo analítico
Training Suggestions
Método	Endpoint	Descrição
GET	/training-suggestions	Busca sugestões
POST	/training-suggestions/apply	Aplica sugestão
NÃO IMPLEMENTADOS (501)
Método	Endpoint
*	/training_sessions/:id/attendance
*	/training_sessions/:id/wellness_pre
*	/training_sessions/:id/wellness_post
ARQUIVOS A CRIAR/MODIFICAR
Arquivo	Ação	Linhas Est.
tests/e2e/training/training-CONTRACT.md	CRIAR	~250
tests/e2e/training/training-e2e.test.ts	CRIAR	~500
docs/modules/training-CONTRACT.md	ATUALIZAR	~800
ESTRUTURA DOS TESTES E2E
Seções Planejadas
A. Navegação e Rotas
/training redireciona para /training/agenda
Todas subrotas carregam (agenda, calendario, planejamento, banco, avaliacoes)
Rota inexistente dentro de /training/*
B. Autenticação
Sem auth → redirect /signin?callbackUrl=...
Com auth → acesso liberado
C. Agenda Semanal (API Real)
Lista sessões por equipe
Navegação entre semanas
Criar sessão via modal
Verificar sessão na lista
D. Calendário (API Real)
Visualização mensal
Navegação entre meses
Click em dia
E. Planejamento (API Real)
Lista ciclos (macro/meso)
Lista microciclos
Criar ciclo via API
F. Banco de Exercícios (Mock)
Página carrega com mock
Filtro funciona
G. Avaliações (Mock)
Dashboard carrega
H. CRUD de Sessões via API
Criar sessão
Buscar por ID
Atualizar
Deletar (soft)
Fechar sessão
Reabrir (se <24h)
I. Validações de Negócio
Soma focos > 120% bloqueia fechamento
Sessão sem focos não fecha
Reabertura após 24h falha
J. Ciclos e Microciclos via API
CRUD de ciclos
CRUD de microciclos
Relacionamento ciclo → microciclo → sessão
VERIFICAÇÃO
Executar testes:


npx playwright test tests/e2e/training/training-e2e.test.ts --project=chromium
Validar contrato:

Cada seção marcada como API REAL, MOCK ou NÃO IMPLEMENTADO
Todas as tabelas e colunas documentadas
Fluxos completos do UI ao banco
Helpers necessários (reutilizar/criar):

createSessionViaAPI
deleteSessionViaAPI
getSessionViaAPI
createCycleViaAPI
createMicrocycleViaAPI
