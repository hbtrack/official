<!-- STATUS: NEEDS_REVIEW -->

# 📋 Relatório Detalhado - Rota /games

**Data:** 07/01/2026  
**Versão:** 1.0  
**Status:** Em Desenvolvimento (Alpha)

---

## 📊 Resumo Executivo

A rota `/games` é o módulo de gerenciamento de jogos e partidas do HB Track. Permite agendar, acompanhar e analisar jogos de handebol com escalação, eventos ao vivo, estatísticas e relatórios pós-jogo.

### Indicadores
| Métrica | Valor |
|---------|-------|
| Componentes implementados | 15 |
| Tabs no detalhe | 5 (overview, lineup, events, stats, report) |
| **Cobertura API** | **🔴 0% (100% Mock)** |
| Funcionalidades core | ⚠️ Parcial |
| Testes automatizados | 🔴 Não existem |

---

## 🗂️ Estrutura da Rota

| Componente | Descrição | Status |
|------------|-----------|--------|
| `/games` | Dashboard de jogos | ✅ UI Completa |
| `/games?gameId=X` | Detalhe do jogo | ✅ UI Completa |
| `/games?isNew=true` | Modal de criação | ✅ UI Completa |

---

## ✅ O QUE ESTÁ IMPLEMENTADO E FUNCIONANDO

### 1. Estrutura de Rota

**Arquivos:**
- `src/app/(admin)/games/page.tsx` - Server Component com metadata
- `src/app/(admin)/games/layout.tsx` - Layout com autenticação
- `src/app/(admin)/games/GamesLayoutWrapper.tsx` - Client wrapper com Provider
- `src/app/(admin)/games/GamesClient.tsx` - Componente principal

**Funcionalidades:**
- ✅ Autenticação via `getSession()` - redireciona para `/signin` se não autenticado
- ✅ GamesContext provider para estado global
- ✅ Seleção de equipe persistente (localStorage)
- ✅ Navegação por query params (`gameId`, `tab`, `isNew`)
- ✅ Modal de seleção de equipe quando necessário

---

### 2. GamesContext (`GamesContext.tsx`)

**Estado Global:**
```typescript
interface GamesContextType {
  // Equipes
  teams: Team[];
  teamsLoading: boolean;
  selectedTeam: Team | null;
  setSelectedTeam: (team: Team | null) => void;
  
  // Jogo selecionado
  selectedGameId: string | null;
  selectedMatch: Match | null;
  
  // Tab ativa
  activeTab: GameTab; // 'overview' | 'lineup' | 'events' | 'stats' | 'report'
  
  // Filtros
  filters: GameFilters;
  
  // Modal de criação
  isCreateModalOpen: boolean;
  
  // Modo de visualização
  viewMode: GameViewMode; // 'cards' | 'table'
}
```

**Tipos Definidos:**
```typescript
interface Match {
  id: string;
  team_id: string;
  opponent_id: string;
  opponent_name?: string;
  match_date?: string;
  venue?: string;
  is_home?: boolean;
  home_score?: number;
  away_score?: number;
  status: 'Agendado' | 'Finalizado' | 'Cancelado';
  competition?: string;
  notes?: string;
}

interface MatchEvent {
  id: string;
  match_id: string;
  event_type: 'goal' | 'yellow_card' | 'red_card' | 'substitution' | 'timeout' | 'other';
  minute?: number;
  player_name?: string;
  description?: string;
}
```

---

### 3. Dashboard de Jogos (`GamesDashboard.tsx`)

**Funcionalidades Implementadas:**
- ✅ Cards de estatísticas resumidas:
  - Próximo jogo (data e adversário)
  - Total de jogos
  - Vitórias e aproveitamento (%)
  - CTA para criar novo jogo
- ✅ Barra de filtros completa
- ✅ Lista de jogos em cards OU tabela (toggle)
- ✅ Estado vazio com CTA
- ✅ Cálculo de estatísticas local
- ✅ Loading skeletons

**⚠️ DADOS MOCK:**
```javascript
const MOCK_GAMES: Match[] = [
  { id: '1', opponent_name: 'Flamengo', status: 'Agendado', ... },
  { id: '2', opponent_name: 'Vasco', status: 'Finalizado', home_score: 28, ... },
  // ... 4 jogos mockados
];
```

---

### 4. Barra de Filtros (`GamesFilterBar.tsx`)

