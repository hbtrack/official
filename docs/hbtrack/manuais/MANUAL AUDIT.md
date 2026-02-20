2. Onde o determinismo quebra hoje (pontos críticos)
   
   2.1 Você diz SSOT = 3 arquivos, mas a CLI só trata 2
   No texto, os “3 pilares SSOT” incluem `alembic_state.txt`, mas em `hb_cli.py` você define `self.contracts = ['schema.sql', 'openapi.json']`. Isso cria uma verdade dupla: o manual promete 3, o guardião fiscaliza 2. Resultado: drift em migrações passa “silenciosamente”.

Correção (MUST): o SSOT é realmente 3 e a CLI fiscaliza os 3. 

2.2 “hb check” só detecta drift no working tree, não valida rastreabilidade
Seu `check_integrity()` usa `git diff` do arquivo contra o estado commitado/working tree. Isso bloqueia alterações “não commitadas”. Mas depois que você commita uma mudança em `schema.sql` ou `openapi.json`, o check passa — mesmo se:

* não existe AR referenciando a mudança,
* não existe evidência executada para essa mudança,
* ou o contrato foi atualizado “na mão” sem correspondência com o código.

Ou seja: você não está validando “mudança contratual exige AR + evidência”, só está validando “não deixe contrato sujo antes do commit”.

Correção (MUST): o guardião precisa validar vínculo contrato↔AR↔evidência (ex.: “qual AR autorizou a alteração do openapi.json?”).

2.3 A parte “PRD” praticamente não existe
O fluxo está todo em ARs (tarefas técnicas). Um PRD de verdade é outro nível: valor, escopo, métricas, não-funcionais, riscos, critérios de aceitação do produto, e rastreabilidade até contratos e gates.

Hoje você tem:

* AR Contract JSON: tarefas técnicas
* AR markdown: execução
  Mas não tem:
* PRD (com ID, versão, escopo, ACs do produto)
* mapeamento PRD → ARs
* regra de “não pode abrir AR fora de um PRD ativo” (se você quiser esse rigor)

Sem PRD, o manual é “AR + Contratos”, não “PRD + Contratos”.

2.4 O hook em Bash conflita com a sua política “Python-only”
Seu manual usa `scripts/git-hooks/pre-commit` em `#!/bin/bash`. Se a sua política operacional é “banir .sh/.ps1” (e você vem insistindo nisso no HB Track), isso precisa ser consistente: hook deve ser um arquivo executável em Python (shebang) ou outro mecanismo permitido.

Correção (MUST, se essa política vale aqui): hook 100% Python.

2.5 Instalação: `pip install argparse difflib` está incorreto
`argparse` e `difflib` são da biblioteca padrão do Python. Esse passo induz ruído e quebra a credibilidade “determinística” do manual (porque uma pessoa vai tentar instalar e estranhar).

Correção (MUST): remover esse passo ou trocar por dependências reais (se existirem).

2.6 `hb report` é vulnerável a inconsistência de estado dentro da AR
Você “marca status” fazendo replace simples de `"🔲 PENDENTE"` por `"✅ SUCESSO"`/`"❌ FALHA"` no arquivo inteiro. Isso pode:

* substituir ocorrências fora do cabeçalho,
* gerar estados inválidos (ex.: “EM_EXECUCAO” nunca é aplicado pela CLI),
* e você mistura “status do resultado do comando” com “status do ciclo de vida” (pendente/em execução/concluído).

Correção (SHOULD): separar dois campos:

* lifecycle_status: PENDENTE | EM_EXECUCAO | CONCLUIDO | BLOQUEADO
* validation_status: PASS | FAIL (última execução)
  Idealmente com front-matter estruturado (YAML/JSON) para parse determinístico.

2.7 O índice (`docs/_INDEX.md`) é append-only (gera duplicação e drift)
`_update_index()` sempre dá append. Isso vira um log, não um “índice confiável”. Com o tempo, duplica entradas e quebra o papel de SSOT.

Correção (SHOULD): índice deve ser regenerável a partir do filesystem (fonte real), não acumulado manualmente.

3. O que falta para “PRD + Contratos” ficar completo (mínimo viável)
   Aqui está o núcleo que eu adicionaria, sem inflar burocracia.

3.1 Introduzir PRD como artefato de topo (MUST, se você quer “PRD e Contratos”)
Um PRD mínimo precisa de:

* PRD_ID, versão, status (DRAFT/ACTIVE/DONE)
* Escopo (IN/OUT)
* ACs do produto (binários, testáveis)
* Contratos afetados (ex.: openapi, schema, UI routes)
* Gates mínimos por AC (comando e evidência esperada)
* Mapa de rastreio: PRD_AC → (1..n) AR_IDs

3.2 Criar “Contract Registry” (MUST)
Você precisa de um “registro de contratos” com:

* lista de contratos (path)
* tipo (DB/API/UI/CONFIG)
* origem (DERIVED vs PROMOTED)
* comando de validação/geração (quando aplicável)
* política de mudança (ex.: “mudanças em openapi exigem gate X”)

Sem isso, “contrato” fica subjetivo e muda por conversa.

3.3 O guardião tem que validar vínculo contratual (MUST)
Quando um contrato muda, o pre-commit precisa responder:

* Qual AR autoriza essa mudança?
* Essa AR tem evidência PASS para os gates exigidos?
* O contrato atualizado está “coerente” com o resto (ex.: openapi válido, schema consistente)?

Isso pode ser feito via convenção simples:

* AR contém uma seção “Contracts touched: [openapi.json, schema.sql]”
* Evidence PASS obrigatória antes de permitir commit que altera esses arquivos

