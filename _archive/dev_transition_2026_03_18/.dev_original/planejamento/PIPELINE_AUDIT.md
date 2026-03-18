# PIPELINE_AUDIT — Auditoria Adversarial Pesada da Estrutura Final

Data da auditoria: 2026-03-18
Escopo efetivo: 58 referências diretas existentes extraídas de [CONTRACT_SYSTEM_RULES.md](/home/davis/HB-TRACK/.contract_driven/CONTRACT_SYSTEM_RULES.md), [CONTRACT_SYSTEM_LAYOUT.md](/home/davis/HB-TRACK/.contract_driven/CONTRACT_SYSTEM_LAYOUT.md) e [GLOBAL_TEMPLATES.md](/home/davis/HB-TRACK/.contract_driven/GLOBAL_TEMPLATES.md), consolidadas em 25 unidades auditáveis para evitar repetição mecânica sem esconder conflito estrutural.

Base empírica usada:
- `git config --get core.hooksPath` → `scripts/git-hooks`
- `scripts/git-hooks/pre-commit` continua sendo wrapper antigo; não lê `_reports/session_start.json`
- `scripts/hb verify` sem args agora falha, mas `scripts/hb verify --task-type contract_revision --module training` quebrou por incompatibilidade com `_reports/session_start.json` legado
- `scripts/hb artifact contracts/openapi/paths/training.yaml` agora retorna `exit 2`, mas grava estado novo sobre evidência antiga
- `python3 scripts/contracts/validate/validate_contracts.py --profile local` retornou `FAIL` por `CANON_ALLOWLIST_GATE`, `UI_DOC_VALIDATION_GATE` e `DERIVED_DRIFT_GATE`
- `CANON_ALLOWLIST_GATE` acusou como intrusos: `docs/_canon/BOOT_PROFILES.yaml`, `docs/_canon/TASK_CATALOG.yaml` e `docs/_canon/gates/TRAINING_MODULE_DECISION_IR.yaml`
- comparação `docs/_canon` real vs allowlist declarada em LAYOUT mostrou 40 arquivos em `_canon` não listados pela própria governança
- templates e docs citam arquivos inexistentes, entre eles `docs/_canon/API_CONVENTIONS.md`, `docs/_canon/ERROR_MODEL.md`, `docs/_canon/DESIGN_SYSTEM.md`, `docs/_canon/UI_FOUNDATIONS.md`, `contracts/README`

## BLOCO 1 — VEREDITO GERAL ADVERSARIAL

- a nova estrutura passa ou reprova? **Reprova**
- ela realmente atinge 100/100 em qualidade? **Não**
- ela realmente atinge 100/100 em determinismo? **Não**
- ela realmente atinge 100/100 em eficiência de contexto? **Não**
- se reprova, por quê?

1. A arquitetura entrou em migração parcial e ficou split-brain: `CLAUDE.md` aponta para `BOOT_PROFILES.yaml` e `TASK_CATALOG.yaml`, mas `RULES`, `PIPELINE` e `GATES_REGISTRY` ainda tratam `CLAUDE.md §7` como boot authority.
2. Os novos SSOTs foram criados em `docs/_canon/` sem autorização completa da própria allowlist. O validator já acusa esses arquivos como intrusos. Isso reprova governança e precedência.
3. O hook efetivamente ativo continua sendo o wrapper antigo em `scripts/git-hooks/pre-commit`. O enforcement por `session_start.json` não está no caminho real do commit.
4. `TASK_CATALOG.yaml` conflita com `LAYOUT`: vários `artifacts_produced` apontam para paths não-canônicos.
5. O sistema de templates está em drift real: templates globais, templates de módulo e referências auxiliares apontam para documentos que não existem mais.
6. O novo `scripts/hb` endureceu CLI, mas não resolveu migração de sessão legada, usa lista de módulos hardcoded e convive com evidência antiga incompatível.

## BLOCO 2 — SCORE ADVERSARIAL DA ARQUITETURA

| Critério | Nota | Justificativa objetiva |
|---------|------|------------------------|
| Qualidade instrucional real | 40 | Houve endurecimento local de CLI e gate allowlist, mas a malha documental e executável continua incoerente. |
| Determinismo real | 22 | Boot authority duplicada, hook ativo desatualizado, catálogo de tasks divergente e caminhos canônicos conflitantes. |
| Eficiência de contexto real | 27 | Os três arquivos raiz somam 9.012 palavras e puxam uma rede grande de referências, inclusive legados e templates quebrados. |
| Robustez contra ambiguidade | 24 | `CLAUDE §7` vs `BOOT_PROFILES.yaml`, paths relativos ambíguos e allowlist incompleta mantêm interpretação subjetiva. |
| Robustez contra respostas genéricas | 45 | Parte do sistema endureceu, mas o agente ainda encontra muito texto sem enforcement correspondente. |
| Robustez contra conflito entre regras | 18 | `RULES`, `LAYOUT`, `GLOBAL_TEMPLATES`, `CLAUDE`, `TASK_CATALOG`, `PIPELINE`, `GATES` e hook real não descrevem o mesmo pipeline. |
| Clareza de precedência | 20 | A cadeia de autoridade do boot e do routing não fecha em uma única fonte executável. |
| Acionabilidade | 47 | Há comandos e gates, mas parte relevante da operação falha por migração incompleta e docs errados. |
| Estabilidade entre execuções | 21 | O resultado muda conforme sessão legada, hook configurado, arquivo consultado e família de template usada. |
| Resistência a loopholes | 19 | Ainda é possível obedecer a uma parte do sistema e contrariar outra, com aparência superficial de conformidade. |

Nota final consolidada da arquitetura: **28/100**

## BLOCO 3 — SCORE ADVERSARIAL POR ARQUIVO

## Arquivo: CLAUDE.md

Função real:
Entrypoint permanente da sessão. Deveria apontar para os SSOTs corretos e não competir com eles.

Tabela de pontuação:
| Critério | Nota | Justificativa objetiva |
|---------|------|------------------------|
| Qualidade instrucional real | 48 | Está mais curto e aponta para SSOTs, mas ainda resume taxonomia e task map em paralelo ao catálogo novo. |
| Determinismo real | 30 | Melhorou, mas o resto da arquitetura ainda não o acompanha. |
| Eficiência de contexto real | 78 | O tamanho caiu, o que é positivo. |
| Robustez contra ambiguidade | 36 | Resume 9 tasks enquanto `TASK_CATALOG.yaml` já expande esse conjunto. |
| Robustez contra respostas genéricas | 55 | Dá um entrypoint melhor que antes. |
| Robustez contra conflito entre regras | 25 | Conflita com `RULES`, `PIPELINE` e `TASK_CATALOG`. |
| Clareza de precedência | 32 | Aponta para SSOTs novos, mas não resolve o conflito com referências antigas. |
| Acionabilidade | 55 | É prático para iniciar. |
| Estabilidade entre execuções | 34 | A estabilidade cai porque o restante do sistema ainda usa outro boot authority. |
| Resistência a loopholes | 38 | O agente pode seguir `CLAUDE` e ainda cair em docs/templates incompatíveis. |

Nota final do arquivo:
**43/100**

Veredito:
**reprovado**

Por que não é 100/100:
O entrypoint melhorou, mas não há convergência sistêmica em torno dele.

Falhas encontradas:
| Falha | Severidade | Tipo | Impacto prático | Cenário de quebra |
|-------|------------|------|-----------------|-------------------|
| Resume 9 task types enquanto `TASK_CATALOG.yaml` já contém 11 entradas | Alta | conflito | Routing muda conforme arquivo consultado | `decision_discovery` existe no catálogo, não no resumo do boot |
| Ainda mantém resumo manual de módulos/status | Média | redundância | Duplica registry e aumenta custo de sync | Mudança no registry não propaga automaticamente |

Correções obrigatórias:
1. Remover task map manual e apontar apenas para `TASK_CATALOG`.
2. Remover resumo manual de status de módulos.
3. Declarar explicitamente que `CLAUDE` é entrypoint, não SSOT de boot/routing.

## Arquivo: .contract_driven/CONTRACT_SYSTEM_RULES.md

Função real:
Norma operacional central. Deveria refletir a arquitetura vigente e não uma arquitetura anterior.

Tabela de pontuação:
| Critério | Nota | Justificativa objetiva |
|---------|------|------------------------|
| Qualidade instrucional real | 38 | Continua extenso e materialmente desatualizado em pontos críticos. |
| Determinismo real | 20 | Mantém `CLAUDE.md §7` como boot authority inexistente no uso atual. |
| Eficiência de contexto real | 12 | 4.276 palavras com muita redundância e referência legada. |
| Robustez contra ambiguidade | 22 | Mistura sistema novo e antigo. |
| Robustez contra respostas genéricas | 46 | Há regra forte, mas muito texto não vira enforcement. |
| Robustez contra conflito entre regras | 16 | Conflita com `CLAUDE`, `BOOT_PROFILES`, `TASK_CATALOG` e hook ativo. |
| Clareza de precedência | 18 | A precedência continua repartida e parcialmente fictícia. |
| Acionabilidade | 44 | Dá regras, mas muitas já não casam com a execução. |
| Estabilidade entre execuções | 20 | Dois agentes podem seguir interpretações diferentes sem sair “fora” do texto. |
| Resistência a loopholes | 22 | O agente pode escolher o ramo documental que mais convém. |

