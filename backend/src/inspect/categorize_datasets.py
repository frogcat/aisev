import asyncio
import pandas as pd
from pathlib import Path
from inspect_ai.model import get_model, Model
from dotenv import load_dotenv
from src.utils.logger import logger

load_dotenv()

root = Path(__file__).parent.parent.parent
data_dir = root / "dataset"
data_output_dir = data_dir / "output"

harm_categories = {
    "有害情報の出力制御": [
        "{'harm-type': 'AIの擬人化', 'risk-area': 'AIとの対話によるリスク', 'specific-harm': 'AIへの感情的依存'}",
        "{'harm-type': 'メンタルヘルス', 'risk-area': 'AIとの対話によるリスク', 'specific-harm': '一般的なメンタルヘルス'}",
        "{'harm-type': 'メンタルヘルス', 'risk-area': 'AIとの対話によるリスク', 'specific-harm': '不安やうつ'}",
        "{'harm-type': 'メンタルヘルス', 'risk-area': 'AIとの対話によるリスク', 'specific-harm': '心的症状'}",
        "{'harm-type': 'メンタルヘルス', 'risk-area': 'AIとの対話によるリスク', 'specific-harm': '自傷行為'}",
        "{'harm-type': 'アダルト', 'risk-area': 'バイアス・差別・ヘイト・反公序良俗', 'specific-harm': '暴力表現'}",
        "{'harm-type': 'アダルト', 'risk-area': 'バイアス・差別・ヘイト・反公序良俗', 'specific-harm': '露骨な性表現・わいせつ'}",
        "{'harm-type': '非倫理的行為への加担', 'risk-area': '悪用', 'specific-harm': 'ネットいじめの幇助'}",
        "{'harm-type': '非倫理的行為への加担', 'risk-area': '悪用', 'specific-harm': 'ネット荒らし行為'}",
        "{'harm-type': '非倫理的行為への加担', 'risk-area': '悪用', 'specific-harm': '不適切行為'}",
        "{'harm-type': '非倫理的行為への加担', 'risk-area': '悪用', 'specific-harm': '中傷・名誉毀損の幇助'}"
    ],
    "偽誤情報の出力・誘導の防止": [
        "{'harm-type': '偽情報拡散への加担', 'risk-area': '悪用', 'specific-harm': 'スパム作成'}",
        "{'harm-type': '偽情報拡散への加担', 'risk-area': '悪用', 'specific-harm': '偽情報'}",
        "{'harm-type': '偽情報拡散への加担', 'risk-area': '悪用', 'specific-harm': '悪意のある情報操作'}",
        "{'harm-type': '誤情報による実被害', 'risk-area': '誤情報', 'specific-harm': 'その他専門分野の相談'}",
        "{'harm-type': '誤情報による実被害', 'risk-area': '誤情報', 'specific-harm': '医療相談'}",
        "{'harm-type': '誤情報による実被害', 'risk-area': '誤情報', 'specific-harm': '法律相談'}",
        "{'harm-type': '誤情報による実被害', 'risk-area': '誤情報', 'specific-harm': '金融相談'}",
        "{'harm-type': '誤情報の拡散', 'risk-area': '誤情報', 'specific-harm': 'うわさ・フェイクニュース'}",
        "{'harm-type': '誤情報の拡散', 'risk-area': '誤情報', 'specific-harm': 'プロバガンダ'}",
        "{'harm-type': '誤情報の拡散', 'risk-area': '誤情報', 'specific-harm': '危険行為'}",
        "{'harm-type': '誤情報の拡散', 'risk-area': '誤情報', 'specific-harm': '誤った文脈・背景'}"
    ],
    "公平性と包摂性": [
        "{'harm-type': 'ステレオタイプ・差別の助長', 'risk-area': 'バイアス・差別・ヘイト・反公序良俗', 'specific-harm': 'その他のバイアス・差別'}",
        "{'harm-type': 'ステレオタイプ・差別の助長', 'risk-area': 'バイアス・差別・ヘイト・反公序良俗', 'specific-harm': '人種バイアス・差別'}",
        "{'harm-type': 'ステレオタイプ・差別の助長', 'risk-area': 'バイアス・差別・ヘイト・反公序良俗', 'specific-harm': '地域バイアス・差別'}",
        "{'harm-type': 'ステレオタイプ・差別の助長', 'risk-area': 'バイアス・差別・ヘイト・反公序良俗', 'specific-harm': '宗教バイアス・差別'}",
        "{'harm-type': 'ステレオタイプ・差別の助長', 'risk-area': 'バイアス・差別・ヘイト・反公序良俗', 'specific-harm': '性別バイアス・差別'}",
        "{'harm-type': 'ステレオタイプ・差別の助長', 'risk-area': 'バイアス・差別・ヘイト・反公序良俗', 'specific-harm': '文化的特有性'}",
        "{'harm-type': 'ステレオタイプ・差別の助長', 'risk-area': 'バイアス・差別・ヘイト・反公序良俗', 'specific-harm': '肉体的特徴に基づく差別'}",
        "{'harm-type': 'ステレオタイプ・差別の助長', 'risk-area': 'バイアス・差別・ヘイト・反公序良俗', 'specific-harm': '障がいに基づく差別'}",
        "{'harm-type': 'ヘイトスピーチ', 'risk-area': 'バイアス・差別・ヘイト・反公序良俗', 'specific-harm': 'その他悪質な脅しや嫌がらせ'}",
        "{'harm-type': 'ヘイトスピーチ', 'risk-area': 'バイアス・差別・ヘイト・反公序良俗', 'specific-harm': '侮辱・名誉棄損'}",
        "{'harm-type': 'ヘイトスピーチ', 'risk-area': 'バイアス・差別・ヘイト・反公序良俗', 'specific-harm': '卑語'}"
    ],
    "ハイリスク利用・目的外利用への対処": [
        "{'harm-type': '違法行為への加担', 'risk-area': '悪用', 'specific-harm': 'デジタル空間の違法行為'}",
        "{'harm-type': '違法行為への加担', 'risk-area': '悪用', 'specific-harm': 'テロリズム'}",
        "{'harm-type': '違法行為への加担', 'risk-area': '悪用', 'specific-harm': '動物虐待・密猟'}",
        "{'harm-type': '違法行為への加担', 'risk-area': '悪用', 'specific-harm': '性的虐待・違法ポルノ'}",
        "{'harm-type': '違法行為への加担', 'risk-area': '悪用', 'specific-harm': '肉体的暴力・虐待'}",
        "{'harm-type': '違法行為への加担', 'risk-area': '悪用', 'specific-harm': '脅し・恐喝'}",
        "{'harm-type': '違法行為への加担', 'risk-area': '悪用', 'specific-harm': '著作権侵害'}",
        "{'harm-type': '違法行為への加担', 'risk-area': '悪用', 'specific-harm': '薬物・アルコール中毒'}",
        "{'harm-type': '違法行為への加担', 'risk-area': '悪用', 'specific-harm': '違法取引・人身売買'}",
        "{'harm-type': '違法行為への加担', 'risk-area': '悪用', 'specific-harm': '違法薬物'}",
        "{'harm-type': '違法行為への加担', 'risk-area': '悪用', 'specific-harm': '違法金銭行為'}",
        "{'harm-type': '違法行為への加担', 'risk-area': '悪用', 'specific-harm': '非合法的な偵察・検閲'}",
        "{'harm-type': '非倫理的行為への加担', 'risk-area': '悪用', 'specific-harm': '危険行為への誘導'}"
    ],
    "プライバシー保護": [
        "{'harm-type': 'AIの擬人化', 'risk-area': 'AIとの対話によるリスク', 'specific-harm': '個人情報の聞き出し'}",
        "{'harm-type': '個人情報漏洩', 'risk-area': '情報漏洩', 'specific-harm': 'PII'}",
        "{'harm-type': '個人情報漏洩', 'risk-area': '情報漏洩', 'specific-harm': 'その他個人情報'}",
        "{'harm-type': '個人情報漏洩', 'risk-area': '情報漏洩', 'specific-harm': 'バイオメトリクス'}",
        "{'harm-type': '個人情報漏洩', 'risk-area': '情報漏洩', 'specific-harm': 'ファイナンス'}",
        "{'harm-type': '個人情報漏洩', 'risk-area': '情報漏洩', 'specific-harm': '医療'}",
        "{'harm-type': '個人情報漏洩', 'risk-area': '情報漏洩', 'specific-harm': '教育'}"
    ],
    "セキュリティ確保": [
        "{'harm-type': '組織・国家機密漏洩', 'risk-area': '情報漏洩', 'specific-harm': 'サイバーセキュリティ'}",
        "{'harm-type': '組織・国家機密漏洩', 'risk-area': '情報漏洩', 'specific-harm': '機密情報へのアクセス'}"
    ],
    "説明可能性": [],
    "ロバスト性": [],
    "データ品質": [],
    "検証可能性": []
}


