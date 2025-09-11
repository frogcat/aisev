import pandas as pd
from inspect_ai import Task, eval
from inspect_ai.dataset import Sample
from inspect_ai.solver import generate, Solver, multiple_choice
from inspect_ai.scorer import exact, model_graded_qa, Scorer
from pathlib import Path
from inspect_ai.log import read_eval_log, EvalLog
from inspect_ai.log._file import eval_log_json_str, eval_log_json
import os
from src.utils.logger import logger

root_dir = Path(__file__).parent.parent.parent
data_dir = root_dir / 'dataset' / 'output'
log_dir = root_dir / 'logs'
inspect_ai_log_dir = root_dir / 'logs/inspect_ai'
os.makedirs(inspect_ai_log_dir, exist_ok=True)


def load_samples_from_csv(csv_path):
    logger.info(f"CSVファイル {csv_path} からサンプルを読み込みます。")
    df = pd.read_csv(csv_path)
    samples = [Sample(input=row['text'], target=row['output'])
               for _, row in df.iterrows()]
    logger.info(f"サンプルの読み込みが完了しました。件数: {len(samples)}")
    return samples


def new_eval_by_ten_perspective(df: pd.DataFrame, target_model_name: str, scorer: Scorer, eval_type: str):
    import json
    logger.info("new_eval_by_ten_perspective: 10観点ごとの新しい評価を開始します。")

    # If row has NaN, remove it
    logger.debug(f"df: {df}")
    logger.debug(f"df columns: {df.columns}")

    if 'text' in df.columns:
        df = df.dropna(subset=['text'])
        logger.debug(f"NaNを含む'text'列を削除しました。残りの行数: {len(df)}")
    if 'output' in df.columns:
        # If all output is NaN, remove 'output' column
        if df['output'].isnull().all():
            df = df.drop(columns=['output'])
            logger.debug("全ての'output'列がNaNのため、列を削除しました。")
        else:
            df = df.dropna(subset=['output'])
            logger.debug(f"NaNを含む'output'列を削除しました。残りの行数: {len(df)}")
    if 'ten_perspective' in df.columns:
        df = df.dropna(subset=['ten_perspective'])
        logger.debug(f"NaNを含む'ten_perspective'列を削除しました。残りの行数: {len(df)}")
    if 'requirement' in df.columns:
        if df['requirement'].isnull().all():
            df = df.drop(columns=['requirement'])
            logger.debug("全ての'requirement'列がNaNのため、列を削除しました。")
        else:
            df = df.dropna(subset=['requirement'])
            logger.debug(f"NaNを含む'requirement'列を削除しました。残りの行数: {len(df)}")
    if 'gsn_perspective' in df.columns:
        df = df.dropna(subset=['gsn_perspective'])
        logger.debug(f"NaNを含む'gsn_perspective'列を削除しました。残りの行数: {len(df)}")


    results = {}
    for perspective in df["ten_perspective"].dropna().unique():
        logger.info(f"観点: {perspective} の評価を開始します。")
        sub_df = df[df["ten_perspective"] == perspective]
        if sub_df.empty:
            logger.info(f"観点: {perspective} のデータが空です。スキップします。")
            continue
        try:
            if eval_type in ["multiple_choice_eval"]:
                def parse_choices(df: pd.DataFrame):
                    import pandas as pd
                    # Get ans columns and convert to list excluding nan values
                    ans_cols = df.filter(like='ans')
                    choices_list = []
                    for _, row in ans_cols.iterrows():
                        choices = [str(val)
                                   for val in row.values if pd.notna(val)]
                        choices_list.append(choices)
                    df['choices'] = choices_list
                    return df
                # NOTE: multiple_choice target is in ABC order of choices (e.g. when answer is 2, choices=[1,2,3], target="B")
                if 'choices' not in sub_df.columns:
                    sub_df = parse_choices(sub_df)
                samples = [Sample(input=row['text'], target=row['output'],
                                  choices=row['choices']) for _, row in sub_df.iterrows()]
                task = Task(dataset=samples, solver=[
                            multiple_choice()], scorer=scorer)
            elif eval_type == "requirement_eval":
                # NOTE: Use requirement column as target
                samples = [Sample(input=row['text'], target=row['requirement'])
                           for _, row in sub_df.iterrows()]
                task = Task(dataset=samples, solver=[
                            generate()], scorer=scorer)
            else:
                # NOTE: If not specified, use output as target and check semantic match with expected answer
                samples = [Sample(input=row['text'], target=row['output'])
                           for _, row in sub_df.iterrows()]
                task = Task(dataset=samples, solver=[
                            generate()], scorer=scorer)
            eval_result = eval(task, model=target_model_name,
                               log_format="json", log_dir=str(inspect_ai_log_dir))
            # Add GSN information to eval_results[0][sample]
            # eval_log = eval_log_json_str(eval_result[0])
            eval_log = json.loads(eval_log_json_str(eval_result[0]))
            logger.debug(f"sub_df: {sub_df.columns}")
            logger.debug(f"eval_log: {eval_log.get('samples')[0]}")
            # gsn_perspectiveをも持っていれば
            if 'gsn_perspective' in sub_df.columns and eval_log.get('samples'):
                logger.debug(f"sub_df: {sub_df}")
                # Reset index to ensure proper alignment
                sub_df_reset = sub_df.reset_index(drop=True)
                # Add gsn_perspective to each corresponding sample
                for i, sample in enumerate(eval_log.get('samples', [])):
                    if i < len(sub_df_reset):
                        gsn_perspective = sub_df_reset.iloc[i]['gsn_perspective']
                        # Handle both string and list cases
                        if pd.notna(gsn_perspective):
                            if isinstance(gsn_perspective, str):
                                # If it's a string, try to parse as list or use as single item
                                try:
                                    # Try to parse as JSON list first
                                    import ast
                                    parsed = ast.literal_eval(gsn_perspective)
                                    if isinstance(parsed, list):
                                        sample['gsn_perspective'] = parsed
                                    else:
                                        sample['gsn_perspective'] = [gsn_perspective]
                                except (ValueError, SyntaxError):
                                    # If parsing fails, treat as single string
                                    sample['gsn_perspective'] = [gsn_perspective]
                            elif isinstance(gsn_perspective, list):
                                sample['gsn_perspective'] = gsn_perspective
                            else:
                                sample['gsn_perspective'] = [str(gsn_perspective)]
                        else:
                            sample['gsn_perspective'] = []
                logger.debug(f"Updated eval_log samples with individual gsn_perspective")
                # eval_log.get['samples']['gsn_name'] = sub_df['ID']
            results[perspective] = json.dumps(eval_log)
            logger.debug(f"evallog: {eval_log}")
            logger.info(f"観点: {perspective} の評価が完了しました。")
        except Exception as e:
            logger.error(f"観点: {perspective} の評価中にエラーが発生しました: {e}")
    logger.info("new_eval_by_ten_perspective: 全観点の評価が完了しました。")
    return results


def extract_scores_from_log(log: EvalLog):
    logger.info("extract_scores_from_log: スコア抽出を開始します。")
    try:
        accuracy = log[0].results.scores[0].metrics['accuracy'].value
        logger.info(f"extract_scores_from_log: 抽出したaccuracy: {accuracy}")
        return accuracy
    except Exception as e:
        logger.error(f"extract_scores_from_log: スコア抽出中にエラーが発生しました: {e}")
        return None


def load_sample_data() -> pd.DataFrame:
    """
    dev has around 3000, test has around 300
    """
    # dev_csv = data_dir / 'labeled-dev-00000-of-00001.csv'
    test_csv = data_dir / 'labeled-test-00000-of-00001.csv'

    df = pd.read_csv(test_csv)
    n = 5
    df = df.sample(n, random_state=42)
    return df


def main():

    df = load_sample_data()
    model = "mockllm/model"
    # model= "openai/gpt-4o-mini"

    results = new_eval_by_ten_perspective(
        df, model=model, scorer=model_graded_qa())
    print(results)

    for perspective, result in results.items():
        print(
            f"Perspective: {perspective}, Accuracy: {extract_scores_from_log(result)}")



if __name__ == "__main__":
    main()
