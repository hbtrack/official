<!-- TEMPLATE: global-canon-template | DEST: docs/_canon/SYSTEM_SCOPE.md | SOURCE: .contract_driven/templates/globais/SYSTEM_SCOPE.md -->

# SYSTEM_SCOPE.md

## Identidade do Sistema
- Nome: `{{PROJECT_NAME}}`
- Domínio principal: `Handebol / Sports-Tech`
- Tipo de sistema: `{{SYSTEM_TYPE}}`

## Missão
{{PROJECT_NAME}} existe para suportar operações, gestão, treinamento, jogos, competições e analytics de handebol por meio de contratos fortes entre domínio, API, interface e testes.

## Objetivos
- Centralizar informação operacional do handebol
- Reduzir inconsistência entre backend, frontend e testes
- Garantir evolução segura orientada a contrato
- Preservar aderência às regras formais do esporte quando aplicável

## Atores
- Administrador
- Coordenador
- Treinador
- Comissão técnica
- Atleta
- Operador de mesa/scout
- Usuário externo autorizado
- Sistema integrador

## Macrodomínios
- Atletas
- Equipes
- Treinos
- Jogos
- Competições
- Analytics
- Usuários e Permissões
- Comunicação/Notificações
- Arquivos e Relatórios

## Dentro do Escopo
- Gestão de entidades esportivas
- Fluxos operacionais do handebol
- Contratos de API e dados
- Fluxos de UI
- Regras de negócio derivadas do domínio esportivo
- Testes orientados a contrato

## Fora do Escopo
{{OUT_OF_SCOPE_MD_LIST}}

## Dependências Externas
{{EXTERNAL_DEPENDENCIES_MD_LIST}}

## Fonte Regulatória do Esporte
Sempre que houver regra de negócio derivada da modalidade, consultar:
- `HANDBALL_RULES_DOMAIN.md`

## Critérios de Aceite do Escopo
- Todo módulo deve mapear seu escopo local contra este documento
- Toda regra transversal deve estar refletida em `GLOBAL_INVARIANTS.md`
- Toda capacidade pública deve aparecer em contrato

## Placeholders de Projeto
- `{{PROJECT_NAME}}`
- `{{ORG_NAME}}`
- `{{TARGET_USERS}}`
- `{{PRIMARY_MARKET}}`
