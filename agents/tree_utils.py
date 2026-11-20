"""Shared console-printing helper for search trees (BaseAgent is left untouched)."""


def _fmt(x):
    return f"{x:.2f}".rstrip("0").rstrip(".")


def _print_node(node, prefix, is_last, depth, max_depth, is_root):
    label = f"{node['node']}  [score={_fmt(node['score'])}]"
    if is_root:
        print(label)
        child_prefix = ""
    else:
        print(prefix + ("└── " if is_last else "├── ") + label)
        child_prefix = prefix + ("    " if is_last else "│   ")
    kids = node.get("children", [])
    if depth >= max_depth:
        if kids:
            print(child_prefix + f"└── ... ({len(kids)} children hidden)")
        return
    for i, ch in enumerate(kids):
        _print_node(ch, child_prefix, i == len(kids) - 1, depth + 1, max_depth, False)


class SearchTreeMixin:
    """Adds print_search_tree(); expects last_tree_data, nodes_expanded, last_execution_time."""

    def print_search_tree(self, max_print_depth: int = 3):
        print("=" * 60)
        print(f"{type(self).__name__} search tree (printed to depth {max_print_depth})")
        print("-" * 60)
        if self.last_tree_data:
            _print_node(self.last_tree_data, "", True, 0, max_print_depth, True)
        print("-" * 60)
        print(f"Nodes Expanded: {self.nodes_expanded}")
        print(f"Time Taken: {self.last_execution_time:.4f}s")
        print("=" * 60)
