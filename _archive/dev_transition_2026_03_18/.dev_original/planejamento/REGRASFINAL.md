# AUDITORIA ADVERSARIAL FINAL — NOVA ESTRUTURA INSTRUCIONAL

Evidência empírica usada nesta auditoria:
- `python3 scripts/validate_contracts.py` executado em 2026-03-17 retornou `FAIL`.
- Gates bloqueantes falhos: `PATH_CANONICALITY_GATE`, `REQUIRED_ARTIFACT_PRESENCE_GATE`, `READINESS_SUMMARY_GATE`.
- Gates não bloqueantes também expuseram drift: `API_NORMATIVE_DUPLICATION_GATE`.
- `PYTHONPATH=. .venv/bin/pytest -q tests/contracts/test_module_doc_governance.py tests/contracts/test_openapi_root_inventory.py tests/pipeline_gates/test_tooling_config_gate.py` retornou `9 passed`, o que prova blind spot relevante: a malha de testes atual não captura o drift documental já existente.
- Busca estrutural encontrou `99` referências ativas para arquivos removidos, paths inexistentes ou saídas derivadas inconsistentes.
- A suposta redução de arquivos não foi “real”: os arquivos removidos continuam preservados em templates e índices, somando pelo menos `238` linhas só em scaffolds residuais diretamente ligados ao canon removido.

## BLOCO 1 — VEREDITO GERAL ADVERSARIAL

- a nova estrutura passa ou reprova?
  Reprova.
- ela realmente atinge 100/100 em qualidade? sim ou não;
  Não.
- ela realmente atinge 100/100 em determinismo? sim ou não;
  Não.
- ela realmente atinge 100/100 em eficiência de contexto? sim ou não;
  Não.
- se reprova, por quê?
  Reprova porque a consolidação foi incompleta e quebrou a coerência operacional do sistema. Arquivos removidos continuam tratados como válidos em governança, prompts, README canônico, templates, OpenAPI root, relatórios derivados e gates. O pipeline real falha por exigir `docs/_canon/BOOT_PROFILES.md` e `docs/_canon/ERROR_MODEL.md`, o `boot_resolution_report.json` ainda aponta para `ERROR_MODEL.md`, e parte dos workers depende de paths de implementação que não existem no workspace (`frontend/src/...`, `Hb Track - Backend/src/...`). A redução de arquivos foi parcialmente cosmética: removeu arquivos do canon, mas manteve o custo cognitivo e de contexto em templates, índices e referências mortas.

## BLOCO 2 — SCORE ADVERSARIAL DA ARQUITETURA

| Critério | Nota | Justificativa objetiva |
|---------|------|------------------------|
| Qualidade instrucional real | 43 | Há instrução forte em alguns pontos, mas a estrutura ainda falha em impor comportamento correto sem interpretação e hoje quebra em validação real. |
| Determinismo real | 36 | Boot, prompts, README, templates, gates e relatórios não concordam entre si; há múltiplos caminhos operacionais plausíveis. |
| Eficiência de contexto real | 39 | Arquivos removidos continuam vivos em templates, índices, backlog histórico e referências redundantes; a economia de contexto não se materializou. |
| Robustez contra ambiguidade | 40 | “arquivo removido” e “arquivo ainda esperado” coexistem; isso é ambiguidade operacional material. |
| Robustez contra respostas genéricas | 52 | Alguns prompts são densos, mas AsyncAPI/Arazzo/Schema/UI ainda permitem resposta boilerplate. |
| Robustez contra conflito entre regras | 32 | Há conflito explícito entre arquivos atuais, templates residuais, relatórios derivados e gates. |
| Clareza de precedência | 41 | A hierarquia existe, mas parte das referências hierárquicas aponta para arquivos extintos ou não canonizados. |
| Acionabilidade | 46 | Parte do fluxo é executável; parte depende de paths inexistentes, artefatos removidos ou registros não classificados em boot. |
| Estabilidade entre execuções | 38 | Duas execuções podem divergir conforme o agente siga o canon vivo, o template residual ou o relatório derivado. |
| Resistência a loopholes | 34 | É fácil “cumprir superficialmente” ignorando referências quebradas, escolhendo só o que funciona e produzindo saída mediana. |

Nota final consolidada da arquitetura:
`40/100`

## BLOCO 3 — SCORE ADVERSARIAL POR ARQUIVO

Escopo auditado neste bloco:
24 arquivos que compõem a nova estrutura operacional ou são evidências/resultados diretos dela.

## Arquivo: CLAUDE.md

Função real:
Boot permanente e autoridade nível-0 do agente.
Define módulos, task_types, bloqueios, árvore de decisão e perfis de boot.

Tabela de pontuação:
| Critério | Nota | Justificativa objetiva |
|---------|------|------------------------|
| Qualidade instrucional real | 82 | Base forte e curta para o papel que cumpre. |
| Determinismo real | 77 | Perfis são claros, mas os relatórios derivados não permanecem alinhados a eles. |
| Eficiência de contexto real | 74 | Caiu bastante de tamanho, porém §8 ainda é redundante. |
| Robustez contra ambiguidade | 80 | Task types e bloqueios estão explícitos. |
| Robustez contra respostas genéricas | 84 | Restringe bem comportamento base. |
| Robustez contra conflito entre regras | 72 | Não impede drift de RULES/LAYOUT/relatórios. |
| Clareza de precedência | 86 | Autoridade nível-0 está explicitada. |
| Acionabilidade | 87 | Roteia bem o sistema para workers. |
| Estabilidade entre execuções | 78 | Depende da coerência dos arquivos subordinados. |
| Resistência a loopholes | 70 | O agente ainda pode fingir que o boot foi respeitado sem validar a evidência gerada. |

Nota final do arquivo:
`79`

Veredito:
`aprovado`

Por que não é 100/100:
Ainda tolera drift entre o boot prescrito e o boot efetivamente reportado.

Falhas encontradas:
| Falha | Severidade | Tipo | Impacto prático | Cenário de quebra |
|-------|------------|------|-----------------|-------------------|
| §8 mantém “paths críticos” já cobertos por `OPERATIONS.md` | Média | redundância | Custo de contexto desnecessário no boot permanente | O agente lê caminhos duplicados sem ganhar regra nova |
| Não existe regra de fail-closed quando a evidência de boot diverge de §7 | Alta | determinismo | O sistema parece obedecido, mas o relatório final pode estar errado | `boot_resolution_report.json` lista arquivo removido e o boot base não detecta isso |

Correções obrigatórias:
1. Remover ou reduzir `§8 PATHS CRÍTICOS` para um ponteiro curto a `OPERATIONS.md`.
2. Adicionar regra explícita: divergência entre §7 e `boot_resolution_report.json` bloqueia.
3. Classificar no próprio boot quais relatórios derivados são apenas evidência e nunca fonte substantiva.

## Arquivo: SESSION_HANDOFF.md

Função real:
Memória intersessão.
Resume estado corrente, pendências, bloqueios e próximos passos.

Tabela de pontuação:
| Critério | Nota | Justificativa objetiva |
|---------|------|------------------------|
| Qualidade instrucional real | 84 | Cumpre bem o papel de continuidade. |
| Determinismo real | 72 | O formato ainda admite prosa livre demais. |
| Eficiência de contexto real | 88 | Curto e barato. |
| Robustez contra ambiguidade | 74 | Não há schema rígido de campos obrigatórios. |
| Robustez contra respostas genéricas | 68 | O agente pode preencher com resumo vago. |
| Robustez contra conflito entre regras | 88 | Baixo risco de conflito direto. |
| Clareza de precedência | 80 | A leitura antes de qualquer outra ação é clara. |
| Acionabilidade | 82 | Fácil de usar em sessões reais. |
| Estabilidade entre execuções | 70 | Varia pela disciplina do agente que escreve. |
| Resistência a loopholes | 62 | Dá para “cumprir” com um texto inútil. |

Nota final do arquivo:
`77`

Veredito:
`aprovado`

Por que não é 100/100:
Falta estrutura mínima obrigatória para impedir handoff superficial.

Falhas encontradas:
| Falha | Severidade | Tipo | Impacto prático | Cenário de quebra |
|-------|------------|------|-----------------|-------------------|
| Ausência de schema/slots obrigatórios | Média | decisão | Handoffs variam demais de qualidade | O agente registra “feito / próximo passo” sem bloqueios, artefatos e data |
| Sem validação de completude | Média | loophole | Permite continuidade com contexto pobre | Sessão seguinte começa sem saber o que realmente foi alterado |

Correções obrigatórias:
1. Fixar schema mínimo obrigatório para cada handoff.
2. Exigir campos binários: feitos, bloqueios, próximos passos, artefatos tocados.
3. Validar completude via gate leve ou checklist determinístico.

## Arquivo: .contract_driven/CONTRACT_SYSTEM_RULES.md

Função real:
Manual operacional vinculante do sistema contract-driven.
Deveria conter só regras substantivas e precedência.

Tabela de pontuação:
| Critério | Nota | Justificativa objetiva |
|---------|------|------------------------|
| Qualidade instrucional real | 32 | Continua contendo regras úteis, mas a lista normativa está contaminada por arquivos removidos e conteúdo morto. |
| Determinismo real | 28 | O agente pode seguir o texto vivo, o canon removido ou improvisar substituição. |
| Eficiência de contexto real | 20 | 820 linhas ainda é custo alto para um arquivo on-demand e com sobra de conteúdo obsoleto. |
| Robustez contra ambiguidade | 30 | Arquivos removidos seguem listados como soberanos. |
| Robustez contra respostas genéricas | 42 | Há boas proibições, mas não cobrem o drift estrutural. |
| Robustez contra conflito entre regras | 18 | Conflita com o filesystem atual e com a validação real. |
| Clareza de precedência | 35 | A hierarquia existe, mas aponta para autoridades extintas. |
| Acionabilidade | 30 | Parte do fluxo operacional cai em artefatos inexistentes. |
| Estabilidade entre execuções | 22 | Execuções divergem conforme o agente poda o que está quebrado. |
| Resistência a loopholes | 20 | Cumprimento superficial por substituição silenciosa é trivial. |

