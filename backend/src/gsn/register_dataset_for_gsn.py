from typing import List, Dict, Any
from src.gsn.gsn_explorer import GSNExplorer
from pathlib import Path
import pandas as pd
from src.manager.quantitative_dataset_manager import QuantitativeDatasetService
from src.manager.qualitative_dataset_manager import QualitativeDatasetService
from sqlalchemy.orm import Session
from src.utils.logger import logger
import pickle
from sqlalchemy import text
from src.db.define_tables import Dataset


class RegisterDatasetForGSN:
    GSN_LIST = [
        "01_Control_of_Toxic_Output_GSN.yaml",
        "02_Prevention_of_Misinformation_Disinformation_and_Manipulation_GSN.yaml",
        "03_Fairness_and_Inclusion_GSN.yaml",
        "04_Addressing_High-risk_Use_and_Unintended_Use_GSN.yaml",
        "05_Privacy_Protection_GSN.yaml",
        "06_Ensuring_Security_GSN.yaml",
        "07_Explainability_GSN.yaml",
        "08_Robustness_GSN.yaml",
        "09_Data_Quality_GSN.yaml",
        "10_Verifiability_GSN.yaml",
    ]

    def __init__(self, db: Session, gsn_yaml_data: Dict[str, Any], dataset: pd.DataFrame):
        self.db = db

        self.gsn_yaml_data = gsn_yaml_data

        # Parsing GSN information using GSNExplorer
        logger.info("RegisterDatasetForGSN: GSNExplorerによるGSN情報のパースを開始します。")
        self.gsn_explorer = GSNExplorer(gsn_yaml_data)
        try:
            self.gsn_results = self.gsn_explorer.explore()
            logger.info("RegisterDatasetForGSN: GSN情報のパースが完了しました。")
        except Exception as e:
            logger.error(
                f"RegisterDatasetForGSN: GSNExplorerによるパース中にエラーが発生しました: {e}")
            raise

        # Receive data sets directly
        self.dataset = dataset

    @staticmethod
    def prepare_gsn_yaml_data():
        """
        Load a set of GSN YAML files and return them in a list.
        """
        import yaml
        from pathlib import Path
        base_path = Path(__file__).parent  # /app/src/gsn/
        gsn_yaml_files = [
            base_path / file_name for file_name in RegisterDatasetForGSN.GSN_LIST]
        gsn_yaml_data = []
        for file in gsn_yaml_files:
            with open(file, "r") as f:
                yaml_text = f.read().replace('\x0b', '')
                gsn_yaml_data.append(yaml.safe_load(yaml_text))
        return gsn_yaml_data

    @staticmethod
    def get_gsn_detail_by_id(gsn_id: str) -> Dict[str, Any]:
        """
        Get GSN details based on GSN ID
        """
        gsn_yaml_data = RegisterDatasetForGSN.prepare_gsn_yaml_data()
        gsn_n = gsn_id[1]
        logger.info(f"get_gsn_detail_by_id: GSN ID '{gsn_id}' の詳細を取得します。")
        return gsn_yaml_data[int(gsn_n)-1].get(gsn_id)

    @staticmethod
    def prepare_dataset(dataset_path):
        """
        Load and return CSV data sets
        """
        import pandas as pd
        return pd.read_csv(dataset_path, encoding="utf-8")

    def register_gsn_dataset(self):
        """
        Register a dataset using gsn_results.
        Quantitative evaluation for those for which quantitative data exist
        Those for which quantitative evaluation data do not exist shall be evaluated qualitatively.

        gsn_results has the following format
        [
            {
                'leaf': 'Final Question',
                'score_rate': 1.0,  # Score ratio
                'second_goal': 'Definition of SecondGoal'
            },
            ...
        ]
        Register “leaf” in the dataset along with the qualitative question items, score_rate, second_goal, and so on.
        """
        logger.info("register_gsn_dataset: GSNデータセット登録処理を開始します。")
        perspective_map = {
            "G1": "有害情報の出力制御",
            "G2": "偽誤情報の出力・誘導の防止",
            "G3": "公平性と包摂性",
            "G4": "ハイリスク利用・目的外利用への対処",
            "G5": "プライバシー保護",
            "G6": "セキュリティ確保",
            "G7": "説明可能性",
            "G8": "ロバスト性",
            "G9": "データ品質",
            "G10": "検証可能性"
        }
        # If the beginning of the string of gsn_perspective is G1,
        # then the ten_perspective column is the output control of harmful information as per map
        # dataset_dropna = self.dataset.dropna(subset=['gsn_perspective'])
        # dataset_dropna = dataset_dropna.copy()
        # dataset_dropna.loc[:, 'ten_perspective'] = dataset_dropna['gsn_perspective'].apply(
        #             lambda x: perspective_map.get(x[0:2], "Unknown")
        #         )

        # Retrieve GSN data from the DB and convert it to a DataFrame
        logger.debug("start register_gsn_dataset: GSNデータの取得を開始します。")
        explorer = GSNExplorer(self.gsn_yaml_data)
        gsn_dfs = []
        for perspective_id in range(1, 11):
            perspective_gsn_data = explorer.get_gsn_data(perspective_id=perspective_id)

            # Delete the retrieved data from the database
            session = self.db
            session.query(Dataset).filter(
                Dataset.evaluation_perspective_id == perspective_id
            ).delete()

            if len(perspective_gsn_data) == 0:
                continue

            gsn_json = {
                "name": [p.name for p in perspective_gsn_data],
                "contents": [p.data_content for p in perspective_gsn_data],
                "score_rate": [p.score_rate for p in perspective_gsn_data],
                "second_goal": [p.second_goal for p in perspective_gsn_data],
                "gsn_leaf": [p.gsn_leaf for p in perspective_gsn_data],
                "criterion": [p.evaluation_perspective_id for p in perspective_gsn_data],
            }
            gsn_dfs.append(pd.DataFrame(gsn_json))
        
        # Merge dataframes from the existing database
        if len(gsn_dfs) == 0:
            db_gsn_df = pd.DataFrame(columns=[
                'name', 'contents', 'score_rate', 'second_goal', 'gsn_leaf', 'criterion'
            ])
        else:
            db_gsn_df = pd.concat(gsn_dfs, ignore_index=True)
        logger.debug(f"register_gsn_dataset: GSNデータの取得が完了しました。取得したデータ: {db_gsn_df}")
        # Debug output of self.dataset format
        logger.debug(f"register_gsn_dataset: datasetの形式: {self.dataset.columns}")
        logger.debug(f"register_gsn_dataset: datasetの形式: {self.dataset}")

        # Modifying db_gsn_df
        # Remove GSN_ from name to create gsn_perspective
        db_gsn_df['gsn_perspective'] = db_gsn_df['name'].str.replace('GSN_', '', regex=False)
        # Add G prefix to criterion to make it a key for perspective_map. Then update criterion
        db_gsn_df['criterion_'] = db_gsn_df['criterion'].apply(
            lambda x: f"G{x}" if isinstance(x, int) else x
        )
        db_gsn_df['criterion_'] = db_gsn_df['criterion_'].apply(
            lambda x: perspective_map.get(x, "Unknown") if isinstance(x, str) else "Unknown"
        )

        # db_dataset: columns 'ten_perspective', 'requirement', 'text', 'output', 'gsn_perspective' are required

        # TODO: Add data retrieved from db to self.gsn_results (add dict to list)
        db_gsn_results_df = pd.DataFrame(
            {'ID': db_gsn_df['gsn_perspective'],
             'leaf': db_gsn_df['gsn_leaf'],
             'score_rate': db_gsn_df['score_rate'],
             'second_goal': db_gsn_df['second_goal'],}
        )
        # Convert df to dict list and merge with self.gsn_results
        gsn_results_df = pd.DataFrame(self.gsn_results)
        db_gsn_results_df = pd.concat([db_gsn_results_df, gsn_results_df], ignore_index=True)
        # remove id duplicates
        db_gsn_results_df = db_gsn_results_df.drop_duplicates(subset=['ID'], keep='last')
        # sort by ID
        db_gsn_results_df = db_gsn_results_df.sort_values(by='ID').reset_index(drop=True)
        # Convert to a list of dictionaries
        db_include_gsn_results = db_gsn_results_df.to_dict(orient='records')

        # TODO: Add data retrieved from db to self.dataset (add df rows)
        db_dataset_df = pd.DataFrame({
            'ten_perspective': db_gsn_df['criterion_'],
            'requirement': db_gsn_df['name'],
            'text': db_gsn_df['contents'],
            'output': db_gsn_df['gsn_leaf'],
            'gsn_perspective': db_gsn_df['gsn_perspective']
        })
        # pickle loads db_gsn_df contents
        db_include_dataset = self.dataset.copy()
        for content in db_gsn_df['contents']:
            if isinstance(content, bytes):
                content = pickle.loads(content)
            else:
                content = content
            
            if isinstance(content, pd.DataFrame):
                db_include_dataset = pd.concat([db_include_dataset, content], ignore_index=True)
            elif isinstance(content, list):
                # NOTE: Qualitative data is automatically created from leaf, so there is no need to retain db data here
                continue

        # remove ID duplicates
        db_include_dataset = db_include_dataset.drop_duplicates(subset=['ID'], keep='last')

        try:
            # for result in self.gsn_results:
            for result in db_include_gsn_results:
                ID = result['ID']
                leaf = result['leaf']
                score_rate = result['score_rate']
                second_goal = result['second_goal']

                # Search by ID from gsn_perspective column of df to get small data frames
                # subset_df = self.dataset[self.dataset['gsn_perspective'] == ID]
                subset_df = db_include_dataset[db_include_dataset['gsn_perspective'] == ID]
                # If ID starts with G10, use ID[0:3], otherwise use ID[0:2] for perspective_map
                if ID.startswith("G10"):
                    criterion = perspective_map.get(ID[0:3])
                else:
                    criterion = perspective_map.get(ID[0:2])

                subset_df = subset_df.copy()
                subset_df['ten_perspective'] = criterion

                # If the data frame is not empty, it is registered as quantitative data
                if not subset_df.empty:
                    dataset_dict = {
                        "name": f"GSN_{ID}",
                        # "criterion": leaf,
                        "contents": subset_df,
                        "score_rate": score_rate,
                        "second_goal": second_goal,
                        "gsn_leaf": leaf,  # Maintains information as a GSN leaf
                        "criterion": criterion
                    }
                    try:
                        # Register in the database using the Quantitative Dataset Service
                        QuantitativeDatasetService.add_from_json(
                            self.db, dataset_dict)
                        logger.info(
                            f"register_gsn_dataset: 定量データセット 'GSN_{ID}' を登録しました。")
                    except Exception as e:
                        logger.error(
                            f"register_gsn_dataset: 定量データセット 'GSN_{ID}' の登録中にエラーが発生しました: {e}")
                        continue

                else:
                    # If data frame is empty, register as qualitative data
                    dataset_dict = {
                        "name": f"GSN_{ID}",
                        # "criterion": leaf,
                        # Qualitative questions are registered as a single text
                        "contents": [leaf],
                        "score_rate": score_rate,
                        "second_goal": second_goal,
                        "gsn_leaf": leaf,  # Maintains information as a GSN leaf
                        "criterion": criterion
                    }
                    try:
                        # Register in the database using the Qualitative Dataset Service
                        QualitativeDatasetService.add_from_json(
                            self.db, dataset_dict)
                        logger.info(
                            f"register_gsn_dataset: 定性データセット 'GSN_{ID}' を登録しました。")
                    except Exception as e:
                        logger.error(
                            f"register_gsn_dataset: 定性データセット 'GSN_{ID}' の登録中にエラーが発生しました: {e}")
                        continue
            logger.info("register_gsn_dataset: GSNデータセット登録処理が完了しました。")
        except Exception as e:
            logger.error(
                f"register_gsn_dataset: GSNデータセット登録処理中にエラーが発生しました: {e}")
            raise

        session.commit()


def sampling_parquet():
    """
    Sample a Parquet file and return a DataFrame.
    """
    import pandas as pd
    from pathlib import Path
    data_dir = Path(__file__).parent.parent.parent / "dataset"
    parquet_file = data_dir / "test-00000-of-00001.parquet"

    df = pd.read_parquet(parquet_file)
    df_sampled = df.head(10)

    df_sampled.to_parquet(
        data_dir / "sampled_test.parquet", index=False, engine='pyarrow'
    )


if __name__ == "__main__":
    sampling_parquet()
