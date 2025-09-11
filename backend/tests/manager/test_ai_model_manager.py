import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.db.define_tables import Base, AIModel
from src.manager.ai_model_manager import AIModelManager

def test_add_model(session):
    data = {
        "name": "TestModel",
        "url": "http://example.com",
        "api_key": "secret",
        "api_request_format": {"input": "text"},
        "type": "target"
    }
    model = AIModelManager.add_model(session, data)
    assert model.id is not None
    assert model.name == "TestModel"
    assert model.url == "http://example.com"
    assert model.api_key == "secret"
    assert model.api_request_format == {"input": "text"}
    assert model.type == "target"

def test_get_model_by_id(session):
    data = {
        "name": "ModelA",
        "url": "http://a.com",
        "api_key": "keyA",
        "api_request_format": {"a": 1},
        "type": "eval"
    }
    model = AIModelManager.add_model(session, data)
    fetched = AIModelManager.get_model_by_id(session, model.id)
    assert fetched is not None
    assert fetched.id == model.id
    assert fetched.name == "ModelA"

def test_get_all_models(session):
    data1 = {
        "name": "Model1",
        "url": "http://1.com",
        "api_key": "k1",
        "api_request_format": {"x": 1},
        "type": "target"
    }
    data2 = {
        "name": "Model2",
        "url": "http://2.com",
        "api_key": "k2",
        "api_request_format": {"y": 2},
        "type": "eval"
    }
    AIModelManager.add_model(session, data1)
    AIModelManager.add_model(session, data2)
    models = AIModelManager.get_all_models(session)
    assert len(models) == 2
    names = [m.name for m in models]
    assert "Model1" in names and "Model2" in names

def test_update_model(session):
    data = {
        "name": "OldName",
        "url": "http://old.com",
        "api_key": "oldkey",
        "api_request_format": {"old": True},
        "type": "target"
    }
    model = AIModelManager.add_model(session, data)
    update_data = {
        "name": "NewName",
        "url": "http://new.com",
        "api_key": "newkey",
        "api_request_format": {"new": False},
        "type": "eval"
    }
    updated = AIModelManager.update_model(session, model.id, update_data)
    assert updated.name == "NewName"
    assert updated.url == "http://new.com"
    assert updated.api_key == "newkey"
    assert updated.api_request_format == {"new": False}
    assert updated.type == "eval"

def test_delete_model(session):
    data = {
        "name": "ToDelete",
        "url": "http://delete.com",
        "api_key": "delkey",
        "api_request_format": {"del": 1},
        "type": "target"
    }
    model = AIModelManager.add_model(session, data)
    deleted = AIModelManager.delete_model(session, model.id)
    assert deleted is True
    # Cannot be retrieved after deletion
    assert AIModelManager.get_model_by_id(session, model.id) is None

def test_delete_model_not_found(session):
    # Deleted with a non-existent ID
    deleted = AIModelManager.delete_model(session, 999)
    assert deleted is False