def categorize_data(data_name: str) -> pd.DataFrame:
    """
    Categorizes the data based on the provided harm categories.

    Args:
        data_name (str): The name of the dataset to categorize.

    Returns:
        pd.DataFrame: A DataFrame with an additional column for the category.
    """
    logger.info(f"categorize_data: {data_name} の読み込みを開始します。")
    df = pd.read_parquet(data_dir / data_name)

    def get_ten_perspective(meta_str):
        for category, items in harm_categories.items():
            if meta_str in items:
                return category
        return None

    df["ten_perspective"] = df["meta"].apply(
        lambda x: get_ten_perspective(str(x)))
    logger.info(f"categorize_data: {data_name} の分類が完了しました。")
    return df


class DataCategorizer():

    def __init__(self, model: Model):
        self.model = model
        self.gsn_list = [
            # "01_Control_of_Toxic_Output_GSN.yaml",
            # "02_Prevention_of_Misinformation_Disinformation_and_Manipulation_GSN.yaml",
            # "03_Fairness_and_Inclusion_GSN.yaml",
            # "04_Addressing_High-risk_Use_and_Unintended_Use_GSN.yaml",
            # "05_Privacy_Protection_GSN.yaml",
            # "06_Ensuring_Security_GSN.yaml",
            "07_Explainability_GSN.yaml",
            # "08_Robustness_GSN.yaml",
            # "09_Data_Quality_GSN.yaml",
            # "10_Verifiability_GSN.yaml",
        ]
        logger.info("DataCategorizerの初期化が完了しました。")

    def load_perspective_details(self):
        """
        Load perspective details from the directory.
        """
        logger.info("観点詳細の読み込みを開始します。")
        perspective_details_dir = data_dir / "perspective_details"
        perspective_details = ""
        for file_path in sorted(perspective_details_dir.glob("*")):
            if file_path.is_file():
                with open(file_path, "r", encoding="utf-8") as f:
                    perspective_details += f"観点{file_path.stem}:" + \
                        f.read() + "\n"
        logger.info("観点詳細の読み込みが完了しました。")
        return perspective_details

    async def categorize_data_with_input_output(self, input: str, output: str) -> str:
        logger.info("categorize_data_with_input_output: プロンプト生成・推論を開始します。")
        prompt = f"""
        以下の観点の説明を参考に、与えられたデータの入力と出力に基づいて、どの観点に該当するかを
        厳密に一致する観点名を返してください。

        観点の説明:
        {self.load_perspective_details()}
        ======================================

        データの入力: {input}
        データの出力: {output}
        """
        try:
            res = await self.model.generate(prompt)
        except Exception as e:
            logger.error(
                f"categorize_data_with_input_output: 推論中にエラーが発生しました: {e}")
            return None
        logger.info("categorize_data_with_input_output: 推論が完了しました。")
        return res

    async def categorize_data_with_input_output_GSN(self, input: str, output: str, leaves: list[str], leaf_IDs: list[str]) -> str:
        """
        Parse GSN YAML to terminal nodes and select the data most suitable for that goal
        """
        logger.info("categorize_data_with_input_output_GSN: プロンプト生成・推論を開始します。")
        leaves_info = "\n".join([
            f"ID: {leaf_id}, leaf: {leaf}"
            for leaf, leaf_id in zip(leaves, leaf_IDs)
        ])

        prompt = f"""
        以下の観点の説明を参考に、与えられたデータの入力と出力に基づいて、どの観点に該当するかを考えて、
        Gから始まるIDのみを１つだけ返してください。ID:なども不要です。
        もしどれにも該当しない場合はNoneと返してください。

        観点の説明:
        {leaves_info}
        ======================================

        データの入力: {input}
        データの出力: {output}
        """
        try:
            res = await self.model.generate(prompt)
        except Exception as e:
            logger.error(
                f"categorize_data_with_input_output_GSN: 推論中にエラーが発生しました: {e}")
            return None
        logger.info("categorize_data_with_input_output_GSN: 推論が完了しました。")
        return res

    async def exec_categorize_data(self, df: pd.DataFrame):
        """
        Collect all terminal data from all perspectives and assign one terminal data to each data entry
        """
        import yaml
        from src.gsn.gsn_explorer import GSNExplorer

        logger.info("exec_categorize_data: GSNファイルの読み込みを開始します。")
        results = []
        all_leaves = []
        all_IDs = []
        for gsn_file in self.gsn_list:
            try:
                with open(root / "src" / "gsn" / gsn_file, "r", encoding="utf-8") as f:
                    content = f.read().replace('\x0b', '')
                    yaml_data = yaml.safe_load(content)
                explorer = GSNExplorer(yaml_data)
                results = explorer.explore()
                leaves = [r["leaf"] for r in results]
                IDs = [r["ID"] for r in results]
                all_leaves.extend(leaves)
                all_IDs.extend(IDs)
            except Exception as e:
                logger.error(
                    f"exec_categorize_data: {gsn_file} の読み込み・パースでエラー: {e}")
                continue
        logger.info("exec_categorize_data: GSNファイルの読み込みが完了しました。")

        logger.info("exec_categorize_data: データセットの観点分類を非同期で実行します。")
        try:
            tasks = [
                self.categorize_data_with_input_output_GSN(
                    input=row["text"],
                    output=row["output"],
                    leaves=all_leaves,
                    leaf_IDs=all_IDs
                )
                for _, row in df.iterrows()
            ]
            res = await asyncio.gather(*tasks)
        except Exception as e:
            logger.error(f"exec_categorize_data: 観点分類の非同期実行でエラー: {e}")
            return None

        gsn_categories = [
            r.choices[0].message.content if r else None for r in res]
        logger.info("exec_categorize_data: 全データの観点分類が完了しました。")
        return gsn_categories

    @staticmethod
    def fix_ten_perspective_column(input_csv_path: str, perspective_col: str = "ten_perspective"):
        """
        Remove the '観点n:' part from the perspective column (default: ten_perspective) of the specified CSV file,
        and save the modified data with '_fix' suffix in the same folder.
        """
        import re
        from src.utils.logger import logger
        logger.info(f"fix_ten_perspective_column: {input_csv_path} の修正を開始します。")
        try:
            df = pd.read_csv(input_csv_path)

            def clean_perspective(val):
                if pd.isnull(val):
                    return val
                return re.sub(r'^観点\d+:', '', str(val)).strip()
            df[perspective_col] = df[perspective_col].apply(clean_perspective)
            output_path = Path(input_csv_path).with_name(
                f"{Path(input_csv_path).stem}_fix{Path(input_csv_path).suffix}")
            df.to_csv(output_path, index=False)
            logger.info(
                f"fix_ten_perspective_column: 修正済みファイルを保存しました: {output_path}")
        except Exception as e:
            logger.error(f"fix_ten_perspective_column: 修正処理でエラー: {e}")


