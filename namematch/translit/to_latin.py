"""Unités phonétiques (hébreu / arabe) -> orthographes latines "à l'anglaise", classées.

Exemple : עדוי -> Adawi, Adwi, Edawi, Adawy...
Chaque choix a une pénalité ; on garde les meilleures combinaisons (beam search).
"""
from .units import ar_units, he_units

BEAM = 60
# voyelles insérées entre deux consonnes (l'hébreu et l'arabe ne les écrivent pas)
FILLED = [("a", 0), ("e", 0.5), ("i", 0.9), ("o", 0.9), ("u", 1.0)]


class State:
    __slots__ = ("text", "pen", "ends", "c_after_v")

    def __init__(self, text="", pen=0.0, ends="S", c_after_v=False):
        self.text, self.pen, self.ends, self.c_after_v = text, pen, ends, c_after_v


def _opts(pairs, starts, ends, used=1):
    """[(texte, pénalité)] -> [(texte, pénalité, début, fin, unités consommées)]."""
    return [(t, p, starts, ends, used) for t, p in pairs]


def _kind(units, k):
    return units[k][0] if 0 <= k < len(units) else None


def _initial_vowel(units, nxt):
    """ALEF / AYN en début de mot, éventuellement fusionné avec la lettre suivante."""
    if nxt == "W":
        return _opts([("O", 0), ("U", 0.3), ("Ou", 0.6)], "V", "V", 2)
    if nxt == "Y" and len(units) > 2:
        return _opts([("I", 0), ("E", 0.3), ("Ei", 0.6)], "V", "V", 2)
    if nxt == "YY":
        return _opts([("Ay", 0), ("Ai", 0.4), ("Ei", 0.5)], "V", "V", 2)
    return None


def _chunk_alef(units, k, st):
    n, nxt = len(units), _kind(units, k + 1)
    if k == 0:
        merged = _initial_vowel(units, nxt)
        if merged:
            return merged
        hint = units[k][1]
        pairs = {"i": [("I", 0), ("E", 0.3)], "a": [("A", 0), ("E", 0.6)],
                 "aa": [("A", 0), ("Aa", 0.5)]}.get(hint)
        return _opts(pairs or [("A", 0), ("E", 0.5), ("I", 0.8), ("O", 0.9)], "V", "V")
    if st.ends == "V" and _kind(units, k - 1) in ("ALEF", "AYN"):    # Raed
        return _opts([("e", 0), ("'", 0.7), ("", 0.8)], "V", "V")
    return _opts([("a", 0), ("aa", 0.8 if k == n - 1 else 0.7)], "V", "V")


def _chunk_ayn(units, k, st):
    n, nxt = len(units), _kind(units, k + 1)
    if k == 0:
        merged = _initial_vowel(units, nxt)
        if merged:
            return merged
        if nxt == "ALEF":
            return _opts([("A", 0), ("Aa", 0.5)], "V", "V", 2)
        return _opts([("A", 0), ("E", 0.5), ("O", 0.8), ("I", 0.9)], "V", "V")
    if k == n - 1:
        return _opts([("a", 0), ("e", 0.5)], "V", "V")
    if st.ends == "V":
        return _opts([("a", 0), ("'a", 0.8)], "V", "V")
    if nxt == "ALEF":
        return _opts([("a", 0), ("aa", 0.5), ("'a", 0.7)], "V", "V", 2)
    if nxt in ("Y", "YY"):
        return _opts([("a", 0)], "V", "V")
    return _opts([("aa", 0), ("a", 0.2), ("a'", 0.7)], "V", "V")


def _chunk_w(units, k, st):
    n, nxt = len(units), _kind(units, k + 1)
    after_v = st.ends == "V"
    if k == 0:
        return _opts([("W", 0), ("V", 0.8)], "C", "C")
    if k == n - 1:
        if after_v:
            return _opts([("w", 0)], "C", "C") + _opts([("u", 0.5)], "V", "V")
        return _opts([("u", 0), ("o", 0.3), ("ou", 0.4)], "V", "V")
    if nxt == "Y" and k + 1 == n - 1:            # terminaison -awi (nisba)
        if after_v:
            return _opts([("wi", 0), ("wy", 0.6)], "X", "V", 2)
        return _opts([("awi", 0), ("wi", 0.5), ("awy", 0.6), ("ewi", 0.8)], "X", "V", 2)
    if nxt in ("ALEF", "END", "AYN") and not (nxt == "AYN" and not after_v):
        return _opts([("w", 0)], "C", "C") + _opts([("u", 0.8)], "V", "V")
    if after_v:
        if k + 1 == n - 1:                       # Daoud
            return _opts([("ou", 0)], "V", "V") + _opts([("w", 0.3)], "C", "C")
        return _opts([("w", 0)], "C", "C") + _opts([("u", 0.6)], "V", "V")
    return _opts([("ou", 0), ("u", 0.2), ("o", 0.3)], "V", "V")


