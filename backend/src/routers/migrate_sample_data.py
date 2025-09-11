from fastapi import APIRouter, HTTPException
from src.db.migrate_sample_data import initialize_sample_data

router = APIRouter()


@router.post("/migrate-sample-data-initialize")
def migrate_sample_data_initialize():
    try:
        initialize_sample_data()
        return {"message": "サンプルデータの初期化が完了しました。"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"初期化中にエラー: {e}")
