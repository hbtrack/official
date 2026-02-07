<!-- STATUS: NEEDS_REVIEW -->

## 🗺️ **MAPA DE FEATURES POR CONTEXTO DO USUÁRIO**

## 👤 **ATLETA** - Suas Telas

### 1️⃣ **Tela: Meu Wellness** (`/athlete/wellness`)
**O que o atleta vê:**
- 📋 **Lista de treinos pendentes** (próximos 7 dias)
- ⏰ **Countdown timer**: "Preencher em X horas" (destaque vermelho <2h)
- ✅ **Status visual**: CheckCircle verde (respondido) | AlertTriangle amarelo (pendente)
- 🏅 **Badge dourado** no canto superior: "Você respondeu 92% este mês!"

**Actions:**
- Clicar em "Preencher Pré-Treino" → Modal com sliders
- Clicar em "Preencher Pós-Treino" → Modal RPE + sensações

---

### 2️⃣ **Modal: Wellness Pré-Treino** (Aberto ao clicar)
**Componentes:**
- 🎯 **4 Presets rápidos**: "💪 Muito Bem" | "😊 Normal" | "😓 Cansado" | "😴 Muito Cansado"
- 🎚️ **5 Sliders** (0-10):
  - 😴 Qualidade do Sono (com emoji dinâmico)
  - 💪 Fadiga Muscular
  - 🧠 Estresse Mental
  - 🏃 Prontidão Física
  - 😌 Humor Geral
- 📝 **Campo opcional**: "Observações"
- ⏱️ **Countdown fixo**: "Tempo restante: 1h 23min"

**Validação:**
- ❌ Bloqueado se prazo expirou (>24h)
- ✅ Sucesso: Toast "Wellness enviado! 🎉"

---

### 3️⃣ **Modal: Wellness Pós-Treino** (Após treino)
**Componentes:**
- 🎚️ **RPE Slider** (0-10) com escala Borg visual:
  - 0: 😌 Repouso
  - 3: 🙂 Leve
  - 5: 😐 Moderado
  - 7: 😤 Pesado
  - 10: 🥵 Máximo
- ⏱️ **Input**: "Minutos efetivos" (pré-preenchido com duração planejada)
- 📊 **Card azul calculado automaticamente**: "Carga Interna: 450" (RPE × minutos)
- 🎚️ **Sliders pós-treino**:
  - 😴 Fadiga Após
  - 😌 Humor Após
- 📝 **Observações opcionais**

---

### 4️⃣ **Tela: Meu Perfil** (`/athlete/profile`)
**Seção "Minhas Conquistas":**
- 🏆 **Badge Grid**: Visualização de todos badges conquistados
  - 🥇 Ouro: ≥90% respostas (3 meses consecutivos)
  - 🥈 Prata: ≥90% (1 mês)
  - 🥉 Bronze: Primeira resposta

**Seção "Privacidade e Dados" (LGPD):**
- 📥 **Botão**: "Exportar Meus Dados" (JSON/CSV)
- 📄 **Link**: "Política de Privacidade"
- 🔒 **Info**: "Seus dados serão anonimizados após 3 anos"

---

### 5️⃣ **Tela: Rankings** (`/training/rankings-wellness`)
**O atleta vê:**
- 🏆 **Ranking de Equipes** (mês atual):
  - 1º Juvenil Feminino - 94% taxa resposta 🥇
  - 2º Sub-16 Masculino - 87% 🥈
  - (Sua equipe destacada em azul)
- 👥 **Top 5 Atletas da Equipe**:
  - Maria Silva - 100% 🏅
  - João Santos - 96% 🏅
  - **Você** - 92% 🏅 (destacado)

---

---

## 👔 **TREINADOR/COORDENADOR** - Suas Telas

### 1️⃣ **Tela: Dashboard Training** (`/training/dashboard`)
**Cards principais:**
- 📊 **Card "Semáforo de Carga"**:
  - Gráfico de barras semanal
  - Verde: carga OK | Amarelo: atenção | Vermelho: sobrecarga
  - Botão: "Ver Alertas Ativos (3)"

- 🔔 **Card "Sugestões Pendentes"**:
  - "5 sugestões aguardando revisão"
  - Preview da primeira: "Reduzir carga 15% - Ana Silva"
  - Botão: "Revisar Todas"

- 📈 **Card "Taxa de Resposta Wellness"**:
  - Gráfico de linha temporal (últimos 30 dias)
  - Meta 80% destacada (linha pontilhada)
  - Área verde quando >80% | Vermelha <70%

- 🏆 **Card "Rankings"**:
  - Mini tabela: Top 3 equipes
  - Link: "Ver Todos os Rankings"

---

### 2️⃣ **Tela: Planejamento Semanal** (`/training/planner`)
**Componente SessionCard:**
- 📅 Data + Horário
- 🚦 **Badge Semáforo**: Verde/Amarelo/Vermelho
- 📊 Carga planejada vs real
- 👥 **Botão "Status Wellness"** → Abre dashboard modal

---

### 3️⃣ **Modal: Dashboard Wellness (ao clicar em treino)**
**Componente WellnessStatusDashboard.tsx:**
- 📊 **Header Stats**:
  - 💙 "12/15 responderam Pré (80%)"
  - 💚 "10/15 responderam Pós (67%)"
  - ⚠️ "5 pendentes"

- 👥 **Grid de Atletas** (3 colunas):
  ```
  ✅ Ana Silva 🏅     | ⚠️ João Santos      | ❌ Maria Costa
  (Pré+Pós completo) | (Apenas Pré)        | (Nenhum - Ausente)
  ```

- 🔔 **Botão "Enviar Lembretes"** (limite 2/mês):
  - Clica → Modal confirma: "Enviar para 5 atletas?"
  - Sucesso → Toast "Lembretes enviados! 📩"

- 🔗 **Link**: "Ver Top 5 Comprometidos" → Redireciona para relatório

---

### 4️⃣ **Tela: Alertas e Sugestões** (`/training/alertas`)
**Aba "Alertas Ativos":**
- 🚨 **AlertBanner.tsx** (lista vertical):
  ```
  ⚠️ SOBRECARGA DETECTADA - Ana Silva
  Carga semanal: 2.450 (130% do esperado)
  Recomendação: Reduzir 15% próxima semana
  [Dispensar] [Ver Detalhes]
  ```

