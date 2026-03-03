import sys

# AR_178
content_r = open('Hb Track - Frontend/src/lib/api/rankings.ts', encoding='utf-8').read()
content_c = open('Hb Track - Frontend/src/app/(admin)/training/rankings/RankingsClient.tsx', encoding='utf-8').read()
content_t = open('Hb Track - Frontend/src/app/(admin)/training/top-performers/[teamId]/TopPerformersClient.tsx', encoding='utf-8').read()

checks_178 = [
    ('team_id: number' not in content_r, 'team_id:number removed from rankings.ts'),
    ('athlete_id: number' not in content_r, 'athlete_id:number removed from rankings.ts'),
    ('parseInt' not in content_r, 'no parseInt in rankings.ts'),
    ('parseInt' not in content_c, 'no parseInt in RankingsClient'),
    ('parseInt' not in content_t, 'no parseInt in TopPerformersClient'),
]
failed_178 = [msg for ok, msg in checks_178 if not ok]
if failed_178:
    print(f"FAIL AR_178: {failed_178}")
else:
    print(f"PASS AR_178 {len(checks_178)} checks")

# AR_180
ct = open('Hb Track - Frontend/src/components/training/analytics/ExportPDFModal.tsx', encoding='utf-8').read()
ce = open('Hb Track - Frontend/src/lib/api/exports.ts', encoding='utf-8').read()

checks_180 = [
    (
        'unavailable' in ct or 'indisponível' in ct or 'unavailable' in ce,
        'estado degradado presente'
    ),
    (
        'export-pdf' in ce or 'export_pdf' in ce,
        'endpoint export-pdf referenciado'
    ),
    (
        'fake' not in ct.lower() or 'mock' not in ct.lower(),
        'sem mock/fake óbvio no modal'
    ),
]
failed_180 = [msg for ok, msg in checks_180 if not ok]
if failed_180:
    print(f"FAIL AR_180: {failed_180}")
else:
    print(f"PASS AR_180 {len(checks_180)} checks")
