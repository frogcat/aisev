import pytest
import pandas as pd
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from src.gsn.register_dataset_for_gsn import RegisterDatasetForGSN
import yaml
from src.gsn.gsn_explorer import GSNExplorer
from src.db.define_tables import Dataset
from src.db.migrate_sample_data import initialize_AISI_preset_data


@pytest.mark.skip()
def test_register_gsn_dataset(session):
    root = Path(__file__).parent.parent.parent
    # yaml
    gsn_path = root / 'src' / 'gsn'
    # yaml_name = "01_Control_of_Toxic_Output_GSN.yaml"
    yaml_name = "05_Privacy_Protection_GSN.yaml"
    yaml_path = gsn_path / yaml_name

    with open(yaml_path, 'r') as f:
        gsn_yaml_data = f.read().replace('\x0b', '')
        gsn_yaml_data = yaml.safe_load(gsn_yaml_data)

    explorer = GSNExplorer(gsn_yaml_data)
    gsn_results = explorer.explore()

    # data
    data_dir = root / "dataset" / "output"
    dataset_path = data_dir / "categorized-test-00000-of-00001_gsn.csv"
    dataset_df = pd.read_csv(dataset_path, encoding="utf-8")

    # Create instance of RegisterDatasetForGSN
    register = RegisterDatasetForGSN(session, gsn_yaml_data, dataset_df)

    # Register datasets using gsn_results
    register.register_gsn_dataset()

    # Get all datasets and check them
    datasets = register.db.query(Dataset).all()
    # print(datasets)
    print(len(datasets))

def test_register_gsn_dataset(session):
    # TODO: initialize_AISI_preset_data(session)と同じ動作をさせる中で、チェックを行う
    try:
        data_dir = Path(__file__).parent.parent.parent / "dataset" / "output"
        gsn_yaml_list = RegisterDatasetForGSN.prepare_gsn_yaml_data()


        db_datasets = session.query(Dataset).all()
        assert len(db_datasets) == 0, "Database should be empty before registration"

        # Hirisk
        gsn_dataset = pd.read_csv(data_dir / "AutoRT_Hirisk.csv")
        gsn_dataset.insert(0, 'ID', range(1, len(gsn_dataset) + 1))
        gsn_dataset['ID'] = 'Hirisk_' + gsn_dataset['ID'].astype(str)
        gsn_yaml = gsn_yaml_list[3]
        register = RegisterDatasetForGSN(
            session, gsn_yaml, gsn_dataset)
        register.register_gsn_dataset()
        print("AISIのプリセットデータ(ハイリスク)を初期化しました。")


        # gsn_datasetでgsn_perspectiveがNaNの行を削除
        gsn_dataset = gsn_dataset.dropna(subset=['gsn_perspective'])
        # dbのGSNデータがgsn_datasetのデータ数と一致するか確認
        db_datasets = session.query(Dataset).all()
        assert len(db_datasets) == len(gsn_dataset), "Dataset count mismatch after registration"


    except Exception as e:
        assert False, f"Failed to register GSN dataset: {e}"
