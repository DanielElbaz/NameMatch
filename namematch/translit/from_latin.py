"""Latin -> écriture arabe ou hébraïque (conventions des noms arabes en Israël)."""
from ..scripts import APOS, strip_accents

FINAL_HE = {"כ": "ך", "מ": "ם", "נ": "ן", "פ": "ף", "צ": "ץ"}

# consonnes : [(forme, pénalité), ...] ; la première est la plus courante
CONS = {
    "ar": {
        "b": [("ب", 0)], "t": [("ت", 0), ("ط", 0.6)], "j": [("ج", 0)], "g": [("ج", 0), ("غ", 0.5)],
        "h": [("ح", 0), ("ه", 0.4)], "d": [("د", 0), ("ض", 0.8)], "r": [("ر", 0)], "z": [("ز", 0)],
        "s": [("س", 0), ("ص", 0.5)], "f": [("ف", 0)], "q": [("ق", 0)], "k": [("ك", 0), ("ق", 0.5)],
        "l": [("ل", 0)], "m": [("م", 0)], "n": [("ن", 0)], "w": [("و", 0)], "y": [("ي", 0)],
        "p": [("ب", 0)], "v": [("ف", 0)], "c": [("ك", 0)], "x": [("كس", 0)],
        "sh": [("ش", 0)], "kh": [("خ", 0)], "gh": [("غ", 0)], "th": [("ث", 0), ("ت", 0.5)],
        "dh": [("ذ", 0), ("ض", 0.5)], "ch": [("ش", 0), ("خ", 0.6)], "ph": [("ف", 0)],
        "ts": [("تس", 0)], "tz": [("تس", 0)], "dj": [("ج", 0)], "zh": [("ج", 0)],
        "'": [("ع", 0)],
    },
    "he": {
        "b": [("ב", 0)], "t": [("ת", 0), ("ט", 0.5)], "j": [("ג'", 0)], "g": [("ג", 0)],
        "h": [("ח", 0), ("ה", 0.4)], "d": [("ד", 0)], "r": [("ר", 0)], "z": [("ז", 0)],
        "s": [("ס", 0), ("צ", 0.6)], "f": [("פ", 0)], "q": [("ק", 0)], "k": [("כ", 0), ("ק", 0.4)],
        "l": [("ל", 0)], "m": [("מ", 0)], "n": [("נ", 0)], "w": [("ו", 0)], "y": [("י", 0)],
        "p": [("פ", 0)], "v": [("ב", 0), ("ו", 0.5)], "c": [("ק", 0)], "x": [("קס", 0)],
        "sh": [("ש", 0)], "kh": [("ח'", 0), ("ח", 0.3)], "gh": [("ע'", 0), ("ג", 0.5)],
        "th": [("ת'", 0), ("ת", 0.4)], "dh": [("ד'", 0), ("ד", 0.4)],
        "ch": [("ח", 0), ("ש", 0.5)], "ph": [("פ", 0)], "ts": [("צ", 0)], "tz": [("צ", 0)],
        "dj": [("ג'", 0)], "zh": [("ז'", 0)], "'": [("ע", 0)],
    },
}
DIGRAPHS = ("sh", "kh", "gh", "th", "dh", "ch", "ph", "ts", "tz", "dj", "zh")
LONG = {"aa": "a", "ee": "i", "ii": "i", "ie": "i", "ou": "u", "oo": "u", "uu": "u"}
ALEF = {"ar": "ا", "he": "א"}
AYN = {"ar": "ع", "he": "ע"}
VAV = {"ar": "و", "he": "ו"}
YOD = {"ar": "ي", "he": "י"}


def _segments(word):
    """'mohammad' -> [('C','m'), ('V','o'), ('C','h'), ...] (lettres doublées fusionnées)."""
    t = strip_accents(word).lower()
    t = "".join("'" if c in APOS else c for c in t if c.isalpha() or c in APOS)
    t = t.replace("sch", "sh")
    segs, i = [], 0
    while i < len(t):
        two = t[i:i + 2]
        if two in LONG:
            segs.append(("L", LONG[two]))
            i += 2
        elif two in DIGRAPHS:
            segs.append(("C", two))
            i += 2
        elif t[i] in "aeiou":
            segs.append(("V", t[i]))
            i += 1
        else:
            segs.append(("C", t[i]))
            i += 1
        if len(segs) > 1 and segs[-1] == segs[-2] and segs[-1][0] == "C":
            segs.pop()                              # Hassan -> Hasan
    return segs


