import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.db.define_tables import Base, EvaluationPerspective, Dataset
from src.manager.dataset_manager import DatasetManager
import pickle
import io
import pandas as pd
from pandas.testing import assert_frame_equal


@pytest.fixture
def db_session():
    # Test with SQLite in-memory DB
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    # Add test perspective
    perspective = EvaluationPerspective(perspective_name="test_criterion")
    session.add(perspective)
    session.commit()
    yield session
    session.close()


def test_register_dataset(db_session):
    data = """
ID,text,output,meta,meta-mlmc,ten_perspective
id1, text1, output1, {"key": "value"}, {"key": "value-mlmc"}, perspective1
id2, text2, output2, {"key": "value"}, {"key": "value-mlmc"}, perspective2
"""
    name = "test_data"

    dataset = DatasetManager.register_dataset(db_session, name, data)

    assert dataset.id is not None
    assert dataset.name == "test_data"
    assert dataset.type == "quantitative"
    # assert dataset.evaluation_perspective_id == 1
    # Validate data content
    orig_content = pd.read_csv(io.StringIO(data.strip()))
    dataset_content = pickle.loads(dataset.data_content)

    assert_frame_equal(orig_content, dataset_content)


def test_get_by_ids(db_session):
    # Register two datasets
    data1 = """
ID,text,output,meta,meta-mlmc,ten_perspective
id1, text1, output1, {\"key\": \"value\"}, {\"key\": \"value-mlmc\"}, perspective1
"""
    data2 = """
ID,text,output,meta,meta-mlmc,ten_perspective
id2, text2, output2, {\"key\": \"value2\"}, {\"key\": \"value-mlmc2\"}, perspective2
"""
    ds1 = DatasetManager.register_dataset(db_session, "ds1", data1)
    ds2 = DatasetManager.register_dataset(db_session, "ds2", data2)

    # Retrieve both with get_by_ids
    result = DatasetManager.get_by_ids(db_session, [ds1.id, ds2.id])
    assert len(result) == 2
    ids = [d.id for d in result]
    assert ds1.id in ids and ds2.id in ids
    # Empty list
    assert DatasetManager.get_by_ids(db_session, []) == []
    # Non-existent ID
    assert DatasetManager.get_by_ids(db_session, [-999]) == []


def test_get_by_ids_and_type(db_session):
    # Register two datasets (quantitative, qualitative)
    data1 = """
ID,text,output,meta,meta-mlmc,ten_perspective
id1, text1, output1, {\"key\": \"value\"}, {\"key\": \"value-mlmc\"}, perspective1
"""
    data2 = """
ID,text,output,meta,meta-mlmc,ten_perspective
id2, text2, output2, {\"key\": \"value2\"}, {\"key\": \"value-mlmc2\"}, perspective2
"""
    ds1 = DatasetManager.register_dataset(db_session, "ds1", data1)
    ds2 = DatasetManager.register_dataset(db_session, "ds2", data2)
    # Explicitly change type
    ds2.type = "qualitative"
    db_session.commit()

    # Retrieve only quantitative
    result_quant = DatasetManager.get_by_ids_and_type(
        db_session, [ds1.id, ds2.id], "quantitative")
    assert len(result_quant) == 1
    assert result_quant[0].id == ds1.id
    assert result_quant[0].type == "quantitative"

    # Retrieve only qualitative
    result_qual = DatasetManager.get_by_ids_and_type(
        db_session, [ds1.id, ds2.id], "qualitative")
    assert len(result_qual) == 1
    assert result_qual[0].id == ds2.id
    assert result_qual[0].type == "qualitative"

    # Empty list
    assert DatasetManager.get_by_ids_and_type(
        db_session, [], "quantitative") == []
    # Non-existent ID
    assert DatasetManager.get_by_ids_and_type(
        db_session, [-999], "quantitative") == []
