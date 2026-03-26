# ADR-011: Política de Retenção de Dados

- Status: Accepted
- Date: 2026-03-15
- Deciders: Equipe HB Track
- Tags: data-retention, lgpd, privacy, compliance
- Resolves: ARCH-005
- Priority: importante — deferido v1.0 (implementação completa em v1.0; estrutura de contrato pode ser criada antes)

## Context

O HB Track armazena dados com ciclos de vida muito distintos: dados históricos de partidas (preservar permanentemente), dados de saúde de atletas (LGPD impõe prazo mínimo e direito ao apagamento), logs de auditoria (prazo regulatório/governança interna), e credenciais transitórias. Sem política formal, o sistema acumula dados sem critério, criando risco de violação LGPD por retenção excessiva e de risco operacional por ausência de dados obrigatórios.

LGPD (Lei 13.709/2018) Art. 15 define fim do tratamento como base em: finalidade atingida, término do período de tratamento, solicitação do titular, ou determinação da autoridade.

## Decision

### Tabela de retenção por categoria de dado

| Categoria | Módulo(s) | Período de retenção | Fundamentação |
|-----------|-----------|--------------------|----|
| Logs de auditoria | `audit` | 2 anos | Governança interna + rastreabilidade |
| Registros médicos (PHI) | `medical` | 5 anos após última atualização | LGPD + CFM Res. 2.218/2018 análogo |
| Dados de wellness (PHI) | `wellness` | 2 anos ou solicitação de exclusão | LGPD Art. 15 IV |
| Dados de partida/competição | `matches`, `competitions` | Indefinido | Histórico esportivo — interesse legítimo |
| Dados de treinamento | `training` | 3 anos | Histórico técnico com validade operacional |
| Dados de usuário ativo | `users` | Enquanto conta ativa | Relação contratual |
| Dados de usuário deletado | `users`, todos | 30 dias → expurgo de PII | LGPD Art. 16 IV — backup/segurança |
| Tokens de refresh | `identity_access` | 7 dias (TTL, ver ADR-007) | —  |
| Logs de aplicação (stdout) | infra | 30 dias | Operacional |
| Snapshots de backup | infra | 30 dias | Continuidade de negócio |
| Agent execution logs | `_reports/agent_execution/` | 30 dias | Governança de desenvolvimento |

### Fluxo de exclusão de conta (conta deletada)

1. **D+0** (data da solicitação): conta marcada como `status: deleted`, login bloqueado.
2. **D+0 a D+30**: dados mantidos no estado atual (window de reversão ou auditoria).
3. **D+30**: purge de todos os campos `PII` (conforme ADR-010) do registro do usuário. PHI de módulo `medical`/`wellness` mantidos sem identificador individual (anonimizados) pelo prazo respectivo (5 anos `medical`, 2 anos `wellness`).
4. Dados de partida/estatísticas: anonimizados (substituir referência ao `userId` por ID de atleta anônimo), não deletados.
5. Evento `USER_GDPR_PURGE` emitido no módulo `audit` com timestamp e confirmação de campos purgados.

### Atletas menores (< 18 anos)

- Dados de PHI de atleta menor: retenção limitada ao período enquanto o responsável legal mantiver o consentimento ativo.
- Revogação de consentimento do responsável legal: aciona o mesmo fluxo de exclusão (D+30 purge).
- Ao atingir 18 anos: notificação ao atleta para reafirmação do consentimento; sem reafirmação em 30 dias, PHI são purgados.

### Responsabilidade de implementação

- Purge automático: processo `scripts/ops/purge_retention.py` (a ser implementado em v1.0), executável via cron diário.
- Trigger manual: endpoint `DELETE /users/{userId}` no módulo `users` deve registrar solicitação e acionar o processo.
- Monitoramento: `audit` module deve registrar cada operação de purge com resultado e campos afetados.

### Exclusão vs. Anonimização

- PII: **deletar** (campos zerados ou substituídos por valor nulo com motivo `GDPR_PURGE`).
- PHI sem PII identificador: **anonimizar** (desvincular do `userId`, manter para análise agregada se útil).
- Dados esportivos (estatísticas de partida): **anonimizar** com referência a `athlete_uuid_anon` gerado no momento do purge.

## Consequences

### Positive
- Conformidade com LGPD — sem retenção excessiva de PII/PHI.
- Janela de 30 dias pós-exclusão reduz risco operacional (reversibilidade, cobertura de auditoria).
- Política clara de anonimização preserva valor analítico dos dados esportivos.
- Menores têm fluxo de proteção explícito.

### Negative
- Implementação do purge automático (v1.0) requer cuidado para não expurgar mais do que necessário.
- Anonimização de atleta em dados históricos de partida exige foreign key design cuidadoso (não pode usar `userId` direto em dados históricos permanentes).
- Reprocessamento analítico após purge pode produzir resultados divergentes de histórico anterior.

## Alternatives Considered

- **Soft delete sempre, sem purge**: mais simples, mas viola LGPD Art. 16. Rejeitado.
- **Deletar tudo imediatamente**: simples para LGPD, mas destrói análises históricas legítimas. Rejeitado — anonimização é melhor.
- **Vault de dados com controle granular por dado**: adequado para escala enterprise, mas overhead inviável para v0. Candidato para v2+.

## Links

- Resolves: `docs/_canon/ARCHITECTURE_DECISION_BACKLOG.md` ARCH-005
- Related: `docs/_canon/decisions/ADR-010-sensitive-data-policy.md` (taxonomia PII/PHI)
- Related: `docs/_canon/decisions/ADR-007-auth-strategy.md` (TTL de tokens)
- Regulatório: LGPD Arts. 5°, 15, 16 — Lei 13.709/2018
