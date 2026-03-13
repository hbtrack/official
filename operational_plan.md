# PLANO PARA ATUALIZAR OS ARQUVIOS DE GOVERNANÇA DO CONTRATO TÉCNICO

`CONTRACT_SYSTEM_LAYOUT.md`, `CONTRACT_SYSTEM_RULES.md`, `GLOBAL_TEMPLATES.md` e `api_rules.yaml`

O diagnóstico-base é este: sua governança já definiu corretamente a separação entre layout, regras operacionais, templates e convenções de API, mas o ganho real só aparece quando essa separação vira rotina de atualização, validação e bloqueio. Hoje, `CONTRACT_SYSTEM_LAYOUT.md` já limita o papel de cada superfície, `CONTRACT_SYSTEM_RULES.md` já centraliza o comportamento do agente, `GLOBAL_TEMPLATES.md` já proíbe duplicar templates de API, e `api_rules.yaml` já se declara como SSOT de convenções e templates HTTP. O plano abaixo transforma isso em operação contínua.    

**Objetivo operacional**

Fazer com que o agente consiga criar contratos a partir dos templates com três garantias: ler pouco e certo, preencher apenas placeholders resolvíveis, e bloquear quando faltar convenção explícita. Essa direção já está embutida nas suas regras: nenhuma superfície pode ter duas fontes primárias, API HTTP deve obedecer a `api_rules.yaml`, e artefatos derivados não redefinem a fonte.  

**Plano operacional**

**Fase 1 — Congelar fronteiras de autoridade** [ ] DONE

Ação 1. Definir dono único por tipo de conteúdo.
`CONTRACT_SYSTEM_LAYOUT.md` fica responsável apenas por paths, layout, naming e soberania por superfície. `CONTRACT_SYSTEM_RULES.md` fica responsável apenas por precedência, boot, bloqueios, readiness e procedimento. `GLOBAL_TEMPLATES.md` fica responsável apenas por scaffolds humanos. `api_rules.yaml` fica responsável por todas as regras, validações e templates de API HTTP. Isso já está previsto nos arquivos; o trabalho agora é remover qualquer duplicação residual no repositório.   

Ação 2. Instituir a regra “uma norma, um arquivo soberano”.
Se uma convenção de paginação, erro, naming, versionamento ou segurança HTTP estiver fora de `api_rules.yaml`, ela deve ser tratada como referência secundária ou removida. O próprio RULES determina que, se a convenção necessária não estiver explícita em `api_rules.yaml`, o agente deve bloquear com `BLOCKED_MISSING_API_CONVENTION`. 

Ação 3. Separar global de módulo sem ambiguidade.
`DOMAIN_AXIOMS.json` deve manter apenas invariantes globais e política de extensão; axiomas específicos devem viver em `docs/hbtrack/modulos/{module}/DOMAIN_AXIOMS_{MODULE}.json`, como o próprio arquivo já prevê. Isso reduz contaminação semântica entre módulos. 

**Fase 2 — Reduzir tamanho e custo cognitivo dos arquivos** [ ] DONE

Ação 4. Quebrar arquivos grandes em índice + unidades atômicas.
Você não precisa matar os arquivos raiz; precisa fazer deles pontos de entrada curtos. O padrão correto é: arquivo raiz com índice, propósito, precedência e links; detalhes extensos em arquivos menores por assunto. Esse desenho é coerente com a sua trilogia e com a regra de navegação vinculante.   

Ação 5. Fatiar `api_rules.yaml` por temas internos, mantendo um índice canônico.
O arquivo já centraliza tudo de API e contém `contract_templates`. O problema operacional não é o conceito; é o volume. Quebre logicamente em blocos como: naming, pagination, errors, security, compatibility, templates root OpenAPI, templates path module, templates schemas HTTP-facing. Mantenha um índice mestre ou loader canônico, mas evite um monólito onde uma pequena mudança em paginação exige revisão visual do arquivo inteiro.   

