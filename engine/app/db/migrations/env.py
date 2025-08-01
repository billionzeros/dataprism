from logging.config import fileConfig
from app.settings.config import settings
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

try:
    from app.db.base_class import Base
    from app.db.models import workspace  # noqa: F401
    from app.db.models import document # noqa: F401
    from app.db.models import block # noqa: F401
    from app.db.models import block_matrix # noqa: F401
    from app.db.models import vector_embedding # noqa: F401
    from app.db.models import upload # noqa: F401
    from app.db.models import workspace_upload # noqa: F401
except ImportError as e:
    print(f"Alembic: Error importing models or Base: {e}")
    raise

target_metadata = Base.metadata

config.set_main_option("sqlalchemy.url", str(settings.database_url))

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
