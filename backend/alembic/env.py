import sys
import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context

# Append current directory to resolve application packages
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import settings
from app.database import Base
# Import all database models to ensure metadata mapping
from app.models import User, Resume, InterviewSession, InterviewMessage, Report, SkillScore, QuestionBank

# Alembic configuration context
config = context.config

# Setup logging configuration if ini file exists
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Map metadata schemas
target_metadata = Base.metadata

# Dynamic connection string injection from app configuration (escape % for configparser)
db_url_escaped = settings.get_db_url.replace("%", "%%")
config.set_main_option("sqlalchemy.url", db_url_escaped)

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
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
    """Run migrations in 'online' mode."""
    # Handle connection pool setup
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
