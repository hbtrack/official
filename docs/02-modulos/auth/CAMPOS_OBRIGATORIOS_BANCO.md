<!-- STATUS: VERIFIED | evidencia: schema.sql (users, persons, athletes, org_memberships) -->

# 📊 Campos Obrigatórios no Banco de Dados - Por Papel

## Data: 13/01/2026

---

## 🎯 Resumo Executivo

Análise da estrutura do banco de dados **hb_track_e2e** para identificar campos obrigatórios (NOT NULL) para cadastro de cada tipo de membro.

---

## 🏗️ Estrutura Geral de Cadastro

### Fluxo de Criação de Usuário/Membro

```
1. Person (dados da pessoa)
   ↓
2. User (autenticação)
   ↓
3. OrgMembership (vínculo com organização + papel)
   ↓
4. TeamMembership (vínculo com equipe)
   ↓
5. [OPCIONAL] Athlete (se papel = atleta)
```

---

## 📋 1. TABELA `persons` (Dados da Pessoa)

### ✅ Campos Obrigatórios (NOT NULL)

| Campo | Tipo | Obrigatório | Observações |
|-------|------|-------------|-------------|
| `full_name` | text | ✅ SIM | Nome completo |
| `first_name` | varchar(100) | ✅ SIM | Primeiro nome |
| `last_name` | varchar(100) | ✅ SIM | Sobrenome |
| `birth_date` | date | ❌ NÃO | Data de nascimento (opcional) |
| `gender` | varchar(20) | ❌ NÃO | Gênero (opcional) |
| `nationality` | varchar(100) | ❌ NÃO | Default: 'brasileira' |

### ✅ Validações (CHECK Constraints)

```sql
gender IN ('masculino', 'feminino', 'outro', 'prefiro_nao_dizer') OR NULL
```

### 📝 Observações Importantes

1. **`full_name` é obrigatório** mas `first_name` e `last_name` também são (NOT NULL)
2. Sistema deve fazer **split do full_name** para preencher first_name e last_name
3. **birth_date NÃO é obrigatório** na tabela persons (mas pode ser para atletas)
4. **gender NÃO é obrigatório** na tabela persons

---

## 📋 2. TABELA `users` (Autenticação)

### ✅ Campos Obrigatórios (NOT NULL)

| Campo | Tipo | Obrigatório | Observações |
|-------|------|-------------|-------------|
| `person_id` | uuid | ✅ SIM | FK para persons |
| `email` | varchar(255) | ✅ SIM | Único (case-insensitive) |
| `password_hash` | text | ❌ NÃO | Pode ser NULL (convite pendente) |
| `status` | varchar(20) | ✅ SIM | Default: 'ativo' |
| `is_superadmin` | boolean | ✅ SIM | Default: false |
| `is_locked` | boolean | ✅ SIM | Default: false |

### ✅ Validações

```sql
status IN ('ativo', 'inativo', 'arquivado')
email UNIQUE (lower)
```

### 📝 Observações Importantes

1. **password_hash pode ser NULL** (usuário convidado ainda não definiu senha)
2. **email é único** (case-insensitive via lower(email))
3. **status default é 'ativo'**

---

## 📋 3. TABELA `org_memberships` (Vínculo com Organização)

### ✅ Campos Obrigatórios (NOT NULL)

| Campo | Tipo | Obrigatório | Observações |
|-------|------|-------------|-------------|
| `person_id` | uuid | ✅ SIM | FK para persons |
| `role_id` | integer | ✅ SIM | FK para roles (1-5) |
| `organization_id` | uuid | ✅ SIM | FK para organizations |
| `start_at` | timestamp | ✅ SIM | Default: now() |

### 📝 Observações Importantes

1. **Vínculo único**: (person_id, organization_id, role_id) WHERE end_at IS NULL
2. **Papel obrigatório** (role_id)
3. **Organização obrigatória** (organization_id)

---

## 📋 4. TABELA `team_memberships` (Vínculo com Equipe)

### ✅ Campos Principais

| Campo | Tipo | Obrigatório | Observações |
|-------|------|-------------|-------------|
| `person_id` | uuid | ✅ SIM | FK para persons |
| `team_id` | uuid | ✅ SIM | FK para teams |
| `org_membership_id` | uuid | ❌ NÃO | FK para org_memberships |
| `status` | varchar(20) | ✅ SIM | 'pendente', 'ativo', 'inativo' |

