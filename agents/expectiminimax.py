import time
from .base import BaseAgent
from .heuristic import evaluate_board, COLUMN_ORDER
from .tree_utils import SearchTreeMixin
from board import ConnectBoard, Player


def _other(p: Player) -> Player:
    return Player.Min if p == Player.Max else Player.Max


# Probabilities:
#   - 0.6 probability that disc falls in chosen column
#   - 0.2 for column on left (0.4 if only left is available)
#   - 0.2 for column on right (0.4 if only right is available)
#
# Structure: MAX -> CHANCE -> MIN -> CHANCE -> ...  `depth` counts player plies only;
# a chance layer belongs to the ply that created it. The slip probability of an
# outcome is shown in its node label, e.g. "MIN (col 2, p=0.20)".
class ExpectedMinimaxAgent(BaseAgent, SearchTreeMixin):
    def __init__(self, depth: int = 3):
        self.depth = max(1, int(depth))
        self.last_tree_data = {}
        self.nodes_expanded = 0
        self.last_execution_time = 0.0

    @staticmethod
    def _outcomes(avail_set: set, c: int):
        left = (c - 1) in avail_set
        right = (c + 1) in avail_set
        if left and right:
            return [(c, 0.6), (c - 1, 0.2), (c + 1, 0.2)]
        if left:
            return [(c, 0.6), (c - 1, 0.4)]
        if right:
            return [(c, 0.6), (c + 1, 0.4)]
        return [(c, 1.0)]

    def get_best_move(self, board: ConnectBoard, player: Player):
        start = time.perf_counter()
        self.nodes_expanded = 1
        maximizing = player == Player.Max
        avail = set(board.get_available_columns())

        best_col, best_val = None, None
        children = []
        for c in COLUMN_ORDER:
            if c not in avail:
                continue
            val, node = self._chance(board, avail, self.depth, player, c)
            children.append(node)
            if best_val is None or (val > best_val if maximizing else val < best_val):
                best_val, best_col = val, c

        if best_val is None:
            best_val = float(evaluate_board(board))

        self.last_tree_data = {
            "node": f"ROOT ({'MAX' if maximizing else 'MIN'})",
            "score": round(float(best_val), 2),
            "children": children,
        }
        self.last_execution_time = time.perf_counter() - start
        self.last_tree_data["_stats"] = {
            "nodes_expanded": self.nodes_expanded,
            "execution_time": self.last_execution_time,
        }
        self.print_search_tree()
        return best_col

    def _chance(self, board: ConnectBoard, avail: set, depth: int, player: Player, c: int):
        self.nodes_expanded += 1
        value, kids = 0.0, []
        for r, p in self._outcomes(avail, c):
            next_board = board.drop(player, r)
            if next_board is None:
                continue
            v, node = self._player_node(next_board, depth - 1, _other(player), r, p)
            value += p * v
            kids.append(node)
        return value, {
            "node": f"CHANCE (col {c})",
            "score": round(float(value), 2),
            "children": kids,
        }

    def _player_node(self, board: ConnectBoard, depth: int, to_move: Player, col: int, prob: float):
        self.nodes_expanded += 1
        tag = f"col {col}, p={prob:.2f}"
        if depth <= 0 or board.is_terminal():
            v = float(evaluate_board(board))
            return v, {"node": f"LEAF ({tag})", "score": round(v, 2), "children": []}

        maximizing = to_move == Player.Max
        best, kids = None, []
        avail = set(board.get_available_columns())
        for c in COLUMN_ORDER:
            if c not in avail:
                continue
            v, node = self._chance(board, avail, depth, to_move, c)
            kids.append(node)
            if best is None or (v > best if maximizing else v < best):
                best = v

        if best is None:
            best = float(evaluate_board(board))

        return best, {
            "node": f"{'MAX' if maximizing else 'MIN'} ({tag})",
            "score": round(float(best), 2),
            "children": kids,
        }

    def get_last_search_tree(self) -> dict:
        return self.last_tree_data
