---
doc_type: guide
version: "1.0.0"
status: derived_reference
created_at: "2026-03-17"
---

# UNBLOCKING_PLAYBOOK.md
## Guia de Primeiros Socorros — Pipeline Travado

> Documento de apoio humano, não canônico e não soberano. Serve como playbook auxiliar de desbloqueio; não substitui `docs/_canon/AGENT_INSTRUCTIONS.md`, `scripts/hb`, `scripts/contracts/validate/validate_contracts.py` ou `_reports/contract_gates/latest.json`.

> Use este guia quando algo travar no desenvolvimento do HB Track.
> Nenhum jargão técnico — se precisar de mais contexto, pergunte para a IA em português.

---

## Sintoma: "CI falhou mas não sei por quê"

1. Abrir `_reports/contract_gates/latest.json`
2. Procurar entradas com `"status": "FAIL"`
3. Copiar o `gate_id` e perguntar para a IA: "O gate [X] falhou. O que preciso fazer?"

A IA vai traduzir o problema para linguagem de produto e indicar a próxima ação.

---

## Sintoma: "A IA travou com um código BLOCKED_*"

Ver tabela de bloqueios em `docs/_canon/AGENT_INSTRUCTIONS.md` §5. Cada código tem uma ação clara.

Exemplos rápidos:
| Código | O que significa em português | O que fazer |
|--------|------------------------------|-------------|
| `BLOCKED_MISSING_MODULE` | A funcionalidade pedida não pertence a nenhum dos 16 módulos do sistema | Pedir para a IA sugerir em qual módulo encaixa |
| `BLOCKED_REQUIRED_ARTIFACT_MISSING` | Falta um documento obrigatório para esse módulo | Perguntar "Qual documento está faltando e como crio?" |
| `BLOCKED_MISSING_ARCH_DECISION` | Uma decisão de produto não foi tomada ainda | Verificar `SESSION_HANDOFF.md` — seção "Decisões Pendentes" |
| `BLOCKED_ADVERSARIAL_PENDING` | A análise de segurança do módulo não foi feita | Pedir para a IA executar a análise adversarial |
| `BLOCKED_HANDOFF_INCOMPLETE` | O módulo não está pronto para começar a gerar código | Perguntar "O que falta para o módulo X estar pronto?" |

Para qualquer outro código: copiar o código e perguntar para a IA "O que significa [CÓDIGO] e como desbloquear?"

---

## Sintoma: "Não sei o que foi decidido na sessão anterior"

Abrir `SESSION_HANDOFF.md` na raiz do projeto.

Se não existir: pedir para a IA "Crie um SESSION_HANDOFF.md com o estado atual do projeto."

O arquivo contém:
- O que foi feito nas últimas sessões
- Próximos passos em ordem de prioridade
- Decisões que você ainda precisa tomar
- Bloqueios ativos

---

## Sintoma: "Quero adicionar uma nova funcionalidade mas não sei como"

Dizer para a IA: **"Quero adicionar [funcionalidade em português]. Qual é o módulo certo e o que preciso fazer?"**

A IA vai:
1. Identificar o módulo correto nos 16 módulos canônicos
2. Verificar se os documentos necessários existem
3. Rodar o processo de contrato automaticamente
4. Informar se precisar de alguma decisão sua

Você não precisa saber nada sobre contratos, schemas ou endpoints.

---

## Sintoma: "Perdi o fio da meada — muito arquivo, não sei o que é o quê"

Pedir para a IA: **"Me dê um resumo do estado atual do projeto em linguagem de produto."**

A IA vai ler `SESSION_HANDOFF.md` + `docs/_canon/FEATURE_REGISTRY.yaml` e responder em português claro, mostrando:
- Quais funcionalidades estão prontas
- Quais estão em andamento
- O que está esperando uma decisão sua
- O que vem a seguir

---

## Sintoma: "O CI estava passando e agora falhou sem eu mudar nada"

Possíveis causas:
1. Um arquivo foi modificado por engano — verificar `git status`
2. Uma dependência mudou — perguntar para a IA "O CI falhou. Veja o relatório em `_reports/contract_gates/latest.json` e me explique o que aconteceu."
3. Um contrato ficou desatualizado em relação ao schema — a IA vai identificar e corrigir

---

## Sintoma: "Não sei em que fase estamos do pipeline"

Abrir `pipeline.md` na raiz. As fases com `[x]` estão concluídas, as com `[ ]` ainda estão pendentes.

Ou perguntar: **"Em que fase do pipeline estamos? O que falta para a próxima fase?"**

---

## Sintoma: "A IA criou um arquivo no lugar errado"

Verificar o path correto em `docs/_canon/AGENT_INSTRUCTIONS.md` §8. Pedir para a IA "Mova o arquivo [X] para o path correto."

Se não souber o path correto: perguntar "Onde deveria estar o arquivo [nome do arquivo]?"

---

## Referências rápidas

| O que preciso | Onde encontrar |
|---------------|---------------|
| Estado atual do projeto | `SESSION_HANDOFF.md` |
| Quais funcionalidades existem | `docs/_canon/FEATURE_REGISTRY.yaml` |
| Resultado do último CI | `_reports/contract_gates/latest.json` |
| Relatório de features | `_reports/feature_readiness.json` |
| Decisões tomadas (ADRs) | `docs/_canon/decisions/` |
| Regras do sistema de contratos | `docs/_canon/AGENT_INSTRUCTIONS.md` |
| Bloqueios e seus significados | `docs/_canon/AGENT_INSTRUCTIONS.md` §5 |
| Arquitetura do código | `docs/_canon/CODE_ARCHITECTURE.md` |
| Política de deploy | `docs/_canon/DEPLOY_PIPELINE.md` |
| Monitoramento em produção | `docs/_canon/RUNTIME_CONTRACT_MONITORING_POLICY.md` |
