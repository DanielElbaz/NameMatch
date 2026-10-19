"""Lexique de prénoms / noms courants (latin | arabe | hébreu) chargé depuis data/lexicon.txt."""
import os
from collections import defaultdict

from .scripts import lex_norm

_PATH = os.path.join(os.path.dirname(__file__), "data", "lexicon.txt")


class Entry:
    __slots__ = ("id", "latin", "arabic", "hebrew", "particle")

    def __init__(self, id_, latin, arabic, hebrew):
        self.id = id_.lstrip("~")
        self.particle = id_.startswith("~")
        self.latin, self.arabic, self.hebrew = latin, arabic, hebrew

    def all_forms(self):
        return self.latin + self.arabic + self.hebrew

    def by_script(self, sc):
        return {"la": self.latin, "ar": self.arabic, "he": self.hebrew}[sc]


def _split_list(field):
    return [v.strip() for v in field.split(",") if v.strip()]


def load(path=_PATH):
    entries = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = [p.strip() for p in line.split("|")]
            parts += [""] * (4 - len(parts))
            entries.append(Entry(parts[0], *(_split_list(p) for p in parts[1:4])))
    return entries


ENTRIES = load()
BY_ID = {e.id: e for e in ENTRIES}


def _build_index():
    """forme normalisée -> [id, ...], l'entrée où la forme est la plus prioritaire d'abord."""
    ranked = defaultdict(dict)
    for order, e in enumerate(ENTRIES):
        for forms in (e.latin, e.arabic, e.hebrew):
            for pos, form in enumerate(forms):
                key = lex_norm(form.replace(" ", ""))
                ranked[key][e.id] = min(ranked[key].get(e.id, (pos, order)), (pos, order))
    return {k: sorted(ids, key=ids.get) for k, ids in ranked.items()}


INDEX = _build_index()
PARTICLES = {lex_norm(f) for e in ENTRIES if e.particle for f in e.all_forms()}
MAX_PHRASE = 3


def lookup(token):
    """Liste des ids du lexique correspondant exactement à un token (peut être vide)."""
    return INDEX.get(lex_norm(token.replace(" ", "")), [])


def lookup_phrase(tokens, start):
    """Cherche la plus longue suite de tokens (2..3) formant une entrée du lexique.

    Retourne (entry_id, nb_tokens) ou (None, 1).
    """
    for n in range(min(MAX_PHRASE, len(tokens) - start), 1, -1):
        ids = INDEX.get(lex_norm("".join(tokens[start:start + n])))
        if ids:
            return ids[0], n
    return None, 1


def is_particle(token):
    return lex_norm(token) in PARTICLES


def entry_forms(entry_id, sc):
    """Variantes d'une entrée pour une écriture ('la', 'ar', 'he')."""
    return BY_ID[entry_id].by_script(sc)
