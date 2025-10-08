# cnf.py
from __future__ import annotations
from typing import Dict, Set, Tuple, List
from grammar import Grammar, Rule

def to_cnf(g: Grammar) -> Grammar:
    """
    Conversión estándar (suficiente para el proyecto):
    1) Eliminar reglas vacías (ε) excepto si S -> ε (no usado aquí).
    2) Eliminar producciones unitarias A -> B.
    3) Sustituir terminales en reglas largas (A -> x B C ...).
    4) Binarizar reglas con longitud > 2.
    Notas: La gramática del enunciado ya está casi en CNF; esto es general.
    """
    g2 = Grammar(start=g.start)
    g2.variables = set(g.variables)
    g2.terminals = set(g.terminals)

    # Copia inicial
    for r in g.all_rules():
        g2.add_rule(r.lhs, r.rhs)

    # (1) No tratamos ε porque el enunciado no usa ε; placeholder por completitud.
    # (2) Eliminar unitarias A -> B
    changed = True
    while changed:
        changed = False
        new_rules: List[Rule] = []
        for A, rhss in list(g2.prod.items()):
            for rhs in list(rhss):
                if len(rhs) == 1 and rhs[0].isupper():
                    # A -> B
                    B = rhs[0]
                    rhss.remove(rhs)
                    for rhsB in g2.prod.get(B, set()):
                        if rhsB not in rhss:
                            new_rules.append(Rule(A, rhsB))
                            changed = True
        for r in new_rules:
            g2.add_rule(r.lhs, r.rhs)

    # (3) Terminales en reglas largas: reemplazar por Ti -> 't'
    term_map: Dict[str, str] = {}
    def lift_terminal(t: str) -> str:
        if t not in term_map:
            Ti = f"T_{t}"
            term_map[t] = Ti
            g2.variables.add(Ti)
            g2.add_rule(Ti, (t,))
        return term_map[t]

    for A, rhss in list(g2.prod.items()):
        for rhs in list(rhss):
            if len(rhs) >= 2 and any(s.islower() for s in rhs):
                new_rhs = tuple(lift_terminal(s) if s.islower() else s for s in rhs)
                rhss.remove(rhs)
                g2.add_rule(A, new_rhs)

    # (4) Binarización A -> X1 X2 X3 ... => A -> X1 Y1 ; Y1 -> X2 Y2 ; ...
    counter = 0
    for A, rhss in list(g2.prod.items()):
        for rhs in list(rhss):
            if len(rhs) > 2:
                rhss.remove(rhs)
                Xs = list(rhs)
                left = Xs[0]
                for i in range(1, len(Xs)-1):
                    counter += 1
                    new_var = f"{A}_BIN_{counter}"
                    g2.variables.add(new_var)
                    if i == 1:
                        g2.add_rule(A, (left, new_var))
                    else:
                        g2.add_rule(prev, (left, new_var))
                    left = Xs[i]
                    prev = new_var
                g2.add_rule(prev, (left, Xs[-1]))

    return g2
