# AR_151 — Service: training_microcycle_service.py — meso date containment

**Status**: 🔲 PENDENTE
**Versão do Protocolo**: 1.3.0

## Descrição
Adicionar guard ao training_cycle_service.py e/ou training_microcycle_service.py para INV-056:

1. INV-056 (micro contido no meso): Ao criar/atualizar microcycle com cycle_id preenchido, validar que:
   - microcycle.week_start >= meso.start_date
   - microcycle.week_end <= meso.end_date
   Se violado, levantar MicrocycleOutsideMesoError.

2. INV-055 (meso overlap documentado): NÃO adicionar constraint de non-overlap entre mesociclos. Garantir que a ausência de constraint é intencional. Adicionar comentário inline no service que overlap entre mesos de EQUIPES DIFERENTES é permitido por design (INV-055).

## Critérios de Aceite
1. create_microcycle() com cycle_id e datas dentro do meso passa. 2. create_microcycle() com cycle_id e datas FORA do meso levanta MicrocycleOutsideMesoError. 3. create_microcycle() sem cycle_id (standalone micro) passa sem validação de datas contra meso.

## Write Scope
- Hb Track - Backend/app/services/training_cycle_service.py

## Validation Command (Contrato)
```
python -c "from pathlib import Path; f=Path('Hb Track - Backend/app/services/training_cycle_service.py'); assert f.exists(), 'FAIL: training_cycle_service.py nao encontrado'; c=f.read_text(encoding='utf-8'); assert 'meso' in c.lower() or 'cycle' in c.lower(), 'FAIL: logica de ciclo/meso ausente'; assert 'overlap' in c.lower() or 'meso_start' in c.lower() or 'start_date' in c.lower(), 'FAIL: guard de overlap ausente'; print('PASS AR_151: training_cycle_service.py com meso+overlap OK')"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_151/executor_main.log`

## Notas do Arquiteto
Classe C2 (Service com DB). O Executor DEVE verificar se training_microcycle_service.py é separado de training_cycle_service.py. Se microciclos são gerenciados pelo mesmo service, adaptar. Depende de Task 149 apenas para testes — a lógica de containment não depende do schema change de standalone.

## Riscos
- training_microcycles.cycle_id é nullable — se cycle_id é NULL, não validar containment (standalone micro é válido per INV-054 lógica similar)

## Análise de Impacto
_(A ser preenchido pelo Executor)_

---
## Carimbo de Execução
_(Gerado por hb report)_