Ação 6. Enxugar `GLOBAL_TEMPLATES.md` para scaffolds realmente instanciáveis.
Hoje ele está correto ao proibir templates de API dentro dele, mas o registro de placeholders está amplo demais. Remova placeholders vagos e preserve apenas os que o agente consegue preencher com base no canon, no módulo ou em decisão explícita do humano. Placeholder genérico demais vira convite para alucinação.  

**Fase 3 — Padronizar o fluxo de atualização** [ ] DONE

Ação 7. Instituir a ordem canônica de alteração.
Toda mudança deve seguir a cadeia: módulo canônico → contrato técnico primário → docs mínimas do módulo → docs condicionais → testes/evidências → derivados. Isso é coerente com a separação de fontes por superfície e com a lista mínima de docs de módulo exigida pelo RULES.  

Ação 8. Atualizar por “arquivo proprietário”, nunca por conveniência.
Se a mudança é de estrutura/path, atualiza LAYOUT. Se é de comportamento do agente, atualiza RULES. Se é scaffold, atualiza GLOBAL_TEMPLATES. Se é convenção HTTP, atualiza api_rules. Se é regra de negócio do módulo, atualiza `DOMAIN_RULES_<MODULE>.md`. Se é interface pública, atualiza OpenAPI. Essa disciplina é o que impede sincronização fantasma.  

Ação 9. Proibir manutenção “espelhada”.
Não manter a mesma regra em texto corrido no canon e em YAML normativo de API ao mesmo tempo. `docs/_canon/API_CONVENTIONS.md` pode existir como material de leitura humana, mas não deve competir com `api_rules.yaml` como fonte decisória para o agente. O RULES já torna `api_rules.yaml` SSOT para design HTTP. 

**Fase 4 — Operar o agente com contexto mínimo suficiente** [ ] DONE

Ação 10. Criar perfis de leitura por tarefa.
O boot geral continua existindo, mas o agente não deve carregar tudo sempre. Para criar contrato de API, ele lê: LAYOUT, RULES, api_rules, `SYSTEM_SCOPE`, docs do módulo e contratos do módulo. Para criar docs de módulo, ele lê: LAYOUT, RULES, GLOBAL_TEMPLATES, `SYSTEM_SCOPE`, `HANDBALL_RULES_DOMAIN` se aplicável, e os contratos do módulo. Isso respeita a regra de leitura conjunta, mas reduz custo de contexto.   

Ação 11. Criar prompts operacionais por tipo de artefato.
Exemplo: “gerar `contracts/openapi/paths/training.yaml`” deve obrigar o agente a usar o template canônico em `api_rules.contract_templates`, respeitar naming do módulo, limitar paths a um único módulo e referenciar somente a pasta canônica de schemas. Isso deriva diretamente das regras de layout e templates já existentes.  

Ação 12. Ensinar o agente a bloquear cedo.
Se módulo não é canônico, bloquear. Se convenção de API não está explícita em `api_rules.yaml`, bloquear. Se um artefato obrigatório está fora do path canônico, não tratá-lo como autoritativo. Esses comportamentos já estão normativamente definidos; falta torná-los gatilhos padrão dos prompts/linters.  

**Fase 5 — Instalar gates automáticos de sincronização** [ ] DONE

Ação 13. Criar um linter de placeholders não resolvidos.
Todo artefato pronto para implementação deve falhar se contiver `{{...}}`, `TODO`, `TBD` ou placeholders equivalentes fora de regiões explicitamente permitidas para scaffold. Isso é particularmente importante em `GLOBAL_TEMPLATES.md`, que hoje registra muitos placeholders.  

Ação 14. Criar um validador de path canônico e naming.
Ele deve verificar se `contracts/openapi/paths/<module>.yaml`, `contracts/schemas/<module>/<entity>.schema.json`, `contracts/workflows/<module>/<use_case>.arazzo.yaml` e `contracts/asyncapi/<layer>/<name>.yaml` obedecem exatamente ao layout definido. 

Ação 15. Criar um detector de duplicação normativa de API.
Sempre que aparecer regra HTTP normativa fora de `api_rules.yaml`, emitir erro ou ao menos warning forte. Isso materializa a regra de SSOT canônico de API. 

