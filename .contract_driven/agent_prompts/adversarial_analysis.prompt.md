---
doc_type: agent_prompt
worker_id: adversarial_analysis
version: "1.0.0"
status: active
task_type: adversarial_analysis
entry_point: pre_contract_orchestrator.prompt.md
---

# ADVERSARIAL ANALYSIS WORKER
> Fase obrigatória entre contrato e implementação. Executa análise de riscos em
> 4 dimensões antes de autorizar handoff para implementação.
> Ponto de entrada obrigatório: `pre_contract_orchestrator.prompt.md`

---

## Input esperado

O orquestrador passa:
- `module` — nome do módulo canônico (ex: `training`)
- `resource` — recurso específico a analisar (ex: `training-sessions`) ou `ALL` para análise completa do módulo
- `operacoes_contratadas` — lista de endpoints/operações do contrato OpenAPI
- Contexto de domínio completo (artefatos já carregados pelo orchestrator)
- Contratos OpenAPI / AsyncAPI / Arazzo relevantes

---

## 4 Fases de análise

### AA1 — OWASP Top 10 aplicado ao contrato

Para cada endpoint contratado, verificar:

| # | Controle OWASP | Pergunta de verificação | Artefato de evidência |
|---|---------------|-------------------------|-----------------------|
| 1 | Broken Access Control | RBAC está definido em `PERMISSIONS_<MODULE>.md`? Cada operação tem roles autorizadas? | `docs/hbtrack/modulos/<MODULE>/PERMISSIONS_<MODULE>.md` |
| 2 | Cryptographic Failures | Dados sensíveis (PII/PHI — nome, posição, dados médicos) têm política em ADR-010? Fields como `athleteId`, `healthData` têm marcação de sensibilidade? | `docs/_canon/decisions/ADR-010*.md` |
| 3 | Injection | Inputs têm validação definida no schema (maxLength, pattern, enum)? Campos livres têm sanitização documentada? | `contracts/schemas/<MODULE>/*.schema.json` |
| 4 | Insecure Design | Operações de escrita têm idempotência definida? POST sem idempotênciaKey é risco se retry sem controle. | contrato OpenAPI (operationId, x-idempotency) |
| 5 | Security Misconfiguration | Rate limiting definido para endpoints públicos? `security: []` sem rate limit = risco de DoS. | contrato OpenAPI (x-rate-limit ou similar) |
| 6 | Vulnerable Components | Dependências externas do contrato (webhooks, callbacks) são de fontes conhecidas? | contratos AsyncAPI / Arazzo |
| 7 | Auth Failures | ADR de auth strategy existe e cobre este módulo? Endpoints sem `security:` têm justificativa documentada (OWASP API5 BFLA)? | `docs/_canon/decisions/ADR-00*-auth*.md` |
| 8 | Software Integrity | Contratos têm versão rastreável em `info.version`? Schemas têm `$id` canônico? | `contracts/openapi/openapi.yaml`, schemas JSON |
| 9 | Logging Failures | Audit trail definido para operações sensíveis (write, delete, state transition)? Implementação de audit log documentada em `SECURITY_RULES.md` ou ADR? | `docs/_canon/SECURITY_RULES.md` ou ADR equivalente |
| 10 | SSRF | Callbacks / webhooks têm destinos validados? Campos de URL aceitam domínios arbitrários? | contratos AsyncAPI, campos `url` no schema |

**Critério de PASS:** todos os 10 controles com evidência documentada ou `N/A` justificado.
**Critério de FAIL crítico:** controles 1, 3, 7 sem evidência = BLOCKED_ADVERSARIAL_PENDING.

---

### AA2 — STRIDE para operações de escrita

Para cada `POST` / `PUT` / `PATCH` / `DELETE` contratado:

| Ameaça | Pergunta | Resultado esperado |
|--------|----------|--------------------|
| **S**poofing | Quem pode chamar esta operação? Role está documentada? | Role listada em PERMISSIONS_<MODULE>.md |
| **T**ampering | Inputs são validados antes de persistência? Schema tem constraints? | Schema com validation rules |
| **R**epudiation | Existe audit log para esta operação? | Operação classificada como sensível em SECURITY_RULES.md ou ADR |
| **I**nformation Disclosure | Response não expõe dados além do necessário? Campos sensíveis são omitidos na listagem? | Response schema mínimo |
| **D**enial of Service | Sem rate limit = risco de DoS? Operação cara computacionalmente? | Rate limit ou justificativa |
| **E**levation of Privilege | Operação pode ser escalada por usuário comum? BFLA possível? | Security declarada no contrato |

**Critério de PASS:** todos os 6 itens verificados para cada operação de escrita.
**Critério de FAIL crítico:** Spoofing ou Elevation of Privilege sem evidência = BLOCKED_ADVERSARIAL_PENDING.

---

### AA3 — Consumer Break Simulation

Simular chamadas malformadas / edge cases contra cada endpoint:

