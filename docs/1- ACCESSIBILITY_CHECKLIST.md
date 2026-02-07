<!-- STATUS: NEEDS_REVIEW -->

# Checklist de Acessibilidade (a11y)

## Objetivo

Este documento define requisitos de acessibilidade para componentes do sistema HB Track, garantindo conformidade com WCAG 2.1 AA e experiência inclusiva para todos os usuários.

## 1. Navegação por Teclado

### Requisitos

- ✅ **Tab**: Navega para próximo elemento interativo
- ✅ **Shift+Tab**: Navega para elemento anterior
- ✅ **Enter/Space**: Ativa botões e links
- ✅ **Escape**: Fecha modais, dropdowns e popovers
- ✅ **Arrow Keys**: Navega em listas, menus e tabs
- ✅ **Home/End**: Vai para início/fim de listas longas

### Checklist de Implementação

- [ ] Todos elementos interativos são acessíveis via Tab
- [ ] Ordem de foco lógica (top-bottom, left-right)
- [ ] Foco visível em todos elementos (focus-visible:ring)
- [ ] Sem armadilhas de foco (focus traps) em modais
- [ ] Atalhos de teclado documentados (tooltip ou hint)

### Exemplos

#### ✅ Correto

```tsx
<Dialog open={open} onOpenChange={setOpen}>
  <DialogTrigger asChild>
    <Button>Abrir Modal</Button>
  </DialogTrigger>
  <DialogContent onEscapeKeyDown={() => setOpen(false)}>
    <DialogTitle>Título</DialogTitle>
    <DialogDescription>Descrição</DialogDescription>
    {/* Conteúdo */}
    <DialogFooter>
      <Button onClick={() => setOpen(false)}>Cancelar</Button>
      <Button onClick={handleSubmit}>Confirmar</Button>
    </DialogFooter>
  </DialogContent>
</Dialog>
```

#### ❌ Incorreto

```tsx
{/* Div clicável sem role ou tabIndex */}
<div onClick={handleClick} className="cursor-pointer">
  Clique aqui
</div>

{/* Focus trap: modal sem botão fechar */}
<Dialog open={open}>
  <DialogContent>
    {/* Sem botão para fechar */}
  </DialogContent>
</Dialog>
```

---

## 2. ARIA Labels e Semântica

### Requisitos

- ✅ **aria-label**: Descreve elementos sem texto visível
- ✅ **aria-labelledby**: Referencia ID do elemento que descreve
- ✅ **aria-describedby**: Referencia descrição adicional (hints, erros)
- ✅ **aria-expanded**: Indica estado de dropdowns/accordions
- ✅ **aria-selected**: Indica item selecionado em listas
- ✅ **aria-live**: Anuncia mudanças dinâmicas (toasts, alerts)

### Checklist de Implementação

- [ ] Ícones sem texto possuem aria-label
- [ ] Botões descritivos (não "Clique aqui", mas "Remover Treinador")
- [ ] Campos de formulário associados a labels via htmlFor/id
- [ ] Erros de validação com aria-describedby
- [ ] Toasts e alerts com role="alert" ou aria-live="polite"

### Exemplos

#### ✅ Correto

```tsx
{/* Botão com ícone + aria-label */}
<Button
  variant="ghost"
  size="icon"
  onClick={handleDelete}
  aria-label="Remover membro da equipe"
>
  <Trash2 className="w-4 h-4" />
</Button>

{/* Campo com erro descrito */}
<div>
  <Label htmlFor="email">Email</Label>
  <Input
    id="email"
    aria-describedby={error ? "email-error" : undefined}
    aria-invalid={error ? "true" : "false"}
  />
  {error && (
    <p id="email-error" className="text-sm text-red-600">
      {error}
    </p>
  )}
</div>

{/* Dropdown com aria-expanded */}
<DropdownMenu>
  <DropdownMenuTrigger aria-expanded={open} aria-haspopup="menu">
    Opções
  </DropdownMenuTrigger>
  <DropdownMenuContent>
    <DropdownMenuItem>Item 1</DropdownMenuItem>
  </DropdownMenuContent>
</DropdownMenu>
```

