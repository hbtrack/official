<!-- STATUS: NEEDS_REVIEW -->

# Email de Convite e Boas-Vindas (Resend)

Documenta o serviço responsável por enviar convites e boas-vindas com token de primeiro acesso, usando Resend.

## Arquivo principal
- `app/services/intake/email_service_v2.py`

## Responsabilidade
- Enviar e-mail de convite com link `/new-password?token=...` (token tipo `welcome`, expira em 48h).
- Enviar e-mail de boas-vindas institucional (sem token), reaproveitando o mesmo layout.

## Entradas das funções
- `send_invite_email(to_email, person_name, token, app_url, organization_name=None, role_name=None)`
  - Monta link de ativação: `{app_url}/new-password?token={token}`.
  - Inclui papel/organização no corpo se fornecidos.
- `send_welcome_email(to_email, person_name, organization_name=None)`

## Saída
- Booleano de sucesso. Faz logging em sucesso/falha.

## Configuração (settings)
- `RESEND_API_KEY` (obrigatório)
- `RESEND_FROM_EMAIL`
- `RESEND_FROM_NAME`
- `RESEND_REPLY_TO` (opcional)

## Expiração do token
- Gerado via `PasswordResetService.create_reset_token(user_id, token_type="welcome", expires_in_hours=48)`.
- Cada novo convite invalida o anterior do mesmo usuário/tipo.

## Layout e copy
- HTML claro com logo “HB TRACK”, botão escuro, copy em português.
- Aviso explícito de expiração: “O link expira em 48 horas por segurança.”
- Texto plano equivalente acompanha o HTML.

## Fluxo típico de uso
1) Criar/garantir usuário e pessoa; gerar token welcome (48h).
2) Chamar `send_invite_email(...)` passando token e `APP_URL` (ou `FRONTEND_URL`).
3) Frontend abre `/new-password?token=...` para o usuário definir a senha.

## Logs
- Sucesso: `Email enviado via Resend` (extra: `to`, `subject`).
- Erro: mensagem de erro via logger com exceção.
