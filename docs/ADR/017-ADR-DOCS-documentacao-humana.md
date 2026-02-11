# 017-ADR-DOCS — Governança de Documentação Humana

**Status:** Proposta
**Data:** 2026-02-11
**Autor:** Equipe HB Track
**Fase:** F2
**Módulos Afetados:** Todos (infraestrutura de governança)

---

## Contexto

A ADR-016 estabeleceu a documentação machine-readable (`docs/_ai/`) como Single Source of Truth para agentes de IA — métricas parseáveis, contratos de agentes, quality gates automatizados. Essa camada é o **"músculo"**: define *como* executar.

Falta o complemento: governar a **documentação humana** (`docs/_canon/`, `docs/02_modulos/`, `docs/ADR/`, `docs/00_product/`) — a **"alma"**: define *por que* executar. Sem governança explícita, surgem três problemas concretos:

### Problema 1: Drift humano ↔ IA

Uma regra é alterada no Markdown canônico (ex: mudar janela de edição de 10min para 15min no `TRD_TRAINING.md`), mas ninguém atualiza o `quality-gates.yml` ou o `agent-spec.json`. Resultado: humano lê 15min, agente aplica 10min.

### Problema 2: Nível de abstração errado

Documentação humana cai no nível técnico (descrevendo "constraint `ck_focus_total_max_120` valida CHECK `total <= 120`") em vez do nível de negócio ("a soma das 7 áreas de foco tático não pode ultrapassar 120% porque reflete a distribuição real de atenção do treinador durante uma sessão"). Novos membros entendem *o que* mas não *por que*.

### Problema 3: Onboarding fragmentado

Um novo desenvolvedor precisa ler `00_START_HERE.md` → `01_AUTHORITY_SSOT.md` → `TRD_TRAINING.md` → `INVARIANTS_TRAINING.md` → vários ADRs para entender o módulo Training. Sem uma narrativa de onboarding por módulo, o caminho é longo e a compreensão superficial.

**Componentes Relacionados:**
- Documentação canônica: `docs/_canon/` (10 ficheiros de governança)
- Documentação modular: `docs/02_modulos/training/` (PRD_BASELINE, TRD, INVARIANTS, UAT_PLAN)
- Documentação estratégica: `docs/00_product/PRD_HB_TRACK.md`
- ADRs: `docs/ADR/` (001–016)
- Docs AI (contraparte): `docs/_ai/` (ADR-016)

---

## Decisão

Estabelecer regras obrigatórias para a criação, manutenção e sincronização da documentação humana no HB Track.

### 1. Taxonomia de Documentação Humana

Cada tipo de documento tem um lugar e um propósito específico:

| Pasta | Tipo | Propósito | Exemplo |
|-------|------|-----------|---------|
| `docs/00_product/` | PRD estratégico | Visão do produto, features macro, roadmap | `PRD_HB_TRACK.md` |
| `docs/02_modulos/<mod>/` | PRD_BASELINE + TRD + INVARIANTS + UAT | Estado implementado, referência técnica, contratos, cenários de teste | `PRD_BASELINE_ASIS_TRAINING.md`, `TRD_TRAINING.md` |
| `docs/_canon/` | Governança operacional | Regras de pipeline, SSOT, workflows, comandos aprovados | `05_MODELS_PIPELINE.md`, `08_APPROVED_COMMANDS.md` |
| `docs/ADR/` | Decisões arquiteturais | Registo formal do "por quê" de decisões técnicas | `001-ADR-TRAIN-ssot-precedencia.md` |
| `docs/_generated/` | Artefatos gerados (READ-ONLY) | `schema.sql`, `openapi.json`, `parity_report.json` | Nunca editar manualmente |
| `docs/_ai/` | Docs machine-readable (ADR-016) | Parseáveis por agentes e CI | `_INDEX.md`, protocolos, guardrails |

**Regra:** Documentos fora destas pastas devem ser movidos ou eliminados. Novas pastas requerem ADR.

### 2. Nível de Abstração Obrigatório

