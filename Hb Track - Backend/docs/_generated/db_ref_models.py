C:\HB TRACK\Hb Track - Backend\venv\Lib\site-packages\sqlacodegen\generators.py:880: SAWarning: Cannot correctly sort tables; there are unresolvable cycles between tables "competition_phases, competitions, seasons, teams", which is usually caused by mutually dependent foreign key constraints.  Foreign key constraints involving these tables will not be considered; this warning may raise an error in a future release.
  for table in self.metadata.sorted_tables:
from typing import Any, Optional
import datetime
import decimal
import uuid

from sqlalchemy import ARRAY, Boolean, CheckConstraint, Column, Date, DateTime, ForeignKeyConstraint, Index, Integer, Numeric, PrimaryKeyConstraint, SmallInteger, String, Table, Text, Time, UniqueConstraint, Uuid, text
from sqlalchemy.dialects.postgresql import INET, JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass


class AdvantageStates(Base):
    __tablename__ = 'advantage_states'
    __table_args__ = (
        PrimaryKeyConstraint('code', name='pk_advantage_states'),
    )

    code: Mapped[str] = mapped_column(String(32), primary_key=True)
    delta_players: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(255))

    match_events: Mapped[list['MatchEvents']] = relationship('MatchEvents', back_populates='advantage_states')


class Categories(Base):
    __tablename__ = 'categories'
    __table_args__ = (
        CheckConstraint('max_age > 0', name='ck_categories_max_age_positive'),
        PrimaryKeyConstraint('id', name='pk_categories'),
        UniqueConstraint('name', name='ux_categories_name')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    max_age: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'))

    teams: Mapped[list['Teams']] = relationship('Teams', back_populates='category')


class CompetitionPhases(Base):
    __tablename__ = 'competition_phases'
    __table_args__ = (
        ForeignKeyConstraint(['competition_id'], ['competitions.id'], ondelete='CASCADE', name='fk_competition_phases_competition_id'),
        PrimaryKeyConstraint('id', name='pk_competition_phases'),
        Index('ix_competition_phases_competition_id', 'competition_id'),
        Index('ix_competition_phases_order', 'competition_id', 'order_index')
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    competition_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    phase_type: Mapped[str] = mapped_column(String(50), nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    is_olympic_cross: Mapped[Optional[bool]] = mapped_column(Boolean, server_default=text('false'))
    config: Mapped[Optional[dict]] = mapped_column(JSONB, server_default=text("'{}'::jsonb"))
    status: Mapped[Optional[str]] = mapped_column(String(50), server_default=text("'pending'::character varying"))

    competition: Mapped['Competitions'] = relationship('Competitions', foreign_keys=[competition_id], back_populates='competition_phases')
    competitions: Mapped[list['Competitions']] = relationship('Competitions', foreign_keys='[Competitions.current_phase_id]', back_populates='current_phase')
    competition_standings: Mapped[list['CompetitionStandings']] = relationship('CompetitionStandings', back_populates='phase')
    competition_matches: Mapped[list['CompetitionMatches']] = relationship('CompetitionMatches', back_populates='phase')


class Competitions(Base):
    __tablename__ = 'competitions'
    __table_args__ = (
        CheckConstraint('deleted_at IS NULL AND deleted_reason IS NULL OR deleted_at IS NOT NULL AND deleted_reason IS NOT NULL', name='ck_competitions_deleted_reason'),
        ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL', name='fk_competitions_created_by'),
        ForeignKeyConstraint(['current_phase_id'], ['competition_phases.id'], ondelete='SET NULL', name='fk_competitions_current_phase_id'),
        ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='RESTRICT', name='fk_competitions_organization_id'),
        ForeignKeyConstraint(['team_id'], ['teams.id'], ondelete='SET NULL', name='fk_competitions_team_id'),
        PrimaryKeyConstraint('id', name='pk_competitions'),
        Index('ix_competitions_created_by', 'created_by'),
        Index('ix_competitions_organization_id', 'organization_id'),
        Index('ix_competitions_season', 'season'),
        Index('ix_competitions_status', 'status'),
        Index('ix_competitions_team_id', 'team_id')
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    organization_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    kind: Mapped[Optional[str]] = mapped_column(String(50))
    team_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    season: Mapped[Optional[str]] = mapped_column(String(50))
    modality: Mapped[Optional[str]] = mapped_column(String(50), server_default=text("'masculino'::character varying"))
    competition_type: Mapped[Optional[str]] = mapped_column(String(50))
    format_details: Mapped[Optional[dict]] = mapped_column(JSONB, server_default=text("'{}'::jsonb"))
    tiebreaker_criteria: Mapped[Optional[dict]] = mapped_column(JSONB, server_default=text('\'["pontos", "saldo_gols", "gols_pro", "confronto_direto"]\'::jsonb'))
    points_per_win: Mapped[Optional[int]] = mapped_column(Integer, server_default=text('2'))
    status: Mapped[Optional[str]] = mapped_column(String(50), server_default=text("'draft'::character varying"))
    current_phase_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    regulation_file_url: Mapped[Optional[str]] = mapped_column(String(500))
    regulation_notes: Mapped[Optional[str]] = mapped_column(Text)
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    deleted_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    deleted_reason: Mapped[Optional[str]] = mapped_column(Text)

    competition_phases: Mapped[list['CompetitionPhases']] = relationship('CompetitionPhases', foreign_keys='[CompetitionPhases.competition_id]', back_populates='competition')
    users: Mapped[Optional['Users']] = relationship('Users', back_populates='competitions')
    current_phase: Mapped[Optional['CompetitionPhases']] = relationship('CompetitionPhases', foreign_keys=[current_phase_id], back_populates='competitions')
    organization: Mapped['Organizations'] = relationship('Organizations', back_populates='competitions')
    team: Mapped[Optional['Teams']] = relationship('Teams', back_populates='competitions')
    competition_opponent_teams: Mapped[list['CompetitionOpponentTeams']] = relationship('CompetitionOpponentTeams', back_populates='competition')
    competition_seasons: Mapped[list['CompetitionSeasons']] = relationship('CompetitionSeasons', back_populates='competition')
    competition_standings: Mapped[list['CompetitionStandings']] = relationship('CompetitionStandings', back_populates='competition')
    competition_matches: Mapped[list['CompetitionMatches']] = relationship('CompetitionMatches', back_populates='competition')


class DataRetentionLogs(Base):
    __tablename__ = 'data_retention_logs'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='data_retention_logs_pkey'),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    table_name: Mapped[str] = mapped_column(String(100), nullable=False)
    records_anonymized: Mapped[int] = mapped_column(Integer, nullable=False)
    anonymized_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))


class DefensivePositions(Base):
    __tablename__ = 'defensive_positions'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='pk_defensive_positions'),
        UniqueConstraint('code', name='ux_defensive_positions_code')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(32), nullable=False)
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'))
    abbreviation: Mapped[Optional[str]] = mapped_column(String(10))

    athletes: Mapped[list['Athletes']] = relationship('Athletes', foreign_keys='[Athletes.main_defensive_position_id]', back_populates='main_defensive_position')
    athletes_: Mapped[list['Athletes']] = relationship('Athletes', foreign_keys='[Athletes.secondary_defensive_position_id]', back_populates='secondary_defensive_position')


class EventTypes(Base):
    __tablename__ = 'event_types'
    __table_args__ = (
        PrimaryKeyConstraint('code', name='pk_event_types'),
    )

    code: Mapped[str] = mapped_column(String(64), primary_key=True)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    is_shot: Mapped[bool] = mapped_column(Boolean, nullable=False)
    is_possession_ending: Mapped[bool] = mapped_column(Boolean, nullable=False)

    event_subtypes: Mapped[list['EventSubtypes']] = relationship('EventSubtypes', back_populates='event_types')
    match_events: Mapped[list['MatchEvents']] = relationship('MatchEvents', back_populates='event_types')


class IdempotencyKeys(Base):
    __tablename__ = 'idempotency_keys'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='idempotency_keys_pkey'),
        UniqueConstraint('key', 'endpoint', name='uq_idempotency_key_endpoint'),
        Index('ix_idempotency_keys_created_at', 'created_at'),
        Index('ix_idempotency_keys_key', 'key'),
        Index('ix_idempotency_keys_key_endpoint', 'key', 'endpoint')
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    key: Mapped[str] = mapped_column(String(255), nullable=False)
    endpoint: Mapped[str] = mapped_column(String(255), nullable=False)
    request_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    response_json: Mapped[Optional[dict]] = mapped_column(JSONB)
    status_code: Mapped[Optional[int]] = mapped_column(Integer)


class OffensivePositions(Base):
    __tablename__ = 'offensive_positions'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='pk_offensive_positions'),
        UniqueConstraint('code', name='ux_offensive_positions_code')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(32), nullable=False)
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'))
    abbreviation: Mapped[Optional[str]] = mapped_column(String(10))

    athletes: Mapped[list['Athletes']] = relationship('Athletes', foreign_keys='[Athletes.main_offensive_position_id]', back_populates='main_offensive_position')
    athletes_: Mapped[list['Athletes']] = relationship('Athletes', foreign_keys='[Athletes.secondary_offensive_position_id]', back_populates='secondary_offensive_position')


class Organizations(Base):
    __tablename__ = 'organizations'
    __table_args__ = (
        CheckConstraint('deleted_at IS NULL AND deleted_reason IS NULL OR deleted_at IS NOT NULL AND deleted_reason IS NOT NULL', name='ck_organizations_deleted_reason'),
        PrimaryKeyConstraint('id', name='pk_organizations'),
        Index('ix_organizations_name', 'name'),
        Index('ix_organizations_name_trgm', 'name')
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    deleted_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    deleted_reason: Mapped[Optional[str]] = mapped_column(Text)

    competitions: Mapped[list['Competitions']] = relationship('Competitions', back_populates='organization')
    teams: Mapped[list['Teams']] = relationship('Teams', back_populates='organization')
    athletes: Mapped[list['Athletes']] = relationship('Athletes', back_populates='organization')
    exercises: Mapped[list['Exercises']] = relationship('Exercises', back_populates='organization')
    medical_cases: Mapped[list['MedicalCases']] = relationship('MedicalCases', back_populates='organization')
    org_memberships: Mapped[list['OrgMemberships']] = relationship('OrgMemberships', back_populates='organization')
    training_cycles: Mapped[list['TrainingCycles']] = relationship('TrainingCycles', back_populates='organization')
    session_templates: Mapped[list['SessionTemplates']] = relationship('SessionTemplates', back_populates='org')
    training_microcycles: Mapped[list['TrainingMicrocycles']] = relationship('TrainingMicrocycles', back_populates='organization')
    training_sessions: Mapped[list['TrainingSessions']] = relationship('TrainingSessions', back_populates='organization')
    wellness_post: Mapped[list['WellnessPost']] = relationship('WellnessPost', back_populates='organization')
    wellness_pre: Mapped[list['WellnessPre']] = relationship('WellnessPre', back_populates='organization')


class Permissions(Base):
    __tablename__ = 'permissions'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='pk_permissions'),
        UniqueConstraint('code', name='ux_permissions_code')
    )

    id: Mapped[int] = mapped_column(SmallInteger, primary_key=True)
    code: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    description: Mapped[Optional[str]] = mapped_column(Text)

    role: Mapped[list['Roles']] = relationship('Roles', secondary='role_permissions', back_populates='permission')


class Persons(Base):
    __tablename__ = 'persons'
    __table_args__ = (
        CheckConstraint('deleted_at IS NULL AND deleted_reason IS NULL OR deleted_at IS NOT NULL AND deleted_reason IS NOT NULL', name='ck_persons_deleted_reason'),
        CheckConstraint("gender IS NULL OR (gender::text = ANY (ARRAY['masculino'::character varying, 'feminino'::character varying, 'outro'::character varying, 'prefiro_nao_dizer'::character varying]::text[]))", name='ck_persons_gender'),
        PrimaryKeyConstraint('id', name='pk_persons'),
        Index('ix_persons_birth_date', 'birth_date'),
        Index('ix_persons_deleted_at', 'deleted_at'),
        Index('ix_persons_first_name', 'first_name'),
        Index('ix_persons_first_name_trgm', 'first_name'),
        Index('ix_persons_full_name_trgm', 'full_name'),
        Index('ix_persons_last_name', 'last_name'),
        Index('ix_persons_last_name_trgm', 'last_name')
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    full_name: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    birth_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    deleted_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    deleted_reason: Mapped[Optional[str]] = mapped_column(Text)
    gender: Mapped[Optional[str]] = mapped_column(String(20))
    nationality: Mapped[Optional[str]] = mapped_column(String(100), server_default=text("'brasileira'::character varying"))
    notes: Mapped[Optional[str]] = mapped_column(Text)

    athletes: Mapped[list['Athletes']] = relationship('Athletes', back_populates='person')
    users: Mapped[list['Users']] = relationship('Users', back_populates='person')
    org_memberships: Mapped[list['OrgMemberships']] = relationship('OrgMemberships', back_populates='person')
    person_addresses: Mapped[list['PersonAddresses']] = relationship('PersonAddresses', back_populates='person')
    person_contacts: Mapped[list['PersonContacts']] = relationship('PersonContacts', back_populates='person')
    person_documents: Mapped[list['PersonDocuments']] = relationship('PersonDocuments', back_populates='person')
    person_media: Mapped[list['PersonMedia']] = relationship('PersonMedia', back_populates='person')
    team_memberships: Mapped[list['TeamMemberships']] = relationship('TeamMemberships', back_populates='person')


class PhasesOfPlay(Base):
    __tablename__ = 'phases_of_play'
    __table_args__ = (
        PrimaryKeyConstraint('code', name='pk_phases_of_play'),
    )

    code: Mapped[str] = mapped_column(String(32), primary_key=True)
    description: Mapped[str] = mapped_column(String(255), nullable=False)

    match_events: Mapped[list['MatchEvents']] = relationship('MatchEvents', back_populates='phases_of_play')


class Roles(Base):
    __tablename__ = 'roles'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='pk_roles'),
        UniqueConstraint('code', name='ux_roles_code'),
        UniqueConstraint('name', name='ux_roles_name')
    )

    id: Mapped[int] = mapped_column(SmallInteger, primary_key=True)
    code: Mapped[str] = mapped_column(String(32), nullable=False)
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    description: Mapped[Optional[str]] = mapped_column(Text)

    permission: Mapped[list['Permissions']] = relationship('Permissions', secondary='role_permissions', back_populates='role')
    org_memberships: Mapped[list['OrgMemberships']] = relationship('OrgMemberships', back_populates='role')


class SchoolingLevels(Base):
    __tablename__ = 'schooling_levels'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='pk_schooling_levels'),
        UniqueConstraint('code', name='ux_schooling_levels_code')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(32), nullable=False)
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'))

    athletes: Mapped[list['Athletes']] = relationship('Athletes', back_populates='schooling')


