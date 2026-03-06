import sys, os
base='Hb Track - Frontend/src/'
c1=open(base+'types/athlete-canonical.ts',encoding='utf-8').read()
c2=open(base+'lib/api/exercises.ts',encoding='utf-8').read()
c3=open(base+'lib/api/trainings.ts',encoding='utf-8').read()
c4=open(base+'components/training/AICoachDraftModal.tsx',encoding='utf-8').read()
p3=os.path.exists(base+'lib/api/training-phase3.ts')
checks=[('id: string',c1,'AC-001 athlete.id'),('scope?: ExerciseScope',c2,'AC-002 scope em ExerciseInput'),('standalone',c3,'AC-003 standalone em TrainingSession'),('justification',c4,'AC-006 justification em AICoachDraftModal')]
failed=[l for t,c,l in checks if t not in c]
failed+=[] if p3 else ['AC-004 training-phase3.ts ausente']
if failed:
    print('FAIL:', failed)
    sys.exit(1)
else:
    print('PASS: AC-001..004+006 verificados (AC-005 requer inspeção manual)')
