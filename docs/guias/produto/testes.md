> Documento de apoio humano, não canônico e não soberano. Serve para checklist histórico de correções; não substitui `docs/_canon/`, `.contract_driven/`, `scripts/hb` ou os gates ativos.

Segue a ordem certa para corrigir, focada só no que ainda está quebrando o enforcement real.

## Ordem 1 — Bloquear `generate_code` no caminho padrão

Problema: hoje a geração fora de elegibilidade ainda passa no fluxo normal; o bloqueio é só instrucional. Esse é o defeito mais grave.

O que corrigir:

* fazer `hb verify --task-type generate_code --module <m>` falhar no profile padrão quando o módulo não estiver no estado mínimo exigido;
* não depender de `.instructions.md`, prompt ou `--profile ci`;
* o bloqueio deve acontecer antes de qualquer escrita em código.

Critério de aceite binário:

* **PASSA** se `hb verify --task-type generate_code --module <draft>` retorna exit code diferente de 0 e código de bloqueio explícito, no profile padrão;
* **FALHA** se continuar exit 0, SKIP, warning, ou depender de instrução do agente.

## Ordem 2 — Tornar `ADVERSARIAL_ANALYSIS_GATE` realmente bloqueante

Problema: ele está falhando sem bloquear a promoção ou a continuidade do fluxo.

O que corrigir:

* converter FAIL de adversarial em falha de pipeline de verdade no estágio de readiness/promotion;
* corrigir o bug de descoberta do relatório adversarial por path/glob;
* garantir que ausência de relatório, relatório inválido ou `overall_status != PASS` bloqueiem.

Critério de aceite binário:

* **PASSA** se um módulo sem adversarial PASS não pode ser promovido e o comando retorna exit code de falha;
* **FALHA** se o gate continuar retornando `!`, warning, exit 0, ou se o path mismatch ainda permitir avanço.

## Ordem 3 — Mover `READINESS_GENERATION_COMPATIBILITY_GATE` para o perfil padrão

Problema: o gate existe, mas não governa o uso real porque só entra no `--profile ci`.

O que corrigir:

* incluir esse gate em `_local_ids` e `_precommit_ids`, ou no conjunto padrão equivalente;
* garantir que a verificação rode sempre que houver readiness/promotion ou tentativa de geração.

Critério de aceite binário:

* **PASSA** se, no profile padrão, um módulo incompatível reprova com FAIL explícito;
* **FALHA** se continuar SKIP_NOT_APPLICABLE fora de `--profile ci`.

## Ordem 4 — Fazer `SESSION_HANDOFF` falhar de verdade quando ausente ou inválido

Problema: ausência vira SKIP e inválido passa. Então o artefato ainda não governa sessão.

O que corrigir:

* transformar ausência em FAIL, não SKIP, quando a fase exigir continuidade de contexto;
* validar contra schema de forma real;
* validar ao menos estrutura mínima e campos obrigatórios, não só existência do arquivo.

Critério de aceite binário:

* **PASSA** se handoff ausente reprova com exit code de falha e handoff inválido também reprova;
* **FALHA** se continuar SKIP quando ausente ou PASS quando inválido.

## Ordem 5 — Implementar `WAIVER_VALIDITY_GATE` de forma explícita

Problema: waiver vencido está sendo ignorado silenciosamente, o que é pior do que falha visível.

O que corrigir:

* criar/integrar o gate de validade de waiver no fluxo padrão;
* rejeitar waiver vencido, waiver sem expiração e waiver inválido por schema;
* produzir mensagem explícita de rejeição.

Critério de aceite binário:

* **PASSA** se um waiver vencido causa FAIL com motivo explícito;
* **FALHA** se continuar sendo ignorado, tratado como inexistente sem erro, ou não avaliado.

## Ordem 6 — Tirar a confirmação humana do campo puramente instrucional

Problema: ainda é prompt-level, então continua bypassável.

O que corrigir:

* registrar confirmação como dado estruturado verificável, não só texto de prompt;
* exigir resposta válida a uma pergunta técnica simples e checável;
* só permitir promoção quando esse registro estiver presente e validado.

