import tkinter as tk

# For BONUS
# Window that renders and traces the search tree for the current turn
class TreeVisualizerWindow(tk.Toplevel):
    def __init__(self, parent, tree_data: dict, algorithm_name: str):
        super().__init__(parent)
        self.title(f"Tree Visualizer")
        self.geometry("650x450")
        self.tree_data = tree_data
        self.create_widgets()

    def create_widgets(self):
        header = tk.Label(
            self, text="Minimax Decision Tree Trace (Bonus Feature)", 
            font=("Arial", 14, "bold"), fg="#1b4f72"
        )
        header.pack(pady=10)

        # Canvas for drawing tree hierarchy nodes
        self.canvas = tk.Canvas(self, bg="white", width=610, height=340)
        self.canvas.pack(pady=5, padx=20)

        # Draw root node and recursive branches
        self.draw_node(self.tree_data, x=305, y=40, dx=150, level=0)

    def draw_node(self, node_dict, x, y, dx, level):
        """Recursively renders tree nodes and connecting branches on the canvas."""
        node_label = f"{node_dict.get('node', 'Node')}\nScore: {node_dict.get('score', 0)}"
        
        # Draw node box
        self.canvas.create_rectangle(x-45, y-20, x+45, y+20, fill="#EBF5FB", outline="#2E86C1", width=2)
        self.canvas.create_text(x, y, text=node_label, font=("Arial", 8, "bold"), justify="center")

        # Draw children nodes
        children = node_dict.get("children", [])
        num_children = len(children)
        if num_children > 0:
            next_y = y + 80
            for i, child in enumerate(children):
                next_x = x - dx + (i * (2 * dx / max(1, num_children - 1))) if num_children > 1 else x
                
                # Draw connecting line
                self.canvas.create_line(x, y + 20, next_x, next_y - 20, fill="#85929E", width=1.5)
                
                # Recursive call
                self.draw_node(child, next_x, next_y, dx / 2, level + 1)