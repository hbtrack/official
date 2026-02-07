<!-- STATUS: NEEDS_REVIEW -->

# ✅ Checklist de Testes - Página de Atletas (3 Colunas)

## 🚀 Servidor de Desenvolvimento

**URL**: http://localhost:3001/admin/athletes

---

## 1️⃣ TESTES DE INTERFACE E NAVEGAÇÃO

### **Coluna 1: Tree View (Organização → Equipes)**

- [ ] Organização é exibida corretamente
- [ ] Ícone de pasta (aberta/fechada) muda ao expandir/recolher
- [ ] Equipes da organização são carregadas do backend
- [ ] Apenas equipes com `is_our_team = true` aparecem
- [ ] Ao clicar em "Relação de Atletas", a equipe é selecionada
- [ ] Equipe selecionada tem destaque visual (background brand)
- [ ] Loading spinner aparece durante carregamento

**❌ Casos de erro a testar:**
- [ ] Mensagem de erro se API falhar
- [ ] Mensagem "Nenhuma equipe cadastrada" se não houver equipes
- [ ] Mensagem "Usuário não autenticado" se não estiver logado

---

### **Coluna 2: Lista de Atletas**

- [ ] Mensagem "Selecione uma equipe" aparece inicialmente
- [ ] Lista de atletas é carregada ao selecionar equipe
- [ ] Foto do perfil aparece (ou inicial do nome)
- [ ] Nome da atleta aparece corretamente
- [ ] Badge verde (●) aparece para vínculos ativos
- [ ] Ícone 👁️ (Eye) aparece ao lado de cada atleta
- [ ] Atleta selecionada tem destaque visual
- [ ] Contador mostra número correto de atletas

**🎯 Estado Vazio (quando equipe não tem atletas):**
- [ ] Ícone de "Users" aparece
- [ ] Mensagem orientada aparece
- [ ] Botão "+ Cadastrar Atleta" funciona (redireciona para `/admin/athletes/new`)
- [ ] Botão "Importar Planilha" funciona (redireciona para `/admin/athletes/import`)

**❌ Casos de erro a testar:**
- [ ] Mensagem de erro se API falhar ao carregar atletas
- [ ] Loading spinner durante carregamento

---

### **Coluna 3: Sidebar (Ficha da Atleta)**

#### **Abertura e Fechamento**
- [ ] Sidebar abre ao clicar em 👁️ Visualizar
- [ ] Overlay escuro aparece atrás da sidebar
- [ ] Sidebar fecha ao clicar no X
- [ ] Sidebar fecha ao clicar no overlay
- [ ] Sidebar fecha ao pressionar **Escape** no teclado ⌨️
- [ ] Ao trocar de equipe, sidebar fecha automaticamente

#### **Loading e Skeleton**
- [ ] Skeleton animado aparece durante carregamento
- [ ] Skeleton tem estrutura visual coerente (foto, títulos, seções)

#### **Conteúdo da Ficha**
- [ ] Foto do perfil aparece (ou inicial)
- [ ] Nome da atleta aparece
- [ ] Apelido aparece (se existir)
- [ ] Badge de estado (ativa, inativa, etc.)
- [ ] Badge de elegibilidade (✓ Pode jogar / ✗ Indisponível)
- [ ] Alertas de restrições aparecem (fundo vermelho)
- [ ] Alertas de avisos aparecem (fundo amarelo)
- [ ] Flags de restrição aparecem (🏥 Lesionada, ⚠️ Restrição Médica, etc.)
- [ ] Dados pessoais estão corretos
- [ ] Dados de contato estão corretos
- [ ] Dados esportivos estão corretos
- [ ] Vínculos com equipes aparecem
- [ ] Badge "Ativo/Encerrado" correto para cada vínculo

#### **Botões de Ação**
- [ ] Link "Abrir ficha completa" redireciona para `/admin/athletes/[id]`
- [ ] Botão "Editar" redireciona para `/admin/athletes/[id]/edit`
- [ ] Botão "Deletar" aparece habilitado se não houver vínculos ativos
- [ ] Botão "Deletar" aparece **desabilitado** se houver vínculos ativos
- [ ] Tooltip explica por que deletar está bloqueado
- [ ] Mensagem de aviso aparece abaixo dos botões quando bloqueado

