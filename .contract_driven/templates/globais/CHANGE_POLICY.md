<!-- TEMPLATE: global-canon-template | DEST: docs/_canon/CHANGE_POLICY.md | SOURCE: .contract_driven/templates/globais/CHANGE_POLICY.md -->

# CHANGE_POLICY.md

## Objetivo
Definir como contratos, documentação e implementação evoluem.

## Regras
1. Mudança pública começa no contrato.
2. Mudança de regra de negócio começa na documentação do domínio.
3. Mudança de arquitetura significativa exige ADR.
4. Mudança breaking exige classificação explícita.
5. Mudança em módulo deve atualizar sua documentação local mínima.

## Classificação de Mudança
- `non-breaking`
- `breaking`
- `internal-only`
- `documentation-only`

## Fluxo
1. Propor mudança
2. Atualizar contrato/documento-fonte
3. Validar gates
4. Atualizar implementação
5. Atualizar testes
6. Revisar impacto

## Exceções
Toda exceção precisa de:
- justificativa
- escopo
- prazo
- responsável
- ADR ou registro equivalente
