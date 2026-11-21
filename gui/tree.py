import tkinter as tk
from tkinter import scrolledtext


class TreeWindow(tk.Toplevel):
    """Scrollable, complete search-tree explorer with step-by-step navigation."""

    NODE_WIDTH = 172
    LEVEL_HEIGHT = 104

    def __init__(self, parent, tree_data: dict, title_info: str):
        super().__init__(parent)
        self.title(f"Search Tree — {title_info}")
        self.geometry("1100x760")
        self.minsize(760, 520)
        self.configure(bg="#f3f6fb")
        self.tree_data = tree_data or {}
        self.stats = self.tree_data.get("_stats", {})
        self.steps = []
        self._collect_steps(self.tree_data, ())
        self.step_index_by_path = {path: index for index, (_node, path) in enumerate(self.steps)}
        self.step_index = 0
        self.positions = {}

        tk.Label(
            self, text="Search Tree Explorer", font=("Arial", 17, "bold"),
            fg="#17324d", bg="#f3f6fb"
        ).pack(pady=(12, 1))
        tk.Label(
            self, text=f"{title_info} · every recorded node and branch",
            font=("Arial", 10), fg="#66788a", bg="#f3f6fb"
        ).pack(pady=(0, 7))
        stats_text = (
            f"Nodes expanded: {self.stats.get('nodes_expanded', '—')}"
            f"    |    Search time: {self.stats.get('execution_time', 0.0):.4f}s"
            if self.stats else "Search statistics unavailable"
        )
        tk.Label(
            self, text=stats_text, font=("Arial", 10, "bold"),
            fg="#315b46", bg="#e9f7ef", padx=10, pady=6
        ).pack(pady=(0, 7))

        self.selected_label = tk.Label(
            self, text="", font=("Arial", 10), fg="#23435e",
            bg="#ffffff", anchor="w", justify="left", wraplength=1500,
            padx=10, pady=8, relief="groove", bd=1
        )
        self.selected_label.pack(fill="x", padx=12, pady=(2, 7))

        nav = tk.Frame(self, bg="#f3f6fb")
        nav.pack(pady=(0, 8))
        self.prev_btn = tk.Button(nav, text="← Previous", width=12, command=self.previous_step)
        self.prev_btn.pack(side="left", padx=5)
        self.step_counter = tk.Label(
            nav, text="", font=("Arial", 10, "bold"), bg="#f3f6fb",
            fg="#435b70", width=18
        )
        self.step_counter.pack(side="left", padx=5)
        self.next_btn = tk.Button(nav, text="Next →", width=12, command=self.next_step)
        self.next_btn.pack(side="left", padx=5)
        tk.Button(nav, text="Start", width=9, command=self.first_step).pack(side="left", padx=(12, 4))
        tk.Button(nav, text="End", width=9, command=self.last_step).pack(side="left", padx=4)

        legend = tk.Frame(self, bg="#f3f6fb")
        legend.pack(pady=(0, 7))
        legend_items = (
            ("ROOT", "#244b6b", "white"),
            ("MAX", "#dceeff", "#183b56"),
            ("MIN", "#fff0d9", "#704214"),
            ("CHANCE", "#efe4ff", "#503078"),
            ("LEAF", "#e1f5e8", "#205b36"),
            ("Selected", "#fff4cc", "#8a5a00"),
        )
        for text, fill, foreground in legend_items:
            tk.Label(
                legend, text=f" {text} ", font=("Arial", 9, "bold"),
                bg=fill, fg=foreground, padx=5, pady=3, relief="groove", bd=1
            ).pack(side="left", padx=4)

        diagram = tk.LabelFrame(
            self, text="Complete recorded search tree (scroll to explore)",
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
        tk.Label(
            lower, text="Complete readable tree trace", font=("Arial", 10, "bold"),
            bg="#f3f6fb", fg="#23435e"
        ).pack(anchor="w")
        self.trace = scrolledtext.ScrolledText(
            lower, height=8, font=("Consolas", 9), wrap="none"
        )
        self.trace.pack(fill="x", pady=(3, 0))
        self.trace.insert("1.0", self._format_text(self.tree_data))
        self.trace.config(state="disabled")

        if not self.steps:
            self.steps = [({}, ())]
        self._show_step()
        self._redraw()

    def _collect_steps(self, node, path):
        """Record every node in depth-first order for the navigation buttons."""
        if not isinstance(node, dict) or not node:
            return
        self.steps.append((node, path))
        for index, child in enumerate(node.get("children", [])):
            self._collect_steps(child, path + (index,))

    def _format_text(self, node):
        """Return a complete indented tree trace; no node/depth truncation."""
        if not node:
            return "<No tree recorded yet>\n"

        lines = []
        stack = [(node, "", True, True)]
        while stack:
            current, prefix, is_last, is_root = stack.pop()
            score = current.get("score", "?")
            label = f"{current.get('node', '?')} [score={score}]"
            if is_root:
                lines.append(label)
                child_prefix = ""
            else:
                lines.append(prefix + ("└── " if is_last else "├── ") + label)
                child_prefix = prefix + ("    " if is_last else "│   ")

            children = current.get("children", [])
            for index in range(len(children) - 1, -1, -1):
                stack.append((
                    children[index], child_prefix,
                    index == len(children) - 1, False
                ))
        return "\n".join(lines) + "\n"

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
            node_name = node.get("node", "?")
            node_type = node_name.split("(", 1)[0].strip()
            children_count = len(node.get("children", []))
            route = "ROOT" if not path else "ROOT → " + " → ".join(
                f"branch {branch + 1}" for branch in path
            )
            label = (
                f"Step {self.step_index + 1}/{len(self.steps)}  ·  {node_name}\n"
                f"Evaluation score: {node.get('score', '?')}    |    "
                f"Node type: {node_type}    |    Depth: {len(path)}    |    "
                f"Children: {children_count}\nPath: {route}"
            )
        else:
            label = "No search tree recorded"
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
        if not self.tree_data:
            return

        leaf_counter = [0]
        max_depth = self._layout(self.tree_data, (), 0, leaf_counter)
        total_leaves = max(1, leaf_counter[0])
        width = max(self.canvas.winfo_width(), total_leaves * self.NODE_WIDTH + 80, 700)
        height = max(self.canvas.winfo_height(), (max_depth + 2) * self.LEVEL_HEIGHT)
        slot_width = max(self.NODE_WIDTH, (width - 80) / total_leaves)
        self._draw_edges(self.tree_data, (), slot_width)
        self.canvas.configure(scrollregion=(0, 0, width, height))

    def _layout(self, node, path, depth, leaf_counter):
        """Assign every node a position and return the deepest level below it."""
        children = node.get("children", [])
        if not children:
            center = leaf_counter[0] + 0.5
            leaf_counter[0] += 1
            deepest = depth
        else:
            child_centers = []
            deepest = depth
            for index, child in enumerate(children):
                child_depth = self._layout(child, path + (index,), depth + 1, leaf_counter)
                child_centers.append(self.positions[path + (index,)][0])
                deepest = max(deepest, child_depth)
            center = sum(child_centers) / len(child_centers)
        self.positions[path] = (center, depth)
        return deepest

    def _draw_edges(self, node, path, slot_width):
        center, depth = self.positions[path]
        x = 40 + center * slot_width
        y = 34 + depth * self.LEVEL_HEIGHT

        children = node.get("children", [])
        for index, child in enumerate(children):
            child_path = path + (index,)
            child_center, child_depth = self.positions[child_path]
            child_x = 40 + child_center * slot_width
            child_y = 34 + child_depth * self.LEVEL_HEIGHT
            self.canvas.create_line(
            x, y + 27, child_x, child_y - 27,
                fill="#b5c2cf", width=1.3
            )
            self._draw_edges(child, child_path, slot_width)

        selected = self.steps[self.step_index][1] if self.steps else None
        is_selected = path == selected
        label = f"{node.get('node', '?')}\n{node.get('score', '')}"
        node_name = str(node.get("node", "?")).upper()
        if node_name.startswith("ROOT"):
            fill, outline, color = "#244b6b", "#17324d", "white"
        elif node_name.startswith("MAX"):
            fill, outline, color = "#dceeff", "#4385b5", "#183b56"
        elif node_name.startswith("MIN"):
            fill, outline, color = "#fff0d9", "#c28a3e", "#704214"
        elif node_name.startswith("CHANCE"):
            fill, outline, color = "#efe4ff", "#8463b6", "#503078"
        elif node_name.startswith("LEAF"):
            fill, outline, color = "#e1f5e8", "#57a773", "#205b36"
        else:
            fill, outline, color = "#eef2f6", "#8796a5", "#34495e"
        if is_selected:
            fill, outline, color = "#fff4cc", "#d18a00", "#5c4100"
        tag = "tree_node_" + ("root" if not path else "_".join(map(str, path)))
        self.canvas.create_rectangle(
            x - 75, y - 27, x + 75, y + 27,
            fill=fill, outline=outline, width=2 if is_selected else 1.2,
            tags=(tag, "tree_node")
        )
        self.canvas.create_text(
            x, y, text=label, width=145, font=("Arial", 9, "bold"),
            fill=color, justify="center", tags=(tag, "tree_node")
        )
        self.canvas.tag_bind(
            tag, "<Button-1>",
            lambda _event, selected_path=path: self._select_node(selected_path)
        )

    def _select_node(self, path):
        """Select a node directly from the diagram and show its details."""
        index = self.step_index_by_path.get(path)
        if index is None:
            return
        self.step_index = index
        self._show_step()
        self._redraw()