# 011-ADR-TRAIN — RBAC por Papéis e Permissões

**Status:** Aceita
**Data:** 2026-02-08
**Autor:** Equipe HB Track
**Fase:** F2
**Módulos Afetados:** backend | database | auth

---

## Contexto

O HB Track possui diferentes tipos de usuários com responsabilidades e permissões distintas: dirigentes, coordenadores, treinadores e atletas. O acesso a funcionalidades e dados deve ser controlado de forma granular, baseado no papel do usuário dentro da organização.

Esta decisão é 100% evidence-first: o modelo RBAC está implementado no schema com 3 tabelas (roles, permissions, role_permissions) e vinculação via org_memberships.

**Componentes Relacionados:**
- Modelo de dados: `roles`, `permissions`, `role_permissions`, `org_memberships`
- Constraints: `ux_roles_code`, `ux_roles_name`, `pk_role_permissions`, `ux_org_memberships_active`
- Hierarquia: Dirigente > Coordenador > Treinador > Atleta
- Invariantes: classe D (Router/RBAC)

---

## Decisão

O controle de acesso é baseado em **RBAC (Role-Based Access Control)** com 3 tabelas:

### Modelo de dados:
| Tabela | Função |
|--------|--------|
| `roles` | Papéis do sistema (Dirigente, Coordenador, Treinador, Atleta) |
| `permissions` | Permissões granulares (ações específicas) |
| `role_permissions` | Junction table: papel ↔ permissão (N:N) |
| `org_memberships` | Vinculação: pessoa ↔ organização ↔ papel |

### Hierarquia de papéis:
```
Dirigente (nível mais alto)
  └── Coordenador
        └── Treinador
              └── Atleta (nível mais baixo)
```

### Regra de unicidade:
Uma pessoa só pode ter **1 vínculo ativo** por combinação (pessoa + organização + papel).

### Detalhes Técnicos

```sql
-- Tabela roles (schema.sql:1983)
CREATE TABLE public.roles (
    id smallint NOT NULL,
    name character varying(50) NOT NULL,
    code character varying(30) NOT NULL,
    description text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);

-- schema.sql:1997
COMMENT ON TABLE public.roles IS
  'Papéis do sistema. R4: Dirigente, Coordenador, Treinador, Atleta.';

-- Unicidade por código e nome (schema.sql:3708, 3716)
CONSTRAINT ux_roles_code UNIQUE (code);
CONSTRAINT ux_roles_name UNIQUE (name);

-- Junction table role ↔ permission (schema.sql:1966)
CREATE TABLE public.role_permissions (
    role_id smallint NOT NULL,
    permission_id integer NOT NULL
);
CONSTRAINT pk_role_permissions PRIMARY KEY (role_id, permission_id);

-- FKs com ON DELETE CASCADE (schema.sql:6236, 6244)
CONSTRAINT fk_role_permissions_permission_id FOREIGN KEY (permission_id)
  REFERENCES public.permissions(id) ON DELETE CASCADE;
CONSTRAINT fk_role_permissions_role_id FOREIGN KEY (role_id)
  REFERENCES public.roles(id) ON DELETE CASCADE;

-- Vinculação pessoa ↔ organização ↔ papel (schema.sql:1617-1618)
-- org_memberships:
--   person_id, role_id, organization_id, start_at, end_at

-- Unique index: 1 vínculo ativo por combinação (schema.sql:5152)
CREATE UNIQUE INDEX ux_org_memberships_active ON public.org_memberships
  USING btree (person_id, organization_id, role_id)
  WHERE ((end_at IS NULL) AND (deleted_at IS NULL));

-- FK para roles (schema.sql:6188)
CONSTRAINT fk_org_memberships_role_id FOREIGN KEY (role_id)
  REFERENCES public.roles(id) ON DELETE RESTRICT;
```

**Stack envolvida:**
- Database: PostgreSQL — tabelas de RBAC + unique index condicional
- Backend: FastAPI — middleware de autenticação + permission guards nos routers
- Invariantes: classe D testa endpoints com 401 (não autenticado) e 403 (sem permissão)

---

## Alternativas Consideradas

### Alternativa 1: Hierarquia hardcoded (sem tabelas de permissão)

**Prós:**
- Mais simples (if role == 'treinador')
- Sem tabelas extras

**Contras:**
- Impossível customizar permissões por papel
- Adicionar novo papel requer mudança de código
- Sem audit trail de quem tem qual permissão

**Razão da rejeição:** A granularidade de permissões é necessária para cenários como "coordenador pode editar treino de outro treinador, mas treinador não".

### Alternativa 2: ABAC (Attribute-Based Access Control)

**Prós:**
- Mais flexível que RBAC
- Regras baseadas em atributos dinâmicos

**Contras:**
- Complexidade de implementação muito maior
- Difícil de auditar e debugar
- Overhead desnecessário para 4 papéis

**Razão da rejeição:** Com apenas 4 papéis bem definidos, RBAC é suficiente. ABAC seria over-engineering.

---

## Consequências

### Positivas
- ✅ Permissões granulares por papel, gerenciáveis via banco (sem redeploy)
- ✅ Unique index garante 1 vínculo ativo por pessoa/org/papel
- ✅ ON DELETE RESTRICT em memberships previne remoção acidental de papéis em uso
- ✅ ON DELETE CASCADE em role_permissions simplifica limpeza

### Negativas
- ⚠️ 3 tabelas extras (roles, permissions, role_permissions) para manter
- ⚠️ Queries de autorização envolvem JOINs (org_memberships → roles → role_permissions)

### Neutras
- ℹ️ `org_memberships` tem campos `start_at`/`end_at` para historicizar vínculos
- ℹ️ A hierarquia (Dirigente > Coordenador > Treinador > Atleta) é convenção de negócio, não enforced por DB

---

## Validação

### Critérios de Conformidade
- [x] Tabela `roles` com UNIQUE em `code` e `name` (`schema.sql:3708, 3716`)
- [x] Junction table `role_permissions` com PK composta (`schema.sql:3468`)
- [x] `org_memberships` com FK para `roles` ON DELETE RESTRICT (`schema.sql:6188`)
- [x] Unique index `ux_org_memberships_active` garante 1 vínculo ativo (`schema.sql:5152`)
- [x] Comment documenta os 4 papéis: Dirigente, Coordenador, Treinador, Atleta (`schema.sql:1997`)

---

## Referências

- `Hb Track - Backend/docs/_generated/schema.sql:1983`: tabela `roles`
- `Hb Track - Backend/docs/_generated/schema.sql:1997`: comment "R4: Dirigente, Coordenador, Treinador, Atleta"
- `Hb Track - Backend/docs/_generated/schema.sql:1966`: tabela `role_permissions`
- `Hb Track - Backend/docs/_generated/schema.sql:5152`: unique index `ux_org_memberships_active`
- `Hb Track - Backend/docs/_generated/schema.sql:6188`: FK `fk_org_memberships_role_id`
- `Hb Track - Backend/docs/_generated/schema.sql:6236`: FK `fk_role_permissions_permission_id`
- ADRs relacionados: ADR-TRAIN-010 (multi-tenancy — org_memberships vincula a org), ADR-TRAIN-004 (invariantes classe D)

---

## Revisões

| Data | Autor | Mudança | Versão |
|------|-------|---------|--------|
| 2026-02-08 | Equipe HB Track | Criação evidence-first a partir de schema.sql | 1.0 |
