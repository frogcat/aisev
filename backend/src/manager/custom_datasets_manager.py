"""
A class that consolidates database query processing related to CustomDatasets.
"""

from ..db.define_tables import CustomDatasets, DatasetCustomMapping, Dataset
from sqlalchemy.orm import Session
from src.utils.logger import logger


class CustomDatasetsManager:
    def __init__(self, session: Session):
        self.session = session

    def get_all_names(self) -> list[tuple[int, str]]:
        """
        Returns all id and name column values from the CustomDatasets table as a list.
        :return: List of tuples (id, name)
        """
        logger.info("get_all_names: CustomDatasetsの全名称取得を開始します。")
        try:
            result = [
                (row.id, row.name)
                for row in self.session.query(CustomDatasets.id, CustomDatasets.name).all()
            ]
            logger.info(f"get_all_names: {len(result)}件の名称を取得しました。")
            return result
        except Exception as e:
            logger.error(f"get_all_names: 取得処理中にエラーが発生しました: {e}")
            return []

    def get_dataset_custom_mappings(self, custom_datasets_id: int) -> list[dict]:
        """
        Returns all information (dataset_id, prompt, percentage) of DatasetCustomMapping belonging to custom_datasets_id as a list.
        :param custom_datasets_id: ID of CustomDatasets
        :return: List of dictionaries
        """
        logger.info(f"get_dataset_custom_mappings: custom_datasets_id={custom_datasets_id} のマッピング取得を開始します。")
        try:
            mappings = self.session.query(DatasetCustomMapping).filter_by(
                custom_datasets_id=custom_datasets_id).all()
            result = [
                {
                    "dataset_id": m.dataset_id,
                    "prompt": m.prompt,
                    "percentage": m.percentage
                }
                for m in mappings
            ]
            logger.info(f"get_dataset_custom_mappings: {len(result)}件のマッピングを取得しました。")
            return result
        except Exception as e:
            logger.error(f"get_dataset_custom_mappings: 取得処理中にエラーが発生しました: {e}")
            return []

    def get_datasets(self, custom_datasets_id: int) -> list[str]:
        """
        Returns all names of Datasets belonging to custom_datasets_id as a list.
        :param custom_datasets_id: ID of CustomDatasets
        :return: List of names
        """
        logger.info(f"get_datasets: custom_datasets_id={custom_datasets_id} のDataset名称取得を開始します。")
        try:
            mappings = self.session.query(DatasetCustomMapping).filter_by(
                custom_datasets_id=custom_datasets_id).all()
            dataset_ids = [m.dataset_id for m in mappings]
            datasets = self.session.query(Dataset).filter(
                Dataset.id.in_(dataset_ids)).all()
            result = [d.name for d in datasets]
            logger.info(f"get_datasets: {len(result)}件のDataset名称を取得しました。")
            return result
        except Exception as e:
            logger.error(f"get_datasets: 取得処理中にエラーが発生しました: {e}")
            return []

    def add_custom_dataset(self, name: str) -> int:
        """
        Adds a new record to the CustomDatasets table.
        :param name: Name of the custom dataset to add
        :return: ID of the added record
        """
        logger.info(f"add_custom_dataset: カスタムデータセット '{name}' の追加を開始します。")
        try:
            new_dataset = CustomDatasets(name=name)
            self.session.add(new_dataset)
            self.session.commit()
            logger.info(f"add_custom_dataset: 追加が完了しました。ID={new_dataset.id}")
            return new_dataset.id
        except Exception as e:
            logger.error(f"add_custom_dataset: 追加処理中にエラーが発生しました: {e}")
            self.session.rollback()
            return -1

    def add_dataset_custom_mapping(self, dataset_id: int, custom_datasets_id: int, perspective_id: int, prompt: str, percentage: int):
        """
        Adds a new mapping to the DatasetCustomMapping table.
        :param dataset_id: ID of the target Dataset
        :param custom_datasets_id: ID of the target CustomDatasets
        :param perspective_id: ID of the target EvaluationPerspective
        :param prompt: Prompt to associate with the mapping
        :param percentage: Percentage to associate with the mapping
        """
        logger.info(f"add_dataset_custom_mapping: dataset_id={dataset_id}, custom_datasets_id={custom_datasets_id} のマッピング追加を開始します。")
        try:
            new_mapping = DatasetCustomMapping(
                dataset_id=dataset_id,
                custom_datasets_id=custom_datasets_id,
                perspective_id=perspective_id,
                prompt=prompt,
                percentage=percentage
            )
            self.session.add(new_mapping)
            self.session.commit()
            logger.info("add_dataset_custom_mapping: 追加が完了しました。")
        except Exception as e:
            logger.error(f"add_dataset_custom_mapping: 追加処理中にエラーが発生しました: {e}")
            self.session.rollback()
