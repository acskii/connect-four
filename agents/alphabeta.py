import time
from .base import BaseAgent
from .heuristic import evaluate_board, COLUMN_ORDER
from .tree_utils import SearchTreeMixin
from board import ConnectBoard, Player

INF = float("inf")


def _other(p: Player) -> Player:
    return Player.Min if p == Player.Max else Player.Max


# Minimax AI Agent with Alpha-Beta Pruning and center-out move ordering.
# Pruned branches are simply absent from the recorded tree.
class AlphaBetaAgent(BaseAgent, SearchTreeMixin):
    def __init__(self, depth: int = 4):
        self.depth = max(1, int(depth))
        self.last_tree_data = {}
        self.nodes_expanded = 0
        self.last_execution_time = 0.0

    def get_best_move(self, board: ConnectBoard, player: Player):
        start = time.perf_counter()
        self.nodes_expanded = 1
        maximizing = player == Player.Max
        alpha, beta = -INF, INF
        avail = set(board.get_available_columns())
        cols = [c for c in COLUMN_ORDER if c in avail]

        best_col, best_val = None, None
        children = []
        for c in cols:
            next_board = board.drop(player, c)
            if next_board is None:
                continue
            val, node = self._search(next_board, self.depth - 1, _other(player), alpha, beta, c)
            children.append(node)
            if best_val is None or (val > best_val if maximizing else val < best_val):
                best_val, best_col = val, c
            if maximizing:
                alpha = max(alpha, best_val)
            else:
                beta = min(beta, best_val)
            if alpha >= beta:
                break

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

    def _search(self, board: ConnectBoard, depth: int, to_move: Player, alpha: float, beta: float, col: int):
        self.nodes_expanded += 1
        if depth <= 0 or board.is_terminal():
            v = float(evaluate_board(board))
            return v, {"node": f"LEAF (col {col})", "score": round(v, 2), "children": []}

        maximizing = to_move == Player.Max
        best = -INF if maximizing else INF
        children = []
        avail = set(board.get_available_columns())

        for c in COLUMN_ORDER:
            if c not in avail:
                continue
            next_board = board.drop(to_move, c)
            if next_board is None:
                continue
            v, node = self._search(next_board, depth - 1, _other(to_move), alpha, beta, c)
            children.append(node)
            if maximizing:
                if v > best:
                    best = v
                if best > alpha:
                    alpha = best
            else:
                if v < best:
                    best = v
                if best < beta:
                    beta = best
            if alpha >= beta:
                break

        if best in (INF, -INF):
            best = float(evaluate_board(board))

        return best, {
            "node": f"{'MAX' if maximizing else 'MIN'} (col {col})",
            "score": round(float(best), 2),
            "children": children,
        }

    def get_last_search_tree(self) -> dict:
        return self.last_tree_data
