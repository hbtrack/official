```json
{
  "openapi": "3.1.0",
  "info": {
    "title": "HB Tracking API",
    "description": "Sistema de Gestao de Handebol",
    "version": "1.0.0"
  },
  "paths": {
    "/api/v1/health": {
      "get": {
        "tags": [
          "health",
          "Health"
        ],
        "summary": "Health",
        "description": "Health check completo\n\nVerifica:\n- Database connection\n- PostgreSQL version\n- pgcrypto extension (RDB1)\n- Alembic migration version\n\nReturns:\n    dict: Status de saúde do sistema",
        "operationId": "health_api_v1_health_get",
        "responses": {
          "200": {
            "description": "Successful Response",
            "content": {
              "application/json": {
                "schema": {}
              }
            }
          }
        }
      }
    },
    "/api/v1/health/liveness": {
      "get": {
        "tags": [
          "health",
          "Health"
        ],
        "summary": "Liveness",
        "description": "Liveness probe (Kubernetes)\n\nRetorna 200 se a aplicação está rodando",
        "operationId": "liveness_api_v1_health_liveness_get",
        "responses": {
          "200": {
            "description": "Successful Response",
            "content": {
              "application/json": {
                "schema": {}
              }
            }
          }
        }
      }
    },
    "/api/v1/health/readiness": {
      "get": {
        "tags": [
          "health",
          "Health"
        ],
        "summary": "Readiness",
        "description": "Readiness probe (Kubernetes)\n\nRetorna 200 se a aplicação está pronta para receber tráfego",
        "operationId": "readiness_api_v1_health_readiness_get",
        "responses": {
          "200": {
            "description": "Successful Response",
            "content": {
              "application/json": {
                "schema": {}
              }
            }
          }
        }
      }
    },
    "/api/v1/health/full": {
      "get": {
        "tags": [
          "health",
          "Health"
        ],
        "summary": "Health Full",
        "description": "Healthcheck completo (validações profundas)\n\nVerifica:\n- Database connection\n- Critical tables exist\n- Alembic migration version\n- Super admin exists (R3, RDB6)\n- Roles seeded (R4)\n- Categories seeded (R15)\n- VIEW v_seasons_with_status exists\n\nReturns:\n    dict: Status detalhado de saúde com todas as validações",
        "operationId": "health_full_api_v1_health_full_get",
        "responses": {
          "200": {
            "description": "Successful Response",
            "content": {
              "application/json": {
                "schema": {}
              }
            }
          }
        }
      }
    },
    "/api/v1/admin/neon/check-and-seed": {
      "get": {
        "tags": [
          "admin",
          "admin"
        ],
        "summary": "Neon Check And Seed",
        "operationId": "neon_check_and_seed_api_v1_admin_neon_check_and_seed_get",
        "responses": {
          "200": {
            "description": "Successful Response",
            "content": {
              "application/json": {
                "schema": {
                  "additionalProperties": true,
                  "type": "object",
                  "title": "Response Neon Check And Seed Api V1 Admin Neon Check And Seed Get"
                }
              }
            }
          }
        }
      }
    },
    "/api/v1/admin/health/utc-season": {
      "get": {
        "tags": [
          "admin",
          "admin"
        ],
        "summary": "Health Utc Season",
        "operationId": "health_utc_season_api_v1_admin_health_utc_season_get",
        "responses": {
          "200": {
            "description": "Successful Response",
            "content": {
              "application/json": {
                "schema": {
                  "additionalProperties": true,
                  "type": "object",
                  "title": "Response Health Utc Season Api V1 Admin Health Utc Season Get"
                }
              }
            }
          }
        }
      }
    },
    "/api/v1/admin/cache/stats": {
      "get": {
        "tags": [
          "admin",
          "admin"
        ],
        "summary": "Get Cache Statistics",
        "description": "Retorna estatísticas dos caches server-side (dev-only).\n\nMostra:\n- Tamanho atual de cada cache\n- Capacidade máxima\n- TTL configurado",
        "operationId": "get_cache_statistics_api_v1_admin_cache_stats_get",
        "responses": {
          "200": {
            "description": "Successful Response",
            "content": {
              "application/json": {
                "schema": {
                  "additionalProperties": true,
                  "type": "object",
                  "title": "Response Get Cache Statistics Api V1 Admin Cache Stats Get"
                }
              }
            }
          }
        }
      }
    },
    "/api/v1/admin/cache/clear": {
      "post": {
        "tags": [
          "admin",
          "admin"
        ],
        "summary": "Clear Cache",
        "description": "Limpa todos os caches server-side (dev-only).\n\nÚtil para:\n- Testes\n- Forçar refresh de dados\n- Debug",
        "operationId": "clear_cache_api_v1_admin_cache_clear_post",
        "responses": {
          "200": {
            "description": "Successful Response",
            "content": {
              "application/json": {
                "schema": {
                  "additionalProperties": {
                    "type": "string"
                  },
                  "type": "object",
                  "title": "Response Clear Cache Api V1 Admin Cache Clear Post"
                }
              }
            }
          }
        }
      }
    },
    "/api/v1/auth/login": {
      "post": {
        "tags": [
          "Authentication"
        ],
        "summary": "Login com email e senha",
        "description": "Autentica usuário e retorna JWT access token.\n\n**Regras aplicáveis:**\n- R2: Usuário com email único\n- R42: Vínculo ativo obrigatório (exceto superadmin)\n- R3: Superadmin pode operar sem vínculo\n\n**Rate Limit:** 5 tentativas por minuto por IP",
        "operationId": "login_api_v1_auth_login_post",
        "requestBody": {
          "content": {
            "application/x-www-form-urlencoded": {
              "schema": {
                "$ref": "#/components/schemas/Body_login_api_v1_auth_login_post"
              }
            }
          },
          "required": true
        },
        "responses": {
          "200": {
            "description": "Successful Response",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/LoginResponse"
                }
              }
            }
          },
          "401": {
            "description": "Email ou senha inválidos"
          },
          "403": {
            "description": "Usuário sem vínculo ativo (R42)"
          },
          "429": {
            "description": "Rate limit excedido - muitas tentativas"
          },
          "422": {
            "description": "Validation Error",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/HTTPValidationError"
                }
              }
            }
          }
        }
      }
    },
    "/api/v1/auth/me": {
      "get": {
        "tags": [
          "Authentication"
        ],
        "summary": "Dados do usuário autenticado",
        "description": "Retorna informações do usuário autenticado a partir do JWT.",
        "operationId": "get_me_api_v1_auth_me_get",
        "security": [
          {
            "HTTPBearer": []
          }
        ],
        "parameters": [
          {
            "name": "X-Request-ID",
            "in": "header",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "title": "X-Request-Id"
            }
          },
          {
            "name": "x-organization-id",
            "in": "header",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "title": "X-Organization-Id"
            }
          }
        ],
        "responses": {
          "200": {
            "description": "Successful Response",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/UserMeResponse"
                }
              }
            }
          },
          "401": {
            "description": "Token inválido ou ausente"
          },
          "422": {
            "description": "Validation Error",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/HTTPValidationError"
                }
              }
            }
          }
        }
      }
    },
    "/api/v1/auth/permissions": {
      "get": {
        "tags": [
          "Authentication"
        ],
        "summary": "Permissões do usuário autenticado",
        "description": "Retorna lista de permissões baseadas no papel do usuário.",
        "operationId": "get_permissions_api_v1_auth_permissions_get",
        "security": [
          {
            "HTTPBearer": []
          }
        ],
        "parameters": [
          {
            "name": "X-Request-ID",
            "in": "header",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "title": "X-Request-Id"
            }
          },
          {
            "name": "x-organization-id",
            "in": "header",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "title": "X-Organization-Id"
            }
          }
        ],
        "responses": {
          "200": {
            "description": "Successful Response",
            "content": {
              "application/json": {
                "schema": {
                  "type": "array",
                  "items": {
                    "type": "string"
                  },
                  "title": "Response Get Permissions Api V1 Auth Permissions Get"
                }
              }
            }
          },
          "401": {
            "description": "Token inválido ou ausente"
          },
          "422": {
            "description": "Validation Error",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/HTTPValidationError"
                }
              }
            }
          }
        }
      }
    },
    "/api/v1/auth/context": {
      "get": {
        "tags": [
          "Authentication"
        ],
        "summary": "Contexto completo de acesso",
        "description": "Retorna papel, vínculos e permissões. CONTRATO FIXO. Apenas espelho do ExecutionContext.",
        "operationId": "get_context_api_v1_auth_context_get",
        "security": [
          {
            "HTTPBearer": []
          }
        ],
        "parameters": [
          {
            "name": "X-Request-ID",
            "in": "header",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "title": "X-Request-Id"
            }
          },
          {
            "name": "x-organization-id",
            "in": "header",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "title": "X-Organization-Id"
            }
          }
        ],
        "responses": {
          "200": {
            "description": "Successful Response",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/AuthContextResponse"
                }
              }
            }
          },
          "422": {
            "description": "Validation Error",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/HTTPValidationError"
                }
              }
            }
          }
        }
      }
    },
    "/api/v1/auth/logout": {
      "post": {
        "tags": [
          "Authentication"
        ],
        "summary": "Logout - Remove cookie HttpOnly",
        "description": "Endpoint de logout que remove o cookie HttpOnly contendo o token.\n\n**Nota:** Em uma implementação completa, este endpoint invalidaria o token em uma blacklist.",
        "operationId": "logout_api_v1_auth_logout_post",
        "security": [
          {
            "HTTPBearer": []
          }
        ],
        "parameters": [
          {
            "name": "X-Request-ID",
            "in": "header",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "title": "X-Request-Id"
            }
          },
          {
            "name": "x-organization-id",
            "in": "header",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "title": "X-Organization-Id"
            }
          }
        ],
        "responses": {
          "204": {
            "description": "Successful Response"
          },
          "422": {
            "description": "Validation Error",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/HTTPValidationError"
                }
              }
            }
          }
        }
      }
    },
    "/api/v1/auth/refresh": {
      "post": {
        "tags": [
          "Authentication"
        ],
        "summary": "Renovar access token",
        "description": "Renova o access token usando um refresh token válido.\n\n**Fluxo:**\n1. Cliente envia refresh_token (recebido no login)\n2. Backend valida o refresh_token\n3. Backend gera novo access_token e refresh_token\n4. Cliente atualiza tokens armazenados\n\n**Segurança:**\n- Refresh token válido por 7 dias\n- Access token válido por 30 minutos\n- Refresh token é invalidado e um novo é gerado (rotation)",
        "operationId": "refresh_token_api_v1_auth_refresh_post",
        "requestBody": {
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/RefreshTokenRequest"
              }
            }
          },
          "required": true
        },
        "responses": {
          "200": {
            "description": "Successful Response",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/RefreshTokenResponse"
                }
              }
            }
          },
          "401": {
            "description": "Refresh token inválido ou expirado"
          },
          "404": {
            "description": "Usuário não encontrado"
          },
          "422": {
            "description": "Validation Error",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/HTTPValidationError"
                }
              }
            }
          }
        }
      }
    },
    "/api/v1/auth/forgot-password": {
      "post": {
        "tags": [
          "Authentication"
        ],
        "summary": "Solicitar recuperação de senha",
        "description": "Solicita recuperação de senha. Envia email com link de reset.\n\n**Fluxo:**\n1. Usuário insere email\n2. Sistema envia email com link de reset\n3. Email contém link para /new-password?token=xxx\n4. Link expira em 24 horas\n\n**Segurança:**\n- Rate limit: 5 requisições por hora por email\n- Token seguro e único\n- Tokens anteriores são invalidados",
        "operationId": "forgot_password_api_v1_auth_forgot_password_post",
        "requestBody": {
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/ForgotPasswordRequest"
              }
            }
          },
          "required": true
        },
        "responses": {
          "200": {
            "description": "Email enviado com sucesso",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ForgotPasswordResponse"
                }
              }
            }
          },
          "400": {
            "description": "Email não encontrado"
          },
          "422": {
            "description": "Validation Error",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/HTTPValidationError"
                }
              }
            }
          }
        }
      }
    },
    "/api/v1/auth/reset-password": {
      "post": {
        "tags": [
          "Authentication"
        ],
        "summary": "Resetar senha com token",
        "description": "Reseta a senha usando um token válido.\n\n**Validações:**\n- Token deve ser válido e não expirado\n- Senhas devem coincidir\n- Nova senha deve ter mínimo 8 caracteres\n- Token pode ser usado apenas uma vez",
        "operationId": "reset_password_api_v1_auth_reset_password_post",
        "requestBody": {
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/app__api__v1__routers__auth__ResetPasswordRequest"
              }
            }
          },
          "required": true
        },
        "responses": {
          "200": {
            "description": "Senha alterada com sucesso",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ResetPasswordResponse"
                }
              }
            }
          },
          "400": {
            "description": "Token inválido, expirado ou senhas não coincidem"
          },
          "404": {
            "description": "Usuário não encontrado"
          },
          "422": {
            "description": "Validation Error",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/HTTPValidationError"
                }
              }
            }
          }
        }
      }
    },
    "/api/v1/auth/set-password": {
      "post": {
        "tags": [
          "Authentication"
        ],
        "summary": "Definir senha com token",
        "description": "Valida token de ativação e define senha (primeira vez).\n    \n    SEGURANÇA:\n    - Token single-use (marcado como `used`)\n    - Expira em 24h\n    - Validado via hash SHA-256\n    \n    Usado quando usuário recebe email de convite.",
        "operationId": "set_password_with_token_api_v1_auth_set_password_post",
        "requestBody": {
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/SetPasswordRequest"
              }
            }
          },
          "required": true
        },
        "responses": {
          "200": {
            "description": "Successful Response",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/SetPasswordResponse"
                }
              }
            }
          },
          "400": {
            "description": "Token inválido ou expirado"
          },
          "404": {
            "description": "Usuário não encontrado"
          },
          "422": {
            "description": "Validation Error",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/HTTPValidationError"
                }
              }
            }
          }
        }
      }
    },
    "/api/v1/auth/welcome/verify": {
      "get": {
        "tags": [
          "Authentication"
        ],
        "summary": "Verificar token de welcome",
        "description": "Verifica se o token de welcome é válido e retorna informações do convite.\n    \n    SEGURANÇA:\n    - Token deve ser do tipo 'welcome'\n    - Token não pode estar usado\n    - Token não pode estar expirado (48h)\n    \n    Retorna dados do convidado para pré-popular o formulário.",
        "operationId": "welcome_verify_api_v1_auth_welcome_verify_get",
        "parameters": [
          {
            "name": "token",
            "in": "query",
            "required": true,
            "schema": {
              "type": "string",
              "title": "Token"
            }
          }
        ],
        "responses": {
          "200": {
            "description": "Successful Response",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/WelcomeVerifyResponse"
                }
              }
            }
          },
          "400": {
            "description": "Token inválido, expirado ou já utilizado"
          },
          "422": {
            "description": "Validation Error",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/HTTPValidationError"
                }
              }
            }
          }
        }
      }
    },
    "/api/v1/auth/welcome/complete": {
      "post": {
        "tags": [
          "Authentication"
        ],
        "summary": "Completar cadastro de welcome",
        "description": "Completa o cadastro do usuário convidado:\n    1. Valida token de welcome\n    2. Define senha do usuário\n    3. Atualiza dados da pessoa (nome, telefone, etc.)\n    4. Ativa o TeamMembership (status → 'ativo')\n    5. Marca token como usado\n    6. Retorna sessão/login automático\n    \n    SEGURANÇA:\n    - Token single-use\n    - Senha validada (mínimo 8 caracteres)",
        "operationId": "welcome_complete_api_v1_auth_welcome_complete_post",
        "requestBody": {
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/WelcomeCompleteRequest"
              }
            }
          },
          "required": true
        },
        "responses": {
          "200": {
            "description": "Successful Response",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/WelcomeCompleteResponse"
                }
              }
            }
          },
          "400": {
            "description": "Token inválido ou senhas não conferem"
          },
          "422": {
            "description": "Validation Error",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/HTTPValidationError"
                }
              }
            }
          }
        }
      }
    },
    "/api/v1/auth/change-password": {
      "post": {
        "tags": [
          "Authentication"
        ],
        "summary": "Alterar senha",
        "description": "Altera a senha do usuário autenticado.",
        "operationId": "change_password_api_v1_auth_change_password_post",
        "security": [
          {
            "HTTPBearer": []
          }
        ],
        "parameters": [
          {
            "name": "X-Request-ID",
            "in": "header",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "title": "X-Request-Id"
            }
          },
          {
            "name": "x-organization-id",
            "in": "header",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "title": "X-Organization-Id"
            }
          }
        ],
        "requestBody": {
          "required": true,
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/ChangePasswordRequest"
              }
            }
          }
        },
        "responses": {
          "204": {
            "description": "Successful Response"
          },
          "401": {
            "description": "Senha atual incorreta"
          },
          "422": {
            "description": "Validation Error",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/HTTPValidationError"
                }
              }
            }
          }
        }
      }
    },
    "/api/v1/auth/initial-setup": {
      "post": {
        "tags": [
          "Authentication"
        ],
        "summary": "Setup inicial para dirigente",
        "description": "Cria organização e temporada inicial para dirigente na primeira vez.\n\n**Requisitos:**\n- Usuário deve ser dirigente\n- Não deve ter organização cadastrada\n\n**O que é criado:**\n- Organização\n- Vínculo do dirigente com a organização\n- Temporada inicial (ativa)",
        "operationId": "initial_setup_api_v1_auth_initial_setup_post",
        "security": [
          {
            "HTTPBearer": []
          }
        ],
        "parameters": [
          {
            "name": "X-Request-ID",
            "in": "header",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "title": "X-Request-Id"
            }
          },
          {
            "name": "x-organization-id",
            "in": "header",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "title": "X-Organization-Id"
            }
          }
        ],
        "requestBody": {
          "required": true,
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/InitialSetupRequest"
              }
            }
          }
        },
        "responses": {
          "200": {
            "description": "Successful Response",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/InitialSetupResponse"
                }
              }
            }
          },
          "401": {
            "description": "Token inválido ou ausente"
          },
          "403": {
            "description": "Usuário não é dirigente ou já tem organização"
          },
          "422": {
            "description": "Dados inválidos"
          }
        }
      }
    },
    "/api/v1/categories": {
      "get": {
        "tags": [
          "lookup",
          "lookup"
        ],
        "summary": "Get Categories",
        "description": "Lista todas as categorias.",
        "operationId": "get_categories_api_v1_categories_get",
        "security": [
          {
            "HTTPBearer": []
          }
        ],
        "parameters": [
          {
            "name": "X-Request-ID",
            "in": "header",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "title": "X-Request-Id"
            }
          },
          {
            "name": "x-organization-id",
            "in": "header",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "title": "X-Organization-Id"
            }
          }
        ],
        "responses": {
          "200": {
            "description": "Successful Response",
            "content": {
              "application/json": {
                "schema": {
                  "type": "array",
                  "items": {
                    "$ref": "#/components/schemas/app__api__v1__routers__lookup__CategoryResponse"
                  },
                  "title": "Response Get Categories Api V1 Categories Get"
                }
              }
            }
          },
          "422": {
            "description": "Validation Error",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/HTTPValidationError"
                }
              }
            }
          }
        }
      },
      "post": {
        "tags": [
          "categories",
          "Categories"
        ],
        "summary": "Create Category",
        "description": "Cria nova categoria\n\nPermissões: coordenador, dirigente (R26)\n\nReferências RAG:\n- R15: Categorias globais definidas por idade\n- RDB11: Validação min_age <= max_age",
        "operationId": "create_category_api_v1_categories_post",
        "security": [
          {
            "HTTPBearer": []
          }
        ],
        "parameters": [
          {
            "name": "X-Request-ID",
            "in": "header",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "title": "X-Request-Id"
            }
          },
          {
            "name": "x-organization-id",
            "in": "header",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "title": "X-Organization-Id"
            }
          }
        ],
        "requestBody": {
          "required": true,
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/CategoryCreate"
              }
            }
          }
        },
        "responses": {
          "201": {
            "description": "Successful Response",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/app__schemas__categories__CategoryResponse"
                }
              }
            }
          },
          "422": {
            "description": "Validation Error",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/HTTPValidationError"
                }
              }
            }
          }
        }
      }
    },
    "/api/v1/categories/{category_id}": {
      "get": {
        "tags": [
          "categories",
          "Categories"
        ],
        "summary": "Get Category",
        "description": "Busca categoria por ID\n\nPermissões: coordenador, dirigente, treinador (R26)\n\nReferências RAG:\n- R15: Categorias globais",
        "operationId": "get_category_api_v1_categories__category_id__get",
        "security": [
          {
            "HTTPBearer": []
          }
        ],
        "parameters": [
          {
            "name": "category_id",
            "in": "path",
            "required": true,
            "schema": {
              "type": "integer",
              "title": "Category Id"
            }
          },
          {
            "name": "X-Request-ID",
            "in": "header",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "title": "X-Request-Id"
            }
          },
          {
            "name": "x-organization-id",
            "in": "header",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "title": "X-Organization-Id"
            }
          }
        ],
        "responses": {
          "200": {
            "description": "Successful Response",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/app__schemas__categories__CategoryResponse"
                }
              }
            }
          },
          "422": {
            "description": "Validation Error",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/HTTPValidationError"
                }
              }
            }
          }
        }
      },
      "put": {
        "tags": [
          "categories",
          "Categories"
        ],
        "summary": "Update Category",
        "description": "Atualiza categoria\n\nPermissões: coordenador, dirigente (R26)\n\nReferências RAG:\n- R15: Categorias globais\n- RDB11: Validação min_age <= max_age",
        "operationId": "update_category_api_v1_categories__category_id__put",
        "security": [
          {
            "HTTPBearer": []
          }
        ],
        "parameters": [
          {
            "name": "category_id",
            "in": "path",
            "required": true,
            "schema": {
              "type": "integer",
              "title": "Category Id"
            }
          },
          {
            "name": "X-Request-ID",
            "in": "header",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "title": "X-Request-Id"
            }
          },
          {
            "name": "x-organization-id",
            "in": "header",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "title": "X-Organization-Id"
            }
          }
        ],
        "requestBody": {
          "required": true,
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/CategoryUpdate"
              }
            }
          }
        },
        "responses": {
          "200": {
            "description": "Successful Response",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/app__schemas__categories__CategoryResponse"
                }
              }
            }
          },
          "422": {
            "description": "Validation Error",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/HTTPValidationError"
                }
              }
            }
          }
        }
      }
    },
    "/api/v1/seasons": {
      "get": {
        "tags": [
          "lookup",
          "lookup"
        ],
        "summary": "Get Seasons",
        "description": "Lista temporadas disponíveis.",
        "operationId": "get_seasons_api_v1_seasons_get",
        "security": [
          {
            "HTTPBearer": []
          }
        ],
        "parameters": [
          {
            "name": "organization_id",
            "in": "query",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "description": "Filtrar por organização",
              "title": "Organization Id"
            },
            "description": "Filtrar por organização"
          },
          {
            "name": "X-Request-ID",
            "in": "header",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "title": "X-Request-Id"
            }
          },
          {
            "name": "x-organization-id",
            "in": "header",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "title": "X-Organization-Id"
            }
          }
        ],
        "responses": {
          "200": {
            "description": "Successful Response",
            "content": {
              "application/json": {
                "schema": {
                  "type": "array",
                  "items": {
                    "$ref": "#/components/schemas/app__api__v1__routers__lookup__SeasonResponse"
                  },
                  "title": "Response Get Seasons Api V1 Seasons Get"
                }
              }
            }
          },
          "422": {
            "description": "Validation Error",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/HTTPValidationError"
                }
              }
            }
          }
        }
      },
      "post": {
        "tags": [
          "seasons",
          "seasons"
        ],
        "summary": "Criar temporada",
        "description": "Cria uma nova temporada.\n\n**Regras:**\n- RF4: Dirigentes, Coordenadores e Treinadores podem criar temporadas\n- R25/R26: Permissões por papel\n- RDB8: start_date < end_date (validado pelo DB)\n- 6.1.1: Status inicial será \"planejada\" (se start_date > hoje)",
        "operationId": "createSeason",
        "security": [
          {
            "HTTPBearer": []
          }
        ],
        "parameters": [
          {
            "name": "organization_id",
            "in": "query",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string",
                  "format": "uuid"
                },
                {
                  "type": "null"
                }
              ],
              "title": "Organization Id"
            }
          },
          {
            "name": "team_id",
            "in": "query",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string",
                  "format": "uuid"
                },
                {
                  "type": "null"
                }
              ],
              "title": "Team Id"
            }
          },
          {
            "name": "athlete_id",
            "in": "query",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string",
                  "format": "uuid"
                },
                {
                  "type": "null"
                }
              ],
              "title": "Athlete Id"
            }
          },
          {
            "name": "X-Request-ID",
            "in": "header",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "title": "X-Request-Id"
            }
          },
          {
            "name": "x-organization-id",
            "in": "header",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "title": "X-Organization-Id"
            }
          }
        ],
        "requestBody": {
          "required": true,
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/SeasonCreate"
              }
            }
          }
        },
        "responses": {
          "201": {
            "description": "Temporada criada",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/app__schemas__seasons__SeasonResponse"
                }
              }
            }
          },
          "401": {
            "description": "Credencial ausente ou inválida"
          },
          "403": {
            "description": "Permissão insuficiente (R25/R26)"
          },
          "422": {
            "description": "Erro de validação"
          }
        }
      }
    },
    "/api/v1/seasons/{season_id}": {
      "get": {
        "tags": [
          "seasons",
          "seasons"
        ],
        "summary": "Obter temporada",
        "description": "Retorna detalhes de uma temporada específica.\n\n**Regras:** R25/R26 (permissões por papel)\n\n**Response inclui:**\n- status derivado conforme 6.1.1\n- deleted_at/deleted_reason se soft-deleted (RDB4)",
        "operationId": "getSeason",
        "security": [
          {
            "HTTPBearer": []
          }
        ],
        "parameters": [
          {
            "name": "season_id",
            "in": "path",
            "required": true,
            "schema": {
              "type": "string",
              "format": "uuid",
              "title": "Season Id"
            }
          },
          {
            "name": "organization_id",
            "in": "query",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string",
                  "format": "uuid"
                },
                {
                  "type": "null"
                }
              ],
              "title": "Organization Id"
            }
          },
          {
            "name": "team_id",
            "in": "query",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string",
                  "format": "uuid"
                },
                {
                  "type": "null"
                }
              ],
              "title": "Team Id"
            }
          },
          {
            "name": "athlete_id",
            "in": "query",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string",
                  "format": "uuid"
                },
                {
                  "type": "null"
                }
              ],
              "title": "Athlete Id"
            }
          },
          {
            "name": "X-Request-ID",
            "in": "header",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "title": "X-Request-Id"
            }
          },
          {
            "name": "x-organization-id",
            "in": "header",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "title": "X-Organization-Id"
            }
          }
        ],
        "responses": {
          "200": {
            "description": "Detalhes da temporada",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/app__schemas__seasons__SeasonResponse"
                }
              }
            }
          },
          "401": {
            "description": "Credencial ausente ou inválida"
          },
          "403": {
            "description": "Permissão insuficiente (R25/R26)"
          },
          "404": {
            "description": "Temporada não encontrada"
          },
          "422": {
            "description": "Validation Error",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/HTTPValidationError"
                }
              }
            }
          }
        }
      },
      "patch": {
        "tags": [
          "seasons",
          "seasons"
        ],
        "summary": "Atualizar temporada",
        "description": "Atualiza parcialmente uma temporada.\n\n**Regras:**\n- RF5: Não permite encerramento manual após início\n- RF5.2: NÃO editar se interrompida\n- R37: Após encerramento, edição só via ação administrativa auditada\n- RDB4: Soft delete via deleted_at/deleted_reason (não DELETE físico)\n- 6.1.1: Status é derivado, não editável diretamente",
        "operationId": "updateSeason",
        "security": [
          {
            "HTTPBearer": []
          }
        ],
        "parameters": [
          {
            "name": "season_id",
            "in": "path",
            "required": true,
            "schema": {
              "type": "string",
              "format": "uuid",
              "title": "Season Id"
            }
          },
          {
            "name": "organization_id",
            "in": "query",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string",
                  "format": "uuid"
                },
                {
                  "type": "null"
                }
              ],
              "title": "Organization Id"
            }
          },
          {
            "name": "team_id",
            "in": "query",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string",
                  "format": "uuid"
                },
                {
                  "type": "null"
                }
              ],
              "title": "Team Id"
            }
          },
          {
            "name": "athlete_id",
            "in": "query",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string",
                  "format": "uuid"
                },
                {
                  "type": "null"
                }
              ],
              "title": "Athlete Id"
            }
          },
          {
            "name": "X-Request-ID",
            "in": "header",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "title": "X-Request-Id"
            }
          },
          {
            "name": "x-organization-id",
            "in": "header",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "title": "X-Organization-Id"
            }
          }
        ],
        "requestBody": {
          "required": true,
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/SeasonUpdate"
              }
            }
          }
        },
        "responses": {
          "200": {
            "description": "Temporada atualizada",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/app__schemas__seasons__SeasonResponse"
                }
              }
            }
          },
          "401": {
            "description": "Credencial ausente ou inválida"
          },
          "403": {
            "description": "Permissão insuficiente (R25/R26)"
          },
          "404": {
            "description": "Temporada não encontrada"
          },
          "409": {
            "description": "season_locked - Temporada interrompida (RF5.2/R37)"
          },
          "422": {
            "description": "Erro de validação"
          }
        }
      },
      "delete": {
        "tags": [
          "seasons",
          "seasons"
        ],
        "summary": "Excluir temporada (soft delete)",
        "description": "Cancela uma temporada planejada (RF5.1).\n\n**Regras:**\n- RF5.1: Apenas temporada planejada e sem dados vinculados\n- R25/R26: Permissões por papel",
        "operationId": "deleteSeason",
        "security": [
          {
            "HTTPBearer": []
          }
        ],
        "parameters": [
          {
            "name": "season_id",
            "in": "path",
            "required": true,
            "schema": {
              "type": "string",
              "format": "uuid",
              "title": "Season Id"
            }
          },
          {
            "name": "organization_id",
            "in": "query",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string",
                  "format": "uuid"
                },
                {
                  "type": "null"
                }
              ],
              "title": "Organization Id"
            }
          },
          {
            "name": "team_id",
            "in": "query",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string",
                  "format": "uuid"
                },
                {
                  "type": "null"
                }
              ],
              "title": "Team Id"
            }
          },
          {
            "name": "athlete_id",
            "in": "query",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string",
                  "format": "uuid"
                },
                {
                  "type": "null"
                }
              ],
              "title": "Athlete Id"
            }
          },
          {
            "name": "X-Request-ID",
            "in": "header",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "title": "X-Request-Id"
            }
          },
          {
            "name": "x-organization-id",
            "in": "header",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "title": "X-Organization-Id"
            }
          }
        ],
        "responses": {
          "204": {
            "description": "Temporada excluída"
          },
          "401": {
            "description": "Credencial ausente ou inválida"
          },
          "403": {
            "description": "Permissão insuficiente (R25/R26)"
          },
          "404": {
            "description": "Temporada não encontrada"
          },
          "422": {
            "description": "Validation Error",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/HTTPValidationError"
                }
              }
            }
          }
        }
      }
    },
    "/api/v1/seasons/{season_id}/interrupt": {
      "post": {
        "tags": [
          "seasons",
          "seasons"
        ],
        "summary": "Interromper temporada",
        "description": "Interrompe uma temporada ativa por força maior.\n\n**Regras:**\n- RF5.2: Interrupção após início (força maior)\n- R37: Bloqueia criação/edição de novos eventos após interrupção\n- 6.1.1: Status muda para \"interrompida\"\n\n**Pré-condições:**\n- Temporada deve estar em status \"ativa\"\n\n**Payload obrigatório:** { \"reason\": \"...\" }",
        "operationId": "interruptSeason",
        "security": [
          {
            "HTTPBearer": []
          }
        ],
        "parameters": [
          {
            "name": "season_id",
            "in": "path",
            "required": true,
            "schema": {
              "type": "string",
              "format": "uuid",
              "title": "Season Id"
            }
          },
          {
            "name": "organization_id",
            "in": "query",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string",
                  "format": "uuid"
                },
                {
                  "type": "null"
                }
              ],
              "title": "Organization Id"
            }
          },
          {
            "name": "team_id",
            "in": "query",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string",
                  "format": "uuid"
                },
                {
                  "type": "null"
                }
              ],
              "title": "Team Id"
            }
          },
          {
            "name": "athlete_id",
            "in": "query",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string",
                  "format": "uuid"
                },
                {
                  "type": "null"
                }
              ],
              "title": "Athlete Id"
            }
          },
          {
            "name": "X-Request-ID",
            "in": "header",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "title": "X-Request-Id"
            }
          },
          {
            "name": "x-organization-id",
            "in": "header",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "title": "X-Organization-Id"
            }
          }
        ],
        "requestBody": {
          "required": true,
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/ReasonRequest"
              }
            }
          }
        },
        "responses": {
          "200": {
            "description": "Temporada interrompida",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/app__schemas__seasons__SeasonResponse"
                }
              }
            }
          },
          "401": {
            "description": "Credencial ausente ou inválida"
          },
          "403": {
            "description": "Permissão insuficiente (R25/R26)"
          },
          "404": {
            "description": "Temporada não encontrada"
          },
          "409": {
            "description": "invalid_state_transition - Temporada não está ativa"
          },
          "422": {
            "description": "Erro de validação"
          }
        }
      }
    },
    "/api/v1/seasons/{season_id}/cancel": {
      "post": {
        "tags": [
          "seasons",
          "seasons"
        ],
        "summary": "Cancelar temporada",
        "description": "Cancela uma temporada antes do início.\n\n**Regras:**\n- RF5.1: Cancelamento permitido apenas se a temporada não possuir dados vinculados\n- 6.1.1: Status muda para \"cancelada\"\n\n**Pré-condições:**\n- Temporada deve estar em status \"planejada\" (antes de start_date)\n- Não pode haver dados vinculados (equipes, jogos, treinos, etc.)\n\n**Payload obrigatório:** { \"reason\": \"...\" }",
        "operationId": "cancelSeason",
        "security": [
          {
            "HTTPBearer": []
          }
        ],
        "parameters": [
          {
            "name": "season_id",
            "in": "path",
            "required": true,
            "schema": {
              "type": "string",
              "format": "uuid",
              "title": "Season Id"
            }
          },
          {
            "name": "organization_id",
            "in": "query",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string",
                  "format": "uuid"
                },
                {
                  "type": "null"
                }
              ],
              "title": "Organization Id"
            }
          },
          {
            "name": "team_id",
            "in": "query",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string",
                  "format": "uuid"
                },
                {
                  "type": "null"
                }
              ],
              "title": "Team Id"
            }
          },
          {
            "name": "athlete_id",
            "in": "query",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string",
                  "format": "uuid"
                },
                {
                  "type": "null"
                }
              ],
              "title": "Athlete Id"
            }
          },
          {
            "name": "X-Request-ID",
            "in": "header",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "title": "X-Request-Id"
            }
          },
          {
            "name": "x-organization-id",
            "in": "header",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "title": "X-Organization-Id"
            }
          }
        ],
        "requestBody": {
          "required": true,
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/ReasonRequest"
              }
            }
          }
        },
        "responses": {
          "200": {
            "description": "Temporada cancelada",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/app__schemas__seasons__SeasonResponse"
                }
              }
            }
          },
          "401": {
            "description": "Credencial ausente ou inválida"
          },
          "403": {
            "description": "Permissão insuficiente (R25/R26)"
          },
          "404": {
            "description": "Temporada não encontrada"
          },
          "409": {
            "description": "Conflito - temporada não pode ser cancelada"
          },
          "422": {
            "description": "Erro de validação"
          }
        }
      }
    },
    "/api/v1/teams": {
      "get": {
        "tags": [
          "lookup",
          "lookup"
        ],
        "summary": "Get Teams",
        "description": "Lista equipes com filtros opcionais.",
        "operationId": "get_teams_api_v1_teams_get",
        "security": [
          {
            "HTTPBearer": []
          }
        ],
        "parameters": [
          {
            "name": "organization_id",
            "in": "query",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "description": "Filtrar por organização",
              "title": "Organization Id"
            },
            "description": "Filtrar por organização"
          },
          {
            "name": "season_id",
            "in": "query",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "description": "Filtrar por temporada",
              "title": "Season Id"
            },
            "description": "Filtrar por temporada"
          },
          {
            "name": "category_id",
            "in": "query",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "integer"
                },
                {
                  "type": "null"
                }
              ],
              "description": "Filtrar por categoria",
              "title": "Category Id"
            },
            "description": "Filtrar por categoria"
          },
          {
            "name": "X-Request-ID",
            "in": "header",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "title": "X-Request-Id"
            }
          },
          {
            "name": "x-organization-id",
            "in": "header",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "title": "X-Organization-Id"
            }
          }
        ],
        "responses": {
          "200": {
            "description": "Successful Response",
            "content": {
              "application/json": {
                "schema": {
                  "type": "array",
                  "items": {
                    "$ref": "#/components/schemas/TeamResponse"
                  },
                  "title": "Response Get Teams Api V1 Teams Get"
                }
              }
            }
          },
          "422": {
            "description": "Validation Error",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/HTTPValidationError"
                }
              }
            }
          }
        }
      },
      "post": {
        "tags": [
          "teams",
          "teams"
        ],
        "summary": "Create Team",
        "description": "Cria nova equipe.\nRegras: RF6\nStep 4: Implementar lógica role-based - treinador se auto-atribui",
        "operationId": "create_team_api_v1_teams_post",
        "security": [
          {
            "HTTPBearer": []
          }
        ],
        "parameters": [
          {
            "name": "organization_id",
            "in": "query",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string",
                  "format": "uuid"
                },
                {
                  "type": "null"
                }
              ],
              "title": "Organization Id"
            }
          },
          {
            "name": "team_id",
            "in": "query",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string",
                  "format": "uuid"
                },
                {
                  "type": "null"
                }
              ],
              "title": "Team Id"
            }
          },
          {
            "name": "athlete_id",
            "in": "query",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string",
                  "format": "uuid"
                },
                {
                  "type": "null"
                }
              ],
              "title": "Athlete Id"
            }
          },
          {
            "name": "X-Request-ID",
            "in": "header",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "title": "X-Request-Id"
            }
          },
          {
            "name": "x-organization-id",
            "in": "header",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "title": "X-Organization-Id"
            }
          }
        ],
        "requestBody": {
          "required": true,
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/TeamCreate"
              }
            }
          }
        },
        "responses": {
          "201": {
            "description": "Successful Response",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/TeamBase"
                }
              }
            }
          },
          "422": {
            "description": "Validation Error",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/HTTPValidationError"
                }
              }
            }
          }
        }
      }
    },
    "/api/v1/teams/{team_id}": {
      "get": {
        "tags": [
          "teams",
          "teams"
        ],
        "summary": "Get Team",
        "description": "Retorna equipe por ID.",
        "operationId": "get_team_api_v1_teams__team_id__get",
        "security": [
          {
            "HTTPBearer": []
          }
        ],
        "parameters": [
          {
            "name": "team_id",
            "in": "path",
            "required": true,
            "schema": {
              "anyOf": [
                {
                  "type": "string",
                  "format": "uuid"
                },
                {
                  "type": "null"
                }
              ],
              "title": "Team Id"
            }
          },
          {
            "name": "organization_id",
            "in": "query",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string",
                  "format": "uuid"
                },
                {
                  "type": "null"
                }
              ],
              "title": "Organization Id"
            }
          },
          {
            "name": "athlete_id",
            "in": "query",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string",
                  "format": "uuid"
                },
                {
                  "type": "null"
                }
              ],
              "title": "Athlete Id"
            }
          },
          {
            "name": "X-Request-ID",
            "in": "header",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "title": "X-Request-Id"
            }
          },
          {
            "name": "x-organization-id",
            "in": "header",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "title": "X-Organization-Id"
            }
          }
        ],
        "responses": {
          "200": {
            "description": "Successful Response",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/TeamBase"
                }
              }
            }
          },
          "422": {
            "description": "Validation Error",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/HTTPValidationError"
                }
              }
            }
          }
        }
      },
      "patch": {
        "tags": [
          "teams",
          "teams"
        ],
        "summary": "Update Team",
        "description": "Atualiza equipe. Regras: RF7, Step 2: Validação de permissão can_manage_teams",
        "operationId": "update_team_api_v1_teams__team_id__patch",
        "security": [
          {
            "HTTPBearer": []
          }
        ],
        "parameters": [
          {
            "name": "team_id",
            "in": "path",
            "required": true,
            "schema": {
              "anyOf": [
                {
                  "type": "string",
                  "format": "uuid"
                },
                {
                  "type": "null"
                }
              ],
              "title": "Team Id"
            }
          },
          {
            "name": "organization_id",
            "in": "query",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string",
                  "format": "uuid"
                },
                {
                  "type": "null"
                }
              ],
              "title": "Organization Id"
            }
          },
          {
            "name": "athlete_id",
            "in": "query",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string",
                  "format": "uuid"
                },
                {
                  "type": "null"
                }
              ],
              "title": "Athlete Id"
            }
          },
          {
            "name": "X-Request-ID",
            "in": "header",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "title": "X-Request-Id"
            }
          },
          {
            "name": "x-organization-id",
            "in": "header",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "title": "X-Organization-Id"
            }
          }
        ],
        "requestBody": {
          "required": true,
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/TeamUpdate"
              }
            }
          }
        },
        "responses": {
          "200": {
            "description": "Successful Response",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/TeamBase"
                }
              }
            }
          },
          "422": {
            "description": "Validation Error",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/HTTPValidationError"
                }
              }
            }
          }
        }
      },
      "delete": {
        "tags": [
          "teams",
          "teams"
        ],
        "summary": "Delete Team",
        "description": "Exclui equipe (soft delete). Regras: R29/R33\n\nComportamento:\n- Soft delete: marca deleted_at e deleted_reason\n- Não remove fisicamente do banco",
        "operationId": "delete_team_api_v1_teams__team_id__delete",
        "security": [
          {
            "HTTPBearer": []
          }
        ],
        "parameters": [
          {
            "name": "team_id",
            "in": "path",
            "required": true,
            "schema": {
              "anyOf": [
                {
                  "type": "string",
                  "format": "uuid"
                },
                {
                  "type": "null"
                }
              ],
              "title": "Team Id"
            }
          },
          {
            "name": "reason",
            "in": "query",
            "required": false,
            "schema": {
              "type": "string",
              "description": "Motivo da exclusão",
              "default": "Exclusão manual",
              "title": "Reason"
            },
            "description": "Motivo da exclusão"
          },
          {
            "name": "organization_id",
            "in": "query",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string",
                  "format": "uuid"
                },
                {
                  "type": "null"
                }
              ],
              "title": "Organization Id"
            }
          },
          {
            "name": "athlete_id",
            "in": "query",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string",
                  "format": "uuid"
                },
                {
                  "type": "null"
                }
              ],
              "title": "Athlete Id"
            }
          },
          {
            "name": "X-Request-ID",
            "in": "header",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "title": "X-Request-Id"
            }
          },
          {
            "name": "x-organization-id",
            "in": "header",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "title": "X-Organization-Id"
            }
          }
        ],
        "responses": {
          "204": {
            "description": "Successful Response"
          },
          "422": {
            "description": "Validation Error",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/HTTPValidationError"
                }
              }
            }
          }
        }
      }
    },
    "/api/v1/teams/{team_id}/settings": {
      "patch": {
        "tags": [
          "teams",
          "teams"
        ],
        "summary": "Update Team Settings",
        "description": "Atualiza configurações da equipe (Step 15).\n\nPermite ajustar o alert_threshold_multiplier que controla a sensibilidade\ndos alertas de wellness automáticos.\n\nValores recomendados:\n- 1.5: Juvenis (mais sensível)\n- 2.0: Padrão adultos\n- 2.5: Adultos tolerantes (menos alertas)\n\nPermissões: Dirigente, Coordenador, ou Treinador responsável",
        "operationId": "update_team_settings_api_v1_teams__team_id__settings_patch",
        "security": [
          {
            "HTTPBearer": []
          }
        ],
        "parameters": [
          {
            "name": "team_id",
            "in": "path",
            "required": true,
            "schema": {
              "anyOf": [
                {
                  "type": "string",
                  "format": "uuid"
                },
                {
                  "type": "null"
                }
              ],
              "title": "Team Id"
            }
          },
          {
            "name": "organization_id",
            "in": "query",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string",
                  "format": "uuid"
                },
                {
                  "type": "null"
                }
              ],
              "title": "Organization Id"
            }
          },
          {
            "name": "athlete_id",
            "in": "query",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string",
                  "format": "uuid"
                },
                {
                  "type": "null"
                }
              ],
              "title": "Athlete Id"
            }
          },
          {
            "name": "X-Request-ID",
            "in": "header",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "title": "X-Request-Id"
            }
          },
          {
            "name": "x-organization-id",
            "in": "header",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "title": "X-Organization-Id"
            }
          }
        ],
        "requestBody": {
          "required": true,
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/TeamSettingsUpdate"
              }
            }
          }
        },
        "responses": {
          "200": {
            "description": "Successful Response",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/TeamBase"
                }
              }
            }
          },
          "422": {
            "description": "Validation Error",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/HTTPValidationError"
                }
              }
            }
          }
        }
      }
    },
    "/api/v1/teams/{team_id}/coach": {
      "patch": {
        "tags": [
          "teams",
          "teams"
        ],
        "summary": "Reatribuir treinador da equipe",
        "description": "Substitui o treinador atual por um novo.\n\n**Steps 18 + 21:** Endpoint com notificações integradas.\n\n**Ordem de operações:**\n1. Busca equipe e valida coach antigo\n2. Busca dados do coach antigo (user_id, nome)\n3. **PRIMEIRO:** Encerra vínculo antigo (end_at, status='inativo')\n4. Valida novo coach (role_id=3, ativo, mesma org)\n5. **DEPOIS:** Cria novo TeamMembership\n6. Atualiza team.coach_membership_id\n7. Commit\n8. Envia notificação + email ao novo coach\n9. Envia notificação ao coach antigo (removido)\n\n**Permissão:** Dirigente ou Coordenador",
        "operationId": "reassign_team_coach_api_v1_teams__team_id__coach_patch",
        "security": [
          {
            "HTTPBearer": []
          }
        ],
        "parameters": [
          {
            "name": "team_id",
            "in": "path",
            "required": true,
            "schema": {
              "anyOf": [
                {
                  "type": "string",
                  "format": "uuid"
                },
                {
                  "type": "null"
                }
              ],
              "title": "Team Id"
            }
          },
          {
            "name": "organization_id",
            "in": "query",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string",
                  "format": "uuid"
                },
                {
                  "type": "null"
                }
              ],
              "title": "Organization Id"
            }
          },
          {
            "name": "athlete_id",
            "in": "query",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string",
                  "format": "uuid"
                },
                {
                  "type": "null"
                }
              ],
              "title": "Athlete Id"
            }
          },
          {
            "name": "X-Request-ID",
            "in": "header",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "title": "X-Request-Id"
            }
          },
          {
            "name": "x-organization-id",
            "in": "header",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "title": "X-Organization-Id"
            }
          }
        ],
        "requestBody": {
          "required": true,
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/TeamCoachUpdate"
              }
            }
          }
        },
        "responses": {
          "200": {
            "description": "Coach reatribuído com sucesso",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/TeamBase"
                }
              }
            }
          },
          "400": {
            "description": "Validação falhou (novo coach inválido)"
          },
          "403": {
            "description": "Permissão insuficiente"
          },
          "404": {
            "description": "Equipe não encontrada"
          },
          "422": {
            "description": "Validation Error",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/HTTPValidationError"
                }
              }
            }
          }
        }
      }
    },
    "/api/v1/teams/{team_id}/coaches/history": {
      "get": {
        "tags": [
          "teams",
          "teams"
        ],
        "summary": "Histórico de treinadores da equipe",
        "description": "Retorna todos os treinadores que já foram vinculados à equipe (ativos e inativos).\n\n**Step 19:** Endpoint de histórico de coaches.\n\n**Consulta:**\n- Busca todos TeamMemberships onde OrgMembership.role_id == 3 (treinador)\n- Ordena por start_at DESC (mais recente primeiro)\n- Inclui coach atual (end_at IS NULL) e coaches anteriores (end_at preenchido)\n\n**Permissão:** Qualquer membro da equipe",
        "operationId": "get_team_coaches_history_api_v1_teams__team_id__coaches_history_get",
        "security": [
          {
            "HTTPBearer": []
          }
        ],
        "parameters": [
          {
            "name": "team_id",
            "in": "path",
            "required": true,
            "schema": {
              "anyOf": [
                {
                  "type": "string",
                  "format": "uuid"
                },
                {
                  "type": "null"
                }
              ],
              "title": "Team Id"
            }
          },
          {
            "name": "organization_id",
            "in": "query",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string",
                  "format": "uuid"
                },
                {
                  "type": "null"
                }
              ],
              "title": "Organization Id"
            }
          },
          {
            "name": "athlete_id",
            "in": "query",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string",
                  "format": "uuid"
                },
                {
                  "type": "null"
                }
              ],
              "title": "Athlete Id"
            }
          },
          {
            "name": "X-Request-ID",
            "in": "header",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "title": "X-Request-Id"
            }
          },
          {
            "name": "x-organization-id",
            "in": "header",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "title": "X-Organization-Id"
            }
          }
        ],
        "responses": {
          "200": {
            "description": "Histórico retornado com sucesso",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/TeamCoachHistoryResponse"
                }
              }
            }
          },
          "403": {
            "description": "Permissão insuficiente"
          },
          "404": {
            "description": "Equipe não encontrada"
          },
          "422": {
            "description": "Validation Error",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/HTTPValidationError"
                }
              }
            }
          }
        }
      }
    },
    "/api/v1/teams/{team_id}/members/{membership_id}/resend-invite": {
      "post": {
        "tags": [
          "teams",
          "teams"
        ],
        "summary": "Resend Team Member Invite",
        "description": "Reenvia convite para membro pendente da equipe.\n\n**Regras:**\n- Apenas membros com status='pendente'\n- Cooldown de 48h entre reenvios (configurável via INVITE_RESEND_COOLDOWN_HOURS)\n- Máximo de 3 reenvios por convite (configurável via INVITE_MAX_RESEND_COUNT)\n- Incrementa resend_count a cada reenvio\n- Atualiza updated_at para marcar último reenvio\n- Busca PasswordReset vinculado ao email da pessoa\n- Atualiza created_at do token para resetar expiry\n- Reenvia email de convite\n\n**Permissões:** Dirigente ou Coordenador\n\n**Step 16** do plano de gestão de staff.",
        "operationId": "resend_team_member_invite_api_v1_teams__team_id__members__membership_id__resend_invite_post",
        "security": [
          {
            "HTTPBearer": []
          }
        ],
        "parameters": [
          {
            "name": "team_id",
            "in": "path",
            "required": true,
            "schema": {
              "anyOf": [
                {
                  "type": "string",
                  "format": "uuid"
                },
                {
                  "type": "null"
                }
              ],
              "title": "Team Id"
            }
          },
          {
            "name": "membership_id",
            "in": "path",
            "required": true,
            "schema": {
              "type": "string",
              "format": "uuid",
              "title": "Membership Id"
            }
          },
          {
            "name": "organization_id",
            "in": "query",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string",
                  "format": "uuid"
                },
                {
                  "type": "null"
                }
              ],
              "title": "Organization Id"
            }
          },
          {
            "name": "athlete_id",
            "in": "query",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string",
                  "format": "uuid"
                },
                {
                  "type": "null"
                }
              ],
              "title": "Athlete Id"
            }
          },
          {
            "name": "X-Request-ID",
            "in": "header",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "title": "X-Request-Id"
            }
          },
          {
            "name": "x-organization-id",
            "in": "header",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "title": "X-Organization-Id"
            }
          }
        ],
        "responses": {
          "200": {
            "description": "Successful Response",
            "content": {
              "application/json": {
                "schema": {}
              }
            }
          },
          "422": {
            "description": "Validation Error",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/HTTPValidationError"
                }
              }
            }
          }
        }
      }
    },
    "/api/v1/teams/{team_id}/members/{membership_id}/cancel-invite": {
      "delete": {
        "tags": [
          "teams",
          "teams"
        ],
        "summary": "Cancel Team Member Invite",
        "description": "Cancela convite pendente de membro da equipe.\n\n**Ações:**\n- Busca TeamMembership com status='pendente'\n- Busca PasswordReset vinculado ao usuário\n- Marca token como usado (used_at = now) para desativar\n- Soft delete do TeamMembership\n- **NÃO envia email ao convidado** (cancelamento silencioso)\n\n**Permissões:** Dirigente ou Coordenador\n\n**Step 16** do plano de gestão de staff.",
        "operationId": "cancel_team_member_invite_api_v1_teams__team_id__members__membership_id__cancel_invite_delete",
        "security": [
          {
            "HTTPBearer": []
          }
        ],
        "parameters": [
          {
            "name": "team_id",
            "in": "path",
            "required": true,
            "schema": {
              "anyOf": [
                {
                  "type": "string",
                  "format": "uuid"
                },
                {
                  "type": "null"
                }
              ],
              "title": "Team Id"
            }
          },
          {
            "name": "membership_id",
            "in": "path",
            "required": true,
            "schema": {
              "type": "string",
              "format": "uuid",
              "title": "Membership Id"
            }
          },
          {
            "name": "organization_id",
            "in": "query",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string",
                  "format": "uuid"
                },
                {
                  "type": "null"
                }
              ],
              "title": "Organization Id"
            }
          },
          {
            "name": "athlete_id",
            "in": "query",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string",
                  "format": "uuid"
                },
                {
                  "type": "null"
                }
              ],
              "title": "Athlete Id"
            }
          },
          {
            "name": "X-Request-ID",
            "in": "header",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "title": "X-Request-Id"
            }
          },
          {
            "name": "x-organization-id",
            "in": "header",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "title": "X-Organization-Id"
            }
          }
        ],
        "responses": {
          "200": {
            "description": "Successful Response",
            "content": {
              "application/json": {
                "schema": {}
              }
            }
          },
          "422": {
            "description": "Validation Error",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/HTTPValidationError"
                }
              }
            }
          }
        }
      }
    },
    "/api/v1/teams/{team_id}/registrations": {
      "post": {
        "tags": [
          "teams",
          "teams"
        ],
        "summary": "Mover atleta para equipe",
        "description": "Move atleta para equipe na temporada.\n\n- Encerra inscricoes ativas na temporada (RDB10)\n- Cria nova inscricao na equipe alvo",
        "operationId": "moveAthleteToTeam",
        "security": [
          {
            "HTTPBearer": []
          }
        ],
        "parameters": [
          {
            "name": "team_id",
            "in": "path",
            "required": true,
            "schema": {
              "anyOf": [
                {
                  "type": "string",
                  "format": "uuid"
                },
                {
                  "type": "null"
                }
              ],
              "title": "Team Id"
            }
          },
          {
            "name": "organization_id",
            "in": "query",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string",
                  "format": "uuid"
                },
                {
                  "type": "null"
                }
              ],
              "title": "Organization Id"
            }
          },
          {
            "name": "athlete_id",
            "in": "query",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string",
                  "format": "uuid"
                },
                {
                  "type": "null"
                }
              ],
              "title": "Athlete Id"
            }
          },
          {
            "name": "X-Request-ID",
            "in": "header",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "title": "X-Request-Id"
            }
          },
          {
            "name": "x-organization-id",
            "in": "header",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "title": "X-Organization-Id"
            }
          }
        ],
        "requestBody": {
          "required": true,
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/TeamRegistrationMoveRequest"
              }
            }
          }
        },
        "responses": {
          "201": {
            "description": "Inscricao criada com sucesso",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/TeamRegistration"
                }
              }
            }
          },
          "401": {
            "description": "Token invalido ou ausente"
          },
          "403": {
            "description": "Permissao insuficiente"
          },
          "404": {
            "description": "Atleta ou equipe nao encontrada"
          },
          "409": {
            "description": "Periodo sobreposto (RDB10)"
          },
          "422": {
            "description": "Validation Error",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/HTTPValidationError"
                }
              }
            }
          }
        }
      },
      "get": {
        "tags": [
          "team-registrations",
          "team-registrations"
        ],
        "summary": "Listar inscrições de uma equipe",
        "operationId": "list_team_registrations_api_v1_teams__team_id__registrations_get",
        "security": [
          {
            "HTTPBearer": []
          }
        ],
        "parameters": [
          {
            "name": "team_id",
            "in": "path",
            "required": true,
            "schema": {
              "anyOf": [
                {
                  "type": "string",
                  "format": "uuid"
                },
                {
                  "type": "null"
                }
              ],
              "title": "Team Id"
            }
          },
          {
            "name": "athlete_id",
            "in": "query",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string",
                  "format": "uuid"
                },
                {
                  "type": "null"
                }
              ],
              "title": "Athlete Id"
            }
          },
          {
            "name": "season_id",
            "in": "query",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string",
                  "format": "uuid"
                },
                {
                  "type": "null"
                }
              ],
              "description": "Filtrar por temporada",
              "title": "Season Id"
            },
            "description": "Filtrar por temporada"
          },
          {
            "name": "active_only",
            "in": "query",
            "required": false,
            "schema": {
              "type": "boolean",
              "description": "Apenas inscrições ativas",
              "default": false,
              "title": "Active Only"
            },
            "description": "Apenas inscrições ativas"
          },
          {
            "name": "page",
            "in": "query",
            "required": false,
            "schema": {
              "type": "integer",
              "minimum": 1,
              "description": "Página",
              "default": 1,
              "title": "Page"
            },
            "description": "Página"
          },
          {
            "name": "limit",
            "in": "query",
            "required": false,
            "schema": {
              "type": "integer",
              "maximum": 200,
              "minimum": 1,
              "description": "Itens por página",
              "default": 50,
              "title": "Limit"
            },
            "description": "Itens por página"
          },
          {
            "name": "organization_id",
            "in": "query",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string",
                  "format": "uuid"
                },
                {
                  "type": "null"
                }
              ],
              "title": "Organization Id"
            }
          },
          {
            "name": "X-Request-ID",
            "in": "header",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "title": "X-Request-Id"
            }
          },
          {
            "name": "x-organization-id",
            "in": "header",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "title": "X-Organization-Id"
            }
          }
        ],
        "responses": {
          "200": {
            "description": "Successful Response",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/TeamRegistrationPaginatedResponse"
                }
              }
            }
          },
          "422": {
            "description": "Validation Error",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/HTTPValidationError"
                }
              }
            }
          }
        }
      }
    },
    "/api/v1/teams/{team_id}/wellness-top-performers": {
      "get": {
        "tags": [
          "teams",
          "teams"
        ],
        "summary": "Get Team Wellness Top Performers",
        "description": "Retorna Top 5 atletas com melhor taxa de resposta de wellness\n\nRelatório de desempenho dos atletas mais comprometidos com wellness.\n\nArgs:\n    team_id: ID do team\n    month: Mês específico (YYYY-MM) ou None para mês anterior\n    \nReturns:\n    {\n        \"month\": \"2026-01\",\n        \"team_id\": \"uuid\",\n        \"team_name\": \"Sub-20\",\n        \"top_performers\": [\n            {\n                \"athlete_id\": 10,\n                \"athlete_name\": \"João Silva\",\n                \"response_rate\": 95.5,\n                \"badges_earned_count\": 3,\n                \"current_streak_months\": 2,\n                \"total_expected\": 20,\n                \"total_responded\": 19\n            }\n        ]\n    }\n\nOrdenação: Por response_rate DESC LIMIT 5\n\nAcesso:\n- Dirigente: Qualquer team da organização\n- Coordenador/Treinador: Apenas teams que coordena/treina",
        "operationId": "get_team_wellness_top_performers_api_v1_teams__team_id__wellness_top_performers_get",
        "security": [
          {
            "HTTPBearer": []
          }
        ],
        "parameters": [
          {
            "name": "team_id",
            "in": "path",
            "required": true,
            "schema": {
              "anyOf": [
                {
                  "type": "string",
                  "format": "uuid"
                },
                {
                  "type": "null"
                }
              ],
              "title": "Team Id"
            }
          },
          {
            "name": "month",
            "in": "query",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "description": "Mês de referência (YYYY-MM), default: mês anterior",
              "title": "Month"
            },
            "description": "Mês de referência (YYYY-MM), default: mês anterior"
          },
          {
            "name": "organization_id",
            "in": "query",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string",
                  "format": "uuid"
                },
                {
                  "type": "null"
                }
              ],
              "title": "Organization Id"
            }
          },
          {
            "name": "athlete_id",
            "in": "query",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string",
                  "format": "uuid"
                },
                {
                  "type": "null"
                }
              ],
              "title": "Athlete Id"
            }
          },
          {
            "name": "X-Request-ID",
            "in": "header",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "title": "X-Request-Id"
            }
          },
          {
            "name": "x-organization-id",
            "in": "header",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "title": "X-Organization-Id"
            }
          }
        ],
        "responses": {
          "200": {
            "description": "Successful Response",
            "content": {
              "application/json": {
                "schema": {}
              }
            }
          },
          "422": {
            "description": "Validation Error",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/HTTPValidationError"
                }
              }
            }
          }
        }
      }
    },
    "/api/v1/teams/{team_id}/staff": {
      "get": {
        "tags": [
          "teams",
          "teams"
        ],
        "summary": "Get Team Staff",
        "description": "Lista staff (treinadores) vinculados à equipe.\n\nRegras:\n- R25/R26: Permissões por papel\n- RF7: coach_membership_id principal\n\nReturns:\n    Lista de membros do staff com informações da pessoa",
        "operationId": "get_team_staff_api_v1_teams__team_id__staff_get",
        "security": [
          {
            "HTTPBearer": []
          }
        ],
        "parameters": [
          {
            "name": "team_id",
            "in": "path",
            "required": true,
            "schema": {
              "anyOf": [
                {
                  "type": "string",
                  "format": "uuid"
                },
                {
                  "type": "null"
                }
              ],
              "title": "Team Id"
            }
          },
          {
            "name": "active_only",
            "in": "query",
            "required": false,
            "schema": {
              "type": "boolean",
              "description": "Apenas vínculos ativos",
              "default": true,
              "title": "Active Only"
            },
            "description": "Apenas vínculos ativos"
          },
          {
            "name": "organization_id",
            "in": "query",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string",
                  "format": "uuid"
                },
                {
                  "type": "null"
                }
              ],
              "title": "Organization Id"
            }
          },
          {
            "name": "athlete_id",
            "in": "query",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string",
                  "format": "uuid"
                },
                {
                  "type": "null"
                }
              ],
              "title": "Athlete Id"
            }
          },
          {
            "name": "X-Request-ID",
            "in": "header",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "title": "X-Request-Id"
            }
          },
          {
            "name": "x-organization-id",
            "in": "header",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "title": "X-Organization-Id"
            }
          }
        ],
        "responses": {
          "200": {
            "description": "Successful Response",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/TeamStaffResponse"
                }
              }
            }
          },
          "422": {
            "description": "Validation Error",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/HTTPValidationError"
                }
              }
            }
          }
        }
      }
    },
    "/api/v1/teams/{team_id}/staff/{membership_id}": {
      "delete": {
        "tags": [
          "teams",
          "teams"
        ],
        "summary": "Remover membro do staff",
        "description": "Remove membro da comissão técnica (dirigente, coordenador ou treinador).\n\n**Step 35:** Endpoint universal com lógica condicional baseada no papel.\n\n**Comportamento:**\n- **SE treinador (role_id=3):**\n  - Encerra vínculo (end_at=now(), status='inativo')\n  - Remove referência team.coach_membership_id = NULL\n  - Envia notificação via WebSocket ao treinador removido\n  - Retorna {team_without_coach: true}\n- **SENÃO (dirigente/coordenador):**\n  - Soft delete (deleted_at=now(), deleted_reason)\n  - Retorna {team_without_coach: false}\n\n**Validações:**\n- 404: team ou membership não encontrado\n- 400: membership não pertence à equipe\n- 403: sem permissão (apenas dirigente/coordenador)\n\n**Permissão:** Dirigente ou Coordenador",
        "operationId": "remove_staff_member_api_v1_teams__team_id__staff__membership_id__delete",
        "security": [
          {
            "HTTPBearer": []
          }
        ],
        "parameters": [
          {
            "name": "team_id",
            "in": "path",
            "required": true,
            "schema": {
              "anyOf": [
                {
                  "type": "string",
                  "format": "uuid"
                },
                {
                  "type": "null"
                }
              ],
              "title": "Team Id"
            }
          },
          {
            "name": "membership_id",
            "in": "path",
            "required": true,
            "schema": {
              "type": "string",
              "format": "uuid",
              "title": "Membership Id"
            }
          },
          {
            "name": "organization_id",
            "in": "query",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string",
                  "format": "uuid"
                },
                {
                  "type": "null"
                }
              ],
              "title": "Organization Id"
            }
          },
          {
            "name": "athlete_id",
            "in": "query",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string",
                  "format": "uuid"
                },
                {
                  "type": "null"
                }
              ],
              "title": "Athlete Id"
            }
          },
          {
            "name": "X-Request-ID",
            "in": "header",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "title": "X-Request-Id"
            }
          },
          {
            "name": "x-organization-id",
            "in": "header",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "title": "X-Organization-Id"
            }
          }
        ],
        "responses": {
          "200": {
            "description": "Membro removido com sucesso",
            "content": {
              "application/json": {
                "schema": {}
              }
            }
          },
          "400": {
            "description": "Membership não pertence à equipe"
          },
          "403": {
            "description": "Permissão insuficiente"
          },
          "404": {
            "description": "Equipe ou membership não encontrado"
          },
          "422": {
            "description": "Validation Error",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/HTTPValidationError"
                }
              }
            }
          }
        }
      }
    },
    "/api/v1/athletes/stats": {
      "get": {
        "tags": [
          "athletes",
          "athletes"
        ],
        "summary": "Get Athlete Stats",
        "description": "Retorna estatísticas de atletas para dashboard (FASE 2).\n\nKPIs:\n- Total de atletas\n- Em captação (sem team_registration ativo)\n- Lesionadas (injured=true)\n- Suspensas (suspended_until >= hoje)\n- Por estado (ativa, dispensada, arquivada)\n- Por categoria",
        "operationId": "get_athlete_stats_api_v1_athletes_stats_get",
        "security": [
          {
            "HTTPBearer": []
          }
        ],
        "parameters": [
          {
            "name": "organization_id",
            "in": "query",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string",
                  "format": "uuid"
                },
                {
                  "type": "null"
                }
              ],
              "title": "Organization Id"
            }
          },
          {
            "name": "team_id",
            "in": "query",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string",
                  "format": "uuid"
                },
                {
                  "type": "null"
                }
              ],
              "title": "Team Id"
            }
          },
          {
            "name": "athlete_id",
            "in": "query",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string",
                  "format": "uuid"
                },
                {
                  "type": "null"
                }
              ],
              "title": "Athlete Id"
            }
          },
          {
            "name": "X-Request-ID",
            "in": "header",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "title": "X-Request-Id"
            }
          },
          {
            "name": "x-organization-id",
            "in": "header",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "title": "X-Organization-Id"
            }
          }
        ],
        "responses": {
          "200": {
            "description": "Successful Response",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/AthleteStatsResponse"
                }
              }
            }
          },
          "422": {
            "description": "Validation Error",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/HTTPValidationError"
                }
              }
            }
          }
        }
      }
    },
    "/api/v1/athletes/available-today": {
      "get": {
        "tags": [
          "athletes",
          "athletes"
        ],
        "summary": "Get Available Today",
        "description": "Retorna atletas disponíveis para jogar hoje (FASE 5.5).\n\nCritérios de disponibilidade:\n- state = 'ativa'\n- injured = false\n- suspended_until IS NULL OR suspended_until < hoje\n- Tem team_registration ativo\n\nRegras RAG:\n- R12: Estado 'ativa' é obrigatório\n- R13: injured=true e suspended_until bloqueiam participação em jogos",
        "operationId": "get_available_today_api_v1_athletes_available_today_get",
        "security": [
          {
            "HTTPBearer": []
          }
        ],
        "parameters": [
          {
            "name": "team_id",
            "in": "query",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string",
                  "format": "uuid"
                },
                {
                  "type": "null"
                }
              ],
              "title": "Team Id"
            }
          },
          {
            "name": "organization_id",
            "in": "query",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string",
                  "format": "uuid"
                },
                {
                  "type": "null"
                }
              ],
              "title": "Organization Id"
            }
          },
          {
            "name": "athlete_id",
            "in": "query",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string",
                  "format": "uuid"
                },
                {
                  "type": "null"
                }
              ],
              "title": "Athlete Id"
            }
          },
          {
            "name": "X-Request-ID",
            "in": "header",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "title": "X-Request-Id"
            }
          },
          {
            "name": "x-organization-id",
            "in": "header",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "title": "X-Organization-Id"
            }
          }
        ],
        "responses": {
          "200": {
            "description": "Successful Response",
            "content": {
              "application/json": {
                "schema": {}
              }
            }
          },
          "422": {
            "description": "Validation Error",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/HTTPValidationError"
                }
              }
            }
          }
        }
      }
    },
    "/api/v1/athletes": {
      "get": {
        "tags": [
          "athletes",
          "athletes"
        ],
        "summary": "List Athletes",
        "description": "Lista atletas da organização.\n\nV1.2 (Opção B - REGRAS.md):\n- Por padrão mostra TODAS as atletas da organização (com ou sem equipe)\n- Filtro has_team:\n  - true: apenas atletas COM team_registration ativo\n  - false: apenas atletas SEM team_registration ativo\n  - null/omitido: todas as atletas\n- RF1.1: Atleta pode existir sem equipe\n- R32: Atleta sem equipe não opera, mas aparece na lista",
        "operationId": "list_athletes_api_v1_athletes_get",
        "security": [
          {
            "HTTPBearer": []
          }
        ],
        "parameters": [
          {
            "name": "state",
            "in": "query",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "$ref": "#/components/schemas/AthleteStateEnum"
                },
                {
                  "type": "null"
                }
              ],
              "title": "State"
            }
          },
          {
            "name": "search",
            "in": "query",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "title": "Search"
            }
          },
          {
            "name": "team_id",
            "in": "query",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string",
                  "format": "uuid"
                },
                {
                  "type": "null"
                }
              ],
              "title": "Team Id"
            }
          },
          {
            "name": "has_team",
            "in": "query",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "boolean"
                },
                {
                  "type": "null"
                }
              ],
              "description": "Filtrar: true=com equipe, false=sem equipe, null=todas",
              "title": "Has Team"
            },
            "description": "Filtrar: true=com equipe, false=sem equipe, null=todas"
          },
          {
            "name": "page",
            "in": "query",
            "required": false,
            "schema": {
              "type": "integer",
              "minimum": 1,
              "default": 1,
              "title": "Page"
            }
          },
          {
            "name": "limit",
            "in": "query",
            "required": false,
            "schema": {
              "type": "integer",
              "maximum": 200,
              "minimum": 1,
              "default": 50,
              "title": "Limit"
            }
          },
          {
            "name": "organization_id",
            "in": "query",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string",
                  "format": "uuid"
                },
                {
                  "type": "null"
                }
              ],
              "title": "Organization Id"
            }
          },
          {
            "name": "athlete_id",
            "in": "query",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string",
                  "format": "uuid"
                },
                {
                  "type": "null"
                }
              ],
              "title": "Athlete Id"
            }
          },
          {
            "name": "X-Request-ID",
            "in": "header",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "title": "X-Request-Id"
            }
          },
          {
            "name": "x-organization-id",
            "in": "header",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "title": "X-Organization-Id"
            }
          }
        ],
        "responses": {
          "200": {
            "description": "Successful Response",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/AthletePaginatedResponse"
                }
              }
            }
          },
          "422": {
            "description": "Validation Error",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/HTTPValidationError"
                }
              }
            }
          }
        }
      },
      "post": {
        "tags": [
          "athletes",
          "athletes"
        ],
        "summary": "Create Athlete",
        "description": "Cria atleta.\n\nRF1.1: Vínculo com equipe é OPCIONAL no cadastro.\nRD13: Goleiras não podem ter posição ofensiva.",
        "operationId": "create_athlete_api_v1_athletes_post",
        "security": [
          {
            "HTTPBearer": []
          }
        ],
        "parameters": [
          {
            "name": "organization_id",
            "in": "query",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string",
                  "format": "uuid"
                },
                {
                  "type": "null"
                }
              ],
              "title": "Organization Id"
            }
          },
          {
            "name": "team_id",
            "in": "query",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string",
                  "format": "uuid"
                },
                {
                  "type": "null"
                }
              ],
              "title": "Team Id"
            }
          },
          {
            "name": "athlete_id",
            "in": "query",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string",
                  "format": "uuid"
                },
                {
                  "type": "null"
                }
              ],
              "title": "Athlete Id"
            }
          },
          {
            "name": "X-Request-ID",
            "in": "header",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "title": "X-Request-Id"
            }
          },
          {
            "name": "x-organization-id",
            "in": "header",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "title": "X-Organization-Id"
            }
          }
        ],
        "requestBody": {
          "required": true,
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/app__schemas__athletes_v2__AthleteCreate"
              }
            }
          }
        },
        "responses": {
          "201": {
            "description": "Successful Response",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/AthleteResponse"
                }
              }
            }
          },
          "422": {
            "description": "Validation Error",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/HTTPValidationError"
                }
              }
            }
          }
        }
      }
    },
    "/api/v1/athletes/{athlete_id}": {
      "get": {
        "tags": [
          "athletes",
          "athletes"
        ],
        "summary": "Get Athlete",
        "description": "Retorna atleta por ID.",
        "operationId": "get_athlete_api_v1_athletes__athlete_id__get",
        "security": [
          {
            "HTTPBearer": []
          }
        ],
        "parameters": [
          {
            "name": "athlete_id",
            "in": "path",
            "required": true,
            "schema": {
              "anyOf": [
                {
                  "type": "string",
                  "format": "uuid"
                },
                {
                  "type": "null"
                }
              ],
              "title": "Athlete Id"
            }
          },
          {
            "name": "organization_id",
            "in": "query",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string",
                  "format": "uuid"
                },
                {
                  "type": "null"
                }
              ],
              "title": "Organization Id"
            }
          },
          {
            "name": "team_id",
            "in": "query",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string",
                  "format": "uuid"
                },
                {
                  "type": "null"
                }
              ],
              "title": "Team Id"
            }
          },
          {
            "name": "X-Request-ID",
            "in": "header",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "title": "X-Request-Id"
            }
          },
          {
            "name": "x-organization-id",
            "in": "header",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "title": "X-Organization-Id"
            }
          }
        ],
        "responses": {
          "200": {
            "description": "Successful Response",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/AthleteResponse"
                }
              }
            }
          },
          "422": {
            "description": "Validation Error",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/HTTPValidationError"
                }
              }
            }
          }
        }
      },
      "patch": {
        "tags": [
          "athletes",
          "athletes"
        ],
        "summary": "Update Athlete",
        "description": "Atualiza atleta.",
        "operationId": "update_athlete_api_v1_athletes__athlete_id__patch",
        "security": [
          {
            "HTTPBearer": []
          }
        ],
        "parameters": [
          {
            "name": "athlete_id",
            "in": "path",
            "required": true,
            "schema": {
              "anyOf": [
                {
                  "type": "string",
                  "format": "uuid"
                },
                {
                  "type": "null"
                }
              ],
              "title": "Athlete Id"
            }
          },
          {
            "name": "organization_id",
            "in": "query",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string",
                  "format": "uuid"
                },
                {
                  "type": "null"
                }
              ],
              "title": "Organization Id"
            }
          },
          {
            "name": "team_id",
            "in": "query",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string",
                  "format": "uuid"
                },
                {
                  "type": "null"
                }
              ],
              "title": "Team Id"
            }
          },
          {
            "name": "X-Request-ID",
            "in": "header",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "title": "X-Request-Id"
            }
          },
          {
            "name": "x-organization-id",
            "in": "header",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "title": "X-Organization-Id"
            }
          }
        ],
        "requestBody": {
          "required": true,
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/AthleteUpdate"
              }
            }
          }
        },
        "responses": {
          "200": {
            "description": "Successful Response",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/AthleteResponse"
                }
              }
            }
          },
          "422": {
            "description": "Validation Error",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/HTTPValidationError"
                }
              }
            }
          }
        }
      },
      "delete": {
        "tags": [
          "athletes",
          "athletes"
        ],
        "summary": "Delete Athlete",
        "description": "Exclui atleta (soft delete - RDB4).\n\nComportamento:\n- Soft delete: marca deleted_at e deleted_reason\n- Encerra todos os team_registrations ativos",
        "operationId": "delete_athlete_api_v1_athletes__athlete_id__delete",
        "security": [
          {
            "HTTPBearer": []
          }
        ],
        "parameters": [
          {
            "name": "athlete_id",
            "in": "path",
            "required": true,
            "schema": {
              "anyOf": [
                {
                  "type": "string",
                  "format": "uuid"
                },
                {
                  "type": "null"
                }
              ],
              "title": "Athlete Id"
            }
          },
          {
            "name": "reason",
            "in": "query",
            "required": false,
            "schema": {
              "type": "string",
              "description": "Motivo da exclusão",
              "default": "Exclusão manual",
              "title": "Reason"
            },
            "description": "Motivo da exclusão"
          },
          {
            "name": "organization_id",
            "in": "query",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string",
                  "format": "uuid"
                },
                {
                  "type": "null"
                }
              ],
              "title": "Organization Id"
            }
          },
          {
            "name": "team_id",
            "in": "query",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string",
                  "format": "uuid"
                },
                {
                  "type": "null"
                }
              ],
              "title": "Team Id"
            }
          },
          {
            "name": "X-Request-ID",
            "in": "header",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "title": "X-Request-Id"
            }
          },
          {
            "name": "x-organization-id",
            "in": "header",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "title": "X-Organization-Id"
            }
          }
        ],
        "responses": {
          "204": {
            "description": "Successful Response"
          },
          "422": {
            "description": "Validation Error",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/HTTPValidationError"
                }
              }
            }
          }
        }
      }
    },
    "/api/v1/athletes/{athlete_id}/badges": {
      "get": {
        "tags": [
          "athletes",
          "athletes"
        ],
        "summary": "Get Athlete Badges",
        "description": "Retorna badges conquistados pelo atleta (Sistema de Gamificação).\n\nBadges disponíveis:\n- wellness_champion_monthly: Taxa de resposta >= 90% no mês\n- wellness_streak_3months: 3 meses consecutivos com badge monthly\n\nResposta:\n[\n    {\n        \"id\": 1,\n        \"badge_type\": \"wellness_champion_monthly\",\n        \"month_reference\": \"2026-01\",\n        \"response_rate\": 95.0,\n        \"earned_at\": \"2026-02-01T00:00:00\"\n    }\n]\n\nRegras:\n- Atleta pode ver apenas próprios badges\n- Staff pode ver badges de qualquer atleta do time",
        "operationId": "get_athlete_badges_api_v1_athletes__athlete_id__badges_get",
        "security": [
          {
            "HTTPBearer": []
          }
        ],
        "parameters": [
          {
            "name": "athlete_id",
            "in": "path",
            "required": true,
            "schema": {
              "anyOf": [
                {
                  "type": "string",
                  "format": "uuid"
                },
                {
                  "type": "null"
                }
              ],
              "title": "Athlete Id"
            }
          },
          {
            "name": "limit",
            "in": "query",
            "required": false,
            "schema": {
              "type": "integer",
              "maximum": 200,
              "minimum": 1,
              "default": 50,
              "title": "Limit"
            }
          },
          {
            "name": "organization_id",
            "in": "query",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string",
                  "format": "uuid"
                },
                {
                  "type": "null"
                }
              ],
              "title": "Organization Id"
            }
          },
          {
            "name": "team_id",
            "in": "query",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string",
                  "format": "uuid"
                },
                {
                  "type": "null"
                }
              ],
              "title": "Team Id"
            }
          },
          {
            "name": "X-Request-ID",
            "in": "header",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "title": "X-Request-Id"
            }
          },
          {
            "name": "x-organization-id",
            "in": "header",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "title": "X-Organization-Id"
            }
          }
        ],
        "responses": {
          "200": {
            "description": "Successful Response",
            "content": {
              "application/json": {
                "schema": {}
              }
            }
          },
          "422": {
            "description": "Validation Error",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/HTTPValidationError"
                }
              }
            }
          }
        }
      }
    },
    "/api/v1/athletes/{athlete_id}/history": {
      "get": {
        "tags": [
          "athletes",
          "athletes"
        ],
        "summary": "Get Athlete History",
        "description": "Retorna histórico de eventos da atleta (FASE 5.4 - Timeline).\n\nBusca eventos de:\n- audit_logs (ações auditadas)\n- team_registrations (vínculos)\n- medical_cases (casos médicos - se existir)\n\nRegras RAG:\n- R30: Ações críticas auditáveis\n- R31: Log obrigatório (actor_id, timestamp, action, context, old_value, new_value)\n- R34: Imutabilidade dos logs",
        "operationId": "get_athlete_history_api_v1_athletes__athlete_id__history_get",
        "security": [
          {
            "HTTPBearer": []
          }
        ],
        "parameters": [
          {
            "name": "athlete_id",
            "in": "path",
            "required": true,
            "schema": {
              "anyOf": [
                {
                  "type": "string",
                  "format": "uuid"
                },
                {
                  "type": "null"
                }
              ],
              "title": "Athlete Id"
            }
          },
          {
            "name": "event_type",
            "in": "query",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "description": "Filtrar por tipo de evento",
              "title": "Event Type"
            },
            "description": "Filtrar por tipo de evento"
          },
          {
            "name": "limit",
            "in": "query",
            "required": false,
            "schema": {
              "type": "integer",
              "maximum": 200,
              "minimum": 1,
              "default": 50,
              "title": "Limit"
            }
          },
          {
            "name": "organization_id",
            "in": "query",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string",
                  "format": "uuid"
                },
                {
                  "type": "null"
                }
              ],
              "title": "Organization Id"
            }
          },
          {
            "name": "team_id",
            "in": "query",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string",
                  "format": "uuid"
                },
                {
                  "type": "null"
                }
              ],
              "title": "Team Id"
            }
          },
          {
            "name": "X-Request-ID",
            "in": "header",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "title": "X-Request-Id"
            }
          },
          {
            "name": "x-organization-id",
            "in": "header",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "title": "X-Organization-Id"
            }
          }
        ],
        "responses": {
          "200": {
            "description": "Successful Response",
            "content": {
              "application/json": {
                "schema": {}
              }
            }
          },
          "422": {
            "description": "Validation Error",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/HTTPValidationError"
                }
              }
            }
          }
        }
      }
    },
    "/api/v1/memberships/{membership_id}": {
      "get": {
        "tags": [
          "memberships",
          "memberships"
        ],
        "summary": "Obter vínculo por ID",
        "description": "Retorna os dados de um vínculo específico.\n\n**Regras aplicáveis:** R25/R26 (permissões)",
        "operationId": "get_membership_by_id_api_v1_memberships__membership_id__get",
        "security": [
          {
            "HTTPBearer": []
          }
        ],
        "parameters": [
          {
            "name": "membership_id",
            "in": "path",
            "required": true,
            "schema": {
              "type": "string",
              "format": "uuid",
              "title": "Membership Id"
            }
          },
          {
            "name": "X-Request-ID",
            "in": "header",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "title": "X-Request-Id"
            }
          },
          {
            "name": "x-organization-id",
            "in": "header",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "title": "X-Organization-Id"
            }
          }
        ],
        "responses": {
          "200": {
            "description": "Successful Response",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/Membership"
                }
              }
            }
          },
          "401": {
            "description": "Token inválido ou ausente",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ErrorResponse"
                }
              }
            }
          },
          "403": {
            "description": "Permissão insuficiente",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ErrorResponse"
                }
              }
            }
          },
          "404": {
            "description": "Vínculo não encontrado",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ErrorResponse"
                }
              }
            }
          },
          "422": {
            "description": "Validation Error",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/HTTPValidationError"
                }
              }
            }
          }
        }
      },
      "patch": {
        "tags": [
          "memberships",
          "memberships"
        ],
        "summary": "Atualizar vínculo",
        "description": "Atualiza role_code e/ou is_active de um vínculo existente.\n\n**Regras aplicáveis:** R6/R7, RDB9, R25/R26",
        "operationId": "update_membership_api_v1_memberships__membership_id__patch",
        "security": [
          {
            "HTTPBearer": []
          }
        ],
        "parameters": [
          {
            "name": "membership_id",
            "in": "path",
            "required": true,
            "schema": {
              "type": "string",
              "format": "uuid",
              "title": "Membership Id"
            }
          },
          {
            "name": "X-Request-ID",
            "in": "header",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "title": "X-Request-Id"
            }
          },
          {
            "name": "x-organization-id",
            "in": "header",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "title": "X-Organization-Id"
            }
          }
        ],
        "requestBody": {
          "required": true,
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/MembershipUpdate"
              }
            }
          }
        },
        "responses": {
          "200": {
            "description": "Successful Response",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/Membership"
                }
              }
            }
          },
          "401": {
            "description": "Token inválido ou ausente",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ErrorResponse"
                }
              }
            }
          },
          "403": {
            "description": "Permissão insuficiente",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ErrorResponse"
                }
              }
            }
          },
          "404": {
            "description": "Vínculo não encontrado",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ErrorResponse"
                }
              }
            }
          },
          "422": {
            "description": "Payload inválido",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ErrorResponse"
                }
              }
            }
          }
        }
      }
    },
    "/api/v1/memberships/{membership_id}/end": {
      "post": {
        "tags": [
          "memberships",
          "memberships"
        ],
        "summary": "Encerrar vínculo",
        "description": "Encerra um vínculo ativo (soft delete via status=inativo).\n\n**Regras aplicáveis:** R7 (encerramento de vínculo)",
        "operationId": "end_membership_api_v1_memberships__membership_id__end_post",
        "security": [
          {
            "HTTPBearer": []
          }
        ],
        "parameters": [
          {
            "name": "membership_id",
            "in": "path",
            "required": true,
            "schema": {
              "type": "string",
              "format": "uuid",
              "title": "Membership Id"
            }
          },
          {
            "name": "end_date",
            "in": "query",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string",
                  "format": "date"
                },
                {
                  "type": "null"
                }
              ],
              "description": "Data de encerramento (default: hoje)",
              "title": "End Date"
            },
            "description": "Data de encerramento (default: hoje)"
          },
          {
            "name": "X-Request-ID",
            "in": "header",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "title": "X-Request-Id"
            }
          },
          {
            "name": "x-organization-id",
            "in": "header",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "title": "X-Organization-Id"
            }
          }
        ],
        "responses": {
          "200": {
            "description": "Successful Response",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/Membership"
                }
              }
            }
          },
          "401": {
            "description": "Token inválido ou ausente",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ErrorResponse"
                }
              }
            }
          },
          "403": {
            "description": "Permissão insuficiente",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ErrorResponse"
                }
              }
            }
          },
          "404": {
            "description": "Vínculo não encontrado",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ErrorResponse"
                }
              }
            }
          },
          "422": {
            "description": "Validation Error",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/HTTPValidationError"
                }
              }
            }
          }
        }
      }
    },
    "/api/v1/organizations/{organization_id}/memberships": {
      "get": {
        "tags": [
          "memberships",
          "memberships"
        ],
        "summary": "Listar vínculos por organização (paginado)",
        "description": "Lista paginada de vínculos (memberships) de uma organização.\n\n**Regras aplicáveis:** R6/R7, RDB9, R25/R26",
        "operationId": "list_memberships_by_organization_api_v1_organizations__organization_id__memberships_get",
        "security": [
          {
            "HTTPBearer": []
          }
        ],
        "parameters": [
          {
            "name": "organization_id",
            "in": "path",
            "required": true,
            "schema": {
              "type": "string",
              "format": "uuid",
              "title": "Organization Id"
            }
          },
          {
            "name": "page",
            "in": "query",
            "required": false,
            "schema": {
              "type": "integer",
              "minimum": 1,
              "description": "Número da página",
              "default": 1,
              "title": "Page"
            },
            "description": "Número da página"
          },
          {
            "name": "limit",
            "in": "query",
            "required": false,
            "schema": {
              "type": "integer",
              "maximum": 100,
              "minimum": 1,
              "description": "Itens por página",
              "default": 50,
              "title": "Limit"
            },
            "description": "Itens por página"
          },
          {
            "name": "order_by",
            "in": "query",
            "required": false,
            "schema": {
              "$ref": "#/components/schemas/MembershipOrderBy",
              "description": "Campo para ordenação",
              "default": "created_at"
            },
            "description": "Campo para ordenação"
          },
          {
            "name": "order_dir",
            "in": "query",
            "required": false,
            "schema": {
              "$ref": "#/components/schemas/OrderDirection",
              "description": "Direção da ordenação",
              "default": "desc"
            },
            "description": "Direção da ordenação"
          },
          {
            "name": "is_active",
            "in": "query",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "boolean"
                },
                {
                  "type": "null"
                }
              ],
              "description": "Filtrar por status ativo/inativo",
              "title": "Is Active"
            },
            "description": "Filtrar por status ativo/inativo"
          },
          {
            "name": "role_code",
            "in": "query",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "$ref": "#/components/schemas/RoleCode"
                },
                {
                  "type": "null"
                }
              ],
              "description": "Filtrar por papel",
              "title": "Role Code"
            },
            "description": "Filtrar por papel"
          },
          {
            "name": "X-Request-ID",
            "in": "header",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "title": "X-Request-Id"
            }
          },
          {
            "name": "x-organization-id",
            "in": "header",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "title": "X-Organization-Id"
            }
          }
        ],
        "responses": {
          "200": {
            "description": "Successful Response",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/MembershipPaginatedResponse"
                }
              }
            }
          },
          "401": {
            "description": "Token inválido ou ausente",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ErrorResponse"
                }
              }
            }
          },
          "403": {
            "description": "Permissão insuficiente",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ErrorResponse"
                }
              }
            }
          },
          "422": {
            "description": "Validation Error",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/HTTPValidationError"
                }
              }
            }
          }
        }
      },
      "post": {
        "tags": [
          "memberships",
          "memberships"
        ],
        "summary": "Criar vínculo para organização",
        "description": "Cria um novo vínculo (membership) user↔organization+role.\n\n**Regras aplicáveis:** R6/R7, RDB9 (exclusividade)",
        "operationId": "create_membership_for_organization_api_v1_organizations__organization_id__memberships_post",
        "security": [
          {
            "HTTPBearer": []
          }
        ],
        "parameters": [
          {
            "name": "organization_id",
            "in": "path",
            "required": true,
            "schema": {
              "type": "string",
              "format": "uuid",
              "title": "Organization Id"
            }
          },
          {
            "name": "X-Request-ID",
            "in": "header",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "title": "X-Request-Id"
            }
          },
          {
            "name": "x-organization-id",
            "in": "header",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "title": "X-Organization-Id"
            }
          }
        ],
        "requestBody": {
          "required": true,
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/app__schemas__rbac__MembershipCreate"
              }
            }
          }
        },
        "responses": {
          "201": {
            "description": "Successful Response",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/Membership"
                }
              }
            }
          },
          "401": {
            "description": "Token inválido ou ausente",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ErrorResponse"
                }
              }
            }
          },
          "403": {
            "description": "Permissão insuficiente",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ErrorResponse"
                }
              }
            }
          },
          "409": {
            "description": "Vínculo ativo duplicado (RDB9)",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ErrorResponse"
                }
              }
            }
          },
          "422": {
            "description": "Payload inválido",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ErrorResponse"
                }
              }
            }
          }
        }
      }
    },
    "/api/v1/competitions": {
      "get": {
        "tags": [
          "competitions",
          "competitions"
        ],
        "summary": "Listar competições",
        "description": "Lista paginada de competições da organização.\n\n**Regras aplicáveis:**\n- R25/R26: Permissões por papel e escopo\n- R34: Clube único na V1 (contexto implícito do token)\n- R42: Modo somente leitura sem vínculo ativo\n\n**Filtros disponíveis:**\n- name: filtro por nome (case-insensitive, ilike)\n- kind: filtro por tipo de competição\n\n**Ordenação:**\n- order_by: created_at (padrão), name, updated_at\n- order_dir: desc (padrão), asc\n\n**Paginação:**\n- page: Número da página (1-indexed)\n- limit: Itens por página (1-100, padrão 50)\n\n**Envelope de resposta:** {items, page, limit, total}",
        "operationId": "listCompetitions",
        "security": [
          {
            "HTTPBearer": []
          }
        ],
        "parameters": [
          {
            "name": "page",
            "in": "query",
            "required": false,
            "schema": {
              "type": "integer",
              "minimum": 1,
              "description": "Número da página (1-indexed)",
              "default": 1,
              "title": "Page"
            },
            "description": "Número da página (1-indexed)"
          },
          {
            "name": "limit",
            "in": "query",
            "required": false,
            "schema": {
              "type": "integer",
              "maximum": 100,
              "minimum": 1,
              "description": "Itens por página (máximo 100)",
              "default": 50,
              "title": "Limit"
            },
            "description": "Itens por página (máximo 100)"
          },
          {
            "name": "order_by",
            "in": "query",
            "required": false,
            "schema": {
              "type": "string",
              "pattern": "^(created_at|name|updated_at)$",
              "description": "Campo para ordenação",
              "default": "created_at",
              "title": "Order By"
            },
            "description": "Campo para ordenação"
          },
          {
            "name": "order_dir",
            "in": "query",
            "required": false,
            "schema": {
              "type": "string",
              "pattern": "^(asc|desc)$",
              "description": "Direção da ordenação",
              "default": "desc",
              "title": "Order Dir"
            },
            "description": "Direção da ordenação"
          },
          {
            "name": "name",
            "in": "query",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "description": "Filtro por nome (case-insensitive)",
              "title": "Name"
            },
            "description": "Filtro por nome (case-insensitive)"
          },
          {
            "name": "kind",
            "in": "query",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "description": "Filtro por tipo de competição",
              "title": "Kind"
            },
            "description": "Filtro por tipo de competição"
          },
          {
            "name": "X-Request-ID",
            "in": "header",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "title": "X-Request-Id"
            }
          },
          {
            "name": "x-organization-id",
            "in": "header",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "title": "X-Organization-Id"
            }
          }
        ],
        "responses": {
          "200": {
            "description": "Lista paginada de competições",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/CompetitionPaginatedResponse"
                }
              }
            }
          },
          "401": {
            "description": "Token inválido ou ausente",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ErrorResponse"
                }
              }
            }
          },
          "403": {
            "description": "Permissão insuficiente (R25/R26)",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ErrorResponse"
                }
              }
            }
          },
          "422": {
            "description": "Validation Error",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/HTTPValidationError"
                }
              }
            }
          }
        }
      },
      "post": {
        "tags": [
          "competitions",
          "competitions"
        ],
        "summary": "Criar competição",
        "description": "Cria uma nova competição (registro base).\n\n**Regras aplicáveis:**\n- R25/R26: Permissões por papel e escopo\n- R29: Exclusão lógica (sem delete físico)\n- R34: Clube único na V1 (organization_id do contexto)\n\n**Campos obrigatórios:**\n- name: Nome da competição\n\n**Campo kind:**\nTexto livre. Exemplos: \"official\", \"friendly\", \"training-game\"\n\n**Nota:** A organização é determinada automaticamente pelo token de autenticação.",
        "operationId": "createCompetition",
        "security": [
          {
            "HTTPBearer": []
          }
        ],
        "parameters": [
          {
            "name": "organization_id",
            "in": "query",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string",
                  "format": "uuid"
                },
                {
                  "type": "null"
                }
              ],
              "title": "Organization Id"
            }
          },
          {
            "name": "team_id",
            "in": "query",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string",
                  "format": "uuid"
                },
                {
                  "type": "null"
                }
              ],
              "title": "Team Id"
            }
          },
          {
            "name": "athlete_id",
            "in": "query",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string",
                  "format": "uuid"
                },
                {
                  "type": "null"
                }
              ],
              "title": "Athlete Id"
            }
          },
          {
            "name": "X-Request-ID",
            "in": "header",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "title": "X-Request-Id"
            }
          },
          {
            "name": "x-organization-id",
            "in": "header",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "title": "X-Organization-Id"
            }
          }
        ],
        "requestBody": {
          "required": true,
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/CompetitionCreate"
              }
            }
          }
        },
        "responses": {
          "201": {
            "description": "Competição criada com sucesso",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/Competition"
                }
              }
            }
          },
          "401": {
            "description": "Token inválido ou ausente",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ErrorResponse"
                }
              }
            }
          },
          "403": {
            "description": "Permissão insuficiente (R25/R26)",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ErrorResponse"
                }
              }
            }
          },
          "422": {
            "description": "Erro de validação",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ErrorResponse"
                }
              }
            }
          }
        }
      }
    },
    "/api/v1/competitions/{competition_id}": {
```