**Aba "Sugestões Pendentes":**
- 🎯 **SuggestionSlider.tsx** (swipe cards):
  ```
  💡 SUGESTÃO AUTOMÁTICA #1234
  Atleta: João Santos
  Motivo: Taxa resposta baixa (60% últimos 7 dias)
  Ação: Sessão de recuperação + conversa individual
  [Aplicar] [Ignorar] [Ver Próxima →]
  ```

**Aba "Histórico":**
- Tabela com filtros (data, tipo, status)

---

### 5️⃣ **Tela: Banco de Exercícios** (`/training/banco`)
**Sidebar Filtros:**
- 🔍 **Busca**: Input com debounce
- 📂 **Tree View** (hierarquia tags):
  ```
  ▼ Tático
    ☑️ Ataque Posicional
    ☐ Defesa 6:0
  ▼ Físico
    ☐ Resistência
    ☑️ Velocidade
  ```
- 🎛️ **Operador**: Radio "E (todas)" | "OU (ao menos uma)"
- ⭐ **Filtro Favoritos**: Toggle

**Grid Principal:**
- 🎬 **ExerciseCard.tsx** (grid 3 colunas):
  ```
  [Thumbnail YouTube]
  Passe e Movimento
  Tags: Tático · Ataque ⭐
  [▶️ Ver Detalhes]
  ```

**Modal Detalhes:**
- 🎥 YouTube player 16:9
- 📝 Descrição completa
- 🏷️ Tags: pills coloridas
- ⭐ Favoritar
- 📋 **Botão "Adicionar ao Treino"** (drag-and-drop)

---

### 6️⃣ **Modal: Planejar Sessão** (SessionModal)
**Aba "Exercícios":**
- 📚 **Sidebar**: Mini banco de exercícios (compacto)
- 🎯 **Drag-and-Drop**:
  - Arraste exercício → Área central
  - Reordene com drag handle 🔀
- 📊 **Lista de Exercícios Adicionados**:
  ```
  1. [🔀] Aquecimento Dinâmico    [10 min] [✏️] [🗑️]
  2. [🔀] Passe e Movimento        [20 min] [✏️] [🗑️]
  Total: 30 min / 60 min planejados ✅
  ```
- ⚠️ **Warning**: "Excede duração em 10 min" (se total > planejado)

---

### 7️⃣ **Tela: Métricas e Analytics** (`/training/metrics`)
**Gráficos:**
- 📈 **WeeklyLoadChart**: Linha temporal carga semanal (threshold destacado)
- 📊 **DeviationBarChart**: Barras com cores (verde/amarelo/vermelho)
- 🥧 **FocusDistributionPieChart**: 7 categorias (Tático, Técnico, etc)
- 📉 **WellnessResponseRateChart**: Linha temporal taxa resposta (meta 80%)

**Filtros:**
- 📅 Seletor de mês
- 👥 Seletor de equipe
- 🔄 **Lazy loading**: Fetch apenas IDs → Detalhes on-demand

---

### 8️⃣ **Tela: Relatório Top 5** (`/teams/{id}/top-performers`)
**Componente:**
- 🏆 **Card Header**: "Top 5 Atletas Comprometidos - Janeiro 2026"
- 📊 **Tabela**:
  ```
  🥇 1º Ana Silva      | 100% | 3 meses consecutivos 🏅
  🥈 2º João Santos    | 96%  | 1 mês 🏅
  🥉 3º Maria Costa    | 92%  | 1 mês 🏅
  ```
- 📥 **Botão "Exportar PDF"**: Relatório completo

---

---

## 🔔 **NOTIFICAÇÕES (Todos os Usuários)**

### Bell Icon (Header Global)
**Componente NotificationBell.tsx:**
- 🔴 **Badge contador**: Círculo vermelho "5"
- Clica → Dropdown

