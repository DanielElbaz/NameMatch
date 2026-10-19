"""Lexique de prénoms / noms courants (latin | arabe | hébreu).

Trois fichiers, du plus prioritaire au moins prioritaire :
  data/user_lexicon.txt   corrections de l'utilisateur (créé par la commande / le bouton "Corriger")
  data/lexicon.txt        noms d'origine arabe
  data/lexicon_he.txt     noms d'origine hébraïque / juive
"""
import os
from collections import defaultdict

from .scripts import lex_norm, script_of

_DATA = os.path.join(os.path.dirname(__file__), "data")
SOURCES = (  # (nom, fichier, origine)
    ("user", None, None),
    ("ar", os.path.join(_DATA, "lexicon.txt"), "ar"),
    ("he", os.path.join(_DATA, "lexicon_he.txt"), "he"),
)
MAX_PHRASE = 3
_SCRIPT_FIELD = {"la": "latin", "ar": "arabic", "he": "hebrew"}


def user_path():
    return os.environ.get("NAMEMATCH_USER_LEXICON") or os.path.join(_DATA, "user_lexicon.txt")


class Entry:
    __slots__ = ("id", "latin", "arabic", "hebrew", "particle", "origin", "source")

    def __init__(self, id_, latin, arabic, hebrew, origin=None, source=""):
        self.particle = id_.startswith("~")
        self.id = f"{source}:{id_.lstrip('~')}"
        self.latin, self.arabic, self.hebrew = latin, arabic, hebrew
        self.origin, self.source = origin, source

    def all_forms(self):
        return self.latin + self.arabic + self.hebrew

    def by_script(self, sc):
        return getattr(self, _SCRIPT_FIELD[sc])

    def to_line(self):
        name = ("~" if self.particle else "") + self.id.split(":", 1)[1]
        return " | ".join([name] + [", ".join(x) for x in (self.latin, self.arabic, self.hebrew)])


def _split_list(field):
    return [v.strip() for v in field.split(",") if v.strip()]


def load(path, origin=None, source=""):
    entries = []
    if not path or not os.path.exists(path):
        return entries
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = [p.strip() for p in line.split("|")]
            parts += [""] * (4 - len(parts))
            entries.append(Entry(parts[0], *(_split_list(p) for p in parts[1:4]),
                                 origin=origin, source=source))
    return entries


def _key(text):
    return lex_norm(text.replace(" ", "").replace("-", ""))


def _build_index(entries):
    """forme normalisée -> [id, ...] : corrections d'abord, puis forme la plus prioritaire."""
    ranked = defaultdict(dict)
    for order, e in enumerate(entries):
        rank_src = 0 if e.source == "user" else 1
        for forms in (e.latin, e.arabic, e.hebrew):
            for pos, form in enumerate(forms):
                key = _key(form)
                cur = (rank_src, pos, order)
                ranked[key][e.id] = min(ranked[key].get(e.id, cur), cur)
    return {k: sorted(ids, key=ids.get) for k, ids in ranked.items()}


ENTRIES, BY_ID, INDEX, PARTICLES = [], {}, {}, set()


def reload():
    global ENTRIES, BY_ID, INDEX, PARTICLES
    ENTRIES = []
    for source, path, origin in SOURCES:
        ENTRIES += load(path or user_path(), origin, source)
    BY_ID = {e.id: e for e in ENTRIES}
    INDEX = _build_index(ENTRIES)
    PARTICLES = {lex_norm(f) for e in ENTRIES if e.particle for f in e.all_forms()}


reload()


def lookup(token, prefer=None):
    """Ids du lexique correspondant exactement à un token (peut être vide).

    prefer ('he' / 'ar') : à égalité, les entrées de cette origine passent devant
    (ex. עומר = Omer en hébreu, Omar en arabe). Les corrections restent toujours en tête.
    """
    ids = INDEX.get(_key(token), [])
    if prefer and len(ids) > 1:
        ids = sorted(ids, key=lambda i: (BY_ID[i].source != "user", BY_ID[i].origin != prefer))
    return ids


def origin_of(entry_id):
    return BY_ID[entry_id].origin


def lookup_phrase(tokens, start):
    """Cherche la plus longue suite de tokens (2..3) formant une entrée du lexique.

    Retourne (entry_id, nb_tokens) ou (None, 1).
    """
    for n in range(min(MAX_PHRASE, len(tokens) - start), 1, -1):
        ids = INDEX.get(_key("".join(tokens[start:start + n])))
        if ids:
            return ids[0], n
    return None, 1


def is_particle(token):
    return lex_norm(token) in PARTICLES


def entry_forms(entry_id, sc):
    """Variantes d'une entrée pour une écriture ('la', 'ar', 'he')."""
    return BY_ID[entry_id].by_script(sc)


def add_correction(token, value):
    """Enregistre que 'token' s'écrit 'value' (dans l'écriture de value) et recharge le lexique.

    La correction passe devant toutes les autres variantes pour ce nom.
    """
    token, value = token.strip(), value.strip()
    if not token or not value:
        raise ValueError("nom vide")
    key = _key(token)
    user = [e for e in ENTRIES if e.source == "user"]
    entry = next((e for e in user if key in {_key(f) for f in e.all_forms()}), None)
    if entry is None:
        base = next((BY_ID[i] for i in lookup(token) if BY_ID[i].source != "user"), None)
        lists = [list(base.by_script(s)) if base else [] for s in ("la", "ar", "he")]
        entry = Entry(f"u{len(user) + 1}", *lists, origin=base.origin if base else None,
                      source="user")
        entry.particle = bool(base and base.particle)
        user.append(entry)
    own = entry.by_script(script_of(token))
    if key not in {_key(f) for f in own}:
        own.insert(0, token)
    target = entry.by_script(script_of(value))
    target[:] = [value] + [f for f in target if f != value]
    _save_user(user)
    reload()
    return entry


def _save_user(entries):
    path = user_path()
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write("# Corrections NameMatch (prioritaires sur le lexique).\n"
                "# Format : id | latin | arabe | hébreu\n")
        for e in entries:
            f.write(e.to_line() + "\n")