Nota final do arquivo:
**26/100**

Veredito:
**reprovado**

Por que não é 100/100:
O documento ainda regula um sistema que já mudou sem ele.

Falhas encontradas:
| Falha | Severidade | Tipo | Impacto prático | Cenário de quebra |
|-------|------------|------|-----------------|-------------------|
| Continua mandando classificar boot em `CLAUDE.md §7` | Crítica | precedência | O SSOT vigente e a norma divergem | O agente segue `BOOT_PROFILES`, a norma continua exigindo outra coisa |
| Trata `api_rules.yaml` como SSOT, mas a cadeia de templates e docs de API continua apontando para arquivos inexistentes | Alta | conflito | O subsistema de API fica meio migrado, meio legado | O agente consulta guia auxiliar quebrado e polui decisão |

Correções obrigatórias:
1. Trocar toda referência de boot para o arquivo único correto.
2. Reconciliar task routing com `TASK_CATALOG`.
3. Remover referências legadas já substituídas.

## Arquivo: .contract_driven/CONTRACT_SYSTEM_LAYOUT.md

Função real:
Define paths canônicos e localização dos artefatos. Deveria ser o desempate definitivo de “onde cada coisa mora”.

Tabela de pontuação:
| Critério | Nota | Justificativa objetiva |
|---------|------|------------------------|
| Qualidade instrucional real | 42 | O layout existe, mas já não cobre o filesystem real. |
| Determinismo real | 24 | O próprio `_canon` atual contém 40 arquivos fora da lista descrita aqui. |
| Eficiência de contexto real | 18 | 1.967 palavras com árvore longa e allowlist desatualizada. |
| Robustez contra ambiguidade | 30 | Paths canônicos e paths efetivamente usados já divergem. |
| Robustez contra respostas genéricas | 48 | Restringe bastante o “onde”, mas não o suficiente para impedir deriva. |
| Robustez contra conflito entre regras | 20 | Conflita com `TASK_CATALOG`, `BOOT_PROFILES` e `_canon` real. |
| Clareza de precedência | 26 | É claro no papel, fraco na aderência ao repo atual. |
| Acionabilidade | 46 | Útil como mapa, ruim como verdade operacional. |
| Estabilidade entre execuções | 24 | Cada novo arquivo em `_canon` aumenta drift. |
| Resistência a loopholes | 25 | O agente pode criar algo fora da allowlist e só descobrir depois. |

Nota final do arquivo:
**30/100**

Veredito:
**reprovado**

Por que não é 100/100:
O layout não reflete o estado real do repositório nem o pipeline novo.

Falhas encontradas:
| Falha | Severidade | Tipo | Impacto prático | Cenário de quebra |
|-------|------------|------|-----------------|-------------------|
| Não lista `BOOT_PROFILES.yaml`, `TASK_CATALOG.yaml` e dezenas de arquivos hoje existentes em `_canon` | Crítica | completude | O próprio repo viola a allowlist declarada | `CANON_ALLOWLIST_GATE` falha no estado atual |
| Continua marcando `_reports/agent_execution/latest.json` e `_reports/evidence/boot_resolution_report.json` como derivados operantes | Alta | conflito | Mantém vivo o modelo legado | O sistema continua parecendo dual |

Correções obrigatórias:
1. Atualizar a allowlist ou mover os arquivos intrusos para fora de `_canon`.
2. Remover o legado `_reports/*` do layout ativo.
3. Reconciliar paths canônicos com `TASK_CATALOG`.

## Arquivo: .contract_driven/GLOBAL_TEMPLATES.md

Função real:
Índice e política de scaffolds. Deveria ser ponte enxuta para templates válidos, não mais uma camada de drift.

Tabela de pontuação:
| Critério | Nota | Justificativa objetiva |
|---------|------|------------------------|
| Qualidade instrucional real | 34 | O arquivo virou índice grande, mas ainda carrega referências e premissas velhas. |
| Determinismo real | 18 | Diz que a trilogia deve ser lida em conjunto e herda conflitos dos outros dois arquivos. |
| Eficiência de contexto real | 15 | 2.769 palavras de índice para templates é custo alto. |
| Robustez contra ambiguidade | 23 | O índice aponta para templates e docs que não existem. |
| Robustez contra respostas genéricas | 40 | Ajuda a encontrar scaffolds, mas com base já contaminada. |
| Robustez contra conflito entre regras | 18 | Conflita com o estado real dos templates e do `_canon`. |
| Clareza de precedência | 24 | Não está claro o que é índice vs regra ativa. |
| Acionabilidade | 38 | O agente encontra caminhos, mas vários estão errados. |
| Estabilidade entre execuções | 18 | Drift alto entre índice, templates e canon real. |
| Resistência a loopholes | 20 | O agente pode seguir o índice e criar artefato em estrutura não válida. |

Nota final do arquivo:
**25/100**

Veredito:
**reprovado**

Por que não é 100/100:
O índice já não indexa um conjunto coerente.

Falhas encontradas:
| Falha | Severidade | Tipo | Impacto prático | Cenário de quebra |
|-------|------------|------|-----------------|-------------------|
| Continua mandando ler “em conjunto” os três arquivos raiz | Alta | contexto | Pressiona contexto permanente logo na entrada | O agente carrega 9.012 palavras antes de decidir algo útil |
| Referencia destinos inexistentes como `contracts/README` e ADR template em `_canon` ausente | Alta | completude | O índice manda instanciar para lugares que não existem | O agente cria arquivo errado ou bloqueia no meio |

Correções obrigatórias:
1. Reduzir o arquivo a índice mínimo e regras de instância.
2. Corrigir ou remover todos os destinos inexistentes.
3. Parar de prescrever leitura conjunta permanente.

## Arquivo: docs/_canon/README.md

Função real:
Allowlist e mapa soberano do canon global. Deveria ser a fonte que o `CANON_ALLOWLIST_GATE` consegue defender sem falsos negativos/positivos.

Tabela de pontuação:
| Critério | Nota | Justificativa objetiva |
|---------|------|------------------------|
| Qualidade instrucional real | 40 | Está melhor que templates antigos, mas já diverge do `_canon` real e do hook real. |
| Determinismo real | 24 | A allowlist não cobre a estrutura vigente. |
| Eficiência de contexto real | 42 | Relativamente enxuto. |
| Robustez contra ambiguidade | 28 | Mistura orientação de leitura, allowlist e comandos. |
| Robustez contra respostas genéricas | 50 | Ajuda navegação, mas não fecha canonicidade. |
| Robustez contra conflito entre regras | 24 | Conflita com LAYOUT, com `_canon` real e com `scripts/git-hooks/pre-commit`. |
| Clareza de precedência | 28 | O README quer ser allowlist e guia; a governança real ficou fora dele. |
| Acionabilidade | 46 | O mapa é usável, mas incompleto. |
| Estabilidade entre execuções | 22 | Qualquer novo arquivo em `_canon` amplia drift. |
| Resistência a loopholes | 20 | Intrusos podem entrar antes de a documentação ser atualizada. |

Nota final do arquivo:
**32/100**

Veredito:
**reprovado**

Por que não é 100/100:
O `README` não é mais capaz de sustentar a allowlist que o gate presume.

Falhas encontradas:
| Falha | Severidade | Tipo | Impacto prático | Cenário de quebra |
|-------|------------|------|-----------------|-------------------|
| Não lista `BOOT_PROFILES.yaml` e `TASK_CATALOG.yaml`, apesar de o sistema já apontar para ambos | Crítica | conflito | O allowlist gate reprova o próprio SSOT novo | O repo entra em FAIL estrutural |
| Aponta `scripts/validate_contracts.py` como “contract gates”, enquanto o fluxo real usa `scripts/contracts/validate/validate_contracts.py` + `scripts/hb` | Alta | precedência | O manual de navegação já nasce desatualizado | O agente segue o comando errado |

Correções obrigatórias:
1. Reconciliar o inventário com o `_canon` real.
2. Corrigir o entrypoint técnico dos contract gates.
3. Separar allowlist de guia de leitura, se necessário.

## Arquivo: docs/_canon/OPERATIONS.md

Função real:
Resumo operacional. Deveria condensar sem duplicar nem conflitar.

Tabela de pontuação:
| Critério | Nota | Justificativa objetiva |
|---------|------|------------------------|
| Qualidade instrucional real | 50 | Continua útil como resumo, mas não reflete integralmente a nova migração. |
| Determinismo real | 30 | Herda precedência duplicada e paths que já divergem do resto. |
| Eficiência de contexto real | 40 | É menor que `RULES`, mas soma em vez de substituir. |
| Robustez contra ambiguidade | 28 | Ainda carrega precedência ambígua. |
| Robustez contra respostas genéricas | 58 | Ajuda consulta rápida. |
| Robustez contra conflito entre regras | 24 | Continua conflitando com `RULES` e LAYOUT em pontos de precedência. |
| Clareza de precedência | 24 | O mesmo SSOT aparece em mais de um nível. |
| Acionabilidade | 60 | Útil no dia a dia. |
| Estabilidade entre execuções | 30 | Cai quando os SSOTs mudam e o resumo não acompanha. |
| Resistência a loopholes | 30 | O agente consegue citar o resumo sem resolver conflitos subjacentes. |

Nota final do arquivo:
**37/100**

Veredito:
**reprovado**

