"""Squelette consonantique phonétique, indépendant de l'écriture.

Chaque token donne une clé "fine" (distingue sh/s, kh/h...) et une clé "souple"
(regroupe les sons que les translittérations confondent souvent).
"""
import re

from .scripts import APOS, collapse, script_of, strip_accents

AR_FINE = {
    "ب": "b", "ت": "t", "ث": "T", "ج": "j", "ح": "H", "خ": "x", "د": "d", "ذ": "D",
    "ر": "r", "ز": "z", "س": "s", "ش": "S", "ص": "s", "ض": "d", "ط": "t", "ظ": "z",
    "ع": "", "غ": "G", "ف": "f", "ق": "q", "ك": "k", "ل": "l", "م": "m", "ن": "n",
    "ا": "",
}
HE_FINE = {
    "א": "", "ב": "b", "ג": "g", "ד": "d", "ז": "z", "ח": "H", "ט": "t", "כ": "k",
    "ך": "k", "ל": "l", "מ": "m", "ם": "m", "נ": "n", "ן": "n", "ס": "s", "ע": "",
    "פ": "p", "ף": "f", "צ": "Z", "ץ": "Z", "ק": "q", "ר": "r", "ש": "S", "ת": "t",
}
HE_GERESH = {"ג": "j", "צ": "x", "ז": "j", "ת": "T", "ד": "D", "ח": "x", "כ": "x", "ר": "G",
             "ע": "G", "ט": "z"}
# Lecture "hébreu moderne" alternative de certaines lettres (בכפ sans dagesh)
HE_ALT = {"ב": "v", "כ": "x", "ך": "x", "פ": "f"}
ARABIZI = {"2": "", "3": "", "5": "x", "6": "t", "7": "H", "8": "G", "9": "q"}
LATIN_DIGRAPHS = {"sh": "S", "kh": "x", "gh": "G", "th": "T", "dh": "D", "zh": "j",
                  "ph": "f", "ch": "x", "ts": "Z", "tz": "Z", "dj": "j"}
LOOSE = str.maketrans({"S": "s", "Z": "s", "x": "h", "H": "h", "T": "t", "D": "d",
                       "G": "g", "j": "g", "q": "k", "v": "f", "p": "b"})


def _semivowel(ch, i):
    """و/ו et ي/י : consonne en début de mot, voyelle ailleurs."""
    return ("w" if ch in "وו" else "y") if i == 0 else ""


# noms étrangers écrits en arabe : تس = ts (צ), تش = ch
AR_DIGRAPHS = {"تس": "Z", "تش": "x"}


def ar_fine(tok):
    out, n = [], len(tok)
    skip = False
    for i, ch in enumerate(tok):
        if skip:
            skip = False
            continue
        if tok[i:i + 2] in AR_DIGRAPHS:
            out.append(AR_DIGRAPHS[tok[i:i + 2]])
            skip = True
        elif ch in "وي":
            out.append(_semivowel(ch, i))
        elif ch == "ة":
            pass
        elif ch == "ه":
            out.append("h" if i < n - 1 else "")
        else:
            out.append(AR_FINE.get(ch, ""))
    return "".join(out)


def he_fine(tok, alt=False):
    out, n, i = [], len(tok), 0
    while i < n:
        ch = tok[i]
        nxt = tok[i + 1] if i + 1 < n else ""
        has_geresh = nxt != "" and nxt in APOS
        last = (i == n - 1) or (has_geresh and i + 1 == n - 1)
        if has_geresh and ch in HE_GERESH:
            out.append(HE_GERESH[ch])
            i += 2
            continue
        if alt and ch == "ו" and (i == 0 or last) and n > 2:
            out.append("v")                        # ורד = Vered, זיו = Ziv
        elif ch in "וי":
            out.append(_semivowel(ch, i))
        elif ch == "ה":
            out.append("" if last else "h")
        elif alt and ch == "פ":
            out.append("f")                        # פאדי = Fadi
        elif alt and ch == "ץ" and tok[:i].endswith("בי"):
            out.append("x")                        # -ביץ : Rabinovitz / Rabinovich
        elif alt and i > 0 and ch in HE_ALT:
            out.append(HE_ALT[ch])
        elif ch not in APOS:
            out.append(HE_FINE.get(ch, ""))
        i += 1
    return "".join(out)


def latin_fine(tok, ch_as_sh=False):
    t = strip_accents(tok).lower()
    t = t.replace("sch", "sh")                     # Schwartz
    if ch_as_sh:                                   # "ch" à la française : Chadi, Michel
        t = t.replace("ch", "sh")
    t = "".join(c for c in t if c not in APOS)
    out, i, n = [], 0, len(t)
    mixed = any(c.isdigit() for c in t) and any(c.isalpha() for c in t)
    while i < n:
        c, two = t[i], t[i:i + 2]
        if two in LATIN_DIGRAPHS:
            out.append(LATIN_DIGRAPHS[two])
            i += 2
            continue
        if c in "aeiou":
            pass
        elif c in "yw":
            out.append(c if i == 0 else "")
        elif c == "c":
            out.append("s" if t[i + 1:i + 2] in ("e", "i", "y") else "k")
        elif c == "x":
            out.append("ks")
        elif c.isdigit():
            if mixed:
                out.append(ARABIZI.get(c, ""))
        elif c.isalpha():
            out.append(c)
        i += 1
    return "".join(out)


def fine_keys(tok):
    """Une ou deux clés fines (l'hébreu a une lecture alternative v/kh/f)."""
    sc = script_of(tok)
    if sc == "ar":
        keys = [ar_fine(tok)]
    elif sc == "he":
        keys = [he_fine(tok), he_fine(tok, alt=True)]
    else:
        keys = [latin_fine(tok)]
        if "ch" in tok.lower():
            keys.append(latin_fine(tok, ch_as_sh=True))
    return [collapse(k) for k in keys]


def loose_key(fine):
    return collapse(fine.translate(LOOSE))


def _without_article(tok):
    sc = script_of(tok)
    low = strip_accents(tok).lower()
    if sc == "ar" and tok.startswith("ال") and len(tok) > 4:
        return tok[2:]
    if sc == "he" and tok.startswith("אל") and len(tok) >= 5:
        return tok[2:]
    if sc == "la" and re.match(r"^(al|el)", low) and len(low) >= 5:
        return tok[2:]
    return None


def token_keys(tok):
    """Liste de (fine, souple) : base, sans article, sans 'h' final, lecture alternative."""
    bases = [tok]
    stripped = _without_article(tok)
    if stripped:
        bases.append(stripped)
    keys = []
    for b in bases:
        for f in fine_keys(b):
            if not f:
                continue
            keys.append(f)
            if f.endswith("h") and len(f) >= 2:
                keys.append(f[:-1])
    seen, res = set(), []
    for f in keys:
        if f not in seen:
            seen.add(f)
            res.append((f, loose_key(f)))
    return res