**Filtros Implementados:**
- ✅ Busca por adversário
- ✅ Status (Todos, Agendados, Finalizados, Cancelados)
- ✅ Período (data início / data fim)
- ✅ Local (Casa / Fora)
- ✅ Toggle de visualização (cards / tabela)
- ✅ Botão de limpar filtros
- ✅ Indicador visual de filtros ativos

---

### 5. Card de Jogo (`GameCard.tsx`)

**Informações Exibidas:**
- ✅ Avatar do adversário (primeira letra)
- ✅ Nome do adversário
- ✅ Mando de campo (Casa/Fora)
- ✅ Status com cor indicativa
- ✅ Placar (se finalizado)
- ✅ Data e horário
- ✅ Local/Ginásio
- ✅ Botão "Ver detalhes"

---

### 6. Header da Página (`GamesHeader.tsx`)

**Funcionalidades:**
- ✅ Breadcrumb de navegação
- ✅ Título dinâmico (Dashboard vs Detalhe)
- ✅ Subtítulo contextual
- ✅ Botão "Voltar" no detalhe
- ✅ Botão "Novo Jogo" no dashboard
- ✅ Tabs de navegação no detalhe (5 tabs)

---

### 7. Detalhe do Jogo (`GameDetail.tsx`)

**Funcionalidades Implementadas:**
- ✅ Card de informações principais
- ✅ Avatar e nome do adversário
- ✅ Status com badge colorido
- ✅ Data, horário e local
- ✅ Placar (se finalizado)
- ✅ Notas do jogo
- ✅ Botões de ação (Editar, Cancelar)
- ✅ Sistema de tabs (5 tabs)
- ✅ Drawer de edição
- ✅ Modal de cancelamento

---

### 8. Tab Overview (`GameOverviewTab.tsx`)

**Funcionalidades:**
- ✅ Card de informações do jogo
- ✅ Histórico de confrontos (head-to-head) - **Mock**
- ✅ Notas e observações
- ✅ Checklist pré-jogo (jogos agendados)

**⚠️ DADOS MOCK:**
```javascript
const headToHead = {
  wins: 3,
  draws: 1,
  losses: 2,
  lastMatch: { date: '2024-01-15', score: '28-25', result: 'win' }
};
```

---

### 9. Tab Escalação (`GameLineupTab.tsx`)

**Funcionalidades:**
- ✅ Lista de titulares (máximo 7)
- ✅ Lista de reservas
- ✅ Contadores de jogadores
- ✅ Modo de edição (arrastar jogadores)
- ✅ Mover jogador entre titulares/reservas
- ✅ Visualização do campo com formação tática
- ✅ Posicionamento visual dos jogadores (formação 6-0)

**⚠️ DADOS MOCK:**
```javascript
const MOCK_PLAYERS = [
  { id: '1', name: 'João Silva', position: 'Goleiro', number: 1 },
  // ... 10 jogadores mockados
];
```

---

### 10. Tab Eventos (`GameEventsTab.tsx`)

**Funcionalidades:**
- ✅ Timeline visual de eventos
- ✅ Cards de estatísticas (Gols, Amarelos, Vermelhos, Substituições)
- ✅ Filtro por tipo de evento (clicável)
- ✅ Adicionar novo evento (modal)
- ✅ Ícones e cores por tipo
- ✅ Ordenação por minuto

**Tipos de Evento:**
| Tipo | Ícone | Cor |
|------|-------|-----|
| Gol | Flag | Verde |
| Cartão Amarelo | AlertTriangle | Amarelo |
| Cartão Vermelho | AlertTriangle | Vermelho |
| Substituição | ArrowRightLeft | Azul |
| Timeout | Hand | Roxo |
| Outro | Clock | Cinza |

**⚠️ DADOS MOCK:**
```javascript
const MOCK_EVENTS: MatchEvent[] = [
  { id: '1', event_type: 'goal', minute: 5, player_name: 'Pedro Santos', ... },
  // ... 5 eventos mockados
];
```

---

### 11. Tab Estatísticas (`GameStatsTab.tsx`)

**Funcionalidades:**
- ✅ Barras de estatísticas gerais (Gols, Finalizações, Defesas, Faltas)
- ✅ Gráficos circulares de eficiência (Ofensiva/Defensiva)
- ✅ Contagem de cartões
- ✅ Tabela de estatísticas por jogador (ordenável)
- ✅ Estados vazios para jogos agendados/cancelados

**Estatísticas Exibidas:**
- Gols marcados vs sofridos
- Finalizações (no alvo / total)
- Defesas do goleiro
- Faltas cometidas
- Eficiência ofensiva (%)
- Eficiência defensiva (%)