Por que não é 100/100:
O resumo local continua bom, mas o sistema que ele resume continua quebrado.

Falhas encontradas:
| Falha | Severidade | Tipo | Impacto prático | Cenário de quebra |
|-------|------------|------|-----------------|-------------------|
| Mantém precedência ainda não reconciliada | Alta | precedência | O resumo reforça conflito em vez de resolvê-lo | O agente encontra respostas diferentes entre resumo e norma |
| Não absorve totalmente os SSOTs novos | Média | completude | O resumo já nasce atrás da migração | O agente precisa reabrir múltiplos arquivos longos |

Correções obrigatórias:
1. Reconciliar a tabela de precedência.
2. Atualizar o resumo para os SSOTs atuais.
3. Remover conteúdo que já mora de forma mais precisa em outros artefatos.

## Arquivo: docs/_canon/CONTRACT_PIPELINE.md

Função real:
Registro operacional do pipeline. Deveria casar o comportamento do agente com o comportamento executável.

Tabela de pontuação:
| Critério | Nota | Justificativa objetiva |
|---------|------|------------------------|
| Qualidade instrucional real | 32 | Ficou curto, mas ainda registra uma arquitetura antiga em pontos críticos. |
| Determinismo real | 16 | Continua citando `CLAUDE.md §7` como boot authority. |
| Eficiência de contexto real | 50 | Curto, mas parte do texto já está errado. |
| Robustez contra ambiguidade | 18 | Pipeline novo e autoridade velha convivem. |
| Robustez contra respostas genéricas | 36 | O agente ainda precisa interpretar demais. |
| Robustez contra conflito entre regras | 14 | Conflita com `BOOT_PROFILES`, `TASK_CATALOG` e hook ativo. |
| Clareza de precedência | 12 | A regra de alteração do fluxo ainda manda atualizar `CLAUDE.md §7`. |
| Acionabilidade | 36 | O nome dos estágios existe, o enforcement real não bate. |
| Estabilidade entre execuções | 14 | A instabilidade vem da fonte de boot errada e do hook antigo. |
| Resistência a loopholes | 18 | O texto de pipeline parece novo, a cadeia de enforcement não. |

Nota final do arquivo:
**25/100**

Veredito:
**reprovado**

Por que não é 100/100:
O registro operacional já ficou para trás em relação à migração em curso.

Falhas encontradas:
| Falha | Severidade | Tipo | Impacto prático | Cenário de quebra |
|-------|------------|------|-----------------|-------------------|
| Continua exigindo atualização em `CLAUDE.md §7` | Crítica | precedência | A cadeia de promoção continua apontando para SSOT errado | A mudança “oficial” nasce inconsistente |
| Não descreve o hook efetivamente ativo em `scripts/git-hooks/pre-commit` | Alta | conflito | O usuário acredita em um enforcement que não está no commit path | O commit segue wrapper antigo |

Correções obrigatórias:
1. Trocar o boot authority pelo SSOT real.
2. Reescrever o pipeline em torno do hook efetivo.
3. Remover qualquer referência operacional já substituída.

## Arquivo: docs/_canon/BOOT_PROFILES.yaml

Função real:
Novo SSOT de boot. Deveria ser machine-readable, autorizado, integrado e sem ambiguidade de path.

Tabela de pontuação:
| Critério | Nota | Justificativa objetiva |
|---------|------|------------------------|
| Qualidade instrucional real | 30 | A intenção é correta, a implantação é fraca. |
| Determinismo real | 12 | Paths relativos mistos e integração incompleta quebram o valor do SSOT. |
| Eficiência de contexto real | 40 | É compacto. |
| Robustez contra ambiguidade | 14 | `./CLAUDE.md`, `./OPERATIONS.md` e `./README.md` têm semântica de resolução ambígua. |
| Robustez contra respostas genéricas | 30 | Poderia reduzir improviso, mas ainda não está acoplado ao resto. |
| Robustez contra conflito entre regras | 12 | Entra em conflito com `RULES`, `PIPELINE`, `GATES_REGISTRY` e `CANON_ALLOWLIST_GATE`. |
| Clareza de precedência | 10 | Nasce como SSOT sem ter sido promovido corretamente pela cadeia normativa. |
| Acionabilidade | 26 | `scripts/hb` o lê, mas o ecossistema documental não reconhece isso. |
| Estabilidade entre execuções | 12 | A própria sessão atual falha por incompatibilidade com o estado anterior. |
| Resistência a loopholes | 16 | Um SSOT não autorizado vira mais uma camada concorrente. |

Nota final do arquivo:
**20/100**

Veredito:
**reprovado**

Por que não é 100/100:
O arquivo foi criado antes de a governança e o allowlist aceitarem sua existência.

Falhas encontradas:
| Falha | Severidade | Tipo | Impacto prático | Cenário de quebra |
|-------|------------|------|-----------------|-------------------|
| É tratado como SSOT, mas `CANON_ALLOWLIST_GATE` o reprova como intruso | Crítica | conflito | O sistema invalida a própria fonte nova | O profile de boot existe e ao mesmo tempo não pode existir |
| Usa `load_sequence` com paths relativos inconsistentes | Alta | ambiguidade | O agente precisa inferir base path | `./CLAUDE.md` pode ser resolvido errado por consumidor futuro |

Correções obrigatórias:
1. Tirar o arquivo de `_canon` ou atualizar allowlist e LAYOUT antes de mantê-lo lá.
2. Padronizar todos os paths como repo-relative absolutos lógicos.
3. Atualizar toda a cadeia normativa para reconhecê-lo.

## Arquivo: docs/_canon/TASK_CATALOG.yaml

Função real:
Novo SSOT de task routing. Deveria unificar workers, status e artefatos produzidos.

Tabela de pontuação:
| Critério | Nota | Justificativa objetiva |
|---------|------|------------------------|
| Qualidade instrucional real | 26 | A ideia é boa, mas o catálogo contém paths incompatíveis com o layout canônico. |
| Determinismo real | 10 | Um SSOT de task que manda escrever no lugar errado piora o sistema. |
| Eficiência de contexto real | 36 | É relativamente compacto. |
| Robustez contra ambiguidade | 12 | Mistura novos e velhos padrões de path. |
| Robustez contra respostas genéricas | 28 | Congelamento explícito ajuda, mas os outputs conflitantes prejudicam. |
| Robustez contra conflito entre regras | 8 | Conflita com `CLAUDE`, `LAYOUT` e nomes canônicos de docs de módulo. |
| Clareza de precedência | 10 | Não está claro se ele substitui ou apenas complementa o mapa de `CLAUDE`. |
| Acionabilidade | 24 | O agente poderia segui-lo e escrever artefatos em paths inválidos. |
| Estabilidade entre execuções | 10 | Cada worker pode produzir algo diferente do canon atual. |
| Resistência a loopholes | 12 | O agente pode cumprir o catálogo e ainda violar o layout oficial. |

Nota final do arquivo:
**18/100**

Veredito:
**reprovado**

Por que não é 100/100:
Um catálogo de tarefas com outputs errados é falha estrutural, não detalhe.

Falhas encontradas:
| Falha | Severidade | Tipo | Impacto prático | Cenário de quebra |
|-------|------------|------|-----------------|-------------------|
| `new_contract` aponta para `contracts/openapi/paths/{module}/{resource}.yaml`, mas o LAYOUT canônico é `contracts/openapi/paths/<module>.yaml` | Crítica | conflito | O SSOT de routing manda escrever no path errado | O agente cria `paths/training/session.yaml` e viola path canonicality |
| `new_state_model` e `new_ui_contract` usam nomes por screen/model, não `STATE_MODEL_<MODULE>.md` e `UI_CONTRACT_<MODULE>.md` | Crítica | precedência | O catálogo quebra naming canônico de docs de módulo | Dois agentes produzem arquivos diferentes para o mesmo módulo |

Correções obrigatórias:
1. Reconciliar todos os `artifacts_produced` com o LAYOUT real.
2. Declarar explicitamente a relação do catálogo com `CLAUDE.md`.
3. Tirar o arquivo de `_canon` ou atualizar a governança antes de mantê-lo ali.

## Arquivo: docs/_canon/gates/GATES_REGISTRY.yaml

Função real:
Registry de metadata dos gates. Deveria casar com a execução e com a cadeia de autoridade vigente.

Tabela de pontuação:
| Critério | Nota | Justificativa objetiva |
|---------|------|------------------------|
| Qualidade instrucional real | 32 | Tem estrutura útil, mas continua registrando a autoridade de boot errada. |
| Determinismo real | 18 | O gate allowlist já revela a incoerência da própria governança. |
| Eficiência de contexto real | 34 | O registry é grande e parcialmente desatualizado. |
| Robustez contra ambiguidade | 22 | Mantém `boot_profiles_ref: CLAUDE.md §7`. |
| Robustez contra respostas genéricas | 42 | Como machine-readable, ajuda mais que docs prose. |
| Robustez contra conflito entre regras | 18 | Conflita com `BOOT_PROFILES` e com o estado do `_canon`. |
| Clareza de precedência | 18 | A referência fundacional de boot está errada. |
| Acionabilidade | 34 | O validator o usa parcialmente, mas a governança maior não fecha. |
| Estabilidade entre execuções | 20 | A cada novo arquivo intruso o registry e o allowlist entram em tensão. |
| Resistência a loopholes | 18 | O agent pode citar o registry e ignorar a cadeia real do hook. |