**❌ Casos de erro a testar:**
- [ ] Mensagem de erro aparece se API falhar
- [ ] Ícone de alerta vermelho aparece no erro

---

## 2️⃣ TESTES DE FUNCIONALIDADE

### **Persistência de Contexto**
- [ ] Ao selecionar uma equipe, ela é salva no `localStorage`
- [ ] Ao recarregar a página (F5), a última equipe selecionada é pré-carregada
- [ ] Ao navegar para outra página e voltar, a equipe continua selecionada

**Como testar:**
1. Selecione uma equipe
2. Abra DevTools → Application → Local Storage
3. Verifique se existe `hb_athletes_last_team` com `{ teamId, teamName }`
4. Recarregue a página e confirme que a equipe é automaticamente selecionada

---

### **Exclusão de Atleta**

#### **Atleta SEM vínculos ativos**
- [ ] Botão "Deletar" está **habilitado** (vermelho)
- [ ] Ao clicar, confirmação aparece com mensagem clara
- [ ] Ao confirmar, atleta é deletada do backend
- [ ] Sidebar fecha automaticamente
- [ ] Lista de atletas é atualizada (atleta removida)

#### **Atleta COM vínculos ativos**
- [ ] Botão "Deletar" está **desabilitado** (cinza)
- [ ] Tooltip explica o bloqueio
- [ ] Mensagem de aviso aparece abaixo
- [ ] Ao clicar, alerta explica que vínculos devem ser encerrados primeiro

---

### **Edição de Atleta**
- [ ] Botão "Editar" redireciona para `/admin/athletes/[id]/edit`
- [ ] Página de edição abre corretamente
- [ ] Após editar e salvar, ao voltar para `/admin/athletes`, mudanças refletem

---

## 3️⃣ TESTES DE ACESSIBILIDADE

### **Navegação por Teclado**
- [ ] Tab funciona para navegar entre elementos
- [ ] Enter/Space funcionam para clicar em botões
- [ ] Escape fecha a sidebar
- [ ] Focus visível (anel azul) aparece em todos os botões interativos

### **Atributos ARIA**
- [ ] Sidebar tem `role="dialog"` e `aria-modal="true"`
- [ ] Botão fechar tem `aria-label="Fechar sidebar"`
- [ ] Botão deletar tem `aria-label` descritivo
- [ ] Tooltips (`title`) estão presentes em ícones

---

## 4️⃣ TESTES DE API E DADOS

### **Endpoints que devem funcionar:**

1. **GET `/api/v1/teams`** (filtrado por `organization_id`)
   - [ ] Retorna equipes da organização do usuário
   - [ ] Campo `is_our_team = true` presente

2. **GET `/api/v1/teams/{team_id}/registrations`**
   - [ ] Retorna atletas vinculadas à equipe
   - [ ] Inclui campo `athlete.full_name`
   - [ ] Inclui campos `start_at` e `end_at`
   - [ ] Parâmetro `active_only=true` funciona

3. **GET `/api/v1/athletes/{athlete_id}`**
   - [ ] Retorna dados completos da atleta
   - [ ] Inclui `team_registrations` expandido
   - [ ] Inclui campos de elegibilidade

4. **DELETE `/api/v1/athletes/{athlete_id}`**
   - [ ] Aceita `reason` no body
   - [ ] Retorna 204 (sem conteúdo) em sucesso
   - [ ] Retorna 403/400 se atleta tiver vínculos críticos

---

## 5️⃣ TESTES DE RESPONSIVIDADE

- [ ] Em desktop (>= 1024px): 3 colunas lado a lado
- [ ] Sidebar ocupa `480px` de largura
- [ ] Coluna 1 (Tree) ocupa `320px`
- [ ] Coluna 2 (Lista) ocupa espaço restante
- [ ] Em mobile: sidebar ocupa `100%` da largura