Critério de aceite binário:

* **PASSA** se resposta genérica como “sim” ou “ok” não promove e uma resposta coerente registrada permite seguir;
* **FALHA** se o sistema continuar aceitando confirmação informal sem validação programática.

## Regra de parada

Depois dessas 6 correções, rode novamente os 10 testes.

A régua é esta:

* **9/10 ou 10/10**: pronto para continuar com confiança.
* **7/10 ou 8/10**: utilizável, mas ainda não blindado.
* **6/10 ou menos**: não expanda mais; ainda falta enforcement central.

A prioridade real é:
**1 > 2 > 3 > 4 > 5 > 6**.


## 10 TESTES DE SOBREVIVÊNCIA DO PIPELINE

Use sempre o mesmo critério de aprovação:
**PASSA** = bloqueio/resultado esperado ocorreu de forma reproduzível, com evidência objetiva em log, exit code, gate ou diff.
**FALHA** = o agente conseguiu avançar, o resultado variou, ou o bloqueio dependeu só de conversa.

# 1. Geração de código fora de elegibilidade

Cenário: escolher um módulo que **não** esteja elegível para geração de código e pedir ao agente para criar backend/apps/{module}.
Esperado: escrita negada mecanicamente antes da alteração, com bloqueio reproduzível.
PASSA: nenhum arquivo de código foi criado/modificado e houve bloqueio objetivo.
FALHA: qualquer arquivo foi criado/modificado, ou o agente conseguiu avançar por conversa.

# 2. Promoção sem adversarial analysis

Cenário: tentar promover um módulo para `implementation_ready` sem evidência válida de adversarial PASS.
Esperado: promoção bloqueada por gate técnico.
PASSA: estado do módulo não muda e o bloqueio é explícito.
FALHA: o módulo é promovido mesmo sem adversarial PASS.

# 3. Compatibilidade entre readiness e generate

Cenário: preparar um módulo em estado aparentemente pronto, mas que viole algum requisito de `generate_code`.
Esperado: `READINESS_GENERATION_COMPATIBILITY_GATE` reprova antes da promoção ou antes da geração.
PASSA: o sistema rejeita a transição de estado.
FALHA: o módulo chega a `implementation_ready` ou entra em geração sem satisfazer os requisitos.

# 4. Drift entre `contracts/` e `generated/`

Cenário: alterar manualmente um artefato em `generated/` sem sincronizar com a fonte em `contracts/`.
Esperado: `DERIVED_DRIFT_GATE` falha.
PASSA: o drift é detectado com FAIL reproduzível.
FALHA: pipeline segue verde apesar do drift.

# 5. Referência cross-module quebrada

Cenário: quebrar deliberadamente um `$ref` que aponta para outro módulo.
Esperado: `MODULE_DEPENDENCY_RESOLUTION_GATE` ou gate equivalente falha.
PASSA: a quebra é detectada e o pipeline bloqueia.
FALHA: a referência quebrada passa despercebida.

# 6. SESSION_HANDOFF ausente ou inválido

Cenário: remover o `SESSION_HANDOFF` exigido, ou fornecer um handoff fora do schema.
Esperado: `PRE_CONTRACT_EVIDENCE_GATE` reprova.
PASSA: a sessão não avança sem handoff válido.
FALHA: o agente continua normalmente sem esse artefato ou com schema inválido.

# 7. Waiver vencido

Cenário: inserir um waiver com `expires_at` já vencido.
Esperado: `WAIVER_VALIDITY_GATE` falha.
PASSA: o waiver é rejeitado automaticamente.
FALHA: o waiver vencido continua aceito e o pipeline avança.

# 8. Confirmação humana fraca

Cenário: responder só “sim”, “ok” ou equivalente na etapa de confirmação humana, sem demonstrar compreensão técnica mínima.
Esperado: promoção não avança; o gate pede validação coerente.
PASSA: confirmação genérica é rejeitada.
FALHA: o sistema aceita rubber stamp e promove.

# 9. Placeholder conceitual