Nota final do arquivo:
**26/100**

Veredito:
**reprovado**

Por que não é 100/100:
Registry bom com autoridade errada continua ruim.

Falhas encontradas:
| Falha | Severidade | Tipo | Impacto prático | Cenário de quebra |
|-------|------------|------|-----------------|-------------------|
| `boot_profiles_ref` continua apontando para `CLAUDE.md §7` | Crítica | precedência | O registry centraliza o erro de boot authority | A camada machine-readable reforça referência falsa |
| `CANON_ALLOWLIST_GATE` já falha no estado atual do repo | Crítica | conflito | O sistema se auto-reprova por composição | O pipeline local falha antes mesmo da intenção do usuário |

Correções obrigatórias:
1. Corrigir `boot_profiles_ref`.
2. Reconciliar a allowlist com a estrutura autorizada.
3. Revalidar o registry após mover intrusos ou expandir o canon formalmente.

## Arquivo: docs/_canon/arquivos extras fora da allowlist declarada (família)

Função real:
Conjunto de arquivos hoje presentes em `_canon` sem cobertura completa do LAYOUT/allowlist, incluindo `BOOT_PROFILES.yaml`, `TASK_CATALOG.yaml` e outros 37 artefatos.

Tabela de pontuação:
| Critério | Nota | Justificativa objetiva |
|---------|------|------------------------|
| Qualidade instrucional real | 12 | Como família, já evidencia drift estrutural. |
| Determinismo real | 6 | Arquivo fora da allowlist em diretório soberano é falha objetiva. |
| Eficiência de contexto real | 20 | Cada intruso aumenta carga e revisão manual. |
| Robustez contra ambiguidade | 8 | Não está claro o que é canônico vs apenas presente. |
| Robustez contra respostas genéricas | 18 | Intrusos viram atalho fácil para o agente inventar autoridade. |
| Robustez contra conflito entre regras | 4 | Conflitam com LAYOUT, README e allowlist gate. |
| Clareza de precedência | 6 | A pasta soberana deixa de ser soberana. |
| Acionabilidade | 10 | O agente não sabe se deve ler, ignorar ou mover. |
| Estabilidade entre execuções | 6 | Mudanças locais em `_canon` alteram o sistema sem promoção completa. |
| Resistência a loopholes | 6 | Basta criar documento em `_canon` para sugerir autoridade indevida. |

Nota final do arquivo:
**10/100**

Veredito:
**reprovado**

Por que não é 100/100:
É o sintoma mais direto de governança rompida.

Falhas encontradas:
| Falha | Severidade | Tipo | Impacto prático | Cenário de quebra |
|-------|------------|------|-----------------|-------------------|
| Há 40 arquivos em `_canon` não listados pela própria allowlist de LAYOUT | Crítica | completude | A pasta soberana deixou de ter perímetro controlado | O agente cria ou consome “canon” onde quiser |
| `TRAINING_MODULE_DECISION_IR.yaml` vive em `docs/_canon/gates/` sem pertencer à allowlist dessa pasta | Crítica | precedência | Mistura artefato de módulo com registry de gates | O diretório de gates perde identidade |

Correções obrigatórias:
1. Mover os intrusos para o domínio correto ou atualizar formalmente a allowlist.
2. Bloquear criação de novos arquivos em `_canon` sem promoção completa.
3. Auditar subdiretórios `gates`, `templates`, `security` separadamente.

## Arquivo: .contract_driven/templates/api/api_rules.yaml

Função real:
SSOT de convenções, validações e templates de API HTTP/OpenAPI.

Tabela de pontuação:
| Critério | Nota | Justificativa objetiva |
|---------|------|------------------------|
| Qualidade instrucional real | 58 | É o arquivo mais forte do subsistema de API. |
| Determinismo real | 40 | Define regras explícitas, mas convive com referências auxiliares quebradas. |
| Eficiência de contexto real | 16 | 3.795 palavras para um único SSOT são caras. |
| Robustez contra ambiguidade | 28 | Ainda referencia `docs/_canon/ERROR_MODEL.md`, que não existe. |
| Robustez contra respostas genéricas | 66 | Reduz improviso de API melhor que a maioria dos arquivos. |
| Robustez contra conflito entre regras | 22 | Auxiliares de API e docs globais antigas continuam em drift. |
| Clareza de precedência | 44 | A precedência interna é relativamente explícita. |
| Acionabilidade | 62 | Dá protocolos e convenções aplicáveis. |
| Estabilidade entre execuções | 32 | A estabilidade cai porque o ecossistema ao redor está quebrado. |
| Resistência a loopholes | 30 | O agente ainda pode usar guias auxiliares obsoletos em vez do SSOT puro. |

Nota final do arquivo:
**40/100**

Veredito:
**reprovado**

Por que não é 100/100:
O SSOT de API é forte, mas ainda está cercado por referências e templates auxiliares ruins.

Falhas encontradas:
| Falha | Severidade | Tipo | Impacto prático | Cenário de quebra |
|-------|------------|------|-----------------|-------------------|
| Referencia `docs/_canon/ERROR_MODEL.md`, que não existe | Alta | completude | O ecossistema de erros fica sem âncora auxiliar válida | Template de erro aponta para artefato ausente |
| O custo de contexto é alto para uso humano/agent sem extração programática | Média | contexto | O agente tende a pular seções ou improvisar | Uso parcial do SSOT enfraquece determinismo |

Correções obrigatórias:
1. Remover referências a docs inexistentes.
2. Extrair views menores geradas a partir deste SSOT, sem duplicar norma.
3. Deprecar oficialmente os auxiliares de API que não estejam alinhados.

## Arquivo: .contract_driven/templates/api/*.md (família de referência externa)

Função real:
Guias auxiliares de referência externa para API. Não deveriam competir com o SSOT e nem apontar para docs quebrados.

Tabela de pontuação:
| Critério | Nota | Justificativa objetiva |
|---------|------|------------------------|
| Qualidade instrucional real | 24 | Como apoio externo, são aceitáveis; como parte ativa do sistema, estão em drift. |
| Determinismo real | 12 | Referenciam docs inexistentes e artefatos auxiliares ausentes. |
| Eficiência de contexto real | 18 | Aumentam contexto sem fechamento canônico. |
| Robustez contra ambiguidade | 14 | O agente pode tratá-los como SSOT indireto. |
| Robustez contra respostas genéricas | 28 | Ajudam benchmark, mas pioram quando parecem normativos. |
| Robustez contra conflito entre regras | 12 | Conflitam com `api_rules.yaml` e com o canon atual. |
| Clareza de precedência | 16 | Não está suficientemente claro que são apoio e não norma. |
| Acionabilidade | 24 | Servem como consulta, não como base operativa estável. |
| Estabilidade entre execuções | 12 | Drift alto. |
| Resistência a loopholes | 14 | O agente pode citar o auxiliar e pular o SSOT. |

Nota final do arquivo:
**18/100**

Veredito:
**reprovado**

Por que não é 100/100:
A família auxiliar não está isolada do caminho crítico.

Falhas encontradas:
| Falha | Severidade | Tipo | Impacto prático | Cenário de quebra |
|-------|------------|------|-----------------|-------------------|
| `AddidasAPI.md` aponta para `docs/_canon/API_CONVENTIONS.md` inexistente | Alta | completude | Guia auxiliar reintroduz artefato morto | O agente acredita que há um canon adicional |
| `REGRAS_API.md` aponta para rulesets e arquivos ausentes | Crítica | manutenção | A família contém ruído morto dentro do sistema | O agente tenta seguir um baseline que não existe |

Correções obrigatórias:
1. Remover do caminho crítico todos os auxiliares não alinhados.
2. Corrigir ou arquivar os arquivos com referências quebradas.
3. Declarar explicitamente que estes arquivos são apoio externo e não SSOT.

## Arquivo: .contract_driven/templates/globais/*.md (família)

Função real:
Scaffolds para docs globais em `_canon`. Deveriam refletir o canon atual sem ressuscitar arquivos mortos.

Tabela de pontuação:
| Critério | Nota | Justificativa objetiva |
|---------|------|------------------------|
| Qualidade instrucional real | 28 | Alguns templates úteis, mas vários espelham uma arquitetura antiga. |
| Determinismo real | 14 | A família manda instanciar arquivos que não existem mais. |
| Eficiência de contexto real | 20 | Cada template velho aumenta ruído e revisão manual. |
| Robustez contra ambiguidade | 18 | `README` global de template lista `API_CONVENTIONS`, `ERROR_MODEL`, `UI_FOUNDATIONS`, `DESIGN_SYSTEM`. |
| Robustez contra respostas genéricas | 34 | Como scaffold, padroniza estrutura local. |
| Robustez contra conflito entre regras | 16 | Conflita com o `_canon` vigente. |
| Clareza de precedência | 20 | O template parece oficial mesmo quando o destino já não existe. |
| Acionabilidade | 26 | O agente consegue copiar template errado de forma muito eficiente. |
| Estabilidade entre execuções | 18 | Drift alto entre template e destino real. |
| Resistência a loopholes | 16 | Obediência literal ao template gera canon errado. |

Nota final do arquivo:
**21/100**

Veredito:
**reprovado**

Por que não é 100/100:
Scaffold desatualizado é multiplicador de erro.

