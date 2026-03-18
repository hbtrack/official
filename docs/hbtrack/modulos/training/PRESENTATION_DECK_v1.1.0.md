---
document: "PRESENTATION_DECK"
module: "training"
version: "1.1.0"
date: "2026-03-17"
format: "Markdown Slides"
---

# 🎯 UI Contract Training v1.1.0
## Apresentação para Sign-off

**Módulo:** training  
**Status:** validated_contract → implementation_ready (pendente aprovação)  
**Data:** 2026-03-17  
**Audience:** Product Owner, UX Designer, Engineering Lead

---

## Slide 1: O Que Está Acontecendo

### Onde Estamos

```
🟡 training = validated_contract
   (único módulo pronto para implementação)

15 módulos restantes = draft_contract
   (contratos básicos presentes; aguardando validação)
```

### O Que Precisamos

✅ **Validação final de 3 estruturas críticas:**
1. 5 User Interaction Flows (UIFs) — Operacionalmente viável?
2. Design Decisions (9 decisões) — Alinhadas com negócio?
3. Stack Frontend (Next.js + PWA) — Tecnicamente viável?

**Se aprovado:** Implementação começa em 2–3 dias (phases 1–7, ~14 semanas)

---

## Slide 2: 5 User Interaction Flows

### O Que o Coach Faz (Desktop)

```
[Coach — Modo Escritório]
┌─────────────────────────────────┐
│ UIF-001: Planejamento           │  ← Criar / configurar sessão
│          + Recomendações        │     com objetivos e blocos
├─────────────────────────────────┤
│ UIF-003: Revisão Pós-Sessão     │  ← Review de execução,
│          + Feedback + Alertas   │     feedback e intervenções
├─────────────────────────────────┤
│ UIF-005: Load Chart             │  ← Carga × recuperação
│          (ATL/CTL)              │     (periodização)
└─────────────────────────────────┘

[Coach — Modo Quadra (Mobile PWA)]
┌─────────────────────────────────┐
│ UIF-004: Team Readiness         │  ← Visão de equipe inteira
│          [**Tela Primária**]    │     antes de treinar
└─────────────────────────────────┘
```

### O Que o Atleta Faz (Mobile)

```
[Atleta — Modo Quadra (Mobile PWA)]
┌─────────────────────────────────┐
│ UIF-002: Check-in Pré-Treino    │  ← Wellness + readiness
│          (< 60 segundos)        │     + ineligibilidades
└─────────────────────────────────┘
```

**Total:** 24 telas, 34 endpoints, 100% mapeados

---

## Slide 3: O Problema Que Resolvemos (D-UI-SP-02)

### ❌ Forma Tradicional (Rejeitar)
```
Coach chega na quadra
    ↓
Abre app → tela individual de atleta (1 de N)
    ↓
Sem visão de equipe → perde contexto
    ↓
Não vê exceções automaticamente
    ↓
❌ Ineficiente
```

### ✅ Nossa Solução
```
Coach chega na quadra
    ↓
Abre PWA → [UIF-004] Team Readiness OVERVIEW
    ↓
VÊ TODA EQUIPE DE UMA VEZ
    ↓
BLOCO DE EXCEÇÃO NO TOPO (autom. destacado)
  • Readiness < 40 (vermelho)
  • Inelegibilidade (cinza)
  • Sem check-in (âmbar)
  • Demais atletas (verde) → scroll abaixo
    ↓
✅ Visão tática em 5 segundos
```

**[D-UI-SP-02] Decisão de Design Crucial:**  
> _"Tela primária do coach no quadra é equipe, não indivíduo."_

---

## Slide 4: Readiness Score (D-UI-SP-01)

### Métrica Central da Plataforma

$$\text{readiness} = \frac{\text{sleep} + \text{mood} + \text{heart\_rate} + \text{fatigue}}{4}$$

**Escala:** 0–100

### Cores Semânticas

| Score | Cor | Significado | Ação |
|-------|-----|-------------|------|
| ≥ 70 | 🟢 Verde | Pronto | Sessão normal |
| 40–69 | 🟠 Âmbar | Atenção | Ajustar intensidade |
| < 40 | 🔴 Vermelho | Crítico | ⚠️ Alerta automático |