Nota final do arquivo:
`28`

Veredito:
`reprovado`

Por que não é 100/100:
Porque ainda descreve como soberanos arquivos que a própria consolidação removeu.

Falhas encontradas:
| Falha | Severidade | Tipo | Impacto prático | Cenário de quebra |
|-------|------------|------|-----------------|-------------------|
| §3.2 ainda lista `API_CONVENTIONS.md`, `ERROR_MODEL.md`, `UI_FOUNDATIONS.md` e `DESIGN_SYSTEM.md` | Crítica | conflito | A governança manda ler artefatos que não existem mais | O agente bloqueia tardiamente ou improvisa substituição |
| §2C reintroduz taxonomia e boundary já cobertos em outros lugares | Alta | redundância | Volta a criar superfície de drift | Um ajuste de módulo exige edição sincronizada em múltiplos arquivos |
| §5/§3B dependem de fontes agora inconsistentes com o estado do repo | Alta | precedência | O sistema perde fonte única real | O agente escolhe o documento mais conveniente |

Correções obrigatórias:
1. Remover da lista normativa todos os arquivos extintos e substituí-los apenas pelas fontes vivas.
2. Eliminar a taxonomia duplicada e apontar unicamente para `CLAUDE.md §2`.
3. Reescrever o arquivo para máximo de regra substantiva, não inventário histórico.

## Arquivo: .contract_driven/CONTRACT_SYSTEM_LAYOUT.md

Função real:
Definir layout canônico de filesystem e naming.
Deveria servir como mapa determinístico de paths vivos.

Tabela de pontuação:
| Critério | Nota | Justificativa objetiva |
|---------|------|------------------------|
| Qualidade instrucional real | 30 | O propósito é claro, mas o conteúdo ainda descreve o canon morto. |
| Determinismo real | 25 | A validação real já falhou em carregar a taxonomia canônica deste arquivo. |
| Eficiência de contexto real | 24 | 491 linhas para um mapa de layout continuam excessivas. |
| Robustez contra ambiguidade | 28 | Mistura paths vivos com referências removidas. |
| Robustez contra respostas genéricas | 38 | Alguns blocos ajudam, mas não fecham execução. |
| Robustez contra conflito entre regras | 18 | Conflita com o estado atual do diretório e com a consolidação anunciada. |
| Clareza de precedência | 34 | Redireciona soberania, mas não limpa o restante. |
| Acionabilidade | 28 | Agente continua encontrando paths mortos como se fossem canônicos. |
| Estabilidade entre execuções | 22 | A saída depende da capacidade do agente de ignorar o texto obsoleto. |
| Resistência a loopholes | 20 | Dá para obedecer “o espírito” e violar o layout real sem perceber. |

Nota final do arquivo:
`27`

Veredito:
`reprovado`

Por que não é 100/100:
Porque o arquivo que deveria fixar o layout ainda contém referências a docs removidos e já não é consumível de forma determinística pelo próprio pipeline.

Falhas encontradas:
| Falha | Severidade | Tipo | Impacto prático | Cenário de quebra |
|-------|------------|------|-----------------|-------------------|
| §1 e §4A seguem listando `ERROR_MODEL.md`, `UI_FOUNDATIONS.md`, `DESIGN_SYSTEM.md` | Crítica | conflito | Layout canônico aponta para artefatos mortos | Worker tenta localizar arquivo inexistente como se fosse obrigatório |
| Taxonomia do módulo não está em formato estável para o gate atual | Crítica | determinismo | `PATH_CANONICALITY_GATE` falha por não conseguir carregar a taxonomia | O pipeline trava antes da validação substantiva |
| Sobrevive muito texto descritivo sem efeito operacional | Média | contexto | Custo de leitura alto sem ganho real | O agente gasta janela em prosa sobre estrutura já conhecida |

Correções obrigatórias:
1. Remover todas as referências a artefatos removidos do canon.
2. Expor a taxonomia em formato estável e compatível com o parser/gate atual.
3. Reduzir o arquivo a paths, naming e exceções reais de layout.

## Arquivo: .contract_driven/GLOBAL_TEMPLATES.md

Função real:
Índice e política dos templates canônicos.
Na prática, virou repositório de memória do canon morto.

Tabela de pontuação:
| Critério | Nota | Justificativa objetiva |
|---------|------|------------------------|
| Qualidade instrucional real | 40 | Explica bem placeholders, mas preserva scaffolds que a solução disse ter eliminado. |
| Determinismo real | 36 | O agente não sabe se deve reinstanciar docs removidos ou ignorá-los. |
| Eficiência de contexto real | 18 | 673 linhas é custo alto para um índice de templates. |
| Robustez contra ambiguidade | 34 | “Template existe” e “doc foi removido” coexistem sem regra de exclusão. |
| Robustez contra respostas genéricas | 46 | Placeholders ajudam, mas não resolvem a governança quebrada. |
| Robustez contra conflito entre regras | 24 | Reintroduz arquivos extintos dentro do fluxo de scaffold. |
| Clareza de precedência | 42 | Diz que é índice, mas ainda orienta criação de artefatos removidos. |
| Acionabilidade | 38 | Parte do que manda instanciar já não pertence ao canon vivo. |
| Estabilidade entre execuções | 30 | Um agente conservador não instanciará; outro recriará o canon morto. |
| Resistência a loopholes | 26 | Permite “corrigir” o sistema recriando arquivos extintos. |

Nota final do arquivo:
`33`

Veredito:
`reprovado`

Por que não é 100/100:
Porque a redução de arquivos foi negada pelo próprio índice de templates.

Falhas encontradas:
| Falha | Severidade | Tipo | Impacto prático | Cenário de quebra |
|-------|------------|------|-----------------|-------------------|
| Mantém templates para `API_CONVENTIONS`, `ERROR_MODEL`, `UI_FOUNDATIONS` e `DESIGN_SYSTEM` | Crítica | conflito | A consolidação pode ser revertida por scaffold | Um agente recria docs removidos “obedecendo” ao template |
| Registro de placeholders é superdimensionado | Média | contexto | Infla tokens sem aumentar enforcement | O agente carrega 600+ linhas para usar poucos placeholders |
| Não há marcação explícita de template aposentado | Alta | manutenção | O repositório preserva dívida semântica indefinidamente | Novo mantenedor supõe que os templates ainda são válidos |

Correções obrigatórias:
1. Excluir do índice e do fluxo todos os templates de artefatos removidos do canon.
2. Separar registro de placeholders em arquivo auxiliar `gate_only` ou sob demanda estrita.
3. Marcar explicitamente templates aposentados e impedir sua instanciação.

## Arquivo: .contract_driven/agent_prompts/pre_contract_orchestrator.prompt.md

Função real:
Entry point obrigatório do fluxo CDD.
Classifica a tarefa, resolve boot, faz foundation readiness e transfere para o worker.

Tabela de pontuação:
| Critério | Nota | Justificativa objetiva |
|---------|------|------------------------|
| Qualidade instrucional real | 69 | Estrutura de fases é boa. |
| Determinismo real | 61 | Não garante que a evidência gerada reflita o boot real. |
| Eficiência de contexto real | 76 | Relativamente enxuto para o papel. |
| Robustez contra ambiguidade | 66 | Alguns critérios estão claros; outros dependem de arquivos em drift. |
| Robustez contra respostas genéricas | 72 | Evita pular fases, mas não fecha todas as entradas. |
| Robustez contra conflito entre regras | 54 | Herda conflito de `RULES`, `LAYOUT`, `README` e backlog. |
| Clareza de precedência | 78 | Fases e dependências estão ordenadas. |
| Acionabilidade | 68 | Operável, porém com boot/report desalinhos. |
| Estabilidade entre execuções | 58 | Depende do agente montar o boot “certo” apesar do drift. |
| Resistência a loopholes | 52 | É possível declarar “pré-contrato concluído” sem validar a evidência final. |

Nota final do arquivo:
`65`

Veredito:
`reprovado`

Por que não é 100/100:
O orquestrador continua central, mas não fecha a integridade entre prescrição, leitura efetiva e evidência publicada.

Falhas encontradas:
| Falha | Severidade | Tipo | Impacto prático | Cenário de quebra |
|-------|------------|------|-----------------|-------------------|
| Publica `boot_resolution_report.json` sem regra explícita de verificação contra o boot efetivo | Alta | determinismo | Evidência pode mentir sem bloqueio imediato | O relatório continua apontando `ERROR_MODEL.md` removido |
| F1.1 usa `OPERATIONS.md §4`, mas não cruza `MODULE_REGISTRY.expected_surfaces` | Alta | decisão | Foundation readiness pode aprovar superfície errada | O módulo parece pronto sem todas as superfícies exigidas |
| `module_status`, `owner` e `expected_surfaces` são passados adiante sem checagem de consistência com o boot montado | Média | precedência | Worker recebe contexto incoerente | O boot carrega menos do que o status do módulo exige |

Correções obrigatórias:
1. Validar programaticamente a lista de leituras contra `CLAUDE.md §7` antes de publicar a evidência.
2. Cruzar F1.1 com `MODULE_REGISTRY.expected_surfaces`.
3. Bloquear quando a evidência publicada divergir do contexto efetivamente carregado.

