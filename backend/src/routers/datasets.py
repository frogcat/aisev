from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Form, Body
from sqlalchemy.orm import Session
from src.db.session import get_db
from src.manager.qualitative_dataset_manager import QualitativeDatasetService
from src.manager.quantitative_dataset_manager import QuantitativeDatasetService
from src.manager.custom_datasets_manager import CustomDatasetsManager
from src.manager.dataset_manager import DatasetManager
from pydantic import BaseModel
from typing import List
from src.utils.logger import logger

router = APIRouter()


@router.get("/datasets")
def list_datasets(db: Session = Depends(get_db)):
    logger.info("list_datasets: データセット一覧取得処理を開始します。")
    try:
        qualitative = QualitativeDatasetService.get_all(db)
        quantitative = QuantitativeDatasetService.get_all(db)
        result = [
            {"id": d["id"], "name": d["name"]} for d in qualitative + quantitative
        ]
        logger.info(f"list_datasets: {len(result)}件のデータセットを取得しました。")
        return {"datasets": result}
    except Exception as e:
        logger.error(f"list_datasets: 取得処理中にエラーが発生しました: {e}")
        raise HTTPException(status_code=500, detail="データセット一覧の取得中にエラーが発生しました。")


@router.get("/custom_datasets")
def list_custom_datasets(db: Session = Depends(get_db)):
    logger.info("list_custom_datasets: カスタムデータセット一覧取得処理を開始します。")
    try:
        handler = CustomDatasetsManager(db)
        custom_datasets = handler.get_all_names()
        logger.info(f"list_custom_datasets: {len(custom_datasets)}件のカスタムデータセットを取得しました。")
        return {"custom_datasets": [{"id": id_, "name": name} for id_, name in custom_datasets]}
    except Exception as e:
        logger.error(f"list_custom_datasets: 取得処理中にエラーが発生しました: {e}")
        raise HTTPException(status_code=500, detail="カスタムデータセット一覧の取得中にエラーが発生しました。")


@router.post("/datasets/register")
def register_dataset(
    file: UploadFile = File(...),
    datasetName: str = Form(...),
    aspect: str = Form(None),
    db: Session = Depends(get_db)
):
    """
    Register a new dataset (multipart/form-data support)
    """
    logger.info(f"register_dataset: データセット '{datasetName}' の登録処理を開始します。")
    try:
        data_text = file.file.read().decode("utf-8")
        dataset = DatasetManager.register_dataset(
            db, datasetName, data_text)
        logger.info(f"register_dataset: データセット '{datasetName}' の登録が完了しました。")
        return {"id": dataset.id, "name": dataset.name}
    except Exception as e:
        logger.error(f"register_dataset: 登録処理中にエラーが発生しました: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/datasets/register/gsn")
def register_dataset_gsn(
    file: UploadFile = File(...),
    datasetName: str = Form(...),
    aspect: str = Form(None),
    db: Session = Depends(get_db)
):
    """
    Register a new GSN dataset (multipart/form-data support)
    #sym:initialize_sample_gsn_datasets Reference implementation
    """
    logger.info(f"register_dataset_gsn: データセット '{datasetName}' の登録処理を開始します。")
    try:
        from src.gsn.register_dataset_for_gsn import RegisterDatasetForGSN
        import pandas as pd
        from io import StringIO

        # Convert file content to DataFrame
        data_text = file.file.read().decode("utf-8")
        dataset = pd.read_csv(StringIO(data_text), encoding="utf-8")

        # Load GSN YAML data
        gsn_yaml_data_list = RegisterDatasetForGSN.prepare_gsn_yaml_data()


        # Register for each GSN
        registered = []
        for yaml_data in gsn_yaml_data_list:
            register_gsn = RegisterDatasetForGSN(db, yaml_data, dataset)
            register_gsn.register_gsn_dataset()
            registered.append(yaml_data.get('name', 'unknown'))

        logger.info(f"register_dataset_gsn: データセット '{datasetName}' のGSN登録が完了しました。")
        return {"registered_gsn": registered, "name": datasetName}
    except Exception as e:
        logger.error(f"register_dataset_gsn: 登録処理中にエラーが発生しました: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/datasets/by_ids")
def get_datasets_by_ids(
    ids: List[int] = Body(..., embed=True),
    db: Session = Depends(get_db)
):
    """
    API to retrieve datasets by multiple IDs
    Request example: {"ids": [1,2,3]}
    """
    logger.info(f"get_datasets_by_ids: IDリスト {ids} のデータセット取得処理を開始します。")
    try:
        datasets = DatasetManager.get_by_ids(db, ids)
        result = [
            {"id": d.id, "name": d.name} for d in datasets
        ]
        logger.info(f"get_datasets_by_ids: {len(result)}件のデータセットを取得しました。")
        return {"datasets": result}
    except Exception as e:
        logger.error(f"get_datasets_by_ids: 取得処理中にエラーが発生しました: {e}")
        raise HTTPException(status_code=500, detail="データセット取得中にエラーが発生しました。")