**⚠️ DADOS MOCK:**
```javascript
const MOCK_TEAM_STATS = {
  goals: 28,
  goalsConceded: 25,
  shots: 45,
  shotsOnTarget: 32,
  // ... mais estatísticas
};
const MOCK_PLAYER_STATS = [...]; // 7 jogadores
```

---

### 12. Tab Relatório (`GameReportTab.tsx`)

**Funcionalidades:**
- ✅ Informações básicas (data, adversário, resultado, local)
- ✅ Resumo da partida (editável)
- ✅ Pontos fortes (editável)
- ✅ Pontos a melhorar (editável)
- ✅ Observações (editável)
- ✅ Próximas ações (editável)
- ✅ Modo de edição inline
- ✅ Botão "Exportar PDF" (placeholder)
- ✅ Estados vazios para jogos agendados/cancelados

**⚠️ DADOS MOCK:**
```javascript
const report = {
  summary: 'Partida disputada com grande intensidade...',
  strengths: 'Contra-ataques rápidos...',
  improvements: 'Marcação individual no pivô...',
  observations: 'Jogador Lucas apresentou fadiga...',
  nextActions: 'Trabalhar posicionamento defensivo...',
};
```

---

### 13. Modais Implementados

#### CreateGameModal
- ✅ Formulário completo de criação
- ✅ Campos: Adversário, Data, Hora, Casa/Fora, Local, Competição, Notas
- ✅ Validação de campos obrigatórios
- ✅ Loading state

#### EditGameDrawer
- ✅ Drawer lateral de edição
- ✅ Preenche automaticamente com dados do jogo
- ✅ Permite editar placar (jogos finalizados)
- ✅ Validação de campos

#### GameEventModal
- ✅ Seleção de tipo de evento
- ✅ Seleção de jogador (dropdown)
- ✅ Campo de minuto
- ✅ Campo de descrição
- ✅ Lista de jogadores **mockada**

#### CancelGameModal
- ✅ Modal de confirmação
- ✅ Campo de motivo (opcional)
- ✅ Aviso visual de ação irreversível

---

## ❌ O QUE FALTA PARA STAGING

### 1. **BLOQUEADOR CRÍTICO: API de Jogos**

**⚠️ NENHUMA INTEGRAÇÃO COM BACKEND EXISTE**

Todo o módulo usa dados **mockados**. Não existe serviço de API (`src/lib/api/games.ts` ou similar).