## Arquivo: .contract_driven/agent_prompts/create_openapi_contract.prompt.md

Função real:
Worker para criar ou revisar contratos OpenAPI por módulo.
É o principal prompt substantivo de authoring HTTP.

Tabela de pontuação:
| Critério | Nota | Justificativa objetiva |
|---------|------|------------------------|
| Qualidade instrucional real | 56 | Melhorou muito frente ao hardcode anterior. |
| Determinismo real | 50 | Ainda depende de registry não canonizado no boot e de output derivado inconsistente. |
| Eficiência de contexto real | 78 | Curto e focado. |
| Robustez contra ambiguidade | 54 | Alguns pré-requisitos não têm status normativo claro. |
| Robustez contra respostas genéricas | 68 | Obriga `api_rules.yaml` e falha cedo em alguns casos. |
| Robustez contra conflito entre regras | 44 | Não resolve conflito entre canon vivo e resíduos documentais. |
| Clareza de precedência | 72 | Ordem de leitura é objetiva. |
| Acionabilidade | 52 | Saída prometida inclui path derivado que não existe no repo atual. |
| Estabilidade entre execuções | 46 | Diverge conforme o agente trate `MODULE_PROFILE_REGISTRY` como normativo ou auxiliar. |
| Resistência a loopholes | 40 | O agente pode gerar só o path soberano e fingir que atualizou os derivados prometidos. |

Nota final do arquivo:
`56`

Veredito:
`reprovado`

Por que não é 100/100:
Ainda não está totalmente alinhado com o grafo canônico real nem com os caminhos derivados existentes.

Falhas encontradas:
| Falha | Severidade | Tipo | Impacto prático | Cenário de quebra |
|-------|------------|------|-----------------|-------------------|
| Depende de `.contract_driven/templates/api/MODULE_PROFILE_REGISTRY.yaml`, mas esse arquivo não está classificado no boot do sistema | Alta | precedência | Introduz autoridade operacional lateral | O worker usa regra que o boot não garante ter carregado |
| Saída promete `generated/contracts/openapi/paths/<MODULE>.yaml`, path inexistente no repositório atual | Crítica | completude | O prompt promete um derivado que não pode ser produzido no lugar descrito | O agente conclui a tarefa com saída inconsistente ou ignorada |
| Não contém regra explícita para remover referências normativas mortas do `openapi.yaml` root | Média | decisão | O root continua apontando para docs removidos | O contrato fica tecnicamente válido, mas documentalmente errado |

Correções obrigatórias:
1. Canonizar o papel de `MODULE_PROFILE_REGISTRY.yaml` ou remover sua dependência do worker.
2. Corrigir a seção de saída para os paths derivados que realmente existem.
3. Exigir saneamento das referências normativas mortas do root OpenAPI.

## Arquivo: .contract_driven/agent_prompts/create_module_docs.prompt.md

Função real:
Worker para criar o pacote mínimo de docs normativas do módulo.
Opera sobre templates de módulo e headers canônicos.

Tabela de pontuação:
| Critério | Nota | Justificativa objetiva |
|---------|------|------------------------|
| Qualidade instrucional real | 70 | O pacote mínimo está bem definido. |
| Determinismo real | 63 | Herda incerteza do `GLOBAL_TEMPLATES.md` e dos templates residuais. |
| Eficiência de contexto real | 82 | Curto para o que precisa fazer. |
| Robustez contra ambiguidade | 66 | Ainda depende do “gatilho do handebol” sem algoritmo determinístico. |
| Robustez contra respostas genéricas | 72 | Exige header, cross-refs e pacote mínimo. |
| Robustez contra conflito entre regras | 58 | Depende de uma camada de templates ainda poluída. |
| Clareza de precedência | 74 | Ordem de leitura está objetiva. |
| Acionabilidade | 70 | Executável no básico. |
| Estabilidade entre execuções | 61 | Varia por interpretação do gatilho esportivo e das docs condicionais. |
| Resistência a loopholes | 54 | O agente pode criar só os arquivos mínimos, mas com conteúdo raso. |

Nota final do arquivo:
`67`

Veredito:
`reprovado`

Por que não é 100/100:
O esqueleto mínimo está bom, mas a camada de template e o gatilho esportivo ainda deixam espaço demais para interpretação.

Falhas encontradas:
| Falha | Severidade | Tipo | Impacto prático | Cenário de quebra |
|-------|------------|------|-----------------|-------------------|
| Gatilho do handebol é referido, mas não operacionalizado em regra binária local | Média | decisão | Docs esportivas podem ser omitidas ou forçadas em excesso | Dois agentes chegam a pacotes diferentes para o mesmo módulo |
| O worker depende de templates que ainda preservam canon removido | Alta | conflito | A limpeza de arquivos pode ser revertida por scaffold indireto | Um agente reaproveita referências mortas no header ou nos related docs |

Correções obrigatórias:
1. Formalizar regra binária local para ativação do gatilho esportivo.
2. Saneiar a camada de templates antes de manter este worker como fonte confiável.
3. Exigir critérios mínimos de densidade por arquivo criado, não apenas existência.

## Arquivo: .contract_driven/agent_prompts/create_asyncapi_contract.prompt.md

Função real:
Worker para criação ou revisão de contratos AsyncAPI.
Deveria impedir boilerplate e forçar modelagem de canal/mensagem/operação.

Tabela de pontuação:
| Critério | Nota | Justificativa objetiva |
|---------|------|------------------------|
| Qualidade instrucional real | 58 | É simples, mas raso demais para o domínio que governa. |
| Determinismo real | 56 | Define leitura mínima, mas não define critérios mínimos de modelagem. |
| Eficiência de contexto real | 90 | Curto. |
| Robustez contra ambiguidade | 52 | Não define quando criar channel, operation ou message separados. |
| Robustez contra respostas genéricas | 42 | Boilerplate AsyncAPI continua viável. |
| Robustez contra conflito entre regras | 66 | Conflito baixo, densidade também baixa. |
| Clareza de precedência | 70 | Ordem mínima é legível. |
| Acionabilidade | 62 | Dá direção, mas não garante saída útil. |
| Estabilidade entre execuções | 54 | Dois agentes podem criar estruturas AsyncAPI muito diferentes. |
| Resistência a loopholes | 40 | Basta criar um arquivo “válido” e sem modelagem séria. |

Nota final do arquivo:
`59`

Veredito:
`reprovado`

Por que não é 100/100:
É instrucionalmente curto demais para impedir resposta genérica.

Falhas encontradas:
| Falha | Severidade | Tipo | Impacto prático | Cenário de quebra |
|-------|------------|------|-----------------|-------------------|
| Não define granularidade canônica entre channel/message/operation | Alta | decisão | Cada agente modela de um jeito | O contrato passa sintaticamente, mas diverge semanticamente |
| Não aponta template SSOT nem checklist de output mínimo | Alta | completude | AsyncAPI pode nascer como esqueleto vazio | Agente cria channel genérico e para ali |

Correções obrigatórias:
1. Adicionar template/canonical snippet obrigatório para channel, message e payload.
2. Definir critérios binários de quando usar `channels/`, `messages/` e `components/schemas/`.
3. Exigir evidência de vínculo com evento de domínio real e consumidor alvo.

## Arquivo: .contract_driven/agent_prompts/create_arazzo_workflow.prompt.md

Função real:
Worker para criação de workflows Arazzo.
Deveria amarrar fluxo multi-step ao OpenAPI root sem improviso.

Tabela de pontuação:
| Critério | Nota | Justificativa objetiva |
|---------|------|------------------------|
| Qualidade instrucional real | 60 | Tem objetivo correto, mas pouco conteúdo operacional. |
| Determinismo real | 59 | Exige `operationId`, mas não especifica a estrutura mínima do workflow. |
| Eficiência de contexto real | 92 | Muito curto. |
| Robustez contra ambiguidade | 54 | Não define steps, conditions, outputs ou compensações mínimas. |
| Robustez contra respostas genéricas | 44 | Esqueleto raso continua aceito. |
| Robustez contra conflito entre regras | 70 | Pouco conflito, pouca substância. |
| Clareza de precedência | 72 | Dependência do OpenAPI root está clara. |
| Acionabilidade | 64 | Ação básica é possível. |
| Estabilidade entre execuções | 57 | Workflows equivalentes podem sair muito diferentes. |
| Resistência a loopholes | 44 | Basta referenciar `operationId` existente para “cumprir”. |

Nota final do arquivo:
`62`

Veredito:
`reprovado`

Por que não é 100/100:
Não define o que torna um workflow realmente bom, completo e não-genérico.

Falhas encontradas:
| Falha | Severidade | Tipo | Impacto prático | Cenário de quebra |
|-------|------------|------|-----------------|-------------------|
| Falta checklist mínima de steps, inputs, outputs e falhas | Alta | completude | Workflow válido pode ser operacionalmente inútil | O agente cria só 2 steps lineares sem tratamento de erro |
| Não exige alinhamento com `TEST_MATRIX_<MODULE>.md` além da leitura | Média | decisão | Fluxo não cobre cenário crítico do módulo | O workflow ignora caso de compensação/rollback relevante |

Correções obrigatórias:
1. Definir schema mínimo para steps, inputs, outputs e error paths.
2. Exigir mapping explícito do workflow para cenários da test matrix.
3. Bloquear quando o workflow não cobrir pré-condições e pós-condições documentadas.

## Arquivo: .contract_driven/agent_prompts/create_json_schema_contract.prompt.md

