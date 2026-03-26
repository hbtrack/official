# Manual Operacional de Criação de Vídeo com Codex

## 1. Propósito

Este manual define o fluxo operacional mínimo para produzir o vídeo com Codex sem ambiguidade de stack, sem depender de limites mensais de SaaS e sem ultrapassar o teto vitalício de `R$ 70,00`.

Ele corrige duas classes de pendência:

1. Pendências documentais.
   O manual anterior não estava materializado no workspace atual e referenciava artefatos que hoje não existem localmente.
2. Pendências operacionais.
   O orçamento estava modelado com margem pequena demais para câmbio, spread e erro humano. Isso tornava insegura a regra de `3 retries de 8s`.

## 2. Decisão Canônica do Projeto

### 2.1 Stack canônica

- Geração visual paga: `Veo 3.1 Fast` via `Vertex AI API`
- Resolução: `1080p`
- Proporção: `16:9`
- Áudio na geração: `não`
- Comprimentos permitidos por request: `4s`, `6s`, `8s`
- Idioma do prompt final enviado ao Veo: `inglês`
- TTS: `Piper` local
- Montagem: `FFmpeg`
- Acabamento opcional: `DaVinci Resolve Free`

### 2.2 Nomenclatura canônica

- `plano_cenas.csv`
- `config_video.json`
- `prompts_video.md`

### 2.3 Arquivos opcionais fora do MVP

- `prompt_base.json`
- arquivos por motor
- `prompt_map.csv`
- `concat_list.txt`

## 3. Causa Real das Pendências

### 3.1 Pendência de estrutura

No estado atual do workspace em `2026-03-23`, os seguintes problemas existem:

- `.CEPRAEA` estava sem o manual operacional materializado
- `projeto_video/` não está presente no workspace atual
- `ffmpeg` não está instalado no ambiente atual
- `piper` não está instalado no ambiente atual

Impacto:

- o manual não podia ser executado no mundo real como runbook
- o pipeline não tinha preflight local para travar falhas antes do gasto
- a ausência do diretório fonte impedia validar os insumos de roteiro, prompts e assets

### 3.2 Pendência de orçamento

A modelagem anterior considerava:

- `108s` de geração base
- `24s` extras de retry
- total de `132s`

Isso funcionava com câmbio de referência muito justo, mas não era uma trava robusta para um teto vitalício de `R$ 70,00`.

Motivo técnico:

- o custo real é em `USD`
- a conversão para `BRL` varia
- pode existir spread ou diferença de faturamento
- `132s` deixam pouca margem de segurança

## 4. Correção Aplicada

### 4.1 Novo guardrail financeiro

O teto operacional passa a ser controlado por `segundos pagos máximos`, e não por contagem informal de tentativas.

Parâmetros canônicos:

- teto vitalício em reais: `R$ 70,00`
- taxa operacional conservadora para travamento: `R$ 5,80 / US$ 1,00`
- custo operacional travado do Veo Fast: `R$ 0,58 por segundo`
- máximo absoluto de geração paga autorizada: `120s`

Fórmula:

- `120s x US$ 0,10/s = US$ 12,00`
- `US$ 12,00 x R$ 5,80 = R$ 69,60`

Resultado:

- o pipeline passa a parar antes de ultrapassar `R$ 70,00`
- a margem remanescente é de `R$ 0,40`

### 4.2 Ajuste obrigatório da política de retries

A regra anterior de `3 retries de 8s` foi substituída.

Nova regra canônica:

- geração base autorizada: `108s`
- reserva total de retry pago: `12s`
- total máximo faturável: `120s`

Aplicação recomendada da reserva:

- `M1-02`: `1` retry de `4s`
- `M2-03`: `1` retry de `4s`
- `EN-03`: `1` retry de `4s`

Motivo da correção:

- preserva as 3 cenas mais sensíveis
- mantém o teto financeiro travado
- usa comprimentos suportados pelo Veo Fast

Se for necessário um retry de `6s` ou `8s`, ele deverá consumir a mesma reserva total de `12s` e reduzir a quantidade de retries em outras cenas.

## 5. Escopo Pago e Escopo Não Pago

### 5.1 Escopo pago autorizado

O escopo pago autorizado permanece:

- somente as `13` cenas estritamente realistas no `Veo 3.1 Fast`

### 5.2 Escopo não pago

Permanece fora do Veo:

- `M4-02`: `motion design + base realista opcional`
- `M7-03`: `motion design + base realista opcional`
- demais blocos narrativos sustentados por motion design, texto em tela, reaproveitamento e edição

## 6. Artefatos Canônicos Criados por Esta Correção

Este manual passa a ser acompanhado por:

