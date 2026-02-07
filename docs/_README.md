<!-- STATUS: DEPRECATED | replaced by docs/README.md -->

# 📚 Documentação HB Track - Estrutura Organizada

**Organizado em**: 13/01/2026  
**Última atualização**: 14/01/2026  
**Total de documentos**: 100+ arquivos organizados em categorias

---

## 🚀 Início Rápido

### Você está perdido? Comece aqui:

1. **[_INDICE.md](./_INDICE.md)** ← Seu ponto de partida! Índice rápido com status do sistema
2. **[_MAPA.md](./_MAPA.md)** ← Guia completo de todos os arquivos e onde encontrá-los

---

## 📁 Estrutura de Pastas

```
docs/
│
├── _INDICE.md                    ⭐ COMECE AQUI - Índice rápido
├── _MAPA.md                      🗺️  Guia completo de navegação
├── _README.md                    📖 Este arquivo
│
├── 01-sistema-atual/             📊 Sistema em produção/staging
│   ├── STATUS_GERAL_TEAMS_STAGING.md
│   ├── MANUAL_SISTEMA_HBTRACK.md
│   ├── ARQUITETURA_PERMISSOES_CANONICAS.md
│   ├── RBAC_MATRIX.md
│   ├── SISTEMA_PERMISSOES.md
│   └── DESIGN_SYSTEM.md
│
├── 02-modulos/                   🧩 Documentação por módulo
│   ├── teams/                    ✅ 100% implementado
│   ├── auth/                     ✅ 100% implementado
│   ├── athletes/                 ✅ 95% implementado
│   ├── training/                 ✅ 90% implementado
│   ├── statistics/               ✅ 85% implementado
│   └── games/                    ⏳ 30% implementado
│
├── 03-implementacoes-concluidas/ ✅ Features prontas
│   ├── ETAPA1_VALIDACAO_MEMBRO_CONCLUIDA.md
│   ├── ETAPA2_FORMULARIOS_ESPECIFICOS_CONCLUIDA.md
│   ├── ETAPA3_SEPARACAO_MEMBROS_CONCLUIDA.md
│   └── ... (outras implementações)
│
├── 04-planejamento/              📋 Planos futuros
│   └── PLANO_*.md
│
├── 05-guias-procedimentos/       📖 Como fazer tarefas
│   ├── MIGRATION_GUIDE.md
│   ├── TROUBLESHOOTING_GUIDE.md
│   ├── TESTES_E2E_ATUALIZADOS.md
│   └── ... (outros guias)
│
└── _archived/                    📦 Arquivos históricos
    ├── analises/                 (análises antigas)
    ├── bugs-resolvidos/          (bugs já corrigidos)
    └── relatorios-antigos/       (relatórios obsoletos)
```

---

## 🎯 Navegação por Objetivo

### Quero saber o STATUS ATUAL do sistema
→ Leia: [`01-sistema-atual/STATUS_GERAL_TEAMS_STAGING.md`](01-sistema-atual/STATUS_GERAL_TEAMS_STAGING.md)

### Quero USAR o sistema
→ Leia: [`01-sistema-atual/MANUAL_SISTEMA_HBTRACK.md`](01-sistema-atual/MANUAL_SISTEMA_HBTRACK.md)

### Quero DESENVOLVER uma feature
→ Veja: [`02-modulos/`](02-modulos/) e [`04-planejamento/`](04-planejamento/)

### Preciso RESOLVER um problema
→ Consulte: [`05-guias-procedimentos/TROUBLESHOOTING_GUIDE.md`](05-guias-procedimentos/TROUBLESHOOTING_GUIDE.md)

### Quero TESTAR o sistema
→ Siga: [`05-guias-procedimentos/TESTES_E2E_ATUALIZADOS.md`](05-guias-procedimentos/TESTES_E2E_ATUALIZADOS.md)

---

## 📊 Status dos Módulos

| Módulo | Status | Documentação |
|--------|--------|--------------|
| **Teams** | ✅ 100% | [02-modulos/teams/](02-modulos/teams/) |
| **Auth** | ✅ 100% | [02-modulos/auth/](02-modulos/auth/) |
| **Athletes** | ✅ 95% | [02-modulos/athletes/](02-modulos/athletes/) |
| **Training** | ✅ 90% | [02-modulos/training/](02-modulos/training/) |
| **Statistics** | ✅ 85% | [02-modulos/statistics/](02-modulos/statistics/) |
| **Games** | ⏳ 30% | [02-modulos/games/](02-modulos/games/) |

---

## 🔑 Documentos Principais

### Sistema Atual
- [STATUS_GERAL_TEAMS_STAGING.md](01-sistema-atual/STATUS_GERAL_TEAMS_STAGING.md) - Status completo
- [MANUAL_SISTEMA_HBTRACK.md](01-sistema-atual/MANUAL_SISTEMA_HBTRACK.md) - Manual do usuário
- [ARQUITETURA_PERMISSOES_CANONICAS.md](01-sistema-atual/ARQUITETURA_PERMISSOES_CANONICAS.md) - Sistema RBAC

