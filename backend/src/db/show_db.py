from sqlalchemy.orm import sessionmaker
from src.db.session import engine
from src.db.define_tables import Dataset, CustomDatasets, EvaluationPerspective, DatasetCustomMapping, AIModel, Evaluation, EvaluationResult, UseGSN
from src.utils.logger import logger

class ShowDatabase:
    def __init__(self, session):
        self.session = session

    def log_table_contents(self, table_class):
        session = self.session
        try:
            logger.info(f"log_table_contents: {table_class.__tablename__} テーブルの内容取得を開始します。")
            results = session.query(table_class).all()
            logger.info(f"Contents of table {table_class.__tablename__}:")
            for result in results:
                logger.info(result)
            logger.info(f"log_table_contents: {table_class.__tablename__} テーブルの内容取得が完了しました。")
        except Exception as e:
            logger.error(f"Error querying table {table_class.__tablename__}: {e}")
        finally:
            session.close()

    def show_all_tables(self):
        logger.info("show_all_tables: 全テーブルの内容表示を開始します。")
        self.log_table_contents(Dataset)
        self.log_table_contents(CustomDatasets)
        self.log_table_contents(EvaluationPerspective)
        self.log_table_contents(DatasetCustomMapping)
        self.log_table_contents(AIModel)
        self.log_table_contents(Evaluation)
        self.log_table_contents(EvaluationResult)
        self.log_table_contents(UseGSN)
        logger.info("show_all_tables: 全テーブルの内容表示が完了しました。")

if __name__ == "__main__":
    try:
        logger.info("__main__: データベース内容表示処理を開始します。")
        db_viewer = ShowDatabase(sessionmaker(bind=engine)())
        db_viewer.show_all_tables()
        logger.info("__main__: データベース内容表示処理が完了しました。")
    except Exception as e:
        logger.error(f"__main__: データベース内容表示処理中にエラーが発生しました: {e}")
