<!-- TEMPLATE: global-canon-template | DEST: docs/_canon/C4_CONTAINERS.md | SOURCE: .contract_driven/templates/globais/C4_CONTAINERS.md -->

# C4_CONTAINERS.md

## Objetivo
Descrever os containers principais de `{{PROJECT_NAME}}`.

```mermaid
flowchart TB
  user["Usuários"]

  subgraph platform["{{PROJECT_NAME}}"]
    web["Web App / Frontend"]
    api["API Backend"]
    db["Banco de Dados"]
    files["Armazenamento de Arquivos"]
    jobs["Workers / Jobs"]
  end

  extNotif["Serviço de Notificação"]
  extBroker["Broker/Event Bus"]

  user --> web
  web --> api
  api --> db
  api --> files
  api --> jobs
  jobs --> db
  api --> extNotif
  jobs --> extBroker
```

## Containers
### Web App / Frontend
- Responsabilidade: interface do usuário
- Entrada: contratos OpenAPI / tipos gerados
- Saída: chamadas HTTP / upload / comandos do usuário

### API Backend
- Responsabilidade: regras de aplicação e exposição dos contratos HTTP
- Entrada: requests, autenticação, payloads
- Saída: responses, eventos, persistência

### Banco de Dados
- Responsabilidade: persistência transacional

### Armazenamento de Arquivos
- Responsabilidade: anexos, mídia, relatórios

### Workers / Jobs
- Responsabilidade: tarefas assíncronas, cálculos, integrações

## Relações Críticas
- Frontend consome apenas contratos públicos
- Backend implementa contratos
- Jobs não alteram semântica pública sem contrato

## Observações
- Adicionar componentes internos em ADR ou documentação específica quando necessário
