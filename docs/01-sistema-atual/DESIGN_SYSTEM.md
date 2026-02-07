<!-- STATUS: NEEDS_REVIEW -->

# Design System - HB Track

## ⚠️ Sistema de Ícones
Este projeto usa **Lucide React** como sistema de ícones.

---

## 🎨 Fontes Configuradas

### Next.js Fonts (Otimizadas)
```tsx
// As fontes já estão carregadas globalmente no layout
className="font-sans"        // Inter (padrão - corpo de texto)
className="font-heading"     // Manrope (títulos)
className="font-mono"        // JetBrains Mono (código)
```

### Variáveis CSS Disponíveis
```css
font-family: var(--font-inter);
font-family: var(--font-manrope);
font-family: var(--font-jetbrains-mono);
```

---

## 🎯 Ícones (Lucide React)

### Sistema Principal: Lucide React
```tsx
import { Target, Shield, Users, Clock } from 'lucide-react';

function MyComponent() {
  return (
    <div className="flex items-center gap-2">
      <Target className="w-5 h-5 text-brand-500" />
      <span>Gol</span>
    </div>
  );
}
```

### Ícones Comuns para Handebol (Lucide)
```tsx
import {
  Target,        // Gol/Arremesso
  Shield,        // Defesa/Falta
  Users,         // Time
  User,          // Atleta
  Clock,         // Cronômetro
  Activity,      // Estatísticas
  FileText,      // Relatório
  Calendar,      // Calendário
  TrendingUp,    // Performance
  Award,         // Conquistas
  Save,          // Defesa do goleiro
  Slash,         // Turnover
} from 'lucide-react';
```

### Ícones por Módulo

| Módulo | Ícone Principal | Import |
|--------|-----------------|--------|
| Treinos | Clipboard | `import { Clipboard } from 'lucide-react'` |
| Jogos | Volleyball | `import { Volleyball } from 'lucide-react'` |
| Atletas | Users | `import { Users } from 'lucide-react'` |
| Estatísticas | Activity | `import { Activity } from 'lucide-react'` |
| Competições | Trophy | `import { Trophy } from 'lucide-react'` |
| Configurações | Settings | `import { Settings } from 'lucide-react'` |

### Ícones do Módulo Treinos

```tsx
import {
  CalendarDays,   // Agenda Semanal
  Calendar,       // Calendário Mensal
  ClipboardList,  // Planejamento
  ListChecks,     // Banco de Exercícios
  Activity,       // Analytics
  Trophy,         // Rankings
  HeartPulse,     // Eficácia Preventiva
  Settings,       // Configurações
} from 'lucide-react';

// Ícone customizado para área médica
import { Icons } from '@/design-system/icons';
// Icons.Medical para Eficácia Preventiva
```

---

## 🎨 Paleta de Cores HB

### Tokens Principais
```tsx
// Backgrounds e Superfícies
bg-hb-surface      // #ffffff - Superfície branca
bg-hb-background   // #f8fafc - Background principal
bg-hb-active       // #f1f5f9 - Estado ativo/hover

// Bordas
border-hb-border   // #e2e8f0 - Borda padrão

// Textos
text-hb-text       // #0f172a - Texto principal
text-hb-muted      // #64748b - Texto secundário
text-hb-subtle     // #94a3b8 - Texto terciário

// Slate Extra
bg-slate-850       // #151b28 - Background escuro extra
```

### Exemplo de Uso
```tsx
<div className="bg-hb-surface border border-hb-border rounded-lg p-4">
  <h2 className="text-hb-text font-heading">Título</h2>
  <p className="text-hb-muted">Descrição secundária</p>
</div>
```

---

## 🪟 Classes Utilitárias

### Glass Panel (Glassmorphism)
```tsx
<div className="glass-panel rounded-xl p-6">
  {/* Efeito vidro com border e background apropriado */}
</div>
```

### Scrollbar Customizada
```tsx
<div className="custom-scrollbar overflow-auto max-h-96">
  {/* Scrollbar fina e estilizada */}
</div>
```

### Remover Scrollbar
```tsx
<div className="no-scrollbar overflow-auto">
  {/* Sem scrollbar visível */}
</div>
```

---

## 🎭 Modal/Overlay

### Componente Modal
O projeto possui um componente Modal padronizado em `src/components/ui/modal/index.tsx`:

```tsx
import { Modal } from '@/components/ui/modal';

function MyComponent() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <Modal
      isOpen={isOpen}
      onClose={() => setIsOpen(false)}
      className="p-6" // Classes adicionais para o conteúdo
      showCloseButton={true}
      isFullscreen={false}
    >
      <h2 className="text-xl font-heading text-hb-text mb-4">
        Título do Modal
      </h2>
      {/* Conteúdo */}
    </Modal>
  );
}
```