3.4 Definir gates mínimos por “capability” (SHOULD)
Seu manual deixa o comando de teste livre. Isso é bom para flexibilidade, ruim para padronização. Pelo menos para AUTH/RBAC/DB-MIGRATIONS, gates mínimos fixos evitam “PASS fraco”.

4. O que você NÃO perguntou, mas deveria (e as respostas objetivas)
   4.1 “Como garanto que schema.sql e openapi.json são verdade e não ‘arquivo editado’?”
   Resposta: você precisa declarar se eles são DERIVED (gerados) ou PROMOTED (editados como fonte). Se forem DERIVED, o protocolo MUST ter comandos determinísticos de geração, e o guardião deve bloquear edição manual. Se forem PROMOTED, você precisa de gates de consistência (ex.: openapi valida + testes de rota).

4.2 “Onde entram contratos de UI/Frontend e config?”
Resposta: se seu sistema tem front e infra, só DB/API não bastam. No mínimo, inclua:

* UI contract: rotas/páginas principais + componentes chave (ou um “ui_manifest.json”)
* Config contract: `config.py` (se isso é regra do seu ecossistema)
  Sem isso, o executor “passa” em backend e quebra UI/ops sem violar o protocolo.

4.3 “Como evito evidência não-determinística?”
Resposta: defina política de evidência:

* comandos MUST ser idempotentes e com exit code confiável
* logs MUST registrar versão do ambiente (python -V, hash do commit, etc.)
* se depende de DB/serviço, precisa de “runtime scenario” reproduzível (senão o PASS não é replicável)

4.4 “Como isso funciona com múltiplas pessoas/branches?”
Resposta: seu modelo atual é local-first. Para time, você precisa:

* convenção de naming/ID global (AR/PRD)
* regra de merge (não aceita PR que altera contratos sem AR+evidência)
  Isso normalmente vira gate de CI, mas mesmo sem CI, o protocolo deve prever o cenário.

5. Recomendações finais (prioridade)
   Prioridade 1 (corrige falsos positivos): alinhar SSOT real (2 vs 3) + fazer guardião validar “contrato mudou ⇒ existe AR + evidência PASS”.
   Prioridade 2 (traz PRD de verdade): adicionar PRD minimalista + rastreio PRD→AR.
   Prioridade 3 (evita drift documental): índice regenerável + status estruturado (front-matter) + padronização mínima de gates por capability.
   Prioridade 4 (consistência com sua política): remover dependências fake do pip e substituir hook bash por hook python (se “Python-only” é requisito do sistema).







### 1. Otimização do Fluxo Arquiteto vs. Executor

Nos seus prints, você já utiliza o **Cline** em um fluxo de separação de papéis. Você pode potencializar isso usando o Gemini como o seu "cérebro" de baixo custo e contexto gigante:

* **Gemini 3.1 Pro no Planejamento (Arquiteto):** Use o Gemini 3.1 Pro para a fase de **"Plan Mode"** no Cline. Por ter uma janela de contexto de até 2 milhões de tokens, ele é imbatível para ler toda a sua documentação de handebol e o histórico do `Hb Track` de uma só vez sem "esquecer" detalhes das regras de negócio.
* **Modelos "Fast" ou "Free" na Execução:** Para tarefas repetitivas de codificação (como criar os enums em `match_events.py` que aparece no seu print), utilize o **Gemini 3 Flash** ou o **z-ai/glm-5** (que você já tem selecionado como "Free"). Isso economiza créditos de modelos caros como o Claude Opus para quando o código realmente falhar.

---

### 2. Divisão de Tarefas por Ferramenta

Como você tem várias extensões instaladas (**Claude Code, Codex, Cline**), evite usá-las para a mesma coisa:

| Ferramenta | Quando Usar | Vantagem para seu Projeto |
| --- | --- | --- |
| **Cline (com Gemini)** | Refatorações estruturais e lógica complexa. | Ótimo para o que você está fazendo: "unificar docs" e segurança em `auth.py`. |
| **Claude Code** | Debugging rápido e "terminal talk". | Use para rodar os testes de validação que aparecem no seu print; ele é muito preciso em interpretar erros de runtime. |
| **Codex / Copilot Chat** | Dúvidas pontuais de sintaxe ou "como fazer X em Python". | Evita que você abra um "ciclo de tarefa" pesado no Cline apenas para uma pergunta simples. |

---

### 3. Dicas Práticas para o seu Cenário

* **Aproveite o Contexto do Gemini:** No seu print, você menciona a tarefa "Criar plano para unificar docs". O Gemini é perfeito aqui. Em vez de colar pedaços, use o `@ context` do Cline para dar o diretório inteiro de documentação para o Gemini 3.1 Pro. Ele conseguirá encontrar inconsistências entre os arquivos que modelos com contextos menores (como GPT-4) perderiam.
* **Auto-approve com Cuidado:** No print do Cline, você tem a opção de "Auto-approve". Para o Gemini 3.1 Pro, você pode deixar o **"Read (all)"** liberado, pois o custo é baixo e ele lê rápido, mas mantenha o **"Edit"** manual para garantir que a lógica esportiva do seu app de handebol permaneça correta.
* **Sincronia com o Plano Premium:** Como você tem o Google AI Pro, use o **Google AI Studio** para gerar chaves de API do Gemini 1.5 e 3.1 Pro. Isso permitirá que você use esses modelos dentro do Cline sem pagar por token extra (dentro do seu limite de assinatura).

**Gostaria que eu te ajudasse a configurar um "System Prompt" específico para o Cline agir como um especialista em sistemas esportivos/handebol?**