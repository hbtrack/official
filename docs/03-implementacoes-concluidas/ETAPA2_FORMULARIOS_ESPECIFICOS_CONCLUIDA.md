<!-- STATUS: DEPRECATED | implementacao concluida -->

# ✅ Etapa 2 Concluída - Formulários Específicos por Papel

## Data: 13/01/2026 - 16:30

## Resumo Executivo

Implementados **formulários específicos** para cada papel (atleta, treinador, coordenador) no fluxo de welcome! Agora cada tipo de convite renderiza seu formulário personalizado com campos apropriados.

---

## 🎯 Implementações Realizadas

### 1. **Novos Componentes de Formulário**

#### ✅ AthleteProfileForm.tsx
- **Localização**: `Hb Track - Fronted/src/components/auth/forms/AthleteProfileForm.tsx`
- **Campos Básicos**: Nome, Telefone, Data Nascimento, Gênero
- **Campos Específicos**:
  - 🏃 Altura (cm)
  - ⚖️ Peso (kg)
  - 👋 Lateralidade (destro/canhoto/ambidestro)
  - 🎯 Posições (múltipla escolha):
    - Goleiro
    - Ponta Esquerda / Ponta Direita
    - Armador Esquerdo / Central / Direito
    - Pivô

#### ✅ CoachProfileForm.tsx
- **Localização**: `Hb Track - Fronted/src/components/auth/forms/CoachProfileForm.tsx`
- **Campos Básicos**: Nome, Telefone, Data Nascimento, Gênero
- **Campos Específicos**:
  - 📜 Certificações (textarea livre)
  - 🎓 Especialização (select):
    - Treinador Principal
    - Auxiliar Técnico
    - Preparador Físico
    - Treinador de Goleiros
    - Analista de Desempenho

#### ✅ CoordinatorProfileForm.tsx
- **Localização**: `Hb Track - Fronted/src/components/auth/forms/CoordinatorProfileForm.tsx`
- **Campos Básicos**: Nome, Telefone, Data Nascimento, Gênero
- **Campos Específicos**:
  - 📋 Área de Atuação (select):
    - Coordenação Técnica
    - Coordenação de Categorias
    - Coordenação Administrativa
    - Coordenação Esportiva
    - Coordenação Metodológica
    - Coordenação de Base

#### ✅ GenericProfileForm.tsx
- **Localização**: `Hb Track - Fronted/src/components/auth/forms/GenericProfileForm.tsx`
- **Uso**: Para papéis "membro" e "dirigente"
- **Campos**: Apenas campos básicos (nome, telefone, data nascimento, gênero)

---

### 2. **Atualização do WelcomeFlow.tsx**

#### ✅ Lógica Condicional por `invitee_kind`
```tsx
{welcomeInfo.invitee_kind === 'athlete' && <AthleteProfileForm ... />}
{welcomeInfo.invitee_kind === 'coach' && <CoachProfileForm ... />}
{welcomeInfo.invitee_kind === 'coordinator' && <CoordinatorProfileForm ... />}
{/* Fallback para membro/dirigente */}
{!welcomeInfo.invitee_kind && <GenericProfileForm ... />}
```

#### ✅ Redirecionamento Unificado
- **TODOS os usuários** agora são redirecionados para `/inicio` após cadastro
- Removida lógica de redirecionamento para `/teams/{id}`
- Consistência UX para todos os papéis

#### ✅ Handler Genérico
```tsx
const handleProfileSubmit = async (data: AthleteFormData | CoachFormData | ...) => {
  // Envia TODOS os campos do formulário para o backend
  // Backend processa apenas os campos relevantes
}
```

---

### 3. **Backend - auth.py**

#### ✅ Schema Expandido: `WelcomeCompleteRequest`
```python
class WelcomeCompleteRequest(BaseModel):
    # Campos básicos
    token: str
    password: str
    confirm_password: str
    full_name: str
    phone: Optional[str]
    birth_date: Optional[date]
    gender: Optional[str]
    
    # Campos específicos de atleta
    height: Optional[str]
    weight: Optional[str]
    laterality: Optional[str]
    defensive_positions: Optional[List[str]]
    
    # Campos específicos de treinador
    certifications: Optional[str]
    specialization: Optional[str]
    
    # Campos específicos de coordenador
    area_of_expertise: Optional[str]
```

#### ✅ Processamento de Atleta
- Cria/atualiza registro em `Athlete`
- Armazena altura, peso, lateralidade
- Cria registros em `AthletePosition` linkando com `DefensivePosition`
- Remove posições antigas antes de adicionar novas

#### ✅ Processamento de Treinador/Coordenador
- Armazena certificações em `Person.metadata`
- Armazena especialização/área de atuação em metadata
- Preparado para migração futura para tabelas específicas

---

## 📊 Mapeamento de Formulários

| invitee_kind | Formulário | Campos Extras |
|-------------|-----------|---------------|
| `athlete` | AthleteProfileForm | altura, peso, lateralidade, posições |
| `coach` / `treinador` | CoachProfileForm | certificações, especialização |
| `coordinator` / `coordenador` | CoordinatorProfileForm | área de atuação |
| `member` / `membro` | GenericProfileForm | - |
| `staff` / `dirigente` | GenericProfileForm | - |
| (null/outros) | GenericProfileForm | - |

---

## 🔄 Fluxo Completo de Cadastro

### Frontend (WelcomeFlow.tsx)

