# grammar.py
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple, Iterable

RHS = Tuple[str, ...]  # lado derecho como tupla inmutable

@dataclass(frozen=True, slots=True)
class Rule:
    lhs: str
    rhs: RHS

@dataclass
class Grammar:
    start: str
    variables: Set[str] = field(default_factory=set)
    terminals: Set[str] = field(default_factory=set)
    rules: List[Rule] = field(default_factory=list)
    prod: Dict[str, Set[RHS]] = field(default_factory=dict)

    def add_rule(self, lhs: str, rhs: Iterable[str]) -> None:
        tup = tuple(rhs)
        self.variables.add(lhs)
        for s in tup:
            if s.islower() and len(s) > 1:
                # Palabras minúsculas (p.ej. 'with', 'knife') => terminal
                self.terminals.add(s)
        rule = Rule(lhs, tup)
        self.rules.append(rule)
        self.prod.setdefault(lhs, set()).add(tup)

    def all_rules(self) -> Iterable[Rule]:
        for lhs, rhss in self.prod.items():
            for rhs in rhss:
                yield Rule(lhs, rhs)

    # grammar.py (solo reemplaza el método from_text)
    @staticmethod
    def from_text(text: str, start_symbol: str = "S") -> "Grammar":
        """
        Formato:
        # comentarios con #
        A -> B C | a | D E F
        A → B C | a                 (soporta flecha unicode)
        A −> B C | a                (soporta guiones alternos)
        Terminales en minúsculas.
        """
        import re
        g = Grammar(start=start_symbol)

        # Regex de flecha: -> | → | −> | —> con espacios opcionales
        arrow = re.compile(r"\s*(->|→|−>|—>)\s*")

        for raw in text.splitlines():
            line = raw.strip()
            if not line or line.startswith("#"):
                continue

            # Normaliza tabs y múltiples espacios
            line = re.sub(r"\s+", " ", line)

            # Divide por flecha robusta
            parts = arrow.split(line, maxsplit=1)
            if len(parts) < 3:
                # Línea inválida, saltar
                continue

            lhs = parts[0].strip()
            rhs_part = parts[2].strip()

            # Soporta alternativas con '|'
            for alt in rhs_part.split("|"):
                symbols = alt.strip().split()
                if not symbols:
                    continue
                g.add_rule(lhs, symbols)

        # Heurística adicional (no crítica) para terminales
        for r in g.rules:
            for s in r.rhs:
                if s.islower() and s.isalpha():
                    g.terminals.add(s)
        return g
