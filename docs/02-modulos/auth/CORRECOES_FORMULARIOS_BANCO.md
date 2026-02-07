<!-- STATUS: DEPRECATED | razao: historico de implementacao, nao referencia canonica -->

# Correções dos Formulários Específicos - Conformidade com Banco de Dados

**Data**: 2025-01-XX  
**Status**: ✅ CONCLUÍDO

## 🎯 Objetivo

Ajustar todos os formulários específicos de boas-vindas para seguir **REGRA DE OURO**:
> **Se o sistema já consegue responder o que é necessário para o cadastro, os formulários não devem pedir novamente.**

Além disso, remover todos os campos que **NÃO EXISTEM** no banco de dados.

---

## 📋 Análise do Problema

### Campos Inexistentes no Banco

A análise do schema PostgreSQL revelou que os seguintes campos **NÃO EXISTEM** na tabela `athletes`:

| Campo                | Status     | Problema                                     |
|----------------------|------------|----------------------------------------------|
| `height`             | ❌ Não existe | AthleteProfileForm estava pedindo           |
| `weight`             | ❌ Não existe | AthleteProfileForm estava pedindo           |
| `laterality`         | ❌ Não existe | AthleteProfileForm estava pedindo           |
| `defensive_positions`| ❌ Não existe | AthleteProfileForm estava pedindo (array)   |

**Tabela `defensive_positions`**:
- ✅ Existe no schema
- ❌ Contém 0 registros (vazia)
- ⚠️ Não pode ser usada para popular dropdowns

**Tabela `athletes` - Campos REAIS**:
```sql
person_id                   | bigint              | NOT NULL
athlete_name                | character varying   | NOT NULL
birth_date                  | date                | NOT NULL
state                       | character varying   | default 'ativa'
main_defensive_position_id  | bigint              | nullable
secondary_defensive_position_id | bigint          | nullable
```

---

## 🔧 Correções Implementadas

### 1. **AthleteProfileForm.tsx**

#### Campos REMOVIDOS:
```typescript
// ❌ REMOVIDOS
height: string
weight: string
laterality: string
defensive_positions: string[]
```

#### Campos MANTIDOS:
```typescript
// ✅ CORRETO - Somente campos que existem no banco
full_name: string      // → person.full_name
phone: string          // → person_contacts.contact_value
birth_date: string     // → athletes.birth_date (NOT NULL)
gender: string         // → person.gender
```

#### Interface Atualizada:
```typescript
export interface AthleteFormData {
  full_name: string
  phone: string
  birth_date: string    // OBRIGATÓRIO para atletas
  gender: string
}
```

#### UI Simplificada:
- Removida seção "Informações do Atleta" com 80+ linhas
- Adicionada nota explicativa:
  > "Dados adicionais do atleta (altura, peso, posições) serão preenchidos posteriormente na ficha completa."

#### Validação:
- `birth_date` agora é **required** (NOT NULL no banco)
- Todos os outros campos são opcionais

---

### 2. **Backend auth.py**

#### Schema WelcomeCompleteRequest - Campos REMOVIDOS:
```python
# ❌ REMOVIDOS
height: Optional[str] = None
weight: Optional[str] = None
laterality: Optional[str] = None
defensive_positions: Optional[List[str]] = None
```

#### Schema Atual (CORRETO):
```python
class WelcomeCompleteRequest(BaseModel):
    token: str
    password: str
    confirm_password: str
    full_name: str
    # Campos opcionais básicos
    phone: Optional[str] = None
    birth_date: Optional[date] = None
    gender: Optional[str] = None
    # Campos específicos de treinador
    certifications: Optional[str] = None
    specialization: Optional[str] = None
    # Campos específicos de coordenador
    area_of_expertise: Optional[str] = None
```

#### Lógica de Processamento Atualizada:

**ANTES** (70+ linhas tentando processar campos inexistentes):
```python
# Tentava criar Athlete com height, weight, laterality
# Tentava criar AthletePosition records
# Processava defensive_positions array
```

**DEPOIS** (simplificado e correto):
```python
# Processar papel de atleta - criar registro na tabela athletes se necessário
if payload.birth_date:
    athlete = db.query(Athlete).filter(
        Athlete.person_id == person.id,
        Athlete.deleted_at.is_(None)
    ).first()
    
    if not athlete:
        athlete = Athlete(
            person_id=person.id,
            athlete_name=person.full_name,  # Usar full_name como athlete_name
            birth_date=payload.birth_date,
            state='ativa'  # Default
        )
        db.add(athlete)
```

**Lógica**:
- Só cria registro `Athlete` se `birth_date` foi fornecido (NOT NULL requirement)
- Usa `person.full_name` como `athlete_name`
- Define `state='ativa'` como padrão
- Não tenta preencher campos inexistentes

---

### 3. **E2E Tests - api.ts**

#### Tipo `completeWelcomeViaAPI` - Campos REMOVIDOS:
```typescript
// ❌ REMOVIDOS do payload
height?: string
weight?: string
laterality?: string
defensive_positions?: string[]
```

#### Tipo Atual (CORRETO):
```typescript
export async function completeWelcomeViaAPI(
  request: APIRequestContext,
  payload: {
    token: string
    password: string
    confirm_password: string
    full_name: string
    phone?: string
    birth_date?: string
    gender?: string
    // Campos específicos de treinador
    certifications?: string
    specialization?: string
    // Campos específicos de coordenador
    area_of_expertise?: string
  }
): Promise<...>
```

---

### 4. **E2E Test - teams.welcome.spec.ts**

#### Teste Atualizado:

**ANTES**:
```typescript
test('formulário de atleta deve incluir campos específicos (altura, peso, posições)', ...)
// Esperava ver labels: "Altura", "Peso", "Lateralidade"
```

**DEPOIS**:
```typescript
test('formulário de atleta deve incluir campos obrigatórios (nome, data de nascimento)', ...)

// Verificar campos obrigatórios de atleta
await expect(newPage.locator('input[name="full_name"]')).toBeVisible()

// Data de nascimento é obrigatória para atletas
const birthDateLabel = newPage.locator('label:has-text("Data de Nascimento")')
await expect(birthDateLabel).toBeVisible({ timeout: 3000 })

// Nota sobre campos adicionais deve estar visível
await expect(newPage.locator('text=Dados adicionais do atleta')).toBeVisible()
```

---

## ✅ Validação dos Outros Formulários

### CoachProfileForm.tsx ✅
```typescript
interface CoachFormData {
  full_name: string      // → person.full_name
  phone: string          // → person_contacts
  birth_date: string     // → person.birth_date (opcional)
  gender: string         // → person.gender
  certifications: string // → person.metadata
  specialization: string // → person.metadata
}
```

**Status**: ✅ Correto
- Todos os campos básicos existem em `person`
- Campos específicos vão para `metadata` (JSONB)
- Nenhum campo inexistente

---

### CoordinatorProfileForm.tsx ✅
```typescript
interface CoordinatorFormData {
  full_name: string         // → person.full_name
  phone: string             // → person_contacts
  birth_date: string        // → person.birth_date (opcional)
  gender: string            // → person.gender
  area_of_expertise: string // → person.metadata
}
```

**Status**: ✅ Correto
- Todos os campos básicos existem em `person`
- Campo específico vai para `metadata` (JSONB)
- Nenhum campo inexistente

---

### GenericProfileForm.tsx ✅
```typescript
interface GenericFormData {
  full_name: string   // → person.full_name
  phone: string       // → person_contacts
  birth_date: string  // → person.birth_date (opcional)
  gender: string      // → person.gender
}
```

**Status**: ✅ Correto
- Usado para `membro` e `dirigente`
- Somente campos básicos do `person`
- Nenhum campo inexistente

