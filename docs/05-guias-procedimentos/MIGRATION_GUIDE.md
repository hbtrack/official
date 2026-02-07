<!-- STATUS: NEEDS_REVIEW -->

# Guia de Migração - Design System HB Track

## 📋 Status Atual

### ✅ O que já está configurado
- Fontes Next.js (Inter, Manrope, JetBrains Mono)
- Material Symbols Outlined (via CDN e classe CSS)
- Tokens de cores HB customizados no Tailwind
- Classes utilitárias (glass-panel, custom-scrollbar, modal-overlay, modal-content)

### 🔍 O que encontramos no projeto

#### 1. Sistema de Ícones Atual
O projeto **já usa Lucide React** (não Material Symbols):
- Arquivo: [src/icons/index.tsx](c:/HB TRACK/Hb Track - Fronted/src/icons/index.tsx)
- SVGs customizados importados
- Componentes Lucide em uso (ex: `<Keyboard />`, `<Target />`)

#### 2. Componente Modal Existente
Arquivo: [src/components/ui/modal/index.tsx](c:/HB TRACK/Hb Track - Fronted/src/components/ui/modal/index.tsx)
- **Já tem backdrop**: `bg-gray-400/50 backdrop-blur-[32px]` (linha 61)
- **Já tem z-index**: `z-99999` (linha 58)
- **Não usa** as classes `modal-overlay` e `modal-content` que criamos

---

## 🎯 Opções de Migração

### Opção A: Manter Lucide Icons (Recomendado)
**Prós:**
- Já está em uso em todo o projeto
- Componentes React tipados
- Melhor integração com TypeScript
- Tree-shaking automático

**Contras:**
- Material Symbols configurado mas não será usado

**Ação:**
- ✅ Manter Lucide React como está
- ⚠️ Remover import de Material Symbols do layout/globals.css (opcional)
- 📝 Documentar Lucide como sistema oficial

### Opção B: Migrar para Material Symbols
**Prós:**
- Usa a configuração que acabamos de criar
- Fonte de ícones do Google (mais leve via CDN)

**Contras:**
- Requer refatorar todos os componentes
- Trabalho manual em ~65 arquivos
- Perde type-safety do Lucide

**Ação:**
- 🔄 Substituir imports de Lucide por spans Material
- Exemplo: `<Keyboard />` → `<span className="material-symbols-outlined">keyboard</span>`

### Opção C: Híbrido (Usar ambos)
**Prós:**
- Flexibilidade para escolher
- Mantém código existente

**Contras:**
- Dois sistemas de ícones (confusão)
- Bundle maior

---

## 🔧 Atualizações Recomendadas

### 1. Atualizar Componente Modal (Opcional)

Para usar as classes padronizadas que criamos:

**Antes** (src/components/ui/modal/index.tsx:58-64):
```tsx
<div className="fixed inset-0 flex items-center justify-center overflow-y-auto modal z-99999">
  <div
    className="fixed inset-0 h-full w-full bg-gray-400/50 backdrop-blur-[32px]"
    onClick={onClose}
  ></div>
  <div ref={modalRef} className={`${contentClasses} ${className}`}>
    {/* ... */}
  </div>
</div>
```

**Depois** (usando nossas classes):
```tsx
<div className="fixed inset-0 flex items-center justify-center overflow-y-auto">
  <div className="modal-overlay" onClick={onClose}></div>
  <div ref={modalRef} className={`modal-content ${className}`}>
    {/* ... */}
  </div>
</div>
```

**Benefícios:**
- Consistência com design system
- Menos código inline
- Fácil customização global

### 2. Atualizar Backdrop Component

**Antes** (src/layout/Backdrop.tsx:10-14):
```tsx
<div
  className="fixed inset-0 z-40 bg-gray-900/50 lg:hidden"
  onClick={toggleMobileSidebar}
/>
```

**Depois**:
```tsx
<div
  className="modal-overlay lg:hidden"
  style={{ zIndex: 40 }}
  onClick={toggleMobileSidebar}
/>
```

---

## 📝 Recomendação Final

### Para seu projeto, recomendamos:

1. **Manter Lucide Icons** como sistema principal
   - Já está implementado e funcionando
   - Melhor DX com TypeScript
   - Componentes React nativos

2. **Manter Material Symbols** disponível para casos específicos
   - Útil para ícones que Lucide não tem
   - Pode ser usado via className quando necessário

3. **Atualizar componente Modal** (opcional mas recomendado)
   - Use as classes `modal-overlay` e `modal-content`
   - Padroniza z-index e backdrop
   - Facilita manutenção futura

4. **Atualizar DESIGN_SYSTEM.md**
   - Documentar que Lucide é o sistema principal
   - Manter Material Symbols como alternativa

---

## 🚀 Próximos Passos

### Curto Prazo
- [ ] Decidir se mantém ou remove Material Symbols
- [ ] Atualizar componente Modal para usar classes padronizadas
- [ ] Revisar Backdrop component

### Médio Prazo
- [ ] Criar biblioteca de ícones comuns do handebol usando Lucide
- [ ] Padronizar tamanhos de ícones (sm, md, lg, xl)
- [ ] Criar componente `<Icon />` wrapper

### Exemplo de Biblioteca de Ícones Handebol com Lucide
```tsx
// src/icons/handball-icons.tsx
import {
  Target,      // → Gol/Arremesso
  Shield,      // → Defesa/Falta
  Users,       // → Time
  User,        // → Atleta
  Clock,       // → Tempo/Cronômetro
  Activity,    // → Estatísticas
  FileText,    // → Relatório
  Calendar,    // → Calendário
  TrendingUp,  // → Performance
  Award,       // → Conquistas
} from 'lucide-react';

export const HandballIcons = {
  goal: Target,
  defense: Shield,
  team: Users,
  athlete: User,
  timer: Clock,
  stats: Activity,
  report: FileText,
  schedule: Calendar,
  performance: TrendingUp,
  achievement: Award,
};
```

---

## 🔗 Arquivos Relevantes

- Modal: [src/components/ui/modal/index.tsx](c:/HB TRACK/Hb Track - Fronted/src/components/ui/modal/index.tsx)
- Backdrop: [src/layout/Backdrop.tsx](c:/HB TRACK/Hb Track - Fronted/src/layout/Backdrop.tsx)
- Icons: [src/icons/index.tsx](c:/HB TRACK/Hb Track - Fronted/src/icons/index.tsx)
- Layout: [src/app/layout.tsx](c:/HB TRACK/Hb Track - Fronted/src/app/layout.tsx)
- Globals CSS: [src/app/globals.css](c:/HB TRACK/Hb Track - Fronted/src/app/globals.css)
- Tailwind Config: [tailwind.config.js](c:/HB TRACK/Hb Track - Fronted/tailwind.config.js)