Função real:
Worker para criação ou revisão de JSON Schemas soberanos.
Deveria traduzir invariantes em schema de forma repetível.

Tabela de pontuação:
| Critério | Nota | Justificativa objetiva |
|---------|------|------------------------|
| Qualidade instrucional real | 60 | O essencial está presente, mas ainda muito sintético. |
| Determinismo real | 58 | Faltam regras locais para traduzir invariantes em constraints. |
| Eficiência de contexto real | 90 | Curto. |
| Robustez contra ambiguidade | 55 | “alinhado ao canon” ainda depende de interpretação. |
| Robustez contra respostas genéricas | 48 | É possível gerar schema válido, porém raso. |
| Robustez contra conflito entre regras | 70 | Baixo conflito direto. |
| Clareza de precedência | 72 | Ordem de leitura é direta. |
| Acionabilidade | 66 | Serve como ponto de partida, não como protocolo fechado. |
| Estabilidade entre execuções | 58 | Tradução de business rules varia. |
| Resistência a loopholes | 46 | O agente pode limitar-se a `type/required` e ignorar invariantes mais densos. |

Nota final do arquivo:
`62`

Veredito:
`reprovado`

Por que não é 100/100:
Não fecha a passagem de invariantes e regras de domínio para constraints concretas.

Falhas encontradas:
| Falha | Severidade | Tipo | Impacto prático | Cenário de quebra |
|-------|------------|------|-----------------|-------------------|
| Não define como decidir entre `enum`, `pattern`, `format`, `allOf`, `oneOf`, `if/then` | Alta | decisão | Schemas do mesmo domínio saem heterogêneos | Dois agentes modelam a mesma regra com qualidade muito distinta |
| Não exige uso de template de schema base | Média | completude | Saída pode variar em estrutura e metadados | Schema válido nasce sem `$id`, descrições ou exemplos |

Correções obrigatórias:
1. Adicionar template mínimo de schema e checklist de metadados obrigatórios.
2. Definir matriz de decisão para mapear invariantes em keywords JSON Schema.
3. Bloquear schema que não demonstre tradução explícita das invariantes relevantes.

## Arquivo: .contract_driven/agent_prompts/create_ui_contract.prompt.md

Função real:
Worker para criar contrato de UI por módulo.
Deveria consumir o guia unificado de UI e alinhar UI com OpenAPI.

Tabela de pontuação:
| Critério | Nota | Justificativa objetiva |
|---------|------|------------------------|
| Qualidade instrucional real | 38 | O prompt ainda aponta para arquivos removidos. |
| Determinismo real | 30 | A instrução central de leitura mínima está quebrada. |
| Eficiência de contexto real | 84 | Curto, mas aponta para o lugar errado. |
| Robustez contra ambiguidade | 32 | O agente pode substituir por `UI_CONTRACT_GUIDE.md` ou bloquear. |
| Robustez contra respostas genéricas | 46 | Sem guia vivo carregado, o resultado tende a ser raso. |
| Robustez contra conflito entre regras | 24 | Conflita com a própria consolidação que criou `UI_CONTRACT_GUIDE.md`. |
| Clareza de precedência | 34 | O prompt não foi atualizado para o novo canon de UI. |
| Acionabilidade | 32 | Do jeito atual, o fluxo pode quebrar logo na leitura mínima. |
| Estabilidade entre execuções | 26 | Um agente bloqueia; outro improvisa; outro troca de arquivo por conta própria. |
| Resistência a loopholes | 22 | Cumprimento superficial por substituição silenciosa é fácil. |

Nota final do arquivo:
`33`

Veredito:
`reprovado`

Por que não é 100/100:
Porque ainda depende explicitamente de `UI_FOUNDATIONS.md` e `DESIGN_SYSTEM.md`, que foram removidos.

Falhas encontradas:
| Falha | Severidade | Tipo | Impacto prático | Cenário de quebra |
|-------|------------|------|-----------------|-------------------|
| Leitura mínima usa `docs/_canon/UI_FOUNDATIONS.md` e `docs/_canon/DESIGN_SYSTEM.md` | Crítica | conflito | O worker ficou incompatível com a nova estrutura | O agente falha cedo ou usa arquivo substituto sem autorização explícita |
| Não foi promovido para consumir `docs/_canon/UI_CONTRACT_GUIDE.md` | Alta | manutenção | A consolidação de UI não entra em operação real | A estrutura parece limpa, mas o worker continua morto |

Correções obrigatórias:
1. Substituir as duas referências removidas por `docs/_canon/UI_CONTRACT_GUIDE.md`.
2. Alinhar a checklist do worker às seções reais do guia unificado.
3. Revalidar o worker contra o pipeline de contratos após a atualização.

## Arquivo: .contract_driven/agent_prompts/decision_discovery.prompt.md

Função real:
Worker do estágio DSS.
Deveria tratar lacunas arquiteturais antes do authoring.

Tabela de pontuação:
| Critério | Nota | Justificativa objetiva |
|---------|------|------------------------|
| Qualidade instrucional real | 64 | Estrutura boa, mas com desalinho semântico para os task_types atuais. |
| Determinismo real | 58 | Usa `contract_creation` em vez de `new_contract`, criando bifurcação interpretativa. |
| Eficiência de contexto real | 78 | Enxuto para a função. |
| Robustez contra ambiguidade | 58 | A tabela de criticidade é boa, mas a entrada esperada já nasce desalinhada. |
| Robustez contra respostas genéricas | 70 | Exige proposta DSS estruturada. |
| Robustez contra conflito entre regras | 54 | Herda backlog inchado e checklist parcialmente obsoleta. |
| Clareza de precedência | 72 | Lê `DECISION_POLICY.md` primeiro. |
| Acionabilidade | 64 | Operável, mas com semântica de task_type quebrada. |
| Estabilidade entre execuções | 56 | O mesmo pedido pode ser tratado ou não como aplicável conforme a nomenclatura usada. |
| Resistência a loopholes | 46 | O agente pode rebatizar o task_type e seguir sem corrigir o problema canônico. |

Nota final do arquivo:
`62`

Veredito:
`reprovado`

Por que não é 100/100:
O worker está semanticamente desalinhado com o roteamento atual do sistema.

Falhas encontradas:
| Falha | Severidade | Tipo | Impacto prático | Cenário de quebra |
|-------|------------|------|-----------------|-------------------|
| Entrada esperada usa `contract_creation` em vez de `new_contract` | Alta | determinismo | DSS pode ser pulado ou invocado de forma inconsistente | Orchestrator e worker não falam o mesmo vocabulário |
| Depende de backlog que declara “sem decisões abertas” mas carrega histórico inteiro | Média | contexto | O estágio lê muito ruído para decidir nada | A sessão consome contexto sem ganho operacional |

Correções obrigatórias:
1. Alinhar os nomes de `task_type` com `CLAUDE.md §3`.
2. Reduzir dependência do backlog ao conjunto realmente aberto.
3. Atualizar o worker para falhar quando o task_type recebido não for canônico.

## Arquivo: .contract_driven/agent_prompts/adversarial_analysis.prompt.md

Função real:
Worker de análise adversarial entre contrato e implementação.
Deveria bloquear handoff quando faltam evidências de risco.

Tabela de pontuação:
| Critério | Nota | Justificativa objetiva |
|---------|------|------------------------|
| Qualidade instrucional real | 46 | A ideia é boa, mas o worker depende de referência inexistente e critérios ainda subjetivos. |
| Determinismo real | 40 | “coverage ≥ 80%” e várias checagens dependem de julgamento do agente. |
| Eficiência de contexto real | 74 | 190 linhas ainda aceitáveis para o escopo. |
| Robustez contra ambiguidade | 42 | Faltam regras binárias para várias perguntas de segurança. |
| Robustez contra respostas genéricas | 58 | O formato ajuda, mas continua possível checklist superficial. |
| Robustez contra conflito entre regras | 36 | Referencia `AUDIT_LOG_POLICY.md`, que não existe. |
| Clareza de precedência | 60 | Fases são claras; fontes não estão todas válidas. |
| Acionabilidade | 44 | Parte do roteiro fica sem fonte ativa. |
| Estabilidade entre execuções | 38 | Agentes diferentes darão notas diferentes ao mesmo contrato. |
| Resistência a loopholes | 34 | Dá para marcar vários itens como `N/A` sem critério duro. |

Nota final do arquivo:
`47`

Veredito:
`reprovado`

Por que não é 100/100:
A análise é ampla, mas não fechada o suficiente para ser determinística e ainda referencia arquivo inexistente.

Falhas encontradas:
| Falha | Severidade | Tipo | Impacto prático | Cenário de quebra |
|-------|------------|------|-----------------|-------------------|
| Referência a `docs/_canon/AUDIT_LOG_POLICY.md`, arquivo inexistente | Crítica | conflito | Uma das 10 dimensões centrais perde âncora normativa | O agente inventa critério de auditabilidade |
| Critério `coverage ≥ 80%` sem método de medição | Alta | determinismo | Resultado varia por avaliador | Dois agentes auditam o mesmo contrato com conclusões distintas |
| Output `_reports/adversarial/...` não está claramente integrado ao boot do handoff seguinte | Média | precedência | A análise existe, mas não se torna insumo confiável | `generate_code` depende do relatório sem protocolo de consumo |

Correções obrigatórias:
1. Substituir `AUDIT_LOG_POLICY.md` por ADR ou arquivo vivo existente.
2. Converter percentuais subjetivos em checklist binária e contável.
3. Canonizar o consumo do relatório adversarial no handoff para implementação.

## Arquivo: .contract_driven/agent_prompts/generate_code.prompt.md