#### ❌ Incorreto

```tsx
{/* Ícone sem descrição */}
<Button onClick={handleDelete}>
  <Trash2 />
</Button>

{/* Label não associado */}
<Label>Email</Label>
<Input />

{/* Dropdown sem aria-expanded */}
<button onClick={toggleMenu}>Menu</button>
{open && <ul>{items}</ul>}
```

---

## 3. Contraste de Cores (WCAG AA)

### Requisitos

- ✅ **Texto normal**: Contraste mínimo 4.5:1
- ✅ **Texto grande** (18px+ ou 14px+ bold): Contraste mínimo 3:1
- ✅ **Elementos interativos**: Contraste mínimo 3:1 (bordas, ícones)
- ✅ **Estados hover/focus**: Contraste suficiente para diferenciar

### Checklist de Implementação

- [ ] Usar cores do design system (text-slate-900, text-slate-700)
- [ ] Evitar text-slate-400 em backgrounds claros (contraste insuficiente)
- [ ] Estados disabled com opacity >= 0.5
- [ ] Links diferenciados por mais que cor (underline ou ícone)
- [ ] Validar contrastes com ferramenta: https://webaim.org/resources/contrastchecker/

### Exemplos

#### ✅ Correto

```tsx
{/* Texto com contraste adequado */}
<p className="text-slate-900">Texto principal</p>
<p className="text-slate-600">Texto secundário</p>

{/* Badge com contraste */}
<Badge className="bg-green-100 text-green-800">Ativo</Badge>

{/* Link com underline */}
<a href="#" className="text-brand-600 underline hover:text-brand-700">
  Saiba mais
</a>
```

#### ❌ Incorreto

```tsx
{/* Contraste insuficiente */}
<p className="text-slate-400">Texto importante</p>

{/* Badge sem contraste */}
<Badge className="bg-gray-200 text-gray-300">Status</Badge>

{/* Link apenas com cor */}
<a href="#" className="text-blue-500">
  Link
</a>
```

---

## 4. Focus Visible

### Requisitos

- ✅ **Ring**: Outline colorido visível ao focar (focus-visible:ring-2)
- ✅ **Cor**: Ring da cor principal (ring-brand-500 ou ring-ring)
- ✅ **Offset**: Espaço entre elemento e ring (ring-offset-2)
- ✅ **Exclusão**: Apenas quando foco via teclado (focus-visible, não focus)

### Checklist de Implementação

- [ ] Todos inputs/buttons com focus-visible:ring
- [ ] Ring com cor de alto contraste
- [ ] Ring offset para não sobrepor bordas
- [ ] Não usar outline: none sem substituir por ring

### Exemplos

#### ✅ Correto

```tsx
{/* Input com focus ring */}
<Input
  className="focus-visible:ring-2 focus-visible:ring-brand-500 focus-visible:ring-offset-2"
/>

{/* Button com focus ring */}
<Button
  className="focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
>
  Confirmar
</Button>
```

#### ❌ Incorreto

```tsx
{/* Ring removido sem substituição */}
<Input className="focus:outline-none" />

{/* Focus apenas, não focus-visible (aparece ao clicar) */}
<Button className="focus:ring-2 focus:ring-blue-500">Botão</Button>
```

---

## 5. Screen Reader Friendly

### Requisitos

- ✅ **Texto alternativo**: Ícones e imagens com alt ou aria-label
- ✅ **Mensagens de erro**: Descritivas e associadas aos campos
- ✅ **Status dinâmico**: Anunciado via aria-live
- ✅ **Landmarks**: Header, nav, main, footer para navegação rápida
- ✅ **Skip links**: Pular para conteúdo principal

### Checklist de Implementação

- [ ] Imagens decorativas com alt="" (ignoradas)
- [ ] Imagens informativas com alt descritivo
- [ ] Avisos com role="alert" ou aria-live="assertive"
- [ ] Status com aria-live="polite"
- [ ] Breadcrumbs com nav e aria-label="Breadcrumb"