**NotificationDropdown.tsx:**
```
🔔 Notificações (5 não lidas)

⏰ Lembrete: Preencher Wellness Pré-Treino
   Sessão amanhã às 18h • Há 2 horas

🏅 Você ganhou um badge!
   Comprometimento Ouro (90%+ 3 meses) • Há 1 dia

📊 Nova sugestão disponível
   Reduzir carga - Ana Silva • Há 3 dias


## 📱 **TOURS GUIADOS (Onboarding)**

### Tour Treinador (7 passos)
**Trigger:** Primeiro login após deploy

1. **Dashboard** → Destaca card "Semáforo de Carga"
2. **Planejamento** → Mostra badge verde/amarelo/vermelho
3. **SessionModal** → Demonstra dashboard wellness
4. **Alertas** → Mostra lista de sugestões
5. **Banco de Exercícios** → Drag-and-drop demo
6. **Rankings** → Explica métricas
7. **Export PDF** → Final

### Tour Atleta (6 passos)
**Trigger:** Primeiro login após deploy

1. **Wellness Pré** → Sliders + presets
2. **Wellness Pós** → RPE + carga interna
3. **Badge** → Mostra conquista 🏅
4. **Deadline** → Countdown timer explicação
5. **Rankings** → "Veja sua posição"
6. **Perfil** → Export de dados LGPD

---

---

## 🎨 **COMPONENTES VISUAIS CHAVE**

| Componente | Onde Aparece | Responsável |
|------------|--------------|-------------|
| **FocusValidationBadge** | SessionCard (lista semanal) | Treinador |
| **WellnessStatusDashboard** | Modal ao clicar em treino | Treinador |
| **ExerciseCard** | Banco de exercícios | Treinador/Coordenador |
| **AlertBanner** | Página de alertas | Treinador |
| **SuggestionSlider** | Página de sugestões | Treinador |
| **WellnessPreForm** | Modal atleta | Atleta |
| **WellnessPostForm** | Modal atleta | Atleta |
| **BadgeDisplay** | Perfil atleta | Atleta |
| **TeamRankingTable** | Página rankings | Todos |
| **NotificationBell** | Header global | Todos |

---

---

## 📋 **CHECKLIST DE NAVEGAÇÃO (Para Testes E2E)**

### Como Atleta:
- [ ] Login → Badge de % aparece no header
- [ ] Ir para `/athlete/wellness` → Ver lista de treinos pendentes
- [ ] Clicar "Preencher Pré" → Modal com sliders + countdown
- [ ] Submeter → Toast sucesso + checkmark verde
- [ ] Ir para perfil → Ver badges conquistados
- [ ] Clicar "Exportar Dados" → Download JSON/CSV

### Como Treinador:
- [ ] Login → Dashboard com 4 cards
- [ ] Ir para `/training/planner` → Ver semáforo em cada treino
- [ ] Clicar treino → Modal com grid de atletas + botão lembretes
- [ ] Ir para `/training/alertas` → Ver sugestões pendentes
- [ ] Aplicar sugestão → Confirm modal → Toast "Aplicado!"
- [ ] Ir para `/training/banco` → Filtrar exercícios por tag
- [ ] Arrastar exercício → SessionModal → Ver lista atualizada


## ✅ **O QUE EXISTE NO SISTEMA**

### **Páginas Implementadas:**

#### ✅ Atleta (Rotas `/athlete/`)
- **`/athlete/wellness-pre/[sessionId]`** - Formulário Wellness Pré-Treino ✅
  - Componente: WellnessPreForm.tsx (378 linhas)
  - Sliders, presets, countdown
  
- **`/athlete/wellness-post/[sessionId]`** - Formulário Wellness Pós-Treino ✅
  - Componente: `WellnessPostForm.tsx` (478 linhas)
  - RPE, carga interna, recovery sliders

#### ✅ Training Staff (Rotas `/training/`)
- **`/training/agenda`** - Planejamento Semanal ✅
  - Componente: `AgendaClient.tsx`
  - SessionCard com badges semáforo
  
- **`/training/exercise-bank`** - Banco de Exercícios ✅
  - Grid de exercícios com drag-and-drop
  - Filtros por tags hierárquicas
  - ExerciseCard component
  
- **`/training/banco`** (rota admin alternativa) - Banco Admin ✅

#### ✅ Analytics
- **`/analytics`** - Dashboard de Métricas ✅
  - WeeklyLoadChart, DeviationAlerts
  - WellnessResponseChart

### **Componentes Implementados:**

✅ **Wellness:**
- WellnessStatusDashboard.tsx (618 linhas) - Grid de atletas no SessionModal
- AthleteWellnessModal.tsx (648 linhas) - Detalhes do atleta
- WellnessPreForm.tsx (378 linhas)
- `WellnessPostForm.tsx` (478 linhas)
- `Slider.tsx` (185 linhas) - Sliders 0-10

✅ **Exercícios:**
- `ExerciseCard.tsx` (320 linhas)
- `DraggableExerciseCard.tsx` (95 linhas)
- `SessionExerciseDropZone.tsx` (545 linhas)
- `VirtualizedExerciseGrid.tsx` (180 linhas)
- `TagFilter.tsx` (280 linhas)

✅ **Validação:**
- `FocusValidationBadge.tsx` (122 linhas)
- `JustificationModal.tsx` (216 linhas)
- `FocusTemplates.tsx` (196 linhas)

✅ **Analytics:**
- `WeeklyLoadChart.tsx` (300 linhas)
- `DeviationAlerts.tsx` (280 linhas)
- `WellnessResponseChart.tsx` (320 linhas)

✅ **Modal:**
- SessionModal.tsx - Com 4 tabs (Detalhes, **Exercícios**, Presenças, Wellness)

---

## ❌ **O QUE NÃO EXISTE (Apenas Planejado)**

### **Páginas Faltantes:**

❌ **`/athlete/wellness`** - Lista de treinos pendentes
❌ **`/athlete/profile`** - Perfil com badges e export LGPD
❌ **`/training/dashboard`** - Dashboard principal com cards
❌ **`/training/planner`** - Planejamento visual
❌ **`/training/alertas`** - Página de alertas e sugestões
❌ **`/training/metrics`** - Métricas avançadas
❌ **`/training/rankings-wellness`** - Rankings de equipes
❌ **`/teams/{id}/top-performers`** - Relatório Top 5

### **Componentes Faltantes:**

❌ **`NotificationBell.tsx`** - Sino com badge (apenas mencionado no README)
❌ **`AlertBanner.tsx`** - Banners de alertas (pendente Step 18)
❌ **`SuggestionSlider.tsx`** - Cards de sugestões (pendente Step 18)
❌ **`BadgeDisplay.tsx`** - Display de badges no perfil
❌ **`TeamRankingTable.tsx`** - Tabela de rankings

### **Funcionalidades Faltantes:**

❌ **Sistema de Notificações:**
- Bell icon no header
- Dropdown de notificações
- WebSocket real-time

❌ **Sistema de Badges:**
- Badge 🏅 ao lado dos atletas
- Conquistas no perfil
- Animação confetti

❌ **Tours Guiados:**
- Tour Treinador (7 passos)
- Tour Atleta (6 passos)
- Onboarding flow

❌ **Alertas e Sugestões:**
- Página de alertas ativos
- Sugestões pendentes
- Aplicar/rejeitar sugestões

❌ **Export e LGPD:**
- Export PDF relatórios
- Export dados do atleta
- Página data retention

---

## 📊 **RESUMO DO STATUS**

| Categoria | Implementado | Pendente |
|-----------|--------------|----------|
| **Páginas Atleta** | 2/4 (50%) | /wellness, /profile |
| **Páginas Training** | 2/8 (25%) | /dashboard, /planner, /alertas, /metrics, /rankings, /top-performers |
| **Componentes Wellness** | 5/5 (100%) | ✅ Completo |
| **Componentes Exercícios** | 5/5 (100%) | ✅ Completo |
| **Componentes Alertas** | 0/2 (0%) | AlertBanner, SuggestionSlider |
| **Sistema Notificações** | 0% | Bell, Dropdown, WebSocket |
| **Sistema Badges** | 0% | Display, Conquistas, Animações |
| **Tours Guiados** | 0% | Treinador, Atleta |

---

## 🎯 **PRIORIDADE DE IMPLEMENTAÇÃO**

**Para completar as telas descritas, faltam:**

1. **ALTA PRIORIDADE** (Features core):
   - `/athlete/wellness` - Lista de treinos (hub principal atleta)
   - `/training/dashboard` - Dashboard principal staff
   - Sistema de notificações (NotificationBell)
   - `/training/alertas` - Página de sugestões

2. **MÉDIA PRIORIDADE** (UX importante):
   - Sistema de badges (display no grid)
   - `/training/rankings-wellness` - Rankings
   - Tours guiados (onboarding)

3. **BAIXA PRIORIDADE** (Nice-to-have):
   - Export PDF relatórios
   - `/athlete/profile` completo
   - Página data retention admin

**As telas que você viu no mapa são uma mistura de:**
- ✅ **Já implementado** (Steps 10-21)
- 📋 **Planejado** (Steps 22-31 do _PLANO_TRAINING.md)


## 🗺️ **CONFIGURAÇÃO DE NAVEGAÇÃO - PÁGINAS IMPLEMENTADAS**

## **1. ESTRUTURA DE ROTAS NEXT.JS**

### **Rotas Protegidas** (`(protected)` layout)
Todas as rotas protegidas compartilham:
- ✅ **Sidebar esquerda** (desktop) / **Drawer** (mobile)
- ✅ **TopBar** com menu hamburger e logout
- ✅ **Autenticação obrigatória** (redirect para `/signin` se não autenticado)
- ✅ **FloatingActionButton** (enviar mensagem)

```
(protected)/
├── analytics/              ✅ Implementado
│   └── page.tsx           → /analytics
├── athlete/
│   ├── wellness-pre/      ✅ Implementado
│   │   └── [sessionId]/
│   │       └── page.tsx   → /athlete/wellness-pre/{id}
│   └── wellness-post/     ✅ Implementado
│       └── [sessionId]/
│           └── page.tsx   → /athlete/wellness-post/{id}
└── training/
    ├── exercise-bank/     ✅ Implementado
    │   └── page.tsx       → /training/exercise-bank
    └── presencas/
        └── page.tsx       → /training/presencas