1. **Verificar Token** → `GET /auth/welcome/verify?token={token}`
   - Retorna `invitee_kind` (athlete/coach/coordinator)

2. **Passo 1: Senha** → Formulário de senha (igual para todos)

3. **Passo 2: Perfil** → Formulário específico baseado em `invitee_kind`
   - Atleta: AthleteProfileForm
   - Treinador: CoachProfileForm
   - Coordenador: CoordinatorProfileForm
   - Outros: GenericProfileForm

4. **Completar** → `POST /auth/welcome/complete`
   - Envia TODOS os campos preenchidos
   - Backend processa apenas os relevantes

5. **Sucesso** → Redireciona para `/inicio` (TODOS)

### Backend (auth.py)

1. **Validar Token** (welcome/complete)
2. **Atualizar User** (senha, status=ativo)
3. **Atualizar Person** (nome, telefone, data, gênero)
4. **Processar Campos Específicos**:
   - Se `height/weight/positions` → Criar/Atualizar `Athlete`
   - Se `certifications/specialization` → Armazenar em `Person.metadata`
   - Se `area_of_expertise` → Armazenar em `Person.metadata`
5. **Ativar TeamMembership** (pendente → ativo)
6. **Criar Sessão** (cookies JWT)
7. **Retornar Sucesso**

---

## 🔍 Testes Recomendados

### Teste 1: Convite de Atleta
1. Dirigente envia convite com `invitee_kind="athlete"`
2. Atleta clica no link de email
3. Verifica formulário com campos de altura/peso/posições
4. Preenche dados e completa cadastro
5. Verifica redirecionamento para `/inicio`
6. Valida no banco: `athletes` table tem registro
7. Valida `athlete_positions` linkadas

### Teste 2: Convite de Treinador
1. Dirigente envia convite com `invitee_kind="coach"`
2. Treinador clica no link
3. Verifica formulário com certificações/especialização
4. Completa cadastro
5. Valida redirecionamento `/inicio`
6. Valida metadata em `persons.metadata`

### Teste 3: Convite de Coordenador
1. Similar ao treinador
2. Formulário específico com área de atuação
3. Valida metadata correto

### Teste 4: Convite de Membro (Genérico)
1. Convite sem `invitee_kind` ou `invitee_kind="member"`
2. Verifica formulário genérico (sem campos extras)
3. Completa cadastro normalmente

---

## 🐛 Possíveis Melhorias Futuras

### 1. **Tabelas Específicas para Staff**
Atualmente certificações de treinador e área de coordenador ficam em `Person.metadata`. No futuro, criar:
- `coaches` table (certifications, specialization, license_number, etc.)
- `coordinators` table (area_of_expertise, department, etc.)

### 2. **Validação de Posições**
Validar no backend que as posições enviadas existem em `defensive_positions`.

### 3. **Upload de Foto**
Adicionar campo de foto de perfil no formulário (especialmente para atletas).

### 4. **Assinatura de Termos**
Checkbox "Aceito os termos de uso" antes de concluir.

### 5. **Preview de Dados**
Tela de confirmação antes do submit final.

---

## 📝 Arquivos Modificados - Etapa 2

### Frontend
| Arquivo | Tipo | Descrição |
|---------|------|-----------|
| `WelcomeFlow.tsx` | Modified | Lógica condicional de formulários |
| `forms/AthleteProfileForm.tsx` | Created | Formulário de atleta |
| `forms/CoachProfileForm.tsx` | Created | Formulário de treinador |
| `forms/CoordinatorProfileForm.tsx` | Created | Formulário de coordenador |
| `forms/GenericProfileForm.tsx` | Created | Formulário genérico |

### Backend
| Arquivo | Tipo | Descrição |
|---------|------|-----------|
| `auth.py` (linha 269-289) | Modified | Schema WelcomeCompleteRequest expandido |
| `auth.py` (linha 1560-1640) | Modified | Processamento de campos específicos |

---

## ✅ Validações Técnicas

### Frontend
- ✅ 4 componentes de formulário criados
- ✅ TypeScript interfaces exportadas
- ✅ Props consistentes entre todos os forms
- ✅ Mesma estrutura de submit/loading/error
- ✅ Dark mode suportado
- ✅ Responsivo (grid-cols-2/3 conforme necessário)

### Backend
- ✅ Schema aceita TODOS os campos
- ✅ Campos opcionais (Optional[])
- ✅ Processa apenas campos preenchidos (any([...]))
- ✅ Cria Athlete se necessário
- ✅ Atualiza posições via AthletePosition
- ✅ Metadata para coach/coordinator
- ✅ Commit único (transação atômica)

---

## 🎯 Status Geral

| Etapa | Status | Notas |
|-------|--------|-------|
| **Etapa 1 - Validar fluxo membro** | ✅ Concluída | Token, TopBar, Permissões, Status |
| **Etapa 2 - Formulários específicos** | ✅ Concluída | 4 forms criados, backend atualizado |
| **Etapa 3 - Separar MembersTab** | ⏳ Pendente | Comissão Técnica vs Atletas |

---

**Próximo Passo**: Começar Etapa 3 - Separar aba "Membros" em duas seções:
1. **Comissão Técnica**: dirigente, coordenador, treinador, membro
2. **Atletas**: atleta

**Data de Implementação**: 2026-01-13  
**Implementado por**: GitHub Copilot Agent  
**Status**: 🟢 **ETAPA 2 PRONTA PARA TESTE**