Ação 16. Criar um gate de documentação mínima por módulo.
Nenhum módulo deve ser considerado “contratado” sem `README`, `MODULE_SCOPE`, `DOMAIN_RULES`, `INVARIANTS` e `TEST_MATRIX`. Os documentos condicionais entram apenas quando a matriz de aplicabilidade exigir.  

Ação 17. Criar um gate de cross-reference obrigatório.
Docs de módulo devem sempre apontar para `SYSTEM_SCOPE.md`, `HANDBALL_RULES_DOMAIN.md` quando o trigger aplicar, OpenAPI path file e pasta de schemas do módulo. Isso já está normativamente expresso no layout e nos headers dos templates.   

**Fase 6 — Definir o pipeline de geração de contratos pelo agente** [ ] DONE

O pipeline recomendado para o agente é este:

1. Validar que o módulo existe na taxonomia canônica. 
2. Ler LAYOUT, RULES e o template pertinente.  
3. Ler `api_rules.yaml` quando a tarefa envolver API. 
4. Instanciar apenas os templates da superfície correta. `GLOBAL_TEMPLATES` para docs humanas; `api_rules.contract_templates` para OpenAPI e artefatos HTTP.  
5. Preencher apenas placeholders suportados por evidência disponível. Se faltar regra explícita, bloquear. 
6. Gerar docs mínimas do módulo antes de docs condicionais. 
7. Validar naming, path, placeholders, cross-references e superfície SSOT.  
8. Só depois gerar derivados como client, UI types ou outros artefatos. 

**Backlog priorizado**

Prioridade alta:

1. Remover duplicações normativas de API fora de `api_rules.yaml`. [ ] DONE
2. Enxugar `GLOBAL_TEMPLATES.md` e reduzir placeholders vagos. [ ] DONE
3. Criar checklist por tipo de tarefa do agente. [ ] DONE
4. Criar validador de placeholder, path canônico e módulo canônico.  [ ] DONE
5. Modularizar `DOMAIN_AXIOMS` por módulo quando aplicável. [ ] DONE

Prioridade média:

1. Fatiar internamente `api_rules.yaml` sem perder SSOT. [ ] DONE
2. Criar prompts operacionais fixos para “gerar contrato de API”, “gerar docs mínimas de módulo”, “gerar schema de domínio”, “gerar workflow Arazzo”.  [ ] DONE
3. Criar gate de cross-reference obrigatório. [ ] DONE
4. Classifique as templates em `GLOBAL_TEMPLATES.md` por tipo de documento. [ ] DONE
5. Cada template em `GLOBAL_TEMPLATES.md` deve ter cabeçalhos claros e consistentes. [ ] DONE
6. Cada template em `GLOBAL_TEMPLATES.md` deve ser completa, permitindo seu uso pelo agente, para criar contratos oficiais. [ ] DONE

Prioridade baixa:

1. Reorganizar materiais humanos explicativos para Diátaxis sem tocar na fonte normativa. [ ] DONE
2. Criar documentação curta de “como alterar convenções” para humanos. [ ] DONE

**Definição de pronto para esse plano** [ ] DONE

Você pode considerar o plano implantado quando o repositório passar a obedecer a estes sinais objetivos: nenhuma convenção HTTP normativa fora de `api_rules.yaml`; nenhum módulo fora da taxonomia canônica; nenhum arquivo obrigatório fora do path canônico sendo tratado como soberano; nenhum contrato pronto com placeholders abertos; e o agente conseguindo gerar `contracts/openapi/paths/<module>.yaml` e o conjunto mínimo de docs do módulo apenas lendo as fontes certas, sem precisar “adivinhar”. Isso é compatível com as regras já existentes.   

O ponto que você não perguntou, mas é decisivo, é este: o gargalo principal não é “tamanho do arquivo”; é ausência de disciplina de propriedade e de bloqueio automático. Arquivo menor ajuda. Mas o que realmente melhora o trabalho do agente é: fonte única por decisão, template sem ambiguidade e pipeline que falha cedo quando a regra não está explícita. Isso é exatamente o que seus próprios documentos já defendem; o plano só operacionaliza.  
