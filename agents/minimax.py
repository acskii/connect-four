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
        self.depth = max(1, int(depth))
        self.last_tree_data = {}
        self.nodes_expanded = 0
        self.last_execution_time = 0.0

    def get_best_move(self, board: ConnectBoard, player: Player):
        start = time.perf_counter()
        self.nodes_expanded = 1
        maximizing = player == Player.Max
        avail = set(board.get_available_columns())
        cols = [c for c in COLUMN_ORDER if c in avail]

        best_col, best_val = None, None
        children = []
        for c in cols:
            next_board = board.drop(player, c)
            if next_board is None:
                continue
            val, node = self._search(next_board, self.depth - 1, _other(player), c)
            children.append(node)
            if best_val is None or (val > best_val if maximizing else val < best_val):
                best_val, best_col = val, c

        if best_val is None:
            best_val = evaluate_board(board)

        self.last_tree_data = {
            "node": f"ROOT ({'MAX' if maximizing else 'MIN'})",
            "score": round(float(best_val), 2),
            "children": children,
        }
        self.last_execution_time = time.perf_counter() - start
        self.print_search_tree()
        return best_col

    def _search(self, board: ConnectBoard, depth: int, to_move: Player, col: int):
        self.nodes_expanded += 1
        if depth <= 0 or board.is_terminal():
            v = float(evaluate_board(board))
            return v, {"node": f"LEAF (col {col})", "score": round(v, 2), "children": []}

        maximizing = to_move == Player.Max
        best, children = None, []
        avail = set(board.get_available_columns())
        for c in COLUMN_ORDER:
            if c not in avail:
                continue
            next_board = board.drop(to_move, c)
            if next_board is None:
                continue
            v, node = self._search(next_board, depth - 1, _other(to_move), c)
            children.append(node)
            if best is None or (v > best if maximizing else v < best):
                best = v

        if best is None:
            best = float(evaluate_board(board))

        return best, {
            "node": f"{'MAX' if maximizing else 'MIN'} (col {col})",
            "score": round(float(best), 2),
            "children": children,
        }

    def get_last_search_tree(self) -> dict:
        return self.last_tree_data