Função real:
Worker para geração de backend.
Deveria transformar contratos aprovados em código no layout real do repositório.

Tabela de pontuação:
| Critério | Nota | Justificativa objetiva |
|---------|------|------------------------|
| Qualidade instrucional real | 36 | O detalhamento parece bom, mas o path alvo não existe no workspace. |
| Determinismo real | 30 | O worker descreve uma árvore de backend externa ao repositório real. |
| Eficiência de contexto real | 64 | Detalhado, porém muito do detalhe é operacionalmente inaplicável. |
| Robustez contra ambiguidade | 34 | O agente não sabe se deve criar uma nova raiz ou adaptar ao repo atual. |
| Robustez contra respostas genéricas | 60 | Bons snippets de camada reduzem boilerplate. |
| Robustez contra conflito entre regras | 24 | Conflita com a estrutura real e com outros canons de stack. |
| Clareza de precedência | 54 | Pré-requisitos claros; destino físico não. |
| Acionabilidade | 28 | Sem `Hb Track - Backend/`, o worker não é realmente executável. |
| Estabilidade entre execuções | 26 | Um agente cria nova pasta; outro tenta adaptar; outro bloqueia. |
| Resistência a loopholes | 22 | Cumprimento superficial por “exemplo teórico” é fácil. |

Nota final do arquivo:
`38`

Veredito:
`reprovado`

Por que não é 100/100:
O worker não está ancorado no layout real do código.

Falhas encontradas:
| Falha | Severidade | Tipo | Impacto prático | Cenário de quebra |
|-------|------------|------|-----------------|-------------------|
| Usa `Hb Track - Backend/src/...`, path inexistente no repositório | Crítica | completude | Geração backend não tem destino físico confiável | O agente escreve em lugar errado ou bloqueia |
| Depende de `_reports/adversarial/...` sem pipeline de consumo totalmente canonizado | Alta | precedência | Handoff implementação depende de artefato lateral | O worker usa relatório ausente ou desatualizado |

Correções obrigatórias:
1. Alinhar o worker ao layout real do backend ou canonizar a nova raiz.
2. Definir destino físico único e verificável por gate.
3. Formalizar como o relatório adversarial vira pré-requisito técnico consumível.

## Arquivo: .contract_driven/agent_prompts/generate_frontend.prompt.md

Função real:
Worker para geração de frontend.
Deveria materializar a estratégia frontend aprovada no repositório real.

Tabela de pontuação:
| Critério | Nota | Justificativa objetiva |
|---------|------|------------------------|
| Qualidade instrucional real | 30 | O worker é detalhado, mas opera sobre estrutura ausente e referencia doc removido. |
| Determinismo real | 24 | Frontend path, cliente HTTP e stack conflitam com outros canons. |
| Eficiência de contexto real | 58 | 235 linhas para um fluxo ainda inexequível é caro. |
| Robustez contra ambiguidade | 28 | React/Vite, openapi-fetch e `schema.d.ts` entram em choque com outros documentos. |
| Robustez contra respostas genéricas | 62 | Os snippets reduzem boilerplate. |
| Robustez contra conflito entre regras | 20 | Conflita com `FRONTEND_CONTRACT.md`, `ARCHITECTURE.md` e a própria ausência da pasta `frontend/`. |
| Clareza de precedência | 48 | Etapas claras; base canônica incoerente. |
| Acionabilidade | 20 | `frontend/` não existe. |
| Estabilidade entre execuções | 18 | Três agentes podem tomar três decisões de scaffolding diferentes. |
| Resistência a loopholes | 18 | Fácil “cumprir” gerando só exemplos em vez de código real. |

Nota final do arquivo:
`33`

Veredito:
`reprovado`

Por que não é 100/100:
O worker depende de uma superfície frontend inexistente e de canon de stack inconsistente.

Falhas encontradas:
| Falha | Severidade | Tipo | Impacto prático | Cenário de quebra |
|-------|------------|------|-----------------|-------------------|
| Usa `frontend/src/api/schema.d.ts`, mas `frontend/` não existe | Crítica | completude | O worker não tem destino real de escrita | A geração falha ou cria árvore paralela arbitrária |
| Continua referenciando `docs/_canon/DESIGN_SYSTEM.md` “se existir” | Alta | conflito | Carrega resíduo do canon morto | O agente improvisa substituição sem regra |
| Stack descrita conflita com outros canons (React/Vite vs Next.js/React Native/Axios) | Crítica | determinismo | Implementação frontend não tem base única | Dois workers distintos geram arquiteturas incompatíveis |

Correções obrigatórias:
1. Canonizar a estrutura frontend real antes de manter este worker ativo.
2. Substituir referências removidas pelo guia vivo e único.
3. Unificar stack frontend entre worker, `FRONTEND_CONTRACT.md` e `ARCHITECTURE.md`.

## Arquivo: docs/_canon/README.md

Função real:
Landing page do canon global.
Deveria ser mapa fiel do canon vivo e da ordem correta de leitura.

Tabela de pontuação:
| Critério | Nota | Justificativa objetiva |
|---------|------|------------------------|
| Qualidade instrucional real | 24 | Hoje descreve um canon que não existe mais. |
| Determinismo real | 18 | A ordem de leitura manda consultar arquivos removidos. |
| Eficiência de contexto real | 32 | 105 linhas que reintroduzem dívida morta. |
| Robustez contra ambiguidade | 18 | “existe como guia/ponteiro” para doc apagado é ambiguidade material. |
| Robustez contra respostas genéricas | 40 | Ajuda a navegar, mas para o mapa errado. |
| Robustez contra conflito entre regras | 12 | Conflita diretamente com a nova estrutura. |
| Clareza de precedência | 42 | Explica bem a hierarquia, mas com inventário errado. |
| Acionabilidade | 18 | Seguir este arquivo leva a caminhos mortos. |
| Estabilidade entre execuções | 14 | Agente pode parar, improvisar ou ignorar a landing. |
| Resistência a loopholes | 14 | Fácil fingir que a landing é “só navegação” e deixar o erro vivo. |

Nota final do arquivo:
`23`

Veredito:
`reprovado`

Por que não é 100/100:
A landing canônica ainda está listando `API_CONVENTIONS.md`, `ERROR_MODEL.md`, `UI_FOUNDATIONS.md`, `DESIGN_SYSTEM.md` e `BOOT_PROFILES.md`.

Falhas encontradas:
| Falha | Severidade | Tipo | Impacto prático | Cenário de quebra |
|-------|------------|------|-----------------|-------------------|
| Inventário do canon global inclui arquivos removidos | Crítica | conflito | Navegação canônica leva a docs inexistentes | Agente novo consulta o README e segue para dead ends |
| Ordem recomendada de leitura manda ler `BOOT_PROFILES.md` | Crítica | precedência | O boot vivo deixa de ser a fonte efetiva de leitura | O humano ou agente usa manual errado |

Correções obrigatórias:
1. Reescrever o inventário para conter apenas arquivos vivos.
2. Atualizar a ordem de leitura para `CLAUDE.md §7` e `UI_CONTRACT_GUIDE.md`.
3. Remover qualquer menção a arquivos removidos.

## Arquivo: docs/_canon/OPERATIONS.md

Função real:
Referência operacional condensada.
Deveria concentrar soberania, boundary, precedência, artefatos e validações vivas.

Tabela de pontuação:
| Critério | Nota | Justificativa objetiva |
|---------|------|------------------------|
| Qualidade instrucional real | 58 | A proposta é boa, mas a seção de precedência ainda carrega canon morto. |
| Determinismo real | 52 | Ajuda bastante, mas não resolve os conflitos herdados. |
| Eficiência de contexto real | 82 | 110 linhas é bom tamanho. |
| Robustez contra ambiguidade | 50 | Lista `API_CONVENTIONS` e `ERROR_MODEL` como nível 5. |
| Robustez contra respostas genéricas | 70 | Tabelas densas reduzem improviso. |
| Robustez contra conflito entre regras | 42 | Continua inconsistente com a consolidação final. |
| Clareza de precedência | 72 | Estrutura boa, conteúdo ainda parcialmente velho. |
| Acionabilidade | 64 | Útil no dia a dia, mas não totalmente confiável. |
| Estabilidade entre execuções | 52 | Varia conforme o agente ignore ou respeite as referências mortas. |
| Resistência a loopholes | 40 | Dá para seguir só as partes que funcionam e fingir aderência total. |

Nota final do arquivo:
`58`

Veredito:
`reprovado`

Por que não é 100/100:
O novo arquivo mais promissor da consolidação ainda não foi limpo completamente.

Falhas encontradas:
| Falha | Severidade | Tipo | Impacto prático | Cenário de quebra |
|-------|------------|------|-----------------|-------------------|
| §3 ainda lista `API_CONVENTIONS.md` e `ERROR_MODEL.md` na precedência | Alta | conflito | O resumo operacional segue apontando para o canon morto | O agente trata docs removidos como nível substantivo |
| Boundary rules e artefatos obrigatórios não se conectam automaticamente a `MODULE_REGISTRY.expected_surfaces` | Média | decisão | Readiness pode ficar incompleta | O resumo aprova menos do que o registry exige |

Correções obrigatórias:
1. Limpar a seção de precedência para refletir apenas fontes vivas.
2. Cruzar artefatos obrigatórios com `MODULE_REGISTRY.expected_surfaces`.
3. Tornar explícito o status de arquivos substituídos: removidos e proibidos.

## Arquivo: docs/_canon/CONTRACT_PIPELINE.md

Função real:
Registro oficial dos estágios do pipeline CDD.
Deveria ligar regra normativa, boot, gates, evidência e handoff.

