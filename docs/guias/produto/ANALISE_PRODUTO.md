# Analise de Robustez dos Contratos Finais
> Documento de apoio humano, não canônico e não soberano. Serve para análise histórica do bundle contratual; não substitui `contracts/`, `docs/_canon/` ou `.contract_driven/`.

**Data:** 2026-03-20  
**Escopo principal auditado:** `contracts/**` e `generated/contracts/**`  
**Apoio contextual minimo:** `docs/_canon/**` e `.contract_driven/**` apenas quando necessario para explicar contradicoes visiveis no contrato final  
**Objeto principal:** bundle contratual final que pretende governar API, modulos e artefatos downstream

## PARTE 1 - Veredito geral

**contrato inadequado como fonte de verdade**

O problema nao e editorial. O problema e normativo e estrutural.  
O bundle final em `generated/contracts/openapi` e `generated/contracts/asyncapi` nao fecha nem o proprio grafo de referencias: o OpenAPI gerado tem `634/634` refs internas apontando para `components/` inexistente, e o AsyncAPI gerado referencia `51` canais que nao existem no proprio bundle.  
Mesmo ignorando `generated/`, o contrato-fonte em `contracts/` continua fraco como SSOT real: usa `58` operacoes com `bearerAuth` indefinido, `44` placeholders `- {}` em `security`, dois modelos de erro paralelos, schemas de resposta amputados e regras criticas presas em prosa ou documentos externos.  
O resultado final parece sofisticado, mas nao e suficientemente deterministico, auto-suficiente nem verificavel para governar geracao downstream com consistencia.

## PARTE 2 - Score de robustez do contrato final

| Criterio | Nota | Justificativa objetiva |
|---------|------|------------------------|
| Capacidade de governar geracao downstream | 15 | O downstream nao tem uma base unica confiavel. `generated/contracts/openapi` esta quebrado como bundle e `generated/contracts/asyncapi` referencia dezenas de arquivos ausentes. |
| Clareza normativa | 36 | Ha muita linguagem normativa, DR/INV/ADR/OWASP e estrutura de modulo, mas a substancia critica fica em prosa, comentarios ou docs externas. |
| Determinismo | 18 | `bearerAuth` indefinido, `security: - {}`, `filterExpression` livre, `additionalProperties: true` em `/analytics/query` e regras de transicao em texto abrem variacao inevitavel. |
| Ausencia de ambiguidade | 16 | `match_operator` nao fecha com RBAC flat 5 roles, `team staff with medical access` nao mapeia para role canonica, e status/enum divergem entre superfices. |
| Acionabilidade | 22 | Alguns paths sao acionaveis para leitura humana, mas um gerador ou implementador estrito para no bundle gerado quebrado ou precisa inferir demais. |
| Verificabilidade | 10 | O contrato final nao e integralmente validavel: refs internas quebradas no gerado, seguranca placeholder, invariantes cross-field so em description, e erro nao padronizado. |
| Cobertura de cenarios | 28 | Happy path existe em boa parte dos paths, mas varias superfices seguem stub, `video` some do OpenAPI gerado, e eventos async do gerado estao fisicamente ausentes. |
| Tratamento de excecoes | 18 | Nao ha respostas `500` nos paths OpenAPI auditados, muitos modulos nao definem `409`, e o modelo de erro muda de modulo para modulo. |
| Consistencia interna | 9 | O contrato se contradiz internamente: OpenAPI diz ser fonte primaria e ao mesmo tempo aponta `api_rules.yaml` como SSOT; source e generated divergem; erro e seguranca nao sao unificados. |
| Resistencia a interpretacao frouxa | 14 | O contrato usa referencias densas e descriptions longas, mas nao fecha estados, RBAC, DSL de filtro, nem varios constraints de forma machine-readable. |
| Capacidade de servir como fonte de verdade | 8 | Nao e possivel tratar o bundle final como fonte unica. Se o consumidor usa `generated/**`, encontra refs quebradas; se usa `contracts/**`, encontra stubs, placeholders e dependencia externa. |
| Robustez real vs qualidade aparente | 12 | A aparencia e forte: comentarios, inventarios gerados, DR/INV/ADR, OWASP, schemas soberanos. A robustez real e baixa porque o artefato final exposto downstream continua incompleto, contraditorio e parcialmente invalido. |

**Nota final consolidada:** 17/100

**Por que nao merece 100/100:**  
Porque o contrato final falha em requisitos basicos de SSOT antes mesmo de entrar em discussoes de negocio: bundle gerado com referencias quebradas, seguranca indefinida, erros nao unificados, superfices omitidas no gerado, schemas de resposta amputados e regras criticas so em texto.