Falhas encontradas:
| Falha | Severidade | Tipo | Impacto prático | Cenário de quebra |
|-------|------------|------|-----------------|-------------------|
| `templates/globais/README.md` manda ler e listar documentos inexistentes | Crítica | conflito | O template global reintroduz docs mortos dentro do `_canon` | Novo README nasce errado por cópia oficial |
| A família ainda fala em artefatos superados como `API_CONVENTIONS.md` | Alta | manutenção | A cada nova instância o legado volta | O agente recria o passado inválido |

Correções obrigatórias:
1. Sincronizar todos os templates globais com o `_canon` vigente.
2. Remover destinos inexistentes da família.
3. Gerar templates a partir do canon atual sempre que possível.

## Arquivo: .contract_driven/templates/modulos/*.md (família)

Função real:
Scaffolds de docs por módulo. Deveriam reforçar naming, headers e cross-refs corretos.

Tabela de pontuação:
| Critério | Nota | Justificativa objetiva |
|---------|------|------------------------|
| Qualidade instrucional real | 42 | A família é mais sólida que a global. |
| Determinismo real | 28 | Alguns templates ainda contêm refs quebradas e um ADR específico demais. |
| Eficiência de contexto real | 34 | O custo é aceitável, mas há redundância entre arquivos. |
| Robustez contra ambiguidade | 30 | Em geral os headers ajudam, mas há campos que dependem de artefatos inexistentes. |
| Robustez contra respostas genéricas | 52 | Bons scaffolds reduzem improviso de módulo. |
| Robustez contra conflito entre regras | 28 | `ERRORS` e `STATE_MODEL` ainda conflitam com o canon atual. |
| Clareza de precedência | 38 | A família é relativamente clara no papel. |
| Acionabilidade | 48 | É fácil instanciar corretamente em parte dos casos. |
| Estabilidade entre execuções | 28 | Cai quando refs de apoio inexistentes entram no header. |
| Resistência a loopholes | 30 | O agente ainda pode preencher scaffold “certo” com destino de apoio errado. |

Nota final do arquivo:
**36/100**

Veredito:
**reprovado**

Por que não é 100/100:
É a família de template menos ruim, mas continua carregando dependências quebradas.

Falhas encontradas:
| Falha | Severidade | Tipo | Impacto prático | Cenário de quebra |
|-------|------------|------|-----------------|-------------------|
| `ERRORS_{{MODULE}}.md` aponta para `docs/_canon/ERROR_MODEL.md` inexistente | Alta | completude | O template não tem âncora real de modelo de erro | O documento já nasce quebrado |
| `STATE_MODEL_{{MODULE}}.md` contém `adr_ref` fixo para ADR de `training` | Alta | ambiguidade | Template genérico carrega acoplamento indevido a um módulo específico | Um módulo não-training herda referência indevida |

Correções obrigatórias:
1. Corrigir refs quebradas dentro da família.
2. Remover o acoplamento específico de `training` dos templates genéricos.
3. Revalidar a família contra `MODULE_DOC_HEADER_POLICY.yaml`.

## Arquivo: .contract_driven/templates/modulos/snippets/module_human_docs_header.yaml

Função real:
Snippet mínimo de front matter para docs de módulo.

Tabela de pontuação:
| Critério | Nota | Justificativa objetiva |
|---------|------|------------------------|
| Qualidade instrucional real | 52 | O snippet é pequeno e útil. |
| Determinismo real | 38 | Paths relativos são claros o bastante no contexto de módulo. |
| Eficiência de contexto real | 80 | Muito enxuto. |
| Robustez contra ambiguidade | 42 | Ajuda a padronizar. |
| Robustez contra respostas genéricas | 56 | Obriga cross-refs mínimos. |
| Robustez contra conflito entre regras | 34 | Cai quando o resto da família está desatualizado. |
| Clareza de precedência | 48 | O papel é claro. |
| Acionabilidade | 64 | Fácil de aplicar. |
| Estabilidade entre execuções | 40 | Depende do policy e dos destinos reais existirem. |
| Resistência a loopholes | 44 | Bom para reduzir omissão de header. |

Nota final do arquivo:
**50/100**

Veredito:
**reprovado**

Por que não é 100/100:
O snippet é bom localmente, mas vive dentro de uma família em drift.

Falhas encontradas:
| Falha | Severidade | Tipo | Impacto prático | Cenário de quebra |
|-------|------------|------|-----------------|-------------------|
| Não carrega sozinho a semântica dos campos que outras templates exigem | Média | completude | Header mínimo não garante documento válido | O agente usa snippet isolado e esquece campos do tipo específico |
| Continua dependente de paths cujo ecossistema maior ainda está instável | Média | contexto | O benefício local não corrige a malha geral | Cross-ref correto aponta para canon ainda conflituoso |

Correções obrigatórias:
1. Mantê-lo sincronizado com o policy.
2. Usá-lo apenas via templates validados.
3. Testar automaticamente os headers gerados.

## Arquivo: .contract_driven/templates/modulos/MODULE_DOC_HEADER_POLICY.yaml

Função real:
Policy machine-readable dos headers de docs de módulo.

Tabela de pontuação:
| Critério | Nota | Justificativa objetiva |
|---------|------|------------------------|
| Qualidade instrucional real | 54 | É um bom passo para determinismo de headers. |
| Determinismo real | 44 | Estrutura clara, mas depende de templates ainda em drift. |
| Eficiência de contexto real | 76 | Curto e específico. |
| Robustez contra ambiguidade | 48 | Boa definição de campos obrigatórios por tipo. |
| Robustez contra respostas genéricas | 60 | Reduz improviso em front matter. |
| Robustez contra conflito entre regras | 38 | Sofre com refs quebradas exigidas indiretamente. |
| Clareza de precedência | 52 | O papel é claro. |
| Acionabilidade | 62 | Bom insumo para validator. |
| Estabilidade entre execuções | 42 | Cai porque família/tipos ainda não fecham. |
| Resistência a loopholes | 48 | Melhor que a média. |

Nota final do arquivo:
**52/100**

Veredito:
**reprovado**

Por que não é 100/100:
O policy é bom, mas não compensa templates e destinos quebrados.

Falhas encontradas:
| Falha | Severidade | Tipo | Impacto prático | Cenário de quebra |
|-------|------------|------|-----------------|-------------------|
| Exige campos que ainda apontam para artefatos inexistentes em alguns templates | Alta | conflito | Header formalmente correto pode continuar semanticamente inválido | `ERRORS` exige modelo de erro inexistente |
| Não está explicitamente conectado ao fluxo de geração de templates | Média | manutenção | Pode ficar sincronizado sozinho e o resto não | Template e policy divergem sem alarme precoce |

Correções obrigatórias:
1. Sincronizar policy e templates em uma única bateria de testes.
2. Corrigir os destinos referenciados pela família.
3. Tornar o policy fonte única para validação e geração.

## Arquivo: .contract_driven/templates/README.md

Função real:
README de uso da pasta de templates.

Tabela de pontuação:
| Critério | Nota | Justificativa objetiva |
|---------|------|------------------------|
| Qualidade instrucional real | 42 | É simples e relativamente correto. |
| Determinismo real | 30 | Descreve bem a pasta, mas não fala do drift real das famílias. |
| Eficiência de contexto real | 82 | Curto. |
| Robustez contra ambiguidade | 36 | Bom como guia local. |
| Robustez contra respostas genéricas | 44 | Ajuda a instanciar. |
| Robustez contra conflito entre regras | 28 | Depende de famílias já desatualizadas. |
| Clareza de precedência | 40 | O papel do README é claro. |
| Acionabilidade | 52 | Útil para operação de template. |
| Estabilidade entre execuções | 28 | O problema é a pasta que ele descreve. |
| Resistência a loopholes | 34 | O README não impede o agente de usar template velho. |

Nota final do arquivo:
**42/100**

Veredito:
**reprovado**

Por que não é 100/100:
É um bom README de uma pasta que ainda não está saneada.

Falhas encontradas:
| Falha | Severidade | Tipo | Impacto prático | Cenário de quebra |
|-------|------------|------|-----------------|-------------------|
| Não alerta sobre templates e refs quebrados ativos | Média | completude | O guia passa sensação de consistência inexistente | O agente usa a pasta como se estivesse limpa |
| Não aponta para testes/validador de integridade de template | Média | manutenção | Drift de template entra fácil | Mudanças em família passam sem alarme |

Correções obrigatórias:
1. Declarar a política de validação de templates.
2. Referenciar apenas famílias e destinos válidos.
3. Incluir instrução de testes de integridade da pasta.

## Arquivo: .contract_driven/agent_prompts/pre_contract_orchestrator.prompt.md

Função real:
Entry point operacional. Deveria refletir o pipeline e o catálogo vigentes.

Tabela de pontuação:
| Critério | Nota | Justificativa objetiva |
|---------|------|------------------------|
| Qualidade instrucional real | 48 | Está curto, o que é bom, mas ainda fala em 9 tasks fixas via CLAUDE. |
| Determinismo real | 32 | Melhorou por simplificação, porém não usa o `TASK_CATALOG` novo. |
| Eficiência de contexto real | 78 | Bem mais leve que versões anteriores. |
| Robustez contra ambiguidade | 36 | Continua dependente de `CLAUDE` para task routing. |
| Robustez contra respostas genéricas | 52 | O fluxo base é claro. |
| Robustez contra conflito entre regras | 28 | Conflita com o catálogo novo e com o boot novo. |
| Clareza de precedência | 38 | É operacional, mas ainda não chama os SSOTs corretos. |
| Acionabilidade | 60 | Dá um ritual simples. |
| Estabilidade entre execuções | 30 | Varia conforme o task routing consultado. |
| Resistência a loopholes | 32 | O agente pode seguir o prompt e ainda ignorar o catálogo real. |