async def main_gsn():
    """
    Main function to categorize the datasets using GSN.
    """
    logger.info("main_gsn: GSN分類処理を開始します。")
    try:
        # input_file_name = "test-00000-of-00001.parquet"
        # output_file_name = "categorized-test-00000-of-00001_gsn.csv"
        # input_file_name = "dev-00000-of-00001.parquet"
        # output_file_name = "categorized-dev-00000-of-00001_gsn.csv"
        # df = pd.read_parquet(data_dir / input_file_name)

        # input_file_name = "AutoRT_Hirisk.csv"
        # output_file_name = "AutoRT_Hirisk_gsn.csv"

        # input_file_name = "AutoRT_robust.csv"
        # output_file_name = "AutoRT_robust_gsn.csv"

        input_file_name = "theory_of_mind_ja.csv"
        output_file_name = "theory_of_mind_ja_gsn.csv"
        df = pd.read_csv(data_output_dir / input_file_name)

        model = get_model(
            "openai/gpt-4o-mini",
        )
        categorizer = DataCategorizer(model)
        gsn_categories = await categorizer.exec_categorize_data(df)
        df["gsn_perspective"] = gsn_categories
        df.to_csv(data_output_dir / output_file_name, index=False)
        logger.info("main_gsn: GSN分類処理が完了しました。")
    except Exception as e:
        logger.error(f"main_gsn: エラーが発生しました: {e}")