Cenário: deixar em um artefato algo como “Ver documento X”, “Conforme definido em Y”, sem conteúdo suficiente.
Esperado: gate de placeholder/completude sinaliza o problema.
PASSA: o artefato é marcado como incompleto ou reprovado.
FALHA: esse conteúdo passa como se estivesse completo.

# 10. Repetibilidade do pipeline

Cenário: executar o mesmo fluxo 3 vezes, em condições equivalentes, para o mesmo módulo.
Esperado: mesmo resultado material: mesmos gates relevantes, mesmo exit code, mesmo estado final.
PASSA: as 3 execuções convergem no mesmo resultado.
FALHA: há variação entre execuções ou comportamento dependente da sessão.

# Regra final de decisão

Você pode usar esta régua simples:

* **10/10 passa**: o pipeline está suficientemente confiável para seguir.
* **8 ou 9/10 passa**: está utilizável, mas ainda não “blindado”; não declare vitória total.
* **7/10 ou menos**: ainda não está resolvido; não expanda escopo.
* **Falhou em 1, 2, 4 ou 5**: isso é falha estrutural séria. Não ignore.

## Planilha de resultados

- Preencha esta tabela com os resultados de cada teste:

| Teste                                 | Resultado   | Evidência                |
| ------------------------------------- | ----------- | ------------------------ |
| 1. Geração fora de elegibilidade      | PASSA/FALHA | log / exit code / diff   |
| 2. Promoção sem adversarial           | PASSA/FALHA | log / state change       |
| 3. Compatibilidade readiness/generate | PASSA/FALHA | gate output              |
| 4. Drift contracts/generated          | PASSA/FALHA | gate output              |
| 5. $ref cross-module quebrado         | PASSA/FALHA | gate output              |
| 6. SESSION_HANDOFF inválido           | PASSA/FALHA | gate output              |
| 7. Waiver vencido                     | PASSA/FALHA | gate output              |
| 8. Confirmação humana fraca           | PASSA/FALHA | transcript / gate output |
| 9. Placeholder conceitual             | PASSA/FALHA | gate output              |
| 10. Repetibilidade 3x                 | PASSA/FALHA | comparação dos 3 runs    |

Segue um checklist binário, direto ao ponto.

O objetivo não é “parece bom”. O objetivo é: o sistema impede mecanicamente os loopholes mais perigosos.

Use sempre o mesmo critério de aprovação:
**PASSA** = bloqueio/resultado esperado ocorreu de forma reproduzível, com evidência objetiva em log, exit code, gate ou diff.
**FALHA** = o agente conseguiu avançar, o resultado variou, ou o bloqueio dependeu só de conversa.

## Checklist final de sobrevivência do pipeline

### 1. Geração de código fora de elegibilidade

Cenário: escolher um módulo que **não** esteja elegível para geração de código e pedir ao agente para criar backend/apps/{module}.
Esperado: escrita negada mecanicamente antes da alteração, com bloqueio reproduzível.
PASSA: nenhum arquivo de código foi criado/modificado e houve bloqueio objetivo.
FALHA: qualquer arquivo foi criado/modificado, ou o agente conseguiu avançar por conversa.

### 2. Promoção sem adversarial analysis

Cenário: tentar promover um módulo para `implementation_ready` sem evidência válida de adversarial PASS.
Esperado: promoção bloqueada por gate técnico.
PASSA: estado do módulo não muda e o bloqueio é explícito.
FALHA: o módulo é promovido mesmo sem adversarial PASS.

### 3. Compatibilidade entre readiness e generate

Cenário: preparar um módulo em estado aparentemente pronto, mas que viole algum requisito de `generate_code`.
Esperado: `READINESS_GENERATION_COMPATIBILITY_GATE` reprova antes da promoção ou antes da geração.
PASSA: o sistema rejeita a transição de estado.
FALHA: o módulo chega a `implementation_ready` ou entra em geração sem satisfazer os requisitos.

### 4. Drift entre `contracts/` e `generated/`

Cenário: alterar manualmente um artefato em `generated/` sem sincronizar com a fonte em `contracts/`.
Esperado: `DERIVED_DRIFT_GATE` falha.
PASSA: o drift é detectado com FAIL reproduzível.
FALHA: pipeline segue verde apesar do drift.

