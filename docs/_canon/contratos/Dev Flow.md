# HBTRACK_DEV_FLOW_CONTRACT — HB Track (Determinístico) — v1.0.5

Este documento é o CONTRATO canônico do fluxo determinístico de desenvolvimento do HB Track usando IA + evidências.
Qualquer divergência entre prática e este contrato é BUG de governança.

## 1. Versão (governança)
- Versão do protocolo: v1.0.5
- scripts/run/hb.py MUST reportar esta versão (comando `hb version` e também no header do `hb check`).

Mudança em qualquer arquivo dentro de:
- docs/_canon/contratos/**
- docs/_canon/specs/**
MUST:
1) ser feita via AR de governança (docs/hbtrack/ars/)
2) bump de versão (ex.: v1.0.4 → v1.0.5)
3) atualizar a versão reportada pelo hb.py

## 2. Canon Paths (imutáveis sem AR de governança)
Dentro do repo:

2.1 Referências
- PRD (referência de negócio): docs/hbtrack/PRD Hb Track.md
- SSOT (contratos do sistema): docs/ssot/
  - docs/ssot/schema.sql
  - docs/ssot/openapi.json
  - docs/ssot/alembic_state.txt

2.2 Fluxo (artefatos)
- Planos (JSON do Arquiteto): docs/_canon/planos/
- ARs (materialização do plano): docs/hbtrack/ars/
- Evidence packs (logs auditáveis): docs/hbtrack/evidence/
- Índice (opcional, rastreio): docs/hbtrack/_INDEX.md

2.3 Execução (scripts)
- CLI: scripts/run/hb.py
- Git hook: scripts/git-hooks/pre-commit (Python)
- Política: scripts MUST ser Python (.py). .sh e .ps1 são proibidos.

## 3. Definições
- Plano (Plan JSON): arquivo JSON criado pelo Arquiteto, validado por schema e versão.
- AR (Architectural Record): arquivo .md gerado por hb plan, governando uma tarefa atômica.
- Evidence pack: arquivo .log gerado por hb report, contendo comando + Exit Code + stdout/stderr + contexto mínimo.
- “Governed code”: diretórios de código que exigem AR no commit quando modificados (definidos em GOVERNED_ROOTS no hb.py).

## 4. Contrato do Plano (AR Contract)
- Plano MUST estar em: docs/_canon/planos/*.json
- Plano MUST validar contra o schema canônico:
  - docs/_canon/contratos/ar_contract.schema.json
- Plano.version MUST ser igual a v1.0.5 (versão do protocolo).
- Campos de “texto livre” são permitidos APENAS nos campos canônicos do schema (notes/assumptions/risks/notes por task).

## 5. Ciclo de Vida do Desenvolvimento (7 passos) — fluxo oficial
Passo 1 — REFERÊNCIA
O Arquiteto lê:
- PRD: docs/hbtrack/PRD Hb Track.md
- SSOT: docs/ssot/**

Passo 2 — PLANO
O Arquiteto gera um plano JSON válido (AR Contract) e salva em:
- docs/_canon/planos/<nome_do_plano>.json

Passo 3 — MATERIALIZAÇÃO
Você executa:
- python scripts/run/hb.py plan docs/_canon/planos/<nome_do_plano>.json

Resultado:
- cria ARs em docs/hbtrack/ars/AR_<id>_<slug>.md
- (opcional) atualiza docs/hbtrack/_INDEX.md

Passo 4 — ANÁLISE
Executor abre a AR e preenche “Análise de Impacto” ANTES de codar.

Passo 5 — AÇÃO
Executor implementa no código (em seus roots reais, ex.: backend/ e Hb Track - Fronted/).

Passo 6 — VALIDAÇÃO
Executor (ou você) executa:
- python scripts/run/hb.py report <id> "<validation_command>"

Regras:
- O comando deve bater exatamente com o Validation Command do contrato da AR (se declarado).
- hb report grava evidence pack no caminho Evidence File do contrato.

Passo 7 — FECHAMENTO
No commit, o hook executa:
- python scripts/run/hb.py check --mode pre-commit

hb check valida integridade do commit e bloqueia se falhar.

## 6. Regras determinísticas mínimas (mecanizadas)
R1) Plano inválido (path/schema/version) => hb plan FAIL (não materializa AR).
R2) Evidência válida de sucesso exige:
- AR com marcador ✅ SUCESSO (gerado pelo hb report)
- Evidence File existente e STAGED com “Exit Code: 0”
R3) Se SSOT estiver STAGED => MUST existir AR STAGED que:
- marcou [x] o SSOT em “SSOT Touches”
- tem evidência ✅ SUCESSO
- tem Evidence File staged com Exit Code: 0
R4) Se houver mudança em governed roots (GOVERNED_ROOTS) no STAGED => MUST existir ao menos 1 AR STAGED.

## 7. O que NÃO é garantido automaticamente (processual)
- Mapear exatamente “quais arquivos pertencem a qual AR” (isso exigiria manifest por AR + checagem diff→manifest).
- Garantir qualidade funcional do produto: isso depende do “validation_command” ser um gate real.

## 8. Nota de estabilidade de paths (Fronted vs Frontend)
Se existir diretório “Hb Track - Fronted” (com ‘Fronted’), ele é um path real do repo.
Renomear diretório é mudança de governança/infra: só por AR dedicada + evidência de migração controlada.