def _vowel_options(segs, k, sc):
    kind, v = segs[k]
    n = len(segs)
    first, last = k == 0, k == n - 1
    open_syll = k + 2 < n and segs[k + 1][0] == "C" and segs[k + 2][0] in "VL"
    if first:
        base = ALEF[sc]
        if sc == "he" and v in "ou":
            base += VAV[sc]
        elif sc == "he" and v == "i":
            base += YOD[sc]
        return [(base, 0), (AYN[sc] + base[1:], 0.4)]
    if kind == "L":
        return [({"a": ALEF, "i": YOD, "u": VAV}[v][sc], 0)]
    if last:
        if v in "ae":
            return [("ة" if sc == "ar" else "ה", 0), ("ا" if sc == "ar" else "א", 0.4)]
        return [(YOD[sc] if v == "i" else VAV[sc], 0)]
    if v in "ou":
        return [(VAV[sc], 0), ("", 0.6)]
    if v == "i":
        return [(YOD[sc], 0), ("", 0.5)]
    if v == "a" and open_syll and sc == "he":   # Jaber -> ג'אבר, Sami -> סאמי
        return [(ALEF[sc], 0), ("", 0.3)]
    if v == "a" and sc == "he" and k + 2 == n and segs[k + 1][0] == "C":
        return [("", 0), (ALEF[sc], 0.2)]       # Hamdan -> חמדן / חמדאן
    return [("", 0), (ALEF[sc], 0.5)] if v == "a" else [("", 0)]


# Arabe "plein" pour les noms d'origine hébraïque / étrangère : toutes les voyelles s'écrivent
# (Hadar -> هدار, Orel -> أوريل, Rabinovich -> ربينوفيتش)
PLENE_AR_CONS = {"ch": [("خ", 0), ("تش", 0.4)], "h": [("ه", 0), ("ح", 0.4)],
                 "ts": [("تس", 0)], "tz": [("تس", 0)], "s": [("س", 0)], "t": [("ت", 0), ("ط", 0.5)]}


def _vowel_options_plene_ar(segs, k):
    kind, v = segs[k]
    n = len(segs)
    if k == 0:
        base = {"o": "أو", "u": "أو", "i": "إي", "e": "إي"}.get(v, "أ")
        return [(base, 0), ("ع" + base[1:], 0.4)]
    if kind == "L":
        return [({"a": "ا", "i": "ي", "u": "و"}[v], 0)]
    if k == n - 1:
        return {"a": [("ا", 0), ("ة", 0.5)], "e": [("يه", 0), ("ه", 0.4)],
                "i": [("ي", 0)]}.get(v, [("و", 0)])
    return {"a": [("ا", 0), ("", 0.4)], "e": [("ي", 0), ("", 0.3)],
            "i": [("ي", 0)]}.get(v, [("و", 0)])


def _cons_options(segs, k, sc):
    c = segs[k][1]
    last = k == len(segs) - 1
    if c == "h" and last:
        return [("ه" if sc == "ar" else "ה", 0)]   # Abdallah
    if c == "w" and sc == "he" and 0 < k < len(segs) - 1:
        return [("ו", 0), ("וו", 0.3)]
    return CONS[sc].get(c, [("", 0)])


def _finalize(word, sc):
    if sc == "he" and word:
        stem = word.rstrip("'")
        if stem and stem[-1] in FINAL_HE:
            word = stem[:-1] + FINAL_HE[stem[-1]] + word[len(stem):]
    return word


def latin_to_script(word, sc, limit=3, style="ar"):
    """Translittérations classées de 'word' vers 'ar' ou 'he'.

    style "he" + sc "ar" : nom d'origine hébraïque écrit en arabe, voyelles notées.
    """
    segs = _segments(word)
    plene = style == "he" and sc == "ar"
    beams = [("", 0.0)]
    for k, (kind, c) in enumerate(segs):
        if kind == "C":
            opts = PLENE_AR_CONS.get(c) if plene else None
            if plene and c == "ch" and k == len(segs) - 1:
                opts = [("تش", 0)]                  # Rabinovich
            opts = opts or _cons_options(segs, k, sc)
        else:
            opts = _vowel_options_plene_ar(segs, k) if plene else _vowel_options(segs, k, sc)
        beams = sorted(((txt + o, pen + p) for txt, pen in beams for o, p in opts),
                       key=lambda b: b[1])[:40]
    seen, out = set(), []
    for txt, _ in beams:
        txt = _finalize(txt, sc)
        if txt and txt not in seen:
            seen.add(txt)
            out.append(txt)
    return out[:limit]
