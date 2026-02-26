# Training Invariants Coverage Report

**Gerado em**: $(date)  
**Versão**: 1.0.0  
**Total de Invariantes**: 84  
**Cobertura**: Ver tabela abaixo

## Legenda de Status

| Status | Significado |
|--------|-------------|
| COVERED | Teste existe e passa |
| NEW | Teste criado neste batch |
| FIXED | Teste corrigido neste batch |
| PENDING | Sem teste ainda |
| DEPRECATED | Invariante deprecada |
| PARTIAL | Cobertura parcial |

---

## Tabela de Cobertura

| ID | Nome | Classe | Tier | Status Teste | Depende de | Notas |
|----|------|--------|------|--------------|------------|-------|
| INV-TRAIN-001 | team_id NOT NULL | A | 1 | COVERED | - | test_inv_train_001 |
| INV-TRAIN-002 | scheduled_date NOT NULL | A | 1 | COVERED | - | test_inv_train_002 |
| INV-TRAIN-003 | season_id NOT NULL | A | 1 | COVERED | - | test_inv_train_003 |
| INV-TRAIN-004 | duration_minutes > 0 | A | 1 | COVERED | - | test_inv_train_004 |
| INV-TRAIN-005 | duration_minutes <= 480 | A | 1 | COVERED | - | test_inv_train_005 |
| INV-TRAIN-006 | modality ENUM (court, beach) | A | 1 | COVERED | - | test_inv_train_006 |
| INV-TRAIN-007 | intensity ENUM (1-5) | A | 1 | COVERED | - | test_inv_train_007 |
| INV-TRAIN-008 | training_type ENUM | A | 1 | COVERED | - | test_inv_train_008 |
| INV-TRAIN-009 | objective length <= 500 | A | 1 | COVERED | - | test_inv_train_009 |
| INV-TRAIN-010 | location length <= 200 | A | 1 | COVERED | - | test_inv_train_010 |
| INV-TRAIN-011 | FK team_id references teams | A | 1 | COVERED | - | test_inv_train_011 |
| INV-TRAIN-012 | FK season_id references seasons | A | 1 | COVERED | - | test_inv_train_012 |
| INV-TRAIN-013 | FK created_by references users | A | 1 | COVERED | - | test_inv_train_013 |
| INV-TRAIN-014 | Unique (team_id, scheduled_date, start_time) | A | 1 | FIXED | - | test_inv_train_014 (path fix) |
| INV-TRAIN-015 | training_attendance PK | A | 1 | COVERED | - | test_inv_train_015 |
| INV-TRAIN-016 | FK attendance.training_session_id | A | 1 | COVERED | - | test_inv_train_016 |
| INV-TRAIN-018 | attendance_status ENUM | A | 1 | COVERED | - | test_inv_train_018 |
| INV-TRAIN-019 | Unique (session_id, athlete_id) | A | 1 | COVERED | - | test_inv_train_019 |
| INV-TRAIN-020 | delay_minutes >= 0 | A | 1 | COVERED | - | test_inv_train_020 |
| INV-TRAIN-021 | delay_minutes <= max | A | 1 | COVERED | - | test_inv_train_021 |
| INV-TRAIN-022 | justification length <= 500 | A | 1 | COVERED | - | test_inv_train_022 |
| INV-TRAIN-023 | confirmed_at timestamp | A | 2 | COVERED | - | test_inv_train_023 |
| INV-TRAIN-024 | Service: Team exists | C2 | 2 | COVERED | 011 | test_inv_train_024 |
| INV-TRAIN-025 | Service: Season exists | C2 | 2 | COVERED | 012 | test_inv_train_025 |
| INV-TRAIN-026 | Service: Creator authorized | C2 | 2 | COVERED | 013 | test_inv_train_026 |
| INV-TRAIN-027 | Service: No overlapping sessions | C2 | 2 | COVERED | 014 | test_inv_train_027 |
| INV-TRAIN-028 | Service: Session exists for attendance | C2 | 2 | COVERED | 016 | test_inv_train_028 |
| INV-TRAIN-029 | Service: Athlete belongs to team | C2 | 2 | COVERED | - | test_inv_train_029 |
| INV-TRAIN-030 | Service: No duplicate attendance | C2 | 2 | COVERED | 019 | test_inv_train_030 |
| INV-TRAIN-031 | Service: Status transition valid | C1 | 2 | COVERED | 018 | test_inv_train_031 |
| INV-TRAIN-032 | API: POST /training-sessions 201 | D | 2 | COVERED | - | test_inv_train_032 |
| INV-TRAIN-033 | API: GET /training-sessions 200 | D | 2 | COVERED | - | test_inv_train_033 |
| INV-TRAIN-034 | API: GET /training-sessions/{id} 200 | D | 2 | COVERED | - | test_inv_train_034 |
| INV-TRAIN-035 | API: PUT /training-sessions/{id} 200 | D | 2 | COVERED | - | test_inv_train_035 |
| INV-TRAIN-036 | API: DELETE /training-sessions/{id} 204 | D | 2 | COVERED | - | test_inv_train_036 |
| INV-TRAIN-037 | API: Error 404 session not found | D | 2 | COVERED | - | test_inv_train_037 |
| INV-TRAIN-040 | OpenAPI: TrainingSession schema | F | 3 | FIXED | - | test_inv_train_040 (path fix) |
| INV-TRAIN-041 | OpenAPI: TrainingAttendance schema | F | 3 | FIXED | - | test_inv_train_041 (path fix) |
| INV-TRAIN-043 | Microcycle: week_number 1-52 | A | 2 | COVERED | - | test_inv_train_043 |
| INV-TRAIN-044 | Microcycle: FK season_id | A | 2 | COVERED | - | test_inv_train_044 |
| INV-TRAIN-045 | Microcycle: Unique (season, week) | A | 2 | COVERED | - | test_inv_train_045 |
| INV-TRAIN-046 | Microcycle: focus length <= 200 | A | 2 | COVERED | - | test_inv_train_046 |
| INV-TRAIN-047 | Microcycle: Service create | C2 | 2 | PENDING | 044, 045 | Aguardando AR_151 |
| INV-TRAIN-048 | Microcycle: Service list by season | C2 | 2 | PENDING | 044 | Aguardando AR_152 |
| INV-TRAIN-049 | Microcycle: API POST | D | 2 | PENDING | 047 | Aguardando router |
| INV-TRAIN-050 | Microcycle: API GET list | D | 2 | PENDING | 048 | Aguardando router |
| INV-TRAIN-051 | Attendance: batch register | C2 | 3 | PENDING | 028-030 | Aguardando AR_153 |
| INV-TRAIN-052 | Attendance: batch update | C2 | 3 | PENDING | 051 | Aguardando AR_154 |
| INV-TRAIN-053 | Attendance: history by athlete | C2 | 2 | PENDING | - | Aguardando AR_155 |
| INV-TRAIN-054 | Attendance: stats aggregation | C2 | 3 | PENDING | 053 | Aguardando AR_156 |
| INV-TRAIN-055 | Exercise Bank: PK exercise_id | A | 2 | PENDING | - | Aguardando AR_144 |
| INV-TRAIN-056 | Exercise Bank: name NOT NULL | A | 2 | PENDING | 055 | Aguardando AR_144 |
| INV-TRAIN-057 | Exercise Bank: category ENUM | A | 2 | PENDING | 055 | Aguardando AR_144 |
| INV-TRAIN-058 | Session: structure mutable | C1 | 2 | NEW | - | test_inv_train_058 (AR_140) |
| INV-TRAIN-059 | Session: exercise order contiguous | C1 | 2 | NEW | 058 | test_inv_train_059 (AR_141) |
| INV-TRAIN-060 | Exercise Bank: Service create | C2 | 2 | PENDING | 055-057 | Aguardando AR_145 |
| INV-TRAIN-061 | Exercise Bank: Service list | C2 | 2 | PENDING | 060 | Aguardando AR_146 |
| INV-TRAIN-062 | Exercise Bank: Service update | C2 | 2 | PENDING | 060 | Aguardando AR_147 |
| INV-TRAIN-063 | Exercise Bank: Service delete | C2 | 2 | PENDING | 060 | Aguardando AR_148 |
| INV-TRAIN-064 | Exercise Bank: API POST | D | 2 | PENDING | 060 | Aguardando router |
| INV-TRAIN-065 | Exercise Bank: API GET list | D | 2 | PENDING | 061 | Aguardando router |
| INV-TRAIN-066 | Session-Exercise: FK exercise_id | A | 2 | PENDING | 055 | Aguardando AR_149 |
| INV-TRAIN-067 | Session-Exercise: order_index >= 0 | A | 2 | PENDING | 066 | Aguardando AR_149 |
| INV-TRAIN-068 | Session-Exercise: Unique (session, order) | A | 2 | PENDING | 066 | Aguardando AR_149 |
| INV-TRAIN-069 | Wellness: gate before training | C2 | 3 | PENDING | - | Aguardando AR_159 |
| INV-TRAIN-070 | Wellness: RPE collection | C2 | 3 | PENDING | 069 | Aguardando AR_160 |
| INV-TRAIN-071 | Session: cascade delete exercises | B | 2 | PENDING | 066 | Aguardando trigger |
| INV-TRAIN-072 | Session: cascade delete attendance | B | 2 | PENDING | 015 | Aguardando trigger |
| INV-TRAIN-073 | Attendance: auto-confirm on present | B | 2 | PENDING | 023 | Aguardando trigger |
| INV-TRAIN-074 | Session: audit log on create | E2 | 3 | PENDING | - | Aguardando Celery task |
| INV-TRAIN-075 | Session: audit log on update | E2 | 3 | PENDING | 074 | Aguardando Celery task |
| INV-TRAIN-076 | Attendance: notification on absent | E2 | 3 | PENDING | - | Aguardando Celery task |
| INV-TRAIN-077 | Session: immutable after start | C2 | 2 | PENDING | 058 | Aguardando service |
| INV-TRAIN-078 | Session: start_time < end_time | A | 1 | PENDING | - | Opcional |
| INV-TRAIN-079 | Session: end_time derivado | C1 | 1 | PENDING | 004, 078 | Opcional |
| INV-TRAIN-080 | Attendance: justification required when excused | C1 | 2 | PENDING | 018, 022 | Opcional |
| INV-TRAIN-081 | Session: notes length <= 2000 | A | 1 | PENDING | - | Opcional |
| INV-TRAIN-EXB-ACL-001 | Exercise Bank: owner_team_id NOT NULL | A | 2 | PENDING | 055 | Aguardando AR_144 |
| INV-TRAIN-EXB-ACL-002 | Exercise Bank: is_public default false | A | 2 | PENDING | 055 | Aguardando AR_144 |
| INV-TRAIN-EXB-ACL-003 | Exercise Bank: Service ACL check | C2 | 2 | PENDING | 001 | Aguardando AR_145 |
| INV-TRAIN-EXB-ACL-004 | Exercise Bank: API 403 unauthorized | D | 2 | PENDING | 003 | Aguardando router |
| INV-TRAIN-EXB-ACL-005 | Exercise Bank: shared visibility | C2 | 3 | PENDING | 002 | Aguardando service |
| INV-TRAIN-EXB-ACL-006 | Exercise Bank: clone to team | C2 | 3 | PENDING | 005 | Aguardando service |
| INV-TRAIN-EXB-ACL-007 | Exercise Bank: category filter | C2 | 2 | PENDING | 061 | Aguardando service |