```

### **Rotas Admin** (`(admin)` layout)
```
(admin)/
└── training/              ✅ Implementado
    ├── page.tsx          → /training (redireciona para /agenda)
    ├── agenda/           ✅ Implementado
    │   └── page.tsx      → /training/agenda
    ├── banco/            ✅ Implementado (duplicata de exercise-bank)
    │   └── page.tsx      → /training/banco
    ├── planejamento/
    │   └── page.tsx      → /training/planejamento
    ├── avaliacoes/
    │   └── page.tsx      → /training/avaliacoes
    └── calendario/
        └── page.tsx      → /training/calendario
```

---

## **2. SIDEBAR PRINCIPAL** (ProfessionalSidebar.tsx)

### **Localização:**
ProfessionalSidebar.tsx

### **Configuração Atual:**

#### **SEÇÃO: PLANEJAMENTO TÉCNICO**
Menu expansível **"Treinos"** com submenu:

```tsx
const treinosSubmenu = [
  { name: 'Agenda Semanal', href: '/training/agenda', icon: CalendarDays },
  { name: 'Planejamento', href: '/training/planejamento', icon: ClipboardList },
  { name: 'Banco de Exercícios', href: '/training/banco', icon: ListChecks }, // ✅
  { name: 'Avaliações', href: '/training/avaliacoes', icon: Target },
  { name: 'Presenças', href: '/training/presencas', icon: UserCheck },
];
```

**Como acessar:**
1. Sidebar → Expandir **"Treinos"** (ícone prancheta)
2. Clicar em **"Agenda Semanal"** → `/training/agenda` ✅
3. Clicar em **"Banco de Exercícios"** → `/training/banco` ✅

---

## **3. COMO O USUÁRIO ACESSA CADA PÁGINA**

### ✅ **Página: Banco de Exercícios**
**Rotas disponíveis:**
- `/training/banco` (rota admin)
- `/training/exercise-bank` (rota protected)

**Navegação:**
```
1. Login
2. Sidebar → "Treinos" (expandir)
3. Clicar "Banco de Exercícios"
4. Página carrega com:
   - Sidebar com filtros (tags, busca, favoritos)
   - Grid de exercícios (3 colunas)
   - Cards draggable
```

**Componentes renderizados:**
- `ExerciseCard.tsx` → Cards de exercícios
- `DraggableExerciseCard.tsx` → Wrapper drag-and-drop
- `TagFilter.tsx` → Tree view de tags
- `VirtualizedExerciseGrid.tsx` → Se >100 exercícios

---

### ✅ **Página: Agenda Semanal**
**Rota:** `/training/agenda`

**Navegação:**
```
1. Login
2. Sidebar → "Treinos" (expandir)
3. Clicar "Agenda Semanal"
4. Página carrega com:
   - Calendário semanal
   - SessionCards com badges semáforo
   - Botão "Criar Sessão"
```

**Clique em SessionCard:**
- Abre SessionModal.tsx com 4 tabs:
  1. **Detalhes** → Form de edição
  2. **Exercícios** ✅ → `SessionExerciseDropZone` (drag-and-drop)
  3. **Presenças** ✅ → `AttendanceTab`
  4. **Wellness** ✅ → `WellnessStatusDashboard`

---

### ✅ **Página: Wellness Pré-Treino (Atleta)**
**Rota:** `/athlete/wellness-pre/{sessionId}`

**Navegação:**
```
❌ NÃO HÁ LINK NA SIDEBAR (acesso via notificação ou link direto)

Formas de acesso:
1. Notificação push → Link direto
2. Email de lembrete → Link direto
3. URL manual: /athlete/wellness-pre/{sessionId}
4. Link no WellnessPostForm: "Preencher Pré primeiro"
```

**Componentes renderizados:**
- WellnessPreForm.tsx → Sliders + presets
- Countdown timer (deadline 2h antes)
- Botões preset (💪 Descansado, 😊 Normal, etc)

---

### ✅ **Página: Wellness Pós-Treino (Atleta)**
**Rota:** `/athlete/wellness-post/{sessionId}`

**Navegação:**
```
❌ NÃO HÁ LINK NA SIDEBAR (acesso via notificação ou link direto)

Formas de acesso:
1. Notificação push → Link direto (24h após treino)
2. Email de lembrete → Link direto
3. URL manual: /athlete/wellness-post/{sessionId}
```

**Componentes renderizados:**
- WellnessPostForm.tsx → RPE + recovery sliders
- Card azul: Carga interna calculada automaticamente
- Badge de progresso mensal

---

### ✅ **Página: Analytics**
**Rota:** `/analytics`

**Navegação:**
```
❌ NÃO HÁ LINK NA SIDEBAR ATUALMENTE

