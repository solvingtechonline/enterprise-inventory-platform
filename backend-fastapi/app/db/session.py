"""
Configuración base de SQLAlchemy.

SQLAlchemy administra EXCLUSIVAMENTE la tabla Inventario en este proyecto.
Empresa y Productos son administrados por el ORM de Django, en el otro
backend.

El modelo concreto de Inventario vive en `app.models.inventario`.
"""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings

engine = create_engine(settings.database_url, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Base declarativa para los modelos SQLAlchemy de la tabla Inventario."""


def get_db() -> Generator:
    """Dependencia de FastAPI para obtener una sesión de base de datos por request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
