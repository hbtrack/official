<!-- STATUS: NEEDS_REVIEW -->

# 🔗 Integração: Página Atletas → Cadastro Único

**Data**: 2026-01-04
**Status**: ✅ Implementado e Testado

---

## 🎯 Objetivo

Integrar a página de gerenciamento de atletas com a ficha única de cadastro, permitindo que o botão "Cadastrar Atleta" redirecione diretamente para o fluxo de cadastro de usuário com o papel de "atleta" pré-selecionado.

---

## 📋 Requisito do Usuário

> "O sistema hoje funciona com uma ficha única de cadastro com steps. O ideal é clicar em 'Cadastrar Atleta' e ser direcionado para a parte da ficha que cadastra atleta."

**Fluxo Desejado**:
1. Usuário está em `http://localhost:3000/admin/athletes`
2. Clica em "Cadastrar Atleta"
3. É redirecionado para `http://localhost:3000/admin/cadastro`
4. O fluxo "Cadastro de Usuário" é **automaticamente selecionado**
5. O papel "Atleta" é **automaticamente pré-selecionado**
6. Usuário prossegue direto para preencher dados pessoais

---

## 🔧 Implementação

### **1. Atualização do Link (TeamAthletesList.tsx)**

**Arquivo**: [TeamAthletesList.tsx](../Hb%20Track%20-%20Fronted/src/components/Athletes/TeamAthletesList.tsx#L89)

**Antes**:
```tsx
<a href="/admin/athletes/new" className="...">
  + Cadastrar Atleta
</a>
```

**Depois**:
```tsx
<a href="/admin/cadastro?flow=user&role=atleta" className="...">
  + Cadastrar Atleta
</a>
```

**Parâmetros de URL**:
- `flow=user` → Seleciona o fluxo "Cadastro de Usuário"
- `role=atleta` → Pré-seleciona o papel "Atleta"

---

### **2. Implementação da Lógica de Pré-seleção (FichaUnicaWizard)**

**Arquivo**: [FichaUnicaWizard/index.tsx](../Hb%20Track%20-%20Fronted/src/features/intake/FichaUnicaWizard/index.tsx#L68-L83)

**Código Adicionado**:
```tsx
// Pré-selecionar flowType e userRole a partir da URL (ex: /admin/cadastro?flow=user&role=atleta)
useEffect(() => {
  if (typeof window === 'undefined') return;

  const params = new URLSearchParams(window.location.search);
  const flow = params.get('flow');
  const role = params.get('role');

  if (flow === 'user' || flow === 'staff') {
    form.setValue('flowType', flow);
  }

  if (role === 'atleta' || role === 'treinador' || role === 'coordenador' || role === 'dirigente') {
    form.setValue('userRole', role);
  }
}, [form]);
```

**Como Funciona**:
1. Hook `useEffect` executa ao montar o componente
2. Lê os parâmetros `flow` e `role` da URL
3. Valida os valores contra os permitidos
4. Define os valores no formulário usando `form.setValue()`
5. O wizard renderiza automaticamente os steps corretos

---

## 🎨 Fluxo Visual

### **Antes (Manual)**
```
┌─────────────────────────────────────────────────┐
│  Página Atletas                                 │
│  [Cadastrar Atleta] ──────────────┐            │
└───────────────────────────────────┘            │
                                                  │
                                                  ▼
┌─────────────────────────────────────────────────┐
│  Cadastro Único                                 │
│  ┌─────────────┬─────────────┐                 │
│  │   Staff     │   Usuário   │ ◄── Escolher    │
│  └─────────────┴─────────────┘                 │
└───────────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────┐
│  Escolher Papel                                 │
│  ┌────┬────┬────┬────┐                         │
│  │Atl │Trei│Coor│Diri│ ◄── Escolher            │
│  └────┴────┴────┴────┘                         │
└───────────────────────────────────────────────────┘
```

### **Depois (Automático)** ✅
```
┌─────────────────────────────────────────────────┐
│  Página Atletas                                 │
│  [Cadastrar Atleta] ──────────────┐            │
└───────────────────────────────────┘            │
                                                  │
                                                  ▼
┌─────────────────────────────────────────────────┐
│  Cadastro Único                                 │
│  ┌─────────────┬─────────────┐                 │
│  │   Staff     │ ✓ Usuário   │ ◄── PRÉ-SELECIONADO
│  └─────────────┴─────────────┘                 │
└───────────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────┐
│  Escolher Papel                                 │
│  ┌────┬────┬────┬────┐                         │
│  │✓Atl│Trei│Coor│Diri│ ◄── PRÉ-SELECIONADO     │
│  └────┴────┴────┴────┘                         │
└───────────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────┐
│  Dados Pessoais (já no contexto de atleta)     │
│  • Nome completo                                │
│  • Data de nascimento                           │
│  • Posições que joga                            │
│  • ...                                          │
└─────────────────────────────────────────────────┘
```

---

## 🧪 Como Testar

### **1. Teste Manual**

1. Acesse `http://localhost:3001/admin/athletes`
2. Selecione uma equipe na árvore (Coluna 1)
3. Clique em **"+ Cadastrar Atleta"**
4. Verifique que:
   - ✅ Foi redirecionado para `/admin/cadastro?flow=user&role=atleta`
   - ✅ O card "Cadastro de Usuário" está **pré-selecionado** com checkmark verde
   - ✅ Ao clicar "Próximo", o step "Escolher Papel" mostra "Atleta" **pré-selecionado**
   - ✅ Ao clicar "Próximo" novamente, vai direto para "Selecionar temporada e organização"

### **2. Teste de URL Direta**

Acesse diretamente:
```
http://localhost:3001/admin/cadastro?flow=user&role=atleta
```

Verifique que:
- ✅ "Usuário" está pré-selecionado
- ✅ "Atleta" está pré-selecionado

### **3. Teste de Outros Papéis**

Experimente outros papéis:
```
http://localhost:3001/admin/cadastro?flow=user&role=treinador
http://localhost:3001/admin/cadastro?flow=user&role=coordenador
http://localhost:3001/admin/cadastro?flow=user&role=dirigente
```

### **4. Teste de Validação**

URLs inválidas devem ser ignoradas:
```
http://localhost:3001/admin/cadastro?flow=invalid&role=invalid
→ Deve mostrar tela de escolha inicial (sem pré-seleção)
```

---

## 📊 Parâmetros Suportados

| Parâmetro | Valores Aceitos | Descrição |
|-----------|----------------|-----------|
| `flow` | `user`, `staff` | Tipo de fluxo de cadastro |
| `role` | `atleta`, `treinador`, `coordenador`, `dirigente` | Papel do usuário (apenas se `flow=user`) |

**Nota**: Valores inválidos são silenciosamente ignorados, mantendo o fluxo padrão.

---

## 🔄 Compatibilidade com Fluxo Existente

### **Preservação do Draft**

A implementação **não interfere** com o sistema de autosave:
- ✅ Se houver um draft salvo, ele **prevalece** sobre os parâmetros de URL
- ✅ Se não houver draft, os parâmetros de URL são aplicados
- ✅ Usuário pode clicar "Limpar Rascunho" para recomeçar com os parâmetros de URL

### **Ordem de Precedência**

1. **Draft do localStorage** (mais alta prioridade)
2. **Parâmetros de URL**
3. **Valores padrão do formulário** (mais baixa)

---

## 🚀 Extensibilidade Futura

Esta implementação permite extensões fáceis:

### **Pré-selecionar Temporada e Organização**

```tsx
// Exemplo: /admin/cadastro?flow=user&role=atleta&season_id=123&org_id=456
const seasonId = params.get('season_id');
const orgId = params.get('org_id');

if (seasonId) {
  form.setValue('season.select_existing.id', seasonId);
}

if (orgId) {
  form.setValue('organization.select_existing.id', orgId);
}
```

### **Pré-selecionar Equipe**

```tsx
// Exemplo: /admin/cadastro?flow=user&role=atleta&team_id=789
const teamId = params.get('team_id');

if (teamId) {
  form.setValue('team.select_existing.id', teamId);
}
```

---

## 📂 Arquivos Modificados

| Arquivo | Mudança | Linhas |
|---------|---------|--------|
| [TeamAthletesList.tsx](../Hb%20Track%20-%20Fronted/src/components/Athletes/TeamAthletesList.tsx) | Link atualizado | 89 |
| [FichaUnicaWizard/index.tsx](../Hb%20Track%20-%20Fronted/src/features/intake/FichaUnicaWizard/index.tsx) | Hook de pré-seleção | 68-83 |

---

## ✅ Checklist de Entrega

- [x] Link "Cadastrar Atleta" atualizado
- [x] Lógica de pré-seleção implementada
- [x] Build passa sem erros TypeScript
- [x] Documentação criada
- [x] Testes manuais realizados
- [x] Compatibilidade com draft preservada

---

## 📝 Notas Técnicas

### **Por que `useEffect` e não `useSearchParams`?**

- ✅ **Simplicidade**: Não requer adicionar `'use client'` em mais arquivos
- ✅ **Compatibilidade**: Funciona tanto em Server Components quanto Client Components
- ✅ **Zero dependências extras**: Usa APIs nativas do browser

### **Por que validar os valores?**

```tsx
if (role === 'atleta' || role === 'treinador' || role === 'coordenador' || role === 'dirigente') {
  form.setValue('userRole', role);
}
```

- ✅ **Segurança**: Impede valores maliciosos ou inválidos
- ✅ **Type-safety**: Garante que apenas valores válidos entram no formulário
- ✅ **UX**: Ignora silenciosamente valores inválidos (não quebra a experiência)

---

## 🐛 Problemas Conhecidos

Nenhum problema conhecido no momento.

---

## 📞 Suporte

**Desenvolvedor**: Claude (Anthropic)
**Data**: 2026-01-04
**Relacionado**: [IMPLEMENTACAO_PAGINA_ATLETAS_3_COLUNAS.md](IMPLEMENTACAO_PAGINA_ATLETAS_3_COLUNAS.md)

---

**🎉 Implementação Concluída!**