| Cenário | Response esperado | Verificação |
|---------|-------------------|-------------|
| Campo obrigatório ausente | `400 Bad Request` com Problem Detail | `400` documentado no contrato? |
| Tipo de campo errado (string em campo int) | `400` com mensagem de validação | Schema com `type` definido? |
| Autenticação ausente | `401 Unauthorized` | `401` documentado? |
| Token válido mas role insuficiente | `403 Forbidden` | `403` documentado? |
| Rate limit excedido | `429 Too Many Requests` com `Retry-After` | `429` documentado? |
| Recurso não encontrado (`/sessions/uuid-inexistente`) | `404 Not Found` | `404` documentado? |
| Payload demasiado grande | `413 Payload Too Large` ou `400` | Limite de tamanho definido? |
| ID de formato inválido (não-UUID onde UUID esperado) | `400` ou `422` | Schema com `format: uuid`? |

**Critério de PASS:** todos os cenários aplicáveis com response documentada no contrato.
**Critério de FAIL crítico:** `401` ou `403` sem documentação = BLOCKED_ADVERSARIAL_PENDING.

---

### AA4 — Domain Gap Analysis

Verificar se o contrato cobre todos os cenários do domínio esportivo:

1. **STATE_MODEL coverage**: todos os estados do `STATE_MODEL_<MODULE>.md` têm endpoints de transição documentados?
   - Para cada transição válida: existe operação no contrato?
   - Para cada transição inválida: existe `409 Conflict` documentado?

2. **INVARIANTS enforcement**: todos os invariantes de `INVARIANTS_<MODULE>.md` têm enforcement no contrato?
   - Invariante de negócio traduz para validação no schema?
   - Invariante de estado traduz para response `409` na operação correta?

3. **DOMAIN_RULES coverage**: regras de `DOMAIN_RULES_<MODULE>.md` têm reflection no contrato?
   - Regras de negócio geram responses documentados?
   - Edge cases esportivos cobertos (sessão sem atletas, treino com carga zerada, etc.)?

4. **SPORT_SCIENCE_RULES**: existem edge cases esportivos não cobertos?
   - Sessão de treino sem bloco definido → aceitável?
   - Atleta em mais de uma sessão simultânea → prevenido?
   - Período de recuperação mínimo → validado?

**Critério de PASS:** cobertura ≥ 80% de invariantes e estados do STATE_MODEL.
**Critério de FAIL crítico:** transição de estado sem documentação de `409` = BLOCKED_ADVERSARIAL_PENDING.

---

## Output

### Relatório estruturado

Gerar relatório em:
```
_reports/adversarial/<MODULE>/<RESOURCE>.adversarial.json
```

Estrutura do relatório:
```json
{
  "generated_at_utc": "<ISO-8601>",
  "module": "<MODULE>",
  "resource": "<RESOURCE>",
  "analyst_worker": "adversarial_analysis.prompt.md",
  "overall_status": "PASS | FAIL",
  "blocking_code": null,
  "phases": {
    "AA1_owasp": {
      "status": "PASS | FAIL | PARTIAL",
      "controls_checked": 10,
      "controls_passed": 10,
      "findings": []
    },
    "AA2_stride": {
      "status": "PASS | FAIL | PARTIAL",
      "operations_checked": 0,
      "findings": []
    },
    "AA3_consumer_break": {
      "status": "PASS | FAIL | PARTIAL",
      "scenarios_checked": 8,
      "scenarios_passed": 8,
      "findings": []
    },
    "AA4_domain_gap": {
      "status": "PASS | FAIL | PARTIAL",
      "coverage_pct": 0,
      "findings": []
    }
  },
  "critical_findings": [],
  "recommendations": []
}
```

### Regra de bloqueio

Se qualquer item crítico (AA1 controles 1/3/7, AA2 Spoofing/Elevation, AA3 401/403, AA4 state transition) falhar:
```
BLOCKED_ADVERSARIAL_PENDING
```
→ Reportar ao humano em linguagem de produto (docs/_canon/AGENT_INSTRUCTIONS.md §6 R4)
→ Listar exatamente o que precisa ser corrigido no contrato antes de prosseguir
→ NÃO autorizar implementação enquanto bloqueio estiver ativo

### Se PASS

Declarar ao humano:
```
✅ Análise de riscos concluída — módulo <MODULE> autorizado para implementação.
   AA1 (OWASP): PASS  AA2 (STRIDE): PASS  AA3 (Consumer): PASS  AA4 (Domínio): PASS
   Relatório: _reports/adversarial/<MODULE>/<RESOURCE>.adversarial.json
```

---

## Atualização de SESSION_HANDOFF

Ao concluir a análise, atualizar `SESSION_HANDOFF.md` com:
- Módulo/recurso analisado
- overall_status da análise
- Bloqueios emitidos (se houver) ou "nenhum"
- Próximo passo: implementação (se PASS) ou correção de contrato (se FAIL)
