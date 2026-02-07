Plano completo para o Agent (Copilot Chat no VS Code) seguir, sem Git, para criar testes “válidos” de invariantes e reduzir alucinação por meio de um gate mecânico (verificador + pytest). Este plano assume sua estrutura local:

* `C:\HB TRACK\Hb Track - Backend\...`
* `C:\HB TRACK\Hb Track - Fronted\...`

Foco: Backend.

---

### 0) Pré-condições operacionais (obrigatório antes de qualquer edição)

0.1. No VS Code, garantir que o Copilot está em **Agent mode** e que o terminal padrão é **PowerShell**.

0.2. O Agent deve operar sempre com `cwd` em:
`C:\HB TRACK\Hb Track - Backend`

0.3. Regras de segurança do fluxo (hard rules):

* Não executar comandos destrutivos (`Remove-Item`, `rd`, `del`) sem **PENDING: autorização**.
* Não “hackear o oráculo” (inventar SQLSTATE, constraint_name, mensagens, etc.).
* Não editar código de app/migrations/schema durante criação de testes. (Somente testes e, se necessário e autorizado, o verificador/canon).

Deliverable: o Agent escreve no chat:

* `cwd` atual
* comando que usará para ativar venv (se existir)
* confirmação dessas regras

---

### 1) Inventário canônico (provar quais são os 3 arquivos e o que dizem)

1.1. O Agent deve listar e abrir os **3 arquivos canônicos do módulo training** (no workspace) e colar trechos (sem resumir) contendo:

* definição das classes (A/B/C1/C2/D/E/F ou equivalente)
* definição do que é “OBRIGAÇÃO A” e “OBRIGAÇÃO B”
* qualquer regra sobre SQLSTATE/constraints

Se um deles for “verify.md” (ou similar), ele precisa colar especificamente o trecho que descreve:

* como o verificador decide PASS/FAIL
* o que ele exige em `OBRIGAÇÃO B`

Deliverable: no chat, “Arquivo X → trecho Y” com linhas e path.


---

### 2) Diagnóstico do verificador real (sem conjetura)

2.1. O Agent deve identificar qual é o comando correto do gate canônico. Ele precisa conferir:

* Existe `docs/scripts/verify_invariants_tests.py`? (path exato)
* Ele tem `--help`? Rodar:
  `python docs\scripts\verify_invariants_tests.py --help`
* Se não houver help, abrir o arquivo e localizar “main/argparse” e colar os parâmetros aceitos.

2.2. Rodar o verificador canônico e salvar output bruto em arquivo local (sem Git):

* Exemplo (PowerShell):
  `python docs\scripts\verify_invariants_tests.py 2>&1 | Tee-Object -FilePath docs\_generated\verify_last.txt`
* Depois colar:
  `$LASTEXITCODE`

2.3. Filtrar no output apenas INV-TRAIN-002 (ou a INV em foco):

* `Select-String -Path docs\_generated\verify_last.txt -Pattern "INV-TRAIN-002"`

Deliverable: o Agent cola:

* o comando exato executado
* o output (ou o trecho filtrado)
* `$LASTEXITCODE`

---

### 3) Alinhar CANON ↔ Verificador ↔ SPEC (somente se houver desalinhamento)

Este passo é crítico: no seu histórico, o Agent trocou de script (`verify_canonical_data.py`) e também houve risco de o verificador exigir SQLSTATE em C2. Então aqui a regra é:

* Se o SPEC da INV for C2 (service + DB) com oráculo `ValidationError`, então **não pode existir exigência de SQLSTATE** para passar.

3.1. O Agent deve abrir o SPEC da INV (ex.: INV-TRAIN-002) em `INVARIANTS_TRAINING.md` e colar o bloco onde aparecem:

* classe
* oráculo esperado (ValidationError etc.)
* âncoras de código (arquivo/símbolo/linhas)
* caminho do teste (tests.primary)

Deliverable: trecho do SPEC colado.

3.2. Se o verificador exigir SQLSTATE para a INV C2:

* O Agent deve parar com:
  `PENDING: verificador em desacordo com o SPEC`
* E propor um patch mínimo (apenas proposta, não aplicar) dizendo:

  * “SQLSTATE obrigatório apenas para classes DB (A/B)”
  * “Para C2, OBRIGAÇÃO B deve validar error_type + anchors, sem SQLSTATE”

3.3. Só se você autorizar, o Agent executa patch mínimo no verificador:

* Condicionar a validação SQLSTATE/constraint à classe efetiva da INV (derivada do SPEC).
* Para C2, validar presença de `error_type: ValidationError` (ou campo equivalente) e anchors.

Deliverable: antes de aplicar, o Agent deve colar “diff lógico” (quais funções, quais condições). Depois de aplicar, deve salvar:

* `docs/_generated/verify_patch_notes.txt` com a explicação do patch

---

### 4) Padronizar o “Gate Runner” local (sem Git, com logs e hashes)

Para impedir o Agent de “trocar comando” novamente e para criar rastreabilidade sem Git, crie um runner único.

4.1. Criar:
`C:\HB TRACK\Hb Track - Backend\scripts\run_invariant_gate.ps1`

Comportamento:

