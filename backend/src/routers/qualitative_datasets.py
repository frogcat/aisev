from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm import Session
from src.db.session import get_db
from src.manager.qualitative_dataset_manager import QualitativeDatasetService
from src.utils.logger import logger

router = APIRouter()


@router.get("/qualitative_datasets")
def list_qualitative_datasets(db: Session = Depends(get_db)):
    logger.info("list_qualitative_datasets: 定性データセット一覧取得処理を開始します。")
    try:
        datasets = QualitativeDatasetService.get_all(db)
        logger.info(f"list_qualitative_datasets: {len(datasets)}件の定性データセットを取得しました。")
        return {"qualitative_datasets": datasets}
    except Exception as e:
        logger.error(f"list_qualitative_datasets: 取得処理中にエラーが発生しました: {e}")
        raise HTTPException(status_code=500, detail="定性データセット一覧の取得中にエラーが発生しました。")


@router.get("/qualitative_datasets/{dataset_id}")
def get_qualitative_dataset(dataset_id: int, db: Session = Depends(get_db)):
    logger.info(f"get_qualitative_dataset: ID={dataset_id} の定性データセット取得処理を開始します。")
    try:
        dataset = QualitativeDatasetService.get_by_id(db, dataset_id)
        if not dataset:
            logger.info(f"get_qualitative_dataset: ID={dataset_id} の定性データセットは見つかりませんでした。")
            raise HTTPException(
                status_code=404, detail="Qualitative dataset not found")
        logger.info(f"get_qualitative_dataset: データセット '{dataset['name']}' を取得しました。")
        return dataset
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"get_qualitative_dataset: 取得処理中にエラーが発生しました: {e}")
        raise HTTPException(status_code=500, detail="定性データセットの取得中にエラーが発生しました。")


@router.get("/qualitative_datasets/by_evaluation/{evaluation_id}")
def get_qualitative_datasets_by_evaluation_id(evaluation_id: int, db: Session = Depends(get_db)):
    logger.info(f"get_qualitative_datasets_by_evaluation_id: evaluation_id={evaluation_id} の定性データセット取得処理を開始します。")
    try:
        datasets = QualitativeDatasetService.get_by_evaluation_id(
            db, evaluation_id)
        if not datasets:
            logger.info(f"get_qualitative_datasets_by_evaluation_id: evaluation_id={evaluation_id} の定性データセットは見つかりませんでした。")
            raise HTTPException(
                status_code=404, detail="Qualitative datasets not found for the given evaluation_id")
        logger.info(f"get_qualitative_datasets_by_evaluation_id: {len(datasets)}件の定性データセットを取得しました。")
        return {"qualitative_datasets": datasets}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"get_qualitative_datasets_by_evaluation_id: 取得処理中にエラーが発生しました: {e}")
        raise HTTPException(status_code=500, detail="定性データセットの取得中にエラーが発生しました。")


@router.post("/qualitative_dataset")
async def create_qualitative_dataset(request: Request, db: Session = Depends(get_db)):
    logger.info("create_qualitative_dataset: 定性データセット作成リクエストの処理を開始します。")
    try:
        body = await request.json()
        logger.info(f"create_qualitative_dataset: 受信データ: {body}")
        added = QualitativeDatasetService.add_from_json(db, body)
        logger.info(f"create_qualitative_dataset: {len(added)}件の定性データセットの追加が完了しました。")
        return {"datasets": [{"id": ds.id, "name": ds.name, "type": ds.type} for ds in added]}
    except Exception as e:
        logger.error(f"create_qualitative_dataset: 作成処理中にエラーが発生しました: {e}")
        raise HTTPException(status_code=500, detail="定性データセットの作成中にエラーが発生しました。")


@router.delete("/qualitative_datasets/{dataset_id}")
def delete_qualitative_datasets(dataset_id: int, db: Session = Depends(get_db)):
    logger.info(f"delete_qualitative_datasets: ID={dataset_id} の定性データセット削除リクエストの処理を開始します。")
    try:
        result = QualitativeDatasetService.delete_by_id(db, dataset_id)
        if not result:
            logger.info(f"delete_qualitative_datasets: ID={dataset_id} の定性データセットは見つかりませんでした。")
            raise HTTPException(
                status_code=404, detail="Qualitative datasets not found")
        logger.info(f"delete_qualitative_datasets: ID={dataset_id} の定性データセット削除が完了しました。")
        return {"result": True}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"delete_qualitative_datasets: 削除処理中にエラーが発生しました: {e}")
        raise HTTPException(status_code=500, detail="定性データセットの削除中にエラーが発生しました。")