**Props do Modal:**
- `isOpen: boolean` - Estado do modal
- `onClose: () => void` - Callback ao fechar
- `className?: string` - Classes adicionais para o conteúdo
- `showCloseButton?: boolean` - Mostrar botão X (padrão: true)
- `isFullscreen?: boolean` - Modal fullscreen (padrão: false)

**Recursos:**
- ✅ Fecha com ESC
- ✅ Bloqueia scroll do body
- ✅ Backdrop com blur (`.modal-overlay`)
- ✅ Botão de fechar customizável
- ✅ Suporte a fullscreen
- ✅ Z-index padronizado (99999)
- ✅ Efeito glass-panel

### Classes Utilitárias Alternativas
Se preferir criar modais customizados sem o componente:

```tsx
{isOpen && (
  <>
    <div className="modal-overlay" onClick={onClose} />
    <div className="modal-content max-w-md w-full p-6">
      <h2 className="text-xl font-heading text-hb-text mb-4">
        Título do Modal
      </h2>
      {/* Conteúdo */}
    </div>
  </>
)}
```

### Z-Index Layers
```css
--z-index-1: 1;        // Base
--z-index-9: 9;        // Elementos elevados
--z-index-99: 99;      // Dropdowns
--z-index-999: 999;    // Tooltips
--z-index-9999: 9999;  // Modal overlay
--z-index-99999: 99999; // Modal content
```

**Implementação interna:**
O Modal usa as classes `.modal-overlay` e `.modal-content` definidas no design system, garantindo consistência visual em toda a aplicação.

---

## 🌗 Dark Mode

Todos os tokens suportam dark mode automaticamente:

```tsx
// Light: bg-white, Dark: bg-[#111]
<div className="glass-panel">

// Light: bg-hb-background, Dark: bg-[#0a0a0a]
<body className="bg-hb-background dark:bg-[#0a0a0a]">

// Scrollbar dark mode automático
<div className="custom-scrollbar">
```

---

## 📦 Exemplo Completo - Card de Atleta

```tsx
import { User, Target, TrendingUp } from 'lucide-react';

<div className="glass-panel rounded-xl p-6 hover:border-hb-text/20 transition-colors">
  <div className="flex items-center gap-3 mb-4">
    <div className="w-12 h-12 rounded-full bg-brand-50 dark:bg-brand-900/30 flex items-center justify-center">
      <User className="w-6 h-6 text-brand-500" />
    </div>
    <div>
      <h3 className="font-heading text-lg text-hb-text">João Silva</h3>
      <p className="text-sm text-hb-muted">Armador Central</p>
    </div>
  </div>

  <div className="space-y-2">
    <div className="flex items-center gap-2 text-hb-subtle text-sm">
      <Target className="w-4 h-4" />
      <span>32 gols na temporada</span>
    </div>
    <div className="flex items-center gap-2 text-hb-subtle text-sm">
      <TrendingUp className="w-4 h-4" />
      <span>Taxa de conversão: 68%</span>
    </div>
  </div>
</div>
```

---

## 🎯 Boas Práticas

1. **Fontes**: Use `font-heading` (Manrope) para títulos e `font-sans` (Inter) para corpo de texto
2. **Ícones**: Use componentes Lucide React importados diretamente
3. **Cores**: Prefira tokens `hb-*` para consistência visual
4. **Glass Panel**: Use para cards, modais e elementos destacados
5. **Scrollbar**: Aplique `custom-scrollbar` em containers com overflow
6. **Dark Mode**: Sempre teste componentes nos dois temas
7. **Modal**: Use o componente `<Modal />` para consistência de z-index e comportamento

---

## 📚 Documentação Relacionada

- **[TOPBAR.md](./TOPBAR.md)** - Documentação da TopBar e Breadcrumbs
- **[SIDEBAR.md](./SIDEBAR.md)** - Documentação da Sidebar e navegação

---

## 🔧 Configuração Técnica

### Arquivos Configurados
- ✅ `src/app/layout.tsx` - Fontes Next.js (Inter, Manrope, JetBrains Mono)
- ✅ `tailwind.config.js` - Tokens de cores customizados (hb-*, slate-850)
- ✅ `src/app/globals.css` - Estilos base e classes utilitárias
- ✅ `src/components/ui/modal/index.tsx` - Modal padronizado

### Dependencies
```json
{
  "next": "^14.x",
  "tailwindcss": "^3.x",
  "lucide-react": "latest"
}
```

Sistema de ícones: **Lucide React** (já instalado no projeto)
