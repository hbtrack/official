# ADR-019: Separação Estrita de Camadas — Domain / DTO / ViewModel / Props

- Status: Accepted
- Date: 2026-03-16
- Deciders: Equipe HB Track
- Tags: architecture, layers, dto, viewmodel, domain-model, platform
- Promotes: TRAIN-DEC-032, TRAIN-DEC-033, TRAIN-DEC-034, TRAIN-DEC-035
- Source: `DTO_VIEWMODEL_BOUNDARY_RULES.md`

---

## Context

Sem separação explícita de camadas, sistemas de médio prazo degenedam de formas previsíveis:

- **DTOs inflados para satisfazer telas**: o backend passa a exportar campos de apresentação (`start_label: "Amanhã às 08h"`) que acoplam o contrato ao idioma e fuso da tela.
- **Modelo de domínio moldado por UI**: entidades de negócio ganham campos adicionais para conveniência de renderização, tornando o domínio impuro.
- **ViewModel como contrato de backend**: o frontend começa a depender de estruturas que deveriam ser efêmeras, quebrando quando o domínio evolui.
- **Payload de provedor vazando para o domínio**: campos com nomenclatura nativa de provedores externos (`catapult_session_id`, `polar_hrv_raw`) aparecem em entidades canônicas.

O HB Track integra dados de dispositivos externos, serve múltiplas superfícies de UI (web, mobile, agente), e tem um modelo de domínio rico com invariantes fortes. Sem separação de camadas, essas tensões tornam o sistema frágil.

---

## Decision

O HB Track mantém separação **estrita e não intercambiável** entre quatro camadas:

### Camadas e responsabilidades

| Camada | Responsabilidade | Proibido |
|---|---|---|
| **Modelo de Domínio** | Invariantes de negócio, ciclo de vida, regras semânticas, agregados | Adaptar-se a conveniências de renderização; carregar campos de provedores externos; vazar estruturas de persistência |
| **DTO de API** | Contrato de transporte versionável entre backend e frontend/agente | Expor entidade de BD diretamente; carregar strings de apresentação; expor payload bruto de provedor |
| **ViewModel** | Composição e formatação específica de tela/contexto | Tornar-se contrato canônico de backend; ser fonte de verdade; acumular lógica de negócio |
| **Props de Componente UI** | Limite mínimo de renderização do componente | Carregar bagagem de transporte/domínio não relacionada; conter lógica de negócio |

### Fluxo canônico obrigatório

```
Fonte externa / Input do usuário
→ Contrato de Ingestão (normalização canônica)
→ Lógica de Domínio (invariantes, transições, regras)
→ DTO de API (contrato versionável de transporte)
→ ViewModel (composição específica de tela)
→ Props de Componente de UI (limite de renderização)
→ UI Renderizada
```

Simplificação de camada só é permitida quando a camada omitida **genuinamente não existe** como preocupação separada — e deve ser justificada explicitamente.

### Regras de DTO de API

DTOs não devem expor:
- Estrutura de tabelas de junção internas ou nomenclatura de FK
- Colunas de soft-delete (`deleted_at`, `deleted_reason`) como campos de primeiro nível em respostas de listagem
- Formato bruto de armazenamento de event store
- Strings de apresentação formatadas (`"Amanhã às 08:00"`, `"1h 30min"`)

DTOs devem carregar **valores semânticos**:
- Correto: `scheduledStartAt: "2026-03-20T19:30:00Z"`, `plannedDurationMinutes: 90`
- Errado: `startLabel: "Amanhã às 08:00"`, `durationLabel: "1h 30min"`

### Regras de ViewModel

ViewModels de telas de treino não devem colapsar distinções de status do domínio em campos genéricos quando a UI ainda precisa delas.

As distinções canônicas (`DRAFT`, `SCHEDULED`, `PUBLISHED`, `IN_PROGRESS`, `COMPLETED`, `CANCELLED`, `ARCHIVED`) devem ser preservadas upstream e derivadas conscientemente para badges ou labels de exibição — **nunca substituídas** por `"active"` genérico no ViewModel.

### Regras de modelo de domínio

O modelo de domínio (agregados `TrainingSession`, `SessionBlock`, `ExecutionRecord`, etc.) não deve ser moldado por:
- Necessidades de renderização de tela específica
- Particularidades de payload de provedores externos (Catapult, Polar, Statsports)

O modelo de domínio pode ser **mais rico** do que os DTOs de API e conter invariantes internas não expostas ao cliente.

---

## Consequences

### Positive

- Refatorações de domínio não quebram contratos de API — as camadas são buffers independentes.
- Telas evoluem (novo layout, nova plataforma) sem alterar contratos de backend.
- Modelo de domínio permanece puro e testável independentemente de UI e provedores.
- Agentes de IA que consomem DTOs não acumulam dependências de apresentação.

### Negative

- Custo inicial de modelagem mais alto — cada funcionalidade requer pensar em qual camada o dado pertence.
- Risco de over-engineering em features simples — a regra de simplificação explícita mitiga isso.

---

## Alternatives Considered

- **DTO = Entidade de domínio direta**: rejeitado — acopla contrato externo ao modelo interno; toda refatoração interna quebra clientes.
- **ViewModel como contrato de backend**: rejeitado — ViewModels mudam com frequência de tela para tela; tratar como contrato gera instabilidade.
- **Camada única "modelo universal"**: rejeitado — leva à degradação observada em sistemas legados (DTOs inflados, modelo impuro, acoplamento UI-backend).

---

## Links

- Related docs: `docs/hbtrack/decisoes/ARCH_DECISIONS_TRAINING.md` (TRAIN-DEC-032, TRAIN-DEC-033, TRAIN-DEC-034, TRAIN-DEC-035)
- Related contracts: `contracts/openapi/components/schemas/training/` (schemas como exemplos de DTOs canônicos)
- Source policy: `DTO_VIEWMODEL_BOUNDARY_RULES.md`