---

## 6️⃣ TESTES DE PERMISSÕES

### **Verificar se permissões do backend são respeitadas:**

- [ ] Usuário sem permissão `view_athletes` não acessa a página
- [ ] Usuário sem permissão `manage_athletes` não vê botão "Editar"
- [ ] Usuário sem permissão `delete_athletes` não vê botão "Deletar"

**Como testar:**
1. Faça login com diferentes roles (treinador, coordenador, dirigente)
2. Verifique se as ações disponíveis mudam conforme permissões

---

## 7️⃣ TESTES DE CASOS EXTREMOS

### **Equipe com muitos atletas (> 50)**
- [ ] Scroll funciona na lista
- [ ] Performance é aceitável
- [ ] Não há lag ao selecionar atleta

### **Atleta com nome muito longo**
- [ ] Nome é truncado com `...` (ellipsis)
- [ ] Não quebra layout

### **Atleta sem dados opcionais**
- [ ] Campos vazios mostram `-` ou mensagem adequada
- [ ] Não exibe campos `null` ou `undefined`

### **Conexão lenta/offline**
- [ ] Loading spinner aparece
- [ ] Mensagem de erro amigável ao falhar

---

## 8️⃣ CHECKLIST DE FOTOS DE ATLETAS

**Status atual**: Campo `athlete_photo_path` existe, mas não é populado pela API.

### **Quando API retornar fotos:**

- [ ] Verificar se campo `athlete.athlete_photo_path` está presente no response de `/athletes/{id}`
- [ ] Verificar se campo está presente em `/teams/{team_id}/registrations`
- [ ] Atualizar componente se necessário (já está preparado para receber)

**Código já preparado em:**
- [TeamAthletesList.tsx:123](TeamAthletesList.tsx#L123) - `athletePhoto = null; // TODO`
- [AthleteDetailSidebar.tsx:133](AthleteDetailSidebar.tsx#L133) - Já renderiza se existir

---

## 9️⃣ VALIDAÇÃO DE REGRAS DE NEGÓCIO

### **Referências REGRAS.md:**

- [ ] **RF1.1**: Atleta pode existir sem equipe (verificar se lista carrega mesmo sem `team_registration`)
- [ ] **R32**: Atleta sem `team_registration` aparece na lista mas não opera
- [ ] **R12/R13**: Estados e flags da atleta aparecem corretamente
- [ ] **R15**: Categoria natural e elegibilidade calculadas corretamente
- [ ] **R24/R25**: Permissões por papel respeitadas

---

## 🎯 RESUMO DE PRIORIDADES

### **Alta Prioridade** 🔴
1. ✅ Navegação funcional entre colunas
2. ✅ Carregamento de dados do backend
3. ✅ Botões de ação funcionais (Editar, Deletar)
4. ✅ Proteção contra exclusão indevida

### **Média Prioridade** 🟡
5. ✅ Persistência de contexto
6. ✅ Estados vazios orientados
7. ⏳ Fotos de atletas (aguardando API)

### **Baixa Prioridade** 🟢
8. ⏳ Toast de Undo após exclusão (não implementado)
9. ✅ Acessibilidade completa

---

## ✅ CHECKLIST FINAL DE ENTREGA

Antes de marcar como concluído, validar:

- [ ] Todos os testes funcionais passaram
- [ ] Nenhum erro no console do navegador
- [ ] Nenhum erro no terminal do servidor
- [ ] Performance aceitável (< 2s para carregar lista)
- [ ] UX fluida e intuitiva
- [ ] Código limpo e documentado

---

## 📝 OBSERVAÇÕES E BUGS ENCONTRADOS

_Anote aqui qualquer problema encontrado durante os testes:_

```
[Data] - [Descrição do bug] - [Prioridade]
Exemplo:
2026-01-04 - Ao deletar atleta, lista não atualiza - ALTA
```

---

**Última atualização**: 2026-01-04
**Responsável pelos testes**: [Seu nome]
**Status**: ⏳ Em andamento
