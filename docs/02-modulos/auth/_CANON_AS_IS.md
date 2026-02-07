<!-- STATUS: VERIFIED | evidencia: openapi.json (paths /api/v1/auth/*), schema.sql (users, password_resets) -->

# Auth Module - Canon AS-IS

## Fontes Canonicas

| Artefato | Localizacao | Evidencia |
|----------|-------------|-----------|
| API Endpoints | `docs/_generated/openapi.json` | paths `/api/v1/auth/*` |
| DB Schema | `docs/_generated/schema.sql` | tables `users`, `password_resets` |

---

## Endpoints Verificados (openapi.json)

| Endpoint | Metodo | Descricao |
|----------|--------|-----------|
| `/api/v1/auth/login` | POST | Login com email e senha |
| `/api/v1/auth/me` | GET | Dados do usuario autenticado |
| `/api/v1/auth/permissions` | GET | Permissoes do usuario |
| `/api/v1/auth/context` | GET | Contexto completo de acesso |
| `/api/v1/auth/logout` | POST | Remove cookie HttpOnly |
| `/api/v1/auth/refresh` | POST | Renovar access token |
| `/api/v1/auth/forgot-password` | POST | Solicitar recuperacao de senha |
| `/api/v1/auth/reset-password` | POST | Resetar senha com token |
| `/api/v1/auth/set-password` | POST | Definir senha com token |
| `/api/v1/auth/welcome/verify` | GET | Verificar token de welcome |
| `/api/v1/auth/welcome/complete` | POST | Completar cadastro de welcome |
| `/api/v1/auth/change-password` | POST | Alterar senha |
| `/api/v1/auth/initial-setup` | POST | Setup inicial para dirigente |

---

## Autenticacao (openapi.json)

| Item | Valor | Evidencia |
|------|-------|-----------|
| Tipo | HTTPBearer | `components.securitySchemes.HTTPBearer` |
| Formato | JWT | Bearer Token |

---

## Tabelas Relacionadas (schema.sql)

### users
```sql
CREATE TABLE public.users (
    id uuid DEFAULT public.gen_random_uuid() NOT NULL,
    person_id uuid NOT NULL,
    email character varying(255) NOT NULL,
    password_hash text,                        -- pode ser NULL (convite pendente)
    is_superadmin boolean DEFAULT false NOT NULL,
    is_locked boolean DEFAULT false NOT NULL,
    status character varying(20) DEFAULT 'ativo' NOT NULL,
    expired_at timestamp with time zone,
    -- timestamps e soft delete
    CONSTRAINT ck_users_status CHECK (status IN ('ativo', 'inativo', 'arquivado'))
);
```

### password_resets
```sql
CREATE TABLE public.password_resets (
    id uuid DEFAULT public.gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    token text NOT NULL,
    token_type text DEFAULT 'reset' NOT NULL,  -- 'reset' ou 'welcome'
    used boolean DEFAULT false NOT NULL,
    used_at timestamp with time zone,
    expires_at timestamp with time zone NOT NULL,
    -- timestamps e soft delete
    CONSTRAINT ck_password_resets_token_type CHECK (token_type IN ('reset', 'welcome'))
);
```

---

## Docs do Modulo - Status Apos Auditoria

| Arquivo | Status | Razao |
|---------|--------|-------|
| CAMPOS_OBRIGATORIOS_BANCO.md | VERIFIED | Campos batem com schema.sql |
| ANALISE_PAGINAS_LOGIN.md | DEPRECATED | Analise de frontend, nao API |
| CORRECOES_FINAIS_WELCOME.md | DEPRECATED | Historico de bug fixes |
| CORRECOES_FORMULARIOS_BANCO.md | DEPRECATED | Historico de implementacao |
| GUIA_TESTE_FORMULARIOS_ESPECIFICOS.md | DEPRECATED | Guia de teste |
| MELHORIAS_AUTENTICACAO_IMPLEMENTADAS.md | DEPRECATED | Historico de implementacao |
| PADRONIZACAO_AUTH_CONTEXT.md | DEPRECATED | Detalhes de implementacao |
| RELATORIO_AUDITORIA_LOGIN_AUTORIZACAO.md | DEPRECATED | Auditoria historica |
| RESUMO_CORRECOES.md | DEPRECATED | Resumo historico |
| SSR_COOKIE_FIX.md | DEPRECATED | Fix tecnico de frontend |

---

## Regenerar Evidencias

```bash
cd "C:\HB TRACK\Hb Track - Backend"
python scripts/generate_docs.py --all
```
