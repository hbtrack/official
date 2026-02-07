<!-- STATUS: NEEDS_REVIEW -->

# Regras de Gerenciamento de Usuários

Este documento consolida todas as regras do sistema aplicáveis à área de gerenciamento de usuários, extraídas do arquivo REGRAS.md principal.

---

## 1. Hierarquia de Papéis (R41)

```
1. Super Administrador (autoridade máxima sobre TODOS os clubes)
2. Dirigente (gestor máximo da organização)
3. Coordenador (gestor de equipes específicas)
4. Treinador/Staff (responsável técnico de equipes)
5. Atleta (praticante do esporte)
```

---

## 2. Cadeia Hierárquica de Criação (RF1)

| Criador | Pode criar |
|---------|-----------|
| Super Administrador | Dirigentes, Coordenadores, Treinadores, Atletas |
| Dirigente | Coordenadores, Treinadores, Atletas |
| Coordenador | Treinadores, Atletas |
| Treinador | Atletas |
| Atleta | ❌ Não pode criar |

**A criação gera automaticamente o papel correspondente.**

---

## 3. Vínculos Automáticos por Papel (RF1.1)

### 3.1. Dirigente Cadastrado
- **Cria:** `person` + `user` + `role=dirigente`
- **NÃO cria vínculo organizacional automático**
- Vínculo ocorre quando:
  - Fundar nova organização
  - Solicitar vínculo com organização existente

### 3.2. Coordenador Cadastrado
- **Cria:** `person` + `user` + `role=coordenador`
- **CRIA vínculo organizacional automático** (`org_membership`) com a organização do agente criador
- Vinculação imediata

### 3.3. Treinador Cadastrado
- **Cria:** `person` + `user` + `role=treinador`
- **CRIA vínculo organizacional automático** (`org_membership`) com a organização do agente criador
- **NÃO cria vínculo com equipe** (definido posteriormente via RF7)

### 3.4. Atleta Cadastrada
- **Cria:** `person` + `role=atleta`
- **Criação de `user` é OPCIONAL** (checkbox "Criar acesso ao sistema")
- **NÃO cria vínculo organizacional automático**
- **NÃO cria vínculo com equipe automático** (`team_registration` é opcional)
- Pode ser cadastrada "sem equipe" e adicionada depois

---

## 4. Papéis do Sistema (R4)

| ID | Code | Nome | Descrição |
|----|------|------|-----------|
| 1 | dirigente | Dirigente | Gestor máximo da organização |
| 2 | coordenador | Coordenador | Gestor de equipes específicas |
| 3 | treinador | Treinador | Responsável técnico de equipes |
| 4 | atleta | Atleta | Praticante do esporte |

---

## 5. Escopo de Permissões por Papel (R25)

| Papel | Escopo |
|-------|--------|
| Super Administrador | Acesso total a TODOS os clubes do sistema |
| Dirigente | Acesso administrativo total da SUA organização |
| Coordenador | Acesso total a dados operacionais e esportivos da organização |
| Treinador | Acesso apenas às suas equipes (definidas via RF7) |
| Atleta | Acesso restrito aos próprios dados |

---

## 6. Vínculos Organizacionais (RDB9 - org_memberships)

### Estrutura da Tabela
```sql
CREATE TABLE org_memberships (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  person_id UUID NOT NULL REFERENCES persons(id),
  role_id INTEGER NOT NULL REFERENCES roles(id),
  organization_id UUID NOT NULL REFERENCES organizations(id),
  start_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  end_at TIMESTAMPTZ,  -- NULL = vínculo ativo
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  deleted_at TIMESTAMPTZ,
  deleted_reason TEXT
);
```

### Regras de Exclusividade
- **R7:** Uma pessoa possui apenas UM vínculo ativo por organização+papel
- Índice único parcial garante: `UNIQUE (person_id, organization_id, role_id) WHERE end_at IS NULL AND deleted_at IS NULL`

---

## 7. Vínculo Ativo e Exclusividade (R5, R7)

### Papéis não acumuláveis (R5)
Uma pessoa NÃO pode ter múltiplos papéis ativos simultaneamente.

**Mudança de papel requer:**
1. Encerramento do vínculo atual (`end_at`)
2. Criação de novo vínculo
3. Sem sobreposição temporal

### Vínculo ativo (R7)
- **Staff:** 1 vínculo ativo por pessoa+organização+papel
- **Atleta:** Pode ter MÚLTIPLOS `team_registrations` ativos simultâneos

---

## 8. Usuário sem Vínculo Ativo (RF3, R40)

| Situação | Comportamento |
|----------|---------------|
| Staff sem `org_membership` | NÃO pode operar no sistema |
| Atleta sem `team_registration` | Mantém acesso SOMENTE LEITURA ao próprio histórico |

---

## 9. Estrutura da Árvore de Usuários

```
HB Track (root)
└── Organização
    ├── 👔 Dirigentes (org_memberships role=dirigente)
    ├── 📋 Coordenadores (org_memberships role=coordenador)
    ├── 🎯 Treinadores (org_memberships role=treinador)
    └── ⚽ Equipes
        └── 🏃 Atletas (team_registrations)
```

**Regras:**
- Dirigentes, Coordenadores e Treinadores são vinculados à **ORGANIZAÇÃO**
- Atletas são vinculados a **EQUIPES** (via `team_registrations`)

---

## 10. Fluxo de Criação por Papel

### 10.1. Criar Dirigente
```
1. Criar Person (full_name, birth_date, gender, email, phone, cpf)
2. Se checkbox "Criar acesso ao sistema" marcado:
   - Criar User (email, person_id, role=dirigente)
   - Enviar email de boas-vindas
3. NÃO criar org_membership (vínculo posterior)
```