## PARTE 3 - Sinais de "contrato bonito"

| Trecho/ponto | Por que parece forte | Por que e fraco na pratica | Impacto downstream | Severidade |
|-------------|----------------------|----------------------------|--------------------|------------|
| `contracts/openapi/openapi.yaml:9-13` declara a especificacao como fonte primaria da verdade | Parece SSOT explicita | Na mesma descricao, manda consultar `.contract_driven/templates/api/api_rules.yaml` como `SSOT`; o contrato final se assume incompleto | O implementador nao sabe se obedece ao OpenAPI ou a regra externa quando houver conflito | Critica |
| Paths cheios de DR/INV/ADR/OWASP | Passa impressao de rastreabilidade e rigor | Na maior parte dos casos isso so aponta para regra externa ou prosa; nao fecha comportamento no schema | Dois implementadores podem "cumprir o texto" e mesmo assim gerar saidas diferentes | Alta |
| `additionalProperties: false` em varios request bodies | Parece contrato estrito | A resposta continua amputada ou apoiada em schema stub; a rigidez esta no input, nao no artefato downstream completo | SDK/cliente gerado conhece menos do que a API real entrega | Alta |
| Inventario "GENERATED PATH INVENTORY - do not edit manually" no OpenAPI root | Parece geracao deterministica e confiavel | O source inclui `video`, mas o bundle gerado omite `video.yaml`; a aparencia de sincronismo nao se sustenta | Geracao downstream usa um inventario diferente do contrato-fonte | Critica |
| Presenca de `shared/problem.yaml` com shape RFC 7807 | Parece padronizacao global de erros | Ainda ha `127` referencias para `common/error.yaml`, com shape totalmente diferente | Middleware, frontend e SDK precisam tratar dois contratos de erro paralelos | Alta |
| Presenca de schemas soberanos em `contracts/schemas/*.schema.json` | Parece haver shape canonico completo | Esses schemas nao estao ligados de forma confiavel ao contrato exposto downstream; o OpenAPI continua devolvendo stubs em modulos criticos | Gera dualidade: schema "bonito" soberano e contrato efetivo amputado | Critica |
| `generated/contracts/asyncapi/asyncapi.yaml` lista muitos canais e parece abrangente | Parece cobertura assicrona madura | O bundle gerado so possui `10` arquivos de canal fisicos; `51` refs do root apontam para arquivos inexistentes | O artefato gerado nao e consumivel como contrato real | Critica |
| `contracts/openapi/paths/video.yaml` parece formalizar o modulo `video` com bastante detalhe | Parece modulo maduro e governado | O `generated/openapi` nao carrega a superficie `video`; alem disso, usa `match_operator` fora do RBAC canonico | Um downstream gera `video`; outro downstream nao gera nada | Critica |
| Comentarios de seguranca OWASP em quase todos os paths | Parece enforcement forte | O contrato usa `58` operacoes com `bearerAuth` indefinido e `44` placeholders `- {}` | Seguranca fica sujeita a alias manual, fallback de framework ou abertura acidental | Critica |

## PARTE 4 - Fragilidades reais