### Implementação: Progressive Disclosure

```
[Primeira Camada] (Quadra — 5 seg)
┌──────────────────┐
│ 🟢 78             │  ← 1 cor + 1 número
│ João da Silva    │
└──────────────────┘

[Segunda Camada] (Um toque)
┌──────────────────────────────┐
│ 🟢 Readiness: 78             │
├──────────────────────────────┤
│ Sono:      25% ████░░░░    │
│ Humor:     25% ████░░░░    │
│ FC Repouso: 25% ████░░░░    │
│ Fadiga:    25% ████░░░░    │
├──────────────────────────────┤
│ Histórico:                   │
│ 73 — 71 — 78 ╱╲╱╲ sparkline │
└──────────────────────────────┘
```

**Padrão:** Kitman Labs, Whoop, Catapult

---

## Slide 5: Stack Frontend (D-UI-18)

### Arquitetura Unificada

```
┌────────────────────────────────────────┐
│ NEXT.JS 14 (App Router + SSR)          │
│ ✅ Performance em redes de ginásio     │
│ ✅ File-based routing (sem config)     │
├────────────────────────────────────────┤
│ SHADCN/UI + TAILWIND CSS               │
│ ✅ Componentes acessíveis (WCAG AA)    │
│ ✅ Open-source (sem vendor lock-in)    │
│ ✅ Dark mode nativo                    │
├────────────────────────────────────────┤
│ RECHARTS (UIF-005 Load Chart)          │
│ DND-KIT (UIF-001 Drag-and-drop)        │
├────────────────────────────────────────┤
│ next-pwa (PWA | Installable)           │
│ ✅ Modo quadra: PWA instalada no tel.  │
│ ✅ Modo escritório: mesmo PWA desktop  │
│ ✅ Service Worker: error UI offline    │
└────────────────────────────────────────┘
```

### Benefícios

- 🎯 Single codebase (sem app nativo separado)
- 📱 Web app instalável (como Whatsapp, Instagram)
- 🎨 Design system coeso (não 2 stacks diferentes)
- 🛡️ Acessível desde v1 (shadcn WCAG AA)
- 💰 Custo: ~50% do que 2 apps nativas (iOS + Android)

---

## Slide 6: Contexto Split (D-UI-16)

### Duas Experiências Distintas, Mesmo App

```
    ┌─────────────────────┐
    │ NEXT.JS PWA App     │
    │ (Único código-base) │
    └─────┬───────────────┘
          │
    ┌─────┴─────┐
    │           │
    
[QUADRA]      [ESCRITÓRIO]
Mobile        Desktop
Touch 48px    Touch 44px
Modo Off      Modo Off
          
UIF-002      UIF-001
UIF-004      UIF-003
             UIF-005
             
Primária:    Primária:
Team View    Session Plan
```

### Hardware Compatível

| Contexto | Device | Exemplo | Breakpoint |
|----------|--------|---------|-----------|
| Quadra | Smartphone | iPhone 13 mini, Galaxy S21 | 360px |
| Quadra | Tablet 7" | iPad mini | 560px |
| Escritório | Laptop | MacBook Air 13", Lenovo X1 | 1440px |
| Escritório | Desktop | Mac Studio 36", iMac 27" | 2560px+ |

---

## Slide 7: Acessibilidade (WCAG AA)

### Touch Targets

```
[Quadra — Uso com Luvas/Mãos Suadas]
┌──────────────────┐
│                  │
│   ▓▓▓▓▓▓▓▓       │  ← Mínimo 48 × 48 px
│   ▓Button▓       │     (vs. padrão web 44px)
│   ▓▓▓▓▓▓▓▓       │
│                  │
└──────────────────┘

[Escritório — Mouse/Teclado]
┌──────────────────┐
│   ▓▓▓▓▓▓        │  ← Mínimo 44 × 44 px
│   ▓Button▓       │
│   ▓▓▓▓▓▓        │
└──────────────────┘
```