---

## 📋 5. TABELA `athletes` (Dados Específicos de Atleta)

### ✅ Campos Obrigatórios (NOT NULL)

| Campo | Tipo | Obrigatório | Observações |
|-------|------|-------------|-------------|
| `person_id` | uuid | ✅ SIM | FK para persons |
| `athlete_name` | varchar(100) | ✅ SIM | Nome do atleta |
| `birth_date` | date | ✅ SIM | **Obrigatório para atletas!** |
| `state` | varchar(20) | ✅ SIM | Default: 'ativa' |
| `injured` | boolean | ✅ SIM | Default: false |
| `medical_restriction` | boolean | ✅ SIM | Default: false |
| `load_restricted` | boolean | ✅ SIM | Default: false |
| `registered_at` | timestamp | ✅ SIM | Default: now() |

### ❌ Campos Opcionais (Podem ser NULL)

| Campo | Tipo | Observações |
|-------|------|-------------|
| `athlete_nickname` | varchar(50) | Apelido |
| `shirt_number` | integer | Número da camisa (1-99) |
| `main_defensive_position_id` | integer | Posição defensiva principal |
| `secondary_defensive_position_id` | integer | Posição defensiva secundária |
| `main_offensive_position_id` | integer | Posição ofensiva principal |
| `secondary_offensive_position_id` | integer | Posição ofensiva secundária |
| `schooling_id` | integer | Nível de escolaridade |
| `guardian_name` | varchar(100) | Nome do responsável |
| `guardian_phone` | varchar(20) | Telefone do responsável |
| `athlete_photo_path` | varchar(500) | Caminho da foto |
| `organization_id` | uuid | FK para organizations |

### ✅ Validações

```sql
state IN ('ativa', 'dispensada', 'arquivada')
shirt_number BETWEEN 1 AND 99 OR NULL
```

### 📝 Observações Importantes

1. **birth_date É OBRIGATÓRIO para atletas** (NOT NULL na tabela athletes)
2. **athlete_name É OBRIGATÓRIO** (pode ser igual ao full_name)
3. **Posições NÃO são obrigatórias** (podem ser definidas depois)
4. **Altura, peso, lateralidade** - **NÃO EXISTEM** na tabela athletes atual!

### ⚠️ IMPORTANTE: Campos de Altura/Peso/Lateralidade

**A tabela `athletes` NÃO possui os campos**:
- `height` (altura)
- `weight` (peso)
- `laterality` (lateralidade)
- `defensive_positions` (array de posições)

**Campos relacionados que EXISTEM**:
- `main_defensive_position_id` (uma posição)
- `secondary_defensive_position_id` (uma posição)

---

## 📋 6. TABELA `roles` (Papéis)

### Papéis Disponíveis

| ID | Nome | Code |
|----|------|------|
| 1 | Dirigente | dirigente |
| 2 | Coordenador | coordenador |
| 3 | Treinador | treinador |
| 4 | Atleta | atleta |
| 5 | Membro | membro |

---

## 📋 7. TABELA `defensive_positions` (Posições)

### ⚠️ Status Atual

```sql
SELECT code, name FROM defensive_positions;
-- Resultado: 0 rows (TABELA VAZIA!)
```

**A tabela existe mas está VAZIA** - nenhuma posição cadastrada!

---

## 🎯 Resumo por Papel

### 1. **MEMBRO** (role_id = 5)

#### Campos Obrigatórios:
```javascript
{
  // Person
  full_name: string,        // ✅ OBRIGATÓRIO
  first_name: string,       // ✅ OBRIGATÓRIO (derivar de full_name)
  last_name: string,        // ✅ OBRIGATÓRIO (derivar de full_name)
  birth_date: date,         // ❌ OPCIONAL
  gender: string,           // ❌ OPCIONAL
  
  // User
  email: string,            // ✅ OBRIGATÓRIO (único)
  password: string,         // ✅ OBRIGATÓRIO (no welcome flow)
  
  // OrgMembership
  role_id: 5,               // ✅ OBRIGATÓRIO (membro)
  organization_id: uuid,    // ✅ OBRIGATÓRIO
  
  // Campos extras
  phone: string,            // ❌ OPCIONAL (via person_contacts)
}
```

---

