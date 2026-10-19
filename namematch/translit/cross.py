"""Conversion directe arabe <-> hébreu, lettre à lettre."""
from ..scripts import APOS
from .from_latin import FINAL_HE

AR2HE = {"ا": "א", "أ": "א", "إ": "א", "آ": "א", "ء": "", "ؤ": "ו", "ئ": "י", "ب": "ב",
         "ت": "ת", "ث": "ת'", "ج": "ג'", "ح": "ח", "خ": "ח'", "د": "ד", "ذ": "ד'", "ر": "ר",
         "ز": "ז", "س": "ס", "ش": "ש", "ص": "צ", "ض": "צ'", "ط": "ט", "ظ": "ט'", "ع": "ע",
         "غ": "ע'", "ف": "פ", "ق": "ק", "ك": "כ", "ل": "ל", "م": "מ", "ن": "נ", "ه": "ה",
         "و": "ו", "ي": "י", "ى": "א", "ة": "ה"}
HE2AR = {"א": "ا", "ב": "ب", "ג": "ج", "ד": "د", "ה": "ه", "ו": "و", "ז": "ز", "ח": "ح",
         "ט": "ط", "י": "ي", "כ": "ك", "ך": "ك", "ל": "ل", "מ": "م", "ם": "م", "נ": "ن",
         "ן": "ن", "ס": "س", "ע": "ع", "פ": "ف", "ף": "ف", "צ": "ص", "ץ": "ص", "ק": "ق",
         "ר": "ر", "ש": "ش", "ת": "ت"}
HE2AR_GERESH = {"ג": "ج", "ח": "خ", "כ": "خ", "ד": "ذ", "ת": "ث", "צ": "ض", "ץ": "ض",
                "ט": "ظ", "ע": "غ", "ר": "غ", "ז": "ج"}


def arabic_to_hebrew(tok):
    out = "".join(AR2HE.get(c, "") for c in tok)
    stem = out.rstrip("'")
    if stem and stem[-1] in FINAL_HE:
        out = stem[:-1] + FINAL_HE[stem[-1]] + out[len(stem):]
    return out


def hebrew_to_arabic(tok):
    out, n, i = [], len(tok), 0
    while i < n:
        ch, nxt = tok[i], tok[i + 1] if i + 1 < n else ""
        if nxt and nxt in APOS and ch in HE2AR_GERESH:
            out.append(HE2AR_GERESH[ch])
            i += 2
            continue
        if ch == "ה" and i == n - 1 and i > 0:
            out.append("ة" if tok[i - 1] not in "או" else "ه")
        elif ch == nxt and ch in "וי":
            out.append(HE2AR[ch])
            i += 1
        else:
            out.append(HE2AR.get(ch, ""))
        i += 1
    return "".join(out)