Tabela de pontuação:
| Critério | Nota | Justificativa objetiva |
|---------|------|------------------------|
| Qualidade instrucional real | 84 | Um dos arquivos mais acertados da consolidação. |
| Determinismo real | 80 | A cadeia normativa/registro/enforcement está bem definida. |
| Eficiência de contexto real | 86 | Curto e denso. |
| Robustez contra ambiguidade | 78 | Estágios e condições de avanço estão objetivos. |
| Robustez contra respostas genéricas | 82 | Fecha bem o pipeline macro. |
| Robustez contra conflito entre regras | 76 | Quase limpo; depende de arquivos subordinados ainda em drift. |
| Clareza de precedência | 84 | Papel do prompt e do boot ficou claro. |
| Acionabilidade | 82 | Usável como mapa operacional. |
| Estabilidade entre execuções | 78 | O pipeline macro tende a ser constante. |
| Resistência a loopholes | 72 | Ainda é possível declarar estágio cumprido sem validar artefatos subordinados. |

Nota final do arquivo:
`80`

Veredito:
`aprovado`

Por que não é 100/100:
Depende de arquivos subordinados que ainda não foram saneados.

Falhas encontradas:
| Falha | Severidade | Tipo | Impacto prático | Cenário de quebra |
|-------|------------|------|-----------------|-------------------|
| O estágio Readiness referencia artefatos dependentes ainda desalinhados com o repo | Média | manutenção | O pipeline macro está certo, mas o micro não acompanha | Readiness exige scorecard e IR ainda com drift |
| Não há regra explícita de invalidação de evidência derivada antiga | Média | determinismo | Relatórios velhos podem sobreviver como se fossem atuais | Um humano usa `latest.json` antigo para decidir avanço |

Correções obrigatórias:
1. Acrescentar regra de invalidação automática de evidência derivada obsoleta.
2. Ligar Readiness a uma lista de dependências vivas e saneadas.
3. Exigir que cada estágio falhe quando a evidência referenciar artefato removido.

## Arquivo: docs/_canon/UI_CONTRACT_GUIDE.md

Função real:
Arquivo unificado de fundamentos e design system de UI.
Substitui dois arquivos antigos.

Tabela de pontuação:
| Critério | Nota | Justificativa objetiva |
|---------|------|------------------------|
| Qualidade instrucional real | 68 | A fusão foi correta, mas o conteúdo ainda é pouco verificável. |
| Determinismo real | 64 | Princípios são claros; enforcement continua fraco. |
| Eficiência de contexto real | 86 | Muito menor que a solução anterior. |
| Robustez contra ambiguidade | 60 | Falta mapping explícito para seções mínimas do UI_CONTRACT. |
| Robustez contra respostas genéricas | 52 | Um agente ainda pode produzir contrato de UI genérico. |
| Robustez contra conflito entre regras | 80 | O arquivo em si é coerente. |
| Clareza de precedência | 72 | É o substituto natural, mas nem todos os workers foram atualizados. |
| Acionabilidade | 66 | Útil como guia, não como protocolo fechado. |
| Estabilidade entre execuções | 62 | Depende da maturidade do agente que consome. |
| Resistência a loopholes | 48 | Dá para listar princípios sem descer para comportamento concreto. |

Nota final do arquivo:
`66`

Veredito:
`aprovado`

Por que não é 100/100:
Consolidou certo, mas ainda sem força suficiente para impedir UI_CONTRACT mediano.

Falhas encontradas:
| Falha | Severidade | Tipo | Impacto prático | Cenário de quebra |
|-------|------------|------|-----------------|-------------------|
| Não define estrutura mínima de `UI_CONTRACT_<MODULE>.md` | Alta | completude | O worker cria contratos heterogêneos | Dois módulos acabam com contratos de UI incomparáveis |
| Regras de composição não têm critérios verificáveis | Média | loophole | O agente pode repetir slogans de UX sem decisão concreta | UI_CONTRACT sai bonito no texto e fraco na execução |

Correções obrigatórias:
1. Definir seções obrigatórias do `UI_CONTRACT`.
2. Tornar verificáveis os estados e componentes mínimos por fluxo.
3. Atualizar todos os workers/UI docs para consumi-lo como única fonte.

## Arquivo: docs/_canon/gates/GATES_REGISTRY.yaml

Função real:
Registry machine-readable dos gates.
Deveria refletir exatamente o pipeline vivo e suas fontes normativas atuais.

Tabela de pontuação:
| Critério | Nota | Justificativa objetiva |
|---------|------|------------------------|
| Qualidade instrucional real | 60 | Estrutura YAML é boa e útil para tooling. |
| Determinismo real | 54 | Algumas descrições ainda apontam para fontes removidas ou caminhos inexistentes. |
| Eficiência de contexto real | 62 | 703 linhas é aceitável para registry, mas ainda há sobra de texto desatualizado. |
| Robustez contra ambiguidade | 50 | Gate ativo ainda referencia `API_CONVENTIONS.md` e backend path inexistente. |
| Robustez contra respostas genéricas | 72 | Gate IDs e severidades restringem bem o pipeline. |
| Robustez contra conflito entre regras | 42 | Registry não está 100% sincronizado com canon vivo. |
| Clareza de precedência | 80 | Fonte de autoridade e evidência estão nomeadas. |
| Acionabilidade | 68 | Ferramentas o consomem, mas com pressupostos já vencidos. |
| Estabilidade entre execuções | 54 | Estável para tooling; instável na semântica de algumas descrições. |
| Resistência a loopholes | 44 | Descrição desatualizada permite justificar falso entendimento do gate. |

Nota final do arquivo:
`59`

Veredito:
`reprovado`

Por que não é 100/100:
Um registry de gates não pode continuar referenciando documentos já removidos do canon.

Falhas encontradas:
| Falha | Severidade | Tipo | Impacto prático | Cenário de quebra |
|-------|------------|------|-----------------|-------------------|
| `OPENAPI_POLICY_RULESET_GATE` ainda descreve conformidade com `docs/_canon/API_CONVENTIONS.md` | Alta | conflito | Registry aponta para fonte morta de API | A equipe entende o gate a partir de documento extinto |
| `CODE_ARCHITECTURE_GATE` assume `Hb Track - Backend/src/` | Crítica | completude | Gate modela layout backend inexistente | O registry legitima estrutura não canonizada no repo |

Correções obrigatórias:
1. Reescrever descrições de gates para fontes vivas apenas.
2. Alinhar `CODE_ARCHITECTURE_GATE` ao layout real do workspace.
3. Rodar diff estrutural entre registry e implementações para eliminar drift semântico.

## Arquivo: contracts/openapi/openapi.yaml

Função real:
Entrypoint soberano da API HTTP.
Também funciona como peça de orientação normativa para implementadores.

Tabela de pontuação:
| Critério | Nota | Justificativa objetiva |
|---------|------|------------------------|
| Qualidade instrucional real | 54 | Estruturalmente forte, documentalmente contaminado por referências mortas. |
| Determinismo real | 52 | A spec é válida, mas a descrição normativa induz leitura errada. |
| Eficiência de contexto real | 72 | O problema não é tamanho, é semântica residual. |
| Robustez contra ambiguidade | 46 | O contrato root segue mandando consultar docs removidos. |
| Robustez contra respostas genéricas | 76 | O shape técnico é forte. |
| Robustez contra conflito entre regras | 40 | Descrição conflita com a nova estrutura. |
| Clareza de precedência | 74 | Continua como entrypoint soberano. |
| Acionabilidade | 66 | Executável tecnicamente, mas orienta mal. |
| Estabilidade entre execuções | 50 | Agente pode seguir a spec e ignorar a descrição; outro pode tentar seguir a descrição morta. |
| Resistência a loopholes | 38 | Fácil dizer “a spec está boa” e ignorar o drift documental. |

Nota final do arquivo:
`57`

Veredito:
`reprovado`

Por que não é 100/100:
Porque o entrypoint mais crítico da superfície HTTP ainda cita `ERROR_MODEL.md` e `API_CONVENTIONS.md`.

Falhas encontradas:
| Falha | Severidade | Tipo | Impacto prático | Cenário de quebra |
|-------|------------|------|-----------------|-------------------|
| `info.description` manda consultar `docs/_canon/ERROR_MODEL.md` | Alta | conflito | O contrato aponta para fonte inexistente para erros HTTP | Implementador procura convenção em arquivo morto |
| `info.description` manda consultar `docs/_canon/API_CONVENTIONS.md` | Alta | conflito | A superfície HTTP reforça uma fonte removida | Novo contrato perpetua a dependência errada |

Correções obrigatórias:
1. Limpar as referências normativas mortas do `info.description`.
2. Apontar apenas para `api_rules.yaml`, `SYSTEM_SCOPE.md` e demais fontes vivas.
3. Regerar baseline e derivados após a correção do root.

## Arquivo: _reports/evidence/boot_resolution_report.json

Função real:
Evidência machine-readable do boot efetivamente aplicado pelo orquestrador.
Deveria ser a prova objetiva de que o boot prescrito foi cumprido.

Tabela de pontuação:
| Critério | Nota | Justificativa objetiva |
|---------|------|------------------------|
| Qualidade instrucional real | 16 | Como evidência, hoje está objetivamente errada. |
| Determinismo real | 12 | O arquivo contradiz o estado atual do sistema. |
| Eficiência de contexto real | 80 | Curto, mas incorreto. |
| Robustez contra ambiguidade | 10 | Lista `ERROR_MODEL.md` removido como leitura obrigatória. |
| Robustez contra respostas genéricas | 18 | Não ajuda a evitar resposta fraca; ajuda a mascarar drift. |
| Robustez contra conflito entre regras | 8 | Conflita com a estrutura viva e com o próprio boot atual. |
| Clareza de precedência | 20 | Não deixa claro se é evidência atual ou resíduo histórico. |
| Acionabilidade | 10 | Não pode ser usado com segurança para auditoria. |
| Estabilidade entre execuções | 10 | Já nasceu obsoleto e não foi invalidado. |
| Resistência a loopholes | 8 | É a própria materialização do loophole “boot declarado ≠ boot real”. |

