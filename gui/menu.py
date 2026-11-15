import tkinter as tk
from .base import BaseScreen

class MenuScreen(BaseScreen):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.create_widgets()

    def create_widgets(self):
        # Title Styling
        title_label = tk.Label(
            self, text="Connect Four AI", font=("Arial", 22, "bold"), fg="#1b4f72"
        )
        title_label.pack(pady=30)

        subtitle = tk.Label(
            self, text="Select an algorithm to configure AI agent:", font=("Arial", 12)
        )
        subtitle.pack(pady=5)

        # Algorithm Selection Dropdown
        selection_frame = tk.Frame(self)
        selection_frame.pack(pady=20)

        lbl_algo = tk.Label(selection_frame, text="Algorithm:", font=("Arial", 11, "bold"))
        lbl_algo.grid(row=0, column=0, padx=10)

        # Can be extended to add required algorithms e.g. minimax
        self.available_algorithms = ["Demo View"]
        
        self.algo_var = tk.StringVar(value=self.available_algorithms[0])
        self.algo_dropdown = tk.OptionMenu(selection_frame, self.algo_var, *self.available_algorithms)
        self.algo_dropdown.config(font=("Arial", 11), width=35)
        self.algo_dropdown.grid(row=0, column=1, padx=10)

        # Start Button
        start_btn = tk.Button(
            self, text="Start", font=("Arial", 12, "bold"),
            bg="#28b463", fg="white", padx=20, pady=10, command=self.launch_board
        )
        start_btn.pack(pady=40)

    def launch_board(self):
        selected_algorithm = self.algo_var.get()
        print(f"[Menu] Launching game using selection: '{selected_algorithm}'")
        
        # Notify controller / switch to board screen
        self.controller.set_selected_algorithm(selected_algorithm)
        self.controller.show_screen("BoardScreen")

    def update_state(self):
        pass