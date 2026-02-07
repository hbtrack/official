<!-- STATUS: DEPRECATED | replaced by docs/README.md -->

# Estrutura de Documentação - HB Track

**Última atualização:** 14 de Janeiro de 2026
**Versão:** 2.0 (pós-organização)

---

## 1. VISÃO GERAL

A documentação do HB Track está organizada em 8 pastas principais + arquivos raiz, seguindo o ciclo de vida do desenvolvimento:

```
docs/
├── 01-sistema-atual/           # Estado atual do sistema
├── 02-modulos/                 # Documentação por módulo funcional
├── 03-implementacoes-concluidas/ # Histórico de implementações
├── 04-planejamento/            # Roadmap e planejamento futuro
├── 05-guias-procedimentos/     # Manuais e procedimentos
├── 06-certificacao-deploy/     # Checklists de deploy
├── 07-organizacao-limpeza/     # Limpeza e refatoração
├── 08-resumos-executivos/      # Resumos para stakeholders
├── _archived/                  # Arquivos obsoletos
├── _INDICE.md                  # Índice navegável
├── _MAPA.md                    # Mapa visual da estrutura
├── _README.md                  # Introdução à documentação
└── ESTRUTURA_BANCO.md          # Schema do banco de dados
```

---

## 2. DESCRIÇÃO DAS PASTAS

### 📁 01-sistema-atual/
**Propósito:** Documentação do estado atual do sistema (arquitetura, tecnologias, configurações)

**Conteúdo típico:**
- Arquitetura técnica (backend, frontend, infra)
- Stack tecnológico
- Configurações de ambiente
- Integrações ativas

**Quando usar:** Onboarding de novos desenvolvedores, troubleshooting

---

### 📁 02-modulos/
**Propósito:** Documentação funcional organizada por módulo (contratos, APIs, componentes)

**Estrutura:**
```
02-modulos/
├── athletes/       # Módulo de Atletas
├── auth/           # Autenticação e Autorização
├── games/          # Jogos/Partidas
├── statistics/     # Estatísticas
├── teams/          # Equipes (módulo principal)
└── training/       # Treinos
```

**Arquivos por módulo:**
- `{modulo}-CONTRACT.md` - Contrato oficial (rotas, schemas, regras)
- `IMPLEMENTACAO_*.md` - Histórico de implementações
- `FIX_*.md` - Correções aplicadas
- `PLANO_*.md` - Planejamentos específicos

**Quando usar:** Desenvolvimento de features, integração entre módulos

---

### 📁 03-implementacoes-concluidas/
**Propósito:** Histórico de implementações importantes com detalhamento técnico

**Conteúdo típico:**
- Bug fixes críticos
- Novas features implementadas
- Refatorações significativas
- Melhorias de performance

**Formato recomendado:**
- Problema identificado
- Solução implementada
- Arquivos modificados (com linhas)
- Testes realizados
- Impacto e benefícios

**Exemplos:**
- `VALIDACAO_CATEGORIA_WELCOME.md` - Validação de idade de atletas
- `CORRECAO_CRITICA_COMPETITIONS_E_TRAINING.md` - Fix de query cartesiana
- `INTEGRACAO_GAPS_COMPLETA.md` - Fechamento de gaps

**Quando usar:** Revisão de decisões técnicas, troubleshooting, documentação de casos complexos

---

### 📁 04-planejamento/
**Propósito:** Roadmap, sprints futuras, features pendentes

**Conteúdo típico:**
- Roadmap trimestral
- Backlog priorizado
- Propostas de arquitetura
- Análises de viabilidade

**Quando usar:** Planning de sprints, discussões de priorização

---

### 📁 05-guias-procedimentos/
**Propósito:** Manuais operacionais e procedimentos step-by-step

**Conteúdo típico:**
- `TESTIDS_MANIFEST.md` - Catálogo de test IDs
- Guias de deploy
- Procedimentos de rollback
- Troubleshooting guides

**Quando usar:** Operações rotineiras, incidentes, onboarding

---

### 📁 06-certificacao-deploy/
**Propósito:** Checklists e validações pré-deploy

**Conteúdo típico:**
- Checklist de deploy
- Critérios de certificação
- Testes de aceitação
- Validação de ambiente

