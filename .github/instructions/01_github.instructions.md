---
description: Carregar quando a tarefa envolver commits, PRs, merges, ou qualquer interação com GitHub.
applyTo: "**"
---

Leia o fluxo canônico de PR/Merge em `docs/_canon/10_GIT_PR_MERGE_WORKFLOW.md` antes de executar qualquer tarefa relacionada a Git/GitHub. Siga as regras gerais e o passo a passo para garantir um processo seguro e eficiente.

## Regras Gerais:
- Seguir as orientações canônicas de Git/GitHub em `docs/_canon/10_GIT_PR_MERGE_WORKFLOW.md`.
- Sempre revisar o status do repositório antes de commitar (`git status --porcelain`).
- Parar no primeiro erro (qualquer comando com exit != 0) e reportar imediatamente.
- Evitar merges automáticos sem autorização explícita do usuário.