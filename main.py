import tkinter as tk
from gui.menu import MenuScreen
from gui.board import BoardScreen

class ConnectFourApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ConnectAI")
        self.geometry("1000x800")
        self.resizable(True, True)

        # Shared application state variables
        self.selected_algorithm = "Default"

        # Container frame holding all screens
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # Dictionary housing polymorphic screen instances
        self.screens = {}
        for ScreenClass in (MenuScreen, BoardScreen):
            screen_name = ScreenClass.__name__
            screen_instance = ScreenClass(parent=container, controller=self)
            self.screens[screen_name] = screen_instance
            screen_instance.grid(row=0, column=0, sticky="nsew")

        # Start by showing the Menu screen immediately on startup
        self.show_screen("MenuScreen")

    def show_screen(self, screen_name: str):
        screen = self.screens[screen_name]
        screen.update_state()
        screen.tkraise()

    def set_selected_algorithm(self, algo_name: str):
        self.selected_algorithm = algo_name
        print(f"[App Controller] Algorithm updated to: {algo_name}")

    # Utility function for getting board screen
    def get_board_screen(self) -> BoardScreen:
        return self.screens["BoardScreen"]

if __name__ == "__main__":
    app = ConnectFourApp()
    app.mainloop()