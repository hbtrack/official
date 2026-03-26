# contracts/asyncapi/

Fonte primária da verdade para **contratos de eventos assíncronos** no HB Track.

## Estrutura

```
contracts/asyncapi/
  asyncapi.yaml       # Documento raiz AsyncAPI (entrypoint)
  channels/           # Definições de canais de mensagem
  operations/         # Definições de operações (publish/subscribe)
  messages/           # Definições de mensagens
  components/
    schemas/          # Schemas de payload de eventos
    messageTraits/    # Traits reutilizáveis de mensagem
    operationTraits/  # Traits reutilizáveis de operação
```

## Regras de uso

- **Soberania**: `contracts/asyncapi/asyncapi.yaml` é a única fonte de verdade para contratos de eventos. Nenhum event handler ou consumer pode definir shape de evento fora deste contrato.
- **Condição de criação**: artefatos AsyncAPI só devem existir quando houver eventos reais publicados ou consumidos pelo sistema. Não criar arquivos AsyncAPI como placeholders.
- **Entrypoint obrigatório**: `asyncapi.yaml` na raiz de `contracts/asyncapi/` é o documento raiz. Channels, operations e messages podem ser fatorados em subpastas quando o documento crescer.
- **Naming**: arquivos em `channels/`, `operations/` e `messages/` devem usar `lower_snake_case`.
- **Validação obrigatória**: todo contrato AsyncAPI deve ser validável por um AsyncAPI parser/validator antes de ser considerado pronto.

## Estado atual

`asyncapi.yaml` (entrypoint raiz) existe e documenta ao menos 1 evento real do módulo `training`.
Validação por AsyncAPI parser/validator é obrigatória para considerar o contrato pronto (Gate 12).

## Referências normativas

- Layout canônico: `.contract_driven/CONTRACT_SYSTEM_LAYOUT.md` seções 4 e 9
- Matriz de aplicabilidade: `.contract_driven/CONTRACT_SYSTEM_RULES.md` seção 11.7
- Gates e ferramentas de validação: `docs/_canon/CI_CONTRACT_GATES.md`