A documentação humana deve operar no **nível de negócio/domínio**, não no nível de implementação:

| Nível | Correto (Humano) | Incorreto (deve estar em `_ai/` ou código) |
|-------|-------------------|---------------------------------------------|
| Regra de negócio | "A soma das áreas de foco tático ≤120% porque reflete a distribuição real de atenção do treinador" | "CHECK constraint `ck_focus_total_max_120` valida `total <= 120`" |
| Lifecycle | "Uma sessão em `pending_review` permite ao coordenador avaliar antes de arquivar" | "Estado muda via `UPDATE training_sessions SET status = 'readonly'`" |
| RBAC | "Apenas o treinador responsável ou hierarquia superior pode editar a sessão nos primeiros 10 minutos" | "router verifica `current_user.role in ['treinador', 'coordenador', 'dirigente']`" |
| Soft delete | "Exclusões preservam histórico com motivo obrigatório para auditoria desportiva" | "`deleted_at` NOT NULL implica `deleted_reason` NOT NULL via CHECK pair" |

**Regra:** Documentação humana referencia constraints e operationIds como **evidência** (ex: "ver `ck_focus_total_max_120` em `schema.sql`"), mas a **explicação** deve ser narrativa e orientada ao domínio de handebol.

### 3. Regra de Sincronia Humano ↔ IA

Quando um documento canônico humano é alterado:

1. O mesmo PR **deve** atualizar o documento AI derivado correspondente (se existir)
2. Se não existir derivado AI, avaliar se deve ser criado (threshold: regra usada por agente ou CI)
3. A checklist de PR inclui item obrigatório: "Documentação AI sincronizada? (N/A se não aplica)"

**Fluxo:**
```
Humano edita docs/_canon/ ou docs/02_modulos/
    │
    ├──→ Atualiza doc AI correspondente em docs/_ai/ (mesmo PR)
    │
    └──→ CI verifica: "artefatos AI regenerados sem erro?"
              │
              ├── OK → PR segue para review
              └── FAIL → PR bloqueado
```

**Mapeamento de sincronia (exemplos iniciais):**

| Doc Humano (SSOT) | Doc AI (derivado) | Trigger |
|--------------------|-------------------|---------|
| `QUALITY_METRICS.md` | `_ai/_specs/quality-gates.yml` | Mudança de threshold |
| `03_WORKFLOWS.md` | `_ai/_specs/workflows.yml` | Mudança de steps/condições |
| `08_APPROVED_COMMANDS.md` | `_ai/_specs/approved-commands.yml` | Mudança de whitelist |
| `INVARIANTS_TRAINING.md` | `_ai/INVARIANTS_AGENT_PROTOCOL.md` | Nova invariante ou mudança de classe |

### 4. Regra de Onboarding por Módulo

Todo módulo documentado deve ter uma **narrativa de entrada** que permita a um novo desenvolvedor (ou a um "eu futuro") compreender o domínio sem decifrar YAMLs:

**Estrutura mínima de onboarding por módulo:**

1. **"Por que existe este módulo?"** — Contexto de negócio (1-2 parágrafos)
2. **"Quais são as regras fundamentais?"** — Top 5-10 regras de domínio em linguagem natural
3. **"Onde está o quê?"** — Mapa: PRD_BASELINE → TRD → INVARIANTS → ADRs relevantes
4. **"Como validar?"** — Comandos para regenerar artefatos e verificar conformidade

**Para o módulo Training**, este papel é cumprido por `PRD_BASELINE_ASIS_TRAINING.md` (seção Contexto + FRs) + `00_START_HERE.md` (routing). Para novos módulos, criar documento equivalente.

### 5. Formato e Convenções

