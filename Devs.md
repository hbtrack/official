# GUIA DE DESENVOLVIMENTO - HB TRACK

Este documento é um guia prático para os devs do HB Track.

* Objetivos: 
   - Fornecer um manual de referência rápida.
   - Documentar as ferramentas e processos do desenvolvimento.
   - Lembrar os devs sobre o uso correto das ferramentas e processos.
   - Evitar erros comuns e tirar dúvidas frequentes.

"In God we trust; all others must bring data." — W. Edwards Deming

## Inicio 

**PASSO 0**: Validação de Contratos — Bootstrap de Sanidade
`scripts/contracts/validate/bootstrap_contract_tools.py`

* Objetivo: 
   - Garantir que todas as ferramentas de validação de contratos estejam instaladas e configuradas corretamente antes de executar qualquer gate de validação.

Comanndo:

```powershell
python scripts/contracts/validate/validate_contracts.py
```



### Ferramentas Necessárias

| Ferramenta | Propósito | Instalação |
|------------|-----------|------------|
| **Node.js** | Runtime para Redocly/Spectral | https://nodejs.org/ |
| **npm** | Package manager | Incluído com Node.js |
| **Go** | Runtime para oasdiff | https://go.dev/dl/ |
| **Redocly CLI** | Validação estrutural OpenAPI | `npm install -g @redocly/cli` |
| **Spectral CLI** | Linting de políticas OpenAPI | `npm install -g @stoplight/spectral-cli` |
| **oasdiff** | Detecção de breaking changes | `go install github.com/oasdiff/oasdiff@latest` |

### Bootstrap Automático

Antes de validar contratos, **sempre execute o bootstrap**:

```powershell
# Verifica e instala ferramentas ausentes
python scripts/contracts/validate/bootstrap_contract_tools.py --auto-install

# Apenas verifica (sem instalação)
python scripts/contracts/validate/bootstrap_contract_tools.py

# Output JSON apenas
python scripts/contracts/validate/bootstrap_contract_tools.py --json
```

**Exit Codes**:
- `0`: ✓ Todas as ferramentas disponíveis — sistema pronto
- `1`: ⚠ Ferramentas ausentes (instalação possível)
- `2`: ⚠ Instalação automática falhou
- `3`: ✗ Node.js/npm ausentes (instalação manual necessária)

**Relatório**: `_reports/contract_gates/bootstrap.json`

### Validação de Contratos

Após o bootstrap bem-sucedido, execute a validação completa:

```powershell
# Windows (adiciona GOPATH/bin ao PATH)
$env:PATH += ";C:\Users\$env:USERNAME\go\bin"
python scripts/contracts/validate/validate_contracts.py
```

**Relatório**: `_reports/contract_gates/latest.json`

### Scripts Auxiliares (Opcionais)

Para desenvolvimento local, existem scripts shell alternativos em `scripts/contract_gates/`:

```powershell
# Configura PATH automaticamente (node_modules/.bin, GOPATH/bin)
. scripts/contract_gates/env.ps1

# Verifica todas as ferramentas
.\scripts\contract_gates\verify_tools.ps1

# Instala apenas oasdiff
.\scripts\contract_gates\provision_oasdiff.ps1
```

**Diferença vs Bootstrap Python**:
- Scripts shell: rápidos para uso manual local, verificação fragmentada
- Bootstrap Python: automático, gera JSON, ideal para CI/CD

**Recomendação**: Use bootstrap Python em pipelines; scripts shell para troubleshooting local.

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
      - name: Bootstrap Contract Tools
        run: |
          python scripts/contracts/validate/bootstrap_contract_tools.py --auto-install
        continue-on-error: false
      
      - name: Validate Contracts
        run: |
          python scripts/contracts/validate/validate_contracts.py
        continue-on-error: false
      
      - name: Upload Evidence
        uses: actions/upload-artifact@v3
        with:
          name: contract-gates-report
          path: _reports/contract_gates/
```

### Troubleshooting

#### Problema: "npm não encontrado" mesmo com Node.js instalado

**Solução**: O Python subprocess pode não herdar o PATH completo. O bootstrap agora usa `shell=True` no Windows para resolver isso.

#### Problema: "oasdiff não encontrado" mesmo após instalação

**Solução**: Adicione `$GOPATH/bin` ao PATH:

```powershell
# Temporário (sessão atual)
$env:PATH += ";C:\Users\$env:USERNAME\go\bin"

# Permanente (Windows)
[Environment]::SetEnvironmentVariable("Path", $env:Path + ";C:\Users\$env:USERNAME\go\bin", "User")
```

#### Problema: Gate OPENAPI_POLICY_RULESET_GATE falha

**Solução**: Execute Spectral manualmente para ver detalhes:

```powershell
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

