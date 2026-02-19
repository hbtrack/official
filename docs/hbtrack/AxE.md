O seu projeto agora não é apenas código, é uma **máquina de engenharia**. Para que o **Cline**, o **ChatGPT** ou até mesmo o "você do futuro" não se percam, o `README.md` precisa atuar como o **Manual de Operação do Sistema**.

Aqui está o `README.md` técnico, formatado para ser o seu **Norte** (e o do Arquiteto):

---

# 🚀 HB Track: Handebol Determinístico

Este projeto utiliza o framework **HB Track**, um sistema de desenvolvimento orientado a evidências e contratos. Aqui, o código é um subproduto de um plano rigoroso e auditável.

## 🏗️ A Estrutura de Verdade (SSOT)

O projeto é guiado por três arquivos mestres que definem a realidade do sistema:

* `schema.sql`: Definição atual e imutável do banco de dados.
* `openapi.json`: Contrato de interface das APIs.
* `alembic_state.txt`: Estado das migrações de dados.

## 🛠️ O Ecossistema de Automação (CLI `hb`)

A CLI `hb` (gerenciada por `hb_cli.py`) é o orquestrador do fluxo.

| Comando | Descrição | Quando usar |
| --- | --- | --- |
| `hb plan <file.json>` | **Explodidor:** Transforma o plano do Arquiteto em ARs individuais. | Após o Arquiteto gerar o JSON. |
| `hb report <id> "<cmd>"` | **Validador:** Executa testes e anexa o log de evidência à AR. | Após o Executor terminar o código. |
| `hb check` | **Guardião:** Verifica se houve drift (desvio) no SQL ou OpenAPI. | Antes de cada commit. |

---

## 🔄 Workflow de Desenvolvimento (Passo a Passo)

### 1. Fase de Arquitetura (O Plano)

O Arquiteto (IA) analisa os requisitos e gera um JSON seguindo o **AR CONTRACT**.

```bash
# Salve o JSON em raw_plan.json e execute:
hb plan raw_plan.json

```

Isso criará os arquivos em `docs/ars/` com status `🔲 PENDENTE`.

### 2. Fase de Execução (O Código)

O Executor (Cline/IA) lê a AR correspondente e implementa a lógica em `src/`.

* Nenhuma linha de código deve ser escrita sem uma AR aberta.

### 3. Fase de Evidência (A Prova)

Após codar, o Executor deve provar que a tarefa foi concluída:

```bash
hb report 001 "npm test tests/scout.test.js"

```

Isso anexa o log de sucesso (ou falha) e a data diretamente no documento da AR.

### 4. Fase de Commit (A Trava)

O projeto possui um **Git Pre-commit Hook**. Se você tentar dar commit e:

* O `schema.sql` tiver mudado sem uma AR de suporte.
* Existirem ARs com status `PENDENTE`.
O commit será **BLOQUEADO** automaticamente.

---

## ⚙️ Configuração do Ambiente

1. **Instalar Dependências:**
`pip install argparse difflib`
2. **Ativar os Hooks de Segurança:**
`git config core.hooksPath scripts/git-hooks`
3. **Alias da CLI (Recomendado):**
Adicione ao seu `.bashrc` ou `.zshrc`:
`alias hb='python3 path/to/hb_cli.py'`

---


**"Como o Arquiteto sabe que uma AR antiga não quebrou com a nova?"**

No futuro, você pode adicionar ao seu `hb check` um comando de **Análise de Impacto Cross-AR**, que verifica se a nova `AR_005` toca em um arquivo que foi "fechado" pela `AR_002`, forçando uma revisão de regressão.

**Quer que eu te ajude com a primeira tarefa do Arquiteto agora para testar se ele entendeu o README?** Basta me dar o objetivo da primeira funcionalidade do seu Handebol Track!