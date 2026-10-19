"""Découpe un token hébreu ou arabe en "unités" phonétiques communes.

Une unité est un tuple (type, données) :
  ("C", options)    consonne ; options = [(latin, pénalité), ...]
  ("ALEF", hint)    alef (hint : "a", "i", "aa" pour les hamza arabes, sinon None)
  ("AYN", None)     ayin / ع
  ("W", None)       vav / و      ("WW", None) vav double (consonne w)
  ("Y", None)       yod / ي      ("YY", None) yod double
  ("END", None)     ה final / ة
  ("MAQ", None)     alif maqsura ى (son "a" final)
  ("V", voyelle)    haraka arabe explicite (a, i, u)
  ("SUK", None)     soukoun arabe (pas de voyelle)
"""
from ..scripts import APOS

HE_CONS = {
    "ב": [("b", 0), ("v", 0.7)], "ג": [("g", 0), ("j", 0.8)], "ד": [("d", 0)],
    "ה": [("h", 0)], "ז": [("z", 0)], "ח": [("h", 0), ("kh", 0.7)], "ט": [("t", 0)],
    "כ": [("k", 0), ("kh", 0.6)], "ך": [("k", 0), ("kh", 0.6)], "ל": [("l", 0)],
    "מ": [("m", 0)], "ם": [("m", 0)], "נ": [("n", 0)], "ן": [("n", 0)], "ס": [("s", 0)],
    "פ": [("f", 0), ("p", 0.6)], "ף": [("f", 0), ("p", 0.6)],
    "צ": [("s", 0), ("tz", 0.6), ("ts", 0.9)], "ץ": [("s", 0), ("tz", 0.6), ("ts", 0.9)],
    "ק": [("k", 0), ("q", 0.4)], "ר": [("r", 0)], "ש": [("sh", 0), ("s", 0.7)],
    "ת": [("t", 0)],
}
HE_GERESH = {
    "ג": [("j", 0), ("g", 0.6)], "ז": [("j", 0), ("zh", 0.6)], "צ": [("d", 0), ("dh", 0.5)],
    "ת": [("th", 0), ("t", 0.5)], "ד": [("dh", 0), ("d", 0.3), ("z", 0.8)],
    "ח": [("kh", 0), ("h", 0.5)], "כ": [("kh", 0), ("h", 0.5)], "ר": [("gh", 0), ("r", 0.6)],
    "ע": [("gh", 0), ("g", 0.5)], "ט": [("z", 0), ("dh", 0.6)],
}
AR_CONS = {
    "ب": [("b", 0)], "ت": [("t", 0)], "ث": [("th", 0), ("t", 0.5)], "ج": [("j", 0), ("g", 0.6)],
    "ح": [("h", 0)], "خ": [("kh", 0), ("h", 0.5)], "د": [("d", 0)],
    "ذ": [("dh", 0), ("z", 0.4), ("d", 0.6)], "ر": [("r", 0)], "ز": [("z", 0)], "س": [("s", 0)],
    "ش": [("sh", 0), ("ch", 0.7)], "ص": [("s", 0), ("ss", 0.7)], "ض": [("d", 0), ("dh", 0.5)],
    "ط": [("t", 0)], "ظ": [("z", 0), ("dh", 0.5)], "غ": [("gh", 0), ("g", 0.5)],
    "ف": [("f", 0)], "ق": [("q", 0), ("k", 0.3)], "ك": [("k", 0)], "ل": [("l", 0)],
    "م": [("m", 0)], "ن": [("n", 0)], "ه": [("h", 0)], "ک": [("k", 0)], "پ": [("p", 0)],
    "ڤ": [("v", 0)], "چ": [("ch", 0)],
}
AR_HAMZA_ALEF = {"أ": "a", "إ": "i", "آ": "aa", "ا": None, "ٱ": None}
AR_HARAKAT = {"َ": "a", "ِ": "i", "ُ": "u"}
AR_SUKUN, AR_SHADDA = "ْ", "ّ"


def he_units(tok):
    units, n, i = [], len(tok), 0
    while i < n:
        ch = tok[i]
        nxt = tok[i + 1] if i + 1 < n else ""
        if nxt and nxt in APOS and ch in HE_GERESH:
            units.append(("C", HE_GERESH[ch]))
            i += 2
            continue
        last = i == n - 1 or (i == n - 2 and nxt in APOS)
        if ch in "וי":
            kind = "W" if ch == "ו" else "Y"
            if nxt == ch:
                units.append((kind * 2, None))
                i += 2
                continue
            units.append((kind, None))
        elif ch == "א":
            units.append(("ALEF", None))
        elif ch == "ע":
            units.append(("AYN", None))
        elif ch == "ה" and last and i > 0:
            units.append(("END", None))
        elif ch in HE_CONS:
            units.append(("C", HE_CONS[ch]))
        i += 1
    return units


def ar_units(tok):
    units, n = [], len(tok)
    for i, ch in enumerate(tok):
        last = i == n - 1
        if ch in AR_HAMZA_ALEF:
            units.append(("ALEF", AR_HAMZA_ALEF[ch]))
        elif ch in "وؤ":
            if units and units[-1][0] == "W" and ch == "و":
                units[-1] = ("WW", None)
            else:
                units.append(("W", None))
        elif ch in "يئی":
            if units and units[-1][0] == "Y" and ch == "ي":
                units[-1] = ("YY", None)
            else:
                units.append(("Y", None))
        elif ch == "ى":
            units.append(("MAQ", None) if last and i > 0 else ("Y", None))
        elif ch == "ع":
            units.append(("AYN", None))
        elif ch == "ة" or (ch == "ه" and last and i > 1):
            units.append(("END", None))
        elif ch in AR_HARAKAT:
            units.append(("V", AR_HARAKAT[ch]))
        elif ch == AR_SUKUN:
            units.append(("SUK", None))
        elif ch == AR_SHADDA and units and units[-1][0] == "C":
            units[-1] = ("C", [(o * 2, p) for o, p in units[-1][1]] + units[-1][1])
        elif ch in AR_CONS:
            units.append(("C", AR_CONS[ch]))
    return units
