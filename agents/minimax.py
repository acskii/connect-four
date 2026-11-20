import time
from .base import BaseAgent
from .heuristic import evaluate_board, COLUMN_ORDER
from .tree_utils import SearchTreeMixin
from board import ConnectBoard, Player


def _other(p: Player) -> Player:
    return Player.Min if p == Player.Max else Player.Max


# Minimax without Alpha-Beta Pruning.
# Tree node labels name the side TO MOVE at that node, plus the column that led there,
# e.g. after Max plays col 3 the child is "MIN (col 3)".
class MinimaxAgent(BaseAgent, SearchTreeMixin):
    def __init__(self, depth: int = 4):
        self.depth = depth
        self.last_tree_data = {}
        self.nodes_expanded = 0
        self.last_execution_time = 0.0

    def get_best_move(self, board: ConnectBoard, player: Player) -> int:
        start = time.perf_counter()
        self.nodes_expanded = 1                      # count the root
        maximizing = player == Player.Max
        cols = [c for c in COLUMN_ORDER if c in board.get_available_columns()]

        best_col, best_val = -1, None
        children = []
        for c in cols:
            val, node = self._search(board.drop(player, c), self.depth - 1,
                                     _other(player), c)
            children.append(node)
            if best_val is None or (val > best_val if maximizing else val < best_val):
                best_val, best_col = val, c

        if best_val is None:                         # no moves (terminal board)
            best_val = evaluate_board(board)
        self.last_tree_data = {
            "node": f"ROOT ({'MAX' if maximizing else 'MIN'})",
            "score": round(float(best_val), 2),
            "children": children,
        }
        self.last_execution_time = time.perf_counter() - start
        self.print_search_tree()
        return best_col

    def _search(self, board, depth, to_move, col):
        self.nodes_expanded += 1
        if depth == 0 or board.is_terminal():
            v = evaluate_board(board)
            return v, {"node": f"LEAF (col {col})", "score": round(v, 2), "children": []}

        maximizing = to_move == Player.Max
        best, children = None, []
        for c in COLUMN_ORDER:
            if c not in board.get_available_columns():
                continue
            v, node = self._search(board.drop(to_move, c), depth - 1, _other(to_move), c)
            children.append(node)
            if best is None or (v > best if maximizing else v < best):
                best = v
        return best, {"node": f"{'MAX' if maximizing else 'MIN'} (col {col})",
                      "score": round(best, 2), "children": children}

    def get_last_search_tree(self) -> dict:
        return self.last_tree_data