### 2. **DIRIGENTE** (role_id = 1)

#### Campos Obrigatórios:
```javascript
{
  // Person
  full_name: string,        // ✅ OBRIGATÓRIO
  first_name: string,       // ✅ OBRIGATÓRIO
  last_name: string,        // ✅ OBRIGATÓRIO
  birth_date: date,         // ❌ OPCIONAL
  gender: string,           // ❌ OPCIONAL
  
  // User
  email: string,            // ✅ OBRIGATÓRIO
  password: string,         // ✅ OBRIGATÓRIO
  
  // OrgMembership
  role_id: 1,               // ✅ OBRIGATÓRIO (dirigente)
  organization_id: uuid,    // ✅ OBRIGATÓRIO
}
```

---

### 3. **COORDENADOR** (role_id = 2)

#### Campos Obrigatórios:
```javascript
{
  // Person
  full_name: string,        // ✅ OBRIGATÓRIO
  first_name: string,       // ✅ OBRIGATÓRIO
  last_name: string,        // ✅ OBRIGATÓRIO
  birth_date: date,         // ❌ OPCIONAL
  gender: string,           // ❌ OPCIONAL
  
  // User
  email: string,            // ✅ OBRIGATÓRIO
  password: string,         // ✅ OBRIGATÓRIO
  
  // OrgMembership
  role_id: 2,               // ✅ OBRIGATÓRIO (coordenador)
  organization_id: uuid,    // ✅ OBRIGATÓRIO
  
  // Campos específicos (via Person.metadata)
  area_of_expertise: string, // ❌ OPCIONAL (metadata)
}
```

---

### 4. **TREINADOR** (role_id = 3)

#### Campos Obrigatórios:
```javascript
{
  // Person
  full_name: string,        // ✅ OBRIGATÓRIO
  first_name: string,       // ✅ OBRIGATÓRIO
  last_name: string,        // ✅ OBRIGATÓRIO
  birth_date: date,         // ❌ OPCIONAL
  gender: string,           // ❌ OPCIONAL
  
  // User
  email: string,            // ✅ OBRIGATÓRIO
  password: string,         // ✅ OBRIGATÓRIO
  
  // OrgMembership
  role_id: 3,               // ✅ OBRIGATÓRIO (treinador)
  organization_id: uuid,    // ✅ OBRIGATÓRIO
  
  // Campos específicos (via Person.metadata)
  certifications: string,   // ❌ OPCIONAL (metadata)
  specialization: string,   // ❌ OPCIONAL (metadata)
}
```

---

### 5. **ATLETA** (role_id = 4)

#### Campos Obrigatórios:
```javascript
{
  // Person
  full_name: string,        // ✅ OBRIGATÓRIO
  first_name: string,       // ✅ OBRIGATÓRIO
  last_name: string,        // ✅ OBRIGATÓRIO
  birth_date: date,         // ⚠️ OBRIGATÓRIO (para athletes table)
  gender: string,           // ❌ OPCIONAL
  
  // User
  email: string,            // ✅ OBRIGATÓRIO
  password: string,         // ✅ OBRIGATÓRIO
  
  // OrgMembership
  role_id: 4,               // ✅ OBRIGATÓRIO (atleta)
  organization_id: uuid,    // ✅ OBRIGATÓRIO
  
  // Athlete (tabela específica)
  athlete_name: string,     // ✅ OBRIGATÓRIO (pode = full_name)
  birth_date: date,         // ✅ OBRIGATÓRIO (na tabela athletes)
  state: 'ativa',           // ✅ OBRIGATÓRIO (default)
  
  // Campos opcionais do atleta
  athlete_nickname: string,                // ❌ OPCIONAL
  shirt_number: integer,                   // ❌ OPCIONAL (1-99)
  main_defensive_position_id: integer,     // ❌ OPCIONAL
  secondary_defensive_position_id: integer,// ❌ OPCIONAL
  guardian_name: string,                   // ❌ OPCIONAL
  guardian_phone: string,                  // ❌ OPCIONAL
}
```

---

## ⚠️ PROBLEMAS IDENTIFICADOS

### 1. **Formulário de Atleta - Campos Inexistentes**

Os formulários implementados incluem campos que **NÃO EXISTEM** no banco:

