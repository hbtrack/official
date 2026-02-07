<!-- STATUS: DEPRECATED | replaced by docs/README.md -->

# 📑 ÍNDICE RÁPIDO - HB Track Sistema

**Última atualização**: 14/01/2026  
**Status Geral**: 🟢 Sistema pronto para staging (críticos resolvidos)  
**Última implementação**: Validação de Categoria no Welcome (Bug Crítico Resolvido)

---

## 🎯 ONDE COMEÇAR

### Você quer...

**Ver o status atual do sistema?**
→ Leia: [01-sistema-atual/STATUS_GERAL_TEAMS_STAGING.md](01-sistema-atual/STATUS_GERAL_TEAMS_STAGING.md)

**Entender a arquitetura?**
→ Leia: [01-sistema-atual/ARQUITETURA_PERMISSOES_CANONICAS.md](01-sistema-atual/ARQUITETURA_PERMISSOES_CANONICAS.md)

**Usar o sistema?**
→ Leia: [01-sistema-atual/MANUAL_SISTEMA_HBTRACK.md](01-sistema-atual/MANUAL_SISTEMA_HBTRACK.md)

**Trabalhar em um módulo específico?**
→ Vá para: [02-modulos/](#-módulos-do-sistema)

**Ver guia completo de navegação?**
→ Leia: [_MAPA.md](./_MAPA.md)

**Ver resumos executivos?**
→ Leia: [08-resumos-executivos/](08-resumos-executivos/)

**Certificação e Deploy?**
→ Leia: [06-certificacao-deploy/](06-certificacao-deploy/)

---

## 📊 STATUS ATUAL DO SISTEMA

### ✅ Módulos Implementados e Funcionais

#### 1. **Teams** (Gestão de Equipes) - 100%
- ✅ CRUD completo de equipes
- ✅ Sistema de convites por email
- ✅ Formulários específicos por papel (atleta, treinador, coordenador, membro)
- ✅ Separação visual: Comissão Técnica vs Atletas
- ✅ Gerenciamento de membros e permissões
- ✅ 114 testes E2E (100% aprovação)

**Documentos principais:**
- [02-modulos/teams/teams-CONTRACT.md](02-modulos/teams/teams-CONTRACT.md)
- [03-implementacoes-concluidas/ETAPA3_SEPARACAO_MEMBROS_CONCLUIDA.md](03-implementacoes-concluidas/ETAPA3_SEPARACAO_MEMBROS_CONCLUIDA.md)

#### 2. **Auth** (Autenticação & Autorização) - 100%
- ✅ Login com JWT cookies
- ✅ Sistema RBAC com 5 papéis (dirigente, coordenador, treinador, atleta, membro)
- ✅ Permissões canônicas por módulo
- ✅ Fluxo de welcome/boas-vindas completo
- ✅ Formulários específicos por papel
- ✅ Validação de campos conforme banco de dados
- ✅ **NOVO**: Validação de categoria/idade no welcome (14/01/2026)

**Documentos principais:**
- [02-modulos/auth/MELHORIAS_AUTENTICACAO_IMPLEMENTADAS.md](02-modulos/auth/MELHORIAS_AUTENTICACAO_IMPLEMENTADAS.md)
- [02-modulos/auth/CAMPOS_OBRIGATORIOS_BANCO.md](02-modulos/auth/CAMPOS_OBRIGATORIOS_BANCO.md)
- [01-sistema-atual/RBAC_MATRIX.md](01-sistema-atual/RBAC_MATRIX.md)

#### 3. **Athletes** (Gestão de Atletas) - 95%
- ✅ Cadastro de atletas
- ✅ Ficha única com wizard
- ✅ Visualização em 3 colunas
- ✅ Integração com teams
- ⏳ Falta: Edição completa de posições defensivas

**Documentos principais:**
- [02-modulos/athletes/IMPLEMENTACAO_PAGINA_ATLETAS_3_COLUNAS.md](02-modulos/athletes/IMPLEMENTACAO_PAGINA_ATLETAS_3_COLUNAS.md)
- [02-modulos/athletes/INTEGRACAO_CADASTRO_ATLETAS.md](02-modulos/athletes/INTEGRACAO_CADASTRO_ATLETAS.md)

#### 4. **Training** (Treinos) - 90%
- ✅ CRUD de sessões de treino
- ✅ Planejamento semanal
- ✅ Auto-save
- ✅ Sugestões inteligentes
- ✅ Focos de treino
- ✅ Alertas e aprendizado
- ⏳ Falta: Visualizações avançadas

**Documentos principais:**
- [02-modulos/training/TRAINING_V2_API.md](02-modulos/training/TRAINING_V2_API.md)
- [02-modulos/training/IMPLEMENTACAO_MODULO_TREINOS_COMPLETO.md](02-modulos/training/IMPLEMENTACAO_MODULO_TREINOS_COMPLETO.md)

#### 5. **Statistics** (Estatísticas) - 85%
- ✅ Relatórios de treinos
- ✅ Eventos e métricas
- ✅ Visualizações básicas
- ⏳ Falta: Dashboard avançado

**Documentos principais:**
- [02-modulos/statistics/IMPLEMENTACOES_STATISTICS.md](02-modulos/statistics/IMPLEMENTACOES_STATISTICS.md)

#### 6. **Games/Competitions** (Jogos/Competições) - 85%
- ✅ API completa implementada (competitions, competition_seasons)
- ✅ Migração 0031 criada - 6 tabelas do módulo competitions
- ✅ Schema canônico 100% operacional
- ✅ Endpoints REST funcionais (GET, POST, PATCH)
- ✅ Correção de bug crítico (ChunkedIteratorResult)
- ⏳ Interface web em desenvolvimento

**Documentos principais:**
- [02-modulos/games/RELATORIO_ROTA_GAMES.md](02-modulos/games/RELATORIO_ROTA_GAMES.md)

---

## 🔑 Conceitos-Chave

### Papéis do Sistema (role_id)
| ID | Nome | Permissões |
|----|------|------------|
| 1 | Dirigente | Acesso total à organização |
| 2 | Coordenador | Gestão técnica e administrativa |
| 3 | Treinador | Treinos, jogos, atletas da equipe |
| 4 | Atleta | Visualização de dados próprios |
| 5 | Membro | Leitura geral da equipe |

### Permissões Canônicas
- **can_view_***: Ver informações do módulo
- **can_manage_***: Criar/editar no módulo
- **can_delete_***: Remover itens do módulo

Detalhes: [01-sistema-atual/ARQUITETURA_PERMISSOES_CANONICAS.md](01-sistema-atual/ARQUITETURA_PERMISSOES_CANONICAS.md)

---

## 🗂️ Estrutura de Pastas

```
docs/
├── _INDICE.md                    ← Você está aqui!
├── _MAPA.md                      ← Guia completo de navegação
│
├── 01-sistema-atual/             ← Documentação do sistema em produção
│   ├── STATUS_GERAL_TEAMS_STAGING.md
│   ├── MANUAL_SISTEMA_HBTRACK.md
│   ├── ARQUITETURA_PERMISSOES_CANONICAS.md
│   ├── RBAC_MATRIX.md
│   ├── SISTEMA_PERMISSOES.md
│   └── DESIGN_SYSTEM.md
│
├── 02-modulos/                   ← Documentação por módulo
│   ├── teams/
│   ├── auth/
│   ├── athletes/
│   ├── training/
│   ├── games/
│   └── statistics/
│
├── 03-implementacoes-concluidas/ ← Features implementadas
│   ├── ETAPA1_VALIDACAO_MEMBRO_CONCLUIDA.md
│   ├── ETAPA2_FORMULARIOS_ESPECIFICOS_CONCLUIDA.md
│   ├── ETAPA3_SEPARACAO_MEMBROS_CONCLUIDA.md
│   └── ...
│
├── 04-planejamento/              ← Planos futuros
│   └── PLANO_*.md
│
├── 05-guias-procedimentos/       ← Como fazer tarefas
│   ├── MIGRATION_GUIDE.md
│   ├── TROUBLESHOOTING_GUIDE.md
│   └── ...
│
└── _archived/                    ← Arquivos históricos
    ├── analises/
    ├── bugs-resolvidos/
    └── relatorios-antigos/
```

---

## 🚀 Workflows Comuns

### Como começar a desenvolver?
1. Leia [05-guias-procedimentos/PRONTO_PARA_EXECUTAR.md](05-guias-procedimentos/PRONTO_PARA_EXECUTAR.md)
2. Configure ambiente seguindo [05-guias-procedimentos/MIGRATION_GUIDE.md](05-guias-procedimentos/MIGRATION_GUIDE.md)
3. Execute: `& 'c:\HB TRACK\reset-and-start.ps1'`

### Como criar um teste E2E?
1. Veja exemplos em [05-guias-procedimentos/TESTES_E2E_ATUALIZADOS.md](05-guias-procedimentos/TESTES_E2E_ATUALIZADOS.md)
2. Siga regras em [05-guias-procedimentos/team_tests_rules.md](05-guias-procedimentos/team_tests_rules.md)
3. Use testids do [05-guias-procedimentos/TESTIDS_MANIFEST.md](05-guias-procedimentos/TESTIDS_MANIFEST.md)

### Como corrigir um bug?
1. Consulte [05-guias-procedimentos/TROUBLESHOOTING_GUIDE.md](05-guias-procedimentos/TROUBLESHOOTING_GUIDE.md)
2. Se for API, veja [05-guias-procedimentos/TROUBLESHOOTING_API_CONNECTION.md](05-guias-procedimentos/TROUBLESHOOTING_API_CONNECTION.md)

### Como adicionar um novo módulo?
1. Estude estrutura de [02-modulos/teams/](02-modulos/teams/)
2. Defina contrato de API (ex: teams-CONTRACT.md)
3. Implemente seguindo padrões do DESIGN_SYSTEM.md

---

## 📈 Próximos Passos

### Prioridade Alta
1. [ ] Deploy em staging
2. [ ] Testes de integração completos
3. [ ] Popular tabela defensive_positions

### Prioridade Média
1. [ ] Modal "Adicionar Atleta" funcional
2. [ ] Visualizações avançadas de treinos
3. [ ] Dashboard de estatísticas

### Prioridade Baixa
1. [ ] Módulo de competições completo
2. [ ] Exportação de dados (CSV/PDF)
3. [ ] Integrações externas

Veja detalhes em [04-planejamento/](04-planejamento/)

---

## 🆘 Ajuda Rápida

**Não sei onde encontrar algo?**
→ Use Ctrl+F neste arquivo ou consulte [_MAPA.md](./_MAPA.md)

**Erro no código?**
→ [05-guias-procedimentos/TROUBLESHOOTING_GUIDE.md](05-guias-procedimentos/TROUBLESHOOTING_GUIDE.md)

**Dúvida sobre arquitetura?**
→ [01-sistema-atual/ARQUITETURA_PERMISSOES_CANONICAS.md](01-sistema-atual/ARQUITETURA_PERMISSOES_CANONICAS.md)

**Como executar testes?**
→ [05-guias-procedimentos/COMANDOS_VALIDACAO.md](05-guias-procedimentos/COMANDOS_VALIDACAO.md)

---

## 📝 Notas Importantes

### ⚠️ Regra de Ouro
> **Se o sistema já consegue responder o que é necessário para o cadastro, os formulários não devem pedir novamente.**

Sempre valide campos contra schema do banco antes de implementar.

### 🎨 Design System
Todos os componentes seguem: [01-sistema-atual/DESIGN_SYSTEM.md](01-sistema-atual/DESIGN_SYSTEM.md)
---

## 📁 ESTRUTURA ORGANIZACIONAL DA DOCUMENTAÇÃO

### Pastas Principais

- **[01-sistema-atual/](01-sistema-atual/)** - Estado atual do sistema, arquitetura e configurações
- **[02-modulos/](02-modulos/)** - Documentação específica por módulo (teams, auth, games, etc.)
- **[03-implementacoes-concluidas/](03-implementacoes-concluidas/)** - Relatórios de implementações finalizadas
- **[04-planejamento/](04-planejamento/)** - Planejamento de sprints e roadmaps
- **[05-guias-procedimentos/](05-guias-procedimentos/)** - Guias práticos e procedimentos
- **[06-certificacao-deploy/](06-certificacao-deploy/)** - Certificação de funcionamento e checklists de deploy
- **[07-organizacao-limpeza/](07-organizacao-limpeza/)** - Documentos de organização e limpeza do sistema
- **[08-resumos-executivos/](08-resumos-executivos/)** - Resumos executivos e relatórios finais
- **[_archived/](archived/)** - Documentos históricos e análises antigas

### 🔒 Segurança
- Nunca exponha tokens em logs
- Use RBAC para todas as operações
- Valide entrada do usuário no backend

### 🧪 Testes
- Coverage mínimo: 80%
- Todos os testes E2E devem ser determinísticos
- Use testids para seleção de elementos

---

## 🎯 Conclusão

Este índice serve como **ponto de partida rápido** para navegar na documentação. Para um guia completo de todos os arquivos, consulte [_MAPA.md](./_MAPA.md).

**Status atual**: Sistema funcional e pronto para staging, com 6 módulos em diferentes estágios de completude.

**Última grande implementação**: Separação de Comissão Técnica e Atletas na aba Membros (13/01/2026)

---

*Documentação organizada em 13/01/2026*
