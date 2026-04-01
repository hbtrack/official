> Documento de apoio humano, não canônico e não soberano. Serve para backlog histórico de melhorias; não substitui `ROADMAP.md`, `docs/_canon/`, `.contract_driven/` ou o handoff operacional.

## BACKLOG DE MELHORIAS E TESTES RECOMENDADOS

A lógica é simples: prioridade alta é o que ainda pode reabrir buraco real. Prioridade média melhora confiança operacional. Prioridade baixa melhora governança e legibilidade, mas não muda o núcleo de segurança do pipeline.

## Prioridade alta

**1. Executar de verdade os validadores externos no caminho padrão**
Hoje parte da confiança ainda depende de contexto local e, em alguns cenários, gates entram como SKIP por falta de tooling externo.
Critério de pronto: AsyncAPI, OpenAPI/lint e gates correlatos rodam de fato no ambiente padrão que você usa para validar, não só em CI ou ambientes especiais.


**2. Teste real de revalidação cross-module com dependência quebrada**
Você já validou o núcleo, mas precisa um caso real e reproduzível em que um módulo dependente falha quando outro muda.
Critério de pronto: alterar um contrato base quebra o dependente e o pipeline reprova pelo mecanismo esperado, com evidência clara.

**3. Congelar a suíte de sobrevivência como gate obrigatório de regressão**
Essa é a proteção mais importante agora. Sem isso, alguém mexe no pipeline e reabre falhas.
Critério de pronto: os 12 testes de sobrevivência viram rotina obrigatória antes de aceitar mudança em gates, profiles, schemas, task catalog ou validação.

**4. Confirmar que todos os gates críticos rodam no profile padrão correto**
Você já resolveu vários, mas vale uma auditoria curta de profile para não ficar nada importante preso em `ci` ou `precommit` apenas.
Critério de pronto: lista fechada dos gates críticos com mapeamento explícito para o profile padrão real de uso.

## Prioridade média

**5. Auditar qualidade semântica dos contratos só nos pontos de domínio críticos**
Não é revisar tudo. É pegar regras de domínio que causariam dano se faltassem: autenticação, restrições de fluxo, invariantes, janelas de edição, controles sensíveis.
Critério de pronto: checklist curto por módulo crítico, com evidência de que essas regras aparecem nos contratos corretos.

**6. Verificar SLAs declarativos onde eles realmente importam**
Só para módulos live ou sensíveis a latência. Não espalhe isso para tudo.
Critério de pronto: os módulos relevantes declaram SLA onde a governança já exige.

**7. Confirmar cobertura mínima de superfícies declaradas vs superfícies esperadas**
Especialmente onde há `expected_surfaces`. Isso evita módulo “pronto” sem superfície que ele próprio declarou.
Critério de pronto: nenhuma divergência aberta entre `expected_surfaces` e artefatos reais.

**8. Fechar o caso de Arazzo apenas com regra simples**
Não tente sofisticar. Só defina claramente quando é obrigatório e quando não é.
Critério de pronto: ausência de ambiguidade. Nada além disso.

## Prioridade baixa

**9. Melhorar relatórios para leitura humana**
Isso ajuda manutenção, mas não aumenta enforcement central.
Critério de pronto: relatório mostra claramente gates ativos, skips, bloqueadores e causa da falha.

**10. Refinar heurísticas de placeholder conceitual**
Útil, mas já não é o ponto mais arriscado.
Critério de pronto: menos falsos positivos sem perder detecção útil.

**11. Consolidar documentação operacional curta**
Uma página só: “como validar, como promover, como bloquear, como rerodar a suíte”.
Critério de pronto: alguém consegue operar o pipeline sem reler todo o sistema normativo.

**12. Limpar ou arquivar regras/documentos que ficaram redundantes**
Agora que o enforcement melhorou, parte do texto antigo pode ter virado peso morto.
Critério de pronto: menos duplicação, sem perda de fonte normativa.

## Regra prática para não inflar o sistema

Só aceite item novo no backlog se ele responder “sim” para uma destas perguntas:

* isso fecha um loophole real?
* isso evita regressão de algo que já foi corrigido?
* isso remove ambiguidade operacional importante?

Se a resposta for “não”, provavelmente é cosmético e deve ficar de fora.

## Ordem recomendada

Faça nesta sequência:
**1 → 2 → 3 → 4 → 5 → 7 → 6 → 8 → 9 → 10 → 11 → 12**

Em uma frase: **agora o foco não é adicionar complexidade; é garantir execução real, revalidação real e proteção contra regressão.**
