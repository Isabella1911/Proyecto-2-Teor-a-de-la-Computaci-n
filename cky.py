# cky.py
from __future__ import annotations
from typing import Dict, List, Tuple, DefaultDict
from collections import defaultdict
from grammar import Grammar

BackPtr = Tuple[str, int, str]  # (B, split_k, C) para A -> B C
LeafPtr = str                   # terminal reconocido

def cyk_parse(g: Grammar, words: List[str]):
    """
    Devuelve:
      - table[i][j]: dict {Variable: [(backpointers...) ...]}
      - acepta: bool
    Convención: i = inicio inclusive, j = longitud del span (1..n)
    """
    n = len(words)
    table: List[List[Dict[str, List[object]]]] = [
        [defaultdict(list) for _ in range(n+1)] for _ in range(n+1)
    ]

    # Inicializar celdas de longitud 1 (terminales)
    for i, w in enumerate(words, start=1):
        for A, rhss in g.prod.items():
            if (w,) in rhss:
                table[i][1][A].append(w)  # LeafPtr

    # DP para longitudes >= 2
    for span in range(2, n+1):
        for i in range(1, n - span + 2):
            for k in range(1, span):
                left = table[i][k]
                right = table[i+k][span-k]
                if not left or not right:
                    continue
                # Probar combinaciones B in left, C in right
                for A, rhss in g.prod.items():
                    for rhs in rhss:
                        if len(rhs) == 2:
                            B, C = rhs
                            if B in left and C in right:
                                table[i][span][A].append((B, k, C))  # BackPtr

    acepta = g.start in table[1][n]
    return table, acepta
# cky.py
def dump_table(table, words):
    """
    Muestra las celdas no vacías de la tabla CYK para depuración.
    Cada celda indica el fragmento de frase que cubre y las variables que lo generan.
    """
    n = len(words)
    print("\n=== DUMP DE TABLA CYK ===")
    for span in range(1, n + 1):
        for i in range(1, n - span + 2):
            cell = table[i][span]
            if not cell:
                continue
            fragment = " ".join(words[i - 1 : i - 1 + span])
            variables = ", ".join(sorted(cell.keys()))
            print(f"[i={i}, span={span}] '{fragment}' -> {{ {variables} }}")

def dump_unaries(table, words):
    print("\n=== DUMP SPAN=1 (base léxica) ===")
    for i, w in enumerate(words, start=1):
        cell = table[i][1]
        if cell:
            vars_in_cell = ", ".join(sorted(cell.keys()))
            print(f"[i={i}] '{w}' -> {{ {vars_in_cell} }}")
        else:
            print(f"[i={i}] '{w}' -> {{ }}")