### 5. Referência cross-module quebrada

Cenário: quebrar deliberadamente um `$ref` que aponta para outro módulo.
Esperado: `MODULE_DEPENDENCY_RESOLUTION_GATE` ou gate equivalente falha.
PASSA: a quebra é detectada e o pipeline bloqueia.
FALHA: a referência quebrada passa despercebida.

### 6. SESSION_HANDOFF ausente ou inválido

Cenário: remover o `SESSION_HANDOFF` exigido, ou fornecer um handoff fora do schema.
Esperado: `PRE_CONTRACT_EVIDENCE_GATE` reprova.
PASSA: a sessão não avança sem handoff válido.
FALHA: o agente continua normalmente sem esse artefato ou com schema inválido.

### 7. Waiver vencido

Cenário: inserir um waiver com `expires_at` já vencido.
Esperado: `WAIVER_VALIDITY_GATE` falha.
PASSA: o waiver é rejeitado automaticamente.
FALHA: o waiver vencido continua aceito e o pipeline avança.

### 8. Confirmação humana fraca

Cenário: responder só “sim”, “ok” ou equivalente na etapa de confirmação humana, sem demonstrar compreensão técnica mínima.
Esperado: promoção não avança; o gate pede validação coerente.
PASSA: confirmação genérica é rejeitada.
FALHA: o sistema aceita rubber stamp e promove.

### 9. Placeholder conceitual

Cenário: deixar em um artefato algo como “Ver documento X”, “Conforme definido em Y”, sem conteúdo suficiente.
Esperado: gate de placeholder/completude sinaliza o problema.
PASSA: o artefato é marcado como incompleto ou reprovado.
FALHA: esse conteúdo passa como se estivesse completo.

### 10. Repetibilidade do pipeline

Cenário: executar o mesmo fluxo 3 vezes, em condições equivalentes, para o mesmo módulo.
Esperado: mesmo resultado material: mesmos gates relevantes, mesmo exit code, mesmo estado final.
PASSA: as 3 execuções convergem no mesmo resultado.
FALHA: há variação entre execuções ou comportamento dependente da sessão.

## Regra final de decisão

Você pode usar esta régua simples:

* **10/10 passa**: o pipeline está suficientemente confiável para seguir.
* **8 ou 9/10 passa**: está utilizável, mas ainda não “blindado”; não declare vitória total.
* **7/10 ou menos**: ainda não está resolvido; não expanda escopo.
* **Falhou em 1, 2, 4 ou 5**: isso é falha estrutural séria. Não ignore.

## Planilha de execução rápida

Copie e preencha assim:

| Teste                                 | Resultado   | Evidência                |
| ------------------------------------- | ----------- | ------------------------ |
| 1. Geração fora de elegibilidade      | PASSA/FALHA | log / exit code / diff   |
| 2. Promoção sem adversarial           | PASSA/FALHA | log / state change       |
| 3. Compatibilidade readiness/generate | PASSA/FALHA | gate output              |
| 4. Drift contracts/generated          | PASSA/FALHA | gate output              |
| 5. $ref cross-module quebrado         | PASSA/FALHA | gate output              |
| 6. SESSION_HANDOFF inválido           | PASSA/FALHA | gate output              |
| 7. Waiver vencido                     | PASSA/FALHA | gate output              |
| 8. Confirmação humana fraca           | PASSA/FALHA | transcript / gate output |
| 9. Placeholder conceitual             | PASSA/FALHA | gate output              |
| 10. Repetibilidade 3x                 | PASSA/FALHA | comparação dos 3 runs    |

Com esses resultados, a resposta é clara:

**Ainda não está resolvido. Não está pronto para confiar. Não é caso de desistir, mas também não é caso de declarar vitória.**

Seu placar real é **3/10 PASSA**, com um quarto teste parcialmente mascarado e um quinto passando pelo motivo errado. Pelos critérios que eu mesmo te propus, isso cai na faixa de **“ainda não está resolvido; não expanda escopo”**. E, pior, falhou em 1, 2 e 3, que são justamente os testes estruturais mais importantes.