Formas de acesso:
1. URL manual: /analytics
2. Link direto de outras páginas (se existir)
```

**Componentes renderizados:**
- 8 cards de resumo (métricas agregadas)
- `WeeklyLoadChart.tsx` → Gráfico linha temporal
- `DeviationAlerts.tsx` → Lista de desvios
- `WellnessResponseChart.tsx` → Taxa de resposta

---

## **4. PROBLEMAS DE NAVEGAÇÃO IDENTIFICADOS**

### ❌ **Páginas sem link na Sidebar:**

| Página | Rota | Status |
|--------|------|--------|
| Wellness Pré/Pós | `/athlete/wellness-pre/{id}` | ⚠️ Sem link (acesso via notificação) |
| Analytics | `/analytics` | ❌ **Sem link na sidebar** |
| Exercise Bank (protected) | `/training/exercise-bank` | ⚠️ Duplicado com `/training/banco` |

### ❌ **Páginas descritas mas não implementadas:**

| Página Planejada | Rota Esperada | Precisa Criar |
|------------------|---------------|---------------|
| Dashboard Training | `/training/dashboard` | ✅ Sim |
| Lista Wellness Atleta | `/athlete/wellness` | ✅ Sim |
| Alertas e Sugestões | `/training/alertas` | ✅ Sim |
| Rankings Wellness | `/training/rankings-wellness` | ✅ Sim |
| Perfil Atleta | `/athlete/profile` | ✅ Sim |
| Top 5 Performers | `/teams/{id}/top-performers` | ✅ Sim |

---

## **5. COMO ADICIONAR NA SIDEBAR**

### **Exemplo 1: Adicionar Analytics na Sidebar**

Editar [ProfessionalSidebar.tsx](c:\HB TRACK\Hb Track - Fronted\src\components\Layout\ProfessionalSidebar.tsx):

```tsx
// Linha ~85 - Adicionar no submenu de Treinos:
const treinosSubmenu = [
  { name: 'Agenda Semanal', href: '/training/agenda', icon: CalendarDays },
  { name: 'Planejamento', href: '/training/planejamento', icon: ClipboardList },
  { name: 'Banco de Exercícios', href: '/training/banco', icon: ListChecks },
  { name: 'Avaliações', href: '/training/avaliacoes', icon: Target },
  { name: 'Presenças', href: '/training/presencas', icon: UserCheck },
  { name: 'Analytics', href: '/analytics', icon: Activity }, // ✅ ADICIONAR
];
```

### **Exemplo 2: Adicionar Menu Wellness para Atleta**

```tsx
// Se role === 'atleta', adicionar seção especial:
const atletaMenu = [
  { name: 'Meu Wellness', href: '/athlete/wellness', icon: Heart },
  { name: 'Meu Perfil', href: '/athlete/profile', icon: UserCircle },
];

// No JSX da sidebar:
{user?.role === 'atleta' && (
  <>
    <SidebarSection title="Meu Desempenho" isCollapsed={isCollapsed} />
    <SidebarSubmenu
      name="Wellness"
      icon={Heart}
      items={atletaMenu}
      isCollapsed={isCollapsed}
    />
  </>
)}
```

---

## **6. FLUXO DE NAVEGAÇÃO IDEAL (Após Correções)**

### **Treinador/Staff:**
```
Login
↓
Sidebar → Treinos → Agenda Semanal (/training/agenda)
                  ↓
           Clica em Sessão → Modal
                           ↓
                      Tab Exercícios → Drag-and-drop
                      Tab Wellness → Grid atletas
↓
Sidebar → Treinos → Analytics (/analytics)
                  ↓
            Gráficos de carga/wellness
```

### **Atleta:**
```
Login
↓
Notificação: "Preencher Wellness Pré-Treino" (push/email)
↓
Clica no link → /athlete/wellness-pre/{id}
↓
Preenche sliders → Submit
↓
24h depois → Notificação "Preencher Pós-Treino"
↓
Clica no link → /athlete/wellness-post/{id}
↓
Preenche RPE → Submit
↓
Sidebar → Meu Wellness (/athlete/wellness) ← CRIAR
         ↓
    Ver histórico + badges
