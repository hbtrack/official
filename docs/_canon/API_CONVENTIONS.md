---
doc_type: canon
version: "2.0.0"
last_reviewed: "2026-03-11"
status: active
---

# Convenções de API — HB Track

## 1. SSOT (Fonte Canônica)

A fonte canônica e determinística para **convenções, validações e templates de API HTTP/OpenAPI** é:

- `.contract_driven/templates/api/api_rules.yaml`

Regra dura:
- Se uma convenção necessária não estiver explícita na SSOT, o agente **DEVE bloquear** (não inferir).
- Em caso de conflito com qualquer outra convenção/documento, prevalece `.contract_driven/templates/api/api_rules.yaml` (salvo exceção HB Track explícita e normativa).

## 2. Ordem de Leitura (APIs)

1. `.contract_driven/CONTRACT_SYSTEM_RULES.md`
2. `.contract_driven/CONTRACT_SYSTEM_LAYOUT.md`
3. `.contract_driven/GLOBAL_TEMPLATES.md`
4. `.contract_driven/templates/api/api_rules.yaml` (**SSOT de API**)
5. `docs/_canon/ERROR_MODEL.md` e `docs/_canon/SECURITY_RULES.md` (cross-cutting)
6. Contratos: `contracts/openapi/openapi.yaml` e `contracts/openapi/paths/<module>.yaml`

## 3. O que ESTE documento governa

Este documento existe para:
- apontar a SSOT de API (`api_rules.yaml`);
- reduzir duplicação normativa dentro de `docs/_canon/`.

Este documento **NÃO** é o local para repetir regras detalhadas de naming, paginação, erros, segurança, compatibilidade ou templates OpenAPI.

## 4. Ponteiros Operacionais

- Convenções/validações/templates (SSOT): `.contract_driven/templates/api/api_rules.yaml`
- Gates de contratos (CI): `docs/_canon/CI_CONTRACT_GATES.md`
- Estratégia de testes: `docs/_canon/TEST_STRATEGY.md`
- Modelo canônico de erros: `docs/_canon/ERROR_MODEL.md`
- Regras globais de segurança: `docs/_canon/SECURITY_RULES.md`

## 5. Registry legado (#NNN)

Qualquer baseline externo que usava numeração estável `(#NNN)` foi migrado para:

- `.contract_driven/templates/api/api_rules.yaml` → `hbtrack_api_rules.legacy_rule_registry`

Isso mantém a numeração estável sem duplicar regras em múltiplos lugares, permitindo overrides por precedência (HB Track > OWASP > Google > Adidas).
