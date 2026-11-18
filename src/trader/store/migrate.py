"""Programmatic Alembic: `tradectl db-init` runs `upgrade head`. Migrations live inside the package so the
Docker image carries them. Models are the source of truth; generate new revisions with `autogenerate`."""

from __future__ import annotations

from pathlib import Path

from alembic import command
from alembic.config import Config


def alembic_config(url: str) -> Config:
    cfg = Config()
    cfg.set_main_option("script_location", str(Path(__file__).parent / "alembic"))
    cfg.set_main_option("sqlalchemy.url", url.replace("%", "%%"))
    return cfg


def upgrade(url: str, revision: str = "head") -> None:
    command.upgrade(alembic_config(url), revision)


def autogenerate(url: str, message: str) -> None:  # dev helper
    command.revision(alembic_config(url), message=message, autogenerate=True)