| Falha | Tipo | Impacto no sistema gerado | Severidade | Correcao necessaria |
|------|------|----------------------------|------------|--------------------|
| `generated/contracts/openapi` nao possui `components/`, mas o root e os paths referenciam `./components/...` e `../components/...`; resultado: `634/634` refs internas faltando | fonte de verdade insuficiente | O bundle OpenAPI gerado nao e utilizavel por parser, gerador de SDK, validador nem codegen sem remendo manual | Critica | Publicar o bundle gerado completo e auto-contido, com `components/` e todos os arquivos referenciados |
| `generated/contracts/asyncapi/asyncapi.yaml` referencia `51` canais ausentes no proprio bundle | verificabilidade fraca | O consumidor do AsyncAPI gerado nao consegue resolver os canais e payloads declarados | Critica | Sincronizar root e filesystem; zero refs quebradas antes de promover o artefato gerado |
| `contracts/openapi/openapi.yaml` define apenas `HTTPBearer`, mas `58` operacoes usam `bearerAuth` | conflito | Ferramentas e implementadores divergem entre alias manual, falha de parse ou abertura indevida | Critica | Unificar para um unico security scheme valido em todas as operacoes |
| `44` operacoes usam `security: - {}` como placeholder | verificabilidade fraca | O contrato nao informa autenticao/autorizacao de forma executavel; gera interpretacao frouxa ou endpoints "publicos por acidente" | Critica | Eliminar placeholders e declarar security requirement real por operacao |
| Dois modelos de erro convivem: `common/error.yaml` e `shared/problem.yaml` | conflito | Frontends, SDKs e middlewares precisam suportar dois formatos incompativeis para a mesma plataforma | Alta | Padronizar um unico modelo de erro e reescrever todas as referencias |
| OpenAPI se declara fonte primaria, mas aponta `api_rules.yaml` como `SSOT` externa | fonte de verdade insuficiente | O contrato final nao e auto-suficiente; o implementador depende de leitura lateral para decidir comportamento | Alta | Fazer o contrato final incorporar as decisoes normativas necessarias, nao apenas referencia-las |
| Schemas OpenAPI de `matches`, `medical`, `scout`, `analytics`, `audit` e `identity_access` sao stubs frente aos shapes soberanos em `contracts/schemas/` | fonte de verdade insuficiente | Clientes, mapeadores e geradores saem com modelos amputados e divergentes do dominio real | Critica | Refatorar o OpenAPI para referenciar ou reproduzir os shapes completos canonicos |
| `contracts/openapi/openapi.yaml` inclui `video`, mas `generated/contracts/openapi/paths/` nao tem `video.yaml` | conflito | O contrato-fonte e o contrato-gerado produzem APIs diferentes | Critica | Garantir que o inventario gerado reflita exatamente as superfices do contrato-fonte |
| `contracts/openapi/openapi.yaml:287-319` nao possui tag `video`, embora exponha paths `video` em `247-257` | conflito | Ferramentas que dependem de tags/modulos para agrupamento geram catalogos inconsistentes | Media | Incluir `video` na taxonomia publicada do contrato ou remover a superficie ate o inventario ficar coerente |
| `contracts/openapi/paths/video.yaml:21-22,110,131,221` usa `match_operator`, enquanto `contracts/openapi/paths/identity_access.yaml:17` fixa RBAC flat 5 roles | ambiguidade | ACL de video muda conforme o implementador inventa role nova, faz alias ou rejeita a regra | Alta | Formalizar `match_operator` no RBAC canonico ou remover o papel do contrato |
| `contracts/openapi/paths/analytics.yaml:422-447` aceita `filterExpression` livre e retorna `data[]` com `additionalProperties: true` | determinismo fraco | Query engine, SDK e UI podem criar DSLs e shapes de resposta diferentes para a mesma operacao | Alta | Definir DSL formal ou trocar por filtros tipados; fixar shape de resposta por projection/query type |
| `contracts/openapi/paths/matches.yaml:264-300` e `contracts/openapi/paths/medical.yaml:116-119` deixam invariantes criticos so em description | verificabilidade fraca | `homeTeamId != awayTeamId`, transicao forward de status e `returnToPlay => returnToTraining` podem ou nao ser implementados | Alta | Codificar invariantes em schema, assertions validaveis ou extensoes normativas executaveis |
| `contracts/openapi/paths/matches.yaml` usa `statusLabel` em lowercase, enquanto `contracts/schemas/matches/match.schema.json` usa enum uppercase | conflito | Validadores, geradores e bancos podem normalizar de maneiras diferentes ou rejeitar payloads validos em outra superficie | Alta | Unificar casing e enum canonico em todas as superfices |
| Nao ha respostas `500` nos paths OpenAPI auditados; `matches`, `medical`, `scout` e `analytics` tambem nao definem `409` | excecao ausente | O comportamento em falhas internas e conflitos de estado/concorrencia fica em branco no contrato | Media | Definir matriz minima de erros e conflitos por operacao critica |
| `contracts/openapi/paths/medical.yaml:116-117` fala em "team staff with medical access" sem role concreta no contrato | ambiguidade | A implementacao de acesso medico pode variar de 403 estrito a leitura ampla para coach/coordinator | Alta | Declarar papeis, escopo e operacoes permitidas de forma machine-readable |

## PARTE 5 - Teste de derivacao

| Item | Resultado | Por que | O que falta no contrato para isso ser confiavel |
|------|-----------|---------|-----------------------------------------------|
| API | nao | O bundle gerado OpenAPI esta quebrado, o source e o generated divergem em `video`, a seguranca nao e unificada e varios responses sao stubs | Bundle auto-contido valido, inventario unico, security scheme unico e responses completos |
| Modulos | nao | Os paths sao agrupados por modulo, mas a taxonomia publicada e inconsistente, ha modulo omitido no gerado e regras de soberania dependem de docs externas | Taxonomia fechada no proprio contrato final, surfaces completas por modulo e zero deriva source/generated |
| Regras principais | parcialmente | Algumas regras aparecem em enums, descriptions e comentarios, mas varias invariantes e ACLs ficam em prosa | Regras codificadas em schema, policy machine-readable e state machines formais |
| Interfaces | nao | O shape de varias respostas expostas no OpenAPI nao representa o agregado real; no gerado, os componentes nem existem | Schemas de request/response completos, resolviveis e alinhados com `contracts/schemas/` |
| Restricoes relevantes | parcialmente | Existem tipos, enums, ranges e `additionalProperties: false`, mas faltam constraints cross-field, DSL formal, conflitos e excecoes | Constraints cross-field executaveis, erro unificado, conflitos/500 formalizados e restricoes de acesso fechadas |