### 10.2. Criar Coordenador
```
1. Criar Person (full_name, birth_date, gender, email, phone, cpf)
2. Criar User (email, person_id, role=coordenador)
3. Criar org_membership:
   - person_id = novo person
   - organization_id = organização do criador
   - role_id = 2 (coordenador)
   - start_at = now()
```

### 10.3. Criar Treinador
```
1. Criar Person (full_name, birth_date, gender, email, phone, cpf)
2. Criar User (email, person_id, role=treinador)
3. Criar org_membership:
   - person_id = novo person
   - organization_id = organização do criador
   - role_id = 3 (treinador)
   - start_at = now()
```

### 10.4. Criar Atleta
```
1. Criar Person (full_name, birth_date, gender, email, phone, cpf)
2. Criar Athlete (person_id, state='ativa', dados esportivos)
3. Se checkbox "Criar acesso ao sistema" marcado:
   - Criar User (email, person_id, role=atleta)
4. Se equipe selecionada:
   - Criar team_registration (athlete_id, team_id, start_at)
```

---

## 11. Encerramento de Vínculos (R9)

| Tipo | Quem pode encerrar | Processo |
|------|-------------------|----------|
| `org_membership` staff | Dirigente (aprovação explícita) | Define `end_at` |
| `team_registration` atleta | Coordenador ou Treinador | Define `end_at` |

**Encerramento automático NÃO ocorre** (sem virada de temporada para vínculos).

---

## 12. Reativação de Vínculo (R29)

- Reativação cria **NOVA LINHA** com novo UUID
- NÃO reabre linha anterior
- Deve respeitar exclusividade (não pode haver vínculo ativo existente)
- Vale a partir da data de reativação

---

## 13. Auditoria de Ações Críticas (R30, R31)

### Ações auditáveis
- Criação de usuário
- Criação de vínculo organizacional
- Encerramento de vínculo
- Reativação de vínculo
- Criação de organização
- Dirigente assume/funda organização

### Campos obrigatórios no log
| Campo | Descrição |
|-------|-----------|
| `actor_id` | Quem fez a ação |
| `timestamp` | Quando |
| `action` | O quê (ex: "create_user", "create_membership") |
| `context` | Detalhes (JSON) |
| `old_value` | Valor anterior (se aplicável) |
| `new_value` | Novo valor |

---

## 14. Exclusão Lógica (R28, RDB4)

- **NUNCA** excluir fisicamente
- Usar `deleted_at` + `deleted_reason`
- `deleted_reason` é OBRIGATÓRIA quando `deleted_at IS NOT NULL`

---

## 15. Permissões de Visualização

| Papel | Pode ver |
|-------|----------|
| Super Admin | Todos os usuários de TODOS os clubes |
| Dirigente | Todos os usuários da SUA organização |
| Coordenador | Todos os usuários da SUA organização |
| Treinador | Usuários das SUAS equipes |
| Atleta | Apenas próprio perfil |

---

## 16. Permissões de Edição

| Papel | Criar | Editar | Encerrar vínculo | Excluir |
|-------|-------|--------|------------------|---------|
| Super Admin | Todos os papéis | ✅ | ✅ | ✅ (soft) |
| Dirigente | Coord, Trein, Atl | ✅ | ✅ | ✅ (soft) |
| Coordenador | Trein, Atl | ✅ (org) | ✅ (team_reg) | ❌ |
| Treinador | Atletas | ✅ (equipes) | ✅ (team_reg) | ❌ |
| Atleta | ❌ | Próprio perfil | ❌ | ❌ |

---

## 17. Super Administrador (R3)

- Existe **EXATAMENTE UM** Super Administrador
- Estrutural, vitalício, imutável e não removível
- Identificado por `users.is_superadmin = true`
- Pode ignorar travas operacionais
- Toda ação crítica é auditada

---

## 18. Troca de Papel (R26, R27)

**NÃO existe troca direta de papel.**

### Processo obrigatório:
1. Encerrar vínculo atual (`org_membership.end_at`)
2. Criar novo vínculo com novo papel
3. Sem sobreposição temporal

### Sem carência (2.X.1)
A troca pode ocorrer imediatamente, sem tempo mínimo entre papéis.

---

## 19. Diagrama de Entidades

```
persons ─────┬──── users (optional)
             │
             └──── org_memberships ─── organizations
                       │
                       └── roles

athletes ────┬──── persons
             │
             └──── team_registrations ─── teams ─── organizations
```

---

## 20. Endpoints da API

### Roles
- `GET /api/v1/roles` - Listar papéis

### Organizations
- `GET /api/v1/organizations` - Listar organizações
- `POST /api/v1/organizations` - Criar organização
- `GET /api/v1/organizations/{id}` - Obter organização

### Users
- `GET /api/v1/users` - Listar usuários
- `POST /api/v1/users` - Criar usuário
- `GET /api/v1/users/{id}` - Obter usuário
- `PATCH /api/v1/users/{id}` - Atualizar usuário

### Memberships
- `GET /api/v1/organizations/{org_id}/memberships` - Listar vínculos
- `POST /api/v1/organizations/{org_id}/memberships` - Criar vínculo
- `PATCH /api/v1/memberships/{id}` - Atualizar vínculo (end_at)

### Persons
- `GET /api/v1/persons` - Listar pessoas
- `POST /api/v1/persons` - Criar pessoa
- `GET /api/v1/persons/{id}` - Obter pessoa

---

## Referências

- **REGRAS.md**: Documento principal com todas as regras do sistema
- **R4**: Papéis do sistema
- **R5**: Papéis não acumuláveis
- **R7**: Vínculo ativo e exclusividade
- **RF1**: Cadeia hierárquica de criação
- **RF1.1**: Vínculos automáticos por papel
- **RDB9**: Estrutura de org_memberships
