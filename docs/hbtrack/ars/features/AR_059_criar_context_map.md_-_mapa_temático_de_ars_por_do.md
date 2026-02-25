# AR_059 — Criar context_map.md — mapa temático de ARs por domínio

**Status**: ✅ VERIFICADO
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
python -c "import pathlib; p=pathlib.Path('docs/_canon/context_map.md'); assert p.exists(),'FAIL: docs/_canon/context_map.md nao existe'; c=p.read_text(encoding='utf-8'); lines=[l for l in c.splitlines() if l.strip()]; assert len(lines)>=20,f'FAIL: context_map.md muito curto ({len(lines)} linhas nao-vazias, minimo 20)'; assert any('Governance' in l or 'governance' in l for l in lines),'FAIL: secao Governance ausente'; assert any('Feature' in l or 'feature' in l for l in lines),'FAIL: secao Features ausente'; assert ('Context Map' in c or 'context_map' in c.lower() or 'Mapa' in c), 'FAIL: cabeçalho context map ausente'; print(f'PASS AR_059: context_map.md existe com {len(lines)} linhas e secoes obrigatorias')"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_059/executor_main.log`

## Notas do Arquiteto
Documento estático criado pelo Executor. Não é auto-gerado — manter manualmente. Próximas atualizações: adicionar entrada manualmente ao criar nova AR de cada domínio.

## Análise de Impacto
**Executor**: 2026-02-24

**Escopo**: Documentação pura - criar context_map.md mapeando ARs por domínio temático.

**Riscos**:
- **BAIXO**: Criação de arquivo .md estático fora dos governed roots.
- **BAIXO**: Documento de referência para navegação — não afeta código ou DB.

**Dependências**:
- Leitura de docs/hbtrack/ars/ para mapear ARs existentes por diretório
- Estrutura esperada: Governance, Features, Business Invariants, Infrastructure, Security, Observability, SUPERSEDED

**Patch**:
- 1 arquivo criado: docs/_canon/context_map.md (~50-100 linhas)

---
## Carimbo de Execução
_(Gerado por hb report)_

### Execução Executor em c5f1ba8
**Status Executor**: ❌ FALHA
**Comando**: `python -c "import pathlib; p=pathlib.Path('docs/_canon/context_map.md'); assert p.exists(),'FAIL: docs/_canon/context_map.md nao existe'; c=p.read_text(encoding='utf-8'); lines=[l for l in c.splitlines() if l.strip()]; assert len(lines)>=20,f'FAIL: context_map.md muito curto ({len(lines)} linhas nao-vazias, minimo 20)'; assert any('Governance' in l or 'governance' in l for l in lines),'FAIL: secao Governance ausente'; assert any('Feature' in l or 'feature' in l for l in lines),'FAIL: secao Features ausente'; assert any('Context Map' in c or 'context_map' in c.lower() or 'Mapa' in c),'FAIL: cabeçalho context map ausente'; print(f'PASS AR_059: context_map.md existe com {len(lines)} linhas e secoes obrigatorias')"`
**Exit Code**: 1
**Timestamp UTC**: 2026-02-24T22:53:53.287211+00:00
**Behavior Hash**: 56963edea338ee9b767dc40ccbfff9d07f14b9f968fb7cb9119eca98467439f9
**Evidence File**: `docs/hbtrack/evidence/AR_059/executor_main.log`
**Python Version**: 3.11.9

### Execução Executor em 1f85071
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python -c "import pathlib; p=pathlib.Path('docs/_canon/context_map.md'); assert p.exists(),'FAIL: docs/_canon/context_map.md nao existe'; c=p.read_text(encoding='utf-8'); lines=[l for l in c.splitlines() if l.strip()]; assert len(lines)>=20,f'FAIL: context_map.md muito curto ({len(lines)} linhas nao-vazias, minimo 20)'; assert any('Governance' in l or 'governance' in l for l in lines),'FAIL: secao Governance ausente'; assert any('Feature' in l or 'feature' in l for l in lines),'FAIL: secao Features ausente'; assert ('Context Map' in c or 'context_map' in c.lower() or 'Mapa' in c), 'FAIL: cabeçalho context map ausente'; print(f'PASS AR_059: context_map.md existe com {len(lines)} linhas e secoes obrigatorias')"`
**Exit Code**: 0
**Timestamp UTC**: 2026-02-25T00:01:19.856762+00:00
**Behavior Hash**: 4356857b1e2c4697aaa1495ba106552b61f660ded8aeef4bd492d3ef6d549582
**Evidence File**: `docs/hbtrack/evidence/AR_059/executor_main.log`
**Python Version**: 3.11.9


### Verificacao Testador em 1f85071
**Status Testador**: ✅ SUCESSO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_059_1f85071/result.json`

### Selo Humano em 1f85071
**Status Humano**: ✅ VERIFICADO
**Timestamp UTC**: 2026-02-25T00:04:27.669895+00:00
**Motivo**: —
**TESTADOR_REPORT**: `_reports/testador/AR_059_1f85071/result.json`
**Evidence File**: `docs/hbtrack/evidence/AR_059/executor_main.log`
