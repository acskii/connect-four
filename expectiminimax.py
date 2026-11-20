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
        self.depth = depth
        self.last_tree_data = {}
        self.nodes_expanded = 0
        self.last_execution_time = 0.0

    @staticmethod
    def _outcomes(board: ConnectBoard, c: int):
        """[(column, probability)] for choosing column c."""
        avail = board.get_available_columns()
        left, right = (c - 1) in avail, (c + 1) in avail
        if left and right:
            return [(c, 0.6), (c - 1, 0.2), (c + 1, 0.2)]
        if left:
            return [(c, 0.6), (c - 1, 0.4)]
        if right:
            return [(c, 0.6), (c + 1, 0.4)]
        return [(c, 1.0)]

    def get_best_move(self, board: ConnectBoard, player: Player) -> int:
        start = time.perf_counter()
        self.nodes_expanded = 1
        maximizing = player == Player.Max
        avail = board.get_available_columns()

        best_col, best_val = -1, None
        children = []
        for c in COLUMN_ORDER:
            if c not in avail:
                continue
            val, node = self._chance(board, self.depth, player, c)
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

    # Chance node: `player` chose column c at `depth` remaining plies.
    def _chance(self, board, depth, player, c):
        self.nodes_expanded += 1
        value, kids = 0.0, []
        for r, p in self._outcomes(board, c):
            v, node = self._player_node(board.drop(player, r), depth - 1,
                                        _other(player), r, p)
            value += p * v
            kids.append(node)
        return value, {"node": f"CHANCE (col {c})", "score": round(value, 2),
                       "children": kids}

    # MAX / MIN node (or leaf) reached via column `col` with probability `prob`.
    def _player_node(self, board, depth, to_move, col, prob):
        self.nodes_expanded += 1
        tag = f"col {col}, p={prob:.2f}"
        if depth == 0 or board.is_terminal():
            v = evaluate_board(board)
            return v, {"node": f"LEAF ({tag})", "score": round(v, 2), "children": []}

        maximizing = to_move == Player.Max
        best, kids = None, []
        avail = board.get_available_columns()
        for c in COLUMN_ORDER:
            if c not in avail:
                continue
            v, node = self._chance(board, depth, to_move, c)
            kids.append(node)
            if best is None or (v > best if maximizing else v < best):
                best = v
        return best, {"node": f"{'MAX' if maximizing else 'MIN'} ({tag})",
                      "score": round(best, 2), "children": kids}

    def get_last_search_tree(self) -> dict:
        return self.last_tree_data
