from .base import BaseAgent
from board import ConnectBoard, Player

# Minimax AI Agent with Alpha-Beta Pruning
class AlphaBetaAgent(BaseAgent):
    def __init__(self, depth: int = 4):
        self.depth = depth
        self.last_tree_data = {}

    def get_best_move(self, board: ConnectBoard, player: Player) -> int:
        # Implement Minimax with Alpha-Beta pruning here.
       return -1

    def get_last_search_tree(self) -> dict:
        return self.last_tree_data