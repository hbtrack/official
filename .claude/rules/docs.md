---
paths:
  - "docs/**/*.md"
  - "**/README.md"
  - ".claude/**/*.md"
  - "CLAUDE.md"
---

# HB Track — Documentação

- Todo doc deve começar com um cabeçalho de status: VERIFIED | NEEDS_REVIEW | DEPRECATED.
- VERIFIED só quando bater com evidência do sistema (ex.: OpenAPI gerado e schema atual).
- Se o doc estiver desatualizado e você não consegue provar: marque NEEDS_REVIEW (não reescreva "no escuro").
- Se conflitar com a implementação atual: marque DEPRECATED e aponte o doc correto/novo.
- Sempre linkar/indicar onde no código o comportamento vive (arquivos e paths).