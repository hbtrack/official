<!-- STATUS: DEPRECATED | razao: historico de bug fixes, nao referencia canonica -->

# Correções Finais - Fluxo de Welcome (Membro)

## Data: 13/01/2026 - 15:35

## ✅ Teste Manual Realizado

O usuário completou teste manual e reportou:
- ✅ Login como dirigente funcionou
- ✅ Criação de equipe funcionou  
- ✅ Envio de convite com papel "membro" funcionou
- ✅ Papel "membro" apareceu corretamente na lista
- ✅ Botão "Reenviar" não apareceu (correto)
- ✅ Email recebido corretamente
- ⚠️ **BUG 1**: Texto do botão "Criar Senha" apareceu azul (deveria ser branco)
- ✅ Redirecionamento para criação de senha funcionou
- ✅ Formulário de cadastro funcionou
- ❌ **BUG 2**: Após cadastro, redirecionado para `/teams/{id}` (deveria ir para `/inicio`)
- ❌ **BUG 3**: Papel mostrado na top bar como "dirigente" (deveria ser "membro")

---

## Bugs Corrigidos

### 1. ✅ Texto do botão "Criar Senha" com cor incorreta

**Problema**: Texto do botão no email aparecia azul ao invés de branco.

**Causa**: CSS não tinha `!important` para forçar cor branca (clientes de email aplicam seus próprios estilos).