### 3 Pilares WCAG AA

| Pilar | Implementação | Status |
|-------|---------------|--------|
| **Percepção** | Color + Icon + Text (não só cor) | ✅ |
| **Rastreamento** | Labels, aria-label, focus visível | ✅ |
| **Compreensão** | Language simples, validação clara | ✅ |

**Dark Mode:** Suportado em toda plataforma

---

## Slide 8: Gaps Resolvidos (G-01 a G-05)

### 9 Endpoints Adicionados ao OpenAPI

```
Problema: UI depende de endpoints inexistentes
Solução:  Adicionar 9 endpoints + criar schemas

G-01: Recomendações (UIF-001 [5])
  POST /training-sessions/{id}/recommendations/{recId}/accept
  POST /training-sessions/{id}/recommendations/{recId}/dismiss

G-02: Inelegibilidade (UIF-002 [5])
  POST /training-sessions/{id}/ineligibility
  GET  /training-sessions/{id}/ineligibility

G-03: Attention Queue (UIF-003 [6])
  POST /training-sessions/{id}/attention-queue/{itemId}/resolve
  POST /training-sessions/{id}/attention-queue/{itemId}/dismiss
  POST /training-sessions/{id}/attention-queue/{itemId}/escalate

G-04: Feedback (UIF-003 [5])
  POST /training-sessions/{id}/feedback-threads/{threadId}/close

G-05: Load Chart (UIF-005 [1])
  GET  /training/load-chart?team_id=&athlete_id=&range=
```

**Status:** ✅ Todos 9 endpoints em `contracts/openapi/paths/training.yaml`

---

## Slide 9: Roadmap MVP v1.0

### 7 Phases, ~14 Semanas

```
Week  1–2  [Phase 1] Session Planning [UIF-001]
      3–4  [Phase 2] Athlete Check-in [UIF-002] + G-02
      5–7  [Phase 3] Coach Review [UIF-003] + G-03 + G-04
      8    [Phase 4] Recommendations [UIF-001 [5]] + G-01
      9–10 [Phase 5] Modo Quadra [UIF-004]
      11–12[Phase 6] Load Chart [UIF-005] + G-05
      13–14[Phase 7] Polish + Deploy

Start: 2026-03-24 (MON, após sign-off)
End:   2026-07-11
```

### Entregáveis por Phase

| Phase | O Que Funciona |
|-------|---|
| 1 | Coach cria sessão, objetivos, blocos |
| 2 | + Atleta faz check-in, vê readiness |
| 3 | + Coach revisa execução, faz feedback |
| 4 | + Coach vê recomendações de analytics |
| 5 | + Coach vê equipe no mobile (PWA) |
| 6 | + Todos veem Load Chart (desktop) |
| 7 | + Polish: notificações, exports, etc |

---

## Slide 10: Checklist de Sign-off

### Decisões Esperadas

Para cada role abaixo, esperamos: ✅ GO | ❌ NO-GO | ⚠️ GO with conditions

---

### 🎯 Product Owner

**Validar:** Produto é operacionalmente viável?

**Quick Checks:**
- [ ] 5 UIFs refletem fluxo real (planning → check-in → review)?
- [ ] Readiness score (0–100) faz sentido clinicamente?
- [ ] Team Readiness Overview (exceção destacada) é útil na quadra?
- [ ] Progressive disclosure reduz fricção de check-in?

**Decisão:** [ ] GO | [ ] NO-GO | [ ] GO w/ conditions: ______

---

### 🎨 UX Designer

**Validar:** Design é acessível e implementável?

**Quick Checks:**
- [ ] WCAG AA: labels visíveis, focus, color + text + icon?
- [ ] Touch targets 48×48 px (quadra), 44×44 px (escritório)?
- [ ] Dark mode tokens aplicados (9 cores semânticas)?
- [ ] Responsiveness: 360px → 2560px sem layout quebrado?

**Decisão:** [ ] GO | [ ] NO-GO | [ ] GO w/ conditions: ______

---

### ⚙️ Engineering Lead

**Validar:** Estrutura técnica é viável?

