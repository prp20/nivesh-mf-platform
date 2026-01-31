from logging.config import fileConfig
import sys
from pathlib import Path

from alembic import context
from sqlalchemy import pool

# -------------------------------------------------
# Ensure project root is on PYTHONPATH
# -------------------------------------------------
BASE_DIR = Path(__file__).resolve().parents[2]
sys.path.append(str(BASE_DIR))

# -------------------------------------------------
# Alembic Config
# -------------------------------------------------
config = context.config
# fileConfig(config.config_file_name)

# -------------------------------------------------
# Import DB engine and metadata
# -------------------------------------------------
from backend.db.session import engine
from backend.models.base import Base

# FORCE MODEL REGISTRATION
from backend.models import (
    mutual_fund,
    fund_manager,
    fund_manager_mapping,
    nav_data,
    benchmark_nav,
    fund_metrics_snapshot,
)
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_online():
    connectable = engine

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


def run_migrations_online():
    connectable = engine

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