```

---

## **7. CHECKLIST DE NAVEGAÇÃO (Para Implementar)**

- [ ] Adicionar `/analytics` na sidebar de Treinos
- [ ] Criar página `/athlete/wellness` (hub de treinos pendentes)
- [ ] Adicionar menu específico para atletas na sidebar
- [ ] Criar página `/training/dashboard` (dashboard principal)
- [ ] Adicionar item "Dashboard" no submenu Treinos
- [ ] Consolidar rotas `/training/banco` e `/training/exercise-bank` (escolher uma)
- [ ] Criar breadcrumbs para navegação secundária
- [ ] Adicionar NotificationBell no TopBar com links para wellness

---

**Resumo:** As páginas **estão implementadas**, mas a **navegação está incompleta**. Faltam links na sidebar e páginas hub (dashboard, lista wellness) para conectar tudo.

---

## ✅ **VALIDAÇÃO REAL - O QUE ESTÁ NO FRONTEND**

### **1. `/training/agenda` - AGENDA SEMANAL**

**Arquivo:** [AgendaClient.tsx](c:\HB TRACK\Hb Track - Fronted\src\app\(admin)\training\agenda\AgendaClient.tsx)

**O que você VÊ na tela:**
```
┌─────────────────────────────────────────────────────┐
│ 🏐 Agenda de Treinos                    [+ Novo]   │
│ Planeje e visualize seus treinos semanais          │
├─────────────────────────────────────────────────────┤
│ [Agenda] [Planejamento] [Banco] [Avaliações]...    │
├─────────────────────────────────────────────────────┤
│                                                     │
│  SEG    TER    QUA    QUI    SEX    SAB    DOM     │
│  ┌───┐  ┌───┐  ┌───┐  ┌───┐  ┌───┐  ┌───┐  ┌───┐  │
│  │ 📅│  │ 📅│  │   │  │ 📅│  │   │  │   │  │   │  │
│  └───┘  └───┘  └───┘  └───┘  └───┘  └───┘  └───┘  │
│   ▼SessionCard aparece aqui                        │
└─────────────────────────────────────────────────────┘
```

**Componentes renderizados:**
- ✅ WeeklyAgenda.tsx - Grid semanal
- ✅ `SessionCard.tsx` - Cards de sessão
- ✅ SessionModal.tsx - Abre ao clicar em card

**Clique em SessionCard → Abre Modal com 4 TABS:**

```
┌──────────────────────────────────────────────────┐
│  Treino Técnico                          [X]     │
│  ┌─────────────────────────────────────────────┐ │
│  │ [Detalhes] [Exercícios] [Presenças] [Wellness] │
│  └─────────────────────────────────────────────┘ │
│                                                  │
│  [TAB ATIVA RENDERIZA AQUI]                     │
│                                                  │
│  ✅ Tab Detalhes: Form de edição                │
│  ✅ Tab Exercícios: SessionExerciseDropZone     │
│  ✅ Tab Presenças: AttendanceTab                │
│  ✅ Tab Wellness: WellnessStatusDashboard       │
│                                                  │
│  [Salvar] [Duplicar] [Fechar] [Deletar]         │
└──────────────────────────────────────────────────┘
```

---

### **2. `/training/banco` - BANCO DE EXERCÍCIOS (Admin)**

**Arquivo:** [BancoClient.tsx](c:\HB TRACK\Hb Track - Fronted\src\app\(admin)\training\banco\BancoClient.tsx)

**O que você VÊ:**
```
┌─────────────────────────────────────────────────────┐
│ 🏋️ Banco de Exercícios              [+ Criar]      │
├─────────────────────────────────────────────────────┤
│ 🔍 [Buscar exercícios...]                           │
│                                                     │
│ Filtros:                                            │
│ [ ] Técnico  [ ] Tático  [ ] Físico  [ ] Regen.    │
│ [ ] Favoritos                                       │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐│
│  │ Aquecimento │  │ Passes em   │  │ Ataque      ││
│  │ Dinâmico    │  │ Movimento   │  │ Posicional  ││
│  │ ⭐ 15min    │  │   20min     │  │ ⭐ 25min    ││
│  │ 🏷️ Físico   │  │ 🏷️ Técnico  │  │ 🏷️ Tático   ││
│  └─────────────┘  └─────────────┘  └─────────────┘│
│                                                     │
│  [1] [2] [3] ... [10]                              │
└─────────────────────────────────────────────────────┘
```

**⚠️ IMPORTANTE:** Este componente usa **MOCK DATA** (dados fake):
```tsx
const MOCK_EXERCISES = [
  { id: '1', name: 'Aquecimento Dinâmico', ... },
  { id: '2', name: 'Passes em Movimento', ... },
  // ... 8 exercícios hardcoded
];
```

**❌ NÃO conecta com backend real ainda**

---

### **3. `/training/exercise-bank` - BANCO DE EXERCÍCIOS (Protected)**

**Arquivo:** [exercise-bank/page.tsx](c:\HB TRACK\Hb Track - Fronted\src\app\(protected)\training\exercise-bank\page.tsx)

**O que você VÊ:**
```
┌─────────────────────────────────────────────────────┐
│ Banco de Exercícios            [Limpar Filtros]    │
│ 156 exercícios disponíveis                          │
├─────────────────────────────────────────────────────┤
│ Sidebar (1/4)       │   Grid (3/4)                 │
│ ─────────────────── │ ──────────────────────────── │
│ 🔍 Buscar           │  ┌──────┐ ┌──────┐ ┌──────┐ │
│ [...............]   │  │ Card │ │ Card │ │ Card │ │
│                     │  │ ⭐   │ │      │ │ ⭐   │ │
│ 📂 Tags             │  └──────┘ └──────┘ └──────┘ │
│ ▼ Tático            │                               │
│   ☑️ Ataque         │  ┌──────┐ ┌──────┐ ┌──────┐ │
│   ☐ Defesa          │  │ Card │ │ Card │ │ Card │ │
│ ▼ Físico            │  └──────┘ └──────┘ └──────┘ │
│   ☐ Velocidade      │                               │
│                     │  [1] [2] [3] ... [13]         │
│ 📁 Categoria        │                               │
│ [Todas ▼]           │                               │
│                     │                               │
│ ⭐ Favoritos        │                               │
│ [ ] Apenas favoritos│                               │
└─────────────────────────────────────────────────────┘
```

**✅ CONECTA COM BACKEND:**
- Hook `useExerciseFilters()` → chama API real
- Dados vêm de `/api/v1/exercises`
- Tags hierárquicas vêm de `/api/v1/exercise-tags`

**Componentes:**
- ✅ `ExerciseCard.tsx` - Cards responsivos
- ✅ `DraggableExerciseCard.tsx` - Wrapper drag-and-drop
- ✅ `VirtualizedExerciseGrid.tsx` - Se >100 exercícios
- ✅ `TagFilter.tsx` - Tree view hierárquica
- ✅ `ExerciseModal.tsx` - Modal de detalhes

**⚠️ ATENÇÃO:** Você tem **2 rotas DIFERENTES**:
- `/training/banco` → Mock data (admin)
- `/training/exercise-bank` → API real (protected)

**RECOMENDAÇÃO:** Deletar `/training/banco` e usar apenas `/training/exercise-bank`

---

### **4. `/analytics` - DASHBOARD ANALYTICS**

**Arquivo:** [analytics/client.tsx](c:\HB TRACK\Hb Track - Fronted\src\app\(protected)\analytics\client.tsx)

**O que você VÊ:**
```
┌─────────────────────────────────────────────────────┐
│ 📊 Analytics Dashboard                              │
│ [Team: Sub-16 Masculino ▼] [Período: 3 meses ▼]   │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────┐│
│  │ 45       │ │ 3,450    │ │ 87%      │ │ 12     ││
│  │ Sessões  │ │ Carga    │ │ Taxa     │ │ Atletas││
│  └──────────┘ └──────────┘ └──────────┘ └────────┘│
│                                                     │
│  📈 Carga Semanal (4 semanas)                      │
│  ┌─────────────────────────────────────────────┐  │
│  │ [Gráfico de linha com threshold vermelho]  │  │
│  └─────────────────────────────────────────────┘  │
│                                                     │
│  ⚠️ Alertas de Desvio                              │
│  ┌─────────────────────────────────────────────┐  │
│  │ • Ana Silva - Sobrecarga 130%              │  │
│  │ • João Santos - RPE alto 3 sessões         │  │
│  └─────────────────────────────────────────────┘  │
│                                                     │
│  💚 Taxa de Resposta Wellness                      │
│  ┌─────────────────────────────────────────────┐  │
│  │ [Gráfico área com meta 80%]                │  │
│  └─────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

**✅ CONECTA COM BACKEND:**
- 3 queries React Query:
  - `getTeamSummary()` → 8 cards de métricas
  - `getWeeklyLoad()` → Gráfico temporal
  - `getDeviationAnalysis()` → Lista de alertas

**Componentes:**
- ✅ `WeeklyLoadChart.tsx` - Recharts LineChart
- ✅ `DeviationAlerts.tsx` - Lista com badges
- ✅ `WellnessResponseChart.tsx` - AreaChart

**⚠️ PROBLEMA:** Seletor de team usa `const teamId = 'TEAM_UUID_AQUI'` (mock)
- Precisa integrar com `TeamSeasonContext` real

---

### **5. `/athlete/wellness-pre/{id}` - WELLNESS PRÉ-TREINO**

