# PROMPT_TEMPLATE_DOCUMENTATION.md

## Descrição
Template padrão para documentation generation: estrutura, seções esperadas, tone, e validação.

---

## Estrutura de Doc Padrão

### Header
```markdown
---
description: "Breve descrição (max 10 palavras)"
authority: "Responsável / SSOT"
applyTo: "Padrão glob ou caminho específico"
lastUpdated: "YYYY-MM-DD"
---
```

### Seção 1: Visão Geral
- Propósito do documento
- Audiência-alvo
- Escopo + o que NÃO está incluído

### Seção 2: Conteúdo Principal (estruturado)
- Ordenado logicamente
- Máximo 2 níveis de nesting
- Exemplos concretos

### Seção 3: Referências + Links
- Cite docs canônicos relevantes
- Link para arquivos relacionados
- Indique SSOT se aplicável

### Seção 4: TODO / Próximas Atualizações (optional)
```markdown
## TODO
- [ ] <descrição breve>
- [ ] <descrição breve>
```

---

## Tone & Voice
- **Formal mas acessível**: Não use jargão sem explicação
- **Objetivo**: Avoid fluff, cite evidence
- **Determinístico**: mesmas inputs → mesma saída, sem ambiguidade
- **Actionable**: Cada seção deve ter algo que o leitor pode fazer

---

## Validação Obrigatória
- [ ] Título claro e descritivo
- [ ] Nenhuma seção vazia (remover ou preencher)
- [ ] Todos os links são relativos (sem file://)
- [ ] Nenhuma PII/secrets disperso no doc
- [ ] Ortografia + markdown sintaxe válida

---

## TODO
- [ ] Criar converter de plain text → formatted doc
- [ ] Adicionar spell checker (PT-BR)
- [ ] Documentar estratégia de versionamento de docs