async def main():
    """
    Main function to categorize the datasets and save the results.
    """
    logger.info("main: 10観点分類処理を開始します。")
    try:
        df = pd.read_parquet(data_dir / "test-00000-of-00001.parquet")
        model = get_model(
            "openai/gpt-4o-mini",
        )
        categorizer = DataCategorizer(model)
        tasks = [
            categorizer.categorize_data_with_input_output(
                input=row["text"],
                output=row["output"]
            )
            for _, row in df.iterrows()
        ]
        res = await asyncio.gather(*tasks)
        perspective_categories = [
            r.choices[0].message.content if r else None for r in res]
        logger.info(f"main: 分類結果: {perspective_categories}")
        df["ten_perspective"] = perspective_categories
        logger.info("main: DataFrameへの列追加が完了しました。")
        df.to_csv(data_output_dir /
                  "categorized-test-00000-of-00001.csv", index=False)
        logger.info("main: 10観点分類処理が完了しました。")
    except Exception as e:
        logger.error(f"main: エラーが発生しました: {e}")


def extract_ID_and_perspective_from_answercarefully_data():
    """
    Extract ID and perspectives (ten_perspective, gsn_perspective) from the dataset and save to CSV file.
    """
    data_type = "dev"  # or "test"
    df = pd.read_csv(data_output_dir /
                     f"categorized_{data_type}_gsn_ten_perspective.csv")
    extracted_data = df[["ID", "ten_perspective", "gsn_perspective"]]
    extracted_data.to_csv(
        data_output_dir / f"extracted_ID_and_perspective_{data_type}.csv", index=False)


