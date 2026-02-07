<!-- STATUS: DEPRECATED | replaced by docs/README.md -->

# 🗺️ MAPA COMPLETO DA DOCUMENTAÇÃO - HB Track

**Última atualização**: 14/01/2026  
**Reorganização**: ✅ Concluída em 14/01/2026  
**Última implementação**: Validação de Categoria no Welcome (14/01/2026)

> **Início Rápido**: Se você está perdido, comece pelo [_INDICE.md](./_INDICE.md)

---

## 🔄 REORGANIZAÇÃO REALIZADA (14/01/2026)

### ✅ O que foi reorganizado:
- **Removidos**: arquivos temporários (`tmpclaude-*`)
- **Criadas**: 3 novas pastas organizacionais
- **Movidos**: 8 arquivos para pastas apropriadas
- **Consolidados**: resumos executivos em pasta dedicada

### 📊 Nova estrutura:
- **06-certificacao-deploy/** - Documentos de certificação e deploy
- **07-organizacao-limpeza/** - Procedimentos de manutenção
- **08-resumos-executivos/** - Todos os resumos executivos centralizados

---

## 📁 Estrutura de Pastas

### 📂 01-sistema-atual/
**O que é**: Documentação oficial do sistema em produção/staging  
**Quando usar**: Para entender como o sistema funciona AGORA

| Arquivo | Descrição | Status |
|---------|-----------|--------|
| `STATUS_GERAL_TEAMS_STAGING.md` | Status completo do módulo Teams pronto para staging | ✅ Atual |
| `MANUAL_SISTEMA_HBTRACK.md` | Manual do usuário do sistema completo | ✅ Atual |
| `ARQUITETURA_PERMISSOES_CANONICAS.md` | Como funciona o sistema RBAC e permissões | ✅ Atual |
| `RBAC_MATRIX.md` | Matriz de permissões por papel | ✅ Atual |
| `SISTEMA_PERMISSOES.md` | Detalhes técnicos de permissões | ✅ Atual |
| `DESIGN_SYSTEM.md` | Guia de componentes e padrões visuais | ✅ Atual |

---

### 📂 02-modulos/

#### 📁 teams/ - Gestão de Equipes
**Status**: ✅ 100% Implementado

| Arquivo | Descrição | Status |
|---------|-----------|--------|
| `teams-CONTRACT.md` | Contrato de API do módulo Teams | ✅ Atual |
| `codigo-teams.md` | Código e estrutura interna | ✅ Atual |
| `TEAMS_ROTAS_CANONICAS.md` | Rotas RESTful do módulo | ✅ Atual |
| `IMPLEMENTACAO_TEAMS_3_COLUNAS.md` | Layout em 3 colunas | ✅ Implementado |
| `IMPLEMENTACAO_PAGINA_TEAMS.md` | Página principal do módulo | ✅ Implementado |
| `PLANO_MIGRACAO_TEAMS.md` | Como migrar versões antigas | 📋 Referência |
| `RODAR_TEAMS.md` | Como executar módulo em dev | 📋 Procedimento |
| `RELATORIO_ROTA_TEAMS.md` | Análise das rotas | 📊 Referência |
| `FIX_TEAM_MEMBERS_INVITE.md` | Correções no sistema de convites | ✅ Implementado |
| `Convidar membros.md` | Documentação do fluxo de convite | ✅ Atual |
| `teams1.md` | Versão antiga (referência histórica) | 📦 Arquivo |

#### 📁 auth/ - Autenticação & Autorização
**Status**: ✅ 100% Implementado

| Arquivo | Descrição | Status |
|---------|-----------|--------|
| `MELHORIAS_AUTENTICACAO_IMPLEMENTADAS.md` | Melhorias aplicadas ao sistema | ✅ Implementado |
| `PADRONIZACAO_AUTH_CONTEXT.md` | Contexto de autenticação React | ✅ Implementado |
| `SSR_COOKIE_FIX.md` | Correção de cookies em SSR | ✅ Implementado |
| `RELATORIO_AUDITORIA_LOGIN_AUTORIZACAO.md` | Auditoria de segurança | 📊 Referência |
| `ANALISE_PAGINAS_LOGIN.md` | Análise das páginas de login | 📊 Referência |
| `CORRECOES_FINAIS_WELCOME.md` | Correções no fluxo de boas-vindas | ✅ Implementado |
| `CORRECOES_FORMULARIOS_BANCO.md` | Ajuste de formulários conforme BD | ✅ Implementado |
| `CAMPOS_OBRIGATORIOS_BANCO.md` | Mapeamento de campos obrigatórios | ✅ Atual |
| `RESUMO_CORRECOES.md` | Resumo de todas as correções | ✅ Atual |
| `GUIA_TESTE_FORMULARIOS_ESPECIFICOS.md` | Como testar formulários por papel | 📋 Procedimento |

#### 📁 athletes/ - Gestão de Atletas
**Status**: ✅ 95% Implementado

| Arquivo | Descrição | Status |
|---------|-----------|--------|
| `IMPLEMENTACAO_PAGINA_ATLETAS_3_COLUNAS.md` | Layout em 3 colunas | ✅ Implementado |
| `INTEGRACAO_CADASTRO_ATLETAS.md` | Integração de cadastro | ✅ Implementado |
| `REGRAS_GERENCIAMENTO_ATLETAS.md` | Regras de negócio | ✅ Atual |
| `CHECKLIST_TESTES_PAGINA_ATLETAS.md` | Checklist de testes | 📋 Procedimento |
| `RESULTADO_TESTES_PAGINA_ATLETAS.md` | Resultados dos testes | 📊 Referência |
| `FICHA_UNICA_REFACTORING_CHECKLIST.md` | Refatoração da ficha única | ✅ Implementado |
| `FICHA_UNICA_WIZARD_CONFIRMACAO.md` | Wizard de confirmação | ✅ Implementado |

#### 📁 training/ - Treinos
**Status**: ✅ 90% Implementado

| Arquivo | Descrição | Status |
|---------|-----------|--------|
| `TRAINING_V2_API.md` | API v2 do módulo | ✅ Atual |
| `TRAINING_V2_EXAMPLES.md` | Exemplos de uso da API | ✅ Atual |
| `PLANO_IMPLEMENTACAO_TREINOS.md` | Planejamento inicial | 📋 Referência |
| `IMPLEMENTACAO_TREINOS_F1.MD` | Fase 1 implementada | ✅ Implementado |
| `IMPLEMENTACAO_MODULO_TREINOS_COMPLETO.md` | Módulo completo | ✅ Implementado |
| `IMPLEMENTACAO_FOCOS_TREINO.md` | Sistema de focos | ✅ Implementado |
| `PROGRESSO_IMPLEMENTACAO_TREINOS_F1.MD` | Progresso da fase 1 | 📊 Referência |
| `TRAINNIG.MD` | Documento antigo (typo no nome) | 📦 Arquivo |
| `TREINOS_ALERTAS_APRENDIZADO.md` | Sistema de alertas | ✅ Implementado |
| `TREINOS_FLUXOS_E_DADOS.md` | Fluxos de dados | ✅ Atual |
| `TREINOS_VISUALIZACOES_RELATORIOS_CONTINUIDADE.md` | Viz e relatórios | ⏳ Em progresso |
| `TAREFA_6_AUTO_SAVE_IMPLEMENTADO.md` | Auto-save | ✅ Implementado |
| `TAREFA_7_8_PAGINA_DETALHES_IMPLEMENTADO.md` | Página detalhes | ✅ Implementado |
| `TAREFA_9_PLANEJAMENTO_SEMANAL_IMPLEMENTADO.md` | Planejamento semanal | ✅ Implementado |
| `TAREFA_10_SUGESTOES_INTELIGENTES_IMPLEMENTADO.md` | Sugestões IA | ✅ Implementado |
| `RELATORIO_ROTA_TRAINING.md` | Análise de rotas | 📊 Referência |
| `BUG_REPORT_training_session_service.md` | Bug resolvido | 📦 Arquivo |

#### 📁 games/ - Jogos & Competições
**Status**: ✅ 85% Implementado (API completa, Migration 0031)

| Arquivo | Descrição | Status |
|---------|-----------|--------|
| `RELATORIO_ROTA_GAMES.md` | Análise de rotas existentes | 📊 Referência |
| `PLANO_IMPLEMENTACAO_COMPETICOES_IA.md` | Plano futuro com IA | 📋 Planejamento |

#### 📁 statistics/ - Estatísticas
**Status**: ✅ 85% Implementado

| Arquivo | Descrição | Status |
|---------|-----------|--------|
| `ESTATISTICAS.MD` | Visão geral do módulo | ✅ Atual |
| `IMPLEMENTACOES_STATISTICS.md` | Features implementadas | ✅ Implementado |
| `SESSAO_IMPLEMENTACAO_STATISTICS_PARTE2.md` | Sessão de implementação | 📊 Referência |
| `STATISTICS_REPORTS_EVENTOS.md` | Sistema de eventos | ✅ Implementado |

---

### 📂 03-implementacoes-concluidas/
**O que é**: Documentação de features que foram completamente implementadas  
**Quando usar**: Para entender o histórico de uma feature ou como foi implementada

| Arquivo | Descrição | Data |
|---------|-----------|------|
| `VALIDACAO_CATEGORIA_WELCOME.md` | **Bug crítico**: Validação de idade/categoria no welcome | 14/01/2026 |
| `CORRECAO_CRITICA_COMPETITIONS_E_TRAINING.md` | Correção crítica: competitions + training | 14/01/2026 |
| `ETAPA3_SEPARACAO_MEMBROS_CONCLUIDA.md` | Separação Comissão/Atletas | 13/01/2026 |
| `ETAPA2_FORMULARIOS_ESPECIFICOS_CONCLUIDA.md` | Formulários por papel | 13/01/2026 |
| `ETAPA1_VALIDACAO_MEMBRO_CONCLUIDA.md` | Validação completa do fluxo de membro | 13/01/2026 |
| `INTEGRACAO_GAPS_COMPLETA.md` | Integração de lacunas | 13/01/2026 |
| `MELHORIAS_EMAIL_IMPLEMENTADAS.md` | Sistema de emails | 13/01/2026 |
| `IMPLEMENTACAO_EMAIL_PROFISSIONAL.md` | Emails profissionais | 13/01/2026 |
| `FIX_CORS_APPLIED.md` | Correção de CORS | 13/01/2026 |
| `PROFESSIONAL_SIDEBAR_FUNCIONAMENTO.md` | Sidebar profissional | 13/01/2026 |
| `RELATORIO_TOPBAR_v2.0.md` | TopBar v2 | 13/01/2026 |

---

### 📂 04-planejamento/
**O que é**: Planos para futuras implementações  
**Quando usar**: Antes de começar uma nova feature

| Arquivo | Descrição | Status |
|---------|-----------|--------|
| `PLANO_ACAO_EXECUTAVEL.md` | Plano de ação geral | 📋 Ativo |
| `PLANO_VALIDACAO_STAGING.md` | Como validar em staging | 📋 Ativo |
| Outros `PLANO_*.md` | Planos diversos por módulo | 📋 Planejamento |

---

### 📂 05-guias-procedimentos/
**O que é**: Como fazer tarefas específicas no sistema  
**Quando usar**: Quando precisar executar uma tarefa ou resolver um problema

| Arquivo | Descrição | Tipo |
|---------|-----------|------|
| `MIGRATION_GUIDE.md` | Como rodar migrações | 📋 Procedimento |
| `FLUXO_RESET_MIGRATION_SEED.md` | Reset completo do BD | 📋 Procedimento |
| `FLUXO_VALIDACAO.md` | Fluxo de validação de features | 📋 Procedimento |
| `COMANDOS_VALIDACAO.md` | Comandos úteis para testes | 📋 Referência |
| `TROUBLESHOOTING_GUIDE.md` | Resolução de problemas gerais | 🆘 Troubleshooting |
| `TROUBLESHOOTING_API_CONNECTION.md` | Problemas de conexão API | 🆘 Troubleshooting |
| `PRONTO_PARA_EXECUTAR.md` | Setup inicial do ambiente | 📋 Procedimento |
| `VALIDACAO_MANUAL_CONVITES.md` | Como testar convites manualmente | 📋 Procedimento |
| `README.md` | README geral | 📋 Referência |
| `email_invite_service.md` | Serviço de email de convites | 📋 Referência |
| `REGRAS_GERENCIAMENTO_USUARIOS.md` | Regras de usuários | 📋 Regras |
| `TESTES_E2E_ATUALIZADOS.md` | Guia de testes E2E | 📋 Procedimento |
| `TESTIDS_MANIFEST.md` | Lista de testids usados | 📋 Referência |
| `team_tests_rules.md` | Regras específicas de testes de teams | 📋 Regras |

---

### 📂 _archived/
**O que é**: Arquivos históricos, análises antigas, bugs resolvidos  
**Quando usar**: Para consultar histórico ou entender decisões passadas

#### 📁 analises/
Análises e relatórios de sprints/fases anteriores

| Arquivo | Descrição | Data |
|---------|-----------|------|
| `ANALISE_COBERTURA*.md` | Análises de cobertura de código | Antigas |
| `CHECKLIST_*.md` | Checklists de validação antigas | Antigas |
| `RELATORIO_*.md` | Relatórios de status antigos | Antigas |
| `PROGRESSO_*.md` | Progressos de fases antigas | Antigas |
| `RUN*_SUMMARY.md` | Sumários de execuções de testes | Antigas |
| `SESSAO_*.md` | Sessões de implementação antigas | Antigas |
| `CORRECOES_POS_TESTE.md` | Correções após testes | Antigas |
| `EXECUTIVE_SUMMARY.md` | Sumário executivo antigo | Antigas |
| `RESUMO_FINAL*.md` | Resumos antigos | Antigas |
| `UX_COMPONENTES_E_CHECKLIST_FINAL.md` | Checklist UX antigo | Antigas |

#### 📁 bugs-resolvidos/
(Vazio por enquanto - bugs resolvidos foram movidos para módulos específicos)

#### 📁 relatorios-antigos/
Relatórios e documentos obsoletos

| Arquivo | Descrição | Status |
|---------|-----------|--------|
| `PROBLEMA_409_ANALYSIS.md` | Análise de erro 409 (resolvido) | 📦 Resolvido |
| `CONTRATO_ATUALIZADO.md` | Contrato antigo | 📦 Obsoleto |
| `BACKEND_VALIDATION_NEEDED.md` | Validação antiga | 📦 Feito |
| `CACHE_LIMITS.md` | Limites de cache | 📦 Antigo |
| `OPENAPI_*.md` | Documentos OpenAPI antigos | 📦 Obsoleto |
| `VALIDACAO_STAGING_RESUMO.md` | Resumo antigo | 📦 Obsoleto |
| `hbtrck.md`, `hb_pt.md` | Docs antigos do projeto | 📦 Obsoleto |
| `neondb.md` | Config antiga de BD | 📦 Obsoleto |
| `Nivel 3.md` | Documento antigo | 📦 Obsoleto |
| `system_rules.md` | Regras antigas | 📦 Obsoleto |
| `RELATORIO_SIDEBAR.md` | Relatório sidebar antigo | 📦 Obsoleto |
| `RUN_LOG.md` | Log de execuções antigas | 📦 Obsoleto |
| `check_users.py` | Script de verificação | 📦 Obsoleto |

---

## 🎯 Como Navegar por Tipo de Tarefa

### 🆕 Quero implementar uma nova feature
1. Veja se já existe planejamento em `04-planejamento/`
2. Estude o módulo relacionado em `02-modulos/`
3. Siga padrões do `01-sistema-atual/DESIGN_SYSTEM.md`
4. Crie testes seguindo `05-guias-procedimentos/TESTES_E2E_ATUALIZADOS.md`

### 🐛 Preciso corrigir um bug
1. Consulte `05-guias-procedimentos/TROUBLESHOOTING_GUIDE.md`
2. Veja se há algo similar em `_archived/bugs-resolvidos/`
3. Documente a correção em `02-modulos/[módulo]/`

### 📖 Quero entender como algo funciona
1. Veja status atual em `01-sistema-atual/STATUS_GERAL_TEAMS_STAGING.md`
2. Leia contrato do módulo em `02-modulos/[módulo]/`
3. Se foi implementado recentemente, veja `03-implementacoes-concluidas/`

### 🧪 Preciso testar uma feature
1. Comandos: `05-guias-procedimentos/COMANDOS_VALIDACAO.md`
2. Testes E2E: `05-guias-procedimentos/TESTES_E2E_ATUALIZADOS.md`
3. Validação manual: `05-guias-procedimentos/VALIDACAO_MANUAL_*.md`

### 🚀 Vou fazer deploy
1. `04-planejamento/PLANO_VALIDACAO_STAGING.md`
2. `05-guias-procedimentos/PRONTO_PARA_EXECUTAR.md`
3. `01-sistema-atual/STATUS_GERAL_TEAMS_STAGING.md`

---

## 📊 Status por Categoria

### ✅ Documentação Atual e Válida
- `01-sistema-atual/` - Tudo atual
- `02-modulos/teams/` - Tudo atual
- `02-modulos/auth/` - Tudo atual
- `02-modulos/athletes/` - Tudo atual
- `02-modulos/training/` - 90% atual (faltam visualizações)
- `02-modulos/statistics/` - 85% atual
- `03-implementacoes-concluidas/` - Tudo atual
- `05-guias-procedimentos/` - Tudo atual

### ⏳ Documentação Parcial
- `02-modulos/games/` - Apenas API básica documentada
- `04-planejamento/` - Planos para futuro

### 📦 Documentação Arquivada
- `_archived/` - Tudo histórico, consultar apenas se necessário

---

## 🔍 Busca Rápida por Palavra-Chave

### Autenticação / Login
→ `02-modulos/auth/`

### Convites / Welcome
→ `02-modulos/teams/` e `03-implementacoes-concluidas/ETAPA*.md`

### Permissões / RBAC
→ `01-sistema-atual/ARQUITETURA_PERMISSOES_CANONICAS.md`

### Atletas
→ `02-modulos/athletes/`

### Treinos
→ `02-modulos/training/`

### Testes / E2E
→ `05-guias-procedimentos/TESTES_E2E_ATUALIZADOS.md`

### Migrações / Banco
→ `05-guias-procedimentos/MIGRATION_GUIDE.md`

### Troubleshooting / Erros
→ `05-guias-procedimentos/TROUBLESHOOTING_*.md`

### Design / UI
→ `01-sistema-atual/DESIGN_SYSTEM.md`

### API / Contratos
→ `02-modulos/[módulo]/*-CONTRACT.md`

---

## 💡 Dicas de Uso

### Para Desenvolvedores Novos
1. Comece pelo `_INDICE.md`
2. Leia `01-sistema-atual/MANUAL_SISTEMA_HBTRACK.md`
3. Configure ambiente com `05-guias-procedimentos/PRONTO_PARA_EXECUTAR.md`
4. Estude módulo específico em `02-modulos/`

### Para Manutenção
1. Sempre atualize documentação ao fazer mudanças
2. Archive documentos obsoletos em `_archived/`
3. Mantenha `_INDICE.md` e este `_MAPA.md` atualizados
4. Use prefixos claros nos nomes de arquivo

### Para Gestores
1. Status geral: `01-sistema-atual/STATUS_GERAL_TEAMS_STAGING.md`
2. Progresso: `03-implementacoes-concluidas/`
3. Próximos passos: `04-planejamento/`

---

## 📝 Legenda de Status

| Símbolo | Significado |
|---------|-------------|
| ✅ | Atual e implementado |
| ⏳ | Em progresso |
| 📋 | Procedimento/guia |
| 📊 | Referência/análise |
| 📦 | Arquivado/histórico |
| 🆘 | Troubleshooting |

---

*Mapa organizado em 13/01/2026 - Estrutura criada para facilitar navegação em 100+ documentos*