class Seasons(Base):
    __tablename__ = 'seasons'
    __table_args__ = (
        CheckConstraint('deleted_at IS NULL AND deleted_reason IS NULL OR deleted_at IS NOT NULL AND deleted_reason IS NOT NULL', name='ck_seasons_deleted_reason'),
        CheckConstraint('start_date < end_date', name='ck_seasons_dates'),
        ForeignKeyConstraint(['created_by_user_id'], ['users.id'], ondelete='SET NULL', name='fk_seasons_created_by_user_id'),
        ForeignKeyConstraint(['team_id'], ['teams.id'], ondelete='RESTRICT', name='fk_seasons_team_id'),
        PrimaryKeyConstraint('id', name='pk_seasons'),
        Index('ix_seasons_team_id', 'team_id'),
        Index('ix_seasons_year', 'year')
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    team_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    start_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    end_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    competition_type: Mapped[Optional[str]] = mapped_column(String(32))
    canceled_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    interrupted_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    created_by_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    deleted_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    deleted_reason: Mapped[Optional[str]] = mapped_column(Text)

    created_by_user: Mapped[Optional['Users']] = relationship('Users', back_populates='seasons')
    team: Mapped['Teams'] = relationship('Teams', foreign_keys=[team_id], back_populates='seasons')
    teams: Mapped[list['Teams']] = relationship('Teams', foreign_keys='[Teams.season_id]', back_populates='season')
    competition_seasons: Mapped[list['CompetitionSeasons']] = relationship('CompetitionSeasons', back_populates='season')
    matches: Mapped[list['Matches']] = relationship('Matches', back_populates='season')
    training_sessions: Mapped[list['TrainingSessions']] = relationship('TrainingSessions', back_populates='season')


class Teams(Base):
    __tablename__ = 'teams'
    __table_args__ = (
        CheckConstraint('active_from IS NULL OR active_until IS NULL OR active_from <= active_until', name='ck_teams_active_dates'),
        CheckConstraint('alert_threshold_multiplier >= 1.0 AND alert_threshold_multiplier <= 3.0', name='teams_alert_threshold_multiplier_check'),
        CheckConstraint('deleted_at IS NULL AND deleted_reason IS NULL OR deleted_at IS NOT NULL AND deleted_reason IS NOT NULL', name='ck_teams_deleted_reason'),
        CheckConstraint("gender::text = ANY (ARRAY['masculino'::character varying, 'feminino'::character varying]::text[])", name='ck_teams_gender'),
        ForeignKeyConstraint(['category_id'], ['categories.id'], ondelete='RESTRICT', name='fk_teams_category_id'),
        ForeignKeyConstraint(['coach_membership_id'], ['org_memberships.id'], ondelete='SET NULL', name='fk_teams_coach_membership_id'),
        ForeignKeyConstraint(['created_by_membership_id'], ['org_memberships.id'], ondelete='SET NULL', name='fk_teams_created_by_membership_id'),
        ForeignKeyConstraint(['created_by_user_id'], ['users.id'], ondelete='SET NULL', name='fk_teams_created_by_user_id'),
        ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='RESTRICT', name='fk_teams_organization_id'),
        ForeignKeyConstraint(['season_id'], ['seasons.id'], ondelete='RESTRICT', name='fk_teams_season_id'),
        PrimaryKeyConstraint('id', name='pk_teams'),
        Index('ix_teams_category_id', 'category_id'),
        Index('ix_teams_coach_membership_id', 'coach_membership_id'),
        Index('ix_teams_created_by_membership_id', 'created_by_membership_id'),
        Index('ix_teams_name_trgm', 'name'),
        Index('ix_teams_organization_active', 'organization_id'),
        Index('ix_teams_organization_id', 'organization_id'),
        Index('ix_teams_season_id', 'season_id')
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    organization_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    category_id: Mapped[int] = mapped_column(Integer, nullable=False)
    gender: Mapped[str] = mapped_column(String(16), nullable=False)
    is_our_team: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    active_from: Mapped[Optional[datetime.date]] = mapped_column(Date)
    active_until: Mapped[Optional[datetime.date]] = mapped_column(Date)
    created_by_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    deleted_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    deleted_reason: Mapped[Optional[str]] = mapped_column(Text)
    season_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    coach_membership_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    created_by_membership_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    alert_threshold_multiplier: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(3, 1), server_default=text('2.0'))

    competitions: Mapped[list['Competitions']] = relationship('Competitions', back_populates='team')
    seasons: Mapped[list['Seasons']] = relationship('Seasons', foreign_keys='[Seasons.team_id]', back_populates='team')
    category: Mapped['Categories'] = relationship('Categories', back_populates='teams')
    coach_membership: Mapped[Optional['OrgMemberships']] = relationship('OrgMemberships', foreign_keys=[coach_membership_id], back_populates='teams')
    created_by_membership: Mapped[Optional['OrgMemberships']] = relationship('OrgMemberships', foreign_keys=[created_by_membership_id], back_populates='teams_')
    created_by_user: Mapped[Optional['Users']] = relationship('Users', back_populates='teams')
    organization: Mapped['Organizations'] = relationship('Organizations', back_populates='teams')
    season: Mapped[Optional['Seasons']] = relationship('Seasons', foreign_keys=[season_id], back_populates='teams')
    competition_opponent_teams: Mapped[list['CompetitionOpponentTeams']] = relationship('CompetitionOpponentTeams', back_populates='linked_team')
    team_wellness_rankings: Mapped[list['TeamWellnessRankings']] = relationship('TeamWellnessRankings', back_populates='team')
    matches: Mapped[list['Matches']] = relationship('Matches', foreign_keys='[Matches.away_team_id]', back_populates='away_team')
    matches_: Mapped[list['Matches']] = relationship('Matches', foreign_keys='[Matches.home_team_id]', back_populates='home_team')
    matches1: Mapped[list['Matches']] = relationship('Matches', foreign_keys='[Matches.our_team_id]', back_populates='our_team')
    team_registrations: Mapped[list['TeamRegistrations']] = relationship('TeamRegistrations', back_populates='team')
    training_alerts: Mapped[list['TrainingAlerts']] = relationship('TrainingAlerts', back_populates='team')
    training_cycles: Mapped[list['TrainingCycles']] = relationship('TrainingCycles', back_populates='team')
    match_possessions: Mapped[list['MatchPossessions']] = relationship('MatchPossessions', back_populates='team')
    match_roster: Mapped[list['MatchRoster']] = relationship('MatchRoster', back_populates='team')
    match_teams: Mapped[list['MatchTeams']] = relationship('MatchTeams', back_populates='team')
    team_memberships: Mapped[list['TeamMemberships']] = relationship('TeamMemberships', back_populates='team')
    training_microcycles: Mapped[list['TrainingMicrocycles']] = relationship('TrainingMicrocycles', back_populates='team')
    match_events: Mapped[list['MatchEvents']] = relationship('MatchEvents', foreign_keys='[MatchEvents.opponent_team_id]', back_populates='opponent_team')
    match_events_: Mapped[list['MatchEvents']] = relationship('MatchEvents', foreign_keys='[MatchEvents.team_id]', back_populates='team')
    training_analytics_cache: Mapped[list['TrainingAnalyticsCache']] = relationship('TrainingAnalyticsCache', back_populates='team')
    training_sessions: Mapped[list['TrainingSessions']] = relationship('TrainingSessions', back_populates='team')
    training_suggestions: Mapped[list['TrainingSuggestions']] = relationship('TrainingSuggestions', back_populates='team')


t_v_anonymization_status = Table(
    'v_anonymization_status', Base.metadata,
    Column('table_name', Text),
    Column('eligible_count', Numeric),
    Column('oldest_record_date', DateTime(True)),
    Column('newest_eligible_date', DateTime(True)),
    Column('cutoff_date', DateTime(True)),
    Column('last_anonymization_run', DateTime(True)),
    Column('last_run_records', Integer),
    Column('status_severity', Text)
)


class Athletes(Base):
    __tablename__ = 'athletes'
    __table_args__ = (
        CheckConstraint('deleted_at IS NULL AND deleted_reason IS NULL OR deleted_at IS NOT NULL AND deleted_reason IS NOT NULL', name='ck_athletes_deleted_reason'),
        CheckConstraint('shirt_number IS NULL OR shirt_number >= 1 AND shirt_number <= 99', name='ck_athletes_shirt_number'),
        CheckConstraint("state::text = ANY (ARRAY['ativa'::character varying, 'dispensada'::character varying, 'arquivada'::character varying]::text[])", name='ck_athletes_state'),
        ForeignKeyConstraint(['main_defensive_position_id'], ['defensive_positions.id'], ondelete='SET NULL', name='fk_athletes_main_defensive_position_id'),
        ForeignKeyConstraint(['main_offensive_position_id'], ['offensive_positions.id'], ondelete='SET NULL', name='fk_athletes_main_offensive_position_id'),
        ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='RESTRICT', name='fk_athletes_organization_id'),
        ForeignKeyConstraint(['person_id'], ['persons.id'], ondelete='RESTRICT', name='fk_athletes_person_id'),
        ForeignKeyConstraint(['schooling_id'], ['schooling_levels.id'], ondelete='SET NULL', name='fk_athletes_schooling_id'),
        ForeignKeyConstraint(['secondary_defensive_position_id'], ['defensive_positions.id'], ondelete='SET NULL', name='fk_athletes_secondary_defensive_position_id'),
        ForeignKeyConstraint(['secondary_offensive_position_id'], ['offensive_positions.id'], ondelete='SET NULL', name='fk_athletes_secondary_offensive_position_id'),
        PrimaryKeyConstraint('id', name='pk_athletes'),
        Index('idx_athletes_person_deleted', 'person_id', 'deleted_at'),
        Index('ix_athletes_birth_date', 'birth_date'),
        Index('ix_athletes_medical_flags', 'state'),
        Index('ix_athletes_organization_id', 'organization_id'),
        Index('ix_athletes_person_id', 'person_id'),
        Index('ix_athletes_person_id_active', 'person_id'),
        Index('ix_athletes_state', 'state'),
        Index('ix_athletes_state_active', 'state')
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    person_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    state: Mapped[str] = mapped_column(String(20), nullable=False, server_default=text("'ativa'::character varying"))
    injured: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    medical_restriction: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    load_restricted: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    athlete_name: Mapped[str] = mapped_column(String(100), nullable=False)
    birth_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    registered_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    suspended_until: Mapped[Optional[datetime.date]] = mapped_column(Date)
    athlete_nickname: Mapped[Optional[str]] = mapped_column(String(50))
    shirt_number: Mapped[Optional[int]] = mapped_column(Integer)
    main_defensive_position_id: Mapped[Optional[int]] = mapped_column(Integer)
    secondary_defensive_position_id: Mapped[Optional[int]] = mapped_column(Integer)
    main_offensive_position_id: Mapped[Optional[int]] = mapped_column(Integer)
    secondary_offensive_position_id: Mapped[Optional[int]] = mapped_column(Integer)
    schooling_id: Mapped[Optional[int]] = mapped_column(Integer)
    guardian_name: Mapped[Optional[str]] = mapped_column(String(100))
    guardian_phone: Mapped[Optional[str]] = mapped_column(String(20))
    athlete_photo_path: Mapped[Optional[str]] = mapped_column(String(500))
    athlete_age_at_registration: Mapped[Optional[int]] = mapped_column(Integer)
    deleted_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    deleted_reason: Mapped[Optional[str]] = mapped_column(Text)
    organization_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)

    main_defensive_position: Mapped[Optional['DefensivePositions']] = relationship('DefensivePositions', foreign_keys=[main_defensive_position_id], back_populates='athletes')
    main_offensive_position: Mapped[Optional['OffensivePositions']] = relationship('OffensivePositions', foreign_keys=[main_offensive_position_id], back_populates='athletes')
    organization: Mapped[Optional['Organizations']] = relationship('Organizations', back_populates='athletes')
    person: Mapped['Persons'] = relationship('Persons', back_populates='athletes')
    schooling: Mapped[Optional['SchoolingLevels']] = relationship('SchoolingLevels', back_populates='athletes')
    secondary_defensive_position: Mapped[Optional['DefensivePositions']] = relationship('DefensivePositions', foreign_keys=[secondary_defensive_position_id], back_populates='athletes_')
    secondary_offensive_position: Mapped[Optional['OffensivePositions']] = relationship('OffensivePositions', foreign_keys=[secondary_offensive_position_id], back_populates='athletes_')
    athlete_badges: Mapped[list['AthleteBadges']] = relationship('AthleteBadges', back_populates='athlete')
    data_access_logs: Mapped[list['DataAccessLogs']] = relationship('DataAccessLogs', back_populates='athlete')
    medical_cases: Mapped[list['MedicalCases']] = relationship('MedicalCases', back_populates='athlete')
    team_registrations: Mapped[list['TeamRegistrations']] = relationship('TeamRegistrations', back_populates='athlete')
    match_roster: Mapped[list['MatchRoster']] = relationship('MatchRoster', back_populates='athlete')
    match_events: Mapped[list['MatchEvents']] = relationship('MatchEvents', foreign_keys='[MatchEvents.assisting_athlete_id]', back_populates='assisting_athlete')
    match_events_: Mapped[list['MatchEvents']] = relationship('MatchEvents', foreign_keys='[MatchEvents.athlete_id]', back_populates='athlete')
    match_events1: Mapped[list['MatchEvents']] = relationship('MatchEvents', foreign_keys='[MatchEvents.secondary_athlete_id]', back_populates='secondary_athlete')
    attendance: Mapped[list['Attendance']] = relationship('Attendance', back_populates='athlete')
    wellness_post: Mapped[list['WellnessPost']] = relationship('WellnessPost', back_populates='athlete')
    wellness_pre: Mapped[list['WellnessPre']] = relationship('WellnessPre', back_populates='athlete')
    wellness_reminders: Mapped[list['WellnessReminders']] = relationship('WellnessReminders', back_populates='athlete')


