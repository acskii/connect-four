from abc import ABC, abstractmethod
import tkinter as tk

class BaseScreen(ABC, tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

    @abstractmethod
    def create_widgets(self):
        pass

    @abstractmethod
    def update_state(self):
        pass