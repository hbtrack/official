# ADR-004 — API Policy Compiler como autoridade executável

Data: 2026-03-12  
Status: ACCEPTED

## Contexto

O HB Track opera em **contract-driven strict mode**: o agente não pode inferir convenções críticas nem “preencher lacunas”.

Para reduzir risco de “soberania invertida” (humano/agente editando YAML técnico e apenas *notariando* o erro), foi introduzido um **compiler determinístico** que:
- valida predicados de convenção (style veto, sufixos canônicos, bindings semânticos mínimos),
- gera policy resolvida por módulo/surface,
- gera manifestos com hash de rastreabilidade,
- e alimenta o gate de drift de derivados.

## Decisão

1. O comando `python3 scripts/contracts/validate/api/compile_api_policy.py --all` é a forma canônica de:
   - atualizar `generated/resolved_policy/**`,
   - atualizar `generated/contracts/**`,
   - atualizar `generated/manifests/**`.
2. O pipeline de validação considera `generated/` **obrigatório** para enforcement de derivados.
3. O `DERIVED_DRIFT_GATE` recompila o esperado e compara semanticamente com o estado do `generated/`; drift falha em **fail-closed**.

## Consequências

- Alterações em contratos SSOT que afetem `generated/` exigem reexecução do compiler; caso contrário, o gate falha.
- O compiler **não** deve “assinar” erro: se detectar violação de convenção obrigatória, ele falha e não produz manifesto/hash para o artefato inválido.

## Referências

- `.contract_driven/CONTRACT_SYSTEM_RULES.md` (procedimento e tooling)
- `docs/_canon/CI_CONTRACT_GATES.md` (DERIVED_DRIFT_GATE)
- `docs/hbtrack/planos/HB_TRACK_API_EXECUTION_CONTRACT.md` (desenho do execution contract)