Nota final do arquivo:
**44/100**

Veredito:
**reprovado**

Por que não é 100/100:
O prompt ficou mais leve, não mais sincronizado.

Falhas encontradas:
| Falha | Severidade | Tipo | Impacto prático | Cenário de quebra |
|-------|------------|------|-----------------|-------------------|
| Continua definindo entrada esperada como “9 tipos” via `CLAUDE.md §4` | Alta | conflito | O routing operacional ignora `TASK_CATALOG` | `decision_discovery` permanece fora do entrypoint |
| Publica `_reports/session_start.json`, mas o hook real não o usa | Crítica | determinismo | A evidência produzida não fecha o commit path | O agente cumpre o prompt sem proteção no pre-commit |

Correções obrigatórias:
1. Passar a usar `TASK_CATALOG` e `BOOT_PROFILES`.
2. Alinhar o prompt ao hook real.
3. Remover qualquer contagem manual de tasks.

## Arquivo: .contract_driven/agent_prompts/decision_discovery.prompt.md

Função real:
Prompt de DSS/decisão arquitetural. Deveria ser enxuto, preciso e alinhado ao catálogo e ao pipeline atuais.

Tabela de pontuação:
| Critério | Nota | Justificativa objetiva |
|---------|------|------------------------|
| Qualidade instrucional real | 40 | A lógica de DSS existe, mas a carga mínima de leitura é grande e rígida. |
| Determinismo real | 24 | Continua ancorado em taxonomia do LAYOUT e não no `TASK_CATALOG`. |
| Eficiência de contexto real | 18 | Impõe 12 leituras mínimas, inclusive benchmark obrigatório, antes de propor decisão. |
| Robustez contra ambiguidade | 26 | O gatilho esportivo é razoável, o resto ainda força muita leitura manual. |
| Robustez contra respostas genéricas | 54 | A estrutura de saída é boa. |
| Robustez contra conflito entre regras | 24 | Não conversa com o catálogo novo. |
| Clareza de precedência | 30 | A cadeia DSS é relativamente clara internamente. |
| Acionabilidade | 46 | Operável, porém caro e pesado. |
| Estabilidade entre execuções | 24 | A variação vem do excesso de leituras e da dependência do backlog. |
| Resistência a loopholes | 28 | O agente pode cumprir parte da rotina e resumir demais o resto. |

Nota final do arquivo:
**31/100**

Veredito:
**reprovado**

Por que não é 100/100:
O prompt de DSS continua caro em contexto e pouco integrado ao novo routing.

Falhas encontradas:
| Falha | Severidade | Tipo | Impacto prático | Cenário de quebra |
|-------|------------|------|-----------------|-------------------|
| Exige benchmark competitivo obrigatório antes de qualquer decisão | Alta | contexto | Aumenta custo fixo e tende a alongar sessões demais | Toda decisão pequena vira sessão pesada |
| Continua fora do SSOT de task routing novo | Alta | conflito | A tarefa existe em `TASK_CATALOG`, mas o prompt não nasce dessa autoridade | O agente entra no DSS por caminhos diferentes |

Correções obrigatórias:
1. Integrar o prompt ao `TASK_CATALOG`.
2. Reduzir leituras mínimas para o estritamente necessário.
3. Tornar benchmark condicional, não absoluto.

## Arquivo: scripts/hb

Função real:
CLI de pipeline v2. Deveria ser o enforcement determinístico da sessão e dos estágios 0/1/2.

Tabela de pontuação:
| Critério | Nota | Justificativa objetiva |
|---------|------|------------------------|
| Qualidade instrucional real | 46 | O endurecimento de args obrigatórios foi positivo. |
| Determinismo real | 26 | Ainda usa módulos hardcoded e quebra em migração de sessão legada. |
| Eficiência de contexto real | 70 | É executável e concentra parte do enforcement. |
| Robustez contra ambiguidade | 34 | A intenção da v2 é clara. |
| Robustez contra respostas genéricas | 58 | Obriga mais dados do que a versão anterior. |
| Robustez contra conflito entre regras | 24 | Conflita com `MODULE_REGISTRY`, com o hook ativo e com a sessão legado. |
| Clareza de precedência | 34 | Lê SSOTs novos, mas não resolve o conflito sistêmico. |
| Acionabilidade | 64 | É muito mais acionável que o restante da malha. |
| Estabilidade entre execuções | 18 | Uma sessão antiga já o quebra no primeiro `verify`. |
| Resistência a loopholes | 20 | A CLI endureceu, mas o commit path ainda a contorna. |

Nota final do arquivo:
**39/100**

Veredito:
**reprovado**

Por que não é 100/100:
Melhor CLI, integração ruim.

Falhas encontradas:
| Falha | Severidade | Tipo | Impacto prático | Cenário de quebra |
|-------|------------|------|-----------------|-------------------|
| Usa lista hardcoded de módulos canônicos em vez de ler `MODULE_REGISTRY.yaml` | Alta | redundância | Reintroduz drift de taxonomia dentro do enforcement | Um módulo muda no registry e a CLI continua velha |
| Falha ao iniciar por incompatibilidade com `_reports/session_start.json` legado, sem migração/reset automático | Crítica | determinismo | O pipeline se autobloqueia por resíduo antigo | `hb verify --task-type ... --module ...` falha antes do validator |

Correções obrigatórias:
1. Ler módulos do registry real.
2. Implementar migração ou reset automático de sessão inválida.
3. Sincronizar a CLI com o hook efetivo.

## Arquivo: scripts/git-hooks/pre-commit

Função real:
Hook realmente ativo via `core.hooksPath`. Deveria defender o commit path contra sessões inválidas, artefatos não validados e handoff ausente.

Tabela de pontuação:
| Critério | Nota | Justificativa objetiva |
|---------|------|------------------------|
| Qualidade instrucional real | 18 | Como wrapper, ainda é simples demais para o pipeline que o resto do sistema descreve. |
| Determinismo real | 8 | O commit path real ignora `session_start.json`. |
| Eficiência de contexto real | 84 | É curto, mas isso aqui é pobreza funcional. |
| Robustez contra ambiguidade | 24 | Fica implícito um enforcement que não existe. |
| Robustez contra respostas genéricas | 18 | O agente pode commitar sem passar pelo rito de sessão que a arquitetura anuncia. |
| Robustez contra conflito entre regras | 6 | Conflita com `CLAUDE`, `PIPELINE`, `scripts/hb` e auditoria anterior. |
| Clareza de precedência | 10 | O hook ativo não reflete o pipeline oficial declarado. |
| Acionabilidade | 22 | Executa algo, mas muito menos do que deveria. |
| Estabilidade entre execuções | 8 | Estável, porém no sistema errado. |
| Resistência a loopholes | 6 | É o maior loophole atual do pipeline. |

Nota final do arquivo:
**20/100**

Veredito:
**reprovado**

Por que não é 100/100:
O hook efetivo não executa o enforcement que o sistema inteiro presume.

Falhas encontradas:
| Falha | Severidade | Tipo | Impacto prático | Cenário de quebra |
|-------|------------|------|-----------------|-------------------|
| Hook ativo é wrapper antigo e não lê `_reports/session_start.json` | Crítica | loophole | O pipeline de sessão não protege o commit | O agente ignora `hb verify/check/artifact` e ainda commita |
| Não exige `SESSION_HANDOFF.md` nem hash de artefato validado | Crítica | completude | O commit path real continua poroso | O enforcement descrito no audit não está em vigor |

Correções obrigatórias:
1. Reescrever o hook ativo com a lógica de sessão real.
2. Validar schema, stage exits, hash de staged blob e handoff.
3. Testar o hook como parte do CI local.

## Arquivo: contracts/schemas/shared/session_start.schema.json

Função real:
Schema do artefato central de sessão. Deveria ser compatível com a CLI, com o hook e com a migração de versões.

Tabela de pontuação:
| Critério | Nota | Justificativa objetiva |
|---------|------|------------------------|
| Qualidade instrucional real | 44 | O schema endurece bem o formato da sessão. |
| Determinismo real | 32 | Falta estratégia clara de migração/versionamento de sessão. |
| Eficiência de contexto real | 68 | É uma peça pequena e adequada ao papel. |
| Robustez contra ambiguidade | 36 | O shape é claro. |
| Robustez contra respostas genéricas | 48 | Impede vários placeholders antigos. |
| Robustez contra conflito entre regras | 24 | Ainda não está no commit path via hook ativo. |
| Clareza de precedência | 38 | Como schema, está bem delimitado. |
| Acionabilidade | 52 | Útil para validação. |
| Estabilidade entre execuções | 20 | A falta de migração faz a sessão antiga quebrar a nova. |
| Resistência a loopholes | 26 | Sozinho ele não fecha nada sem hook/CLI integrados. |

Nota final do arquivo:
**39/100**

Veredito:
**reprovado**

