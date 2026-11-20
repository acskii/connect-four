import tkinter as tk
from tkinter import scrolledtext

# For BONUS
# Window that renders and traces the search tree for the current turn
class TreeWindow(tk.Toplevel):
    def __init__(self, parent, tree_data: dict, title_info: str):
        super().__init__(parent)
        self.title(f"Search Tree — {title_info}")
        self.geometry("760x560")
        self.tree_data = tree_data or {}

        tk.Label(self, text=f"Search Tree ({title_info})", font=("Arial", 13, "bold"), fg="#1b4f72").pack(pady=8)

        tabs = tk.Frame(self)
        tabs.pack(fill="both", expand=True, padx=12, pady=6)

        # Left/Top: Readable indented text trace
        tk.Label(tabs, text="Readable Tree Trace:", font=("Arial", 10, "bold")).pack(anchor="w")
        txt = scrolledtext.ScrolledText(tabs, height=11, font=("Consolas", 9))
        txt.pack(fill="x", pady=(2, 8))
        txt.insert("1.0", self._format_text(self.tree_data))
        txt.config(state="disabled")

        # Bottom: Visual node diagram
        tk.Label(tabs, text="Visual Tree:", font=("Arial", 10, "bold")).pack(anchor="w")
        self.canvas = tk.Canvas(tabs, bg="white", height=240)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Configure>", lambda e: self._redraw())

    def _format_text(self, node: dict, prefix: str = "", is_last: bool = True, is_root: bool = True) -> str:
        if not node:
            return "<No tree recorded yet>"
        line = f"{node.get('node', '?')} [val={node.get('score', '?')}]\n"
        if is_root:
            out = line
            new_prefix = ""
        else:
            out = f"{prefix}{'└── ' if is_last else '├── '}{line}"
            new_prefix = prefix + ("    " if is_last else "│   ")
        kids = node.get("children", [])
        for i, k in enumerate(kids):
            out += self._format_text(k, new_prefix, i == len(kids) - 1, is_root=False)
        return out

    def _redraw(self):
        self.canvas.delete("all")
        if not self.tree_data:
            return
        w = max(300, self.canvas.winfo_width())
        self._draw_node(self.tree_data, x=w / 2, y=28, spread=w / 4, depth_left=3)

    def _draw_node(self, node: dict, x: float, y: float, spread: float, depth_left: int):
        label = f"{node.get('node', '?')}\n{node.get('score', '?')}"
        self.canvas.create_rectangle(x - 52, y - 16, x + 52, y + 16, fill="#ebf5fb", outline="#2e86c1", width=1.5)
        self.canvas.create_text(x, y, text=label, font=("Arial", 7, "bold"), justify="center")

        if depth_left <= 0:
            return
        kids = node.get("children", [])
        n = len(kids)
        if n == 0:
            return
        ny = y + 62
        for i, kid in enumerate(kids):
            nx = x if n == 1 else (x - spread + i * (2 * spread / (n - 1)))
            self.canvas.create_line(x, y + 16, nx, ny - 16, fill="#7f8c8d")
            self._draw_node(kid, nx, ny, max(25.0, spread * 0.55), depth_left - 1)