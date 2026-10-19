"""Score de similarité entre deux noms (0-100), quel que soit l'ordre des tokens."""
from . import lexicon
from .phonetic import token_keys
from .scripts import lex_norm, script_of, split_tokens

try:
    from rapidfuzz import fuzz

    def ratio(a, b):
        return fuzz.ratio(a, b) / 100.0
except ImportError:  # repli sur la bibliothèque standard
    from difflib import SequenceMatcher

    def ratio(a, b):
        return SequenceMatcher(None, a, b).ratio()


LOOSE_EQUAL = 0.92


class Tok:
    __slots__ = ("text", "lexids", "keys")

    def __init__(self, text):
        self.text = text
        self.lexids = set(lexicon.lookup(text))
        self.keys = token_keys(text)


class Name:
    def __init__(self, raw):
        self.raw = raw
        toks = split_tokens(raw)
        merged = _merge_phrases(toks)            # Abu Ghosh, Abdel Rahman : un seul mot
        kept = [t for t in merged if not lexicon.is_particle(t)] or merged
        self.tokens = [Tok(t) for t in kept]

    def first_chars(self):
        return {loose[0] for t in self.tokens for (_, loose) in t.keys if loose}


def _merge_phrases(toks):
    """Recolle les entrées du lexique écrites en plusieurs mots (ex. 'Abdel Rahman')."""
    out, i = [], 0
    while i < len(toks):
        entry_id, n = lexicon.lookup_phrase(toks, i)
        out.append("".join(toks[i:i + n]) if entry_id else toks[i])
        i += n
    return out


def token_score(a, b):
    if a.lexids & b.lexids:
        return 1.0
    if lex_norm(a.text) == lex_norm(b.text):
        return 1.0
    best = 0.0
    for fa, la in a.keys:
        for fb, lb in b.keys:
            s = 0.4 * ratio(fa, fb) + 0.6 * ratio(la, lb)
            if la == lb:              # même squelette souple : seules des confusions de translittération
                s = max(s, LOOSE_EQUAL)
            best = max(best, s)
    if script_of(a.text) == script_of(b.text) == "la":
        # deux noms en latin : les voyelles départagent Omar / Amer, Ali / Eli
        best *= 0.8 + 0.2 * ratio(lex_norm(a.text), lex_norm(b.text))
    return best


def score_names(a, b):
    """Retourne (score 0-100, [(token_a, token_b, score 0-1), ...])."""
    if not isinstance(a, Name):
        a = Name(a)
    if not isinstance(b, Name):
        b = Name(b)
    if not a.tokens or not b.tokens:
        return 0.0, []
    pairs = sorted(((token_score(ta, tb), i, j)
                    for i, ta in enumerate(a.tokens)
                    for j, tb in enumerate(b.tokens)), reverse=True)
    used_i, used_j, chosen = set(), set(), []
    for s, i, j in pairs:
        if i in used_i or j in used_j:
            continue
        used_i.add(i)
        used_j.add(j)
        chosen.append((a.tokens[i].text, b.tokens[j].text, s))
    n_min = min(len(a.tokens), len(b.tokens))
    n_max = max(len(a.tokens), len(b.tokens))
    denom = n_min + 0.5 * (n_max - n_min)
    total = sum(s for _, _, s in chosen) / denom
    return round(min(total, 1.0) * 100, 1), chosen
