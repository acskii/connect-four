from .base import BaseAgent
from board import ConnectBoard, Player

# Probabilities:
#   - 0.6 probability that disc falls in chosen column
#   - 0.2 for column on left (0.4 if only left is available)
#   - 0.2 for column on right (0.4 if only right is available)
class ExpectedMinimaxAgent(BaseAgent):
    def __init__(self, depth: int = 3):
        self.depth = depth
        self.last_tree_data = {}

    def get_best_move(self, board: ConnectBoard, player: Player) -> int:
        # Implement Expected Minimax handling chance nodes and slip probabilities here.
        return -1

    def get_last_search_tree(self) -> dict:
        return self.last_tree_data