1. Recebe `INV-ID` (ex.: `INV-TRAIN-002`)
2. Roda o verificador canônico correto e salva output:

   * `docs/_generated/_reports/<INV-ID>/verify.txt`
   * imprime exit code
3. Roda pytest no arquivo/node do teste e salva output:

   * `docs/_generated/_reports/<INV-ID>/pytest.txt`
   * imprime exit code
4. Calcula hash dos arquivos de teste relevantes:

   * `Get-FileHash tests\...conftest.py`
   * `Get-FileHash tests\...test_inv_...py`
     salva em `hashes.txt`

4.2. Regra do Agent a partir daqui:

* Ele só pode declarar “PASSOU” se existir a pasta de report com verify.txt + pytest.txt + hashes.txt, e se os exit codes forem 0.

Deliverable: o Agent cria o arquivo do runner e executa:
`pwsh -File scripts\run_invariant_gate.ps1 INV-TRAIN-002`
e cola os exit codes.

---

### 5) Implementar/ajustar a INV (modelo operacional por invariante)

Este é o loop padrão que o Agent deve repetir para cada INV.

5.1. Recon (antes de editar qualquer arquivo):
A) Colar SPEC da INV (classe/oráculo/anchors/test path)
B) Colar trecho do schema que define payload mínimo (FKs/NOT NULL/enums)
C) Identificar fixtures existentes:

* procurar `tests/**/conftest.py` relevantes
* plano de `pytest_plugins` (primeiro) e fallback (copiar somente o mínimo)

5.2. Implementação (mudanças permitidas):

* criar/ajustar `tests/training/invariants/conftest.py` para reuso via `pytest_plugins` (primeira tentativa)
* se falhar import, copiar apenas fixtures mínimas necessárias (mantendo mesma lógica)
* ajustar o teste para usar fixtures reais (sem bypass de permissão)

5.3. Gate:

* rodar `scripts\run_invariant_gate.ps1 <INV-ID>`
* se verify falhar: corrigir docstring/obrigações/anchors conforme canon
* se pytest falhar: corrigir setup respeitando schema e permissão (sem bypass)

Deliverable: reports salvos em `_reports/<INV-ID>/...`.

---

### 6) Transformar INV-TRAIN-002 em “Golden” (provar que o modelo bate com o sistema)

6.1. Rodar o gate runner e obter PASS (exit code 0/0).

6.2. Congelar como golden (sem Git):

* manter o report `_reports/INV-TRAIN-002/`
* manter hashes.txt
* opcional: criar `docs/_generated/_reports/INV-TRAIN-002/README.txt` com:

  * classe
  * oráculo
  * comandos usados
  * data/hora

Deliverable: pasta golden completa.

---

### 7) Validar o verificador com “mutation tests” (prova objetiva de que ele pega violações)

Como você quer saber se “o script valida corretamente”, você precisa provar que ele falha quando deve.

7.1. Backup local do golden (sem Git):

* copiar o teste para `.bak` dentro da mesma pasta:

  * `Copy-Item test_inv_...py test_inv_...py.bak`

7.2. Mutação 1 (quebrar o padrão sem mexer na lógica):

* remover “OBRIGAÇÃO A” do docstring
* rodar gate (ou só verify) e esperar FAIL no verify

7.3. Restaurar do `.bak` e repetir Mutação 2:

* remover “OBRIGAÇÃO B” → verify deve falhar

7.4. Mutação 3:

* alterar classe declarada no docstring (C2→C1) mantendo a lógica → verify deve falhar por mismatch com SPEC

Deliverable:

* `docs/_generated/_reports/verifier_mutations_INV-TRAIN-002.txt` contendo:

  * qual mutação
  * comando
  * exit code
  * trecho da falha

Se alguma mutação não for detectada, isso é evidência de lacuna no verificador (e aí você decide endurecer o script).

---

### 8) Escalar para outras invariantes (por classes)

8.1. Escolher 1 INV por classe (A, C2, D, etc.) e repetir o loop:

* recon → implementação → gate → golden → mutation

8.2. Só depois que você tiver pelo menos 1 golden por classe é que você pode dizer:

* “os modelos estão corretos para o meu sistema” (porque são validados por execução real)
* “o verificador está correto” (porque rejeita mutações controladas)

---

### 9) Regras finais que o Agent deve obedecer sempre

* Nunca substituir o comando do verificador por outro “parecido”.
* Nunca declarar PASS sem reports + exit codes.
* Nunca “simplificar” removendo permissões/validações.
* Sempre resolver setup via fixtures reutilizáveis (pytest_plugins → fallback mínimo).

----

### Depois que o verificador parar de exigir SQLSTATE

Aí sim vem o próximo passo:

**Passo 3.10 — Rodar pytest do backend e confirmar que C2 está ok**

* `cd C:\HB TRACK\Hb Track - Backend`
* `python -m pytest -q tests\training\invariants\test_inv_train_002_wellness_pre_deadline.py`
* `Write-Host "EXIT=$LASTEXITCODE"`

### Observação: o patch do verificador (OBLIG_B_NO_ERROR_TYPE)

Ele ainda é útil, mas só vai fazer sentido quando INV-TRAIN-002 ficar com `primary_classes=["C2"]`. Aí você garante que Obrigação B para C2 inclui `ValidationError` (ou o error_type definido no SPEC).

---
