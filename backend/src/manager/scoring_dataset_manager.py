from datetime import date
from src.db.define_tables import EvaluationResult, Dataset, AIModel, Evaluation
from sqlalchemy.orm import Session
from src.utils.logger import logger


class ScoringDatasetManager:
    @staticmethod
    def scoring_results(db: Session, data: dict, model_id: int) -> dict:
        """
        Execute quantitative evaluation by specifying dataset ID and model ID, and register the results to evaluation_result
        """
        from src.inspect.scoring_datasets import paraphrase_and_score
        import pickle
        from inspect_ai.scorer import model_graded_qa
        import json

        logger.info("scoring_results: 評価処理を開始します。")
        try:
            # model
            # NOTE: Model information includes API key and URL
            model = db.query(AIModel).filter_by(id=model_id).first()
            if model is None:
                logger.error("scoring_results: AIModelが見つかりません。")
                raise ValueError("AIModel not found")


            # Scorer is also fixed for now
            scorer = model_graded_qa()

            # Number of generations is also fixed for now
            n_paraphrases = 10

            # Evaluate question text
            logger.info("scoring_results: paraphrase_and_scoreを実行します。")
            results = paraphrase_and_score(
                data['question'], data['expected_answer'], model, scorer, n_paraphrases)

            # Format results
            paraphrase_results = []
            total_correct = 0
            for i, result_json in enumerate(results):
                try:
                    result_json = json.loads(result_json)
                    is_correct = result_json["samples"][0]["scores"]["model_graded_qa"]["value"]
                    p = result_json["samples"][0]["input"]
                except Exception as e:
                    logger.error(f"scoring_results: 結果のパースに失敗しました: {e}")
                    continue

                logger.info(f'scoring_results: 言い換え: {p}, 判定: {is_correct}')

                paraphrase_results.append({
                    "paraphrase": p,
                    "is_correct": is_correct
                })
                if is_correct == "C":
                    total_correct += 1

            scores = {
                "results": paraphrase_results,
                "total_correct": total_correct
            }
            logger.info(f"scoring_results: 評価処理が完了しました。合計正解数: {total_correct}")
            return scores
        except Exception as e:
            logger.error(f"scoring_results: 評価処理中にエラーが発生しました: {e}")
            return {"results": [], "total_correct": 0}
