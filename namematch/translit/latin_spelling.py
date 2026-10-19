"""Variantes orthographiques d'un nom déjà écrit en latin (Youssef -> Yousef, Yusef...)."""
from ..scripts import strip_accents

SUBS = [("ou", "u"), ("u", "ou"), ("oo", "u"), ("ei", "ay"), ("ay", "ei"), ("ee", "i"),
        ("i", "ee"), ("kh", "h"), ("q", "k"), ("k", "q"), ("dj", "j"), ("y", "i"),
        ("ph", "f"), ("ch", "sh"), ("sh", "ch"), ("o", "ou"), ("e", "i"), ("i", "e"),
        ("a", "e"), ("e", "a"), ("ss", "s"), ("dh", "d"), ("ah", "a"), ("eh", "a")]


def spelling_variants(tok, limit=12):
    low = strip_accents(tok).lower()
    out = set()
    for a, b in SUBS:
        start = 0
        while True:
            k = low.find(a, start)
            if k < 0:
                break
            out.add(low[:k] + b + low[k + len(a):])
            start = k + 1
    if low.endswith("h") and len(low) > 3:
        out.add(low[:-1])
    out.discard(low)
    ranked = sorted(out, key=lambda w: (abs(len(w) - len(low)), w))
    return [w.capitalize() for w in ranked[:limit]]
