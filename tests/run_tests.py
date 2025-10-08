# tests/run_tests.py
import sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from grammar import Grammar
from cnf import to_cnf
from cky import cyk_parse

def run(sentences):
    gtext = (ROOT / "examples" / "english.cfg").read_text(encoding="utf-8")
    g = Grammar.from_text(gtext, start_symbol="S")
    gcnf = to_cnf(g)

    for s in sentences:
        words = [w.lower() for w in s.strip().replace(".", "").split()]
        t0 = time.perf_counter()
        table, ok = cyk_parse(gcnf, words)
        dt = (time.perf_counter() - t0) * 1000
        print(f"[{'SI' if ok else 'NO'}] {s}  ({dt:.2f} ms)")

if __name__ == "__main__":
    sample = [
        "She eats a cake",
        "He cuts the meat with a knife",
        "She drinks a cake",
        "she eat a cake",
        "cat drinks the beer",
        "She cuts the meat with",
    ]
    run(sample)
