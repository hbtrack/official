import pathlib, psycopg2
p=list(pathlib.Path('Hb Track - Backend/db/alembic/versions').glob('0055_*.py'))
assert p, 'FAIL: 0055 not found'
c=p[0].read_text(encoding='utf-8')
assert 'revision' in c and '"0055"' in c, 'FAIL: revision 0055 not found'
assert 'down_revision' in c and '"0054"' in c, 'FAIL: down_revision 0054 not found'
conn=psycopg2.connect('postgresql://hbtrack_dev:hbtrack_dev_pwd@localhost:5433/hb_track_dev')
cur=conn.cursor()
cur.execute("SELECT count(*) FROM information_schema.columns WHERE table_name IN ('match_events','competition_matches','competition_opponent_teams','competition_phases','match_roster') AND column_name='deleted_at'")
cols=cur.fetchone()[0]
assert cols==5, f'FAIL: expected 5 cols, got {cols}'
cur.execute("SELECT count(*) FROM information_schema.triggers WHERE trigger_name LIKE '%block_delete%'")
trigs=cur.fetchone()[0]
assert trigs>=24, f'FAIL: expected >=24 triggers, got {trigs}'
cur.execute("SELECT version_num FROM alembic_version")
head=cur.fetchone()[0]
conn.close()
print(f'PASS: 0055 verified on head {head} — {cols} cols, {trigs} triggers')