class CompetitionOpponentTeams(Base):
    __tablename__ = 'competition_opponent_teams'
    __table_args__ = (
        ForeignKeyConstraint(['competition_id'], ['competitions.id'], ondelete='CASCADE', name='fk_competition_opponent_teams_competition_id'),
        ForeignKeyConstraint(['linked_team_id'], ['teams.id'], ondelete='SET NULL', name='fk_competition_opponent_teams_linked_team_id'),
        PrimaryKeyConstraint('id', name='pk_competition_opponent_teams'),
        Index('ix_competition_opponent_teams_competition_id', 'competition_id'),
        Index('ix_competition_opponent_teams_group', 'competition_id', 'group_name'),
        Index('ix_competition_opponent_teams_linked_team_id', 'linked_team_id')
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    competition_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    short_name: Mapped[Optional[str]] = mapped_column(String(50))
    category: Mapped[Optional[str]] = mapped_column(String(50))
    city: Mapped[Optional[str]] = mapped_column(String(100))
    logo_url: Mapped[Optional[str]] = mapped_column(String(500))
    linked_team_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    group_name: Mapped[Optional[str]] = mapped_column(String(50))
    stats: Mapped[Optional[dict]] = mapped_column(JSONB, server_default=text('\'{"wins": 0, "draws": 0, "losses": 0, "played": 0, "points": 0, "goals_for": 0, "goals_against": 0, "goal_difference": 0}\'::jsonb'))
    status: Mapped[Optional[str]] = mapped_column(String(50), server_default=text("'active'::character varying"))

    competition: Mapped['Competitions'] = relationship('Competitions', back_populates='competition_opponent_teams')
    linked_team: Mapped[Optional['Teams']] = relationship('Teams', back_populates='competition_opponent_teams')
    competition_standings: Mapped[list['CompetitionStandings']] = relationship('CompetitionStandings', back_populates='opponent_team')
    competition_matches: Mapped[list['CompetitionMatches']] = relationship('CompetitionMatches', foreign_keys='[CompetitionMatches.away_team_id]', back_populates='away_team')
    competition_matches_: Mapped[list['CompetitionMatches']] = relationship('CompetitionMatches', foreign_keys='[CompetitionMatches.home_team_id]', back_populates='home_team')


class CompetitionSeasons(Base):
    __tablename__ = 'competition_seasons'
    __table_args__ = (
        ForeignKeyConstraint(['competition_id'], ['competitions.id'], ondelete='CASCADE', name='fk_competition_seasons_competition_id'),
        ForeignKeyConstraint(['season_id'], ['seasons.id'], ondelete='CASCADE', name='fk_competition_seasons_season_id'),
        PrimaryKeyConstraint('id', name='pk_competition_seasons'),
        UniqueConstraint('competition_id', 'season_id', name='uk_competition_seasons_competition_season'),
        Index('ix_competition_seasons_competition_id', 'competition_id'),
        Index('ix_competition_seasons_season_id', 'season_id')
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    competition_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    season_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    name: Mapped[Optional[str]] = mapped_column(String(100))

    competition: Mapped['Competitions'] = relationship('Competitions', back_populates='competition_seasons')
    season: Mapped['Seasons'] = relationship('Seasons', back_populates='competition_seasons')


class EventSubtypes(Base):
    __tablename__ = 'event_subtypes'
    __table_args__ = (
        ForeignKeyConstraint(['event_type_code'], ['event_types.code'], ondelete='RESTRICT', name='fk_event_subtypes_event_type_code'),
        PrimaryKeyConstraint('code', name='pk_event_subtypes'),
        Index('ix_event_subtypes_event_type_code', 'event_type_code')
    )

    code: Mapped[str] = mapped_column(String(64), primary_key=True)
    event_type_code: Mapped[str] = mapped_column(String(64), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=False)

    event_types: Mapped['EventTypes'] = relationship('EventTypes', back_populates='event_subtypes')
    match_events: Mapped[list['MatchEvents']] = relationship('MatchEvents', back_populates='event_subtypes')


t_role_permissions = Table(
    'role_permissions', Base.metadata,
    Column('role_id', SmallInteger, primary_key=True),
    Column('permission_id', SmallInteger, primary_key=True),
    ForeignKeyConstraint(['permission_id'], ['permissions.id'], ondelete='CASCADE', name='fk_role_permissions_permission_id'),
    ForeignKeyConstraint(['role_id'], ['roles.id'], ondelete='CASCADE', name='fk_role_permissions_role_id'),
    PrimaryKeyConstraint('role_id', 'permission_id', name='pk_role_permissions')
)


class TeamWellnessRankings(Base):
    __tablename__ = 'team_wellness_rankings'
    __table_args__ = (
        ForeignKeyConstraint(['team_id'], ['teams.id'], ondelete='CASCADE', name='team_wellness_rankings_team_id_fkey'),
        PrimaryKeyConstraint('id', name='team_wellness_rankings_pkey'),
        UniqueConstraint('team_id', 'month_reference', name='uq_team_wellness_rankings_team_month'),
        Index('idx_rankings_month_rank', 'month_reference', 'rank'),
        Index('idx_rankings_team_month', 'team_id', 'month_reference')
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    team_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    month_reference: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    athletes_90plus: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    response_rate_pre: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    response_rate_post: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    avg_rate: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    rank: Mapped[Optional[int]] = mapped_column(Integer)

    team: Mapped['Teams'] = relationship('Teams', back_populates='team_wellness_rankings')


class Users(Base):
    __tablename__ = 'users'
    __table_args__ = (
        CheckConstraint('deleted_at IS NULL AND deleted_reason IS NULL OR deleted_at IS NOT NULL AND deleted_reason IS NOT NULL', name='ck_users_deleted_reason'),
        CheckConstraint("status::text = ANY (ARRAY['ativo'::character varying, 'inativo'::character varying, 'arquivado'::character varying]::text[])", name='ck_users_status'),
        ForeignKeyConstraint(['person_id'], ['persons.id'], ondelete='RESTRICT', name='fk_users_person_id'),
        PrimaryKeyConstraint('id', name='pk_users'),
        Index('ix_users_person_id', 'person_id'),
        Index('ux_users_email', unique=True),
        Index('ux_users_superadmin', 'is_superadmin', unique=True)
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    person_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    is_superadmin: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    is_locked: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    status: Mapped[str] = mapped_column(String(20), nullable=False, server_default=text("'ativo'::character varying"))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    password_hash: Mapped[Optional[str]] = mapped_column(Text)
    expired_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    deleted_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    deleted_reason: Mapped[Optional[str]] = mapped_column(Text)

    competitions: Mapped[list['Competitions']] = relationship('Competitions', back_populates='users')
    seasons: Mapped[list['Seasons']] = relationship('Seasons', back_populates='created_by_user')
    teams: Mapped[list['Teams']] = relationship('Teams', back_populates='created_by_user')
    person: Mapped['Persons'] = relationship('Persons', back_populates='users')
    audit_logs: Mapped[list['AuditLogs']] = relationship('AuditLogs', back_populates='actor')
    data_access_logs: Mapped[list['DataAccessLogs']] = relationship('DataAccessLogs', back_populates='user')
    email_queue: Mapped[list['EmailQueue']] = relationship('EmailQueue', back_populates='created_by_user')
    exercise_tags: Mapped[list['ExerciseTags']] = relationship('ExerciseTags', foreign_keys='[ExerciseTags.approved_by_admin_id]', back_populates='approved_by_admin')
    exercise_tags_: Mapped[list['ExerciseTags']] = relationship('ExerciseTags', foreign_keys='[ExerciseTags.suggested_by_user_id]', back_populates='suggested_by_user')
    exercises: Mapped[list['Exercises']] = relationship('Exercises', back_populates='created_by_user')
    export_jobs: Mapped[list['ExportJobs']] = relationship('ExportJobs', back_populates='user')
    export_rate_limits: Mapped[list['ExportRateLimits']] = relationship('ExportRateLimits', back_populates='user')
    matches: Mapped[list['Matches']] = relationship('Matches', back_populates='created_by_user')
    medical_cases: Mapped[list['MedicalCases']] = relationship('MedicalCases', back_populates='created_by_user')
    notifications: Mapped[list['Notifications']] = relationship('Notifications', back_populates='user')
    org_memberships: Mapped[list['OrgMemberships']] = relationship('OrgMemberships', back_populates='created_by_user')
    password_resets: Mapped[list['PasswordResets']] = relationship('PasswordResets', back_populates='user')
    person_addresses: Mapped[list['PersonAddresses']] = relationship('PersonAddresses', back_populates='created_by_user')
    person_contacts: Mapped[list['PersonContacts']] = relationship('PersonContacts', back_populates='created_by_user')
    person_documents: Mapped[list['PersonDocuments']] = relationship('PersonDocuments', back_populates='created_by_user')
    person_media: Mapped[list['PersonMedia']] = relationship('PersonMedia', back_populates='created_by_user')
    team_registrations: Mapped[list['TeamRegistrations']] = relationship('TeamRegistrations', back_populates='created_by_user')
    training_alerts: Mapped[list['TrainingAlerts']] = relationship('TrainingAlerts', back_populates='dismissed_by_user')
    training_cycles: Mapped[list['TrainingCycles']] = relationship('TrainingCycles', back_populates='created_by_user')
    exercise_favorites: Mapped[list['ExerciseFavorites']] = relationship('ExerciseFavorites', back_populates='user')
    training_microcycles: Mapped[list['TrainingMicrocycles']] = relationship('TrainingMicrocycles', back_populates='created_by_user')
    match_events: Mapped[list['MatchEvents']] = relationship('MatchEvents', back_populates='created_by_user')
    training_sessions: Mapped[list['TrainingSessions']] = relationship('TrainingSessions', foreign_keys='[TrainingSessions.closed_by_user_id]', back_populates='closed_by_user')
    training_sessions_: Mapped[list['TrainingSessions']] = relationship('TrainingSessions', foreign_keys='[TrainingSessions.created_by_user_id]', back_populates='created_by_user')
    attendance: Mapped[list['Attendance']] = relationship('Attendance', foreign_keys='[Attendance.correction_by_user_id]', back_populates='correction_by_user')
    attendance_: Mapped[list['Attendance']] = relationship('Attendance', foreign_keys='[Attendance.created_by_user_id]', back_populates='created_by_user')
    wellness_post: Mapped[list['WellnessPost']] = relationship('WellnessPost', back_populates='created_by_user')
    wellness_pre: Mapped[list['WellnessPre']] = relationship('WellnessPre', back_populates='created_by_user')


class AthleteBadges(Base):
    __tablename__ = 'athlete_badges'
    __table_args__ = (
        CheckConstraint("badge_type::text = ANY (ARRAY['wellness_champion_monthly'::character varying, 'wellness_streak_3months'::character varying]::text[])", name='ck_athlete_badges_type'),
        ForeignKeyConstraint(['athlete_id'], ['athletes.id'], ondelete='CASCADE', name='athlete_badges_athlete_id_fkey'),
        PrimaryKeyConstraint('id', name='athlete_badges_pkey'),
        Index('idx_badges_athlete_month', 'athlete_id', 'month_reference')
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    athlete_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    badge_type: Mapped[str] = mapped_column(String(50), nullable=False)
    earned_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    month_reference: Mapped[Optional[datetime.date]] = mapped_column(Date)

    athlete: Mapped['Athletes'] = relationship('Athletes', back_populates='athlete_badges')


class AuditLogs(Base):
    __tablename__ = 'audit_logs'
    __table_args__ = (
        ForeignKeyConstraint(['actor_id'], ['users.id'], ondelete='SET NULL', name='fk_audit_logs_actor_id'),
        PrimaryKeyConstraint('id', name='pk_audit_logs'),
        Index('ix_audit_logs_actor_id', 'actor_id'),
        Index('ix_audit_logs_created_at', 'created_at'),
        Index('ix_audit_logs_entity', 'entity'),
        Index('ix_audit_logs_entity_id', 'entity_id')
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    entity: Mapped[str] = mapped_column(String(64), nullable=False)
    action: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    entity_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    actor_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    context: Mapped[Optional[dict]] = mapped_column(JSONB)
    old_value: Mapped[Optional[dict]] = mapped_column(JSONB)
    new_value: Mapped[Optional[dict]] = mapped_column(JSONB)
    justification: Mapped[Optional[str]] = mapped_column(Text)

    actor: Mapped[Optional['Users']] = relationship('Users', back_populates='audit_logs')


class CompetitionStandings(Base):
    __tablename__ = 'competition_standings'
    __table_args__ = (
        ForeignKeyConstraint(['competition_id'], ['competitions.id'], ondelete='CASCADE', name='fk_competition_standings_competition_id'),
        ForeignKeyConstraint(['opponent_team_id'], ['competition_opponent_teams.id'], ondelete='CASCADE', name='fk_competition_standings_opponent_team_id'),
        ForeignKeyConstraint(['phase_id'], ['competition_phases.id'], ondelete='CASCADE', name='fk_competition_standings_phase_id'),
        PrimaryKeyConstraint('id', name='pk_competition_standings'),
        UniqueConstraint('competition_id', 'phase_id', 'opponent_team_id', name='uk_competition_standings_team_phase'),
        Index('ix_competition_standings_competition_id', 'competition_id'),
        Index('ix_competition_standings_position', 'competition_id', 'phase_id', 'position')
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    competition_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    opponent_team_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    phase_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    group_name: Mapped[Optional[str]] = mapped_column(String(50))
    points: Mapped[Optional[int]] = mapped_column(Integer, server_default=text('0'))
    played: Mapped[Optional[int]] = mapped_column(Integer, server_default=text('0'))
    wins: Mapped[Optional[int]] = mapped_column(Integer, server_default=text('0'))
    draws: Mapped[Optional[int]] = mapped_column(Integer, server_default=text('0'))
    losses: Mapped[Optional[int]] = mapped_column(Integer, server_default=text('0'))
    goals_for: Mapped[Optional[int]] = mapped_column(Integer, server_default=text('0'))
    goals_against: Mapped[Optional[int]] = mapped_column(Integer, server_default=text('0'))
    goal_difference: Mapped[Optional[int]] = mapped_column(Integer, server_default=text('0'))
    recent_form: Mapped[Optional[str]] = mapped_column(String(10))
    qualification_status: Mapped[Optional[str]] = mapped_column(String(50))

    competition: Mapped['Competitions'] = relationship('Competitions', back_populates='competition_standings')
    opponent_team: Mapped['CompetitionOpponentTeams'] = relationship('CompetitionOpponentTeams', back_populates='competition_standings')
    phase: Mapped[Optional['CompetitionPhases']] = relationship('CompetitionPhases', back_populates='competition_standings')


class DataAccessLogs(Base):
    __tablename__ = 'data_access_logs'
    __table_args__ = (
        ForeignKeyConstraint(['athlete_id'], ['athletes.id'], ondelete='SET NULL', name='data_access_logs_athlete_id_fkey'),
        ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE', name='data_access_logs_user_id_fkey'),
        PrimaryKeyConstraint('id', name='data_access_logs_pkey'),
        Index('idx_access_logs_accessed_at', 'accessed_at'),
        Index('idx_access_logs_athlete', 'athlete_id', 'accessed_at'),
        Index('idx_access_logs_user', 'user_id', 'accessed_at')
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    accessed_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    athlete_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    ip_address: Mapped[Optional[Any]] = mapped_column(INET)
    user_agent: Mapped[Optional[str]] = mapped_column(Text)

    athlete: Mapped[Optional['Athletes']] = relationship('Athletes', back_populates='data_access_logs')
    user: Mapped['Users'] = relationship('Users', back_populates='data_access_logs')


class EmailQueue(Base):
    __tablename__ = 'email_queue'
    __table_args__ = (
        ForeignKeyConstraint(['created_by_user_id'], ['users.id'], name='fk_email_queue_created_by_user'),
        PrimaryKeyConstraint('id', name='email_queue_pkey'),
        Index('ix_email_queue_created_at', 'created_at'),
        Index('ix_email_queue_next_retry', 'next_retry_at'),
        Index('ix_email_queue_status', 'status'),
        Index('ix_email_queue_to_email', 'to_email')
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    template_type: Mapped[str] = mapped_column(String(50), nullable=False)
    to_email: Mapped[str] = mapped_column(String(255), nullable=False)
    template_data: Mapped[dict] = mapped_column(JSONB, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    attempts: Mapped[int] = mapped_column(Integer, nullable=False)
    max_attempts: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    next_retry_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    last_error: Mapped[Optional[str]] = mapped_column(Text)
    sent_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    created_by_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)

    created_by_user: Mapped[Optional['Users']] = relationship('Users', back_populates='email_queue')


class ExerciseTags(Base):
    __tablename__ = 'exercise_tags'
    __table_args__ = (
        ForeignKeyConstraint(['approved_by_admin_id'], ['users.id'], ondelete='SET NULL', name='exercise_tags_approved_by_admin_id_fkey'),
        ForeignKeyConstraint(['parent_tag_id'], ['exercise_tags.id'], ondelete='CASCADE', name='exercise_tags_parent_tag_id_fkey'),
        ForeignKeyConstraint(['suggested_by_user_id'], ['users.id'], ondelete='SET NULL', name='exercise_tags_suggested_by_user_id_fkey'),
        PrimaryKeyConstraint('id', name='exercise_tags_pkey'),
        UniqueConstraint('name', name='exercise_tags_name_key'),
        Index('idx_tags_parent', 'parent_tag_id')
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    parent_tag_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    description: Mapped[Optional[str]] = mapped_column(Text)
    display_order: Mapped[Optional[int]] = mapped_column(Integer)
    suggested_by_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    approved_by_admin_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    approved_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))

    approved_by_admin: Mapped[Optional['Users']] = relationship('Users', foreign_keys=[approved_by_admin_id], back_populates='exercise_tags')
    parent_tag: Mapped[Optional['ExerciseTags']] = relationship('ExerciseTags', remote_side=[id], back_populates='parent_tag_reverse')
    parent_tag_reverse: Mapped[list['ExerciseTags']] = relationship('ExerciseTags', remote_side=[parent_tag_id], back_populates='parent_tag')
    suggested_by_user: Mapped[Optional['Users']] = relationship('Users', foreign_keys=[suggested_by_user_id], back_populates='exercise_tags_')


class Exercises(Base):
    __tablename__ = 'exercises'
    __table_args__ = (
        ForeignKeyConstraint(['created_by_user_id'], ['users.id'], ondelete='CASCADE', name='exercises_created_by_user_id_fkey'),
        ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE', name='exercises_organization_id_fkey'),
        PrimaryKeyConstraint('id', name='exercises_pkey'),
        Index('idx_exercises_tags', 'tag_ids')
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    organization_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    tag_ids: Mapped[list[uuid.UUID]] = mapped_column(ARRAY(Uuid()), nullable=False, server_default=text("'{}'::uuid[]"))
    created_by_user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    description: Mapped[Optional[str]] = mapped_column(Text)
    category: Mapped[Optional[str]] = mapped_column(String(100))
    media_url: Mapped[Optional[str]] = mapped_column(String(500))

    created_by_user: Mapped['Users'] = relationship('Users', back_populates='exercises')
    organization: Mapped['Organizations'] = relationship('Organizations', back_populates='exercises')
    exercise_favorites: Mapped[list['ExerciseFavorites']] = relationship('ExerciseFavorites', back_populates='exercise')
    training_session_exercises: Mapped[list['TrainingSessionExercises']] = relationship('TrainingSessionExercises', back_populates='exercise')


class ExportJobs(Base):
    __tablename__ = 'export_jobs'
    __table_args__ = (
        CheckConstraint("status::text = ANY (ARRAY['pending'::character varying, 'processing'::character varying, 'completed'::character varying, 'failed'::character varying]::text[])", name='ck_export_jobs_status'),
        ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE', name='export_jobs_user_id_fkey'),
        PrimaryKeyConstraint('id', name='export_jobs_pkey'),
        Index('idx_export_cache', 'params_hash', 'status')
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    export_type: Mapped[str] = mapped_column(String(50), nullable=False)
    params: Mapped[dict] = mapped_column(JSONB, nullable=False)
    params_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, server_default=text("'pending'::character varying"))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    file_url: Mapped[Optional[str]] = mapped_column(String(500))
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    completed_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))

    user: Mapped['Users'] = relationship('Users', back_populates='export_jobs')


class ExportRateLimits(Base):
    __tablename__ = 'export_rate_limits'
    __table_args__ = (
        ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE', name='export_rate_limits_user_id_fkey'),
        PrimaryKeyConstraint('user_id', 'date', name='export_rate_limits_pkey')
    )

    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    date: Mapped[datetime.date] = mapped_column(Date, primary_key=True)
    count: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'))

    user: Mapped['Users'] = relationship('Users', back_populates='export_rate_limits')


class Matches(Base):
    __tablename__ = 'matches'
    __table_args__ = (
        CheckConstraint('deleted_at IS NULL AND deleted_reason IS NULL OR deleted_at IS NOT NULL AND deleted_reason IS NOT NULL', name='ck_matches_deleted_reason'),
        CheckConstraint('final_score_away IS NULL OR final_score_away >= 0', name='ck_matches_score_away'),
        CheckConstraint('final_score_home IS NULL OR final_score_home >= 0', name='ck_matches_score_home'),
        CheckConstraint('home_team_id <> away_team_id', name='ck_matches_different_teams'),
        CheckConstraint('our_team_id = home_team_id OR our_team_id = away_team_id', name='ck_matches_our_team'),
        CheckConstraint("phase::text = ANY (ARRAY['group'::character varying, 'semifinal'::character varying, 'final'::character varying, 'friendly'::character varying]::text[])", name='ck_matches_phase'),
        CheckConstraint("status::text = ANY (ARRAY['scheduled'::character varying, 'in_progress'::character varying, 'finished'::character varying, 'cancelled'::character varying]::text[])", name='ck_matches_status'),
        ForeignKeyConstraint(['away_team_id'], ['teams.id'], ondelete='RESTRICT', name='fk_matches_away_team_id'),
        ForeignKeyConstraint(['created_by_user_id'], ['users.id'], ondelete='RESTRICT', name='fk_matches_created_by_user_id'),
        ForeignKeyConstraint(['home_team_id'], ['teams.id'], ondelete='RESTRICT', name='fk_matches_home_team_id'),
        ForeignKeyConstraint(['our_team_id'], ['teams.id'], ondelete='RESTRICT', name='fk_matches_our_team_id'),
        ForeignKeyConstraint(['season_id'], ['seasons.id'], ondelete='RESTRICT', name='fk_matches_season_id'),
        PrimaryKeyConstraint('id', name='pk_matches'),
        Index('ix_matches_away_team_id', 'away_team_id'),
        Index('ix_matches_home_team_id', 'home_team_id'),
        Index('ix_matches_match_date', 'match_date'),
        Index('ix_matches_season_date_active', 'season_id', 'match_date'),
        Index('ix_matches_season_id', 'season_id'),
        Index('ix_matches_status', 'status')
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    season_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    match_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    phase: Mapped[str] = mapped_column(String(32), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    home_team_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    away_team_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    our_team_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    created_by_user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    competition_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    start_time: Mapped[Optional[datetime.time]] = mapped_column(Time)
    venue: Mapped[Optional[str]] = mapped_column(String(120))
    final_score_home: Mapped[Optional[int]] = mapped_column(SmallInteger)
    final_score_away: Mapped[Optional[int]] = mapped_column(SmallInteger)
    notes: Mapped[Optional[str]] = mapped_column(Text)
    deleted_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    deleted_reason: Mapped[Optional[str]] = mapped_column(Text)

    away_team: Mapped['Teams'] = relationship('Teams', foreign_keys=[away_team_id], back_populates='matches')
    created_by_user: Mapped['Users'] = relationship('Users', back_populates='matches')
    home_team: Mapped['Teams'] = relationship('Teams', foreign_keys=[home_team_id], back_populates='matches_')
    our_team: Mapped['Teams'] = relationship('Teams', foreign_keys=[our_team_id], back_populates='matches1')
    season: Mapped['Seasons'] = relationship('Seasons', back_populates='matches')
    competition_matches: Mapped[list['CompetitionMatches']] = relationship('CompetitionMatches', back_populates='linked_match')
    match_periods: Mapped[list['MatchPeriods']] = relationship('MatchPeriods', back_populates='match')
    match_possessions: Mapped[list['MatchPossessions']] = relationship('MatchPossessions', back_populates='match')
    match_roster: Mapped[list['MatchRoster']] = relationship('MatchRoster', back_populates='match')
    match_teams: Mapped[list['MatchTeams']] = relationship('MatchTeams', back_populates='match')
    match_events: Mapped[list['MatchEvents']] = relationship('MatchEvents', back_populates='match')


class MedicalCases(Base):
    __tablename__ = 'medical_cases'
    __table_args__ = (
        CheckConstraint('deleted_at IS NULL AND deleted_reason IS NULL OR deleted_at IS NOT NULL AND deleted_reason IS NOT NULL', name='ck_medical_cases_deleted_reason'),
        CheckConstraint("status::text = ANY (ARRAY['ativo'::character varying, 'resolvido'::character varying, 'em_acompanhamento'::character varying]::text[])", name='medical_cases_status_check'),
        ForeignKeyConstraint(['athlete_id'], ['athletes.id'], ondelete='RESTRICT', name='fk_medical_cases_athlete_id'),
        ForeignKeyConstraint(['created_by_user_id'], ['users.id'], ondelete='SET NULL', name='fk_medical_cases_created_by_user'),
        ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='RESTRICT', name='fk_medical_cases_organization'),
        PrimaryKeyConstraint('id', name='pk_medical_cases'),
        Index('idx_medical_cases_athlete', 'athlete_id'),
        Index('idx_medical_cases_organization_id', 'organization_id'),
        Index('ix_medical_cases_athlete_status_active', 'athlete_id', 'status')
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    athlete_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    started_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    reason: Mapped[Optional[str]] = mapped_column(String(500))
    status: Mapped[Optional[str]] = mapped_column(String(50), server_default=text("'ativo'::character varying"))
    notes: Mapped[Optional[str]] = mapped_column(Text)
    ended_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    deleted_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    deleted_reason: Mapped[Optional[str]] = mapped_column(Text)
    organization_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    created_by_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)

    athlete: Mapped['Athletes'] = relationship('Athletes', back_populates='medical_cases')
    created_by_user: Mapped[Optional['Users']] = relationship('Users', back_populates='medical_cases')
    organization: Mapped[Optional['Organizations']] = relationship('Organizations', back_populates='medical_cases')


class Notifications(Base):
    __tablename__ = 'notifications'
    __table_args__ = (
        ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE', name='notifications_user_id_fkey'),
        PrimaryKeyConstraint('id', name='notifications_pkey'),
        Index('idx_notifications_cleanup', 'read_at', 'created_at'),
        Index('idx_notifications_created', 'created_at'),
        Index('idx_notifications_unread', 'user_id', 'created_at'),
        Index('idx_notifications_user_read', 'user_id', 'read_at')
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    notification_data: Mapped[Optional[dict]] = mapped_column(JSONB)
    read_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))

    user: Mapped['Users'] = relationship('Users', back_populates='notifications')


class OrgMemberships(Base):
    __tablename__ = 'org_memberships'
    __table_args__ = (
        CheckConstraint('deleted_at IS NULL AND deleted_reason IS NULL OR deleted_at IS NOT NULL AND deleted_reason IS NOT NULL', name='ck_org_memberships_deleted_reason'),
        ForeignKeyConstraint(['created_by_user_id'], ['users.id'], name='fk_org_memberships_created_by_user'),
        ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='RESTRICT', name='fk_org_memberships_organization_id'),
        ForeignKeyConstraint(['person_id'], ['persons.id'], ondelete='RESTRICT', name='fk_org_memberships_person_id'),
        ForeignKeyConstraint(['role_id'], ['roles.id'], ondelete='RESTRICT', name='fk_org_memberships_role_id'),
        PrimaryKeyConstraint('id', name='pk_org_memberships'),
        Index('ix_org_memberships_org_active', 'organization_id'),
        Index('ix_org_memberships_organization_id', 'organization_id'),
        Index('ix_org_memberships_person_active', 'person_id'),
        Index('ix_org_memberships_person_id', 'person_id'),
        Index('ix_org_memberships_person_org_active', 'person_id', 'organization_id'),
        Index('ix_org_memberships_role_id', 'role_id'),
        Index('ux_org_memberships_active', 'person_id', 'organization_id', 'role_id', unique=True)
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    person_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    role_id: Mapped[int] = mapped_column(Integer, nullable=False)
    organization_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    start_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    end_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    deleted_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    deleted_reason: Mapped[Optional[str]] = mapped_column(Text)
    created_by_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)

    teams: Mapped[list['Teams']] = relationship('Teams', foreign_keys='[Teams.coach_membership_id]', back_populates='coach_membership')
    teams_: Mapped[list['Teams']] = relationship('Teams', foreign_keys='[Teams.created_by_membership_id]', back_populates='created_by_membership')
    created_by_user: Mapped[Optional['Users']] = relationship('Users', back_populates='org_memberships')
    organization: Mapped['Organizations'] = relationship('Organizations', back_populates='org_memberships')
    person: Mapped['Persons'] = relationship('Persons', back_populates='org_memberships')
    role: Mapped['Roles'] = relationship('Roles', back_populates='org_memberships')
    session_templates: Mapped[list['SessionTemplates']] = relationship('SessionTemplates', back_populates='created_by_membership')
    team_memberships: Mapped[list['TeamMemberships']] = relationship('TeamMemberships', back_populates='org_membership')


class PasswordResets(Base):
    __tablename__ = 'password_resets'
    __table_args__ = (
        CheckConstraint('deleted_at IS NULL AND deleted_reason IS NULL OR deleted_at IS NOT NULL AND deleted_reason IS NOT NULL', name='ck_password_resets_deleted_reason'),
        CheckConstraint("token_type = ANY (ARRAY['reset'::text, 'welcome'::text])", name='ck_password_resets_token_type'),
        ForeignKeyConstraint(['user_id'], ['users.id'], name='fk_password_resets_user_id'),
        PrimaryKeyConstraint('id', name='pk_password_resets'),
        UniqueConstraint('token', name='password_resets_token_key'),
        Index('ix_password_resets_expires_at', 'expires_at'),
        Index('ix_password_resets_token', 'token'),
        Index('ix_password_resets_user_id', 'user_id')
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    token: Mapped[str] = mapped_column(Text, nullable=False)
    token_type: Mapped[str] = mapped_column(Text, nullable=False, server_default=text("'reset'::text"))
    used: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    expires_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    used_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    deleted_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    deleted_reason: Mapped[Optional[str]] = mapped_column(Text)

    user: Mapped['Users'] = relationship('Users', back_populates='password_resets')


class PersonAddresses(Base):
    __tablename__ = 'person_addresses'
    __table_args__ = (
        CheckConstraint("address_type::text = ANY (ARRAY['residencial_1'::character varying, 'residencial_2'::character varying, 'comercial'::character varying, 'outro'::character varying]::text[])", name='ck_person_addresses_type'),
        CheckConstraint('deleted_at IS NULL AND deleted_reason IS NULL OR deleted_at IS NOT NULL AND deleted_reason IS NOT NULL', name='ck_person_addresses_deleted_reason'),
        ForeignKeyConstraint(['created_by_user_id'], ['users.id'], ondelete='SET NULL', name='fk_person_addresses_created_by_user'),
        ForeignKeyConstraint(['person_id'], ['persons.id'], ondelete='CASCADE', name='person_addresses_person_id_fkey'),
        PrimaryKeyConstraint('id', name='person_addresses_pkey'),
        Index('ix_person_addresses_city_state', 'city', 'state'),
        Index('ix_person_addresses_created_by_user_id', 'created_by_user_id'),
        Index('ix_person_addresses_deleted_at', 'deleted_at'),
        Index('ix_person_addresses_person_id', 'person_id'),
        Index('uq_person_addresses_primary', 'person_id', unique=True)
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    person_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    address_type: Mapped[str] = mapped_column(String(50), nullable=False)
    street: Mapped[str] = mapped_column(String(200), nullable=False)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    state: Mapped[str] = mapped_column(String(2), nullable=False)
    country: Mapped[str] = mapped_column(String(100), nullable=False, server_default=text("'Brasil'::character varying"))
    is_primary: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    number: Mapped[Optional[str]] = mapped_column(String(20))
    complement: Mapped[Optional[str]] = mapped_column(String(100))
    neighborhood: Mapped[Optional[str]] = mapped_column(String(100))
    postal_code: Mapped[Optional[str]] = mapped_column(String(10))
    deleted_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    deleted_reason: Mapped[Optional[str]] = mapped_column(Text)
    created_by_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)

    created_by_user: Mapped[Optional['Users']] = relationship('Users', back_populates='person_addresses')
    person: Mapped['Persons'] = relationship('Persons', back_populates='person_addresses')


class PersonContacts(Base):
    __tablename__ = 'person_contacts'
    __table_args__ = (
        CheckConstraint("contact_type::text = ANY (ARRAY['telefone'::character varying, 'email'::character varying, 'whatsapp'::character varying, 'outro'::character varying]::text[])", name='ck_person_contacts_type'),
        CheckConstraint('deleted_at IS NULL AND deleted_reason IS NULL OR deleted_at IS NOT NULL AND deleted_reason IS NOT NULL', name='ck_person_contacts_deleted_reason'),
        ForeignKeyConstraint(['created_by_user_id'], ['users.id'], ondelete='SET NULL', name='fk_person_contacts_created_by_user'),
        ForeignKeyConstraint(['person_id'], ['persons.id'], ondelete='CASCADE', name='person_contacts_person_id_fkey'),
        PrimaryKeyConstraint('id', name='person_contacts_pkey'),
        Index('ix_person_contacts_created_by_user_id', 'created_by_user_id'),
        Index('ix_person_contacts_deleted_at', 'deleted_at'),
        Index('ix_person_contacts_email_lower'),
        Index('ix_person_contacts_person_id', 'person_id'),
        Index('ix_person_contacts_type_value', 'contact_type', 'contact_value'),
        Index('ix_person_contacts_type_value_active', 'contact_type', 'contact_value'),
        Index('ix_person_contacts_value', 'contact_value'),
        Index('ix_person_contacts_value_active', 'contact_value'),
        Index('uq_person_contacts_primary_per_type', 'person_id', 'contact_type', unique=True)
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    person_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    contact_type: Mapped[str] = mapped_column(String(50), nullable=False)
    contact_value: Mapped[str] = mapped_column(String(200), nullable=False)
    is_primary: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    is_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    notes: Mapped[Optional[str]] = mapped_column(Text)
    deleted_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    deleted_reason: Mapped[Optional[str]] = mapped_column(Text)
    created_by_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)

    created_by_user: Mapped[Optional['Users']] = relationship('Users', back_populates='person_contacts')
    person: Mapped['Persons'] = relationship('Persons', back_populates='person_contacts')


class PersonDocuments(Base):
    __tablename__ = 'person_documents'
    __table_args__ = (
        CheckConstraint('deleted_at IS NULL AND deleted_reason IS NULL OR deleted_at IS NOT NULL AND deleted_reason IS NOT NULL', name='ck_person_documents_deleted_reason'),
        CheckConstraint("document_type::text = ANY (ARRAY['cpf'::character varying, 'rg'::character varying, 'cnh'::character varying, 'passaporte'::character varying, 'certidao_nascimento'::character varying, 'titulo_eleitor'::character varying, 'outro'::character varying]::text[])", name='ck_person_documents_type'),
        ForeignKeyConstraint(['created_by_user_id'], ['users.id'], ondelete='SET NULL', name='fk_person_documents_created_by_user'),
        ForeignKeyConstraint(['person_id'], ['persons.id'], ondelete='CASCADE', name='person_documents_person_id_fkey'),
        PrimaryKeyConstraint('id', name='person_documents_pkey'),
        Index('ix_person_documents_cpf_active', 'document_number'),
        Index('ix_person_documents_created_by_user_id', 'created_by_user_id'),
        Index('ix_person_documents_deleted_at', 'deleted_at'),
        Index('ix_person_documents_number', 'document_number'),
        Index('ix_person_documents_person_id', 'person_id'),
        Index('ix_person_documents_rg_active', 'document_number'),
        Index('ix_person_documents_type', 'document_type'),
        Index('ix_person_documents_type_number', 'document_type', 'document_number'),
        Index('uq_person_documents_per_type', 'person_id', 'document_type', 'document_number', unique=True)
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    person_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    document_type: Mapped[str] = mapped_column(String(50), nullable=False)
    document_number: Mapped[str] = mapped_column(String(100), nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    issuing_authority: Mapped[Optional[str]] = mapped_column(String(100))
    issue_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    expiry_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    document_file_url: Mapped[Optional[str]] = mapped_column(Text)
    notes: Mapped[Optional[str]] = mapped_column(Text)
    deleted_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    deleted_reason: Mapped[Optional[str]] = mapped_column(Text)
    created_by_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)

    created_by_user: Mapped[Optional['Users']] = relationship('Users', back_populates='person_documents')
    person: Mapped['Persons'] = relationship('Persons', back_populates='person_documents')


class PersonMedia(Base):
    __tablename__ = 'person_media'
    __table_args__ = (
        CheckConstraint('deleted_at IS NULL AND deleted_reason IS NULL OR deleted_at IS NOT NULL AND deleted_reason IS NOT NULL', name='ck_person_media_deleted_reason'),
        CheckConstraint("media_type::text = ANY (ARRAY['foto_perfil'::character varying, 'foto_documento'::character varying, 'video'::character varying, 'outro'::character varying]::text[])", name='ck_person_media_type'),
        ForeignKeyConstraint(['created_by_user_id'], ['users.id'], ondelete='SET NULL', name='fk_person_media_created_by_user'),
        ForeignKeyConstraint(['person_id'], ['persons.id'], ondelete='CASCADE', name='person_media_person_id_fkey'),
        PrimaryKeyConstraint('id', name='person_media_pkey'),
        Index('ix_person_media_created_by_user_id', 'created_by_user_id'),
        Index('ix_person_media_deleted_at', 'deleted_at'),
        Index('ix_person_media_person_id', 'person_id'),
        Index('ix_person_media_person_type', 'person_id', 'media_type'),
        Index('ix_person_media_type', 'media_type'),
        Index('uq_person_media_primary_per_type', 'person_id', 'media_type', unique=True)
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    person_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    media_type: Mapped[str] = mapped_column(String(50), nullable=False)
    file_url: Mapped[str] = mapped_column(Text, nullable=False)
    is_primary: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    file_name: Mapped[Optional[str]] = mapped_column(String(255))
    file_size: Mapped[Optional[int]] = mapped_column(Integer)
    mime_type: Mapped[Optional[str]] = mapped_column(String(100))
    description: Mapped[Optional[str]] = mapped_column(Text)
    deleted_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    deleted_reason: Mapped[Optional[str]] = mapped_column(Text)
    created_by_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)

    created_by_user: Mapped[Optional['Users']] = relationship('Users', back_populates='person_media')
    person: Mapped['Persons'] = relationship('Persons', back_populates='person_media')


class TeamRegistrations(Base):
    __tablename__ = 'team_registrations'
    __table_args__ = (
        CheckConstraint('deleted_at IS NULL AND deleted_reason IS NULL OR deleted_at IS NOT NULL AND deleted_reason IS NOT NULL', name='ck_team_registrations_deleted_reason'),
        ForeignKeyConstraint(['athlete_id'], ['athletes.id'], ondelete='RESTRICT', name='fk_team_registrations_athlete_id'),
        ForeignKeyConstraint(['created_by_user_id'], ['users.id'], name='fk_team_registrations_created_by_user'),
        ForeignKeyConstraint(['team_id'], ['teams.id'], ondelete='RESTRICT', name='fk_team_registrations_team_id'),
        PrimaryKeyConstraint('id', name='pk_team_registrations'),
        Index('idx_team_registrations_athlete_active', 'athlete_id', 'deleted_at'),
        Index('idx_team_registrations_team_active', 'team_id', 'deleted_at'),
        Index('ix_team_registrations_athlete_active', 'athlete_id'),
        Index('ix_team_registrations_athlete_id', 'athlete_id'),
        Index('ix_team_registrations_period', 'start_at', 'end_at'),
        Index('ix_team_registrations_team_active', 'team_id'),
        Index('ix_team_registrations_team_athlete_active', 'team_id', 'athlete_id'),
        Index('ix_team_registrations_team_id', 'team_id'),
        Index('ux_team_registrations_active', 'athlete_id', 'team_id', unique=True)
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    athlete_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    team_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    start_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    end_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    deleted_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    deleted_reason: Mapped[Optional[str]] = mapped_column(Text)
    created_by_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)

    athlete: Mapped['Athletes'] = relationship('Athletes', back_populates='team_registrations')
    created_by_user: Mapped[Optional['Users']] = relationship('Users', back_populates='team_registrations')
    team: Mapped['Teams'] = relationship('Teams', back_populates='team_registrations')
    attendance: Mapped[list['Attendance']] = relationship('Attendance', back_populates='team_registration')


class TrainingAlerts(Base):
    __tablename__ = 'training_alerts'
    __table_args__ = (
        CheckConstraint("alert_type::text = ANY (ARRAY['weekly_overload'::character varying, 'low_wellness_response'::character varying]::text[])", name='ck_training_alerts_type'),
        CheckConstraint("severity::text = ANY (ARRAY['warning'::character varying, 'critical'::character varying]::text[])", name='ck_training_alerts_severity'),
        ForeignKeyConstraint(['dismissed_by_user_id'], ['users.id'], ondelete='SET NULL', name='training_alerts_dismissed_by_user_id_fkey'),
        ForeignKeyConstraint(['team_id'], ['teams.id'], ondelete='CASCADE', name='training_alerts_team_id_fkey'),
        PrimaryKeyConstraint('id', name='training_alerts_pkey'),
        Index('idx_alerts_active', 'team_id', 'triggered_at')
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    team_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    alert_type: Mapped[str] = mapped_column(String(50), nullable=False)
    severity: Mapped[str] = mapped_column(String(20), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    triggered_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    alert_metadata: Mapped[Optional[dict]] = mapped_column(JSONB)
    dismissed_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    dismissed_by_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)

    dismissed_by_user: Mapped[Optional['Users']] = relationship('Users', back_populates='training_alerts')
    team: Mapped['Teams'] = relationship('Teams', back_populates='training_alerts')


class TrainingCycles(Base):
    __tablename__ = 'training_cycles'
    __table_args__ = (
        CheckConstraint('start_date < end_date', name='check_cycle_dates'),
        CheckConstraint("status::text = ANY (ARRAY['active'::character varying, 'completed'::character varying, 'cancelled'::character varying]::text[])", name='check_cycle_status'),
        CheckConstraint("type::text = ANY (ARRAY['macro'::character varying, 'meso'::character varying]::text[])", name='check_cycle_type'),
        ForeignKeyConstraint(['created_by_user_id'], ['users.id'], name='training_cycles_created_by_user_id_fkey'),
        ForeignKeyConstraint(['organization_id'], ['organizations.id'], name='training_cycles_organization_id_fkey'),
        ForeignKeyConstraint(['parent_cycle_id'], ['training_cycles.id'], name='training_cycles_parent_cycle_id_fkey'),
        ForeignKeyConstraint(['team_id'], ['teams.id'], name='training_cycles_team_id_fkey'),
        PrimaryKeyConstraint('id', name='training_cycles_pkey'),
        Index('idx_training_cycles_dates', 'start_date', 'end_date'),
        Index('idx_training_cycles_org', 'organization_id'),
        Index('idx_training_cycles_parent', 'parent_cycle_id'),
        Index('idx_training_cycles_status', 'status'),
        Index('idx_training_cycles_team', 'team_id'),
        Index('idx_training_cycles_type', 'type')
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    organization_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    team_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    type: Mapped[str] = mapped_column(String, nullable=False)
    start_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    end_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False, server_default=text("'''active'''::character varying"))
    created_by_user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    objective: Mapped[Optional[str]] = mapped_column(Text)
    notes: Mapped[Optional[str]] = mapped_column(Text)
    parent_cycle_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    deleted_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    deleted_reason: Mapped[Optional[str]] = mapped_column(Text)

    created_by_user: Mapped['Users'] = relationship('Users', back_populates='training_cycles')
    organization: Mapped['Organizations'] = relationship('Organizations', back_populates='training_cycles')
    parent_cycle: Mapped[Optional['TrainingCycles']] = relationship('TrainingCycles', remote_side=[id], back_populates='parent_cycle_reverse')
    parent_cycle_reverse: Mapped[list['TrainingCycles']] = relationship('TrainingCycles', remote_side=[parent_cycle_id], back_populates='parent_cycle')
    team: Mapped['Teams'] = relationship('Teams', back_populates='training_cycles')
    training_microcycles: Mapped[list['TrainingMicrocycles']] = relationship('TrainingMicrocycles', back_populates='cycle')


class CompetitionMatches(Base):
    __tablename__ = 'competition_matches'
    __table_args__ = (
        ForeignKeyConstraint(['away_team_id'], ['competition_opponent_teams.id'], ondelete='SET NULL', name='fk_competition_matches_away_team_id'),
        ForeignKeyConstraint(['competition_id'], ['competitions.id'], ondelete='CASCADE', name='fk_competition_matches_competition_id'),
        ForeignKeyConstraint(['home_team_id'], ['competition_opponent_teams.id'], ondelete='SET NULL', name='fk_competition_matches_home_team_id'),
        ForeignKeyConstraint(['linked_match_id'], ['matches.id'], ondelete='SET NULL', name='fk_competition_matches_linked_match_id'),
        ForeignKeyConstraint(['phase_id'], ['competition_phases.id'], ondelete='SET NULL', name='fk_competition_matches_phase_id'),
        PrimaryKeyConstraint('id', name='pk_competition_matches'),
        Index('ix_competition_matches_competition_id', 'competition_id'),
        Index('ix_competition_matches_date', 'match_date'),
        Index('ix_competition_matches_linked_match_id', 'linked_match_id'),
        Index('ix_competition_matches_our_match', 'is_our_match'),
        Index('ix_competition_matches_phase_id', 'phase_id')
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    competition_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    phase_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    external_reference_id: Mapped[Optional[str]] = mapped_column(String(100))
    home_team_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    away_team_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    is_our_match: Mapped[Optional[bool]] = mapped_column(Boolean, server_default=text('false'))
    our_team_is_home: Mapped[Optional[bool]] = mapped_column(Boolean)
    linked_match_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    match_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    match_time: Mapped[Optional[datetime.time]] = mapped_column(Time)
    match_datetime: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    location: Mapped[Optional[str]] = mapped_column(String(255))
    round_number: Mapped[Optional[int]] = mapped_column(Integer)
    round_name: Mapped[Optional[str]] = mapped_column(String(100))
    home_score: Mapped[Optional[int]] = mapped_column(Integer)
    away_score: Mapped[Optional[int]] = mapped_column(Integer)
    home_score_extra: Mapped[Optional[int]] = mapped_column(Integer)
    away_score_extra: Mapped[Optional[int]] = mapped_column(Integer)
    home_score_penalties: Mapped[Optional[int]] = mapped_column(Integer)
    away_score_penalties: Mapped[Optional[int]] = mapped_column(Integer)
    status: Mapped[Optional[str]] = mapped_column(String(50), server_default=text("'scheduled'::character varying"))
    notes: Mapped[Optional[str]] = mapped_column(Text)

    away_team: Mapped[Optional['CompetitionOpponentTeams']] = relationship('CompetitionOpponentTeams', foreign_keys=[away_team_id], back_populates='competition_matches')
    competition: Mapped['Competitions'] = relationship('Competitions', back_populates='competition_matches')
    home_team: Mapped[Optional['CompetitionOpponentTeams']] = relationship('CompetitionOpponentTeams', foreign_keys=[home_team_id], back_populates='competition_matches_')
    linked_match: Mapped[Optional['Matches']] = relationship('Matches', back_populates='competition_matches')
    phase: Mapped[Optional['CompetitionPhases']] = relationship('CompetitionPhases', back_populates='competition_matches')


class ExerciseFavorites(Base):
    __tablename__ = 'exercise_favorites'
    __table_args__ = (
        ForeignKeyConstraint(['exercise_id'], ['exercises.id'], ondelete='CASCADE', name='exercise_favorites_exercise_id_fkey'),
        ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE', name='exercise_favorites_user_id_fkey'),
        PrimaryKeyConstraint('user_id', 'exercise_id', name='exercise_favorites_pkey')
    )

    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    exercise_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))

    exercise: Mapped['Exercises'] = relationship('Exercises', back_populates='exercise_favorites')
    user: Mapped['Users'] = relationship('Users', back_populates='exercise_favorites')


class MatchPeriods(Base):
    __tablename__ = 'match_periods'
    __table_args__ = (
        CheckConstraint('duration_seconds > 0', name='ck_match_periods_duration'),
        CheckConstraint('number >= 1', name='ck_match_periods_number'),
        CheckConstraint("period_type::text = ANY (ARRAY['regular'::character varying, 'extra_time'::character varying, 'shootout_7m'::character varying]::text[])", name='ck_match_periods_type'),
        ForeignKeyConstraint(['match_id'], ['matches.id'], ondelete='CASCADE', name='fk_match_periods_match_id'),
        PrimaryKeyConstraint('id', name='pk_match_periods'),
        Index('ix_match_periods_match_id', 'match_id')
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    match_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    number: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    duration_seconds: Mapped[int] = mapped_column(Integer, nullable=False)
    period_type: Mapped[str] = mapped_column(String(32), nullable=False)

    match: Mapped['Matches'] = relationship('Matches', back_populates='match_periods')


class MatchPossessions(Base):
    __tablename__ = 'match_possessions'
    __table_args__ = (
        CheckConstraint('end_period_number >= start_period_number', name='ck_match_possessions_end_period'),
        CheckConstraint('end_time_seconds >= 0', name='ck_match_possessions_end_time'),
        CheckConstraint("result::text = ANY (ARRAY['goal'::character varying, 'turnover'::character varying, 'seven_meter_won'::character varying, 'time_over'::character varying]::text[])", name='ck_match_possessions_result'),
        CheckConstraint('start_period_number >= 1', name='ck_match_possessions_start_period'),
        CheckConstraint('start_time_seconds >= 0', name='ck_match_possessions_start_time'),
        ForeignKeyConstraint(['match_id'], ['matches.id'], ondelete='CASCADE', name='fk_match_possessions_match_id'),
        ForeignKeyConstraint(['team_id'], ['teams.id'], ondelete='RESTRICT', name='fk_match_possessions_team_id'),
        PrimaryKeyConstraint('id', name='pk_match_possessions'),
        Index('ix_match_possessions_match_id', 'match_id'),
        Index('ix_match_possessions_team_id', 'team_id')
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    match_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    team_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    start_period_number: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    start_time_seconds: Mapped[int] = mapped_column(Integer, nullable=False)
    end_period_number: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    end_time_seconds: Mapped[int] = mapped_column(Integer, nullable=False)
    start_score_our: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    start_score_opponent: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    end_score_our: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    end_score_opponent: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    result: Mapped[str] = mapped_column(String(32), nullable=False)

    match: Mapped['Matches'] = relationship('Matches', back_populates='match_possessions')
    team: Mapped['Teams'] = relationship('Teams', back_populates='match_possessions')
    match_events: Mapped[list['MatchEvents']] = relationship('MatchEvents', back_populates='possession')


class MatchRoster(Base):
    __tablename__ = 'match_roster'
    __table_args__ = (
        CheckConstraint('jersey_number > 0', name='ck_match_roster_jersey'),
        ForeignKeyConstraint(['athlete_id'], ['athletes.id'], ondelete='RESTRICT', name='fk_match_roster_athlete_id'),
        ForeignKeyConstraint(['match_id'], ['matches.id'], ondelete='CASCADE', name='fk_match_roster_match_id'),
        ForeignKeyConstraint(['team_id'], ['teams.id'], ondelete='RESTRICT', name='fk_match_roster_team_id'),
        PrimaryKeyConstraint('id', name='pk_match_roster'),
        Index('ix_match_roster_athlete_id', 'athlete_id'),
        Index('ix_match_roster_athlete_match', 'athlete_id', 'match_id'),
        Index('ix_match_roster_match_id', 'match_id')
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    match_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    team_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    athlete_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    jersey_number: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    is_goalkeeper: Mapped[bool] = mapped_column(Boolean, nullable=False)
    is_available: Mapped[bool] = mapped_column(Boolean, nullable=False)
    is_starting: Mapped[Optional[bool]] = mapped_column(Boolean)
    notes: Mapped[Optional[str]] = mapped_column(Text)

    athlete: Mapped['Athletes'] = relationship('Athletes', back_populates='match_roster')
    match: Mapped['Matches'] = relationship('Matches', back_populates='match_roster')
    team: Mapped['Teams'] = relationship('Teams', back_populates='match_roster')


class MatchTeams(Base):
    __tablename__ = 'match_teams'
    __table_args__ = (
        ForeignKeyConstraint(['match_id'], ['matches.id'], ondelete='CASCADE', name='fk_match_teams_match_id'),
        ForeignKeyConstraint(['team_id'], ['teams.id'], ondelete='RESTRICT', name='fk_match_teams_team_id'),
        PrimaryKeyConstraint('id', name='pk_match_teams'),
        Index('ix_match_teams_match_id', 'match_id'),
        Index('ix_match_teams_team_id', 'team_id')
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    match_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    team_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    is_home: Mapped[bool] = mapped_column(Boolean, nullable=False)
    is_our_team: Mapped[bool] = mapped_column(Boolean, nullable=False)

    match: Mapped['Matches'] = relationship('Matches', back_populates='match_teams')
    team: Mapped['Teams'] = relationship('Teams', back_populates='match_teams')


class SessionTemplates(Base):
    __tablename__ = 'session_templates'
    __table_args__ = (
        CheckConstraint('(focus_attack_positional_pct + focus_defense_positional_pct + focus_transition_offense_pct + focus_transition_defense_pct + focus_attack_technical_pct + focus_defense_technical_pct + focus_physical_pct) <= 120::numeric', name='chk_session_templates_total_focus'),
        CheckConstraint("icon::text = ANY (ARRAY['target'::character varying, 'activity'::character varying, 'bar-chart'::character varying, 'shield'::character varying, 'zap'::character varying, 'flame'::character varying]::text[])", name='chk_session_templates_icon'),
        ForeignKeyConstraint(['created_by_membership_id'], ['org_memberships.id'], ondelete='SET NULL', name='session_templates_created_by_membership_id_fkey'),
        ForeignKeyConstraint(['org_id'], ['organizations.id'], ondelete='CASCADE', name='session_templates_org_id_fkey'),
        PrimaryKeyConstraint('id', name='session_templates_pkey'),
        UniqueConstraint('org_id', 'name', name='uq_session_templates_org_name'),
        Index('idx_session_templates_active', 'is_active'),
        Index('idx_session_templates_org_favorite', 'org_id', 'is_favorite', 'name')
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    org_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    icon: Mapped[str] = mapped_column(String(20), nullable=False, server_default=text("'target'::character varying"))
    focus_attack_positional_pct: Mapped[decimal.Decimal] = mapped_column(Numeric(5, 2), nullable=False, server_default=text("'0'::numeric"))
    focus_defense_positional_pct: Mapped[decimal.Decimal] = mapped_column(Numeric(5, 2), nullable=False, server_default=text("'0'::numeric"))
    focus_transition_offense_pct: Mapped[decimal.Decimal] = mapped_column(Numeric(5, 2), nullable=False, server_default=text("'0'::numeric"))
    focus_transition_defense_pct: Mapped[decimal.Decimal] = mapped_column(Numeric(5, 2), nullable=False, server_default=text("'0'::numeric"))
    focus_attack_technical_pct: Mapped[decimal.Decimal] = mapped_column(Numeric(5, 2), nullable=False, server_default=text("'0'::numeric"))
    focus_defense_technical_pct: Mapped[decimal.Decimal] = mapped_column(Numeric(5, 2), nullable=False, server_default=text("'0'::numeric"))
    focus_physical_pct: Mapped[decimal.Decimal] = mapped_column(Numeric(5, 2), nullable=False, server_default=text("'0'::numeric"))
    is_favorite: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    description: Mapped[Optional[str]] = mapped_column(Text)
    created_by_membership_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)

    created_by_membership: Mapped[Optional['OrgMemberships']] = relationship('OrgMemberships', back_populates='session_templates')
    org: Mapped['Organizations'] = relationship('Organizations', back_populates='session_templates')


class TeamMemberships(Base):
    __tablename__ = 'team_memberships'
    __table_args__ = (
        CheckConstraint("status = ANY (ARRAY['pendente'::text, 'ativo'::text, 'inativo'::text])", name='check_team_memberships_status'),
        ForeignKeyConstraint(['org_membership_id'], ['org_memberships.id'], ondelete='SET NULL', name='team_memberships_org_membership_id_fkey'),
        ForeignKeyConstraint(['person_id'], ['persons.id'], ondelete='CASCADE', name='team_memberships_person_id_fkey'),
        ForeignKeyConstraint(['team_id'], ['teams.id'], ondelete='CASCADE', name='team_memberships_team_id_fkey'),
        PrimaryKeyConstraint('id', name='team_memberships_pkey'),
        Index('idx_team_memberships_active', 'team_id', 'status', 'end_at'),
        Index('idx_team_memberships_org_membership_id', 'org_membership_id'),
        Index('idx_team_memberships_person_id', 'person_id'),
        Index('idx_team_memberships_person_team_active', 'person_id', 'team_id', unique=True),
        Index('idx_team_memberships_status', 'status'),
        Index('idx_team_memberships_team_active', 'team_id', 'status'),
        Index('idx_team_memberships_team_id', 'team_id')
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    person_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    team_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    start_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    status: Mapped[str] = mapped_column(Text, nullable=False, server_default=text("'pendente'::text"))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    resend_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'))
    org_membership_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    end_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    deleted_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    deleted_reason: Mapped[Optional[str]] = mapped_column(Text)

    org_membership: Mapped[Optional['OrgMemberships']] = relationship('OrgMemberships', back_populates='team_memberships')
    person: Mapped['Persons'] = relationship('Persons', back_populates='team_memberships')
    team: Mapped['Teams'] = relationship('Teams', back_populates='team_memberships')


class TrainingMicrocycles(Base):
    __tablename__ = 'training_microcycles'
    __table_args__ = (
        CheckConstraint('week_start < week_end', name='check_microcycle_dates'),
        ForeignKeyConstraint(['created_by_user_id'], ['users.id'], name='training_microcycles_created_by_user_id_fkey'),
        ForeignKeyConstraint(['cycle_id'], ['training_cycles.id'], name='training_microcycles_cycle_id_fkey'),
        ForeignKeyConstraint(['organization_id'], ['organizations.id'], name='training_microcycles_organization_id_fkey'),
        ForeignKeyConstraint(['team_id'], ['teams.id'], name='training_microcycles_team_id_fkey'),
        PrimaryKeyConstraint('id', name='training_microcycles_pkey'),
        Index('idx_training_microcycles_cycle', 'cycle_id'),
        Index('idx_training_microcycles_dates', 'week_start', 'week_end'),
        Index('idx_training_microcycles_org', 'organization_id'),
        Index('idx_training_microcycles_team', 'team_id')
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    organization_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    team_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    week_start: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    week_end: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    created_by_user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    cycle_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    planned_focus_attack_positional_pct: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    planned_focus_defense_positional_pct: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    planned_focus_transition_offense_pct: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    planned_focus_transition_defense_pct: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    planned_focus_attack_technical_pct: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    planned_focus_defense_technical_pct: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    planned_focus_physical_pct: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    planned_weekly_load: Mapped[Optional[int]] = mapped_column(Integer)
    microcycle_type: Mapped[Optional[str]] = mapped_column(String)
    notes: Mapped[Optional[str]] = mapped_column(Text)
    deleted_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    deleted_reason: Mapped[Optional[str]] = mapped_column(Text)

    created_by_user: Mapped['Users'] = relationship('Users', back_populates='training_microcycles')
    cycle: Mapped[Optional['TrainingCycles']] = relationship('TrainingCycles', back_populates='training_microcycles')
    organization: Mapped['Organizations'] = relationship('Organizations', back_populates='training_microcycles')
    team: Mapped['Teams'] = relationship('Teams', back_populates='training_microcycles')
    training_analytics_cache: Mapped[list['TrainingAnalyticsCache']] = relationship('TrainingAnalyticsCache', back_populates='microcycle')
    training_sessions: Mapped[list['TrainingSessions']] = relationship('TrainingSessions', back_populates='microcycle')


class MatchEvents(Base):
    __tablename__ = 'match_events'
    __table_args__ = (
        CheckConstraint('game_time_seconds >= 0', name='ck_match_events_time'),
        CheckConstraint('period_number >= 1', name='ck_match_events_period'),
        CheckConstraint('score_opponent >= 0', name='ck_match_events_score_opponent'),
        CheckConstraint('score_our >= 0', name='ck_match_events_score_our'),
        CheckConstraint("source::text = ANY (ARRAY['live'::character varying, 'video'::character varying, 'post_game_correction'::character varying]::text[])", name='ck_match_events_source'),
        CheckConstraint('x_coord IS NULL OR x_coord >= 0::numeric AND x_coord <= 100::numeric', name='ck_match_events_x_coord'),
        CheckConstraint('y_coord IS NULL OR y_coord >= 0::numeric AND y_coord <= 100::numeric', name='ck_match_events_y_coord'),
        ForeignKeyConstraint(['advantage_state'], ['advantage_states.code'], ondelete='RESTRICT', name='fk_match_events_advantage_state'),
        ForeignKeyConstraint(['assisting_athlete_id'], ['athletes.id'], ondelete='RESTRICT', name='fk_match_events_assisting_athlete_id'),
        ForeignKeyConstraint(['athlete_id'], ['athletes.id'], ondelete='RESTRICT', name='fk_match_events_athlete_id'),
        ForeignKeyConstraint(['created_by_user_id'], ['users.id'], ondelete='RESTRICT', name='fk_match_events_created_by_user_id'),
        ForeignKeyConstraint(['event_subtype'], ['event_subtypes.code'], ondelete='RESTRICT', name='fk_match_events_event_subtype'),
        ForeignKeyConstraint(['event_type'], ['event_types.code'], ondelete='RESTRICT', name='fk_match_events_event_type'),
        ForeignKeyConstraint(['match_id'], ['matches.id'], ondelete='CASCADE', name='fk_match_events_match_id'),
        ForeignKeyConstraint(['opponent_team_id'], ['teams.id'], ondelete='RESTRICT', name='fk_match_events_opponent_team_id'),
        ForeignKeyConstraint(['phase_of_play'], ['phases_of_play.code'], ondelete='RESTRICT', name='fk_match_events_phase_of_play'),
        ForeignKeyConstraint(['possession_id'], ['match_possessions.id'], ondelete='SET NULL', name='fk_match_events_possession_id'),
        ForeignKeyConstraint(['related_event_id'], ['match_events.id'], ondelete='SET NULL', name='fk_match_events_related_event_id'),
        ForeignKeyConstraint(['secondary_athlete_id'], ['athletes.id'], ondelete='RESTRICT', name='fk_match_events_secondary_athlete_id'),
        ForeignKeyConstraint(['team_id'], ['teams.id'], ondelete='RESTRICT', name='fk_match_events_team_id'),
        PrimaryKeyConstraint('id', name='pk_match_events'),
        Index('ix_match_events_athlete_id', 'athlete_id'),
        Index('ix_match_events_event_type', 'event_type'),
        Index('ix_match_events_match_id', 'match_id'),
        Index('ix_match_events_phase_of_play', 'phase_of_play'),
        Index('ix_match_events_team_id', 'team_id')
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    match_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    team_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    period_number: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    game_time_seconds: Mapped[int] = mapped_column(Integer, nullable=False)
    phase_of_play: Mapped[str] = mapped_column(String(32), nullable=False)
    advantage_state: Mapped[str] = mapped_column(String(32), nullable=False)
    score_our: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    score_opponent: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    event_type: Mapped[str] = mapped_column(String(64), nullable=False)
    outcome: Mapped[str] = mapped_column(String(64), nullable=False)
    is_shot: Mapped[bool] = mapped_column(Boolean, nullable=False)
    is_goal: Mapped[bool] = mapped_column(Boolean, nullable=False)
    source: Mapped[str] = mapped_column(String(32), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    created_by_user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    opponent_team_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    athlete_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    assisting_athlete_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    secondary_athlete_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    possession_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    event_subtype: Mapped[Optional[str]] = mapped_column(String(64))
    x_coord: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    y_coord: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    related_event_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    notes: Mapped[Optional[str]] = mapped_column(Text)

    advantage_states: Mapped['AdvantageStates'] = relationship('AdvantageStates', back_populates='match_events')
    assisting_athlete: Mapped[Optional['Athletes']] = relationship('Athletes', foreign_keys=[assisting_athlete_id], back_populates='match_events')
    athlete: Mapped[Optional['Athletes']] = relationship('Athletes', foreign_keys=[athlete_id], back_populates='match_events_')
    created_by_user: Mapped['Users'] = relationship('Users', back_populates='match_events')
    event_subtypes: Mapped[Optional['EventSubtypes']] = relationship('EventSubtypes', back_populates='match_events')
    event_types: Mapped['EventTypes'] = relationship('EventTypes', back_populates='match_events')
    match: Mapped['Matches'] = relationship('Matches', back_populates='match_events')
    opponent_team: Mapped[Optional['Teams']] = relationship('Teams', foreign_keys=[opponent_team_id], back_populates='match_events')
    phases_of_play: Mapped['PhasesOfPlay'] = relationship('PhasesOfPlay', back_populates='match_events')
    possession: Mapped[Optional['MatchPossessions']] = relationship('MatchPossessions', back_populates='match_events')
    related_event: Mapped[Optional['MatchEvents']] = relationship('MatchEvents', remote_side=[id], back_populates='related_event_reverse')
    related_event_reverse: Mapped[list['MatchEvents']] = relationship('MatchEvents', remote_side=[related_event_id], back_populates='related_event')
    secondary_athlete: Mapped[Optional['Athletes']] = relationship('Athletes', foreign_keys=[secondary_athlete_id], back_populates='match_events1')
    team: Mapped['Teams'] = relationship('Teams', foreign_keys=[team_id], back_populates='match_events_')


class TrainingAnalyticsCache(Base):
    __tablename__ = 'training_analytics_cache'
    __table_args__ = (
        CheckConstraint("granularity::text = ANY (ARRAY['weekly'::character varying, 'monthly'::character varying]::text[])", name='ck_training_analytics_cache_granularity'),
        ForeignKeyConstraint(['microcycle_id'], ['training_microcycles.id'], ondelete='CASCADE', name='training_analytics_cache_microcycle_id_fkey'),
        ForeignKeyConstraint(['team_id'], ['teams.id'], ondelete='CASCADE', name='training_analytics_cache_team_id_fkey'),
        PrimaryKeyConstraint('id', name='training_analytics_cache_pkey'),
        UniqueConstraint('team_id', 'microcycle_id', 'month', 'granularity', name='uq_training_analytics_cache_lookup'),
        Index('idx_analytics_lookup', 'team_id', 'granularity', 'cache_dirty')
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    team_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    granularity: Mapped[str] = mapped_column(String(20), nullable=False)
    cache_dirty: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'))
    microcycle_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    month: Mapped[Optional[datetime.date]] = mapped_column(Date)
    total_sessions: Mapped[Optional[int]] = mapped_column(Integer)
    avg_focus_attack_positional_pct: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    avg_focus_defense_positional_pct: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    avg_focus_transition_offense_pct: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    avg_focus_transition_defense_pct: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    avg_focus_attack_technical_pct: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    avg_focus_defense_technical_pct: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    avg_focus_physical_pct: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    avg_rpe: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    avg_internal_load: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(10, 2))
    total_internal_load: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(12, 2))
    attendance_rate: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    wellness_response_rate_pre: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    wellness_response_rate_post: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    athletes_with_badges_count: Mapped[Optional[int]] = mapped_column(Integer)
    deviation_count: Mapped[Optional[int]] = mapped_column(Integer)
    threshold_mean: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(10, 2))
    threshold_stddev: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(10, 2))
    calculated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))

    microcycle: Mapped[Optional['TrainingMicrocycles']] = relationship('TrainingMicrocycles', back_populates='training_analytics_cache')
    team: Mapped['Teams'] = relationship('Teams', back_populates='training_analytics_cache')


class TrainingSessions(Base):
    __tablename__ = 'training_sessions'
    __table_args__ = (
        CheckConstraint('(COALESCE(focus_attack_positional_pct, 0::numeric) + COALESCE(focus_defense_positional_pct, 0::numeric) + COALESCE(focus_transition_offense_pct, 0::numeric) + COALESCE(focus_transition_defense_pct, 0::numeric) + COALESCE(focus_attack_technical_pct, 0::numeric) + COALESCE(focus_defense_technical_pct, 0::numeric) + COALESCE(focus_physical_pct, 0::numeric)) <= 120::numeric', name='ck_training_sessions_focus_total_sum'),
        CheckConstraint('deleted_at IS NULL AND deleted_reason IS NULL OR deleted_at IS NOT NULL AND deleted_reason IS NOT NULL', name='ck_training_sessions_deleted_reason'),
        CheckConstraint('focus_attack_positional_pct IS NULL OR focus_attack_positional_pct >= 0::numeric AND focus_attack_positional_pct <= 100::numeric', name='ck_training_sessions_focus_attack_positional_range'),
        CheckConstraint('focus_attack_technical_pct IS NULL OR focus_attack_technical_pct >= 0::numeric AND focus_attack_technical_pct <= 100::numeric', name='ck_training_sessions_focus_attack_technical_range'),
        CheckConstraint('focus_defense_positional_pct IS NULL OR focus_defense_positional_pct >= 0::numeric AND focus_defense_positional_pct <= 100::numeric', name='ck_training_sessions_focus_defense_positional_range'),
        CheckConstraint('focus_defense_technical_pct IS NULL OR focus_defense_technical_pct >= 0::numeric AND focus_defense_technical_pct <= 100::numeric', name='ck_training_sessions_focus_defense_technical_range'),
        CheckConstraint('focus_physical_pct IS NULL OR focus_physical_pct >= 0::numeric AND focus_physical_pct <= 100::numeric', name='ck_training_sessions_focus_physical_range'),
        CheckConstraint('focus_transition_defense_pct IS NULL OR focus_transition_defense_pct >= 0::numeric AND focus_transition_defense_pct <= 100::numeric', name='ck_training_sessions_focus_transition_defense_range'),
        CheckConstraint('focus_transition_offense_pct IS NULL OR focus_transition_offense_pct >= 0::numeric AND focus_transition_offense_pct <= 100::numeric', name='ck_training_sessions_focus_transition_offense_range'),
        CheckConstraint('group_climate IS NULL OR group_climate >= 1 AND group_climate <= 5', name='ck_training_sessions_climate'),
        CheckConstraint('intensity_target IS NULL OR intensity_target >= 1 AND intensity_target <= 5', name='ck_training_sessions_intensity'),
        CheckConstraint('phase_focus_attack = ((COALESCE(focus_attack_positional_pct, 0::numeric) + COALESCE(focus_attack_technical_pct, 0::numeric)) >= 5::numeric)', name='ck_phase_focus_attack_consistency'),
        CheckConstraint('phase_focus_defense = ((COALESCE(focus_defense_positional_pct, 0::numeric) + COALESCE(focus_defense_technical_pct, 0::numeric)) >= 5::numeric)', name='ck_phase_focus_defense_consistency'),
        CheckConstraint('phase_focus_transition_defense = (COALESCE(focus_transition_defense_pct, 0::numeric) >= 5::numeric)', name='ck_phase_focus_transition_defense_consistency'),
        CheckConstraint('phase_focus_transition_offense = (COALESCE(focus_transition_offense_pct, 0::numeric) >= 5::numeric)', name='ck_phase_focus_transition_offense_consistency'),
        CheckConstraint("session_type::text = ANY (ARRAY['quadra'::character varying, 'fisico'::character varying, 'video'::character varying, 'reuniao'::character varying, 'teste'::character varying]::text[])", name='ck_training_sessions_type'),
        CheckConstraint("status::text = ANY (ARRAY['draft'::character varying, 'scheduled'::character varying, 'in_progress'::character varying, 'closed'::character varying, 'readonly'::character varying]::text[])", name='check_training_session_status'),
        ForeignKeyConstraint(['closed_by_user_id'], ['users.id'], name='fk_training_sessions_closed_by'),
        ForeignKeyConstraint(['created_by_user_id'], ['users.id'], ondelete='RESTRICT', name='fk_training_sessions_created_by_user_id'),
        ForeignKeyConstraint(['microcycle_id'], ['training_microcycles.id'], name='fk_training_sessions_microcycle'),
        ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='RESTRICT', name='fk_training_sessions_organization_id'),
        ForeignKeyConstraint(['season_id'], ['seasons.id'], ondelete='RESTRICT', name='fk_training_sessions_season_id'),
        ForeignKeyConstraint(['team_id'], ['teams.id'], ondelete='RESTRICT', name='fk_training_sessions_team_id'),
        PrimaryKeyConstraint('id', name='pk_training_sessions'),
        Index('idx_sessions_team_date', 'team_id', 'session_at'),
        Index('idx_training_sessions_deviation_flag', 'planning_deviation_flag'),
        Index('idx_training_sessions_microcycle', 'microcycle_id'),
        Index('idx_training_sessions_org', 'organization_id', 'deleted_at'),
        Index('idx_training_sessions_status', 'status'),
        Index('idx_training_sessions_team_date', 'team_id', 'session_at', 'deleted_at'),
        Index('ix_training_sessions_organization_id', 'organization_id'),
        Index('ix_training_sessions_season_id', 'season_id'),
        Index('ix_training_sessions_session_at', 'session_at'),
        Index('ix_training_sessions_team_date_active', 'team_id', 'session_at'),
        Index('ix_training_sessions_team_id', 'team_id'),
        Index('ix_training_sessions_team_season_date', 'team_id', 'season_id', 'session_at')
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    organization_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    session_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False)
    session_type: Mapped[str] = mapped_column(String(32), nullable=False)
    phase_focus_defense: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    phase_focus_attack: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    phase_focus_transition_offense: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    phase_focus_transition_defense: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    created_by_user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    status: Mapped[str] = mapped_column(String, nullable=False, server_default=text("'''draft'''::character varying"))
    planning_deviation_flag: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    team_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    season_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    duration_planned_minutes: Mapped[Optional[int]] = mapped_column(SmallInteger)
    location: Mapped[Optional[str]] = mapped_column(String(120))
    main_objective: Mapped[Optional[str]] = mapped_column(String(255))
    secondary_objective: Mapped[Optional[str]] = mapped_column(Text)
    planned_load: Mapped[Optional[int]] = mapped_column(SmallInteger)
    group_climate: Mapped[Optional[int]] = mapped_column(SmallInteger)
    notes: Mapped[Optional[str]] = mapped_column(Text)
    intensity_target: Mapped[Optional[int]] = mapped_column(SmallInteger)
    session_block: Mapped[Optional[str]] = mapped_column(String(32))
    deleted_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    deleted_reason: Mapped[Optional[str]] = mapped_column(Text)
    focus_attack_positional_pct: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    focus_defense_positional_pct: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    focus_transition_offense_pct: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    focus_transition_defense_pct: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    focus_attack_technical_pct: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    focus_defense_technical_pct: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    focus_physical_pct: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    microcycle_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    closed_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    closed_by_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    deviation_justification: Mapped[Optional[str]] = mapped_column(Text)

    closed_by_user: Mapped[Optional['Users']] = relationship('Users', foreign_keys=[closed_by_user_id], back_populates='training_sessions')
    created_by_user: Mapped['Users'] = relationship('Users', foreign_keys=[created_by_user_id], back_populates='training_sessions_')
    microcycle: Mapped[Optional['TrainingMicrocycles']] = relationship('TrainingMicrocycles', back_populates='training_sessions')
    organization: Mapped['Organizations'] = relationship('Organizations', back_populates='training_sessions')
    season: Mapped[Optional['Seasons']] = relationship('Seasons', back_populates='training_sessions')
    team: Mapped[Optional['Teams']] = relationship('Teams', back_populates='training_sessions')
    attendance: Mapped[list['Attendance']] = relationship('Attendance', back_populates='training_session')
    training_session_exercises: Mapped[list['TrainingSessionExercises']] = relationship('TrainingSessionExercises', back_populates='session')
    training_suggestions: Mapped[list['TrainingSuggestions']] = relationship('TrainingSuggestions', back_populates='origin_session')
    wellness_post: Mapped[list['WellnessPost']] = relationship('WellnessPost', back_populates='training_session')
    wellness_pre: Mapped[list['WellnessPre']] = relationship('WellnessPre', back_populates='training_session')
    wellness_reminders: Mapped[list['WellnessReminders']] = relationship('WellnessReminders', back_populates='training_session')


class Attendance(Base):
    __tablename__ = 'attendance'
    __table_args__ = (
        CheckConstraint('deleted_at IS NULL AND deleted_reason IS NULL OR deleted_at IS NOT NULL AND deleted_reason IS NOT NULL', name='ck_attendance_deleted_reason'),
        CheckConstraint("participation_type IS NULL OR (participation_type::text = ANY (ARRAY['full'::character varying, 'partial'::character varying, 'adapted'::character varying, 'did_not_train'::character varying]::text[]))", name='ck_attendance_participation_type'),
        CheckConstraint("presence_status::text = ANY (ARRAY['present'::character varying, 'absent'::character varying]::text[])", name='ck_attendance_status'),
        CheckConstraint("reason_absence IS NULL OR (reason_absence::text = ANY (ARRAY['medico'::character varying, 'escola'::character varying, 'familiar'::character varying, 'opcional'::character varying, 'outro'::character varying]::text[]))", name='ck_attendance_reason'),
        CheckConstraint("source::text <> 'correction'::text OR source::text = 'correction'::text AND correction_by_user_id IS NOT NULL AND correction_at IS NOT NULL", name='ck_attendance_correction_fields'),
        CheckConstraint("source::text = ANY (ARRAY['manual'::character varying, 'import'::character varying, 'correction'::character varying]::text[])", name='ck_attendance_source'),
        ForeignKeyConstraint(['athlete_id'], ['athletes.id'], ondelete='RESTRICT', name='fk_attendance_athlete_id'),
        ForeignKeyConstraint(['correction_by_user_id'], ['users.id'], ondelete='SET NULL', name='attendance_correction_by_user_id_fkey'),
        ForeignKeyConstraint(['created_by_user_id'], ['users.id'], ondelete='RESTRICT', name='fk_attendance_created_by_user_id'),
        ForeignKeyConstraint(['team_registration_id'], ['team_registrations.id'], ondelete='RESTRICT', name='fk_attendance_team_registration_id'),
        ForeignKeyConstraint(['training_session_id'], ['training_sessions.id'], ondelete='RESTRICT', name='fk_attendance_training_session_id'),
        PrimaryKeyConstraint('id', name='pk_attendance'),
        Index('idx_attendance_corrections', 'correction_by_user_id', 'correction_at'),
        Index('idx_attendance_session', 'training_session_id'),
        Index('ix_attendance_athlete_id', 'athlete_id'),
        Index('ix_attendance_athlete_session_active', 'athlete_id', 'training_session_id'),
        Index('ix_attendance_training_session_id', 'training_session_id')
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    training_session_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    team_registration_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    athlete_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    presence_status: Mapped[str] = mapped_column(String(32), nullable=False)
    source: Mapped[str] = mapped_column(String(32), nullable=False, server_default=text("'manual'::character varying"))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    created_by_user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    minutes_effective: Mapped[Optional[int]] = mapped_column(SmallInteger)
    comment: Mapped[Optional[str]] = mapped_column(Text)
    participation_type: Mapped[Optional[str]] = mapped_column(String(32))
    reason_absence: Mapped[Optional[str]] = mapped_column(String(32))
    is_medical_restriction: Mapped[Optional[bool]] = mapped_column(Boolean, server_default=text('false'))
    deleted_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    deleted_reason: Mapped[Optional[str]] = mapped_column(Text)
    correction_by_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    correction_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))

    athlete: Mapped['Athletes'] = relationship('Athletes', back_populates='attendance')
    correction_by_user: Mapped[Optional['Users']] = relationship('Users', foreign_keys=[correction_by_user_id], back_populates='attendance')
    created_by_user: Mapped['Users'] = relationship('Users', foreign_keys=[created_by_user_id], back_populates='attendance_')
    team_registration: Mapped['TeamRegistrations'] = relationship('TeamRegistrations', back_populates='attendance')
    training_session: Mapped['TrainingSessions'] = relationship('TrainingSessions', back_populates='attendance')


class TrainingSessionExercises(Base):
    __tablename__ = 'training_session_exercises'
    __table_args__ = (
        CheckConstraint('duration_minutes IS NULL OR duration_minutes >= 0', name='ck_session_exercises_duration_positive'),
        CheckConstraint('order_index >= 0', name='ck_session_exercises_order_positive'),
        ForeignKeyConstraint(['exercise_id'], ['exercises.id'], ondelete='RESTRICT', name='training_session_exercises_exercise_id_fkey'),
        ForeignKeyConstraint(['session_id'], ['training_sessions.id'], ondelete='CASCADE', name='training_session_exercises_session_id_fkey'),
        PrimaryKeyConstraint('id', name='training_session_exercises_pkey'),
        Index('idx_session_exercises_exercise', 'exercise_id'),
        Index('idx_session_exercises_session_order', 'session_id', 'order_index', 'deleted_at'),
        Index('idx_session_exercises_session_order_unique', 'session_id', 'order_index', unique=True)
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    session_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    exercise_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    duration_minutes: Mapped[Optional[int]] = mapped_column(SmallInteger)
    notes: Mapped[Optional[str]] = mapped_column(Text)
    deleted_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))

    exercise: Mapped['Exercises'] = relationship('Exercises', back_populates='training_session_exercises')
    session: Mapped['TrainingSessions'] = relationship('TrainingSessions', back_populates='training_session_exercises')


class TrainingSuggestions(Base):
    __tablename__ = 'training_suggestions'
    __table_args__ = (
        CheckConstraint("status::text = ANY (ARRAY['pending'::character varying, 'applied'::character varying, 'dismissed'::character varying]::text[])", name='ck_training_suggestions_status'),
        CheckConstraint("type::text = ANY (ARRAY['compensation'::character varying, 'reduce_next_week'::character varying]::text[])", name='ck_training_suggestions_type'),
        ForeignKeyConstraint(['origin_session_id'], ['training_sessions.id'], ondelete='CASCADE', name='training_suggestions_origin_session_id_fkey'),
        ForeignKeyConstraint(['team_id'], ['teams.id'], ondelete='CASCADE', name='training_suggestions_team_id_fkey'),
        PrimaryKeyConstraint('id', name='training_suggestions_pkey')
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    team_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, server_default=text("'pending'::character varying"))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    origin_session_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    target_session_ids: Mapped[Optional[list[uuid.UUID]]] = mapped_column(ARRAY(Uuid()))
    recommended_adjustment_pct: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    reason: Mapped[Optional[str]] = mapped_column(Text)
    applied_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    dismissed_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    dismissal_reason: Mapped[Optional[str]] = mapped_column(Text)

    origin_session: Mapped[Optional['TrainingSessions']] = relationship('TrainingSessions', back_populates='training_suggestions')
    team: Mapped['Teams'] = relationship('Teams', back_populates='training_suggestions')


class WellnessPost(Base):
    __tablename__ = 'wellness_post'
    __table_args__ = (
        CheckConstraint('deleted_at IS NULL AND deleted_reason IS NULL OR deleted_at IS NOT NULL AND deleted_reason IS NOT NULL', name='ck_wellness_post_deleted_reason'),
        CheckConstraint('fatigue_after >= 0 AND fatigue_after <= 10', name='ck_wellness_post_fatigue'),
        CheckConstraint('mood_after >= 0 AND mood_after <= 10', name='ck_wellness_post_mood'),
        CheckConstraint('muscle_soreness_after IS NULL OR muscle_soreness_after >= 0 AND muscle_soreness_after <= 10', name='ck_wellness_post_soreness'),
        CheckConstraint('perceived_intensity IS NULL OR perceived_intensity >= 1 AND perceived_intensity <= 5', name='ck_wellness_post_intensity'),
        CheckConstraint('session_rpe >= 0 AND session_rpe <= 10', name='ck_wellness_post_rpe'),
        ForeignKeyConstraint(['athlete_id'], ['athletes.id'], ondelete='RESTRICT', name='fk_wellness_post_athlete_id'),
        ForeignKeyConstraint(['created_by_user_id'], ['users.id'], ondelete='RESTRICT', name='fk_wellness_post_created_by_user_id'),
        ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='RESTRICT', name='fk_wellness_post_organization_id'),
        ForeignKeyConstraint(['training_session_id'], ['training_sessions.id'], ondelete='RESTRICT', name='fk_wellness_post_training_session_id'),
        PrimaryKeyConstraint('id', name='pk_wellness_post'),
        Index('idx_wellness_athlete_date', 'athlete_id', 'filled_at'),
        Index('ix_wellness_post_athlete_id', 'athlete_id'),
        Index('ix_wellness_post_athlete_session_active', 'athlete_id', 'training_session_id', 'created_at'),
        Index('ix_wellness_post_training_session_id', 'training_session_id'),
        Index('ux_wellness_post_session_athlete', 'training_session_id', 'athlete_id', unique=True)
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    organization_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    training_session_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    athlete_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    session_rpe: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    fatigue_after: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    mood_after: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    filled_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    created_by_user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    muscle_soreness_after: Mapped[Optional[int]] = mapped_column(SmallInteger)
    notes: Mapped[Optional[str]] = mapped_column(Text)
    perceived_intensity: Mapped[Optional[int]] = mapped_column(SmallInteger)
    flag_medical_followup: Mapped[Optional[bool]] = mapped_column(Boolean, server_default=text('false'))
    deleted_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    deleted_reason: Mapped[Optional[str]] = mapped_column(Text)
    internal_load: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(10, 2), server_default=text('0'))
    minutes_effective: Mapped[Optional[int]] = mapped_column(SmallInteger)
    locked_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))

    athlete: Mapped['Athletes'] = relationship('Athletes', back_populates='wellness_post')
    created_by_user: Mapped['Users'] = relationship('Users', back_populates='wellness_post')
    organization: Mapped['Organizations'] = relationship('Organizations', back_populates='wellness_post')
    training_session: Mapped['TrainingSessions'] = relationship('TrainingSessions', back_populates='wellness_post')


class WellnessPre(Base):
    __tablename__ = 'wellness_pre'
    __table_args__ = (
        CheckConstraint('deleted_at IS NULL AND deleted_reason IS NULL OR deleted_at IS NOT NULL AND deleted_reason IS NOT NULL', name='ck_wellness_pre_deleted_reason'),
        CheckConstraint('fatigue_pre >= 0 AND fatigue_pre <= 10', name='ck_wellness_pre_fatigue'),
        CheckConstraint("menstrual_cycle_phase IS NULL OR (menstrual_cycle_phase::text = ANY (ARRAY['folicular'::character varying, 'lutea'::character varying, 'menstruacao'::character varying, 'nao_informa'::character varying]::text[]))", name='ck_wellness_pre_menstrual'),
        CheckConstraint('muscle_soreness >= 0 AND muscle_soreness <= 10', name='ck_wellness_pre_soreness'),
        CheckConstraint('readiness_score IS NULL OR readiness_score >= 0 AND readiness_score <= 10', name='ck_wellness_pre_readiness'),
        CheckConstraint('sleep_hours >= 0::numeric AND sleep_hours <= 24::numeric', name='ck_wellness_pre_sleep_hours'),
        CheckConstraint('sleep_quality >= 1 AND sleep_quality <= 5', name='ck_wellness_pre_sleep_quality'),
        CheckConstraint('stress_level >= 0 AND stress_level <= 10', name='ck_wellness_pre_stress'),
        ForeignKeyConstraint(['athlete_id'], ['athletes.id'], ondelete='RESTRICT', name='fk_wellness_pre_athlete_id'),
        ForeignKeyConstraint(['created_by_user_id'], ['users.id'], ondelete='RESTRICT', name='fk_wellness_pre_created_by_user_id'),
        ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='RESTRICT', name='fk_wellness_pre_organization_id'),
        ForeignKeyConstraint(['training_session_id'], ['training_sessions.id'], ondelete='RESTRICT', name='fk_wellness_pre_training_session_id'),
        PrimaryKeyConstraint('id', name='pk_wellness_pre'),
        Index('idx_wellness_session_athlete', 'training_session_id', 'athlete_id'),
        Index('ix_wellness_pre_athlete_id', 'athlete_id'),
        Index('ix_wellness_pre_training_session_id', 'training_session_id'),
        Index('ux_wellness_pre_session_athlete', 'training_session_id', 'athlete_id', unique=True)
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    organization_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    training_session_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    athlete_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    sleep_hours: Mapped[decimal.Decimal] = mapped_column(Numeric(4, 1), nullable=False)
    sleep_quality: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    fatigue_pre: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    stress_level: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    muscle_soreness: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    filled_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    created_by_user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    notes: Mapped[Optional[str]] = mapped_column(Text)
    menstrual_cycle_phase: Mapped[Optional[str]] = mapped_column(String(32))
    readiness_score: Mapped[Optional[int]] = mapped_column(SmallInteger)
    deleted_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    deleted_reason: Mapped[Optional[str]] = mapped_column(Text)
    locked_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))

    athlete: Mapped['Athletes'] = relationship('Athletes', back_populates='wellness_pre')
    created_by_user: Mapped['Users'] = relationship('Users', back_populates='wellness_pre')
    organization: Mapped['Organizations'] = relationship('Organizations', back_populates='wellness_pre')
    training_session: Mapped['TrainingSessions'] = relationship('TrainingSessions', back_populates='wellness_pre')


class WellnessReminders(Base):
    __tablename__ = 'wellness_reminders'
    __table_args__ = (
        ForeignKeyConstraint(['athlete_id'], ['athletes.id'], ondelete='CASCADE', name='wellness_reminders_athlete_id_fkey'),
        ForeignKeyConstraint(['training_session_id'], ['training_sessions.id'], ondelete='CASCADE', name='wellness_reminders_training_session_id_fkey'),
        PrimaryKeyConstraint('id', name='wellness_reminders_pkey'),
        UniqueConstraint('training_session_id', 'athlete_id', name='uq_wellness_reminders_session_athlete'),
        Index('idx_wellness_reminders_pending', 'training_session_id', 'athlete_id')
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    training_session_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    athlete_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    sent_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False)
    reminder_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'))
    responded_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    locked_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))

    athlete: Mapped['Athletes'] = relationship('Athletes', back_populates='wellness_reminders')
    training_session: Mapped['TrainingSessions'] = relationship('TrainingSessions', back_populates='wellness_reminders')
