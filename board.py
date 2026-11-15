from enum import Enum

class Player(Enum):
    Min = 1
    Max = 2

class ConnectBoard:
    def __init__(self, board=None):
        # Board of size 6 x 7
        # Represents board from bottom up across every column e.g. index 5 is the top disc in the first column
        if board is None:
            self._board = [0]*6*7
        else:
            # Verify it is correct??
            self._board = board

    # Checks which columns are available for new discs
    # Returns a list of column indexes with space available
    def get_available_columns(self) -> list:
        possible_columns = []

        # Only return a column as possible if top disc is empty
        for col in range(5, 6 * 7, 6):
            if self._board[col] == 0: 
                possible_columns.append(col // 6)

        return possible_columns

    # Drop a disc in a column with the player value to occupy it
    # Will not allow drops in a full column
    def drop(self, ply: Player, col: int) -> ConnectBoard:
        if col not in self.get_available_columns():
            print(f"Column {col} is full or invalid, nothing is done.")
            return

        new_board = self._board.copy()

        start = col * 6
        for i in range(6):
            idx = start + i
            if new_board[idx] == 0:
                new_board[idx] = ply.value
                break

        return ConnectBoard(new_board)

    # Counts all distinct 4-in-a-row alignments (horizontal, vertical, and diagonal) for the given player.
    def count_connect_fours(self, ply: Player) -> int:
        val = ply.value
        count = 0

        def get_cell(c, r):
            if 0 <= c < 7 and 0 <= r < 6:
                return self._board[c * 6 + r]
            return None

        # Horizontal
        for c in range(4):
            for r in range(6):
                if all(get_cell(c + i, r) == val for i in range(4)):
                    count += 1

        # Vertical
        for c in range(7):
            for r in range(3):
                if all(get_cell(c, r + i) == val for i in range(4)):
                    count += 1

        # Positive Diagonal (/)
        for c in range(4):
            for r in range(3):
                if all(get_cell(c + i, r + i) == val for i in range(4)):
                    count += 1

        # Negative Diagonal (\)
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

    # Check if board has reached a terminal state
    # This happens when the board is completely filled
    def is_terminal(self) -> bool:
        return all(self._board[col] != 0 for col in range(5, 6 * 7, 6))

    def get_board(self):
        return self._board

    # Check if both instances are equal states
    def __eq__(self, other):
        return isinstance(other, ConnectBoard) and self._board == other.get_board()

    # Used to add instance in sets
    def __hash__(self):
        return hash(tuple(self._board))

    def __str__(self):
        t = [str(x) for x in self._board]
        return ", ".join(t)

    def pretty(self):
        symbols = {0: "-", 1: "X", 2: "O"}
        rows = []
        for r in range(5, -1, -1):
            row_str = " ".join(symbols[self._board[c * 6 + r]] for c in range(7))
            rows.append(row_str)
        return "\n".join(rows)