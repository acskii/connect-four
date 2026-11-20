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
        self.depth = depth
        self.last_tree_data = {}
        self.nodes_expanded = 0
        self.last_execution_time = 0.0

    def get_best_move(self, board: ConnectBoard, player: Player) -> int:
        start = time.perf_counter()
        self.nodes_expanded = 1
        maximizing = player == Player.Max
        alpha, beta = -INF, INF
        cols = [c for c in COLUMN_ORDER if c in board.get_available_columns()]

        best_col, best_val = -1, None
        children = []
        for c in cols:
            val, node = self._search(board.drop(player, c), self.depth - 1,
                                     _other(player), alpha, beta, c)
            children.append(node)
            if best_val is None or (val > best_val if maximizing else val < best_val):
                best_val, best_col = val, c
            # Alpha only moves at MAX nodes, beta only at MIN nodes.
            if maximizing:
                alpha = max(alpha, best_val)
            else:
                beta = min(beta, best_val)
            if alpha >= beta:
                break

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

    def _search(self, board, depth, to_move, alpha, beta, col):
        self.nodes_expanded += 1
        if depth == 0 or board.is_terminal():
            v = evaluate_board(board)
            return v, {"node": f"LEAF (col {col})", "score": round(v, 2), "children": []}

        maximizing = to_move == Player.Max
        best = -INF if maximizing else INF
        children = []
        avail = board.get_available_columns()
        for c in COLUMN_ORDER:
            if c not in avail:
                continue
            v, node = self._search(board.drop(to_move, c), depth - 1,
                                   _other(to_move), alpha, beta, c)
            children.append(node)
            if maximizing:
                best = max(best, v)
                alpha = max(alpha, best)
            else:
                best = min(best, v)
                beta = min(beta, best)
            if alpha >= beta:        # prune remaining siblings
                break
        return best, {"node": f"{'MAX' if maximizing else 'MIN'} (col {col})",
                      "score": round(best, 2), "children": children}

    def get_last_search_tree(self) -> dict:
        return self.last_tree_data
