import tkinter as tk
from .base import BaseScreen
from board import Player, ConnectBoard

class BoardScreen(BaseScreen):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        # Load a sample board configuration to demonstrate state rendering
        # You can replace or load dynamic board instances here
        self.board = ConnectBoard()
        self.setup_demo_board_state()
        self.create_widgets()

    # This function is temporary
    def setup_demo_board_state(self):
        # Drop a few mock pieces so colors can be demonstrated visually
        self.board = self.board.drop(Player.Max, 2) # Red
        self.board = self.board.drop(Player.Max, 3) # Yellow
        self.board = self.board.drop(Player.Min, 3) # Yellow
        self.board = self.board.drop(Player.Max, 4) # Red
        self.board = self.board.drop(Player.Max, 4) # Red
        self.board = self.board.drop(Player.Min, 5) # Yellow

    def create_widgets(self):
        # Top Header Frame
        header_frame = tk.Frame(self)
        header_frame.pack(pady=10)

        title = tk.Label(header_frame, text="Connect Four - Board State Viewer", font=("Arial", 16, "bold"), fg="#1b4f72")
        title.pack()

        # Canvas Frame to draw the exact blue board graphic grid matching your photo
        board_container = tk.Frame(self, bg="#104e8b", padx=10, pady=10, relief="raised", bd=4)
        board_container.pack(pady=10)

        # Grid dimensions: 7 columns x 6 rows. Slot size = 70px diameter
        self.cell_size = 75
        canvas_width = 7 * self.cell_size
        canvas_height = 6 * self.cell_size

        self.canvas = tk.Canvas(
            board_container, width=canvas_width, height=canvas_height, 
            bg="#1874cd", highlightthickness=0
        )
        self.canvas.pack()

        # Legend Frame
        legend_frame = tk.LabelFrame(self, text=" Legend", font=("Arial", 11, "bold"), padx=15, pady=10)
        legend_frame.pack(pady=10, fill="x", padx=40)

        # Max Legend indicator
        max_color_box = tk.Canvas(legend_frame, width=22, height=22, bg="#1874cd", highlightthickness=0)
        max_color_box.create_oval(2, 2, 20, 20, fill="#e74c3c", outline="#b03a2e", width=2)
        max_color_box.grid(row=0, column=0, sticky="w", padx=5)
        lbl_max = tk.Label(legend_frame, text="Max", font=("Arial", 10, "bold"))
        lbl_max.grid(row=0, column=1, sticky="w", padx=5)

        # Min Legend indicator
        min_color_box = tk.Canvas(legend_frame, width=22, height=22, bg="#1874cd", highlightthickness=0)
        min_color_box.create_oval(2, 2, 20, 20, fill="#f1c40f", outline="#d4ac0d", width=2)
        min_color_box.grid(row=0, column=2, sticky="w", padx=15)
        lbl_min = tk.Label(legend_frame, text="Min", font=("Arial", 10, "bold"))
        lbl_min.grid(row=0, column=3, sticky="w", padx=5)

        # Empty Slot indicator
        empty_color_box = tk.Canvas(legend_frame, width=22, height=22, bg="#1874cd", highlightthickness=0)
        empty_color_box.create_oval(2, 2, 20, 20, fill="#d0d3d4", outline="#909497", width=2)
        empty_color_box.grid(row=0, column=4, sticky="w", padx=15)
        lbl_empty = tk.Label(legend_frame, text="Empty", font=("Arial", 10, "bold"))
        lbl_empty.grid(row=0, column=5, sticky="w", padx=5)

        # Navigation back to menu
        back_btn = tk.Button(
            self, text="← Return to Menu", font=("Arial", 10, "bold"),
            command=lambda: self.controller.show_screen("MenuScreen"), padx=10, pady=5
        )
        back_btn.pack(pady=10)

        self.draw_board()

    # Renders connect board into a 2D board visual
    def draw_board(self):
        self.canvas.delete("all")
        board_data = self.board.get_board()

        # Connect Board coordinate mapping:
        # Col ranges from 0 to 6 (left to right)
        # Row ranges from 5 (top) down to 0 (bottom)
        for c in range(7):
            for r in range(6):
                # Calculate pixel positions
                x1 = c * self.cell_size + 10
                # Invert row so row 5 is at the top of the canvas
                canvas_r = 5 - r
                y1 = canvas_r * self.cell_size + 10
                x2 = x1 + self.cell_size - 20
                y2 = y1 + self.cell_size - 20

                # Fetch cell value from 1D list: index = c * 6 + r
                cell_value = board_data[c * 6 + r]

                # Assign colors based on player mappings requested:
                # Player Max (2) -> Red, Player Min (1) -> Yellow, Empty (0) -> Grey/Silver
                if cell_value == Player.Max.value:
                    fill_color = "#e74c3c"  # Red
                    outline_color = "#922b21"
                elif cell_value == Player.Min.value:
                    fill_color = "#f1c40f"  # Yellow
                    outline_color = "#b7950b"
                else:
                    fill_color = "#d0d3d4"  # Grey slot as seen in reference
                    outline_color = "#808b96"

                # Draw outer blue ring shadow and circular slot disc
                self.canvas.create_oval(x1-2, y1-2, x2+2, y2+2, fill="#125c8f", outline="") # Bevel ring shadow
                self.canvas.create_oval(x1, y1, x2, y2, fill=fill_color, outline=outline_color, width=3)

    # Used to load a new board state
    def load_board(self, new_board: ConnectBoard):
        self.board = new_board
        self.draw_board()

    def update_state(self):
        # Refreshes canvas whenever screen becomes active
        self.draw_board()