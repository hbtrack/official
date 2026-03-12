<!-- TEMPLATE: global-canon-template | DEST: docs/_canon/SECURITY_RULES.md | SOURCE: .contract_driven/templates/globais/SECURITY_RULES.md -->

# SECURITY_RULES.md

## Objetivo
Definir regras transversais de segurança.

## Áreas
- autenticação
- autorização
- sessão
- proteção de dados
- upload
- auditoria
- rate limiting
- observabilidade de segurança

## Regras
1. Toda operação sensível requer autorização explícita.
2. Todo acesso administrativo deve ser auditável.
3. Toda ação destrutiva deve ser rastreável.
4. Toda exposição de dados pessoais deve obedecer política de minimização.

## Perfis Base
- admin
- coordenador
- treinador
- staff
- atleta
- operador
- leitura restrita

## Segredos e Configuração
- origem: `{{SECRETS_POLICY}}`
- rotação: `{{ROTATION_POLICY}}`
- logs: `{{LOGGING_POLICY}}`