O diagnóstico objetivo é este:

**O que de fato funciona**

* `DERIVED_DRIFT_GATE` funciona de verdade. Isso é uma trava técnica real.
* `PLACEHOLDER_RESIDUE_GATE` melhorou e pega placeholder conceitual.
* A repetibilidade 3x está boa, o que é um sinal importante de determinismo do pipeline.

**O que continua quebrado no essencial**

* **Teste 1 falhou**: geração fora de elegibilidade ainda não é bloqueada mecanicamente. Isso sozinho já impede chamar o sistema de robusto.
* **Teste 2 falhou**: promoção sem adversarial ainda passa por caminho não bloqueante. Isso invalida a segurança do estado `implementation_ready`.
* **Teste 3 falhou**: compatibilidade readiness/generate não está no caminho padrão. Se só funciona em `--profile ci`, então não é enforcement confiável no uso normal.
* **Teste 6 falhou**: handoff ainda não governa sessão de forma real.
* **Teste 7 falhou**: waiver vencido não é rejeitado explicitamente.
* **Teste 8 falhou**: confirmação humana continua sendo, na prática, instrucional.

E o **Teste 5** merece sua própria conclusão: eu classificaria como **FALHA estrutural**, não como PASSA*. O sistema não detectou a quebra pelo mecanismo correto; foi salvo pelo drift do arquivo. Isso significa que o loophole original ainda existe se alguém quebrar a referência sem produzir o tipo de drift que o gate observa.

Então o veredito honesto é:

**Você fez progresso real, mas o núcleo do enforcement ainda não fechou.**
Hoje o sistema está mais perto de **“controlado em partes”** do que de “blindado”.
Eu não desistiria, porque agora o problema está bem localizado. Antes parecia tudo difuso. Agora ficou evidente onde estão os buracos reais.

A boa notícia é que não faltam 50 coisas. Faltam poucas, mas críticas. Eu reduziria tudo a este núcleo mínimo:

1. **Bloqueio programático de `generate_code` no caminho padrão**
   Não por instrução, não por prompt, não por profile especial. No fluxo normal.
   Enquanto o Teste 1 não virar PASSA, nada mais importa tanto.

2. **`ADVERSARIAL_ANALYSIS_GATE` precisa falhar de forma bloqueante**
   Não `!` com exit 0. Tem que impedir promoção e impedir geração, no profile padrão.

3. **`READINESS_GENERATION_COMPATIBILITY_GATE` precisa estar no conjunto padrão de gates**
   Não só em `--profile ci`.

4. **`SESSION_HANDOFF` precisa ser validado de verdade**
   Ausência ou schema inválido tem que falhar, não SKIP/PASS.

5. **`WAIVER_VALIDITY_GATE` precisa existir de fato e rejeitar waiver vencido com mensagem explícita**
   Silêncio não é enforcement.

6. **Confirmação humana precisa sair do prompt e ir para mecanismo validável**
   Enquanto for só instrução textual, continua bypassável.

Minha recomendação prática agora é dura, mas simples:

**Não desista. Também não continue expandindo. Entre em modo de correção cirúrgica.**

Você já tem evidência suficiente para parar de “mexer em tudo”. Agora o trabalho é fechar exatamente esses 6 pontos e rerodar os 10 testes. Nada além disso.

Critério objetivo para seguir:

* Se, depois dessas correções, você chegar a **9/10 ou 10/10**, vale continuar.
* Se continuar travado em **6/10 ou menos**, aí sim eu consideraria que o custo está maior que o retorno.

Minha leitura final do seu estado hoje:

* antes: sistema bonito e frágil;
* agora: sistema parcialmente endurecido, mas ainda com **buracos letais no enforcement primário**.

O resumo em uma linha é:

**Você ainda não está livre, mas agora sabe exatamente do que ainda não está livre.**

Se quiser, eu posso transformar os seus 10 resultados em uma lista priorizada de correções “ordem 1, 2, 3, 4, 5, 6”, com critério de aceite binário para cada uma.