### Implementações Recentes
- [VALIDACAO_CATEGORIA_WELCOME.md](03-implementacoes-concluidas/VALIDACAO_CATEGORIA_WELCOME.md) - **Bug crítico**: Validação idade/categoria (14/01/2026)
- [CORRECAO_CRITICA_COMPETITIONS_E_TRAINING.md](03-implementacoes-concluidas/CORRECAO_CRITICA_COMPETITIONS_E_TRAINING.md) - Fix ChunkedIteratorResult (14/01/2026)
- [ETAPA3_SEPARACAO_MEMBROS_CONCLUIDA.md](03-implementacoes-concluidas/ETAPA3_SEPARACAO_MEMBROS_CONCLUIDA.md) - Separação Comissão/Atletas (13/01/2026)
- [ETAPA2_FORMULARIOS_ESPECIFICOS_CONCLUIDA.md](03-implementacoes-concluidas/ETAPA2_FORMULARIOS_ESPECIFICOS_CONCLUIDA.md) - Formulários por papel (13/01/2026)
- [ETAPA1_VALIDACAO_MEMBRO_CONCLUIDA.md](03-implementacoes-concluidas/ETAPA1_VALIDACAO_MEMBRO_CONCLUIDA.md) - Validação de fluxo (13/01/2026)

### Guias Essenciais
- [MIGRATION_GUIDE.md](05-guias-procedimentos/MIGRATION_GUIDE.md) - Migrações de BD
- [TROUBLESHOOTING_GUIDE.md](05-guias-procedimentos/TROUBLESHOOTING_GUIDE.md) - Resolver problemas
- [TESTES_E2E_ATUALIZADOS.md](05-guias-procedimentos/TESTES_E2E_ATUALIZADOS.md) - Testes automatizados

---

## 💡 Dicas

### Para quem está começando:
1. Leia [`_INDICE.md`](./_INDICE.md) primeiro
2. Configure ambiente: [`05-guias-procedimentos/PRONTO_PARA_EXECUTAR.md`](05-guias-procedimentos/PRONTO_PARA_EXECUTAR.md)
3. Estude arquitetura: [`01-sistema-atual/ARQUITETURA_PERMISSOES_CANONICAS.md`](01-sistema-atual/ARQUITETURA_PERMISSOES_CANONICAS.md)

### Para desenvolvimento:
1. Veja módulo específico em [`02-modulos/`](02-modulos/)
2. Siga padrões: [`01-sistema-atual/DESIGN_SYSTEM.md`](01-sistema-atual/DESIGN_SYSTEM.md)
3. Crie testes: [`05-guias-procedimentos/TESTES_E2E_ATUALIZADOS.md`](05-guias-procedimentos/TESTES_E2E_ATUALIZADOS.md)

### Para gestão:
1. Status: [`01-sistema-atual/STATUS_GERAL_TEAMS_STAGING.md`](01-sistema-atual/STATUS_GERAL_TEAMS_STAGING.md)
2. Progresso: [`03-implementacoes-concluidas/`](03-implementacoes-concluidas/)
3. Próximos: [`04-planejamento/`](04-planejamento/)

---

## 🗂️ Sobre a Organização

### Por que foi reorganizado?
Antes: 100+ arquivos misturados sem estrutura clara  
Agora: Organização lógica por categoria e status

### Critérios de organização:
- **01-sistema-atual/**: O que está em produção AGORA
- **02-modulos/**: Documentação técnica por módulo
- **03-implementacoes-concluidas/**: Histórico de features
- **04-planejamento/**: Futuro do sistema
- **05-guias-procedimentos/**: Como fazer tarefas
- **_archived/**: Histórico para consulta

### Arquivos arquivados
Documentos em `_archived/` são históricos. Não estão obsoletos, apenas não são necessários no dia a dia. Consulte se precisar entender decisões passadas.

---

## 🔍 Busca Rápida

Use Ctrl+F no [`_MAPA.md`](./_MAPA.md) para encontrar qualquer arquivo por palavra-chave.

Exemplos:
- Busque "auth" para encontrar tudo sobre autenticação
- Busque "treinos" para módulo de training
- Busque "teste" para guias de testes

---

## 📝 Manutenção da Documentação

### Ao adicionar novo documento:
1. Coloque na pasta correta
2. Atualize [`_MAPA.md`](./_MAPA.md)
3. Se for importante, adicione ao [`_INDICE.md`](./_INDICE.md)

### Ao arquivar documento:
1. Mova para `_archived/[categoria]/`
2. Remova do [`_MAPA.md`](./_MAPA.md) (ou marque como arquivado)
3. Não delete (pode ser útil no futuro)

---

## 🆘 Ajuda

**Não encontrou o que procura?**
1. Leia [`_INDICE.md`](./_INDICE.md)
2. Consulte [`_MAPA.md`](./_MAPA.md)
3. Use Ctrl+F para buscar palavras-chave
4. Verifique `_archived/` se for algo antigo

**Documento desatualizado?**
- Atualize-o
- Ou mova para `_archived/` se estiver obsoleto

---

## 📈 Estatísticas

- **Total de documentos**: 100+
- **Módulos documentados**: 6
- **Implementações concluídas**: 15+
- **Guias práticos**: 14
- **Status**: 🟢 Sistema funcional e documentado

---

## ✅ Conclusão

Esta estrutura foi criada para:
- ✅ Facilitar navegação
- ✅ Separar atual de histórico
- ✅ Organizar por módulo
- ✅ Permitir busca rápida
- ✅ Manter histórico acessível

**Sempre comece pelo [`_INDICE.md`](./_INDICE.md)!**

---

*Estrutura organizada em 13/01/2026 - Mantida pela equipe HB Track*
