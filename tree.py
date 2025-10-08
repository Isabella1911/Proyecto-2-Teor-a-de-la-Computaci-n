# tree.py (parche: soporta hojas (A, word) y (A, (terminal, word)))
from __future__ import annotations
from typing import Dict, List, Tuple, Union, Optional

# Puede venir como:
#  - Hoja: (A, "word")
#  - Hoja: (A, ("terminal", "word"))
#  - Interno: (A, leftNode, rightNode)
Node = Union[Tuple[str, str], Tuple[str, Tuple[str, str]], Tuple[str, "Node", "Node"]]

def _is_leaf(n: Node) -> bool:
    if not isinstance(n, tuple):
        return False
    if len(n) == 2:
        # (A, word) o (A, ("terminal","word"))
        return True
    return False

def _leaf_text(n: Node) -> Tuple[str, str]:
    """Devuelve (A, word_visible) para una hoja."""
    assert len(n) == 2
    A, payload = n
    if isinstance(payload, str):
        return A, payload
    # payload puede ser ("terminal", "word")
    if isinstance(payload, tuple) and len(payload) == 2 and isinstance(payload[1], str):
        return A, payload[1]
    # fallback (raro): renderiza lo que haya
    return A, str(payload)

def build_one_parse(table, words: List[str], start_symbol: str) -> Optional[Node]:
    n = len(words)
    cell = table[1][n]
    if start_symbol not in cell:
        return None

    def backtrack(i: int, span: int, A: str) -> Optional[Node]:
        # Preferir backpointer binario
        for bp in table[i][span].get(A, []):
            if isinstance(bp, tuple):
                B, k, C = bp
                left = backtrack(i, k, B)
                right = backtrack(i + k, span - k, C)
                if left and right:
                    return (A, left, right)
        # Intentar hoja
        if span == 1:
            w = words[i - 1]
            for leaf in table[i][span].get(A, []):
                if isinstance(leaf, str) and leaf == w:
                    # Devolver hoja en formato compatible (A, ("terminal", "word"))
                    return (A, (leaf, w))
        return None

    return backtrack(1, n, start_symbol)

def to_dot(node: Node) -> str:
    """Exporta a Graphviz DOT; tolera ambos formatos de hoja."""
    lines = ["digraph ParseTree {", 'node [shape=ellipse];']
    counter = 0

    def add(n: Node, parent_id: Optional[int] = None) -> int:
        nonlocal counter
        counter += 1
        my = counter
        if _is_leaf(n):
            A, word = _leaf_text(n)
            label = f'{A}\\n"{word}"'
            lines.append(f'{my} [label="{label}", shape=box];')
        else:
            # interno binario
            A = n[0]
            lines.append(f'{my} [label="{A}"];')
            left_id = add(n[1], my)
            right_id = add(n[2], my)
        if parent_id is not None:
            lines.append(f"{parent_id} -> {my};")
        return my

    add(node, None)
    lines.append("}")
    return "\n".join(lines)

# -------------------------------
# Dibujo con matplotlib (sin Graphviz)
# -------------------------------
def _tree_size(n: Node) -> int:
    if _is_leaf(n):
        return 1
    # interno binario
    return _tree_size(n[1]) + _tree_size(n[2])

def _layout_positions(n: Node, x0: float, x1: float, y: int,
                      pos: Dict[int, Tuple[float, int]], ids, edges):
    my_id = ids["next"]; ids["next"] += 1
    pos[my_id] = ((x0 + x1) / 2.0, y)
    if _is_leaf(n):
        return my_id
    # interno
    left, right = n[1], n[2]
    left_leaves = _tree_size(left)
    right_leaves = _tree_size(right)
    total = left_leaves + right_leaves
    lx0, lx1 = x0, x0 + (x1 - x0) * (left_leaves / total)
    rx0, rx1 = lx1, x1
    lid = _layout_positions(left, lx0, lx1, y + 1, pos, ids, edges)
    rid = _layout_positions(right, rx0, rx1, y + 1, pos, ids, edges)
    edges.append((my_id, lid))
    edges.append((my_id, rid))
    return my_id

def render_tree_matplotlib(node: Node, out_path: Optional[str] = None, dpi: int = 150):
    """
    Dibuja el árbol con matplotlib (sin estilos ni colores explícitos).
    """
    import matplotlib.pyplot as plt

    pos: Dict[int, Tuple[float, int]] = {}
    ids = {"next": 1}
    edges: List[Tuple[int, int]] = []
    width = float(_tree_size(node))
    _layout_positions(node, 0.0, max(1.0, width), 0, pos, ids, edges)

    xs = [x for x, _ in pos.values()]
    ys = [y for _, y in pos.values()]
    max_y = max(ys) if ys else 0

    fig = plt.figure(figsize=(max(6.0, width * 1.2), max(3.0, (max_y + 1) * 1.2)))
    ax = fig.add_subplot(111)
    ax.set_axis_off()

    # Aristas
    for a, b in edges:
        xa, ya = pos[a]
        xb, yb = pos[b]
        ax.plot([xa, xb], [-(ya), -(yb)], linewidth=1)

    # Textos
    # Recorremos nodos en el mismo orden del layout (1..N)
    def id_iter():
        i = 1
        while i < ids["next"]:
            yield i
            i += 1

    # Construir mapping id->texto recorriendo el árbol en el mismo orden
    text_map: Dict[int, str] = {}
    def assign_text(n: Node, node_id_iter):
        my_id = next(node_id_iter)
        if _is_leaf(n):
            A, word = _leaf_text(n)
            text_map[my_id] = f"{A}\n“{word}”"
            return
        text_map[my_id] = n[0]
        assign_text(n[1], node_id_iter)
        assign_text(n[2], node_id_iter)

    assign_text(node, id_iter())

    for nid, (x, y) in pos.items():
        ax.text(x, -y, text_map.get(nid, ""), ha="center", va="center")

    plt.tight_layout()
    if out_path:
        fig.savefig(out_path, dpi=dpi, bbox_inches="tight")
        plt.close(fig)
    else:
        plt.show()