**Quando usar:** Antes de cada deploy para produção

---

### 📁 07-organizacao-limpeza/
**Propósito:** Documentação de limpeza de código, refatorações, dívidas técnicas

**Conteúdo típico:**
- Arquivos mortos removidos
- Refatorações de estrutura
- Consolidação de duplicatas
- Resolução de dívidas técnicas

**Quando usar:** Sprints de housekeeping, análise de débito técnico

---

### 📁 08-resumos-executivos/
**Propósito:** Documentos resumidos para stakeholders não-técnicos

**Conteúdo típico:**
- Status de projeto
- Principais entregas
- Métricas e KPIs
- Decisões de negócio

**Quando usar:** Reuniões com Product Owners, apresentações, relatórios gerenciais

---

### 📁 _archived/
**Propósito:** Documentos obsoletos mas preservados para histórico

**Regra:** Documentos movidos para `_archived/` devem ter data e motivo no nome
- Exemplo: `teams-CONTRACT_OLD_2025-12-15_substituido-por-v1.3.md`

---

## 3. ARQUIVOS RAIZ

### _INDICE.md
**Propósito:** Índice navegável de toda a documentação
**Atualização:** Manual (após mudanças significativas)

### _MAPA.md
**Propósito:** Mapa visual da estrutura (árvore de pastas)
**Atualização:** Manual (após reorganização)

### _README.md
**Propósito:** Introdução à documentação, como navegar, convenções
**Atualização:** Manual (após mudanças de convenções)

### ESTRUTURA_BANCO.md
**Propósito:** Schema completo do banco de dados
**Atualização:** Automática (via script) ou manual após migrations

---

## 4. CONVENÇÕES DE NOMENCLATURA

### 4.1. Arquivos de Contrato
**Formato:** `{modulo}-CONTRACT.md`
- Exemplo: `teams-CONTRACT.md`, `training-CONTRACT.md`
- **Sempre em MAIÚSCULAS**
- Versionado no cabeçalho

### 4.2. Implementações
**Formato:** `IMPLEMENTACAO_{FUNCIONALIDADE}.md` ou `{MODULO}_IMPLEMENTACAO.md`
- Exemplo: `IMPLEMENTACAO_PAGINA_TEAMS.md`
- **Sempre em MAIÚSCULAS**

### 4.3. Correções/Fixes
**Formato:** `FIX_{PROBLEMA}.md` ou `CORRECAO_{ESCOPO}.md`
- Exemplo: `FIX_CORS_APPLIED.md`, `CORRECAO_CRITICA_COMPETITIONS.md`
- **Sempre em MAIÚSCULAS**

### 4.4. Planejamentos
**Formato:** `PLANO_{ESCOPO}.md`
- Exemplo: `PLANO_MIGRACAO_TEAMS.md`
- **Sempre em MAIÚSCULAS**

### 4.5. Relatórios
**Formato:** `RELATORIO_{ESCOPO}.md`
- Exemplo: `RELATORIO_TOPBAR_v2.0.md`
- **Sempre em MAIÚSCULAS**

### 4.6. Arquivos Temporários/Debug
**Formato:** `_prefixo_nome.md` (começar com underscore)
- Exemplo: `_DEBUG_TEAMS.md`, `_TEMP_NOTES.md`
- **Deletar após uso**

---

## 5. FLUXO DE DOCUMENTAÇÃO

### 5.1. Durante Desenvolvimento de Feature
```
1. Consultar contrato em 02-modulos/{modulo}/{modulo}-CONTRACT.md
2. Criar documento de planejamento em 04-planejamento/ (se necessário)
3. Desenvolver feature
4. Atualizar contrato se API/schema mudou
5. Criar documento em 03-implementacoes-concluidas/ com detalhes técnicos
```

### 5.2. Durante Bug Fix
```
1. Identificar módulo afetado
2. Criar FIX_{PROBLEMA}.md em 03-implementacoes-concluidas/
3. Documentar:
   - Problema
   - Causa raiz
   - Solução
   - Arquivos modificados
   - Testes
4. Atualizar contrato se comportamento mudou
```

### 5.3. Durante Refatoração
```
1. Criar documento em 07-organizacao-limpeza/
2. Listar arquivos antes/depois
3. Justificar mudanças
4. Atualizar referências em outros docs
5. Mover arquivos obsoletos para _archived/
```