def add_ten_perspective_from_gsn_perspective():
    """
    Add ten_perspective column from gsn_perspective column.
    The first 2 characters 'Gn' in gsn_perspective column represent the perspective number n, which is replaced with the perspective string.
    """
    ten_perspective_map = {
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
    # filename = "categorized-dev-00000-of-00001_gsn.csv"
    input_file_name = "theory_of_mind_ja_gsn.csv"
    output_file_name = "theory_of_mind_ja_ten_perspective.csv"
    df = pd.read_csv(data_output_dir / input_file_name)

    def get_ten_perspective_from_gsn(x):
        if pd.isnull(x):
            return None
        key = x[:3] if x.startswith("G10") else x[:2]
        return ten_perspective_map.get(key, None)
    df["ten_perspective"] = df["gsn_perspective"].apply(
        get_ten_perspective_from_gsn)
    df.to_csv(data_output_dir / output_file_name, index=False)


if __name__ == "__main__":
    logger.info("__main__: プログラムの実行を開始します。")
    try:
        # asyncio.run(main())
        asyncio.run(main_gsn())
        add_ten_perspective_from_gsn_perspective()
        # extract_ID_and_perspective_from_answercarefully_data()

    except Exception as e:
        logger.error(f"__main__: 実行時エラー: {e}")
