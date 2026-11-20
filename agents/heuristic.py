"""Heuristic evaluation for the "play until the board is full" Connect 4 variant.

evaluate_board() is ALWAYS from Player.Max's perspective:
positive favours Max, negative favours Min.
"""
from board import ConnectBoard, Player

ROWS, COLS = 6, 7

# Center-out column ordering (shared by all agents for move ordering / tie-breaks).
COLUMN_ORDER = [3, 2, 4, 1, 5, 0, 6]

# Tunable weights
SCORE_WEIGHT = 1000          # per connected-four already on the board
TERMINAL_WEIGHT = 10000      # terminal outcomes strictly dominate estimates
THREE_WEIGHT = 50            # 3 pieces + 1 empty
THREE_PLAYABLE_BONUS = 25    # ...and the empty cell can be played right now
TWO_WEIGHT = 10              # 2 pieces + 2 empty
OPP_FACTOR = 1.2             # opponent threats count slightly more (defence)
CENTER_WEIGHTS = {3: 6, 2: 4, 4: 4, 1: 2, 5: 2, 0: 0, 6: 0}


def _build_windows():
    """All 69 four-cell windows as lists of (col, row): 24 H + 21 V + 12 / + 12 \\."""
    wins = []
    for c in range(COLS - 3):                       # horizontal
        for r in range(ROWS):
            wins.append([(c + i, r) for i in range(4)])
    for c in range(COLS):                           # vertical
        for r in range(ROWS - 3):
            wins.append([(c, r + i) for i in range(4)])
    for c in range(COLS - 3):                       # positive diagonal
        for r in range(ROWS - 3):
            wins.append([(c + i, r + i) for i in range(4)])
    for c in range(COLS - 3):                       # negative diagonal
        for r in range(3, ROWS):
            wins.append([(c + i, r - i) for i in range(4)])
    return wins


WINDOWS = _build_windows()  # computed once at import time


def evaluate_board(board: ConnectBoard) -> float:
    max_fours = board.count_connect_fours(Player.Max)
    min_fours = board.count_connect_fours(Player.Min)
    diff = max_fours - min_fours

    # Terminal: exact result, scaled so it dominates any heuristic estimate.
    if board.is_terminal():
        return float(diff * TERMINAL_WEIGHT)

    cells = board.get_board()          # index = col * 6 + row, row 0 = bottom
    MAX, MIN = Player.Max.value, Player.Min.value
    score = float(diff * SCORE_WEIGHT)

    # --- Window analysis ---
    for win in WINDOWS:
        n_max = n_min = 0
        empty = None                    # last empty cell (only used when exactly 1)
        n_empty = 0
        for (c, r) in win:
            v = cells[c * 6 + r]
            if v == MAX:
                n_max += 1
            elif v == MIN:
                n_min += 1
            else:
                n_empty += 1
                empty = (c, r)
        if n_max and n_min:
            continue                    # blocked window, no potential for either

        if n_empty == 1:                # 3 + 1 empty: immediate-ish threat
            c, r = empty
            playable = (r == 0) or cells[c * 6 + r - 1] != 0
            val = THREE_WEIGHT + (THREE_PLAYABLE_BONUS if playable else 0)
            score += val if n_max == 3 else -val * OPP_FACTOR
        elif n_empty == 2:              # 2 + 2 empty: developing
            score += TWO_WEIGHT if n_max == 2 else -TWO_WEIGHT * OPP_FACTOR

    # --- Center column control ---
    for c in range(COLS):
        w = CENTER_WEIGHTS[c]
        if w:
            for r in range(ROWS):
                v = cells[c * 6 + r]
                if v == MAX:
                    score += w
                elif v == MIN:
                    score -= w

    return score