**Endpoints Necessários:**
| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/matches` | GET | Listar jogos da equipe |
| `/matches` | POST | Criar novo jogo |
| `/matches/:id` | GET | Buscar jogo por ID |
| `/matches/:id` | PATCH | Atualizar jogo |
| `/matches/:id` | DELETE | Excluir jogo |
| `/matches/:id/cancel` | POST | Cancelar jogo |
| `/matches/:id/events` | GET | Listar eventos do jogo |
| `/matches/:id/events` | POST | Adicionar evento |
| `/matches/:id/lineup` | GET | Buscar escalação |
| `/matches/:id/lineup` | PUT | Salvar escalação |
| `/matches/:id/stats` | GET | Buscar estatísticas |
| `/matches/:id/report` | GET/PUT | Buscar/Salvar relatório |
| `/teams/:id/athletes` | GET | Listar atletas para escalação |
| `/teams/:id/h2h/:opponentId` | GET | Histórico de confrontos |

---

### 2. Funcionalidades Pendentes

#### Dashboard
| Item | Status | Prioridade |
|------|--------|------------|
| Integração com API real | 🔴 Não implementado | **CRÍTICA** |
| Filtro por competição | 🔴 Não implementado | Média |
| Ordenação de jogos | 🔴 Não implementado | Baixa |
| Paginação | 🔴 Não implementado | Média |
| Busca avançada (fuzzy) | 🔴 Não implementado | Baixa |

#### Detalhe do Jogo
| Item | Status | Prioridade |
|------|--------|------------|
| Carregar jogo da API | 🔴 Mock | **CRÍTICA** |
| Salvar edições na API | 🔴 Mock | **CRÍTICA** |
| Cancelar via API | 🔴 Mock | **CRÍTICA** |
| Duplicar jogo | 🔴 Não implementado | Baixa |
| Histórico de alterações | 🔴 Não implementado | Baixa |

#### Tab Escalação
| Item | Status | Prioridade |
|------|--------|------------|
| Listar atletas da API | 🔴 Mock | **CRÍTICA** |
| Salvar escalação na API | 🔴 Mock | **CRÍTICA** |
| Drag & drop entre posições | 🔴 Não implementado | Média |
| Formações táticas variadas | 🔴 Apenas 6-0 | Baixa |
| Foto do jogador | 🔴 Não implementado | Baixa |

#### Tab Eventos
| Item | Status | Prioridade |
|------|--------|------------|
| Listar eventos da API | 🔴 Mock | **CRÍTICA** |
| Salvar evento na API | 🔴 Mock | **CRÍTICA** |
| Editar evento existente | 🔴 Não implementado | Alta |
| Excluir evento | 🔴 Não implementado | Alta |
| Eventos em tempo real (WebSocket) | 🔴 Não implementado | Baixa |

#### Tab Estatísticas
| Item | Status | Prioridade |
|------|--------|------------|
| Buscar stats da API | 🔴 Mock | **CRÍTICA** |
| Gráficos interativos (Recharts) | 🟡 Básico | Média |
| Comparativo com média do time | 🔴 Não implementado | Média |
| Exportar estatísticas | 🔴 Não implementado | Baixa |

#### Tab Relatório
| Item | Status | Prioridade |
|------|--------|------------|
| Salvar relatório na API | 🔴 Mock | **CRÍTICA** |
| Exportar PDF funcional | 🔴 Placeholder | Alta |
| Templates de relatório | 🔴 Não implementado | Média |
| Compartilhar relatório | 🔴 Não implementado | Baixa |

---

### 3. Serviço de API a Criar

**Arquivo necessário:** `src/lib/api/games.ts`

```typescript
// Estrutura sugerida
export const gamesService = {
  // Jogos
  getMatches: (teamId: string, filters?: GameFilters) => Promise<Match[]>,
  getMatchById: (matchId: string) => Promise<Match>,
  createMatch: (teamId: string, data: CreateMatchDTO) => Promise<Match>,
  updateMatch: (matchId: string, data: UpdateMatchDTO) => Promise<Match>,
  cancelMatch: (matchId: string, reason?: string) => Promise<void>,
  
  // Escalação
  getLineup: (matchId: string) => Promise<MatchParticipant[]>,
  saveLineup: (matchId: string, participants: MatchParticipant[]) => Promise<void>,
  
  // Eventos
  getEvents: (matchId: string) => Promise<MatchEvent[]>,
  createEvent: (matchId: string, event: CreateEventDTO) => Promise<MatchEvent>,
  updateEvent: (eventId: string, data: UpdateEventDTO) => Promise<MatchEvent>,
  deleteEvent: (eventId: string) => Promise<void>,
  
  // Estatísticas
  getMatchStats: (matchId: string) => Promise<MatchStats>,
  
  // Relatório
  getReport: (matchId: string) => Promise<MatchReport>,
  saveReport: (matchId: string, report: MatchReport) => Promise<void>,
  exportPDF: (matchId: string) => Promise<Blob>,
};
```

---

### 4. Hook a Criar

**Arquivo necessário:** `src/hooks/useMatches.ts`

```typescript
export function useMatches(teamId: string, filters?: GameFilters) {
  return useQuery({
    queryKey: ['matches', teamId, filters],
    queryFn: () => gamesService.getMatches(teamId, filters),
    enabled: !!teamId,
  });
}

