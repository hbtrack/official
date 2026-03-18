# GUIA DE DESENVOLVIMENTO - HB TRACK

Este documento é um guia prático para os devs do HB Track.

> **⚠️ AMBIENTE LINUX-FIRST:** A partir de 2026-03-13, todos os comandos neste guia assumem **Linux/WSL** como ambiente de desenvolvimento. Comandos PowerShell são mantidos apenas como referência histórica.

* Objetivos: 
   - Fornecer um manual de referência rápida.
   - Documentar as ferramentas e processos do desenvolvimento.
   - Lembrar os devs sobre o uso correto das ferramentas e processos.
   - Evitar erros comuns e tirar dúvidas frequentes.

"In God we trust; all others must bring data." — W. Edwards Deming

---

## Workspace

**Root canônico:** `/home/$USER/HB-TRACK` (Linux/WSL)

```bash
cd ~/HB-TRACK
pwd  # Confirmar workspace correto
```

---

## Inicio 

**PASSO 0**: Toolchain WSL-native (sem wrappers Windows) + sanity check

* Objetivo: 
   - Garantir Node.js **WSL-native** no PATH (evitar `node.exe`/interop).
   - Preferir CLIs pinadas do projeto (via `node_modules/.bin`).
   - Evitar wrappers em `${HOME}/bin/*`.

Comando:

```bash
# Linux/WSL (carrega NVM + PATH do projeto)
source ./setup-env.sh

# (Opcional) verificação rápida das ferramentas externas
bash scripts/contract_gates/verify_tools.sh

# Pipeline oficial de contract gates (gera _reports/contract_gates/latest.json)
python3 scripts/validate_contracts.py
```

<details>
<summary>📦 Comando PowerShell (legado - apenas referência)</summary>

```powershell
# ⚠️ Legado: o ambiente canônico é WSL/Linux. Use apenas se necessário.
python scripts/validate_contracts.py
```
</details>



### Ferramentas Necessárias

| Ferramenta | Propósito | Instalação |
|------------|-----------|------------|
| **Node.js (WSL-native)** | Runtime para CLIs Node (Redocly/Spectral/AsyncAPI) | `nvm install` + `source ./setup-env.sh` |
| **npm** | Package manager | Incluído com Node.js (via nvm) |
| **Go** | Runtime para `oasdiff` (recomendado) | https://go.dev/dl/ |
| **Redocly CLI** | Validação estrutural OpenAPI | **Preferir local** (devDependency) via `npm ci` / `npm i -D @redocly/cli` |
| **Spectral CLI** | Linting de políticas OpenAPI | **Preferir local** (devDependency) via `npm ci` / `npm i -D @stoplight/spectral-cli` |
| **oasdiff** | Detecção de breaking changes | `go install github.com/oasdiff/oasdiff@latest` |

### Bootstrap (WSL-native)

O bootstrap canônico do workspace é **carregar a toolchain WSL-native** e validar as ferramentas externas:

```bash
source ./setup-env.sh
bash scripts/contract_gates/verify_tools.sh
```

> Nota: o pipeline oficial não depende de wrappers Windows (`node.exe`/`oasdiff.exe`) e deve rodar no WSL.

### Validação de Contratos (pipeline oficial)

```bash
python3 scripts/validate_contracts.py
```

**Relatório (evidência):** `_reports/contract_gates/latest.json`

### Scripts auxiliares (opcionais)

- `source scripts/contract_gates/env.sh` — prepara PATH (WSL-native) e expõe `node_modules/.bin`
- `bash scripts/contract_gates/verify_tools.sh` — sanity check de CLIs
- `bash scripts/contract_gates/provision_oasdiff.sh` — instala `oasdiff` via `go install` (se Go estiver disponível)

### Gates Críticos

| Gate | Ferramenta | Bloqueia | Descrição |
|------|-----------|----------|-----------|
| `OPENAPI_POLICY_RULESET_GATE` | Spectral | ✓ | Linting de regras custom (`.spectral.yaml`) |
| `CONTRACT_BREAKING_CHANGE_GATE` | oasdiff | ✓ | Detecta breaking changes vs baseline |
| `OPENAPI_ROOT_STRUCTURE_GATE` | Redocly | ✓ | Validação estrutural (`redocly.yaml`) |

### Pipeline CI/CD Recomendado

```yaml
jobs:
  validate-contracts:
    steps:
      - name: Install Node deps (pinned)
        run: npm ci
      
      - name: Validate Contracts
        run: |
          python3 scripts/validate_contracts.py
        continue-on-error: false
      
      - name: Upload Evidence
        uses: actions/upload-artifact@v3
        with:
          name: contract-gates-report
          path: _reports/contract_gates/
```