### Exemplos

#### ✅ Correto

```tsx
{/* Imagem com alt */}
<img src="logo.png" alt="HB Track - Sistema de Gestão Esportiva" />

{/* Ícone decorativo (sr-only para screen readers) */}
<AlertCircle className="w-4 h-4" aria-hidden="true" />
<span className="sr-only">Aviso:</span>

{/* Toast com role alert */}
<Toast role="alert" aria-live="assertive" aria-atomic="true">
  <ToastTitle>Erro</ToastTitle>
  <ToastDescription>Email já cadastrado</ToastDescription>
</Toast>

{/* Status dinâmico */}
<div aria-live="polite" aria-atomic="true">
  {loading ? "Carregando..." : `${items.length} itens encontrados`}
</div>
```

#### ❌ Incorreto

```tsx
{/* Imagem sem alt */}
<img src="logo.png" />

{/* Ícone sem contexto */}
<AlertCircle className="w-4 h-4" />
<p>Atenção</p>

{/* Mudança de estado sem anúncio */}
<div>{loading ? <Spinner /> : <Content />}</div>
```

---

## 6. Semântica HTML

### Requisitos

- ✅ **Botões**: `<button>` para ações, não `<div>`
- ✅ **Links**: `<a>` para navegação, não `<button>`
- ✅ **Formulários**: `<form>` com `<label>` associados
- ✅ **Listas**: `<ul>`/`<ol>`/`<li>` para listas, não divs
- ✅ **Cabeçalhos**: Hierarquia lógica (h1 → h2 → h3)

### Checklist de Implementação