**Arquivo:** [WellnessPreClient.tsx](c:\HB TRACK\Hb Track - Fronted\src\app\(protected)\athlete\wellness-pre\[sessionId]\WellnessPreClient.tsx)

**O que você VÊ:**
```
┌─────────────────────────────────────────────────────┐
│ [← Voltar]                                          │
├─────────────────────────────────────────────────────┤
│ Wellness Pré-Treino                                 │
│                                                     │
│  ┌─────────────────────────────────────────────┐  │
│  │ 📅 Treino Técnico                           │  │
│  │ 🕐 Hoje, 18:00 (90 min)                    │  │
│  │ 🎯 Trabalho de técnica individual          │  │
│  │                                             │  │
│  │ ⏰ Tempo restante: 2h 15min                 │  │
│  └─────────────────────────────────────────────┘  │
│                                                     │
│  Presets Rápidos:                                  │
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐             │
│  │ 💪   │ │ 😊   │ │ 😓   │ │ 😴   │             │
│  │ Muito│ │Normal│ │Cansado│ │Muito │             │
│  │ Bem  │ │      │ │      │ │Cansado│             │
│  └──────┘ └──────┘ └──────┘ └──────┘             │
│                                                     │
│  Sliders (0-10):                                   │
│  ────────────────────────────────────────────────  │
│  😴 Qualidade do Sono:        [========] 8        │
│  ⚡ Fadiga Muscular:           [====    ] 4        │
│  🧠 Estresse Mental:           [==      ] 2        │
│  💪 Dor Muscular:              [===     ] 3        │
│  😊 Humor Geral:               [=========] 9       │
│  🎯 Prontidão Física:          [=======  ] 7       │
│                                                     │
│  📝 Observações (opcional):                        │
│  [..........................................]     │
│                                                     │
│  [Enviar Wellness]                                 │
└─────────────────────────────────────────────────────┘
```

**Componentes:**
- ✅ WellnessPreForm.tsx - Form completo
- ✅ `Slider.tsx` - Sliders 0-10 com cores
- ✅ Countdown timer
- ✅ 4 botões preset

**⚠️ DADOS MOCKADOS:**
```tsx
// TODO: Fetch session info from API
setSession({
  id: sessionId,
  session_type: 'Treino Técnico',
  session_at: new Date(...).toISOString(), // Mock
  ...
});
```

**❌ NÃO conecta com backend para buscar sessão**
**❌ NÃO conecta com backend para submeter wellness**

---

### **6. `/athlete/wellness-post/{id}` - WELLNESS PÓS-TREINO**

**Similar ao wellness-pre, com:**
- ✅ RPE Slider (0-10) com escala Borg
- ✅ Card azul: Carga Interna calculada (RPE × minutos)
- ✅ 3 recovery sliders (Fadiga Após, Humor, Dor)
- ⚠️ Dados mockados (sem conexão backend)

---

## 🚨 **PROBLEMAS IDENTIFICADOS**

### **1. Dados Mockados vs API Real**

| Página | Backend Conectado | Status |
|--------|-------------------|--------|
| `/training/exercise-bank` | ✅ SIM | Funciona com API |
| `/training/banco` | ❌ NÃO | Mock hardcoded |
| `/analytics` | ⚠️ PARCIAL | API funciona, mas teamId=mock |
| `/athlete/wellness-pre` | ❌ NÃO | Mock data |
| `/athlete/wellness-post` | ❌ NÃO | Mock data |
| `/training/agenda` | ⚠️ DEPENDE | Se backend auth OK, funciona |

### **2. Rotas Duplicadas**

- `/training/banco` (admin, mock) ❌
- `/training/exercise-bank` (protected, API real) ✅

**Solução:** Deletar `/training/banco` ou refatorar para usar mesma API

### **3. Navegação Sidebar**

- ✅ `/training/agenda` - Link existe
- ✅ `/training/banco` - Link existe
- ❌ `/training/exercise-bank` - **SEM LINK NA SIDEBAR**
- ❌ `/analytics` - **SEM LINK NA SIDEBAR**
- ❌ `/athlete/wellness-pre` - Acesso apenas via URL direta

---

## ✅ **RESUMO: O QUE FUNCIONA DE VERDADE**

| Funcionalidade | Status Real |
|----------------|-------------|
| **Agenda Semanal** | ✅ Completa (se backend auth OK) |
| **SessionModal 4 tabs** | ✅ Renderiza (exercícios/presenças/wellness) |
| **Drag-and-drop exercícios** | ✅ Implementado (SessionExerciseDropZone) |
| **Banco exercícios (protected)** | ✅ API real, filtros, paginação |
| **Analytics Dashboard** | ⚠️ Layout OK, mas teamId mock |
| **Wellness Pré/Pós** | ⚠️ Layout OK, mas sem API integration |

---

**Quer que eu corrija algum desses problemas específicos?** Por exemplo:
1. Conectar wellness-pre/post com backend real
2. Adicionar `/analytics` na sidebar
3. Consolidar as 2 rotas de exercícios
4. Integrar teamId real no analytics


## 📋 **PLANO: Consolidar Rotas e Adicionar Analytics**

---

### **PASSO 1: Atualizar Sidebar (ProfessionalSidebar.tsx)**

**Arquivo:** [ProfessionalSidebar.tsx](c:\HB TRACK\Hb Track - Fronted\src\components\Layout\ProfessionalSidebar.tsx)

**Linha 80-86** - Substituir:

```tsx
// ANTES:
const treinosSubmenu = [
  { name: 'Agenda Semanal', href: '/training/agenda', icon: CalendarDays, tooltip: 'Visão semanal dos treinos' },
  { name: 'Planejamento', href: '/training/planejamento', icon: ClipboardList, tooltip: 'Ciclos e microciclos' },
  { name: 'Banco de Exercícios', href: '/training/banco', icon: ListChecks, tooltip: 'Biblioteca de exercícios' },
  { name: 'Avaliações', href: '/training/avaliacoes', icon: Target, tooltip: 'Métricas de desempenho' },
  { name: 'Presenças', href: '/training/presencas', icon: UserCheck, tooltip: 'Controle de frequência' },
];

// DEPOIS:
const treinosSubmenu = [
  { name: 'Agenda Semanal', href: '/training/agenda', icon: CalendarDays, tooltip: 'Visão semanal dos treinos' },
  { name: 'Planejamento', href: '/training/planejamento', icon: ClipboardList, tooltip: 'Ciclos e microciclos' },
  { name: 'Banco de Exercícios', href: '/training/exercise-bank', icon: ListChecks, tooltip: 'Biblioteca de exercícios' },
  { name: 'Avaliações', href: '/training/avaliacoes', icon: Target, tooltip: 'Métricas de desempenho' },
  { name: 'Presenças', href: '/training/presencas', icon: UserCheck, tooltip: 'Controle de frequência' },
  { name: 'Analytics', href: '/analytics', icon: Activity, tooltip: 'Análise de desempenho e métricas' },
];
```