---

## 📊 Resumo das Correções

### Arquivos Modificados:
1. ✅ `src/components/auth/forms/AthleteProfileForm.tsx` - 4 replacements
   - Removida interface com 4 campos inexistentes
   - Removidos useState hooks
   - Removida função togglePosition
   - Simplificada seção de UI

2. ✅ `app/api/v1/routers/auth.py` - 2 replacements
   - Removidos 4 campos do schema WelcomeCompleteRequest
   - Simplificada lógica de criação de Athlete (70+ linhas → 15 linhas)

3. ✅ `tests/e2e/helpers/api.ts` - 1 replacement
   - Removidos 4 campos do tipo completeWelcomeViaAPI

4. ✅ `tests/e2e/teams/teams.welcome.spec.ts` - 1 replacement
   - Atualizado teste de atleta para não esperar campos removidos
   - Validação focada em campos obrigatórios reais

### Arquivos Verificados (sem mudanças necessárias):
- ✅ `CoachProfileForm.tsx` - Correto
- ✅ `CoordinatorProfileForm.tsx` - Correto
- ✅ `GenericProfileForm.tsx` - Correto

---

## 🎯 Conformidade com REGRA DE OURO

### ✅ O que NÃO pedimos mais:
1. **Email** - Sistema já tem (vem do convite)
2. **Altura, Peso, Lateralidade** - Não existem no banco
3. **Posições Defensivas** - Tabela vazia, não pode popular
4. **Campos que o sistema não pode armazenar**

### ✅ O que PEDIMOS (apenas essencial):
1. **Nome Completo** - Obrigatório para todos
2. **Senha** - Obrigatório para ativar conta
3. **Data de Nascimento** - Obrigatório APENAS para atletas (NOT NULL)
4. **Telefone, Gênero** - Opcionais
5. **Campos específicos** - Apenas para treinador/coordenador (vão para metadata)

---

## 🧪 Próximos Passos

1. **Executar testes E2E**:
   ```bash
   cd "Hb Track - Fronted"
   npm run test:e2e:teams
   ```

2. **Testar fluxo completo**:
   - Criar convite para atleta
   - Receber email com token
   - Completar cadastro
   - Verificar que dados salvam corretamente no banco

3. **Validar outros papéis**:
   - Testar formulário de treinador
   - Testar formulário de coordenador
   - Testar formulário genérico (membro/dirigente)

4. **Popular tabela defensive_positions** (futuro):
   - Criar seed data com posições padrão de handebol
   - Depois adicionar campos de posição no formulário de atleta

---

## 📝 Notas Importantes

### birth_date - Validação Especial

**Regra**:
- ⚠️ Opcional em `person` table
- ✅ Obrigatório em `athletes` table (NOT NULL)

**Implementação**:
```typescript
// AthleteProfileForm.tsx
<input
  type="date"
  required  // ← Obrigatório apenas no formulário de atleta
  value={birthDate}
  onChange={(e) => setBirthDate(e.target.value)}
/>

// Outros formulários
<input
  type="date"
  // ← Não é required
  value={birthDate}
  onChange={(e) => setBirthDate(e.target.value)}
/>
```

### Metadata para Campos Específicos

Coach e Coordinator usam `person.metadata` (JSONB) para armazenar campos específicos:

```python
# Backend armazena assim:
if payload.certifications or payload.specialization:
    current_metadata = person.metadata or {}
    current_metadata.update({
        'certifications': payload.certifications,
        'specialization': payload.specialization
    })
    person.metadata = current_metadata
```

---

## ✅ Conclusão

Todos os formulários agora seguem a **REGRA DE OURO**:
- Não pedem informações que o sistema já tem
- Não pedem campos que não existem no banco
- Somente campos essenciais e armazenáveis
- Formulário de atleta focado no mínimo necessário

**Status**: ✅ Pronto para testes E2E completos
