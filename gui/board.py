import tkinter as tk
from tkinter import messagebox
from .base import BaseScreen
from board import ConnectBoard, Player
from .tree import TreeWindow

class BoardScreen(BaseScreen):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.board = ConnectBoard()
        self.current_turn = Player.Max
        self.human_player = Player.Min
        self.agent_player = Player.Max
        self.col_buttons = []
        self.create_widgets()

    def create_widgets(self):
        self.status_label = tk.Label(self, text="", font=("Arial", 13, "bold"), fg="#1b4f72")
        self.status_label.pack(pady=(10, 4))

        # Column drop buttons for Human turn
        col_bar = tk.Frame(self)
        col_bar.pack(pady=4)
        self.col_buttons.clear()
        for c in range(7):
            btn = tk.Button(
                col_bar, text=f"Drop {c}", width=7, font=("Arial", 9, "bold"),
                command=lambda col=c: self.on_human_drop(col)
            )
            btn.grid(row=0, column=c, padx=3)
            self.col_buttons.append(btn)

        # Board canvas
        board_box = tk.Frame(self, bg="#104e8b", padx=8, pady=8, relief="raised", bd=3)
        board_box.pack(pady=6)

        self.cell = 68
        self.canvas = tk.Canvas(
            board_box, width=7 * self.cell, height=6 * self.cell,
            bg="#1874cd", highlightthickness=0
        )
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.on_canvas_click)

        # Action bar: View Tree (opens after turns) + Restart + Menu
        actions = tk.Frame(self)
        actions.pack(pady=8)

        self.tree_btn = tk.Button(
            actions, text="View Search Tree", font=("Arial", 10, "bold"),
            bg="#8e44ad", fg="white", padx=12, pady=5,
            state="disabled", command=self.open_tree_window
        )
        self.tree_btn.grid(row=0, column=0, padx=6)

        tk.Button(
            actions, text="Restart Match", font=("Arial", 10),
            padx=10, pady=5, command=self.reset_match
        ).grid(row=0, column=1, padx=6)

        tk.Button(
            actions, text="Menu", font=("Arial", 10),
            padx=10, pady=5, command=lambda: self.controller.show_screen("MenuScreen")
        ).grid(row=0, column=2, padx=6)

        # Legend
        legend = tk.LabelFrame(self, text="Legend", font=("Arial", 9, "bold"), padx=10, pady=4)
        legend.pack(pady=4)
        tk.Label(legend, text="● Max", fg="#c0392b", font=("Arial", 9, "bold")).pack(side="left", padx=10)
        tk.Label(legend, text="● Min", fg="#b7950b", font=("Arial", 9, "bold")).pack(side="left", padx=10)
        tk.Label(legend, text="○ Empty", fg="#5d6d7e", font=("Arial", 9)).pack(side="left", padx=10)

    def update_state(self):
        self.human_player = Player.Max if self.controller.human_is_max else Player.Min
        self.agent_player = Player.Min if self.human_player == Player.Max else Player.Max
        self.reset_match()

    def reset_match(self):
        self.board = ConnectBoard()
        self.current_turn = Player.Max  # Max starts
        self.tree_btn.config(state="disabled")
        self._refresh_ui()
        if self.current_turn == self.agent_player:
            self.after(200, self.run_agent_turn)

    def on_canvas_click(self, event):
        if self.current_turn != self.human_player or self.board.is_terminal():
            return
        col = event.x // self.cell
        if 0 <= col < 7:
            self.on_human_drop(col)

    def on_human_drop(self, col: int):
        if self.current_turn != self.human_player or self.board.is_terminal():
            return
        if col not in self.board.get_available_columns():
            messagebox.showwarning("Column Full", f"Column {col} is full.")
            return

        next_board = self.board.drop(self.human_player, col)
        if next_board is None:
            return
        self.board = next_board
        self._advance_after_move()

        if not self.board.is_terminal() and self.current_turn == self.agent_player:
            self.after(150, self.run_agent_turn)

    def run_agent_turn(self):
        if self.board.is_terminal() or self.current_turn != self.agent_player:
            return
        agent = self.controller.agent
        col = agent.get_best_move(self.board, self.agent_player)
        if col is not None:
            next_board = self.board.drop(self.agent_player, col)
            if next_board is not None:
                self.board = next_board
        # Enable tree viewer after agent turn (tree was printed to console inside get_best_move)
        if getattr(agent, "last_tree_data", None):
            self.tree_btn.config(state="normal")
        self._advance_after_move()

    def _advance_after_move(self):
        if self.board.is_terminal():
            self.current_turn = None
            self._refresh_ui()
            max_4s = self.board.count_connect_fours(Player.Max)
            min_4s = self.board.count_connect_fours(Player.Min)
            if max_4s > min_4s:
                winner = "Max"
            elif min_4s > max_4s:
                winner = "Min"
            else:
                winner = "Draw"
            messagebox.showinfo(
                "Game Over",
                f"Board full!\nMax Connect-4s: {max_4s} | Min Connect-4s: {min_4s}\nResult: {winner}"
            )
            return

        self.current_turn = Player.Min if self.current_turn == Player.Max else Player.Max
        self._refresh_ui()

    def open_tree_window(self):
        agent = self.controller.agent
        tree = agent.get_last_search_tree() if agent else {}
        info = f"{self.controller.algorithm} | K={self.controller.depth}"
        TreeWindow(self, tree, info)

    def _refresh_ui(self):
        avail = set(self.board.get_available_columns())
        human_can_act = (self.current_turn == self.human_player) and not self.board.is_terminal()
        for c, btn in enumerate(self.col_buttons):
            btn.config(state="normal" if (human_can_act and c in avail) else "disabled")

        if self.board.is_terminal():
            turn_text = "Finished"
        elif self.current_turn == self.human_player:
            turn_text = f"Human ({self.human_player.name})"
        else:
            turn_text = f"Agent ({self.agent_player.name}) thinking..."

        self.status_label.config(
            text=f"{self.controller.algorithm} (K={self.controller.depth}) | Turn: {turn_text}"
        )
        self._draw_board()

    def _draw_board(self):
        self.canvas.delete("all")
        cells = self.board.get_board()
        for c in range(7):
            for r in range(6):
                x1 = c * self.cell + 8
                y1 = (5 - r) * self.cell + 8
                x2 = (c + 1) * self.cell - 8
                y2 = (6 - r) * self.cell - 8
                v = cells[c * 6 + r]
                if v == Player.Max.value:
                    fill, outline = "#e74c3c", "#922b21"
                elif v == Player.Min.value:
                    fill, outline = "#f1c40f", "#b7950b"
                else:
                    fill, outline = "#d0d3d4", "#808b96"
                self.canvas.create_oval(x1, y1, x2, y2, fill=fill, outline=outline, width=2.5)