def _chunk_y(units, k, st):
    n, nxt = len(units), _kind(units, k + 1)
    after_v = st.ends == "V"
    if k == 0:
        return _opts([("Y", 0)], "C", "C")
    if k == n - 1:
        pairs = [("i", 0), ("y", 0.3)] if after_v else [("i", 0), ("y", 0.6), ("ee", 0.8)]
        return _opts(pairs, "V", "V")
    if after_v and nxt in ("ALEF", "END"):
        return _opts([("y", 0)], "C", "C")
    if nxt == "ALEF":
        return _opts([("i", 0), ("iy", 0.4), ("y", 0.6)], "V", "V")
    if nxt == "END":
        return _opts([("i", 0), ("iy", 0.7)], "V", "V")
    if after_v:
        if _kind(units, k - 1) == "AYN":         # Saeed / Said
            return _opts([("ee", 0), ("i", 0.1)], "V", "V") + _opts([("y", 0.6)], "C", "C")
        return _opts([("i", 0)], "V", "V") + _opts([("y", 0.3)], "C", "C")
    return _opts([("i", 0), ("ee", 0.3), ("e", 0.6)], "V", "V")


def _chunk_yy(units, k, st):
    nxt = _kind(units, k + 1)
    if k == 0:
        return _opts([("Y", 0)], "C", "C")
    if st.ends == "V" or nxt in ("ALEF", "END", "AYN"):
        return _opts([("y", 0), ("yy", 0.5)], "C", "C")
    return _opts([("ei", 0), ("ay", 0.2), ("ai", 0.4)], "V", "V")


def _chunk_ww(units, k, st):
    if k == 0:
        return _opts([("W", 0)], "C", "C")
    return _opts([("w", 0), ("ww", 0.3), ("v", 0.9)], "C", "C")


def _chunk_end(units, k, st):
    if st.ends == "V":
        return _opts([("a", 0), ("ah", 0.4)], "V", "V")
    return _opts([("a", 0), ("ah", 0.3), ("eh", 0.4), ("e", 0.5)], "V", "V")


def _chunk_c(units, k, st):
    opts = units[k][1]
    if k > 0 and units[k - 1] == units[k]:       # consonne doublée (ex. לל)
        return _opts([(opts[0][0][-1], 0), ("", 0.4)], "X", "C")
    if k == 0:
        opts = [(t.capitalize(), p) for t, p in opts]
    return _opts(opts, "C", "C")


_CHUNKS = {
    "C": _chunk_c, "ALEF": _chunk_alef, "AYN": _chunk_ayn, "W": _chunk_w, "WW": _chunk_ww,
    "Y": _chunk_y, "YY": _chunk_yy, "END": _chunk_end,
    "MAQ": lambda u, k, st: _opts([("a", 0)], "V", "V"),
    "V": lambda u, k, st: _opts([(u[k][1], 0)], "V", "V"),
    "SUK": lambda u, k, st: _opts([("", 0)], "X", "C"),
}


def _gap_options(st, is_final, after_long_a):
    """Voyelle à insérer entre deux consonnes."""
    if is_final and after_long_a:  # schème CaaCiC : Jaber, Maher, Khaled, Adel
        return [("e", 0), ("i", 0.3), ("a", 0.5)]
    if not st.c_after_v:          # déjà 2 consonnes de suite (ou début de mot) : voyelle obligatoire
        return FILLED
    if is_final:                  # Ahm-a-d, Has-a-n : voyelle avant la dernière consonne
        return FILLED + [("", 1.0)]
    return [("", 0), ("a", 0.6), ("e", 0.9)]     # Ah-m-ad, Man-s-our


def render(units, limit=12):
    """Liste d'orthographes latines classées de la plus probable à la moins probable."""
    if not units:
        return []
    n = len(units)
    beams = {0: [State()]}
    finals = []
    for k in range(n):
        for st in beams.pop(k, []):
            for text, pen, starts, ends, used in _CHUNKS[units[k][0]](units, k, st):
                is_final = k + used >= n
                gaps = [("", 0)]
                if starts == "C" and st.ends == "C":
                    gaps = _gap_options(st, is_final, _kind(units, k - 2) == "ALEF")
                for gap, gpen in gaps:
                    if ends == "C":
                        c_after_v = bool(gap) or st.ends == "V" or len(text) > 1 and text[0] in "aeiou"
                    else:
                        c_after_v = False
                    nst = State(st.text + gap + text, st.pen + pen + gpen, ends, c_after_v)
                    if is_final:
                        finals.append(nst)
                    else:
                        beams.setdefault(k + used, []).append(nst)
        for key in beams:
            beams[key] = sorted(beams[key], key=lambda s: s.pen)[:BEAM]
    best = {}
    for st in finals:
        word = st.text[:1].upper() + st.text[1:]
        if word and (word not in best or st.pen < best[word]):
            best[word] = st.pen
    ranked = sorted(best.items(), key=lambda kv: (kv[1], len(kv[0])))
    return [w for w, _ in ranked[:limit]]


def hebrew_to_latin(tok, limit=12):
    return render(he_units(tok), limit)


def arabic_to_latin(tok, limit=12):
    return render(ar_units(tok), limit)
