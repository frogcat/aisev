from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm import Session
from src.db.session import get_db
from src.manager.quantitative_dataset_manager import QuantitativeDatasetService
from src.utils.logger import logger
import pandas as pd

router = APIRouter()

@router.get("/quantitative_datasets")
def list_quantitative_datasets(db: Session = Depends(get_db)):
    logger.info("list_quantitative_datasets: 定量データセット一覧取得処理を開始します。")
    try:
        datasets = QuantitativeDatasetService.get_all(db)
        logger.info(f"list_quantitative_datasets: {len(datasets)}件の定量データセットを取得しました。")
        # Loop through datasets and if contents is df, erase the row with NaN
        for dataset in datasets:
            contents = dataset.get('contents')
            if isinstance(contents, pd.DataFrame):
                contents.dropna(inplace=True)
        return {"quantitative_datasets": datasets}
    except Exception as e:
        logger.error(f"list_quantitative_datasets: 取得処理中にエラーが発生しました: {e}")
        raise HTTPException(status_code=500, detail="定量データセット一覧の取得中にエラーが発生しました。")

@router.post("/quantitative_dataset")
async def create_quantitative_dataset(request: Request, db: Session = Depends(get_db)):
    logger.info("create_quantitative_dataset: 定量データセット作成リクエストの処理を開始します。")
    try:
        body = await request.json()
        logger.info(f"create_quantitative_dataset: 受信データ: {body}")
        added = QuantitativeDatasetService.add_from_json(db, body)
        logger.info(f"create_quantitative_dataset: {len(added)}件の定量データセットの追加が完了しました。")
        return {"datasets": [{"id": ds.id, "name": ds.name, "type": ds.type} for ds in added]}
    except Exception as e:
        logger.error(f"create_quantitative_dataset: 作成処理中にエラーが発生しました: {e}")
        raise HTTPException(status_code=500, detail="定量データセットの作成中にエラーが発生しました。")

@router.delete("/quantitative_datasets/{dataset_id}")
def delete_quantitative_datasets(dataset_id: int, db: Session = Depends(get_db)):
    logger.info(f"delete_quantitative_datasets: ID={dataset_id} の定量データセット削除リクエストの処理を開始します。")
    try:
        result = QuantitativeDatasetService.delete_by_id(db, dataset_id)
        if not result:
            logger.info(f"delete_quantitative_datasets: ID={dataset_id} の定量データセットは見つかりませんでした。")
            raise HTTPException(status_code=404, detail="Quantitative datasets not found")
        logger.info(f"delete_quantitative_datasets: ID={dataset_id} の定量データセット削除が完了しました。")
        return {"result": True}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"delete_quantitative_datasets: 削除処理中にエラーが発生しました: {e}")
        raise HTTPException(status_code=500, detail="定量データセットの削除中にエラーが発生しました。")