| Convenção | Regra |
|-----------|-------|
| **Idioma** | Português (PT-BR) para narrativa; Inglês para termos técnicos (`constraint_name`, `operationId`, nomes de tabelas) |
| **Referências cruzadas** | Links relativos ao repo root: `[TRD_TRAINING.md](../02_modulos/training/TRD_TRAINING.md)` |
| **Evidência** | Citar `ficheiro:símbolo` (ex: `schema.sql:ck_focus_total_max_120`) — não inventar |
| **Versionamento** | PRD/TRD/INVARIANTS usam semver no header (`v1.8`); ADRs usam Status (`Proposta → Aceita`) |
| **Sincronismo de versão** | Todos os docs de um módulo devem referenciar a mesma versão TRD; se TRD avança, atualizar referências no mesmo PR |
| **Proibição** | Não duplicar conteúdo de `schema.sql` ou `openapi.json` — apenas referenciar |

---

## Alternativas Consideradas

### Alternativa 1: Não criar ADR — manter documentação humana sem governança

**Prós:**
- Zero overhead adicional
- Flexibilidade total na escrita

**Contras:**
- Drift inevitável entre docs humanos e AI (já observado com thresholds)
- Onboarding depende de conhecimento tribal
- Sem contrato de sincronia, ADR-016 perde eficácia (YAML correto, Markdown desatualizado)

**Razão da rejeição:** ADR-016 governa a IA; sem ADR-017, metade do sistema documental fica sem regras.

### Alternativa 2: Fundir com ADR-016 (um único ADR de documentação)

**Prós:**
- Um único ponto de referência
- Menos ADRs para manter

**Contras:**
- ADR fica excessivamente longo e com dois públicos distintos (agentes vs humanos)
- Decisões de formato YAML/JSON (ADR-016) são ortogonais a decisões de narrativa/onboarding (ADR-017)
- Dificulta rastreabilidade: "mudámos a regra de sincronia humana" vs "mudámos o schema do agent-spec"

**Razão da rejeição:** Separação de concerns — cada ADR deve ter um único propósito claro.

### Alternativa 3: Wiki externa (Notion, Confluence)

**Prós:**
- Interface rica (tabelas, embeds, busca)
- Colaboração em tempo real

**Contras:**
- Fora do Git — sem versionamento, sem PRs, sem CI
- Impossível validar sincronia com docs AI automaticamente
- Vendor lock-in

**Razão da rejeição:** Documentação que governa código deve viver junto ao código. Princípio: "docs as code".

---

## Consequências

### Positivas

- ✅ **Sincronia garantida:** Regra explícita de que mudança humana → atualização AI no mesmo PR elimina drift estrutural
- ✅ **Onboarding previsível:** Novos devs seguem caminho padronizado por módulo (contexto → regras → mapa → validação)
- ✅ **Manutenibilidade:** Daqui a 6 meses, a razão de negócio de uma regra está documentada em linguagem natural, não enterrada em YAML
- ✅ **Complemento da ADR-016:** Sistema documental completo — alma (017) + músculo (016)
- ✅ **Rastreabilidade:** Git history mostra *o que* mudou (diff) e docs humanos explicam *por que* mudou

### Negativas

- ⚠️ **Overhead de PR:** Cada mudança em doc canônico pode exigir atualização AI — aumenta escopo de PRs
  - *Mitigação:* Checklist com "N/A" para mudanças sem impacto AI
- ⚠️ **Disciplina editorial:** Manter nível de abstração correto (negócio vs técnico) requer revisão humana
  - *Mitigação:* Exemplos concretos nesta ADR servem como referência para reviewers

### Neutras

- ℹ️ A taxonomia de pastas já existe informalmente; esta ADR formaliza e torna obrigatória
- ℹ️ A regra de idioma (PT-BR + EN técnico) já é prática corrente; agora é vinculante

---

## Validação

### Critérios de Conformidade

- [ ] Taxonomia de pastas (`00_product/`, `02_modulos/`, `_canon/`, `ADR/`, `_generated/`, `_ai/`) documentada e respeitada
- [ ] Nenhum documento canônico novo criado fora das pastas definidas sem ADR
- [ ] Regra de sincronia humano ↔ AI incluída em checklist de PR
- [ ] Módulo Training possui narrativa de onboarding validada (PRD_BASELINE + 00_START_HERE)
- [ ] Referências cruzadas em docs existentes usam formato `ficheiro:símbolo`
- [ ] Documentação atualizada: `_INDEX_ADR.md` inclui entrada 017

