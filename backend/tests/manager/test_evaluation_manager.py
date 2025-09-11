import pytest
from src.manager.evaluation_manager import EvaluationManager
from src.db.define_tables import Dataset, EvaluationPerspective, DatasetCustomMapping, Evaluation, UseGSN
import datetime
from src.db.define_tables import CustomDatasets
from src.db.show_db import ShowDatabase

@pytest.mark.asyncio
async def test_register_evaluation_from_json(session):
    """
    Test whether Evaluation, EvaluationPerspective, DatasetCustomMapping are correctly registered by EvaluationManager.register_evaluation_from_json
    - Evaluation is created
    - EvaluationPerspective is created for each criteria
    - DatasetCustomMapping is created for quantitative/qualitative with correct prompt/percentage
    """
    # Prepare EvaluationPerspective in advance and specify evaluation_perspective_id for Dataset
    perspective1 = EvaluationPerspective(perspective_name="有害情報の出力制御")
    perspective2 = EvaluationPerspective(perspective_name="偽誤情報の出力・誘導の防止")
    session.add_all([perspective1, perspective2])
    session.commit()
    # Prepare Dataset in advance (both quantitative/qualitative)
    ds1 = Dataset(name="ds_quant1", data_content=b"A",
                  type="quantitative", evaluation_perspective_id=perspective1.id)
    ds2 = Dataset(name="ds_qual1", data_content=b"B",
                  type="qualitative", evaluation_perspective_id=perspective1.id)
    ds3 = Dataset(name="ds_quant2", data_content=b"C",
                  type="quantitative", evaluation_perspective_id=perspective2.id)
    session.add_all([ds1, ds2, ds3])
    session.commit()
    # Sample JSON
    data = {
        "evaluationName": "サンプル評価定義",
        "criteria": [
            {
                "criterion": "有害情報の出力制御",
                "quantitative": {
                    "checked": True,
                    "datasets": [ds1.id],
                    "percentage": 54,
                    "text": "サンプルプロンプトA"
                },
                "qualitative": {
                    "checked": True,
                    "questions": [ds2.id],
                    "percentage": 46
                }
            },
            {
                "criterion": "偽誤情報の出力・誘導の防止",
                "quantitative": {
                    "checked": True,
                    "datasets": [ds3.id],
                    "percentage": 100,
                    "text": "サンプルプロンプトB"
                },
                "qualitative": {
                    "checked": False,
                    "questions": [],
                    "percentage": 0
                }
            }
        ]
    }
    # Execute
    manager = EvaluationManager(session)
    evaluation = await manager.register_evaluation_from_json(data)
    # --- Check 1: Evaluation is created ---
    eval_obj = session.query(Evaluation).filter_by(name="サンプル評価定義").first()
    assert eval_obj is not None, "Evaluationが作成されていること"
    assert eval_obj.created_date.date() == datetime.date.today(), "created_dateが今日になっていること"
    # --- Check 2: EvaluationPerspective is created for each criteria ---
    perspectives = session.query(EvaluationPerspective).all()
    names = [p.perspective_name for p in perspectives]
    assert set(names) >= {"有害情報の出力制御",
                          "偽誤情報の出力・誘導の防止"}, "criteriaの観点が全て登録されていること"
    # --- Check 3: DatasetCustomMapping is created for quantitative/qualitative ---
    mappings = session.query(DatasetCustomMapping).all()
    assert len(mappings) == 3, "quantitative/qualitative分のマッピングが作成されていること"
    # --- Check 4: prompt/percentage is correct. ---
    m1 = session.query(DatasetCustomMapping).filter_by(
        dataset_id=ds1.id, prompt="サンプルプロンプトA").first()
    assert m1 is not None, "quantitativeのマッピングが存在すること"
    assert m1.percentage == 54, "quantitativeのpercentageが正しいこと"
    m2 = session.query(DatasetCustomMapping).filter_by(
        dataset_id=ds2.id, prompt=None).first()
    assert m2 is not None, "qualitativeのマッピングが存在すること"
    assert m2.percentage == 46, "qualitativeのpercentageが正しいこと"
    m3 = session.query(DatasetCustomMapping).filter_by(
        dataset_id=ds3.id, prompt="サンプルプロンプトB").first()
    assert m3 is not None, "quantitativeのマッピングが存在すること"
    assert m3.percentage == 100, "quantitativeのpercentageが正しいこと"
    # --- Check 5: ID duplication check ---
    all_ids = [ds1.id, ds2.id, ds3.id]
    assert len(all_ids) == len(set(all_ids)), "DatasetのIDが重複していないこと"
    session.close()