- [ ] Botões com type="button" (não submit se dentro de form)
- [ ] Links com href válido (não #)
- [ ] Labels associados via htmlFor/id
- [ ] Listas semânticas para dados tabulares
- [ ] Apenas um h1 por página

### Exemplos

#### ✅ Correto

```tsx
{/* Botão semântico */}
<button type="button" onClick={handleClick}>
  Clique aqui
</button>

{/* Link semântico */}
<a href="/teams/123">Ver Equipe</a>

{/* Form com labels */}
<form onSubmit={handleSubmit}>
  <Label htmlFor="name">Nome</Label>
  <Input id="name" name="name" />
  <Button type="submit">Enviar</Button>
</form>

{/* Lista semântica */}
<ul>
  {items.map((item) => (
    <li key={item.id}>{item.name}</li>
  ))}
</ul>
```

#### ❌ Incorreto

```tsx
{/* Div clicável */}
<div onClick={handleClick} className="cursor-pointer">
  Clique aqui
</div>

{/* Botão como link */}
<button onClick={() => router.push('/teams')}>Ver Equipe</button>

{/* Input sem label */}
<Input placeholder="Nome" />

{/* Lista como divs */}
<div>
  {items.map((item) => (
    <div key={item.id}>{item.name}</div>
  ))}
</div>
```

---

## 7. Testes de Acessibilidade

### Ferramentas

1. **axe DevTools** (Chrome/Firefox extension)
   - Scan automático de problemas a11y
   - Sugestões de correção

2. **Lighthouse** (Chrome DevTools)
   - Auditoria de acessibilidade
   - Score 90+ como meta

3. **Screen Readers**
   - **NVDA** (Windows) - grátis
   - **JAWS** (Windows) - pago
   - **VoiceOver** (macOS/iOS) - integrado

4. **Keyboard Testing**
   - Desconectar mouse
   - Navegar apenas com teclado
   - Testar todos fluxos críticos

### Checklist de Testes

- [ ] Scan com axe DevTools (zero issues críticos)
- [ ] Lighthouse Accessibility Score >= 90
- [ ] Navegação completa por teclado (sem mouse)
- [ ] Teste com screen reader (NVDA ou VoiceOver)
- [ ] Teste de contraste com ferramenta online
- [ ] Teste com zoom 200% (layout não quebra)

---

## 8. Componentes Comuns

### Modais (Dialog)

```tsx
<Dialog open={open} onOpenChange={setOpen}>
  <DialogTrigger asChild>
    <Button>Abrir</Button>
  </DialogTrigger>
  <DialogContent 
    aria-describedby="dialog-description"
    onEscapeKeyDown={() => setOpen(false)}
  >
    <DialogTitle>Remover Membro</DialogTitle>
    <DialogDescription id="dialog-description">
      Esta ação não pode ser desfeita. O membro será removido permanentemente.
    </DialogDescription>
    <DialogFooter>
      <Button variant="ghost" onClick={() => setOpen(false)}>
        Cancelar
      </Button>
      <Button variant="destructive" onClick={handleConfirm}>
        Remover
      </Button>
    </DialogFooter>
  </DialogContent>
</Dialog>
```

### Dropdowns (DropdownMenu)

```tsx
<DropdownMenu>
  <DropdownMenuTrigger asChild>
    <Button variant="ghost" size="icon" aria-label="Mais opções">
      <MoreVertical className="w-4 h-4" />
    </Button>
  </DropdownMenuTrigger>
  <DropdownMenuContent align="end">
    <DropdownMenuItem onSelect={handleEdit}>
      <Edit className="w-4 h-4 mr-2" />
      Editar
    </DropdownMenuItem>
    <DropdownMenuItem 
      onSelect={handleDelete}
      className="text-red-600"
    >
      <Trash2 className="w-4 h-4 mr-2" />
      Remover
    </DropdownMenuItem>
  </DropdownMenuContent>
</DropdownMenu>
```

### Toasts (Sonner)

```tsx
import { toast } from "sonner";

// Toast simples
toast.success("Membro removido com sucesso");

// Toast com ação
toast.error("Equipe sem treinador", {
  duration: 7000,
  action: {
    label: "Adicionar Treinador",
    onClick: () => setOpenAddCoachModal(true),
  },
});

// Toast com descrição
toast.info("Convite reenviado", {
  description: "Email enviado para joao@example.com",
});
```

### Badges

```tsx
{/* Badge com contraste adequado */}
<Badge className="bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
  Ativo
</Badge>

<Badge className="bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200">
  Pendente
</Badge>

<Badge className="bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200">
  Inativo
</Badge>
```

---

## 9. Recursos e Referências

### Documentação

- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [MDN Accessibility](https://developer.mozilla.org/en-US/docs/Web/Accessibility)
- [shadcn/ui Accessibility](https://ui.shadcn.com/docs/guides/accessibility)
- [Radix UI Primitives](https://www.radix-ui.com/primitives/docs/overview/accessibility)

### Ferramentas Online

- [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/)
- [WAVE Web Accessibility Evaluation Tool](https://wave.webaim.org/)
- [Accessible Colors](https://accessible-colors.com/)

### Extensões

- [axe DevTools](https://www.deque.com/axe/devtools/)
- [Lighthouse](https://developers.google.com/web/tools/lighthouse)
- [WAVE Extension](https://wave.webaim.org/extension/)

---

## 10. Checklist Geral (Copy-Paste para PRs)

```markdown
## Accessibility Checklist

- [ ] Navegação por teclado funcional (Tab, Enter, Esc, Arrow keys)
- [ ] Ordem de foco lógica e sem armadilhas
- [ ] ARIA labels em ícones e elementos interativos
- [ ] Contraste de cores >= 4.5:1 (texto normal)
- [ ] Focus visible em todos elementos interativos
- [ ] Mensagens de erro associadas via aria-describedby
- [ ] Semântica HTML correta (button, a, form, label)
- [ ] Toasts e alerts com role="alert"
- [ ] Scan com axe DevTools (zero issues críticos)
- [ ] Teste de navegação sem mouse
- [ ] Lighthouse Accessibility Score >= 90
```

---

**Última atualização:** 2026-01-15  
**Autor:** GitHub Copilot  
**Revisão:** Equipe Frontend HB Track
