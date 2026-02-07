<!-- STATUS: NEEDS_REVIEW -->

# Plano de Migração: Teams → Teams-v2

## Análise Completa

### 1. Situação Atual das Rotas

**Rotas Existentes:**
- [/teams/page.tsx](src/app/(admin)/teams/page.tsx) - Rota atual ativa
- [/admin/teams/page.tsx](src/app/(admin)/admin/teams/page.tsx) - Rota duplicada (CONFLITO)
- [/teams-v2/page.tsx](src/app/(admin)/teams-v2/page.tsx) - Nova implementação

**Sidebar Atual:**
- [ProfessionalSidebar.tsx:40](src/components/Layout/ProfessionalSidebar.tsx) → Link aponta para `/teams`

---

### 2. Comparação: Teams vs Teams-v2

#### **Arquitetura**

| Aspecto | `/teams` (Antigo) | `/teams-v2` (Novo) |
|---------|-------------------|-------------------|
| **API** | ✅ Integrado via `teamsService.list()` | ❌ Usa `MOCK_TEAMS` estático |
| **Layout** | Two-column com lista + detalhe | ViewState pattern (Dashboard/TeamDetail) |
| **Componente** | `TeamsManagementAPI` | `Dashboard` + `TeamDetail` |
| **Tipos** | [/lib/api/teams.ts](src/lib/api/teams.ts) | [/types/teams-v2.ts](src/types/teams-v2.ts) |
| **Auth** | ✅ Validação de sessão | ❌ Sem validação |

#### **Diferenças de Tipos**

**Team Type (Antigo - /lib/api/teams.ts:3-19)**
```typescript
interface Team {
  id: string;
  name: string;
  organization_id: string;
  category_id: number;
  gender: TeamGender;
  is_our_team: boolean;
  season_id?: string;
  // ... mais campos do backend
}
```

**Team Type (Novo - /types/teams-v2.ts:5-18)**
```typescript
interface Team {
  id: string;
  name: string;
  code: string;
  role: string;
  lastActivity: string;
  activityTime: string;
  status: 'active' | 'archived';
  initial: string;
  // ... campos diferentes
}
```

#### **Componentes Teams-v2**

Localizados em `/components/teams-v2/`:
- [Dashboard.tsx](src/components/teams-v2/Dashboard.tsx) - Lista com filtros e ações
- [TeamDetail.tsx](src/components/teams-v2/TeamDetail.tsx) - Visualização detalhada com tabs
- `CreateTeamModal.tsx` - Criação de equipes
- `MembersTab.tsx` - Gerenciamento de membros
- `TrainingsTab.tsx` - Treinos
- `StatsTab.tsx` - Estatísticas
- `OverviewTab.tsx` - Visão geral
- `SettingsTab.tsx` - Configurações

---

### 3. Arquivos a Remover

**CRÍTICO - Rota Duplicada:**
- ❌ [/admin/teams/page.tsx](src/app/(admin)/admin/teams/page.tsx)
- ❌ [/admin/teams/360/page.tsx](src/app/(admin)/admin/teams/360/page.tsx) (se existir)

**APÓS migração completa:**
- ⏳ [/teams/page.tsx](src/app/(admin)/teams/page.tsx) (antiga implementação)
- ⏳ `TeamsManagementAPI` component (se não usado em outro lugar)

**NÃO REMOVER:**
- ✅ [/lib/api/teams.ts](src/lib/api/teams.ts) - Serviço API necessário
- ✅ Pasta `/components/teams-v2/` - Nova implementação

---

## Plano de Migração: Passo a Passo

### **FASE 1: Preparação e Backup**

#### 1.1 Criar Backup
```bash
# Backup dos arquivos antigos
mkdir -p backup/teams-migration
cp -r src/app/(admin)/teams backup/teams-migration/
cp -r src/app/(admin)/admin/teams backup/teams-migration/
cp src/components/Layout/ProfessionalSidebar.tsx backup/teams-migration/
```

#### 1.2 Verificar Dependências
- Conferir se `TeamsManagementAPI` é usado em outros lugares
- Verificar imports de `/lib/api/teams.ts` no projeto
- Validar uso de `CreateTeamModal` nos dois sistemas

---

### **FASE 2: Remover Rotas Duplicadas**

#### 2.1 Remover `/admin/teams`
```bash
# Remover rota duplicada
rm -rf src/app/(admin)/admin/teams
```

**Resultado:** Apenas `/teams` e `/teams-v2` coexistem temporariamente.

---

### **FASE 3: Integrar API Real no Teams-v2**

#### 3.1 Mapear Tipos
Criar adapter em `/lib/adapters/teams-v2-adapter.ts`:
```typescript
import { Team as ApiTeam } from '@/lib/api/teams';
import { Team as V2Team } from '@/types/teams-v2';

export function mapApiTeamToV2(apiTeam: ApiTeam): V2Team {
  return {
    id: apiTeam.id,
    name: apiTeam.name,
    code: apiTeam.id.substring(0, 10).toUpperCase(),
    role: 'Treinador', // determinar role baseado em auth
    lastActivity: 'Sem atividade recente',
    activityTime: apiTeam.updated_at || 'Não disponível',
    status: apiTeam.is_active ? 'active' : 'archived',
    initial: apiTeam.name.charAt(0).toUpperCase(),
    category: getCategoryLabel(apiTeam.category_id),
    gender: apiTeam.gender === 'masculino' ? 'Masculino' : 'Feminino',
    club: apiTeam.organization_name || apiTeam.organization_id,
    season: apiTeam.season_id
  };
}
```

