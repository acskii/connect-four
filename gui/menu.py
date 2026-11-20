import tkinter as tk
from .base import BaseScreen
from selector import Selector

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

        tk.Label(
            self, text="Configure algorithm and search depth K before starting",
            font=("Arial", 11), fg="#555"
        ).pack(pady=(0, 20))

        form = tk.Frame(self)
        form.pack(pady=10)

        # Algorithm selection
        tk.Label(form, text="AI Algorithm:", font=("Arial", 11, "bold")).grid(row=0, column=0, padx=10, pady=10, sticky="e")
        self.algo_var = tk.StringVar(value=Selector.ALGORITHMS[0])
        tk.OptionMenu(form, self.algo_var, *Selector.ALGORITHMS).grid(row=0, column=1, padx=10, pady=10, sticky="w")

        # Depth K selection
        tk.Label(form, text="Search Depth (K):", font=("Arial", 11, "bold")).grid(row=1, column=0, padx=10, pady=10, sticky="e")
        self.depth_var = tk.IntVar(value=3)
        tk.Spinbox(form, from_=1, to=8, textvariable=self.depth_var, width=6, font=("Arial", 11)).grid(row=1, column=1, padx=10, pady=10, sticky="w")

        # Human side selection (Human = Min [Yellow], Agent = Max [Red], or vice versa)
        tk.Label(form, text="Human Plays As:", font=("Arial", 11, "bold")).grid(row=2, column=0, padx=10, pady=10, sticky="e")
        self.side_var = tk.StringVar(value="Min (Yellow)")
        tk.OptionMenu(form, self.side_var, "Min (Yellow)", "Max (Red)").grid(row=2, column=1, padx=10, pady=10, sticky="w")

        tk.Button(
            self, text="Start Human vs Agent", font=("Arial", 12, "bold"),
            bg="#28b463", fg="white", padx=20, pady=10, command=self.launch_board
        ).pack(pady=30)

    def launch_board(self):
        selected_algorithm = self.algo_var.get()
        print(f"[Menu] Launching game using selection: '{selected_algorithm}'")
        
        # Switch to board screen and start the game
        self.controller.configure_match(
            algorithm=self.algo_var.get(),
            depth=int(self.depth_var.get()),
            human_is_max=("Max" in self.side_var.get()),
        )
        self.controller.show_screen("BoardScreen")

    def update_state(self):
        pass