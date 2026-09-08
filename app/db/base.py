# SQLAlchemy declarative base used across all models.

import importlib

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


# Import models so SQLAlchemy registers them before create_all().
importlib.import_module("app.db.models")
