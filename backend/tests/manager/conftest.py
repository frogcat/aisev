import pytest
from loguru import logger
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
import os
from sqlalchemy.orm import sessionmaker
from src.db.define_tables import Base, EvaluationPerspective, engine


@pytest.fixture(scope="function")
def session():
    """
    Use SQLite in-memory database during test and close the session after the test.
    """

    inmemory_engine = create_engine("sqlite:///:memory:")

    # Drop and recreate all tables
    Base.metadata.drop_all(bind=inmemory_engine)
    Base.metadata.create_all(bind=inmemory_engine)

    session = sessionmaker(bind=inmemory_engine)()
    yield session
    session.close()


@pytest.fixture(scope="function")
def setup_perspectives(session):
    """
    Populates the EvaluationPerspective table with common perspectives for tests.
    """
    names = [
        "有害情報の出力制御",
        "偽誤情報の出力・誘導の防止",
        "公平性と包摂性",
        "ハイリスク利用・目的外利用への対処",
        "プライバシー保護",
        "セキュリティ確保",
        "説明可能性",
        "ロバスト性",
        "データ品質",
        "検証可能性"
    ]
    for n in names:
        session.add(EvaluationPerspective(perspective_name=n))
    session.commit()


@pytest.fixture(scope="function")
def real_db_session():
    session = sessionmaker(bind=engine)()
    yield session
    session.close()