Nota final do arquivo:
`19`

Veredito:
`reprovado`

Por que não é 100/100:
Porque a evidência obrigatória de boot está factual e operacionalmente desatualizada.

Falhas encontradas:
| Falha | Severidade | Tipo | Impacto prático | Cenário de quebra |
|-------|------------|------|-----------------|-------------------|
| `mandatory_reads` ainda inclui `docs/_canon/ERROR_MODEL.md` | Crítica | determinismo | A prova de boot contradiz o canon vivo | Auditoria ou agente confiam em leitura inexistente |
| Não há versão/schema que permita invalidar relatório gerado contra estrutura anterior | Alta | manutenção | Resíduo antigo continua parecendo atual | O pipeline usa “latest known evidence” errada |

Correções obrigatórias:
1. Regenerar o arquivo com a resolução real atual.
2. Adicionar schema/versionamento da evidência para invalidar formatos antigos.
3. Bloquear handoff quando o report mencionar artefato removido.

## Arquivo: _reports/contract_gates/latest.json

Função real:
Relatório corrente do pipeline de gates.
Deveria ser a fotografia confiável da saúde contratual do sistema.

Tabela de pontuação:
| Critério | Nota | Justificativa objetiva |
|---------|------|------------------------|
| Qualidade instrucional real | 42 | Após rerun, o arquivo corretamente mostra FAIL, mas também expõe dependências mortas ainda consideradas obrigatórias. |
| Determinismo real | 38 | O relatório muda, mas o próprio baseline do pipeline ainda contém pressupostos errados. |
| Eficiência de contexto real | 54 | Grande, porém justificável como evidência. |
| Robustez contra ambiguidade | 34 | Antes do rerun havia sinal contraditório; agora há falha, mas o grafo normativo segue quebrado. |
| Robustez contra respostas genéricas | 70 | Como evidência, é detalhado. |
| Robustez contra conflito entre regras | 28 | Registra conflito estrutural sem resolvê-lo. |
| Clareza de precedência | 58 | Mostra gates e entradas, mas não diferencia bem regra viva de dependência legada. |
| Acionabilidade | 46 | Ajuda a encontrar falhas, mas parte das falhas já deveria ter sido resolvida no canon. |
| Estabilidade entre execuções | 36 | Um relatório anterior recente parecia aceitar o estado; o atual reprova. |
| Resistência a loopholes | 26 | Pode ser ignorado como “só um relatório” embora seja evidência de quebra real. |

Nota final do arquivo:
`43`

Veredito:
`reprovado`

Por que não é 100/100:
É evidência útil, mas prova que a nova estrutura não fechou seu próprio enforcement.

Falhas encontradas:
| Falha | Severidade | Tipo | Impacto prático | Cenário de quebra |
|-------|------------|------|-----------------|-------------------|
| O pipeline ainda considera `docs/_canon/BOOT_PROFILES.md` e `docs/_canon/ERROR_MODEL.md` obrigatórios | Crítica | conflito | A estrutura removida continua viva no enforcement | O sistema não chega a readiness mesmo após consolidação |
| O relatório recente mostra que a governança e o enforcement divergiram por pelo menos um ciclo | Alta | estabilidade | Pode haver falsa aprovação anterior | Decisão humana foi tomada com base em estado aparentemente verde |

Correções obrigatórias:
1. Atualizar a lista de artefatos obrigatórios e os gates para o canon vivo.
2. Limpar relatórios anteriores ou marcá-los explicitamente como incompatíveis.
3. Tratar qualquer referência morta no report como incidente de governança, não só como detalhe técnico.

## BLOCO 4 — CASOS DE QUEBRA

| Condição de entrada | Ponto de falha | Arquivo(s) envolvido(s) | Consequência no comportamento | Severidade |
|---------------------|----------------|--------------------------|-------------------------------|------------|
| Pedido `new_ui_contract` em módulo com UI real | Worker lê `UI_FOUNDATIONS.md` e `DESIGN_SYSTEM.md`, ambos removidos | `create_ui_contract.prompt.md`, `docs/_canon/UI_CONTRACT_GUIDE.md` | O agente bloqueia, improvisa substituição ou produz contrato de UI genérico | Crítica |
| Pedido `generate_frontend` | Worker exige `frontend/src/api/schema.d.ts`, mas `frontend/` não existe | `generate_frontend.prompt.md`, `docs/_canon/FRONTEND_CONTRACT.md`, `docs/_canon/ARCHITECTURE.md` | Geração inexequível ou scaffolding arbitrário fora do repo real | Crítica |
| Pedido `generate_code` | Worker aponta para `Hb Track - Backend/src/`, path inexistente | `generate_code.prompt.md`, `docs/_canon/CODE_ARCHITECTURE.md` | Código vai para árvore errada, ou o agente trava, ou ignora o worker | Crítica |
| Execução do pipeline contratual | Gates ainda exigem `BOOT_PROFILES.md` e `ERROR_MODEL.md` | `GATES_REGISTRY.yaml`, `CI_CONTRACT_GATES.md`, `_reports/contract_gates/latest.json` | A própria consolidação falha na validação real | Crítica |
| Auditor usa evidência de boot | Evidência aponta `ERROR_MODEL.md` como leitura obrigatória | `_reports/evidence/boot_resolution_report.json`, `CLAUDE.md`, `pre_contract_orchestrator.prompt.md` | O sistema parece obedecer ao boot, mas a prova é falsa | Crítica |
| Novo agente entra pelo canon | Landing canônica lista arquivos mortos | `docs/_canon/README.md` | Navegação inicial incorreta; perda de tempo e inferência indevida | Alta |
| Criação/revisão OpenAPI | `openapi.yaml` manda consultar `ERROR_MODEL.md` e `API_CONVENTIONS.md` | `contracts/openapi/openapi.yaml`, `create_openapi_contract.prompt.md` | Contrato tecnicamente válido, mas com documentação normativa morta | Alta |
| Decision Discovery acionado por `new_contract` | Worker espera `contract_creation` | `decision_discovery.prompt.md`, `CLAUDE.md` | DSS pode ser pulado, rebatizado ou aplicado de forma inconsistente | Alta |
| Instanciação de template global | Índice e templates ainda permitem recriar docs removidos | `GLOBAL_TEMPLATES.md`, `.contract_driven/templates/globais/*` | Redução de arquivos é revertida “obedecendo” ao scaffold | Alta |
| Uso de backlog arquitetural | Arquivo declara zero abertos, mas carrega histórico resolvido inteiro | `ARCHITECTURE_DECISION_BACKLOG.md`, `DECISION_POLICY.md` | Consumo de contexto sem valor operacional e risco de leitura equivocada | Média |
| Leitura de stack frontend/backend | Canon de stack entra em conflito entre React/Vite, Next.js e React Native; Python/Postgres também divergem | `ARCHITECTURE.md`, `FRONTEND_CONTRACT.md`, `CODE_ARCHITECTURE.md`, `generate_frontend.prompt.md` | Implementação depende de escolha subjetiva do agente | Crítica |
| Adversarial analysis de logging | Worker procura `AUDIT_LOG_POLICY.md`, que não existe | `adversarial_analysis.prompt.md`, `ARCHITECTURE.md`, `SECURITY_RULES.md` | Parte da análise de risco vira inferência livre | Alta |

## BLOCO 5 — REGRESSÕES DE CONTEXTO

| Arquivo ou decisão estrutural | Regressão identificada | Impacto em tokens/contexto | Gravidade | Correção |
|------------------------------|------------------------|----------------------------|----------|----------|
| `.contract_driven/GLOBAL_TEMPLATES.md` | Consolidou templates, mas preservou scaffolds do canon removido | 673 linhas de índice + reintrodução semântica do canon morto | Alta | Remover templates aposentados e mover registro de placeholders para leitura sob demanda |
| `.contract_driven/templates/globais/{API_CONVENTIONS,ERROR_MODEL,UI_FOUNDATIONS,DESIGN_SYSTEM}.md` | “Arquivos removidos” continuam existindo como templates | 167 linhas de texto morto + risco de recriação | Alta | Excluir ou aposentar formalmente esses templates |
| `docs/_canon/README.md` | Landing ainda lista arquivos removidos e `BOOT_PROFILES.md` | Reabre custo de navegação e interpretação | Alta | Reescrever inventário e ordem de leitura |
| `.contract_driven/CONTRACT_SYSTEM_RULES.md` | Continua listando soberanos mortos e taxonomia duplicada | 820 linhas ainda caras e parcialmente obsoletas | Alta | Reduzir para regra substantiva viva |
| `.contract_driven/CONTRACT_SYSTEM_LAYOUT.md` | Continua listando docs removidos em paths canônicos | 491 linhas com ruído estrutural | Alta | Enxugar para layout real vivo |
| `docs/_canon/ARCHITECTURE_DECISION_BACKLOG.md` | Declara zero decisões abertas, mas carrega histórico resolvido detalhado | 227 linhas de contexto quase todo não operacional | Média | Manter só entradas abertas no backlog vivo; mover histórico resolvido para índice curto |
| `docs/_canon/UI_CONTRACT_GUIDE.md` | Melhorou clareza local, mas ficou genérico demais para substituir dois arquivos sem perda | Redução de tokens com perda de acionabilidade | Média | Adicionar critérios verificáveis e estrutura mínima do UI_CONTRACT |
| `_reports/evidence/boot_resolution_report.json` | Evidência curta, porém errada | Pouco token, alto dano contextual | Alta | Invalidar e regerar automaticamente |
| `generate_frontend.prompt.md` | Alto detalhamento para stack/path inexistentes | 235 linhas gastas em fluxo inexequível | Alta | Congelar worker até canonizar estrutura real |
| `generate_code.prompt.md` | Alto detalhamento para backend inexistente | 242 linhas de custo sem destino físico confiável | Alta | Alinhar ao repo real antes de manter ativo |

