from .base import BaseAgent
from board import ConnectBoard, Player

# Minimax without Alpha-Beta Pruning
class MinimaxAgent(BaseAgent):
    def __init__(self, depth: int = 4):
        self.depth = depth
        self.last_tree_data = {}

    def get_best_move(self, board: ConnectBoard, player: Player) -> int:
        # Implement minimax algorithm here.
        return -1

    def get_last_search_tree(self) -> dict:
        return self.last_tree_data