export function useMatch(matchId: string) { ... }
export function useMatchEvents(matchId: string) { ... }
export function useMatchLineup(matchId: string) { ... }
export function useMatchStats(matchId: string) { ... }
```

---

### 5. Testes Necessários

| Tipo | Cobertura Atual | Meta |
|------|-----------------|------|
| Testes unitários | 🔴 0% | 70% |
| Testes de integração (API) | 🔴 0% | 80% |
| Testes E2E (Cypress) | 🔴 0% | 60% |

**Cenários críticos:**
1. [ ] Criar jogo → Verificar na lista
2. [ ] Editar jogo → Verificar alterações
3. [ ] Cancelar jogo → Verificar status
4. [ ] Adicionar evento → Verificar timeline
5. [ ] Salvar escalação → Verificar persistência
6. [ ] Editar relatório → Salvar → Recarregar → Verificar

---

### 6. Validações de Backend Necessárias

| Validação | Descrição |
|-----------|-----------|
| Conflito de datas | Não permitir 2 jogos no mesmo horário |
| Escalação completa | Mínimo de jogadores para jogar |
| Status de atleta | Verificar se atleta está ativo/disponível |
| Permissões | Verificar se usuário pode editar jogo |
| Histórico | Não permitir editar jogos muito antigos |

---

## 📁 Estrutura de Arquivos

```
src/
├── app/(admin)/games/
│   ├── layout.tsx                    # Layout com auth
│   ├── GamesLayoutWrapper.tsx        # Client wrapper
│   ├── GamesClient.tsx               # Componente principal
│   └── page.tsx                      # Server component
│
├── components/games/
│   ├── index.ts                      # Exports
│   ├── GameCard.tsx                  # Card de jogo
│   ├── GameDetail.tsx                # Componente de detalhe
│   ├── GamesDashboard.tsx            # Dashboard principal
│   ├── GamesFilterBar.tsx            # Barra de filtros
│   ├── GamesHeader.tsx               # Header da página
│   │
│   ├── tabs/
│   │   ├── GameOverviewTab.tsx       # Tab resumo
│   │   ├── GameLineupTab.tsx         # Tab escalação
│   │   ├── GameEventsTab.tsx         # Tab eventos
│   │   ├── GameStatsTab.tsx          # Tab estatísticas
│   │   └── GameReportTab.tsx         # Tab relatório
│   │
│   └── modals/
│       ├── CreateGameModal.tsx       # Modal criar jogo
│       ├── EditGameDrawer.tsx        # Drawer editar
│       ├── GameEventModal.tsx        # Modal adicionar evento
│       └── CancelGameModal.tsx       # Modal cancelar
│
├── context/
│   └── GamesContext.tsx              # Context provider
│
└── lib/api/
    └── games.ts                      # ❌ NÃO EXISTE
```

---

## 📊 Comparativo de Prontidão

| Aspecto | /teams | /training | /games |
|---------|--------|-----------|--------|
| UI Completa | ✅ 90% | ✅ 85% | ✅ 95% |
| API Service | ✅ Existe | ✅ Existe | ❌ Não existe |
| Hooks | ✅ Existem | ✅ Existem | ❌ Não existem |
| Dados Mock | 10% | 30% | **100%** |
| Pronto para staging | ⚠️ Parcial | ⚠️ Parcial | ❌ Não |

---

## 🚀 Recomendações para Staging

### Prioridade Crítica (Bloqueadores)
1. **Criar serviço de API** (`src/lib/api/games.ts`)
2. **Implementar endpoints no backend** (matches CRUD)
3. **Criar hooks React Query** (`useMatches`, `useMatch`, etc.)
4. **Remover todos os dados mock**
5. **Implementar persistência de escalação**

### Prioridade Alta
1. Editar/Excluir eventos
2. Exportar PDF de relatório
3. Validações de formulário
4. Tratamento de erros de API
5. Loading states em todas as operações

### Prioridade Média
1. Paginação no dashboard
2. Gráficos interativos com Recharts
3. Filtro por competição
4. Drag & drop na escalação
5. Histórico de alterações

### Prioridade Baixa
1. WebSocket para eventos em tempo real
2. Templates de relatório
3. Formações táticas variadas
4. Compartilhamento de relatório
5. PWA / Offline support

---

## 📈 Roadmap Sugerido

### Sprint 1 (2 semanas) - **Fundação**
- [ ] Backend: Criar tabelas `matches`, `match_events`, `match_participants`
- [ ] Backend: Endpoints CRUD de matches
- [ ] Frontend: Criar `src/lib/api/games.ts`
- [ ] Frontend: Criar hooks básicos

### Sprint 2 (2 semanas) - **Integração Core**
- [ ] Frontend: Substituir mocks por chamadas reais
- [ ] Frontend: Integrar escalação com atletas
- [ ] Frontend: Integrar eventos
- [ ] Backend: Endpoint de estatísticas calculadas

### Sprint 3 (1 semana) - **Polimento**
- [ ] Frontend: Exportar PDF
- [ ] Frontend: Validações completas
- [ ] QA: Testes manuais
- [ ] Fix: Bugs encontrados

### Sprint 4 (1 semana) - **Staging**
- [ ] Testes E2E
- [ ] Performance review
- [ ] Deploy staging

---

## ⚠️ Alertas Importantes

1. **Módulo 100% Mock** - Nenhuma funcionalidade persiste dados reais
2. **Sem service de API** - Arquivo `games.ts` precisa ser criado do zero
3. **Sem hooks** - Nenhum hook React Query existe para jogos
4. **Backend não verificado** - Endpoints podem não existir
5. **Dependência de atletas** - Escalação depende do módulo de atletas funcionar

---

**Documento gerado automaticamente em 07/01/2026**
