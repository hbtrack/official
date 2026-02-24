# AR_111 — Adicionar limpeza automática de carimbos antigos em cmd_verify (antes de append)

**Status**: 🏗️ EM_EXECUCAO
**Versão do Protocolo**: 1.3.0

## Descrição
Em scripts/run/hb_cli.py, função cmd_verify (linha ~1298), ANTES do append do novo carimbo do Testador (linha ~1487: 'ar_updated = ar_updated + stamp'), adicionar lógica de limpeza: (1) Remover todos os carimbos anteriores do Testador via regex substitution: 'ar_updated = re.sub(r"### Verificacao Testador em [a-f0-9]{7}.*?(?=(###|\Z))", "", ar_updated, flags=re.DOTALL)' (remove carimbos até próximo '###' ou fim do arquivo), (2) Strip whitespace excessivo após remoção: 'ar_updated = re.sub(r"\n{3,}", "\n\n", ar_updated)' (normaliza múltiplos linebreaks para no máximo 2), (3) Comentário inline antes da lógica: '# Remover carimbos anteriores do Testador (idempotência: cada verify sobrescreve histórico)'. Lógica executa dentro do bloco 'with HBLock()' para atomicidade. Não modificar a construção de 'stamp' nem lógica de finalize_verification().

## Critérios de Aceite
- Regex remove todos os carimbos anteriores do Testador (padrão '### Verificacao Testador em <hash>')
- Remoção usa re.DOTALL para capturar multi-line content até próximo '###' ou fim
- Normalização de linebreaks evita whitespace excessivo (max 2 newlines consecutivos)
- Lógica executa ANTES do append do novo stamp (dentro de HBLock)
- Comentário inline explica idempotência (cada verify sobrescreve histórico)
- NÃO remove outros carimbos (Executor, Selo Humano) — apenas Testador
- Código testável: re.sub com pattern correto (não quebra outros markdown headers '###')

## Write Scope
- scripts/run/hb_cli.py

## Validation Command (Contrato)
```
python temp/validate_ar111.py
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_111/executor_main.log`

## Rollback Plan (Contrato)
```
git checkout -- scripts/run/hb_cli.py
```
⚠️ **ATENÇÃO**: Este AR modifica banco. Execute rollback em caso de falha.

## Notas do Arquiteto
Limpeza automática: cada verify sobrescreve histórico (não acumula carimbos). Pattern re.DOTALL garante captura multi-line do carimbo completo. Previne acúmulo infinito de carimbos em ARs re-executadas.

## Análise de Impacto
**Escopo**: Modificar a função `cmd_verify` em `scripts/run/hb_cli.py`.

**Impacto**:
- Antes de adicionar um novo "Carimbo de Verificação" do Testador, uma nova lógica removerá todos os carimbos de verificação anteriores.
- A remoção é feita com uma expressão regular que localiza e apaga a seção inteira do carimbo, garantindo que o histórico não seja acumulado.
- Um passo de normalização de espaços em branco garantirá que a formatação do arquivo da AR permaneça limpa após a remoção.
- Essa mudança torna o processo de verificação idempotente, onde cada execução de `hb verify` substitui completamente o resultado anterior.

**Risco**: Baixo. A lógica de remoção é bem contida e atua somente antes da adição do novo carimbo, dentro de um bloco atômico (`HBLock`). O padrão regex é específico para carimbos do Testador, não afetando outros tipos de carimbo.

**Implementação**: Inserir o bloco de código com a lógica de limpeza e normalização na função `cmd_verify`, imediatamente antes da linha `ar_updated = ar_updated + stamp`.

---
## Carimbo de Execução
_(Gerado por hb report)_


### Execução Executor em 8608b0a
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python temp/validate_ar111.py`
**Exit Code**: 0
**Timestamp UTC**: 2026-02-24T17:59:38.180807+00:00
**Behavior Hash**: 22908d4d66771adf4298ed6ea97acf740e844e5cb6a07eac118c9188561699fe
**Evidence File**: `docs/hbtrack/evidence/AR_111/executor_main.log`
**Python Version**: 3.11.9

