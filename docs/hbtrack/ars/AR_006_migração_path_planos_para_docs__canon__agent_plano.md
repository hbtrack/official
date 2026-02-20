# AR_006 — Migração path planos para docs/_canon/_agent/planos + v1.0.5

**Status**: COMPLETED ✅
**Versão do Protocolo**: 1.0.5
**Plano Fonte**: `docs/_canon/planos/AR_GOV_001_plans_path_migration.json`

## Descrição
CONTEXTO: Os planos JSON do Arquiteto estão armazenados em docs/_canon/planos/, mas os contratos (Dev Flow v1.0.4 + Hb CLI Spec v1.0.4) especificavam docs/hbtrack/planos/. Isso causava E_PLAN_PATH ao tentar materializar planos. A localização atual em _canon/planos é CORRETA do ponto de vista de organização lógica (artefatos canônicos de governança dentro de _canon/, separados de artefatos finais auditáveis como ARs/evidence em hbtrack/), portanto a solução é atualizar os contratos e o CLI para refletir a realidade.

MUDANÇAS REALIZADAS:
1. scripts/run/hb.py: PLANS_DIR = 'docs/_canon/planos' (antes: 'docs/hbtrack/planos')
2. scripts/run/hb.py: HB_PROTOCOL_VERSION = '1.0.5' (bump)
3. docs/_canon/contratos/Dev Flow.md: §1 versão → v1.0.5; §2.2 path planos; §4 plano path; §5 comandos exemplo
4. docs/_canon/specs/Hb cli.md: §2 PLANS_DIR; §5 assinatura hb plan

REGRADO-UP: Esta AR documenta a mudança de governança conforme exigido pelo próprio Dev Flow Contract §1 (mudança em docs/_canon/contratos/** ou docs/_canon/specs/** MUST ser via AR + bump).

IMPACTO: Planos existentes em docs/_canon/planos/ agora são localizáveis pelo hb plan. Exemplo de comando válido após essa mudança: hb plan docs/_canon/planos/matchservice.json.

## Critérios de Aceite
1) hb version retorna 'HB Track Protocol v1.0.5'. 2) hb plan docs/_canon/planos/matchservice.json executa sem E_PLAN_PATH (localiza o arquivo corretamente). 3) Dev Flow Contract §1 reporta v1.0.5. 4) Hb CLI Spec §2 reporta PLANS_DIR = docs/_canon/planos. 5) PLANS_DIR em hb.py == 'docs/_canon/planos'. 6) Esta AR (006) está em docs/hbtrack/ars/ e possui evidence pack com Exit Code: 0.

## Validation Command (Contrato)
```
python scripts/run/hb.py version && python scripts/run/hb.py plan docs/_canon/planos/matchservice.json
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_006_gov_plans_path_migration.log`

## Riscos
- Planos JSON antigos com version: '1.0.4' falharão com E_PLAN_VERSION_MISMATCH — devem ser atualizados manualmente para '1.0.5'.
- Referências hard-coded a docs/hbtrack/planos/ em scripts auxiliares ou documentação externa precisam ser auditadas e corrigidas.
- Mudanças em docs/_canon/contratos/Dev Flow.md §1,§2.2,§4,§5 (path + bump v1.0.5).
- Mudanças em docs/_canon/specs/Hb cli.md Header,§1,§2,§5 (path + bump v1.0.5).
- Mudanças em scripts/run/hb.py PLANS_DIR e HB_PROTOCOL_VERSION (implementação já feita).

## Análise de Impacto

| Componente | Tipo de Mudança | Nível de Risco | Reversibilidade |
|------------|----------------|----------------|-----------------|
| `scripts/run/hb.py` | Atualização de constantes (PLANS_DIR, HB_PROTOCOL_VERSION) | BAIXO | Alta (revert commit) |
| `docs/_canon/contratos/Dev Flow.md` | Bump de versão + correção de path canônico | BAIXO | Alta (revert commit) |
| `docs/_canon/specs/Hb cli.md` | Bump de versão + correção de path canônico | BAIXO | Alta (revert commit) |
| Planos JSON existentes | Requer update manual de version: "1.0.4" → "1.0.5" | MÉDIO | Alta (bulk edit) |
| PowerShell alias `hb` | Atualização de path do script | BAIXO | Alta (revert profile) |

### Mudanças em Banco de Dados
Nenhuma.

### Mudanças em API
Nenhuma.

### Mudanças em IHM (Frontend)
Nenhuma.

### Dependências Externas
- Planos JSON em `docs/_canon/planos/` com version: "1.0.4" precisam ser atualizados para "1.0.5".
  - Identificados: `matchservice.json`, `scout_implementation.json`, `ar_002_5_schema_conformidade_prd.json`

### Rollback
```bash
git revert <commit_hash_006>
```

---
## Carimbo de Execução

**Status**: ✅ SUCESSO (Exit Code: 0)  
**Data**: 2026-02-19  
**Executor**: HB Track CLI v1.0.5  
**Validation Command**:
```
python scripts/run/hb.py version && python scripts/run/hb.py plan docs/_canon/planos/matchservice.json
```

**Evidence Pack**: [AR_006_gov_plans_path_migration.log](../evidence/AR_006_gov_plans_path_migration.log)

**Resultado**:
- [x] hb version retorna 'HB Track Protocol v1.0.5' ✅
- [x] hb plan docs/_canon/planos/matchservice.json materializa ARs com sucesso ✅
- [x] Dev Flow Contract §1 versão v1.0.5 ✅
- [x] Hb CLI Spec §2 PLANS_DIR = docs/_canon/planos ✅
- [x] PLANS_DIR em hb.py atualizado ✅
- [x] Evidence pack gerado com Exit Code: 0 ✅

**Observações**:
- Planos JSON atualizados para version "1.0.5": matchservice.json, scout_implementation.json, ar_002_5_schema_conformidade_prd.json
- Correção de encoding UTF-8 aplicada em hb.py (sys.stdout.reconfigure) para suportar emojis no Windows
- Path correto confirmado: docs/_canon/planos/ (não docs/_canon/_agent/planos/)