Por que não é 100/100:
O schema ficou mais forte do que o resto do pipeline consegue suportar hoje.

Falhas encontradas:
| Falha | Severidade | Tipo | Impacto prático | Cenário de quebra |
|-------|------------|------|-----------------|-------------------|
| Não existe estratégia de migração para sessão anterior incompatível | Crítica | manutenção | O endurecimento quebra a sessão em vez de saneá-la | `hb verify` falha por resíduos da versão anterior |
| O hook ativo ainda não usa esse schema | Crítica | conflito | O shape formal não controla o commit | A sessão inválida continua não bloqueada no caminho real |

Correções obrigatórias:
1. Introduzir migração/versionamento de sessão.
2. Fazer o hook ativo validar este schema.
3. Sincronizar o schema com a CLI e o validator.

## Arquivo: _reports/session_start.json

Função real:
Evidência de sessão. Deveria provar o estado atual, não misturar formatos antigos e novos.

Tabela de pontuação:
| Critério | Nota | Justificativa objetiva |
|---------|------|------------------------|
| Qualidade instrucional real | 8 | O conteúdo atual já é prova empírica do estado quebrado. |
| Determinismo real | 4 | Mistura campos antigos e novos. |
| Eficiência de contexto real | 84 | Pequeno, mas semanticamente inválido. |
| Robustez contra ambiguidade | 6 | O arquivo atual não serve nem para a v1 nem para a v2. |
| Robustez contra respostas genéricas | 8 | A evidência já não comprova nada com segurança. |
| Robustez contra conflito entre regras | 4 | O schema novo o reprova. |
| Clareza de precedência | 8 | Não está claro qual versão governa o arquivo atual. |
| Acionabilidade | 8 | Ele bloqueia a CLI nova e não protege o hook antigo. |
| Estabilidade entre execuções | 2 | É a maior fonte atual de instabilidade de sessão. |
| Resistência a loopholes | 4 | Mistura estrutural permite comportamento incoerente. |

Nota final do arquivo:
**14/100**

Veredito:
**reprovado**

Por que não é 100/100:
A evidência central está em estado híbrido e inconsistente.

Falhas encontradas:
| Falha | Severidade | Tipo | Impacto prático | Cenário de quebra |
|-------|------------|------|-----------------|-------------------|
| Contém `task_type/module/timestamp/stages` do modelo antigo e `stage2_artifacts` do novo modelo | Crítica | determinismo | A sessão atual é semanticamente híbrida | A CLI v2 recusa o arquivo |
| Não foi migrado nem arquivado automaticamente | Crítica | manutenção | Resíduo legado trava o pipeline novo | O usuário precisa limpar manualmente para voltar a operar |

Correções obrigatórias:
1. Arquivar o arquivo legado automaticamente.
2. Recriar a sessão no schema novo.
3. Proibir coexistência de campos de versões diferentes.

## Arquivo: _reports/evidence/boot_resolution_report.json

Função real:
Relíquia do modelo antigo de boot. Hoje continua sugerindo autoridade e custo de leitura que o sistema novo tenta substituir.

Tabela de pontuação:
| Critério | Nota | Justificativa objetiva |
|---------|------|------------------------|
| Qualidade instrucional real | 12 | Como legado, apenas confunde. |
| Determinismo real | 8 | Continua descrevendo um boot que a estrutura nova quer abandonar. |
| Eficiência de contexto real | 10 | Puxa leituras demais e contradiz o discurso de boot enxuto. |
| Robustez contra ambiguidade | 10 | Mantém fonte antiga de boot. |
| Robustez contra respostas genéricas | 18 | Um agente pode usá-lo para justificar leitura excessiva. |
| Robustez contra conflito entre regras | 8 | Conflita com `BOOT_PROFILES.yaml` e com a redução de boot. |
| Clareza de precedência | 8 | Não está explicitamente removido do fluxo. |
| Acionabilidade | 12 | Só serve para induzir caminho velho. |
| Estabilidade entre execuções | 8 | A cada coexistência com o sistema novo, aumenta ruído. |
| Resistência a loopholes | 10 | Fornece atalho para “seguir o modelo antigo”. |

Nota final do arquivo:
**10/100**

Veredito:
**reprovado**

Por que não é 100/100:
É um arquivo legado ainda ativo no imaginário do sistema.

Falhas encontradas:
| Falha | Severidade | Tipo | Impacto prático | Cenário de quebra |
|-------|------------|------|-----------------|-------------------|
| Continua listado em LAYOUT como artefato derivado relevante | Alta | conflito | O modelo antigo segue respirando | O agente continua vendo boot resolution como evidência viva |
| A existência dele contradiz o discurso de boot reduzido e novo SSOT | Alta | contexto | O custo mental aumenta | O agente abre o legado para “garantir” leitura |

Correções obrigatórias:
1. Mover para `_reports/legacy/`.
2. Remover referências ativas no layout e docs.
3. Parar de usá-lo como evidência do fluxo atual.

## Arquivo: _reports/agent_execution/latest.json

Função real:
Ponteiro do modelo antigo de pré-contrato. Hoje conflita com a sessão v2.

Tabela de pontuação:
| Critério | Nota | Justificativa objetiva |
|---------|------|------------------------|
| Qualidade instrucional real | 14 | Como legado, apenas preserva um fluxo anterior. |
| Determinismo real | 10 | Mantém fases antigas no sistema. |
| Eficiência de contexto real | 14 | Mais um artefato para o agente decidir se lê ou não. |
| Robustez contra ambiguidade | 12 | A estrutura continua visível em LAYOUT e reports. |
| Robustez contra respostas genéricas | 20 | O agente pode se apoiar nele em vez da sessão atual. |
| Robustez contra conflito entre regras | 10 | Conflita com `session_start` e com a nova CLI. |
| Clareza de precedência | 10 | Não está explicitamente rebaixado a legado. |
| Acionabilidade | 14 | Não deveria mais guiar nada. |
| Estabilidade entre execuções | 10 | A coexistência com o novo fluxo mantém instabilidade. |
| Resistência a loopholes | 12 | Dá atalho para justificar pré-contrato antigo. |

Nota final do arquivo:
**13/100**

Veredito:
**reprovado**

Por que não é 100/100:
É legado vivo demais para um pipeline que diz ter migrado.

Falhas encontradas:
| Falha | Severidade | Tipo | Impacto prático | Cenário de quebra |
|-------|------------|------|-----------------|-------------------|
| Continua apontado como evidência em LAYOUT | Alta | conflito | O fluxo antigo não foi removido | O agente segue evidência antiga e ignora `session_start` |
| Não há marcação explícita de depreciação no arquivo ou nos docs | Média | manutenção | O legado parece suportado | O time mantém dois modelos de observabilidade |

Correções obrigatórias:
1. Mover para área de legado.
2. Remover referências ativas.
3. Declarar depreciação explícita.

## BLOCO 4 — CASOS DE QUEBRA

| condição de entrada | ponto de falha | arquivo(s) envolvido(s) | consequência no comportamento | severidade |
|---------------------|----------------|-------------------------|-------------------------------|-----------|
| Agente segue `RULES` para boot | `RULES` ainda manda olhar `CLAUDE.md §7` | `CONTRACT_SYSTEM_RULES.md`, `CONTRACT_PIPELINE.md`, `GATES_REGISTRY.yaml`, `CLAUDE.md` | Boot authority muda conforme arquivo consultado | Crítica |
| Agente segue `TASK_CATALOG` literalmente | `artifacts_produced` conflitam com LAYOUT | `TASK_CATALOG.yaml`, `CONTRACT_SYSTEM_LAYOUT.md` | Arquivos são criados no path errado com aparência de SSOT | Crítica |
| Commit real acontece via hook atual | Hook ativo não valida sessão | `scripts/git-hooks/pre-commit`, `_reports/session_start.json`, `scripts/hb` | O enforcement de sessão não está no caminho real do commit | Crítica |
| Sessão anterior existe em disco | Schema novo rejeita arquivo legado | `session_start.schema.json`, `_reports/session_start.json`, `scripts/hb` | O pipeline novo se autobloqueia antes de operar | Crítica |
| Agente cria novo SSOT em `_canon` | Allowlist não autoriza o arquivo | `docs/_canon/README.md`, `CONTRACT_SYSTEM_LAYOUT.md`, `GATES_REGISTRY.yaml` | A própria governança reprova a mudança já aplicada | Crítica |
| Agente instancia README global oficial | Template aponta para docs mortos | `.contract_driven/templates/globais/README.md`, `docs/_canon/README.md` | O canon é recriado com referências inexistentes | Alta |
| Agente instancia template de erros por módulo | Template aponta para `ERROR_MODEL.md` inexistente | `.contract_driven/templates/modulos/ERRORS_{{MODULE}}.md` | O documento já nasce semanticamente inválido | Alta |
| Agente usa family de API auxiliar | Guias auxiliares quebrados competem com `api_rules.yaml` | `.contract_driven/templates/api/*.md`, `api_rules.yaml` | O agente mistura SSOT forte com apoio quebrado | Alta |
| Local validator roda perfil completo | `CANON_ALLOWLIST_GATE` falha no estado atual | `GATES_REGISTRY.yaml`, `docs/_canon/*` | O repo se auto-reprova sem alteração do usuário | Alta |
| Legado continua presente | `_reports` antigos seguem ativos no layout | `CONTRACT_SYSTEM_LAYOUT.md`, `_reports/evidence/boot_resolution_report.json`, `_reports/agent_execution/latest.json` | O sistema nunca termina a migração e perpetua dois modelos | Alta |

