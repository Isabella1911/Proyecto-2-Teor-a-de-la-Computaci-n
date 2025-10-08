# main.py
from __future__ import annotations
import argparse
import time
import sys
import re
from pathlib import Path

from grammar import Grammar
from cnf import to_cnf
from cky import cyk_parse, dump_table, dump_unaries
from tree import build_one_parse, to_dot, render_tree_matplotlib


def load_grammar(path: Path, start: str) -> Grammar:
    text = path.read_text(encoding="utf-8")
    return Grammar.from_text(text, start_symbol=start)


def normalize_sentence(s: str) -> list[str]:
    # Normaliza: todo a minúsculas y sin puntuación
    s = s.lower()
    s = re.sub(r"[^\w\s]", " ", s)   # elimina signos
    s = re.sub(r"\s+", " ", s).strip()
    return s.split()


def cli():
    p = argparse.ArgumentParser(description="CFG → CNF + CYK parser con debug y matplotlib")
    p.add_argument("--grammar", "-g", type=Path, required=True, help="ruta del archivo .cfg")
    p.add_argument("--start", default="S", help="símbolo inicial (default: S)")
    p.add_argument("--sent", "-s", required=True, help='frase, ej: "She eats a cake with a fork"')
    p.add_argument("--export-dot", type=Path, help="exporta el árbol a formato DOT (Graphviz)")
    p.add_argument("--export-png", type=Path, help="exporta el árbol a imagen PNG (matplotlib)")
    p.add_argument("--show-cnf", action="store_true", help="imprimir reglas convertidas a CNF")
    p.add_argument("--debug", action="store_true", help="mostrar tabla CYK con detalles")
    args = p.parse_args()

    # === Cargar gramática ===
    g = load_grammar(args.grammar, args.start)
    gcnf = to_cnf(g)

    if args.show_cnf:
        print("# Reglas en CNF:")
        for r in gcnf.all_rules():
            print(f"{r.lhs} -> {' '.join(r.rhs)}")
        print()

    # === Normalizar frase ===
    words = normalize_sentence(args.sent)

    # === Verificar qué tokens matchean ===
    print("\n# Sanity: reglas léxicas que matchean cada token")
    for i, w in enumerate(words, start=1):
        hits = []
        for A, rhss in gcnf.prod.items():
            if (w,) in rhss:
                hits.append(A)
        print(f"  token[{i}]='{w}': {', '.join(sorted(hits)) if hits else '(ninguna)'}")
    print()

    # === Ejecutar algoritmo CYK ===
    t0 = time.perf_counter()
    table, ok = cyk_parse(gcnf, words)
    dt = time.perf_counter() - t0

    print("Resultado:", "SI" if ok else "NO")
    print(f"Tiempo: {dt*1000:.3f} ms")

    # === Depuración ===
    if args.debug:
        dump_unaries(table, words)
        print()
        dump_table(table, words)

    # === Si la oración pertenece al lenguaje ===
    if ok:
        node = build_one_parse(table, words, gcnf.start)
        if node:
            if args.export_dot:
                args.export_dot.write_text(to_dot(node), encoding="utf-8")
                print(f"Árbol exportado a: {args.export_dot}")
            if args.export_png:
                render_tree_matplotlib(node, str(args.export_png))
                print(f"Árbol exportado a: {args.export_png}")


if __name__ == "__main__":
    try:
        cli()
    except Exception as e:
        print("Error:", e, file=sys.stderr)
        sys.exit(1)