## PARTE 6 - Teste adversarial

| Cenario | Trecho causador | Divergencia possivel | Consequencia | Severidade |
|--------|------------------|----------------------|--------------|------------|
| `video` entra ou nao entra na API final | `contracts/openapi/openapi.yaml:247-257` vs ausencia de `generated/contracts/openapi/paths/video.yaml` | Implementador A gera endpoints `video`; implementador B usa o bundle gerado e nao gera nada | Duas APIs publicas diferentes a partir do mesmo fluxo | Critica |
| SDK gerado a partir do OpenAPI final | `generated/contracts/openapi/openapi.yaml` + ausencia de `generated/contracts/openapi/components/` | Implementador A remenda refs usando `contracts/openapi/components`; implementador B aborta codegen; implementador C cria mocks proprios | Clientes e servidores gerados nao compartilham o mesmo contrato real | Critica |
| Autenticacao de varias rotas | `58` usos de `bearerAuth` com apenas `HTTPBearer` definido | Implementador A trata `bearerAuth` como alias; B rejeita spec; C deixa rotas acessiveis por fallback | Comportamento de seguranca muda conforme ferramenta ou framework | Critica |
| Match response model | `contracts/openapi/components/schemas/matches/match.yaml` vs `contracts/schemas/matches/match.schema.json` | Implementador A gera modelo com 4 campos; B usa schema soberano com status, placar, lineup, arbitros, timestamps | Integracoes e UIs divergem sobre o mesmo endpoint | Critica |
| ACL de `video` | `contracts/openapi/paths/video.yaml:21-22,110,131,221` vs RBAC flat 5 roles em `contracts/openapi/paths/identity_access.yaml:17` | Implementador A cria role `match_operator`; B mapeia para `coordinator`; C rejeita a role | Permissoes reais de video ficam arbitrarias | Alta |
| Query analytics | `contracts/openapi/paths/analytics.yaml:422-447` | Implementador A cria DSL `key=value`; B aceita expressao SQL-like; C trata como string opaca sem validacao | Mesma operacao produz contratos de cliente, validacao e semantics diferentes | Alta |
| Status de partida | `contracts/openapi/paths/matches.yaml:264-300` vs `contracts/schemas/matches/match.schema.json` | Implementador A usa lowercase e bloqueia backward transitions; B usa uppercase do JSON Schema; C aceita ambos | Validacao, serializacao e estados persistidos divergem | Alta |
| Acesso medico | `contracts/openapi/paths/medical.yaml:116-117` | Implementador A permite so medico/fisio; B inclui coordinator; C deixa coach ler resumo por inferencia funcional | Exposicao de dado sensivel varia entre implementacoes | Critica |

## PARTE 7 - Veredito final

- **este contrato e fonte de verdade real?** nao
- **ele e suficientemente deterministico para geracao downstream?** nao
- **ele esta em nivel 100/100?** nao
- **ele governa comportamento real ou so aparenta governar?** so aparenta governar; a densidade documental e alta, mas o bundle final continua quebrado, contraditorio e dependente de inferencia
- **o que falta para deixar de ser "bonito" e passar a ser "forte"?**
  - publicar bundles gerados auto-contidos e validos, com zero refs quebradas
  - unificar seguranca em um unico scheme real, sem `bearerAuth` fantasma nem `- {}`
  - unificar o modelo de erro
  - eliminar stubs de resposta e ligar o OpenAPI aos shapes soberanos completos
  - codificar ACL, state machine, constraints cross-field e DSLs em forma machine-readable
  - garantir identidade perfeita entre `contracts/**` e `generated/**`, inclusive para `video`

## Conclusao objetiva

Se o downstream consumir `generated/**`, o contrato final falha antes da interpretacao: ha referencias quebradas e superfices ausentes.  
Se o downstream consumir `contracts/**`, ainda encontra placeholders, ambiguidades, dualidade de schema e dependencia externa para fechar regras centrais.  
Em ambos os casos, o artefato final nao atinge o minimo para ser tratado como fonte unica de verdade do sistema.
