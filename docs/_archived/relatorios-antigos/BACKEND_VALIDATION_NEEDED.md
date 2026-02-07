<!-- STATUS: DEPRECATED | arquivado -->

# ⚠️ VALIDAÇÃO DE BACKEND NECESSÁRIA - EQUIPES DUPLICADAS

## 🔴 Problema Identificado

O sistema permitiu criar **3 equipes com o mesmo nome** através da interface `/teams`.

## 🔍 Análise da Causa Raiz

### O que foi testado:
- ✅ Frontend em `/teams` **está correto** - usa `CreateTeamModal.tsx`
- ✅ Modal chama `teamsService.create()` corretamente
- ✅ Tratamento de erros está implementado
- ❌ **Backend NÃO está validando nomes duplicados**
- ❌ Toast mostra "sucesso" porque backend retorna HTTP 200/201

### Por que aconteceu:
1. Usuário criou equipe "Time A" → Backend aceitou ✅
2. Usuário criou equipe "Time A" novamente → Backend aceitou ❌ (deveria rejeitar)
3. Usuário criou equipe "Time A" pela 3ª vez → Backend aceitou ❌ (deveria rejeitar)

## ✅ Solução Temporária Implementada no Frontend (HOJE)

Adicionada **validação preventiva no frontend** em `CreateTeamModal.tsx`:

```typescript
// Busca todas as equipes antes de criar
const existingTeams = await teamsService.list();
const duplicateTeam = existingTeams.items.find(
  team => team.name.toLowerCase().trim() === teamName.toLowerCase().trim() &&
          team.organization_id === user?.organization_id &&
          team.category_id === selectedCategoryId &&
          team.gender === selectedGender
);

if (duplicateTeam) {
  setValidationError(`Já existe uma equipe "${teamName}" com esta categoria e gênero`);
  return; // Bloqueia criação
}
```

**IMPORTANTE:** A validação verifica **NOME + CATEGORIA + GÊNERO**. Isso permite:
- ✅ "IDEC Feminino" e "IDEC Masculino" (mesmo nome, gêneros diferentes)
- ✅ "IDEC Cadete" e "IDEC Juvenil" (mesmo nome, categorias diferentes)
- ❌ "IDEC Cadete Feminino" duplicado (nome + categoria + gênero iguais)

**Benefícios da solução frontend:**
- ✅ Previne duplicatas imediatamente
- ✅ Feedback instantâneo ao usuário
- ✅ Funciona como camada extra de segurança

**Limitações da solução frontend:**
- ⚠️ Não previne race conditions (2 usuários criando ao mesmo tempo)
- ⚠️ Não protege se alguém usar API diretamente (Postman, curl, etc.)
- ⚠️ Adiciona latência (precisa buscar todas equipes primeiro)

## ❌ AÇÃO NECESSÁRIA NO BACKEND (PRIORITÁRIO)

### 1. Adicionar Constraint UNIQUE no Banco

```sql
-- Adicionar constraint para evitar nomes duplicados com mesma categoria e gênero
ALTER TABLE teams
ADD CONSTRAINT unique_team_name_category_gender_per_org
UNIQUE (name, organization_id, category_id, gender, season_id);
```

**Nota:** O constraint permite o mesmo nome se categoria OU gênero forem diferentes.

### 2. Adicionar Validação na API

No endpoint `POST /teams`, adicionar validação:

```python
# Pseudo-código
def create_team(payload):
    existing = db.query(Team).filter(
        Team.name == payload.name,
        Team.organization_id == payload.organization_id,
        Team.category_id == payload.category_id,
        Team.gender == payload.gender,
        Team.season_id == payload.season_id,
        Team.deleted_at == None
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Já existe uma equipe '{payload.name}' com esta categoria e gênero"
        )

    # Criar equipe...
```

### 3. Retornar Erro Apropriado

```json
{
  "detail": "Já existe uma equipe com este nome nesta temporada"
}
```

## 📊 Impacto

### Sem correção do backend:
- ❌ Dados duplicados no banco
- ❌ Relatórios inconsistentes
- ❌ Confusão para usuários
- ❌ Problemas de integridade referencial

### Com correção do backend:
- ✅ Garantia de unicidade no banco de dados
- ✅ Mensagens de erro apropriadas
- ✅ Proteção contra race conditions
- ✅ Validação em qualquer camada (web, API direta, scripts)

## 🚨 Prioridade

🔴 **CRÍTICA** - Corrigir **IMEDIATAMENTE** antes de produção

## ✅ Checklist de Implementação

### Backend (Obrigatório):
- [ ] Adicionar constraint UNIQUE no banco de dados
- [ ] Adicionar validação na API `POST /teams`
- [ ] Testar com casos de duplicata
- [ ] Retornar HTTP 400 com mensagem clara
- [ ] Documentar erro na OpenAPI/Swagger

### Frontend (Concluído):
- [x] Validação preventiva adicionada em `CreateTeamModal.tsx`
- [x] Mensagem de erro exibida ao usuário
- [x] Toast de erro funcionando

### Banco de Dados (Para Limpar):
- [ ] Identificar equipes duplicadas existentes
- [ ] Decidir qual manter (mais antiga, mais completa, etc.)
- [ ] Deletar ou mesclar duplicatas
- [ ] Aplicar constraint após limpeza

## 📝 Exemplo de Query para Encontrar Duplicatas

```sql
-- Encontrar equipes duplicadas (mesmo nome + categoria + gênero)
SELECT
    name,
    category_id,
    gender,
    organization_id,
    COUNT(*) as quantidade
FROM teams
WHERE deleted_at IS NULL
GROUP BY name, category_id, gender, organization_id
HAVING COUNT(*) > 1;
```

## 🔗 Arquivos Relacionados

- Frontend: `src/components/teams-v2/CreateTeamModal.tsx` (linha 94-109)
- API Service: `src/lib/api/teams.ts` (linha 114-116)
- Documentação: Este arquivo

## 📌 Regras de Validação

**Equipes duplicadas são bloqueadas quando:**
- Nome + Categoria + Gênero + Organização são TODOS iguais

**Equipes permitidas (mesmo nome, mas diferem em pelo menos um campo):**
- "IDEC" Feminino vs "IDEC" Masculino ✅
- "IDEC" Cadete vs "IDEC" Juvenil ✅
- "IDEC" Cadete Feminino vs "IDEC" Cadete Masculino ✅
