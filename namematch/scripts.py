"""Détection d'écriture, normalisation et découpage en tokens."""
import re
import unicodedata

APOS = "'’`ʿʾʻ´׳"

_AR_DIAC = re.compile("[ً-ٰٟـۖ-ۭ]")
_HE_DIAC = re.compile("[֑-ׇׄ]")
_AR_NORM = str.maketrans({
    "أ": "ا", "إ": "ا", "آ": "ا", "ٱ": "ا", "ى": "ي", "ی": "ي", "ؤ": "و",
    "ئ": "ي", "ک": "ك", "ء": "", "پ": "ب", "ڤ": "ف", "چ": "ج",
})
_SPLIT = re.compile(r"[\s\-_.,/;:()]+")


def has_arabic(s):
    return any("؀" <= c <= "ۿ" for c in s)


def has_hebrew(s):
    return any("֐" <= c <= "׿" for c in s)


def script_of(s):
    """'ar', 'he' ou 'la' (latin / autre)."""
    if has_arabic(s):
        return "ar"
    if has_hebrew(s):
        return "he"
    return "la"


def strip_accents(s):
    return "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))


def strip_apos(s):
    return "".join(c for c in s if c not in APOS)


def prep(s):
    """Normalisation lourde (pour la comparaison) : sans diacritiques, hamza unifiée."""
    s = unicodedata.normalize("NFKC", s)
    s = _AR_DIAC.sub("", s)
    s = _HE_DIAC.sub("", s)
    s = s.translate(_AR_NORM)
    return s.strip()


def prep_light(s):
    """Normalisation légère (pour la translittération) : garde hamza et harakat."""
    s = unicodedata.normalize("NFKC", s)
    s = _HE_DIAC.sub("", s).replace("ـ", "")
    return s.strip()


def split_raw(s):
    return [t for t in _SPLIT.split(s) if t]


def split_tokens(s):
    return split_raw(prep(s))


def collapse(s):
    """Supprime les lettres doublées : 'mohammad' -> 'mohamad'."""
    return re.sub(r"(.)\1+", r"\1", s)


def lex_norm(tok):
    """Forme canonique d'un token pour les recherches dans le lexique."""
    t = strip_accents(prep(tok)).lower()
    t = "".join(c for c in t if c not in APOS and c != '"')
    return collapse(t)