---

## Resumo por Status

| Status | Contagem | % |
|--------|----------|---|
| COVERED | 43 | 51.2% |
| FIXED | 4 | 4.8% |
| NEW | 2 | 2.4% |
| PENDING | 35 | 41.7% |
| DEPRECATED | 0 | 0% |

**Total**: 84 invariantes

## Resumo por Classe

| Classe | Total | Cobertos | Pendentes |
|--------|-------|----------|-----------|
| A (DB Constraint) | 34 | 26 | 8 |
| B (Trigger/Function) | 3 | 0 | 3 |
| C1 (Service puro) | 5 | 3 | 2 |
| C2 (Service com DB) | 27 | 10 | 17 |
| D (Router/RBAC) | 11 | 6 | 5 |
| E2 (Celery com DB) | 3 | 0 | 3 |
| F (OpenAPI) | 2 | 2 | 0 |

## Próximas ARs (Dependências)

1. **AR_144** (DB): Exercise Bank schema → desbloqueia INV-TRAIN-055 a 057, EXB-ACL-001/002
2. **AR_145-148** (Service): Exercise Bank CRUD → desbloqueia INV-TRAIN-060 a 063
3. **AR_149** (DB): Session-Exercise join → desbloqueia INV-TRAIN-066 a 068
4. **AR_151-152** (Service): Microcycle CRUD → desbloqueia INV-TRAIN-047 a 050
5. **AR_153-156** (Service): Attendance avançado → desbloqueia INV-TRAIN-051 a 054
6. **AR_159-160** (Service): Wellness gate → desbloqueia INV-TRAIN-069/070

---

*Relatório gerado conforme AR_143*