---

## 6. MANUTENÇÃO DA DOCUMENTAÇÃO

### 6.1. Revisão Mensal
- [ ] Verificar docs desatualizados
- [ ] Mover obsoletos para `_archived/`
- [ ] Atualizar `_INDICE.md`
- [ ] Consolidar duplicatas

### 6.2. Revisão Trimestral
- [ ] Revisar estrutura de pastas
- [ ] Atualizar convenções se necessário
- [ ] Arquivar sprints antigas de `04-planejamento/`
- [ ] Consolidar resumos executivos

### 6.3. Pós-Deploy
- [ ] Verificar `_DEPLOY_CHECKLIST.md` em `06-certificacao-deploy/`
- [ ] Criar resumo executivo se deploy major
- [ ] Atualizar contratos afetados

---

## 7. FERRAMENTAS E AUTOMAÇÃO

### 7.1. Scripts Disponíveis
- `scripts/generate_db_schema.py` - Gera `ESTRUTURA_BANCO.md`
- `scripts/validate_testids.py` - Valida `TESTIDS_MANIFEST.md`
- (Futuro) `scripts/generate_index.py` - Gera `_INDICE.md` automaticamente

### 7.2. Validação de Docs
```powershell
# Verificar links quebrados
Get-ChildItem -Recurse -Filter *.md | Select-String -Pattern '\[.*\]\((.*)\)' | ...

# Listar docs sem atualização recente
Get-ChildItem -Recurse -Filter *.md | Where-Object { $_.LastWriteTime -lt (Get-Date).AddMonths(-3) }
```

---

## 8. EXEMPLOS DE USO

### Exemplo 1: Novo desenvolvedor entrando no projeto
```
1. Ler: docs/_README.md
2. Ler: docs/01-sistema-atual/ARQUITETURA.md (se existir)
3. Explorar: docs/02-modulos/ (módulo que vai trabalhar)
4. Consultar: docs/05-guias-procedimentos/ (setup de ambiente)
```

### Exemplo 2: Implementando nova feature no módulo Teams
```
1. Ler: docs/02-modulos/teams/teams-CONTRACT.md
2. Planejar: Criar docs/04-planejamento/PLANO_NOVA_FEATURE.md
3. Desenvolver
4. Documentar: Criar docs/03-implementacoes-concluidas/IMPLEMENTACAO_NOVA_FEATURE.md
5. Atualizar: docs/02-modulos/teams/teams-CONTRACT.md
```

### Exemplo 3: Corrigindo bug crítico
```
1. Investigar: docs/02-modulos/{modulo}/ + logs
2. Corrigir código
3. Documentar: Criar docs/03-implementacoes-concluidas/FIX_{PROBLEMA}.md
4. Validar: Executar testes E2E
5. Atualizar: Contrato se comportamento mudou
```

---

## 9. DOCUMENTOS CANÔNICOS

Estes documentos são **fontes da verdade** e devem ser mantidos atualizados:

| Documento | Localização | Responsável | Frequência de Atualização |
|-----------|-------------|-------------|---------------------------|
| `teams-CONTRACT.md` | `02-modulos/teams/` | Tech Lead | A cada mudança de API |
| `ESTRUTURA_BANCO.md` | `docs/` (raiz) | Backend Lead | A cada migration |
| `TESTIDS_MANIFEST.md` | `05-guias-procedimentos/` | QA Lead | A cada novo testid |
| `_DEPLOY_CHECKLIST.md` | `06-certificacao-deploy/` | DevOps | A cada lição aprendida |

---

## 10. STATUS ATUAL (14/01/2026)

### ✅ Completo
- Estrutura de 8 pastas criada
- Contratos de Teams, Training documentados
- Implementações recentes documentadas
- TESTIDS_MANIFEST atualizado

### 🚧 Em Progresso
- Consolidação de docs antigos para estrutura nova
- Criação de resumos executivos

### ❌ Pendente
- Documentação do módulo Athletes (contrato)
- Documentação do módulo Games (contrato)
- Automação de geração de _INDICE.md
- Guias de procedimentos completos

---

**Mantido por:** Tech Team  
**Revisão:** Mensal  
**Última revisão:** 14/01/2026
