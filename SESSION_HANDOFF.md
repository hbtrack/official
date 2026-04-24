---
data_ultima_sessao: "2026-04-24"
branch_ativo: feat/training-module-phase4
modo_operacao: ROADMAP
ci_status: UNKNOWN
modulo_foco: training
fase_roadmap: 6
roadmap_phase: 6
task_type: execute_roadmap_phase
boot_profile_id: roadmap_execution
task_id: CI_CD_FORENSICS_AND_REMEDIATION
resultado: PENDENTE
proxima_acao_permitida: "commitar fixes (traceId ProblemOut + compile_api_policy --all + scripts/hb TRAINING_CURSOR_SECRET) e fazer push para feat/training-module-phase4"
bloqueios_ativos: []
evidence_paths:
  - "src/identity_access/schemas.py"
  - "src/users/schemas.py"
  - "src/video/schemas.py"
  - "scripts/hb"
  - "generated/manifests/"
---
# SESSION HANDOFF — HB TRACK (CI FORENSICS)

## O que foi feito

Investigação forense das falhas de deployment na branch `main`:
- **Run 24766628453:** falha de permissão em `/opt/hbtrack/production`; o workflow já tinha sido endurecido com guardas de owner/stat.
- **Run 24785900356:** falha no gate de testes por execução de casos `slow`; o workflow já tinha sido ajustado para `-m "not slow"`.
- **Run 24792649602:** falha de autenticação ao fazer pull da imagem no VPS de staging (`Error response from daemon: denied`).
- `.github/workflows/deploy.yml` ajustado para usar `GHCR_PULL_TOKEN` e `GHCR_PULL_USERNAME` como credenciais persistentes de pull no VPS.
- Secrets `GHCR_PULL_TOKEN` e `GHCR_PULL_USERNAME` criadas no repositório `hbtrack/official` via API do GitHub.

## Estado Geral

| Item | Status |
|---|---|
| Reparo de Permissões VPS | ✅ Aplicado |
| Reparo de Testes (not slow) | ✅ Aplicado |
| Reparo de Autenticação GHCR | ✅ Patch aplicado |
| Bug de Imports Generated Schemas | ✅ Corrigido no merge do PR #84 |
| Secrets de pull GHCR no repositório | ✅ Criadas |

## Próxima ação permitida

1. Commit e push da alteração de `.github/workflows/deploy.yml` para `main`.
2. Monitorar o próximo run automático do deploy pipeline em staging.
3. Se staging ficar verde, seguir para a etapa humana de aprovação de produção.

## Bloqueios ativos

Nenhum.

## Evidências


## Próxima sessão

1. Confirmar que o commit do workflow entrou na `main`.
2. Monitorar o pipeline de deploy na `main`.
3. Prosseguir com a Fase 6 do Roadmap assim que staging e produção estabilizarem.
