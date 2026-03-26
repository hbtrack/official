# SECURITY_RULES.md

## Objetivo
Definir regras transversais de segurança.

## Fonte canônica para APIs
Regras de segurança específicas para design/contrato de APIs (OWASP API Top 10, BOLA, allowlists, consumo seguro, inventário) estão consolidadas em:
- **Matriz normativa (OWASP → declaração → evidência → gate)**: `docs/_canon/security/OWASP_API_CONTROL_MATRIX.yaml`
- **SSOT de convenções/templates/validações de API HTTP**: `.contract_driven/templates/api/api_rules.yaml`

> Regra de governança: referências e guias (ex.: OWASP em texto) não substituem a matriz normativa.
> A matriz define campos estáveis, evidência mínima e gates nomeados; `api_rules.yaml` define convenções e templates.

## Áreas
- autenticação
- autorização
- sessão
- proteção de dados
- upload
- auditoria
- rate limiting / quotas
- observabilidade de segurança

## Regras (mínimo)
1. Toda operação sensível requer autorização explícita (negação por omissão).
2. Toda operação que acessa/edita um objeto deve validar autorização no servidor ao nível do objeto (BOLA).
3. Toda escrita deve usar allowlist de propriedades (evitar mass assignment).
4. Todo acesso administrativo deve ser auditável.
5. Toda ação destrutiva deve ser rastreável.
6. Toda exposição de dados pessoais deve obedecer política de minimização (need-to-know).
7. Endpoints de autenticação e fluxos sensíveis devem ter proteção contra abuso (rate limit, quotas e monitoramento).

## Gates
- Gate canônico de integridade/estrutura da matriz OWASP: `OWASP_API_CONTROL_MATRIX_GATE` (em `python3 scripts/validate_contracts.py`).

## Perfis Base (referência)
Perfis são um ponto de partida; o modelo autoritativo de permissões deve existir por módulo em `PERMISSIONS_<MODULE>.md` quando aplicável.
- admin
- coordenador
- treinador
- staff
- atleta
- operador
- leitura restrita

## Decisões Arquiteturais de Segurança (ADRs Normativas)

> As regras abaixo são elevadas a status normativo pelos ADRs correspondentes.
> Em caso de conflict, o ADR prevalece sobre descrições textuais neste arquivo.

| Área | ADR | Sumário |
|------|-----|-------|
| Autenticação (JWT) | [ADR-007](decisions/ADR-007-auth-strategy.md) | RS256, claims mínimas, 15min access / 7d refresh, jti blacklist Redis |
| Autorização (RBAC) | [ADR-008](decisions/ADR-008-authz-strategy.md) | RBAC flat 5 roles, deny-by-omission, BOLA/BOPLA/BFLA por camada |
| Dados Sensíveis (PII/PHI) | [ADR-010](decisions/ADR-010-sensitive-data-policy.md) | Taxonomia 4 classes, mascaramento em logs, restrição PHI em analytics |
| Secrets e Rotação | [ADR-012](decisions/ADR-012-secrets-policy.md) | .env em dev, env vars VPS prod, JWT key rotation 90 dias |
| Logging e Observabilidade | [ADR-013](decisions/ADR-013-logging-policy.md) | JSON estruturado, X-Flow-ID, PHI/CREDENTIALS nunca logados |

## Segredos e Configuração
- origem: secret manager do ambiente (proibido commitar segredos no repositório) — ver **ADR-012**
- rotação: JWT keys 90 dias, DB credentials 90 dias — definido em **ADR-012**
- logs: não registrar segredos nem dados sensíveis; mascarar identificadores quando apropriado — regras detalhadas em **ADR-013**