### Troubleshooting

#### Problema: "npm não encontrado" mesmo com Node.js instalado

**Solução (WSL/Linux)**: rode `source ./setup-env.sh` para carregar NVM e expor `node`/`npm` no PATH.

#### Problema: "oasdiff não encontrado" mesmo após instalação

**Solução (WSL/Linux)**: adicione `$GOPATH/bin` ao PATH e/ou rode `bash scripts/contract_gates/provision_oasdiff.sh`.

#### Problema: Gate OPENAPI_POLICY_RULESET_GATE falha

**Solução**: Execute Spectral manualmente para ver detalhes:

```bash
spectral lint contracts/openapi/openapi.yaml --ruleset .spectral.yaml
```

### Relatórios de Evidência

Todos os relatórios são machine-readable (JSON):

- **Bootstrap**: `_reports/contract_gates/bootstrap.json`
- **Gates**: `_reports/contract_gates/latest.json`
- **Conformidade**: `_reports/contract_gates/CONFORMIDADE_EMPIRICA.md`

### Próximos Passos

Após validação 100% PASS:

1. **Gerar cliente TypeScript**:
   ```bash
   openapi-generator generate \
     -i contracts/openapi/openapi.yaml \
     -g typescript-fetch \
     -o "Hb Track - Frontend/src/api/generated"
   ```

2. **Sincronizar tipos** (gate `GENERATED_CLIENT_SYNC`)

3. **Testes de contrato runtime** (Schemathesis)

---

## Ecossistema de Scripts

### Scripts de Geração (`scripts/generate/`)

**Objetivo**: Automatizar criação de artefatos derivados (DRY — Don't Repeat Yourself)

```powershell
# Criar estrutura mínima de docs para novo módulo
python scripts/generate/gen_module_docs_minimum.py

# Gerar baseline do OpenAPI para oasdiff
python scripts/generate/gen_openapi_baseline.py

# Gerar matriz de testes por módulo
python scripts/generate/gen_test_matrix.py
```

**Filosofia**: Artefatos derivados são **gerados**, não escritos manualmente.

### Scripts de Compilação (`scripts/contracts/validate/`)

**Objetivo**: Compilar intenções em contratos validados (fail-closed)

#### 1. Compilador de Intenção (DSL de alto nível)

```powershell
# Compila .intent.yaml → OpenAPI completo
python scripts/contracts/validate/api/compile_api_intent.py \
  --module training \
  --apply
```

**O que faz**: Transforma DSL simples em OpenAPI verboso + valida contra políticas.

#### 2. Compilador de Política (enforcement de regras)

```powershell
# Valida contrato contra api_rules.yaml
python scripts/contracts/validate/api/compile_api_policy.py \
  --module training \
  --surface sync

# Verificar drift nos artefatos gerados
python scripts/contracts/validate/api/compile_api_policy.py \
  --all \
  --check
```

**Enforcements**:
- ✓ camelCase obrigatório em campos JSON
- ✓ Semantic IDs (`x-semantic-id`) em todos os campos
- ✓ UUID-v4: sufixo `Id` (não `Uuid`)
- ✓ Compatibilidade entre módulos via ARCHITECTURE_MATRIX.yaml

**Artefatos gerados**: `generated/manifests/<module>_<surface>_manifest.json`

### Fluxo Típico de Trabalho

```mermaid
1. Escrever intent → 2. Compilar → 3. Validar gates → 4. Gerar cliente
```

**Passo a passo**:

1. **Criar/editar intenção**:
   ```yaml
   # contracts/openapi/intents/training.intent.yaml
   hbtrack_api_intent:
     module: training
     endpoints:
       - path: /training/sessions
         method: post
         semantic_id: CREATE_TRAINING_SESSION
   ```

2. **Compilar intenção**:
   ```powershell
   python scripts/contracts/validate/api/compile_api_intent.py --module training --apply
   ```
   → Gera: `contracts/openapi/paths/training.yaml`  
   → Gera: `generated/manifests/training_sync_manifest.json`

3. **Validar gates**:
   ```powershell
   python scripts/contracts/validate/validate_contracts.py
   ```
   → Executa Spectral, oasdiff, Redocly

4. **Gerar cliente TypeScript** (após PASS)

### Quando Usar Cada Script

| Cenário | Script |
|---------|--------|
| Novo módulo criado | `gen_module_docs_minimum.py` |
| Definir novos endpoints | `compile_api_intent.py` |
| Validar conformidade de contrato | `compile_api_policy.py --check` |
| Executar todos os gates | `validate_contracts.py` |
| Atualizar baseline do OpenAPI | `gen_openapi_baseline.py` |

---
