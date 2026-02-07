import os
import sys
import pkgutil
import importlib
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from dotenv import load_dotenv
from alembic.operations import ops as alembic_ops

# Carregar .env
load_dotenv()

# Garantir que o root do repo está no path (Windows com espaço no caminho)
sys.path.append(os.getcwd())

from app.models.base import Base
# declarative base

# Importa todos os módulos em app.models para popular Base.metadata
import app.models as models_pkg
for _, modname, _ in pkgutil.iter_modules(models_pkg.__path__, models_pkg.__name__ + "."):
    importlib.import_module(modname)

target_metadata = Base.metadata

# Opcional: filtrar tabelas a comparar via env var
ONLY = {t.strip() for t in os.getenv("ALEMBIC_COMPARE_TABLES", "").split(",") if t.strip()}

# Modo apenas-scan: quando ativo, não gera arquivo de revisão mesmo que haja diffs
SCAN_ONLY = os.getenv("ALEMBIC_SCAN_ONLY", "").strip() == "1"

# -------------------------------------------------------------------
# Tabelas que existem no model mas NÃO no DB (parity scan ignora).
# Excluídas da comparação durante SCAN_ONLY para evitar
# "Detected added table" falsos positivos.
# -------------------------------------------------------------------
SKIP_MODEL_ONLY_TABLES = set()

# -------------------------------------------------------------------
# Tabelas que existem no DB mas NÃO têm ORM model (apenas stubs para FK).
# Excluídas da comparação para evitar diffs irrelevantes.
# -------------------------------------------------------------------
SKIP_STUB_ONLY_TABLES = {
    "alembic_version",  # tabela técnica de infraestrutura (migrations)
    "advantage_states",
    "event_types",
    "event_subtypes",
    "phases_of_play",
    "match_possessions",
}

# -------------------------------------------------------------------
# Stub tables para parity scan: tabelas de lookup referenciadas por
# models mas que não possuem ORM model próprio no projeto.
# Carregadas APENAS quando ALEMBIC_SCAN_ONLY=1 para evitar erros de
# NoReferencedTableError, sem impactar runtime da aplicação.
# -------------------------------------------------------------------
if SCAN_ONLY:
    from sqlalchemy import Table, Column, String, Boolean, SmallInteger, ForeignKey

    # advantage_states (PK: code)
    if "advantage_states" not in target_metadata.tables:
        Table(
            "advantage_states",
            target_metadata,
            Column("code", String(32), primary_key=True),
            Column("delta_players", SmallInteger, nullable=False),
            Column("description", String(255), nullable=True),
        )

    # event_types (PK: code)
    if "event_types" not in target_metadata.tables:
        Table(
            "event_types",
            target_metadata,
            Column("code", String(64), primary_key=True),
            Column("description", String(255), nullable=False),
            Column("is_shot", Boolean, nullable=False),
            Column("is_possession_ending", Boolean, nullable=False),
        )

    # event_subtypes (PK: code, FK: event_type_code -> event_types.code)
    if "event_subtypes" not in target_metadata.tables:
        Table(
            "event_subtypes",
            target_metadata,
            Column("code", String(64), primary_key=True),
            Column("event_type_code", String(64), ForeignKey("event_types.code"), nullable=False),
            Column("description", String(255), nullable=False),
        )

    # phases_of_play (PK: code)
    if "phases_of_play" not in target_metadata.tables:
        Table(
            "phases_of_play",
            target_metadata,
            Column("code", String(32), primary_key=True),
            Column("description", String(255), nullable=False),
        )

    # match_possessions (PK: id) - stub mínimo para FK resolution
    if "match_possessions" not in target_metadata.tables:
        from sqlalchemy.dialects.postgresql import UUID as PG_UUID
        Table(
            "match_possessions",
            target_metadata,
            Column("id", PG_UUID(as_uuid=True), primary_key=True),
        )


def include_object(obj, name, type_, reflected, compare_to):
    # Ignorar índices no autogenerate
    # Preserva índices unique (importante para unicidade), ignora os demais
    if type_ == "index":
        return bool(getattr(obj, "unique", False))

    # Skip tabelas model-only e stub-only durante parity scan
    if SCAN_ONLY:
        skip_tables = SKIP_MODEL_ONLY_TABLES | SKIP_STUB_ONLY_TABLES
        if type_ == "table" and name in skip_tables:
            return False
        parent = getattr(getattr(obj, "table", None), "name", None)
        if parent and parent in skip_tables:
            return False

    # Se quiser focar em uma tabela específica: ALEMBIC_COMPARE_TABLES=athletes,attendance
    if ONLY:
        if type_ == "table":
            return name in ONLY
        parent = getattr(getattr(obj, "table", None), "name", None)
        return (parent in ONLY) if parent else True

    # Sem filtro: ignora DB-only (reflected) quando não existe no metadata
    if reflected and compare_to is None:
        # para "table" e objetos que pertencem a uma tabela não mapeada
        if type_ == "table":
            return False
        parent = getattr(getattr(obj, "table", None), "name", None)
        if parent and parent not in target_metadata.tables:
            return False

    return True


