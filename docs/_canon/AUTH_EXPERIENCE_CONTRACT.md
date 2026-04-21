---
doc_type: canon
version: "1.0.0"
status: active
state_semantics: target-state
owner: product-owner
related_docs:
  - docs/_canon/UX_BRAND_CONTRACT.md
---

# AUTH_EXPERIENCE_CONTRACT.md

## 0. Objetivo
Define a experiência normativa de autenticação do HB Track Web.

## 1. Escopo
Inclui:
- signin
- forgot/reset password
- new password
- confirm reset
- estados de erro/sucesso
- redirect pós-login

## 2. Tela de login
### Elementos obrigatórios
- logo de auth
- tagline institucional
- campo email
- campo senha
- toggle mostrar/ocultar senha
- botão principal
- tratamento visual de erro
- loading state
- link “Esqueceu a senha?”

### Branding
- light mode usa `generated/images/auth-logo.svg`
- dark mode usa `generated/images/auth-logo-dark.svg`

### Tagline oficial
- “Dados que decidem jogos”

### Comportamento
- o botão principal só habilita com formulário válido
- erro de login deve ser controlado
- sucesso redireciona para a home autenticada

## 3. Recuperação de senha

### Fluxo obrigatório
- solicitar reset
- enviar email transacional com link seguro ao usuário
- abrir tela de nova senha
- confirmar redefinição

### Provider inicial de email transacional
- baseline inicial: Resend

### Regra
- o link enviado deve apontar para o frontend usando `FRONTEND_URL` do ambiente
- o produto não pode ser considerado pronto para uso real sem fluxo de recuperação de senha com envio real de email

## 4. Estados obrigatórios
- loading
- credenciais inválidas
- reset solicitado com sucesso
- token inválido/expirado
- senha redefinida com sucesso

## 5. Sessão
- usuário autenticado não deve permanecer na tela de login
- logout deve estar disponível no menu do usuário
- a experiência deve suportar redirect pós-login

## 6. Critérios de aceite
Auth só pode ser aprovada se:
- login estiver conforme contrato
- forgot/reset existir
- envio de email real existir
- mensagens de erro/sucesso estiverem definidas
- redirect pós-login funcionar