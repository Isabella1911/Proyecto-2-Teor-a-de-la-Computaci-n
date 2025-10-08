# tests/test_cyk.py
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from grammar import Grammar
from cnf import to_cnf
from cky import cyk_parse

GRAMMAR = (ROOT / "examples" / "english.cfg").read_text(encoding="utf-8")
G = Grammar.from_text(GRAMMAR, start_symbol="S")
GCNF = to_cnf(G)

def accepts(sentence: str) -> bool:
    words = [w.lower() for w in sentence.strip().replace(".", "").split()]
    _, ok = cyk_parse(GCNF, words)
    return ok

def test_accept_simple():
    assert accepts("She eats a cake")

def test_accept_pp():
    assert accepts("He cuts the meat with a knife")

def test_semantic_weird_but_accept():
    assert accepts("She drinks a cake")

def test_reject_bad_verb():
    assert not accepts("she eat a cake")

def test_reject_missing_det():
    assert not accepts("cat drinks the beer")

def test_reject_incomplete_pp():
    assert not accepts("She cuts the meat with")
