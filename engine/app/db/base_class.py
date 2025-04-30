# app/db/base_class.py
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import MetaData



POSTGRES_INDEXES_NAMING_CONVENTION = {
    "ix": "%(column_0_label)s_ix",
    "uq": "%(table_name)s_%(column_0_name)s_uq",
    "ck": "%(table_name)s_%(constraint_name)s_ck",
    "fk": "%(table_name)s_%(column_0_name)s_%(referred_table_name)s_fk",
    "pk": "%(table_name)s_pk",
}

class Base(DeclarativeBase):
    """
    Base class for SQLAlchemy models.
    Includes configuration for metadata naming conventions.
    """
    metadata = MetaData(naming_convention=POSTGRES_INDEXES_NAMING_CONVENTION)

    pass
    