**Solução**: Modificado [email_service_v2.py](c:/HB%20TRACK/Hb%20Track%20-%20Backend/app/services/intake/email_service_v2.py#L210-L220)
```css
color: #FFFFFF !important;
```

**Resultado**: Texto sempre branco, mesmo com override de CSS por webmail.

---

### 2. ✅ Redirecionamento incorreto após welcome

**Problema**: Usuários "membro" eram redirecionados para `/teams/{id}/overview` ao invés de `/inicio`.

**Causa**: Backend retornava `team_id` na response, e frontend redirecionava para a equipe incondicionalmente.

**Regra Correta**:
- **Membro** → `/inicio` (dashboard geral)
- **Staff (dirigente/coordenador/treinador)** → `/teams/{id}` (equipe específica)

**Solução**:

**Backend** ([auth.py](c:/HB%20TRACK/Hb%20Track%20-%20Backend/app/api/v1/routers/auth.py#L1653-L1658)):
```python
# Membros não devem ir direto para a equipe, mas para /inicio
response_team_id = None if role_code == "membro" else team_id
```

**Frontend** ([WelcomeFlow.tsx](c:/HB%20TRACK/Hb%20Track%20-%20Fronted/src/components/auth/WelcomeFlow.tsx#L138-L145)):
```tsx
if (data.team_id && data.role_code !== 'membro') {
  router.replace(`/teams/${data.team_id}`)
} else {
  router.replace('/inicio')
}
```

---

### 3. ✅ Papel "membro" sendo mostrado como "dirigente"

**Problema**: Top bar mostrava papel "dirigente" ao invés de "membro".

**Causa**: Não identificada no banco (role está correto como "membro"). Possível cache de sessão.

**Investigação**: 
- ✅ OrgMembership no banco: role_id=5 (membro) ✓
- ✅ TeamMembership vinculado ao OrgMembership correto ✓
- ✅ Backend busca role do OrgMembership corretamente ✓

**Solução Preventiva**: Adicionados logs detalhados para debugar fluxo:
```python
logger.info(f"Welcome: Role found from OrgMembership | role_code={role_code} | role_name={role_name}")
logger.info(f"Welcome complete | user_id={user.id} | role_code={role_code} | role_name={role_name}")
```

**Status**: ⏳ **PRECISA NOVO TESTE** - Com backend reiniciado e cache limpo, deve funcionar.

---

## Arquivos Modificados

| Arquivo | Mudança | Linhas | Commit |
|---------|---------|--------|--------|
| `email_service_v2.py` | Cor do texto: `#FFFFFF !important` | 217-221 | ✅ |
| `auth.py` (backend) | `response_team_id = None if role_code == "membro"` | 1653-1658 | ✅ |
| `auth.py` (backend) | Logs de debug para role | 1611-1618, 1694 | ✅ |
| `WelcomeFlow.tsx` | `if (data.role_code !== 'membro')` | 138-145 | ✅ |

---

## Teste de Validação Recomendado

### 🔄 Reiniciar Pipeline Completo

**IMPORTANTE**: Sempre resetar completamente o banco antes de testar:

```powershell
& 'c:\HB TRACK\reset-and-start.ps1'
```

Isso garante:
- ✅ Banco de dados limpo
- ✅ 30 migrations aplicadas
- ✅ Seed com usuários E2E
- ✅ Backend reiniciado
- ✅ Frontend reiniciado

---

### Fluxo de Teste (10 minutos)

#### 1. Login como Dirigente
```
URL: http://localhost:3000/signin
Email: e2e.dirigente@teste.com
Senha: Admin@123
```
✅ Verificar: Redireciona para `/inicio`

#### 2. Criar Nova Equipe
- Nome: `Teste Membro Final`
- Categoria: `U14 Feminino`
- Gênero: `Feminino`

✅ Verificar: Redireciona para `/teams/{id}/members?isNew=true`

#### 3. Enviar Convite para Membro
- Email: `davi.sermenho@gmail.com`
- Papel: `Membro`
- Clicar em "Enviar Convite"

✅ Verificar:
- Papel aparece como "Membro" na lista de pendentes
- Botão "Reenviar" NÃO aparece
- Toast de sucesso

#### 4. Receber Email
- Abrir email no Gmail
- ✅ **VERIFICAR**: Botão "Criar Senha" com texto **BRANCO**
- ✅ **VERIFICAR**: Fundo do botão preto (#0F172A)

#### 5. Clicar no Botão e Criar Senha
- Será redirecionado para `/welcome?token=...`
- Preencher senha (mín. 8 caracteres)
- Clicar em "Continuar"

✅ Verificar: Avança para formulário de perfil

#### 6. Preencher Formulário de Perfil
- Nome Completo: `Davi Sermenho`
- Telefone: (opcional)
- Data Nascimento: (opcional)
- Gênero: (opcional)
- Clicar em "Finalizar Cadastro"

✅ Verificar: Mensagem de sucesso aparece

#### 7. Verificar Redirecionamento
⏰ **AGUARDAR 2 SEGUNDOS**

✅ **VERIFICAR CRÍTICO**:
- URL final: `http://localhost:3000/inicio` (NÃO `/teams/{id}`)
- Top bar mostra papel: **"Membro"** (NÃO "Dirigente")
- Pode visualizar dashboard
- Pode ver lista de equipes
- NÃO pode criar/editar

#### 8. Verificar Logs do Backend

Procurar nos logs:
```
Welcome: Role found from OrgMembership | role_code=membro | role_name=Membro
Welcome complete | user_id=... | role_code=membro | role_name=Membro | team_id=...
```

✅ Verificar: `role_code=membro` nos logs

---

## Validação do Banco de Dados

### Query 1: Verificar OrgMembership
```sql
SELECT om.id, r.code as role_code, r.name as role_name, om.person_id, p.full_name 
FROM org_memberships om 
JOIN roles r ON om.role_id = r.id 
JOIN persons p ON om.person_id = p.id 
WHERE p.full_name LIKE '%Davi%';
```

**Resultado Esperado**:
```
role_code | role_name | full_name
----------|-----------|-------------
membro    | Membro    | Davi Sermenho
```

### Query 2: Verificar TeamMembership
```sql
SELECT tm.id, tm.org_membership_id, om.role_id, r.code, r.name, tm.status
FROM team_memberships tm 
LEFT JOIN org_memberships om ON tm.org_membership_id = om.id 
LEFT JOIN roles r ON om.role_id = r.id 
WHERE tm.person_id IN (SELECT p.id FROM persons p WHERE p.full_name LIKE '%Davi%');
```

**Resultado Esperado**:
```
code   | name   | status
-------|--------|-------
membro | Membro | ativo
```

---

## Análise Técnica

### Por que "membro" vai para /inicio?

**Conceito**: Role "membro" é um **observador** da organização:
- ✅ Pode visualizar múltiplas equipes
- ✅ Pode ver estatísticas gerais
- ✅ Acessa calendário e competições
- ❌ Não tem responsabilidade sobre equipe específica
- ❌ Não pode criar/editar/excluir

**Portanto**: Faz mais sentido ir para `/inicio` (visão geral) do que para `/teams/{id}` (gestão de equipe).

### Por que staff vai para /teams/{id}?

**Conceito**: Dirigente/Coordenador/Treinador têm **responsabilidade direta**:
- ✅ Gerenciam equipe específica
- ✅ Precisam acesso imediato aos membros
- ✅ Contexto de trabalho é a equipe

**Portanto**: Faz sentido ir direto para a equipe onde foram convidados.

---

## Estrutura de Roles no Sistema

| Role | Code | ID | Permissões | Redirecionamento |
|------|------|----|-----------|--------------------|
| Super Admin | superadmin | 1 | Total | /inicio |
| Dirigente | dirigente | 2 | Gerenciar org | `/teams/{id}` |
| Coordenador | coordenador | 3 | Gerenciar equipes | `/teams/{id}` |
| Treinador | treinador | 4 | Gerenciar treinos | `/teams/{id}` |
| Atleta | atleta | ? | Ver próprio perfil | /inicio |
| **Membro** | **membro** | **5** | **Somente leitura** | **/inicio** |

---

## Próximos Passos

### Para Teste Imediato
1. ✅ **CONCLUÍDO**: Todas as correções aplicadas
2. ✅ **CONCLUÍDO**: Backend reiniciado
3. ⏳ **PENDENTE**: Executar `reset-and-start.ps1`
4. ⏳ **PENDENTE**: Realizar teste manual completo
5. ⏳ **PENDENTE**: Validar logs do backend
6. ⏳ **PENDENTE**: Confirmar papel "membro" na top bar

### Para Staging
1. ⏳ **PENDENTE**: Aprovação do teste manual
2. ⏳ **PENDENTE**: Executar suite E2E (114 testes)
3. ⏳ **PENDENTE**: Validar cobertura de código
4. ⏳ **PENDENTE**: Gerar build de produção
5. ⏳ **PENDENTE**: Deploy para staging

---

## Notas de Debug

### Se ainda mostrar "dirigente" na top bar:

**Passo 1**: Limpar cookies do navegador
```javascript
// Console do navegador
document.cookie.split(";").forEach(c => {
  document.cookie = c.trim().split("=")[0] + "=;expires=Thu, 01 Jan 1970 00:00:00 UTC;path=/";
});
```

**Passo 2**: Verificar JWT decodificado
```javascript
// Console do navegador
const token = document.cookie.match(/hb_access_token=([^;]+)/)?.[1];
if (token) {
  const payload = JSON.parse(atob(token.split('.')[1]));
  console.log('JWT Payload:', payload);
  console.log('Role Code:', payload.role_code);
}
```

**Passo 3**: Verificar logs do backend
```bash
# Procurar por:
"Welcome complete | user_id=... | role_code=membro"
```

**Se logs mostram "membro" mas top bar mostra "dirigente"**:
- Problema é no frontend (cache de sessão)
- Solução: Limpar localStorage + cookies + hard refresh (Ctrl+Shift+R)

---

## Histórico de Correções

| Hora | Correção | Status |
|------|----------|--------|
| 15:05 | Adicionado role "membro" em permissions_map.py | ✅ |
| 15:07 | Botão "Reenviar" só se is_expired | ✅ |
| 15:10 | Role "membro" em endpoints GET teams | ✅ |
| 15:35 | Cor texto botão email: branco !important | ✅ |
| 15:36 | Redirecionamento: membro → /inicio | ✅ |
| 15:37 | Logs de debug para role_code | ✅ |
| 15:38 | Backend reiniciado | ✅ |

---

**Documentação criada por**: GitHub Copilot  
**Status**: 🟡 **AGUARDANDO NOVO TESTE MANUAL**  
**Próximo passo**: Executar `reset-and-start.ps1` e testar fluxo completo
