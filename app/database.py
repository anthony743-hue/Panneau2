from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

_engine = None
_SessionLocal = None


def get_database_url():
    URL = (
        'mssql+pyodbc://sa:Sqlserver123!@localhost:1433/'
        'PanneauSolaireDB?driver=ODBC+Driver+17+for+SQL+Server'
    )
    return URL


def get_engine():
    global _engine, _SessionLocal

    if _engine is not None:
        return _engine

    database_url = get_database_url()
    if not database_url:
        raise RuntimeError(
            "Aucune base configuree. Definis PANNEAU_DATABASE_URL ou DATABASE_URL."
        )

    _engine = create_engine(database_url)
    _SessionLocal = sessionmaker(bind=_engine, expire_on_commit=False)
    return _engine


def get_session_factory():
    global _SessionLocal
    if _SessionLocal is None:
        get_engine()
    return _SessionLocal


@contextmanager
def session_scope():
    session = get_session_factory()()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
