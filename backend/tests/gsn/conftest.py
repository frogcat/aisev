from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.db.define_tables import Base
import pytest


@pytest.fixture(scope="function")
def session():
    """
    Use SQLite in-memory database during test and close the session after the test.
    """

    engine = create_engine("sqlite:///:memory:")

    # Drop and recreate all tables
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    session = sessionmaker(bind=engine)()
    yield session
    session.close()
