<!-- STATUS: NEEDS_REVIEW -->

## RBAC Matrix (papel x domínios/rotas)

Observação: superadmin é bypass (fora da tabela roles) e ignora checks de papel, mas não deve ver /statistics/me.

### Papéis
- dirigente
- coordenador
- treinador
- atleta
- superadmin (bypass)

### Treinos
- /training-cycles*, /training-microcycles*, /training-sessions* (CRUD/close)
  - dirigente: create/read/update/delete/close
  - coordenador: create/read/update/close
  - treinador: create/read/update/close
  - atleta: read quando aplicável; nunca escreve
  - superadmin: bypass

### Statistics
- /statistics (operacional), /statistics/teams, /statistics/athletes, /statistics/snapshots/{scope}/{id}
  - dirigente: read (agregado, sem sessão individual)
  - coordenador: read (agregado, sem sessão individual)
  - treinador: read (equipe)
  - atleta: apenas /statistics/me
  - superadmin: read, exceto /statistics/me por padrão

### Reports
- /reports (create/read/finalize/lock), /reports/operational-session, /reports/athlete-self
  - dirigente: finalize/lock, read
  - coordenador: read (conforme escopo)
  - treinador: create/edit (draft), finalize (se permitido), read
  - atleta: n/a
  - superadmin: bypass

### Auth/Media
- /auth/login|refresh|logout, /media/cloudinary/sign
  - Todos autenticados conforme fluxo; sign exige permissão de media e contexto (person_id quando aplicável).

### Matches/Wellness/Alerts (resumo)
- Matches (/matches, roster, attendance, events): coordenador/treinador; atleta read/próprio quando aplicável.
- Wellness (/wellness_pre, /wellness_post): atleta (self), staff lê; unicidade atleta+sessão.
- Alerts (/alerts): staff (dirigente/coordenador/treinador); atleta não vê.

Nota: respeitar escopo de organização/time/temporada derivado de memberships. Filtrar por team_id/season_id obrigatórios onde aplicável.