### Impacto em Testes

**Testes afetados:** Nenhum (ADR de governança documental, não de código).

**Novos testes necessários:**
- CI lint (futuro, P2): script que valida sincronia entre docs humanos e AI derivados

---

## Implementação

### Fase 0: ADR e Audit (P0 — Sprint atual)

- [ ] Criar esta ADR (`017-ADR-DOCS-documentacao-humana.md`)
- [ ] Atualizar `_INDEX_ADR.md`
- [ ] Auditar docs existentes contra taxonomia: listar documentos fora do lugar

### Fase 1: Templates e Onboarding (P1 — Próxima sprint)

- [ ] Criar template de onboarding por módulo (`_TEMPLATE_MODULE_ONBOARDING.md`)
- [ ] Validar que módulo Training cumpre requisitos de onboarding
- [ ] Adicionar item de sincronia humano ↔ AI ao PR template (`.github/PULL_REQUEST_TEMPLATE.md`)

### Fase 2: CI Lint de Sincronia (P2 — Backlog)

- [ ] Script que verifica timestamps: se doc humano é mais recente que doc AI derivado, emitir warning
- [ ] Integrar no workflow CI existente (`quality-gates.yml`)

### Dependências

- Depende de: ADR-016 (estrutura `docs/_ai/` já criada)
- Complementa: ADR-001 (SSOT precedência), ADR-008 (governança por artefatos)

### Estimativa

- Complexidade: Baixa (governança documental, sem código de produção)
- Risco: Baixo (não altera comportamento do sistema)

---

## Segurança e Compliance

- [ ] Documentação humana **não deve conter** dados reais de atletas (nomes, CPF, dados médicos) — usar exemplos fictícios
- [ ] Exemplos em docs devem seguir LGPD: "Atleta A", "Equipa X", nunca dados identificáveis
- [ ] Docs com informação sensível de infraestrutura (credentials, connection strings) são **proibidos** — usar referências a variáveis de ambiente

---

## Rollback Plan

Caso seja necessário reverter esta decisão:

1. Alterar Status desta ADR para `Depreciada`
2. Remover item de sincronia do PR template
3. Desactivar CI lint de sincronia (se implementado)
4. Documentar razão da depreciação em nota nesta ADR

**Impacto:** Documentação humana volta a ser não-governada; risco de drift aceite explicitamente.

---

## Referências

- ADR-001: [001-ADR-TRAIN-ssot-precedencia.md](001-ADR-TRAIN-ssot-precedencia.md) — Hierarquia SSOT
- ADR-008: [008-ADR-TRAIN-governanca-por-artefatos.md](008-ADR-TRAIN-governanca-por-artefatos.md) — Governança por artefatos gerados
- ADR-016: [016-ADR-DOCS.md](016-ADR-DOCS.md) — Machine-Readable Documentation & AI Quality Gates
- Governança: [00_START_HERE.md](../docs/_canon/00_START_HERE.md) — Porta de entrada obrigatória
- SSOT: [01_AUTHORITY_SSOT.md](../docs/_canon/01_AUTHORITY_SSOT.md) — Precedência de fontes

---

## Notas Adicionais

- Esta ADR formaliza práticas que já existem informalmente no projecto (taxonomia de pastas, idioma misto, referências por evidência). O valor está em torná-las **vinculantes e rastreáveis**.
- A metáfora "alma (017) + músculo (016)" deve ser usada em onboarding para explicar o sistema documental dual.
- Futuro: quando novos módulos forem criados (ex: Match, Analytics), aplicar a mesma estrutura de onboarding definida aqui.

---

## Revisões

| Data | Autor | Mudança | Versão |
|------|-------|---------|--------|
| 2026-02-11 | Equipe HB Track | Criação inicial | 1.0 |

---

**Assinaturas:**

- [ ] Aprovado por: [nome do tech lead/arquiteto]
- [ ] Revisado por: [nome do revisor]
- [ ] Data de aprovação: YYYY-MM-DD