## BLOCO 6 — LACUNAS DE DETERMINISMO E QUALIDADE

### bloqueadores críticos;
- O pipeline real ainda falha porque a governança continua exigindo `BOOT_PROFILES.md` e `ERROR_MODEL.md`.
- Workers ativos e relevantes dependem de arquivos removidos (`create_ui_contract`) ou de paths inexistentes (`generate_code`, `generate_frontend`).
- O boot prescrito e a evidência de boot publicada divergem; isso destrói o determinismo operacional.
- Há conflito material entre canons de stack/arquitetura (`ARCHITECTURE.md`, `FRONTEND_CONTRACT.md`, `CODE_ARCHITECTURE.md`) suficiente para mudar a implementação resultante.

### bloqueadores altos;
- `GLOBAL_TEMPLATES.md` e os templates residuais mantêm viva a possibilidade de recriar o canon morto.
- `docs/_canon/README.md` e `contracts/openapi/openapi.yaml` continuam apontando para fontes removidas.
- `decision_discovery.prompt.md` usa semântica de `task_type` divergente do roteamento atual.
- `adversarial_analysis.prompt.md` contém dependência de arquivo inexistente e critério subjetivo de cobertura.

### bloqueadores médios;
- `ARCHITECTURE_DECISION_BACKLOG.md` continua caro em contexto e com ruído histórico.
- `UI_CONTRACT_GUIDE.md` consolidou, mas perdeu parte da força operacional.
- `create_asyncapi`, `create_arazzo` e `create_json_schema` ainda são prompts magros demais para impedir boilerplate.
- A malha de testes passou (`9 passed`) sem detectar a inconsistência documental real, o que revela cobertura insuficiente.

### bloqueadores baixos.
- `SESSION_HANDOFF.md` ainda permite preenchimento genérico.
- `CLAUDE.md §8` mantém redundância de paths.
- Alguns relatórios antigos permanecem legíveis sem marcação forte de incompatibilidade estrutural.

## BLOCO 7 — TESTE DE LOOPHOLES

| Arquivo | Exemplo de loophole |
|--------|----------------------|
| Arquitetura geral | O agente ignora referências mortas, usa só os arquivos que “ainda existem” e entrega algo aparentemente bom, mas não determinístico e incompatível com o enforcement. |
| `CLAUDE.md` | O agente segue §7 superficialmente, mas publica evidência de boot errada sem bloquear. |
| `SESSION_HANDOFF.md` | O agente escreve “feito / próximo passo” sem artefatos, bloqueios ou decisões, e o handoff parece completo. |
| `.contract_driven/CONTRACT_SYSTEM_RULES.md` | O agente troca mentalmente `API_CONVENTIONS.md` por `api_rules.yaml` e continua sem registrar que a regra formal está errada. |
| `.contract_driven/CONTRACT_SYSTEM_LAYOUT.md` | O agente usa o layout real do disco e ignora as referências mortas, fingindo conformidade total com o layout canônico. |
| `.contract_driven/GLOBAL_TEMPLATES.md` | O agente recria `ERROR_MODEL.md` e `API_CONVENTIONS.md` a partir dos templates e alega que “corrigiu” a governança. |
| `pre_contract_orchestrator.prompt.md` | O agente declara “pré-contrato concluído” sem conferir se o `boot_resolution_report.json` reflete as leituras reais. |
| `create_openapi_contract.prompt.md` | O agente atualiza só `contracts/openapi/paths/<MODULE>.yaml` e afirma que também atualizou derivados que nem existem nesse path. |
| `create_module_docs.prompt.md` | O agente cria os cinco arquivos mínimos com duas linhas cada e a tarefa parece cumprida. |
| `create_asyncapi_contract.prompt.md` | O agente cria um AsyncAPI formalmente válido, porém sem separar message, channel e semantics de consumidor. |
| `create_arazzo_workflow.prompt.md` | O agente cria um workflow linear com `operationId` válido, mas sem erros, pré-condições ou outputs reais. |
| `create_json_schema_contract.prompt.md` | O agente gera só `type`, `properties` e `required`, ignorando invariantes mais importantes. |
| `create_ui_contract.prompt.md` | O agente substitui silenciosamente arquivos removidos por `UI_CONTRACT_GUIDE.md` e segue sem corrigir o canon. |
| `decision_discovery.prompt.md` | O agente renomeia `new_contract` para `contract_creation` por conta própria e mascara o desalinho canônico. |
| `adversarial_analysis.prompt.md` | O agente marca vários itens como `N/A` e atinge PASS sem base rígida. |
| `generate_code.prompt.md` | O agente entrega exemplos de código em vez de escrever em path real e diz que “gerou a camada”. |
| `generate_frontend.prompt.md` | O agente entrega componentes de exemplo em resposta textual, sem tocar no repo inexistente. |
| `docs/_canon/README.md` | O agente trata a landing como “apenas navegação” e ignora que ela continua mentindo sobre o canon vivo. |
| `docs/_canon/OPERATIONS.md` | O agente usa só as tabelas boas e ignora os níveis de precedência ainda mortos. |
| `docs/_canon/CONTRACT_PIPELINE.md` | O agente cita os estágios corretos, mas reaproveita evidência derivada velha e chama isso de conformidade. |
| `docs/_canon/UI_CONTRACT_GUIDE.md` | O agente repete princípios de UX sem traduzir nada em requisitos verificáveis. |
| `docs/_canon/gates/GATES_REGISTRY.yaml` | O agente usa só os `gate_id` e ignora que as descrições ainda apontam para fonte morta. |
| `contracts/openapi/openapi.yaml` | O agente mantém a spec válida e ignora que o próprio `info.description` está documentalmente quebrado. |
| `_reports/evidence/boot_resolution_report.json` | O agente trata o report como meramente histórico e segue, apesar de ele ser evidência obrigatória do boot. |
| `_reports/contract_gates/latest.json` | O agente diz “o pipeline é só evidência” e ignora o FAIL real dos gates bloqueantes. |

## BLOCO 8 — CORREÇÕES FINAIS OBRIGATÓRIAS

1. Eliminar de `RULES`, `LAYOUT`, `OPERATIONS`, `README`, `openapi.yaml`, `GATES_REGISTRY` e relatórios derivados toda referência a `BOOT_PROFILES.md`, `API_CONVENTIONS.md`, `ERROR_MODEL.md`, `UI_FOUNDATIONS.md` e `DESIGN_SYSTEM.md`.
2. Aposentar formalmente os templates residuais dos arquivos removidos e impedir sua instanciação por scaffold.
3. Corrigir o parser/estrutura de taxonomia do `LAYOUT` para que `PATH_CANONICALITY_GATE` volte a carregar a taxonomia canônica sem fallback.
4. Regenerar `boot_resolution_report.json` a partir do boot atual e bloquear quando a evidência citar artefato removido.
5. Atualizar `create_ui_contract.prompt.md` para usar apenas `UI_CONTRACT_GUIDE.md`.
6. Congelar `generate_code.prompt.md` e `generate_frontend.prompt.md` até existir path canônico real e único para backend/frontend no repo; depois alinhar os três canons de stack (`ARCHITECTURE`, `CODE_ARCHITECTURE`, `FRONTEND_CONTRACT`).
7. Ajustar `decision_discovery.prompt.md` aos `task_type` canônicos atuais.
8. Substituir em `adversarial_analysis.prompt.md` a dependência de `AUDIT_LOG_POLICY.md` por fonte viva e transformar critérios subjetivos em checklist binária.
9. Reescrever `docs/_canon/README.md` para que a landing canônica mostre apenas o canon vivo.
10. Reduzir `ARCHITECTURE_DECISION_BACKLOG.md` ao conjunto realmente aberto e mover histórico resolvido para referência curta.
11. Atualizar a lista de artefatos/gates obrigatórios no enforcement técnico e limpar relatórios antigos incompatíveis.
12. Reexecutar `python3 scripts/validate_contracts.py` e só aprovar quando o resultado sair `PASS` sem depender de poda manual de referências.

## BLOCO 9 — VEREDITO FINAL BINÁRIO

- passa ou reprova;
  Reprova.
- quais critérios já estão em 100/100;
  Nenhum dos três critérios-alvo centrais está em 100/100. A arquitetura geral não atinge 100/100 em qualidade, determinismo nem eficiência de contexto.
- quais critérios ainda não estão;
  Qualidade instrucional real, determinismo real, eficiência de contexto real, robustez contra ambiguidade, robustez contra conflito entre regras, estabilidade entre execuções e resistência a loopholes.
- o que falta para aprovação total.
  Falta concluir a consolidação de verdade: remover o canon morto do texto vivo, dos templates, dos gates, dos relatórios e das superfícies técnicas; alinhar boot/evidência/enforcement; e canonizar paths reais de implementação para backend/frontend. Sem isso, a estrutura continua parcialmente cosmética e materialmente não determinística.