- `.CEPRAEA/video_pipeline/config_video.json`
- `.CEPRAEA/video_pipeline/cenas_premium_autorizadas.csv`
- `.CEPRAEA/video_pipeline/logs/geracao_log.csv`
- `.CEPRAEA/video_pipeline/logs/render_log.txt`
- `.CEPRAEA/video_pipeline/scripts/preflight_pipeline.py`
- `.CEPRAEA/video_pipeline/scripts/verificar_orcamento.py`

Esses arquivos resolvem a lacuna anterior entre documentação e execução.

## 7. Fluxo Operacional Ponta a Ponta

### 7.1 Preflight obrigatório

Antes de qualquer gasto:

1. Executar `python3 .CEPRAEA/video_pipeline/scripts/preflight_pipeline.py`
2. Corrigir todos os bloqueios retornados
3. Executar `python3 .CEPRAEA/video_pipeline/scripts/verificar_orcamento.py`
4. Antes de cada request pago, simular a proxima chamada com `python3 .CEPRAEA/video_pipeline/scripts/verificar_orcamento.py --next-scene SCENE_ID --next-seconds N`
5. Confirmar que o total projetado permanece abaixo do teto

Nenhuma chamada paga ao Veo deve ocorrer antes de os dois validadores passarem.

### 7.2 Geração visual

Para cada cena paga:

1. partir do roteiro e do prompt técnico
2. converter o prompt final para inglês
3. simular previamente o gasto com `--next-scene` e `--next-seconds`
4. escolher somente `4s`, `6s` ou `8s`
5. registrar a chamada em `logs/geracao_log.csv`
6. reexecutar `verificar_orcamento.py`

Regra de ouro:

- se o validador reprovar, a geração para imediatamente

### 7.3 Narração

Fluxo canônico:

1. gerar narração localmente com `Piper`
2. armazenar o arquivo de voz em diretório de assets do projeto real
3. manter `R$ 0,00` de custo nessa etapa

### 7.4 Montagem

Fluxo canônico:

1. usar `FFmpeg` para compor clipes, locução e legendas
2. gerar primeiro uma versão de revisão
3. só depois gerar `video_final.mp4`

### 7.5 Acabamento opcional

Somente se necessário:

1. abrir a versão de revisão no `DaVinci Resolve Free`
2. fazer ajuste fino de ritmo, cor ou áudio
3. exportar a versão final sem alterar o orçamento pago de geração

## 8. Requisitos Técnicos Reais

### 8.1 Obrigatórios

- `Python 3`
- `FFmpeg` instalado e acessível no `PATH`
- `Piper` instalado e acessível no `PATH`
- variáveis de ambiente do `Vertex AI` configuradas
- diretório fonte do projeto de vídeo presente
- logs obrigatórios presentes

### 8.2 Não obrigatórios

- `DaVinci Resolve Free`
- `jq`

Correção aplicada:

- os scripts auxiliares desta versão não dependem de `jq`

## 9. Critérios Operacionais de Sucesso

O pipeline só é considerado apto quando:

1. o preflight retornar `OK`
2. o validador de orçamento retornar `OK`
3. nenhum request pago fora da allowlist ocorrer
4. o acumulado pago permanecer em `120s` ou menos
5. o projeto gerar uma versão de revisão antes do render final

## 10. Condições de Falha

O pipeline deve ser interrompido se qualquer uma destas condições ocorrer:

- `ffmpeg` ausente
- `piper` ausente
- `GOOGLE_CLOUD_PROJECT` ausente
- `GOOGLE_APPLICATION_CREDENTIALS` ausente ou apontando para arquivo inexistente
- `VERTEX_LOCATION` ausente
- `projeto_video/` ausente
- falta de qualquer arquivo-fonte obrigatório
- request pago para cena fora da allowlist
- request pago acima do número máximo de tentativas por cena
- projeção de custo acima de `R$ 70,00`
- total pago acima de `120s`

## 11. Estado do Workspace em 2026-03-23

Validação local realizada neste workspace:

- `ffmpeg`: ausente
- `piper`: ausente
- `python3`: presente
- `.CEPRAEA`: recriado com artefatos operacionais
- `projeto_video/`: ausente no estado atual

Interpretação:

- o manual foi corrigido
- o runbook local foi criado
- mas o ambiente ainda não está pronto para execução real até que as dependências e os arquivos-fonte sejam restaurados

## 12. Pendências Remanescentes do Mundo Real

Estas pendências não são mais de decisão; são de implantação:

1. restaurar ou recriar `projeto_video/`
2. instalar `ffmpeg`
3. instalar `piper`
4. configurar credenciais reais do `Vertex AI`
5. executar o preflight novamente
6. só então iniciar a geração paga

## 13. Veredito Operacional

O manual agora está operacionalmente correto para o cenário definido, porque:

- fixa a stack canônica
- remove ambiguidades de custo
- transforma o orçamento em trava verificável
- materializa artefatos de controle
- bloqueia execução quando o ambiente não estiver apto

O que continua faltando não é desenho do pipeline. É implantação local do ambiente e restauração dos arquivos-fonte do projeto.
