from src.db.define_tables import EvaluationPerspective, Dataset
from src.db.session import SessionLocal
from src.utils.logger import logger

"""
Class that recursively searches YAML for GoalStructureNotation(GNS)
"""


class GSNExplorer:
    """
    GSNExplorer is a class that recursively explores the YAML of GoalStructureNotation (GSN).
    """

    def __init__(self, yaml_data):
        """
        Constructor.
        :param yaml_data: YAML data of GSN
        """
        self.yaml_data = yaml_data
        self.results = []

    def explore(self, current_position="", second_goal="", current_score_rate=1.0):
        """
        Recursively explore YAML data and display hierarchical structures.
        The result will contain
        - leaf: Final question
        - score_rate: Score rate
        - second_goal: Definition of SecondGoal
        """
        logger.info(f"explore: current_position={current_position}, second_goal={second_goal}, current_score_rate={current_score_rate}")
        try:
            # Find the starting point for TopGoal search
            if current_position == "":
                # Initialization at first call
                self.results = []
                # Search TopGoal
                for key, node in self.yaml_data.items():
                    if node.get('goalType') == 'TopGoal':
                        next_position = node['supportedBy'][0]
                        self.explore(current_position=next_position,
                                     second_goal="",
                                     current_score_rate=1.0)
                        return self.results

            # See elements specified by supported_by
            node = self.yaml_data[current_position]
            scores = node.get('scoreRate')

            # print(f"current_position: {current_position}")
            # print(f"node: {node}")

            # If goalType is SecondGoal, set second_goal
            if node.get('goalType') == 'SecondGoal':
                second_goal = node.get('definition', '')

            # If leaf、add to result
            if node.get('undeveloped', False):
                self.results.append({
                    'ID': current_position,
                    'leaf': node.get('question', ''),
                    'score_rate': current_score_rate,
                    'second_goal': second_goal,
                })

            # If choice、continued search with no change in score
            # -> If a node has no score, the search continues without changing the score.
            # elif node.get('relationshipType') == 'choice':
            elif scores is None:
                for next_position in node.get('supportedBy', []):
                    self.explore(current_position=next_position,
                                 second_goal=second_goal,
                                 current_score_rate=current_score_rate,)

            # If it is just a node, update the score and continue the search
            else:
                for next_position, score_rate in zip(node.get('supportedBy', []), node.get('scoreRate', [])):
                    # If current_position is Sn-1 (n is an integer between 1 and 10), the first node directly connected from Top
                    if current_position.startswith('S') and current_position.endswith('-1'):
                        new_score_rate = 1.0 * score_rate
                    else:
                        new_score_rate = current_score_rate * score_rate
                    # print(f"next_position: {next_position}, score_rate: {score_rate}, new_score_rate: {new_score_rate}")
                    # Recursive search
                    self.explore(current_position=next_position,
                                second_goal=second_goal,
                                current_score_rate=new_score_rate,)
            logger.info(f"explore: current_position={current_position} の探索が完了しました。")
        except Exception as e:
            logger.error(f"explore: 探索処理中にエラーが発生しました: {e}")
            raise

    def get_gsn_data(self, perspective_id) -> list[Dataset]:
        """
        Obtains GSN data based on the specified evaluation viewpoint ID.
        :param perspective_id: ID of perspective 
        :return: GSN data list
        """
        logger.info(f"get_gsn_data: perspective_id={perspective_id} のGSNデータ取得処理を開始します。")
        try:
            # Implement logic to filter GSN data
            # Extract data from DB whose name starts with GSN and is associated with the corresponding perspective_id
            session = SessionLocal()
            gsn_datasets = session.query(Dataset).filter(
                Dataset.name.like("GSN_%"),
                Dataset.evaluation_perspective_id == perspective_id
            ).all()
            
            logger.info(f"get_gsn_data: {len(gsn_datasets)}件のGSNデータを取得しました。")
            return gsn_datasets
        except Exception as e:
            logger.error(f"get_gsn_data: 取得処理中にエラーが発生しました: {e}")
            return []
        finally:
            session.close()