def _is_comment_op(op) -> bool:
    # Tipos dependem da versão do Alembic; pega os que existirem.
    comment_types = (
        getattr(alembic_ops, "CreateTableCommentOp", None),
        getattr(alembic_ops, "DropTableCommentOp", None),
        getattr(alembic_ops, "CreateColumnCommentOp", None),
        getattr(alembic_ops, "DropColumnCommentOp", None),
    )
    comment_types = tuple(t for t in comment_types if t is not None)
    return isinstance(op, comment_types)


def _is_comment_only_alter_column(op) -> bool:
    if not isinstance(op, alembic_ops.AlterColumnOp):
        return False

    # 1) Se há qualquer modify_* (exceto modify_comment) que indique mudança estrutural
    modify_attrs = [a for a in dir(op) if a.startswith("modify_")]
    for a in modify_attrs:
        if a == "modify_comment":
            continue
        val = getattr(op, a, None)
        # Ignore métodos/descritores
        if callable(val):
            continue
        # Nenhum valor -> sem mudança
        if val is None:
            continue

        # - modify_nullable: considerar estrutural (mantido comportamento seguro)
        if a == "modify_nullable":
            return False

        # Para qualquer modify_* booleano: considerar estrutural tanto True quanto False,
        # exceto o sentinel conhecido: modify_server_default == False (Alembic usa False como sentinel)
        if isinstance(val, bool):
            if a == "modify_server_default" and val is False:
                continue
            return False

        # - modify_type / modify_name: qualquer non-None indica mudança estrutural
        if a in ("modify_type", "modify_name"):
            return False

        # Fallback: qualquer non-bool non-None também é estrutural
        return False

    # 2) Se alterou comentário explicitamente
    if getattr(op, "modify_comment", None) is not None:
        return True

    # 3) Caso comum: DB tem existing_comment e metadata não tem comment => autogen propõe remover comment
    existing_comment = getattr(op, "existing_comment", None)
    new_comment = getattr(op, "comment", None)

    if existing_comment is not None and new_comment is None:
        return True

    return False


def _filter_ops_list(ops_list):
    out = []
    for op in ops_list:
        # Recursão: ops por tabela
        if isinstance(op, alembic_ops.ModifyTableOps):
            op.ops = _filter_ops_list(op.ops)
            if op.ops:
                out.append(op)
            continue

        if _is_comment_op(op):
            continue

        if _is_comment_only_alter_column(op):
            continue

        out.append(op)

    return out


def process_revision_directives(context, revision, directives):
    if not directives:
        return

    script = directives[0]

    script.upgrade_ops.ops = _filter_ops_list(script.upgrade_ops.ops)
    script.downgrade_ops.ops = _filter_ops_list(script.downgrade_ops.ops)

    # Se estamos em modo apenas-scan, sempre descarta diretivas (não gera arquivo)
    if SCAN_ONLY:
        directives[:] = []
        return

    if not script.upgrade_ops.ops and not script.downgrade_ops.ops:
        directives[:] = []

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)


# Helper: normaliza/deriva uma URL compatível com psycopg2 a partir de vários formatos
def _normalize_sync_url(url: str) -> str:
    # aceita postgresql://, postgresql+asyncpg://, postgresql+psycopg2://, postgres://
    if url.startswith("postgresql+asyncpg://"):
        return url.replace("postgresql+asyncpg://", "postgresql+psycopg2://", 1)
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+psycopg2://", 1)
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+psycopg2://", 1)
    if url.startswith("postgresql+psycopg2://"):
        return url
    # fallback: se vier outro driver (ex: postgresql+pg8000://), troca esquema para psycopg2
    if url.startswith("postgresql+"):
        return "postgresql+psycopg2://" + url.split("://", 1)[1]
    return url


# Migrations devem usar DATABASE_URL_SYNC (psycopg2). Se não definido, tenta derivar de DATABASE_URL.
DATABASE_URL_SYNC = os.getenv("DATABASE_URL_SYNC")
if not DATABASE_URL_SYNC:
    base = os.getenv("DATABASE_URL")
    if base:
        DATABASE_URL_SYNC = _normalize_sync_url(base)

if not DATABASE_URL_SYNC:
    raise RuntimeError("DATABASE_URL_SYNC não definido e não foi possível derivar de DATABASE_URL. Configure .env com postgresql+psycopg2://...")

# variavel usada abaixo pelo resto do env.py para conectar/configurar Alembic
DATABASE_URL = DATABASE_URL_SYNC

def run_migrations_offline():
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
        include_object=include_object,
        process_revision_directives=process_revision_directives,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = DATABASE_URL

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            include_object=include_object,
            process_revision_directives=process_revision_directives,
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()