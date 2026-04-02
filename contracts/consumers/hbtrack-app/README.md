# Consumer Contracts — hbtrack-app

## O que é isso?

Este diretório marca `hbtrack-app` como consumer registrado da API HB Track.
Os arquivos de contrato gerados pelo app (`.json` do Pact) **não ficam aqui** —
eles são publicados diretamente no Pact Broker (VPS Locaweb).
O provider canônico desta integração é `hbtrack-api`.

## Como gerar o consumer contract

1. O frontend do monorepo roda a suíte Pact bootstrap em `frontend/src/api/__tests__/hbtrack.consumer.pact.test.ts`
2. Os testes geram automaticamente `frontend/pacts/*.json`
3. O publish local/CI usa `scripts/contracts/pact/publish_frontend_pacts.py`
4. O CI do app publica esse arquivo no Pact Broker:
   ```
   python3 scripts/contracts/pact/publish_frontend_pacts.py
   ```

Equivalente via CLI:

```bash
pact-broker publish ./frontend/pacts \
     --consumer-app-version <version> \
     --broker-base-url $PACT_BROKER_BASE_URL \
     --branch <git-branch> \
     --broker-token $PACT_BROKER_TOKEN
```

## Como verificar o provider

O deploy de staging usa `scripts/contracts/pact/verify_staging_provider.py`, que:

1. consulta o broker para saber se `hbtrack-app` já publicou o primeiro pact
2. se sim, executa `pact-provider-verifier` contra `hbtrack-api`
3. publica os verification results do provider
4. permite que `PACT_PROVIDER_GATE` deixe o estado `SKIP_NOT_APPLICABLE`

## Pact Broker

- **Tipo:** Auto-hospedado (Docker) na VPS Locaweb
- **Configuração:** ver `VPS/` e ADR-025
- **Env vars necessárias:** `PACT_BROKER_BASE_URL`, `PACT_BROKER_TOKEN`
- **Provider name:** `hbtrack-api`

## Referências

- `docs/_canon/decisions/ADR-025-cdct-pact-strategy.md`
- `PACT_PROVIDER_GATE` no pipeline CI
