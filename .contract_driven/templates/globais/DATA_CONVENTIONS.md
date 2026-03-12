<!-- TEMPLATE: global-canon-template | DEST: docs/_canon/DATA_CONVENTIONS.md | SOURCE: .contract_driven/templates/globais/DATA_CONVENTIONS.md -->

# DATA_CONVENTIONS.md

## Objetivo
Padronizar modelagem de dados, tipos e nomenclatura.

## Convenções Gerais
- IDs: `{{ID_STRATEGY}}`
- Datas: `{{DATE_TIME_STANDARD}}`
- Fuso horário: `{{TIMEZONE_POLICY}}`
- Enum: `{{ENUM_POLICY}}`
- Nullability: `{{NULLABILITY_POLICY}}`

## Convenções de Nome
- tabelas/coleções: `{{TABLE_NAMING}}`
- colunas/campos: `{{FIELD_NAMING}}`
- arquivos de schema: `*.schema.json`

## Auditoria
- createdAt
- updatedAt
- deletedAt (se aplicável)
- createdBy / updatedBy (se aplicável)

## Dados Sensíveis
- classificação: `{{SENSITIVE_DATA_POLICY}}`
- retenção: `{{RETENTION_POLICY}}`
- mascaramento: `{{MASKING_POLICY}}`

## Regras
- não duplicar campo sem motivo explícito
- não usar enum implícito sem contrato
- não usar data local ambígua sem política de timezone
