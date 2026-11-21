from __future__ import annotations

from enum import Enum


class Player(Enum):
    Min = 1
    Max = 2


class ConnectBoard:
    def __init__(self, board=None):
        # Board of size 6 x 7. Each column is stored bottom-to-top.
        if board is None:
            self._board = [0] * 6 * 7
        else:
            self._board = board

    # Returns column indexes with space available.
    def get_available_columns(self) -> list:
        possible_columns = []
        for col in range(5, 6 * 7, 6):
            if self._board[col] == 0:
                possible_columns.append(col // 6)
        return possible_columns

    # Drop a disc in a column, returning a new board or None if invalid/full.
    def drop(self, ply: Player, col: int) -> ConnectBoard:
        if col not in self.get_available_columns():
            print(f"Column {col} is full or invalid, nothing is done.")
            return None

        new_board = self._board.copy()
        start = col * 6
        for i in range(6):
            idx = start + i
            if new_board[idx] == 0:
                new_board[idx] = ply.value
                break
        return ConnectBoard(new_board)

    # Counts all distinct four-in-a-row alignments for the given player.
    def count_connect_fours(self, ply: Player) -> int:
        val = ply.value
        count = 0

        def get_cell(c, r):
            if 0 <= c < 7 and 0 <= r < 6:
                return self._board[c * 6 + r]
            return None

        for c in range(4):
            for r in range(6):
                if all(get_cell(c + i, r) == val for i in range(4)):
                    count += 1

        for c in range(7):
            for r in range(3):
                if all(get_cell(c, r + i) == val for i in range(4)):
                    count += 1

        for c in range(4):
            for r in range(3):
                if all(get_cell(c + i, r + i) == val for i in range(4)):
                    count += 1

        for c in range(4):
            for r in range(3, 6):
                if all(get_cell(c + i, r - i) == val for i in range(4)):
                    count += 1

        return count

    def has_won(self, ply: Player) -> bool:
        if not self.is_terminal():
            return False
        opponent = Player.Min if ply == Player.Max else Player.Max
        return self.count_connect_fours(ply) > self.count_connect_fours(opponent)

    # A terminal position is reached when the board is completely filled.
    def is_terminal(self) -> bool:
        return all(self._board[col] != 0 for col in range(5, 6 * 7, 6))

    def get_board(self):
        return self._board

    def __eq__(self, other):
        return isinstance(other, ConnectBoard) and self._board == other.get_board()

    def __hash__(self):
        return hash(tuple(self._board))

    def __str__(self):
        return ", ".join(str(x) for x in self._board)

    def pretty(self):
        symbols = {0: "-", 1: "X", 2: "O"}
        rows = []
        for r in range(5, -1, -1):
            rows.append(" ".join(symbols[self._board[c * 6 + r]] for c in range(7)))
        return "\n".join(rows)