# HB Track — Resumo Executivo do PRD
> Documento de apoio humano, não canônico e não soberano. Serve para resumo executivo histórico; não substitui `docs/_canon/`, `ROADMAP.md`, `docs/hbtrack/modulos/` ou o PRD normativo vigente.

> Data: 2026-03-19  
> Documento principal: `docs/guias/produto/PRD_OFICIAL_HB_TRACK.md`

## Resumo

O HB Track é uma plataforma unificada para handebol pensada para substituir um ecossistema fragmentado de planilhas, vídeo, scouting, comunicação dispersa e sistemas isolados. A visão de longo prazo cobre treino, jogo, vídeo, performance, competição e mídia. O ponto de entrada recomendado, porém, é mais estreito: comissão técnica e operação esportiva.

O MVP deve provar uma tese simples e verificável: um clube consegue trocar 3 a 4 ferramentas por uma só, reduzir o retrabalho da comissão técnica e acelerar análise pós-jogo e preparação de adversário. Para isso, o pacote inicial precisa focar em identidade e permissões, cadastros esportivos, planejamento de treino, vídeo, tagging manual de handebol, match ops básico, relatórios e distribuição interna.

## O que está decidido

- A visão de produto é de plataforma end-to-end para handebol.
- O mercado primário inicial é handebol indoor, com entrada mais viável por clubes e comissões técnicas.
- O roadmap é progressivo:
  `Coach/MVP` -> `Performance/V2` -> `League/V3`.
- Treino, vídeo, scout, relatório e adversário formam o núcleo de valor do MVP.
- Wellness, medical, analytics e IA consultiva pertencem à V2.
- Competição institucional, live stats públicos, APIs e mídia pertencem à V3.

## O que bloqueia o avanço

- O módulo `video` é essencial para o MVP, mas não existe formalmente no registry atual.
- `matches`, `scout` e `reports` ainda precisam sair de stubs contratuais.
- Há conflito documental sobre a stack backend oficial.
- Há conflito documental sobre o readiness do módulo `training`.

## Recomendação executiva

Congelar o MVP como `HB Track Coach`, resolver primeiro os gaps estruturais de `video`, `matches`, `scout` e `reports`, e só então iniciar implementação. Comunicação estruturada e IA conversacional para atleta devem ser tratadas como extensão posterior, salvo decisão formal em contrário.

## MVP proposto

- Usuários: treinador principal, auxiliar, analista de desempenho, analista de vídeo, scout.
- Escopo: auth, cadastros, treino, vídeo, tagging, live ops básico, relatório pós-jogo, dossiê pré-jogo, distribuição interna.
- Critério de sucesso: substituição de 3 a 4 ferramentas, redução real de tempo operacional e adoção recorrente pela comissão técnica.

## Principais perguntas em aberto

1. Quando o módulo `video` será criado formalmente?
2. O requisito de comunicação estruturada entra em qual fase?
3. A IA conversacional do atleta será apenas coach esportivo ou também apoio emocional?
4. Offline no scout ao vivo é obrigatório no MVP?
5. Quais metas numéricas oficiais serão usadas no piloto?