#### 3.2 Substituir MOCK_TEAMS no Dashboard
Atualizar [Dashboard.tsx:29](src/components/teams-v2/Dashboard.tsx):
```typescript
// ANTES (linha 29)
const [teams, setTeams] = useState<Team[]>(MOCK_TEAMS);

// DEPOIS
const [teams, setTeams] = useState<Team[]>([]);
const [loading, setLoading] = useState(true);

useEffect(() => {
  async function loadTeams() {
    setLoading(true);
    const response = await teamsService.list();
    const mappedTeams = response.items.map(mapApiTeamToV2);
    setTeams(mappedTeams);
    setLoading(false);
  }
  loadTeams();
}, []);
```

#### 3.3 Adicionar Autenticação
Atualizar [/teams-v2/page.tsx:9](src/app/(admin)/teams-v2/page.tsx):
```typescript
import { getSession } from '@/lib/auth/actions';
import { redirect } from 'next/navigation';

export default async function TeamsV2Page() {
  const session = await getSession();

  if (!session) {
    redirect('/signin');
  }

  // ... resto do código
}
```

---

### **FASE 4: Atualizar Navegação**

#### 4.1 Atualizar Sidebar
Editar [ProfessionalSidebar.tsx:40](src/components/Layout/ProfessionalSidebar.tsx):
```typescript
// ANTES
{ name: 'Equipes', href: '/teams', icon: UsersRound },

// DEPOIS
{ name: 'Equipes', href: '/teams-v2', icon: UsersRound },
```

---

### **FASE 5: Deprecar Rota Antiga**

#### 5.1 Mover `/teams` para Backup
```bash
# Mover implementação antiga
mv src/app/(admin)/teams src/app/(admin)/_teams-deprecated
```

**Resultado:** Rota `/teams` deixa de existir, evitando acessos acidentais.

---

### **FASE 6: Renomear Teams-v2 → Teams**

#### 6.1 Renomear Pasta
```bash
# Renomear pasta da rota
mv src/app/(admin)/teams-v2 src/app/(admin)/teams
```

#### 6.2 Atualizar Imports
Buscar e substituir no projeto:
- `from '@/types/teams-v2'` → `from '@/types/teams'`
- `from '@/constants/teams-v2'` → `from '@/constants/teams'`
- `from '@/components/teams-v2/` → `from '@/components/teams/`

#### 6.3 Renomear Arquivos de Tipos e Constants
```bash
mv src/types/teams-v2.ts src/types/teams-new.ts
mv src/constants/teams-v2.ts src/constants/teams-new.ts
mv src/components/teams-v2 src/components/teams
```

#### 6.4 Atualizar Sidebar (final)
```typescript
// Já apontará para /teams automaticamente após rename
{ name: 'Equipes', href: '/teams', icon: UsersRound },
```

---

### **FASE 7: Testar e Validar**

#### 7.1 Checklist de Testes
- [ ] Rota `/teams` carrega corretamente
- [ ] API retorna dados reais (não mock)
- [ ] Autenticação bloqueia acesso não autorizado
- [ ] Filtros funcionam (por role, categoria, etc)
- [ ] Criação de nova equipe funciona
- [ ] Visualização de detalhes funciona
- [ ] Tabs (Members, Trainings, Stats, Settings) funcionam
- [ ] Ações (Sair, Arquivar, Editar) funcionam
- [ ] Dark mode funciona
- [ ] Responsivo funciona

#### 7.2 Validar Logs
```bash
# Verificar console para erros
npm run dev
# Acessar: http://localhost:3000/teams
```

---

### **FASE 8: Limpeza Final**

#### 8.1 Remover Arquivos Obsoletos
```bash
# Remover pasta deprecada
rm -rf src/app/(admin)/_teams-deprecated

# Remover constantes mock (se não mais necessário)
# Manter apenas se usar em testes
rm src/constants/teams-new.ts # apenas se não usado
```

#### 8.2 Atualizar Documentação
- Atualizar README com nova estrutura
- Documentar mudanças no CHANGELOG

---

## Riscos e Mitigação

| Risco | Mitigação |
|-------|-----------|
| **Quebra de API** | Validar campos retornados pelo backend antes de mapear |
| **Perda de Funcionalidades** | Comparar features antigas vs novas antes de remover |
| **Usuários com Links Antigos** | Criar redirect de `/admin/teams` → `/teams` (302) |
| **Tipos Incompatíveis** | Usar adapter para traduzir tipos |
| **Dados Mock em Produção** | CRÍTICO - Validar que API está integrada antes de deploy |

---

## Checklist Final de Configuração

### Antes de Iniciar
- [ ] Backup completo realizado
- [ ] Revisão de dependências concluída
- [ ] Plano aprovado pela equipe

### Durante Migração
- [ ] Rota `/admin/teams` removida
- [ ] API integrada ao teams-v2
- [ ] Adapter de tipos criado
- [ ] Autenticação adicionada
- [ ] Sidebar atualizada
- [ ] Rotas renomeadas

### Após Migração
- [ ] Todos os testes passaram
- [ ] Sem erros no console
- [ ] Performance validada
- [ ] Documentação atualizada
- [ ] Deploy realizado com sucesso

---

## Notas Importantes

1. **NÃO executar em produção sem testes completos**
2. **Validar que backend retorna dados compatíveis com o adapter**
3. **Considerar migração gradual** (feature flag se necessário)
4. **Comunicar mudança aos usuários** (se URLs mudarem)
5. **Manter backup por 30 dias** após migração bem-sucedida

---

## Contatos e Suporte

- **Responsável Técnico:** [Definir]
- **Data Estimada:** [Definir]
- **Ambiente de Teste:** [Definir URL]
- **Rollback Plan:** Restaurar de `backup/teams-migration/`
