import tkinter as tk
from tkinter import scrolledtext


class TreeWindow(tk.Toplevel):
    """Scrollable search-tree explorer with DFS previous/next navigation."""

    MAX_VISIBLE_NODES = 220
    MAX_VISIBLE_DEPTH = 5
    MAX_STEPS = 1500
    NODE_WIDTH = 128
    LEVEL_HEIGHT = 88

    def __init__(self, parent, tree_data: dict, title_info: str):
        super().__init__(parent)
        self.title(f"Search Tree — {title_info}")
        self.geometry("1000x720")
        self.minsize(760, 520)
        self.configure(bg="#f3f6fb")
        self.tree_data = tree_data or {}
        self.steps = []
        self._collect_steps(self.tree_data, ())
        self.step_index = 0
        self.visible_tree = self._make_visible_tree(self.tree_data)
        self.positions = {}

        tk.Label(
            self, text="Search Tree Explorer", font=("Arial", 17, "bold"),
            fg="#17324d", bg="#f3f6fb"
        ).pack(pady=(12, 1))
        tk.Label(
            self, text=f"{title_info} · follow evaluated nodes one step at a time",
            font=("Arial", 10), fg="#66788a", bg="#f3f6fb"
        ).pack(pady=(0, 7))

        self.selected_label = tk.Label(
            self, text="", font=("Arial", 10, "bold"), fg="#23435e",
            bg="#ffffff", anchor="w", padx=10, pady=8, relief="groove", bd=1
        )
        self.selected_label.pack(fill="x", padx=12, pady=(2, 7))

        nav = tk.Frame(self, bg="#f3f6fb")
        nav.pack(pady=(0, 8))
        self.prev_btn = tk.Button(nav, text="← Previous", width=12, command=self.previous_step)
        self.prev_btn.pack(side="left", padx=5)
        self.step_counter = tk.Label(nav, text="", font=("Arial", 10, "bold"), bg="#f3f6fb", fg="#435b70", width=18)
        self.step_counter.pack(side="left", padx=5)
        self.next_btn = tk.Button(nav, text="Next →", width=12, command=self.next_step)
        self.next_btn.pack(side="left", padx=5)
        tk.Button(nav, text="Start", width=9, command=self.first_step).pack(side="left", padx=(12, 4))
        tk.Button(nav, text="End", width=9, command=self.last_step).pack(side="left", padx=4)

        diagram = tk.LabelFrame(
            self, text="Recorded search tree (scroll to explore)",
            font=("Arial", 10, "bold"), bg="#f3f6fb", fg="#23435e", padx=4, pady=4
        )
        diagram.pack(fill="both", expand=True, padx=12, pady=(0, 8))
        self.canvas = tk.Canvas(diagram, bg="#ffffff", highlightthickness=0)
        xbar = tk.Scrollbar(diagram, orient="horizontal", command=self.canvas.xview)
        ybar = tk.Scrollbar(diagram, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(xscrollcommand=xbar.set, yscrollcommand=ybar.set)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        ybar.grid(row=0, column=1, sticky="ns")
        xbar.grid(row=1, column=0, sticky="ew")
        diagram.grid_rowconfigure(0, weight=1)
        diagram.grid_columnconfigure(0, weight=1)
        self.canvas.bind("<Configure>", lambda _event: self._redraw())
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)

        lower = tk.Frame(self, bg="#f3f6fb")
        lower.pack(fill="x", padx=12, pady=(0, 10))
        tk.Label(lower, text="Readable trace", font=("Arial", 10, "bold"), bg="#f3f6fb", fg="#23435e").pack(anchor="w")
        self.trace = scrolledtext.ScrolledText(lower, height=7, font=("Consolas", 9), wrap="none")
        self.trace.pack(fill="x", pady=(3, 0))
        self.trace.insert("1.0", self._format_text(self.tree_data))
        self.trace.config(state="disabled")

        if not self.steps:
            self.steps = [({}, ())]
        self._show_step()
        self._redraw()

    def _collect_steps(self, node, path):
        if len(self.steps) >= self.MAX_STEPS or not isinstance(node, dict) or not node:
            return
        self.steps.append((node, path))
        for index, child in enumerate(node.get("children", [])):
            if len(self.steps) >= self.MAX_STEPS:
                break
            self._collect_steps(child, path + (index,))

    def _make_visible_tree(self, node):
        remaining = [self.MAX_VISIBLE_NODES]

        def copy(source, depth):
            if remaining[0] <= 0:
                return None
            remaining[0] -= 1
            result = {"node": source.get("node", "?"), "score": source.get("score", "?"), "children": []}
            children = source.get("children", [])
            if depth >= self.MAX_VISIBLE_DEPTH:
                if children:
                    result["children"].append({"node": f"… {len(children)} deeper", "score": "", "children": [], "_summary": True})
                return result
            for child in children:
                if remaining[0] <= 1:
                    result["children"].append({"node": "… more nodes", "score": "", "children": [], "_summary": True})
                    break
                rendered = copy(child, depth + 1)
                if rendered:
                    result["children"].append(rendered)
            return result

        return copy(node or {}, 0)

    def _format_text(self, node, prefix="", is_last=True, is_root=True, count=None):
        if count is None:
            count = [0]
        if not node:
            return "<No tree recorded yet>\n"
        count[0] += 1
        if count[0] > 600:
            return prefix + "└── … trace shortened after 600 nodes\n"
        score = node.get("score", "?")
        line = f"{node.get('node', '?')} [score={score}]\n"
        if is_root:
            out, new_prefix = line, ""
        else:
            out = f"{prefix}{'└── ' if is_last else '├── '}{line}"
            new_prefix = prefix + ("    " if is_last else "│   ")
        kids = node.get("children", [])
        for i, kid in enumerate(kids):
            if count[0] >= 600:
                out += new_prefix + "└── … remaining trace hidden\n"
                break
            out += self._format_text(kid, new_prefix, i == len(kids) - 1, False, count)
        return out

    def previous_step(self):
        self.step_index = max(0, self.step_index - 1)
        self._show_step()
        self._redraw()

    def next_step(self):
        self.step_index = min(len(self.steps) - 1, self.step_index + 1)
        self._show_step()
        self._redraw()

    def first_step(self):
        self.step_index = 0
        self._show_step()
        self._redraw()

    def last_step(self):
        self.step_index = len(self.steps) - 1
        self._show_step()
        self._redraw()

    def _show_step(self):
        node, path = self.steps[self.step_index]
        if node:
            label = f"Step {self.step_index + 1}/{len(self.steps)}  ·  {node.get('node', '?')}  ·  score {node.get('score', '?')}"
        else:
            label = "No search tree recorded"
        if self.step_index == len(self.steps) - 1 and len(self.steps) >= self.MAX_STEPS:
            label += "  (step limit reached)"
        self.selected_label.config(text=label)
        self.step_counter.config(text=f"{self.step_index + 1} / {len(self.steps)}")
        self.prev_btn.config(state="normal" if self.step_index > 0 else "disabled")
        self.next_btn.config(state="normal" if self.step_index < len(self.steps) - 1 else "disabled")

    def _on_mousewheel(self, event):
        if event.delta:
            self.canvas.yview_scroll(-1 if event.delta > 0 else 1, "units")

    def _redraw(self):
        self.canvas.delete("all")
        self.positions.clear()
        if not self.visible_tree:
            return
        leaf_counter = [0]
        self._layout(self.visible_tree, (), 0, leaf_counter)
        total_leaves = max(1, leaf_counter[0])
        width = max(self.canvas.winfo_width(), total_leaves * self.NODE_WIDTH + 80, 700)
        height = (self.MAX_VISIBLE_DEPTH + 2) * self.LEVEL_HEIGHT
        # Scale leaf slots to the available minimum width, retaining a wide
        # scrollable canvas when the tree has many branches.
        slot_width = max(self.NODE_WIDTH, (width - 80) / total_leaves)
        self._draw_edges(self.visible_tree, (), slot_width, width)
        self.canvas.configure(scrollregion=(0, 0, width, height))

    def _layout(self, node, path, depth, leaf_counter):
        children = node.get("children", [])
        if not children:
            center = leaf_counter[0] + 0.5
            leaf_counter[0] += 1
        else:
            child_centers = [self._layout(child, path + (i,), depth + 1, leaf_counter) for i, child in enumerate(children)]
            center = sum(child_centers) / len(child_centers)
        self.positions[path] = (center, depth)
        return center

    def _draw_edges(self, node, path, slot_width, width):
        center, depth = self.positions[path]
        x = 40 + center * slot_width
        y = 34 + depth * self.LEVEL_HEIGHT
        for i, child in enumerate(node.get("children", [])):
            child_path = path + (i,)
            child_center, child_depth = self.positions[child_path]
            child_x = 40 + child_center * slot_width
            child_y = 34 + child_depth * self.LEVEL_HEIGHT
            self.canvas.create_line(x, y + 23, child_x, child_y - 23, fill="#b5c2cf", width=1.3)
            self._draw_edges(child, child_path, slot_width, width)

        selected = self.steps[self.step_index][1] if self.steps and self.steps[self.step_index][0] else None
        is_selected = path == selected
        label = f"{node.get('node', '?')}\n{node.get('score', '')}"
        if node.get("_summary"):
            fill, outline, color = "#f2f4f7", "#9aa8b5", "#596a78"
        elif is_selected:
            fill, outline, color = "#d6f5e3", "#1e8449", "#145a32"
        else:
            fill, outline, color = "#eaf3fb", "#2e86c1", "#183b56"
        self.canvas.create_rectangle(x - 58, y - 23, x + 58, y + 23, fill=fill, outline=outline, width=2 if is_selected else 1.2)
        self.canvas.create_text(x, y, text=label, width=110, font=("Arial", 8, "bold"), fill=color, justify="center")