@pytest.mark.asyncio
async def test_register_evaluation_from_json_gsn(session):
    """
    Test whether GSN-related (UseGSN) is correctly registered by EvaluationManager.register_evaluation_from_json
    - Evaluation is created
    - EvaluationPerspective is created for each criteria
    - DatasetCustomMapping is created for quantitative/qualitative
    - UseGSN is created for each criteria
    """
    perspective_str1 = "有害情報の出力制御"
    perspective_str2 = "公平性と包摂性"
    # Prepare EvaluationPerspective in advance and specify evaluation_perspective_id for Dataset
    perspective1 = EvaluationPerspective(perspective_name=perspective_str1)
    perspective2 = EvaluationPerspective(perspective_name=perspective_str2)
    session.add_all([perspective1, perspective2])
    session.commit()
    # Prepare Dataset in advance
    ds1 = Dataset(name="gsn_ds1", data_content=b"A", type="quantitative", evaluation_perspective_id=perspective1.id)
    ds2 = Dataset(name="gsn_ds2", data_content=b"B", type="qualitative", evaluation_perspective_id=perspective2.id)
    session.add_all([ds1, ds2])
    session.commit()
    # Create Evaluation and establish connection with UseGSN
    custom_dataset = CustomDatasets(name="GSN用カスタムデータセット")
    session.add(custom_dataset)
    session.commit()
    evaluation = Evaluation(
        name="GSN評価定義",
        created_date=datetime.datetime.now(),
        custom_datasets_id=custom_dataset.id
    )
    session.add(evaluation)
    session.commit()
    # Create UseGSN for each criteria
    use_gsn1 = UseGSN(
        evaluation_id=evaluation.id,
        evaluation_perspective_id=perspective1.id,
    )
    use_gsn2 = UseGSN(
        evaluation_id=evaluation.id,
        evaluation_perspective_id=perspective2.id,
    )
    session.add_all([use_gsn1, use_gsn2])
    session.commit()

    
    

    # Sample JSON for GSN
    data = {
        "evaluationName": "GSN評価定義",
        "criteria": [
            {
                "criterion": perspective_str1,
                "quantitative": {
                    "checked": True,
                    "datasets": [ds1.id],
                    "percentage": 60,
                    "text": "GSNプロンプトA"
                },
                "qualitative": {
                    "checked": False,
                    "questions": [],
                    "percentage": 0
                },
                "use_gsn": True
            },
            {
                "criterion": perspective_str2,
                "quantitative": {
                    "checked": False,
                    "datasets": [],
                    "percentage": 0,
                    "text": None
                },
                "qualitative": {
                    "checked": True,
                    "questions": [ds2.id],
                    "percentage": 40
                },
                "use_gsn": False
            }
        ]
    }
    # Execute
    manager = EvaluationManager(session)
    evaluation = await manager.register_evaluation_from_json(data)
    # --- Check 1: Evaluation is created ---
    eval_obj = session.query(Evaluation).filter_by(name="GSN評価定義").first()
    assert eval_obj is not None, "Evaluationが作成されていること"
    assert eval_obj.created_date.date() == datetime.date.today(), "created_dateが今日になっていること"
    # --- Check 2: EvaluationPerspective is created only for criteria ---
    perspectives = session.query(EvaluationPerspective).all()
    names = [p.perspective_name for p in perspectives]
    assert set(names) >= {perspective_str1, perspective_str2}, "criteriaの観点が全て登録されていること"
    ShowDatabase(session).show_all_tables()