```typescript
// ❌ CAMPOS QUE NÃO EXISTEM NA TABELA athletes:
height: string              // NÃO EXISTE
weight: string              // NÃO EXISTE
laterality: string          // NÃO EXISTE
defensive_positions: []     // NÃO EXISTE (é main/secondary_position_id)
```

**Solução**: Escolher uma das opções:
1. **Remover esses campos** dos formulários
2. **Adicionar migration** para criar essas colunas na tabela athletes
3. **Armazenar em metadata** temporariamente (não recomendado)

---

### 2. **Tabela defensive_positions Vazia**

A tabela existe mas **não tem dados cadastrados**:

```sql
SELECT * FROM defensive_positions;
-- 0 rows
```

**Solução**: Popular a tabela com as posições:
- Goleiro
- Ponta Esquerda
- Ponta Direita
- Armador Esquerdo
- Armador Central
- Armador Direito
- Pivô

---

### 3. **birth_date - Inconsistência**

- Na tabela `persons`: birth_date é **OPCIONAL** (NULL permitido)
- Na tabela `athletes`: birth_date é **OBRIGATÓRIO** (NOT NULL)

**Impacto**: 
- Formulário de membro/dirigente pode deixar birth_date vazio ✅
- Formulário de atleta **DEVE exigir** birth_date ✅

---

## 🎯 Recomendações para os Formulários

### ✅ Campos que DEVEM ser obrigatórios em TODOS os formulários:

```typescript
full_name: string     // ✅ SEMPRE obrigatório
email: string         // ✅ SEMPRE obrigatório
password: string      // ✅ SEMPRE obrigatório (welcome flow)
```

### ✅ Campos opcionais em formulários genéricos (membro/dirigente/coordenador/treinador):

```typescript
phone: string         // ❌ OPCIONAL
birth_date: date      // ❌ OPCIONAL
gender: string        // ❌ OPCIONAL
```

### ✅ Campos obrigatórios no formulário de ATLETA:

```typescript
full_name: string     // ✅ OBRIGATÓRIO
email: string         // ✅ OBRIGATÓRIO
password: string      // ✅ OBRIGATÓRIO
birth_date: date      // ✅ OBRIGATÓRIO (para athletes table)
```

### ⚠️ Campos do formulário de atleta que PRECISAM SER REVISADOS:

```typescript
// Esses campos NÃO existem no banco atual:
height: string              // ❌ REMOVER ou criar migration
weight: string              // ❌ REMOVER ou criar migration
laterality: string          // ❌ REMOVER ou criar migration
defensive_positions: []     // ❌ AJUSTAR para usar main/secondary_position_id
```

---

## 📊 Matriz de Validação Final

| Campo | Membro | Dirigente | Coordenador | Treinador | Atleta |
|-------|--------|-----------|-------------|-----------|--------|
| **full_name** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **email** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **password** | ✅ | ✅ | ✅ | ✅ | ✅ |
| phone | ❌ | ❌ | ❌ | ❌ | ❌ |
| **birth_date** | ❌ | ❌ | ❌ | ❌ | ✅ |
| gender | ❌ | ❌ | ❌ | ❌ | ❌ |
| area_of_expertise | - | - | ❌ | - | - |
| certifications | - | - | - | ❌ | - |
| specialization | - | - | - | ❌ | - |
| height | - | - | - | - | ⚠️ |
| weight | - | - | - | - | ⚠️ |
| laterality | - | - | - | - | ⚠️ |
| defensive_positions | - | - | - | - | ⚠️ |

**Legenda**:
- ✅ = Obrigatório no banco (NOT NULL)
- ❌ = Opcional (pode ser NULL)
- ⚠️ = Campo não existe no banco (precisa migration ou remoção)
- `-` = Não aplicável

---

## 🚀 Próximos Passos

1. **Decidir sobre campos de atleta**:
   - Criar migration para adicionar height, weight, laterality?
   - Ou remover esses campos do formulário?

2. **Popular defensive_positions**:
   - Criar seed/migration com as 7 posições básicas

3. **Ajustar formulários**:
   - birth_date obrigatório apenas para atleta
   - Campos específicos de atleta conforme decisão do item 1

4. **Atualizar validações frontend**:
   - Validar birth_date obrigatório apenas em AthleteProfileForm

---

**Data**: 2026-01-13  
**Status**: 🔴 **REQUER AÇÃO** - Campos de atleta precisam ser ajustados