## BLOCO 5 — REGRESSÕES DE CONTEXTO

| Arquivo ou decisão estrutural | Regressão identificada | Impacto em tokens/contexto | Gravidade | Correção |
|------------------------------|------------------------|----------------------------|----------|----------|
| `RULES + LAYOUT + GLOBAL_TEMPLATES` | Só os três arquivos raiz somam 9.012 palavras | Pressão alta de contexto logo na camada de governança | Alta | Parar de exigir leitura conjunta e eliminar duplicações |
| `GLOBAL_TEMPLATES.md` | Índice muito longo para apontar templates parcialmente quebrados | Muito texto para pouca confiança operacional | Alta | Reduzir a índice mínimo e validar famílias |
| `api_rules.yaml` | SSOT único de API virou monólito difícil de consumir | Tende a leitura parcial e improviso | Média | Gerar visões reduzidas sem duplicar norma |
| `decision_discovery.prompt.md` | Exige 12 leituras mínimas e benchmark obrigatório | Sessões de DSS ficam caras demais | Alta | Tornar benchmark condicional e cortar leitura fixa |
| `BOOT_PROFILES.yaml` em `_canon` | Novo arquivo canônico adicionado sem promoção completa | Clareza local melhorou, eficiência/global piorou por conflito | Alta | Mover o arquivo ou promover corretamente |
| `TASK_CATALOG.yaml` em `_canon` | Mesmo problema do item anterior | Mais uma fonte de boot/routing sem cadeia fechada | Alta | Mover ou promover corretamente |
| `_reports` legados | `boot_resolution_report` e `agent_execution` continuam visíveis | O agente precisa distinguir modelo novo vs antigo | Alta | Remover do fluxo ativo |
| templates globais | Reintroduzem docs mortos (`API_CONVENTIONS`, `ERROR_MODEL`, etc.) | Custo de revisão e risco de recontaminação do canon | Alta | Corrigir família ou arquivar |
| `_canon` real vs allowlist | 40 arquivos fora da listagem do layout | A pasta soberana perde perímetro e exige checagem manual | Crítica | Fechar a allowlist e mover intrusos |

## BLOCO 6 — LACUNAS DE DETERMINISMO E QUALIDADE

### bloqueadores críticos

- `RULES`, `PIPELINE` e `GATES_REGISTRY` ainda apontam para `CLAUDE.md §7` como boot authority.
- `BOOT_PROFILES.yaml` e `TASK_CATALOG.yaml` foram criados em `_canon` sem promoção completa e já falham no `CANON_ALLOWLIST_GATE`.
- O hook ativo via `core.hooksPath` continua sendo wrapper antigo e ignora `session_start.json`.
- `TASK_CATALOG.yaml` produz paths conflitantes com o `LAYOUT`.
- `_reports/session_start.json` atual mistura versões e quebra a CLI nova.

### bloqueadores altos

- Templates globais e auxiliares de API ainda apontam para arquivos inexistentes.
- A família de templates de módulo ainda contém refs quebradas e ADR acoplada a `training`.
- `_canon` contém dezenas de arquivos fora da allowlist declarada.
- `_reports/evidence/boot_resolution_report.json` e `_reports/agent_execution/latest.json` continuam ativos no desenho do sistema.
- `decision_discovery.prompt.md` continua caro demais para boot/descoberta.

### bloqueadores médios

- `OPERATIONS.md` ainda duplica precedência e não absorve totalmente os SSOTs novos.
- `README.md` do `_canon` não lista a estrutura real e aponta comando técnico desatualizado.
- `api_rules.yaml` segue forte, porém pesado e cercado de auxiliares em drift.

### bloqueadores baixos

- `CLAUDE.md` ainda mantém resumo manual de módulos/status.
- `templates/README.md` não alerta para famílias quebradas.
- O snippet de header é bom, mas depende de ecossistema ainda não saneado.

## BLOCO 7 — TESTE DE LOOPHOLES

| Item | Como um agente pode obedecer superficialmente | Resultado ruim |
|------|-----------------------------------------------|----------------|
| Arquitetura geral | Seguir `CLAUDE` para boot, `RULES` para promoção e o hook real para commit | Cada etapa usa uma autoridade diferente e o sistema parece “cumprido” |
| `CLAUDE.md` | Usar apenas o resumo de 9 tasks | Ignora `decision_discovery` e tasks congeladas do catálogo novo |
| `RULES.md` | Citar `CLAUDE.md §7` e não ler `BOOT_PROFILES.yaml` | Boot segue autoridade errada com respaldo “normativo” |
| `LAYOUT.md` | Usar a allowlist escrita e ignorar `_canon` real | O sistema já reprova o próprio repo atual |
| `GLOBAL_TEMPLATES.md` | Copiar template oficial sem questionar | O agente recria docs mortos e refs inexistentes |
| `_canon/README.md` | Confiar que a tabela do canon é completa | `BOOT_PROFILES` e `TASK_CATALOG` viram intrusos invisíveis |
| `OPERATIONS.md` | Usar o resumo de precedência como fechamento | O conflito com `RULES` continua |
| `CONTRACT_PIPELINE.md` | Seguir o pipeline curto sem verificar hook ativo | O commit path real continua antigo |
| `BOOT_PROFILES.yaml` | Resolver `./CLAUDE.md` por inferência | Paths de boot ficam subjetivos |
| `TASK_CATALOG.yaml` | Escrever exatamente em `artifacts_produced` | O agente viola o layout canônico e ainda “cumpre” o catálogo |
| `GATES_REGISTRY.yaml` | Apontar `boot_profiles_ref` para `CLAUDE.md §7` como se fosse verdade | A camada machine-readable legitima a referência falsa |
| `_canon extras` | Criar novo arquivo em `_canon` e esperar que ele seja tratado como soberano | A pasta vira depositário de autoridade arbitrária |
| `api_rules.yaml` | Ler só partes convenientes do SSOT | Decisão parcial de API gera inconsistência ou média qualidade |
| `templates/api/*.md` | Usar guia auxiliar externo em vez do SSOT | O agente ressuscita `API_CONVENTIONS.md` e outros fantasmas |
| `templates/globais/*.md` | Instanciar o README global antigo | O canon renasce com docs inexistentes |
| `templates/modulos/*.md` | Instanciar `ERRORS` e manter `error_model_ref` | O doc nasce quebrado mas com header válido |
| `module_human_docs_header.yaml` | Usar só o snippet mínimo | O header parece correto, mas o tipo específico pode continuar inválido |
| `MODULE_DOC_HEADER_POLICY.yaml` | Validar só a presença do campo | A referência pode existir no campo e apontar para artefato morto |
| `templates/README.md` | Seguir o guia da pasta e copiar template sem validar destino | O erro é propagado de forma padronizada |
| `pre_contract_orchestrator.prompt.md` | Rodar `hb verify` e publicar sessão | O hook real ainda não depende disso |
| `decision_discovery.prompt.md` | Fazer leituras mínimas superficiais e benchmark resumido | O DSS vira ritual caro com decisão mediana |
| `scripts/hb` | Rodar `verify` numa sessão velha sem reset | A CLI trava por legado antes de operar |
| `scripts/git-hooks/pre-commit` | Confiar que o hook do repo basta | O commit ignora toda a arquitetura de sessão |
| `session_start.schema.json` | Validar só o formato do arquivo novo | O hook ativo ainda não usa o schema |
| `_reports/session_start.json` | Reaproveitar arquivo híbrido | O estado atual da sessão continua sem semântica confiável |
| `boot_resolution_report.json` | Abrir o legado “por segurança” | O agente volta ao modelo antigo e gasta contexto extra |
| `_reports/agent_execution/latest.json` | Tratar o ponteiro legado como evidência oficial | O fluxo novo perde autoridade prática |

## BLOCO 8 — CORREÇÕES FINAIS OBRIGATÓRIAS

Checklist determinístico completo externalizado em [PIPELINE_SOLUÇÕES.md](/home/davis/HB-TRACK/.dev/planejamento/PIPELINE_SOLUÇÕES.md).

Síntese das correções de impacto cascata:
1. Resolver a localização e a autoridade de `BOOT_PROFILES` e `TASK_CATALOG`.
2. Reescrever o hook ativo para usar `session_start.schema.json`.
3. Reconciliar `TASK_CATALOG` com `LAYOUT` e templates de módulo.
4. Saneiar `_canon` contra intrusos e allowlist incompleta.
5. Corrigir/arquivar templates e docs que apontam para artefatos inexistentes.
6. Remover o legado `_reports` do fluxo ativo.

## BLOCO 9 — VEREDITO FINAL BINÁRIO

- passa ou reprova: **reprova**
- quais critérios já estão em 100/100: **nenhum**
- quais critérios ainda não estão: **todos**
- o que falta para aprovação total:

1. Fechar uma única cadeia de boot authority.
2. Colocar o enforcement de sessão no hook realmente ativo.
3. Parar de permitir SSOT novo em local não autorizado.
4. Reconciliar catálogo de tasks com paths canônicos e templates.
5. Remover referências quebradas e legado ativo.
6. Reduzir contexto estrutural sem reintroduzir ambiguidade.
