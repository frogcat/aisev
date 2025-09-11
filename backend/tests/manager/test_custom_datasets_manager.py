from src.db.define_tables import Dataset, CustomDatasets, DatasetCustomMapping, EvaluationPerspective
from src.manager.custom_datasets_manager import CustomDatasetsManager


def test_get_all_names(session, setup_perspectives):
    custom1 = CustomDatasets(name="custom1")
    custom2 = CustomDatasets(name="custom2")
    session.add_all([custom1, custom2])
    session.commit()
    handler = CustomDatasetsManager(session)
    results = handler.get_all_names()
    names = [name for (_id, name) in results]
    assert set(names) >= {"custom1", "custom2"}
    ids = [id for (id, _name) in results]
    assert all(isinstance(i, int) for i in ids)


def test_get_datasets(session, setup_perspectives):
    perspective = EvaluationPerspective(perspective_name="persp1")
    session.add(perspective)
    session.commit()
    dataset1 = Dataset(name="datasetA", data_content=b"A",
                       type="quantitative", evaluation_perspective_id=perspective.id)
    dataset2 = Dataset(name="datasetB", data_content=b"B",
                       type="qualitative", evaluation_perspective_id=perspective.id)
    custom = CustomDatasets(name="customX")
    session.add_all([dataset1, dataset2, custom])
    session.commit()
    mapping1 = DatasetCustomMapping(
        dataset_id=dataset1.id, custom_datasets_id=custom.id, perspective_id=perspective.id, prompt=None, percentage=0)
    mapping2 = DatasetCustomMapping(
        dataset_id=dataset2.id, custom_datasets_id=custom.id, perspective_id=perspective.id, prompt=None, percentage=0)
    session.add_all([mapping1, mapping2])
    session.commit()
    handler = CustomDatasetsManager(session)
    results = handler.get_datasets(custom.id)
    assert set(results) == {"datasetA", "datasetB"}
    assert all(isinstance(name, str) for name in results)


def test_get_dataset_custom_mappings(session, setup_perspectives):
    perspective = EvaluationPerspective(perspective_name="persp1")
    session.add(perspective)
    session.commit()
    dataset1 = Dataset(name="datasetA", data_content=b"A",
                       type="quantitative", evaluation_perspective_id=perspective.id)
    dataset2 = Dataset(name="datasetB", data_content=b"B",
                       type="qualitative", evaluation_perspective_id=perspective.id)
    custom = CustomDatasets(name="customX")
    session.add_all([dataset1, dataset2, custom])
    session.commit()
    mapping1 = DatasetCustomMapping(
        dataset_id=dataset1.id, custom_datasets_id=custom.id, perspective_id=perspective.id, prompt="p1", percentage=10)
    mapping2 = DatasetCustomMapping(
        dataset_id=dataset2.id, custom_datasets_id=custom.id, perspective_id=perspective.id, prompt="p2", percentage=20)
    session.add_all([mapping1, mapping2])
    session.commit()
    handler = CustomDatasetsManager(session)
    results = handler.get_dataset_custom_mappings(custom.id)
    assert isinstance(results, list)
    assert len(results) == 2
    for r in results:
        assert "dataset_id" in r
        assert "prompt" in r
        assert "percentage" in r
    d = {r["prompt"]: r["percentage"] for r in results}
    assert d["p1"] == 10
    assert d["p2"] == 20