**Quick Checks:**
- [ ] 34 endpoints em `contracts/openapi/paths/training.yaml`?
- [ ] 10 schemas em `contracts/schemas/training/`?
- [ ] Backend stack (Django 5.x + Django Ninja 1.x) decidido?
- [ ] Next.js + next-pwa possível com stack backend?
- [ ] Phases 1–7 timeline (~14 sem) é realista?

**Decisão:** [ ] GO | [ ] NO-GO | [ ] GO w/ conditions: ______

---

## Slide 11: Dependências Críticas

### ✅ TUDO PRONTO

Nenhuma dependência pendente:

| Item | Status | Evidência |
|------|--------|-----------|
| OpenAPI endpoints (34) | ✅ | `training.yaml` atualizado |
| JSON schemas (10) | ✅ | `contracts/schemas/training/` |
| Design decisions (9) | ✅ | D-UI-15 a D-UI-19 documentadas |
| Backend stack | ✅ | ADR-030, ADR-031 aprovadas |
| UIFs completos (5) | ✅ | 24 telas + states + components |

---

## Slide 12: Benefícios Resumidos

### 🏀 Para o Coach

```
✅ Readiness score por atleta (antes de treinar)
✅ Bloco de exceção destacado (automático)
✅ Feedback rastreável com contexto histórico
✅ Gráfico de carga para decisões de intensidade
✅ Modo quadra: PWA instalada (offline UI)
✅ Modo escritório: desktop completo
```

### 👨‍💻 Para o Atleta

```
✅ Check-in rápido (< 60 segundos)
✅ Feedback instantâneo (readiness visual)
✅ Clarity: por que estou inelegível?
✅ Usa PWA mobile (igual app nativo)
```

### 💰 Para o CEO

```
✅ Plataforma unificada (não 2 apps)
✅ Open-source design (sem vendor lock)
✅ Roadmap claro: 14 semanas → MVP pronto
✅ Custo: ~50% vs. 2 aplicações nativas
```

---

## Slide 13: Próximos Passos

### Timeline Imediata

| Data | O Que | Quem |
|------|-------|------|
| 2026-03-17 | Hoje: review deste deck | PO + UX + Eng |
| 2026-03-18 | Reunião de sign-off | PO + UX + Eng |
| 2026-03-18 EOD | GO/NO-GO decision | Eng Lead |
| 2026-03-19 | Phase 1 planning | Eng Lead + Squad |
| 2026-03-24 MON | **Coding starts** | Dev Team |

### Documentos de Referência

- 📄 [UI_CONTRACT_TRAINING.md](./UI_CONTRACT_TRAINING.md) — Contrato completo (30+ páginas)
- 📋 [SIGN_OFF_CHECKLIST_v1.1.0.md](./SIGN_OFF_CHECKLIST_v1.1.0.md) — Questões detalhadas por role
- 📊 [EXECUTIVE_SUMMARY_v1.1.0.md](./EXECUTIVE_SUMMARY_v1.1.0.md) — Resumo executivo

---

## Slide 14: Pergunta Final

### A Grande Decisão

> ## "Aprovamos a implementação do módulo training conforme proposto?"

### Respostas Esperadas

✅ **GO**  
→ Promover para `implementation_ready`  
→ Iniciar Phase 1 em 2026-03-24

❌ **NO-GO**  
→ Retornar para revisão  
→ Identificar gaps específicos

⚠️ **GO with conditions**  
→ Condição: _________  
→ Quando resolvida: GO automático

---

## Slide 15: Obrigado

### Qualquer Dúvida?

**Contatos:**
- **Product Owner:** _______________
- **UX Designer:** _______________
- **Engineering Lead:** _______________

**Documentos:**
- Checklist: `SIGN_OFF_CHECKLIST_v1.1.0.md`
- Resumo: `EXECUTIVE_SUMMARY_v1.1.0.md`
- Contrato: `UI_CONTRACT_TRAINING.md`

---

**Apresentação Preparada:** 2026-03-17  
**Próxima Review:** 2026-03-18 (sign-off meeting)  
**Status:** Aguardando Aprovação
