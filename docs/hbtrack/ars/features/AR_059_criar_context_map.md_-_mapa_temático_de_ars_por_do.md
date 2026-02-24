# AR_059 — Criar context_map.md — mapa temático de ARs por domínio

**Status**: 🔲 PENDENTE
**Versão do Protocolo**: 1.3.0

## Descrição
Criar docs/hbtrack/context_map.md — documento de contexto que mapeia as ARs por domínio temático. Estrutura esperada:

## Governance (docs/hbtrack/ars/governance/)
ARs de protocolo, CLI, Dev Flow, Gates — ex: AR_033, AR_051–055

## Features (docs/hbtrack/ars/features/)
ARs de implementação de produto — ex: AR_005, AR_014/015, AR_068

## Business Invariants
ARs de verificação de regras de negócio — ex: AR_056–058

## Infrastructure / SSOT
ARs de schema, alembic, OpenAPI — ex: AR_060–061

## Security / RBAC
ARs de autenticação e autorização — ex: AR_062

## Observability
ARs de logging e trace — ex: AR_063

## SUPERSEDED
ARs obsoletas marcadas como ⛔ SUPERSEDED

O documento deve ter cabeçalho com data de geração e contagem total.

## Critérios de Aceite
- Arquivo docs/_canon/context_map.md existe
- Arquivo tem seção '## Governance' ou equivalente
- Arquivo tem seção '## Features' ou equivalente
- Arquivo tem pelo menos 20 linhas de conteúdo
- Arquivo tem cabeçalho com data ou linha 'Gerado em' / 'Context Map'
- hb report gera evidence exit 0

## Write Scope
- docs/_canon/context_map.md

## Validation Command (Contrato)
```
python -c "import pathlib; p=pathlib.Path('docs/_canon/context_map.md'); assert p.exists(),'FAIL: docs/_canon/context_map.md nao existe'; c=p.read_text(encoding='utf-8'); lines=[l for l in c.splitlines() if l.strip()]; assert len(lines)>=20,f'FAIL: context_map.md muito curto ({len(lines)} linhas nao-vazias, minimo 20)'; assert any('Governance' in l or 'governance' in l for l in lines),'FAIL: secao Governance ausente'; assert any('Feature' in l or 'feature' in l for l in lines),'FAIL: secao Features ausente'; assert any('Context Map' in c or 'context_map' in c.lower() or 'Mapa' in c),'FAIL: cabeçalho context map ausente'; print(f'PASS AR_059: context_map.md existe com {len(lines)} linhas e secoes obrigatorias')"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_059/executor_main.log`

## Notas do Arquiteto
Documento estático criado pelo Executor. Não é auto-gerado — manter manualmente. Próximas atualizações: adicionar entrada manualmente ao criar nova AR de cada domínio.

## Análise de Impacto
_(A ser preenchido pelo Executor)_

---
## Carimbo de Execução
_(Gerado por hb report)_

