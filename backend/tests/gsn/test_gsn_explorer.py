import yaml
from pathlib import Path
from src.gsn.gsn_explorer import GSNExplorer

GSN_LIST = [
    "01_Control_of_Toxic_Output_GSN.yaml",
    "02_Prevention_of_Misinformation_Disinformation_and_Manipulation_GSN.yaml",
    "03_Fairness_and_Inclusion_GSN.yaml",
    "04_Addressing_High-risk_Use_and_Unintended_Use_GSN.yaml",
    "05_Privacy_Protection_GSN.yaml",
    "06_Ensuring_Security_GSN.yaml",
    "07_Explainability_GSN.yaml",
    "08_Robustness_GSN.yaml",
    "09_Data_Quality_GSN.yaml",
    "10_Verifiability_GSN.yaml",
]

def test_explore_10_Verifiability_GSN():
    root = Path(__file__).parent.parent.parent
    gsn_dir = root / 'src' / 'gsn'
    yaml_file = gsn_dir / GSN_LIST[9]
    with open(yaml_file, 'r') as f:
        content = f.read().replace('\x0b', '')
        yaml_data = yaml.safe_load(content)

    # One of the ideal result
    ideal_result = {
        'leaf': "組織外で開発されたAIモデルの設計についての情報を入手し、AIモデルの設計が検証可能になっているか",
        'score_rate': 0.15 * 0.4,
        'second_goal': 'SG: AIモデルの設計・学習に関する検証可能性の確保'
    }

    explorer = GSNExplorer(yaml_data)
    results = explorer.explore()
    print(f"Results: {results}")
    assert len(results) > 0, "Results should not be empty"
    for result in results:
        if result.get('leaf') == ideal_result.get('leaf'):
            assert result['score_rate'] == ideal_result['score_rate']
            assert result['second_goal'] == ideal_result['second_goal']
            break

    # Confirm that the total score_rate in RESULTS is 1.4 (because 0.4 is double-counted in CHOICE).
    total_score_rate = sum([result['score_rate'] for result in results])
    assert abs(total_score_rate -
               1.4) < 1e-8, f"Total score rate should be 1.4, but got {total_score_rate}"
    print(f"Total score rate: {total_score_rate}")

def test_print_parsed_result():
    root = Path(__file__).parent.parent.parent
    gsn_dir = root / 'src' / 'gsn'
    num_leaf = [52,18,38,7,8,11,5,7,61,19]
    for gsn_num in range(0,10):
        yaml_file = gsn_dir / GSN_LIST[gsn_num]
        with open(yaml_file, 'r') as f:
            content = f.read().replace('\x0b', '')
            yaml_data = yaml.safe_load(content)

        explorer = GSNExplorer(yaml_data)
        results = explorer.explore()
        
        print(f"print results idx{gsn_num}: len(results) = {len(results)}")
        assert len(results) == num_leaf[gsn_num], f"Results should have {num_leaf[gsn_num]} items, but got {len(results)}"
        # for result in results:
        #     print(f"ID: {result['ID']}, Leaf: {result['leaf']}, "
        #           f"Score Rate: {result['score_rate']}, Second Goal: {result['second_goal']}")


    

def test_get_gsn_data():
    explorer = GSNExplorer(yaml_data={})
    result = explorer.get_gsn_data(1)
    return None
