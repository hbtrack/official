# Consumer Contracts — hbtrack-app

## O que é isso?

Este diretório marca `hbtrack-app` como consumer registrado da API HB Track.
Os arquivos de contrato gerados pelo app (`.json` do Pact) **não ficam aqui** —
eles são publicados diretamente no Pact Broker (VPS Locaweb).

## Como gerar o consumer contract

1. O app roda seus testes de integração com a biblioteca Pact (Pact JS / Pact Swift / etc.)
2. Os testes geram automaticamente um arquivo `.json` de contrato
3. O CI do app publica esse arquivo no Pact Broker:
   ```
   pact-broker publish ./pacts \
     --consumer-app-version <version> \
     --broker-base-url $PACT_BROKER_BASE_URL \
     --broker-token $PACT_BROKER_TOKEN
   ```

## Pact Broker

- **Tipo:** Auto-hospedado (Docker) na VPS Locaweb
- **Configuração:** ver `VPS/` e ADR-025
- **Env vars necessárias:** `PACT_BROKER_BASE_URL`, `PACT_BROKER_TOKEN`

## Referências

- `docs/_canon/decisions/ADR-025-cdct-pact-strategy.md`
- `PACT_PROVIDER_GATE` no pipeline CI
