from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.manager.scoring_dataset_manager import ScoringDatasetManager
from src.db.session import get_db
from typing import List, Dict
from pydantic import BaseModel
from src.utils.logger import logger

router = APIRouter()

class ScoringRequest(BaseModel):
    question: str
    expected_answer: str
    model_id: int

@router.post("/scoring-dataset")
def scoring_dataset(request: ScoringRequest, db: Session = Depends(get_db)):
    logger.info("scoring_dataset: スコアリングリクエストの処理を開始します。")
    model_id = request.model_id
    data = {
        "question": request.question,
        "expected_answer": request.expected_answer
    }
    try:
        scoring_results = ScoringDatasetManager.scoring_results(db, data, model_id)
        logger.info("scoring_dataset: スコアリング処理が完了しました。")
        return scoring_results
    except Exception as e:
        logger.error(f"scoring_dataset: スコアリング処理中にエラーが発生しました: {e}")
        raise HTTPException(status_code=500, detail="スコアリング処理中にエラーが発生しました")
