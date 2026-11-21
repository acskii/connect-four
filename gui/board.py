import threading
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
        self._agent_busy = False
        self._match_id = 0
        self._tree_window = None
        self.create_widgets()

    def create_widgets(self):
        self.configure(bg="#f3f6fb")
        tk.Label(
            self, text="CONNECT FOUR", font=("Arial", 21, "bold"),
            fg="#17324d", bg="#f3f6fb"
        ).pack(pady=(16, 1))
        tk.Label(
            self, text="Human vs AI · Search-backed play", font=("Arial", 10),
            fg="#66788a", bg="#f3f6fb"
        ).pack(pady=(0, 8))

        self.status_label = tk.Label(
            self, text="", font=("Arial", 12, "bold"), fg="#1b4f72",
            bg="#f3f6fb", padx=12, pady=7
        )
        self.status_label.pack(pady=(2, 4))

        col_bar = tk.Frame(self, bg="#f3f6fb")
        col_bar.pack(pady=5)
        self.col_buttons.clear()
        for c in range(7):
            btn = tk.Button(
                col_bar, text=f"Drop {c + 1}", width=8,
                font=("Arial", 9, "bold"), bg="#ffffff", fg="#24435c",
                activebackground="#d6eaf8", relief="groove", bd=1,
                command=lambda col=c: self.on_human_drop(col)
            )
            btn.grid(row=0, column=c, padx=3)
            self.col_buttons.append(btn)

        board_box = tk.Frame(self, bg="#104e8b", padx=9, pady=9, relief="raised", bd=2)
        board_box.pack(pady=7)
        self.cell = 66
        self.canvas = tk.Canvas(
            board_box, width=7 * self.cell, height=6 * self.cell,
            bg="#1874cd", highlightthickness=0, cursor="hand2"
        )
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.on_canvas_click)

        actions = tk.Frame(self, bg="#f3f6fb")
        actions.pack(pady=9)
        self.tree_btn = tk.Button(
            actions, text="Explore Search Tree", font=("Arial", 10, "bold"),
            bg="#7651a8", fg="white", activebackground="#60418d",
            padx=12, pady=6, state="disabled", command=self.open_tree_window
        )
        self.tree_btn.grid(row=0, column=0, padx=6)
        tk.Button(
            actions, text="Restart Match", font=("Arial", 10, "bold"),
            bg="#ffffff", fg="#24435c", padx=10, pady=6,
            command=self.reset_match
        ).grid(row=0, column=1, padx=6)
        tk.Button(
            actions, text="Menu", font=("Arial", 10), bg="#ffffff",
            fg="#24435c", padx=10, pady=6,
            command=lambda: self.controller.show_screen("MenuScreen")
        ).grid(row=0, column=2, padx=6)

        legend = tk.Frame(self, bg="#f3f6fb")
        legend.pack(pady=(1, 8))
        tk.Label(legend, text="● Max", fg="#c0392b", bg="#f3f6fb", font=("Arial", 9, "bold")).pack(side="left", padx=10)
        tk.Label(legend, text="● Min", fg="#b7950b", bg="#f3f6fb", font=("Arial", 9, "bold")).pack(side="left", padx=10)
        tk.Label(legend, text="○ Empty", fg="#5d6d7e", bg="#f3f6fb", font=("Arial", 9)).pack(side="left", padx=10)

    def update_state(self):
        self.human_player = Player.Max if self.controller.human_is_max else Player.Min
        self.agent_player = Player.Min if self.human_player == Player.Max else Player.Max
        self.reset_match()

    def reset_match(self):
        self._match_id += 1
        self.board = ConnectBoard()
        self.current_turn = Player.Max
        self.tree_btn.config(state="disabled")
        self._refresh_ui()
        if self.current_turn == self.agent_player:
            self.after(150, self.run_agent_turn)

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
            messagebox.showwarning("Column Full", f"Column {col + 1} is full.")
            return
        next_board = self.board.drop(self.human_player, col)
        if next_board is not None:
            self.board = next_board
            self._advance_after_move()
            if not self.board.is_terminal() and self.current_turn == self.agent_player:
                self.after(120, self.run_agent_turn)

    def run_agent_turn(self):
        if self.board.is_terminal() or self.current_turn != self.agent_player or self._agent_busy:
            return
        agent = self.controller.agent
        if agent is None:
            return

        self._agent_busy = True
        match_id = self._match_id
        snapshot = ConnectBoard(self.board.get_board().copy())
        player = self.agent_player
        self._refresh_ui()

        def calculate():
            try:
                col = agent.get_best_move(snapshot, player)
                tree = agent.get_last_search_tree()
                error = None
            except Exception as exc:  # Surface search errors on the Tk main thread.
                col, tree, error = None, {}, exc
            self.after(0, lambda: self._finish_agent_turn(match_id, col, tree, error))

        threading.Thread(target=calculate, name="connect-four-agent", daemon=True).start()

    def _finish_agent_turn(self, match_id, col, tree, error):
        self._agent_busy = False
        if match_id != self._match_id:
            # A restart happened while the old search was running. If the new
            # match also starts with the AI, let the now-free worker start it.
            if self.current_turn == self.agent_player and not self.board.is_terminal():
                self.after(0, self.run_agent_turn)
            return
        if error is not None:
            self.current_turn = self.human_player
            self._refresh_ui()
            messagebox.showerror("AI search failed", f"The agent could not complete its turn:\n{error}")
            return

        if tree:
            self.tree_btn.config(state="normal")
        if col is not None and col in self.board.get_available_columns():
            next_board = self.board.drop(self.agent_player, col)
            if next_board is not None:
                self.board = next_board
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
        if not tree:
            messagebox.showinfo("Search Tree", "The agent has not recorded a search tree yet.")
            return
        info = f"{self.controller.algorithm} · depth {self.controller.depth}"
        if self._tree_window is not None and self._tree_window.winfo_exists():
            self._tree_window.destroy()
        self._tree_window = TreeWindow(self, tree, info)

    def _refresh_ui(self):
        avail = set(self.board.get_available_columns())
        human_can_act = self.current_turn == self.human_player and not self.board.is_terminal()
        for c, btn in enumerate(self.col_buttons):
            btn.config(state="normal" if human_can_act and c in avail else "disabled")

        if self.board.is_terminal():
            turn_text = "Match complete"
        elif self._agent_busy:
            turn_text = f"{self.controller.algorithm} is searching…"
        elif self.current_turn == self.human_player:
            turn_text = f"Your turn ({self.human_player.name})"
        else:
            turn_text = f"AI turn ({self.agent_player.name})"
        self.status_label.config(text=f"{self.controller.algorithm} · depth {self.controller.depth}  |  {turn_text}")
        self._draw_board()

    def _draw_board(self):
        self.canvas.delete("all")
        cells = self.board.get_board()
        for c in range(7):
            for r in range(6):
                x1 = c * self.cell + 7
                y1 = (5 - r) * self.cell + 7
                x2 = (c + 1) * self.cell - 7
                y2 = (6 - r) * self.cell - 7
                value = cells[c * 6 + r]
                if value == Player.Max.value:
                    fill, outline = "#e74c3c", "#922b21"
                elif value == Player.Min.value:
                    fill, outline = "#f1c40f", "#b7950b"
                else:
                    fill, outline = "#eaf1f8", "#c5d2df"
                self.canvas.create_oval(x1, y1, x2, y2, fill=fill, outline=outline, width=2.5)