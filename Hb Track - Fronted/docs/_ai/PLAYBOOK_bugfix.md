# PLAYBOOK — BUGFIX (FastAPI/SQLAlchemy/Alembic)

## Objetivo
Resolver o bug com patch mínimo, ancorado em evidências do repo, com verificação objetiva.

## Procedimento
1) Reproduzir
- Preferir: teste existente falhando ou request reprodutível.
- Se não houver, criar teste mínimo (pytest) ou script de reprodução.

2) Localizar a causa
- Navegar do sintoma para a origem (endpoint -> service -> repo/query -> DB).
- Não "adivinhar" comportamento de schema: conferir schema.sql quando o bug envolver dados.

3) Fix mínimo
- Alterar apenas o necessário.
- Se a correção muda contrato: validar contra openapi.json (e atualizar o gerado se for o caso).

4) Verificação
- Rodar checks do projeto (ver docs/_ai/CHECKS.md).
- Se checks não forem executáveis, declarar exatamente o que falta (ex.: nome do serviço no compose).

## Formato de saída (obrigatório)
Evidências:
- <lista de paths>

Mudança:
- <resumo do patch mínimo>

Checks:
- <comandos executados e resultado>