**Mudanças:**
- ✅ `/training/banco` → `/training/exercise-bank` (API real)
- ✅ Adiciona item "Analytics" com ícone `Activity` (já importado no arquivo)

---

### **PASSO 2: Deletar Rota Admin /training/banco**

**Arquivos para DELETAR:**

1. **`c:\HB TRACK\Hb Track - Fronted\src\app\(admin)\training\banco\page.tsx`**
   - Remove wrapper de página

2. **`c:\HB TRACK\Hb Track - Fronted\src\app\(admin)\training\banco\BancoClient.tsx`**
   - Remove componente com mock data (352 linhas)

**Comando PowerShell:**
```powershell
Remove-Item "c:\HB TRACK\Hb Track - Fronted\src\app\(admin)\training\banco" -Recurse -Force
```

---

### **PASSO 3: Validar Rota Exercise Bank Existente**

**Verificar que está funcionando:**

[exercise-bank/page.tsx](c:\HB TRACK\Hb Track - Fronted\src\app\(protected)\training\exercise-bank\page.tsx) ✅

**Features confirmadas:**
- ✅ Hook `useExerciseFilters()` conecta com backend
- ✅ Grid responsivo (1-3 colunas)
- ✅ `DraggableExerciseCard` para drag-and-drop
- ✅ `VirtualizedExerciseGrid` para >100 itens
- ✅ `TagFilter` hierárquico
- ✅ Paginação com prefetch
- ✅ Favoritos com optimistic updates

**Nenhuma mudança necessária nesta rota.**

---

### **PASSO 4: Integrar TeamId Real no Analytics**

**Arquivo:** [analytics/client.tsx](c:\HB TRACK\Hb Track - Fronted\src\app\(protected)\analytics\client.tsx)

**Linha ~42** - Substituir:

```tsx
// ANTES:
const [selectedTeamId, setSelectedTeamId] = useState<string>('')
// ...
const teamId = selectedTeamId || 'TEAM_UUID_AQUI'

// DEPOIS:
import { useTeamSeasonOptional } from '@/context/TeamSeasonContext';

export default function AnalyticsDashboardClient() {
  const teamSeasonContext = useTeamSeasonOptional();
  const activeTeam = teamSeasonContext?.selectedTeam;
  
  const [dateRange, setDateRange] = useState<DateRange>(getCurrentMonthRange());
  const [weeksToShow, setWeeksToShow] = useState<number>(4);

  // Usar team ID real do contexto
  const teamId = activeTeam?.id || '';
```

**Adicionar fallback UI se sem team:**

```tsx
// Após line ~150, antes dos queries:
if (!activeTeam) {
  return (
    <div className="min-h-screen bg-slate-50 dark:bg-[#0a0a0a] p-8">
      <div className="max-w-2xl mx-auto text-center">
        <Activity className="w-16 h-16 mx-auto text-slate-300 mb-4" />
        <h2 className="text-2xl font-bold text-slate-900 dark:text-white mb-2">
          Selecione uma equipe
        </h2>
        <p className="text-slate-600 dark:text-slate-400">
          Use o seletor no cabeçalho para escolher uma equipe e visualizar as métricas.
        </p>
      </div>
    </div>
  );
}
```

---

## 📊 **RESULTADO ESPERADO**

### **Sidebar depois das mudanças:**

```
┌───────────────────────────┐
│ HB Track                  │
├───────────────────────────┤
│ 🏠 Início                 │
│ 📊 Dashboard              │
├───────────────────────────┤
│ ▼ Treinos                 │
│   📅 Agenda Semanal       │
│   📋 Planejamento         │
│   📚 Banco de Exercícios  ← Agora aponta para /training/exercise-bank
│   🎯 Avaliações           │
│   ✅ Presenças            │
│   📊 Analytics           ← NOVO ITEM ADICIONADO
├───────────────────────────┤
│ ▼ Jogos                   │
│   ...                     │
└───────────────────────────┘
```

### **Navegação Completa:**

1. **Usuário clica "Banco de Exercícios"**
   - Redireciona para `/training/exercise-bank`
   - Carrega dados da API real
   - Mostra filtros + grid responsivo
   - Drag-and-drop funciona

2. **Usuário clica "Analytics"**
   - Redireciona para `/analytics`
   - Se tem team selecionada → mostra dashboard
   - Se não tem team → mostra mensagem "Selecione uma equipe"
   - Carrega 3 queries:
     - Team summary (8 cards)
     - Weekly load (gráfico)
     - Deviation analysis (alertas)

---

## ✅ **CHECKLIST DE VALIDAÇÃO**

Após fazer as mudanças, teste:

- [ ] Sidebar renderiza item "Analytics" no submenu Treinos
- [ ] Clicar "Banco de Exercícios" → abre `/training/exercise-bank` (não `/training/banco`)
- [ ] Clicar "Analytics" → abre `/analytics`
- [ ] Analytics mostra "Selecione uma equipe" se contexto vazio
- [ ] Analytics carrega dados quando equipe ativa
- [ ] Banco de exercícios mostra dados reais da API
- [ ] Drag-and-drop funciona do banco → SessionModal
- [ ] Rota `/training/banco` retorna 404 (deletada)

---

## 🚀 **COMANDOS PARA EXECUTAR**

```bash
cd "c:\HB TRACK\Hb Track - Fronted"

# 1. Deletar rota antiga
Remove-Item "src\app\(admin)\training\banco" -Recurse -Force

# 2. Editar ProfessionalSidebar.tsx (manual)
code "src\components\Layout\ProfessionalSidebar.tsx"
# Aplicar mudanças da linha 80-86

# 3. Editar analytics/client.tsx (manual)
code "src\app\(protected)\analytics\client.tsx"
# Adicionar import useTeamSeasonOptional
# Substituir teamId mock por activeTeam?.id

# 4. Testar
npm run dev
# Navegar até /training → clicar Banco de Exercícios
# Navegar até /analytics
```

---


