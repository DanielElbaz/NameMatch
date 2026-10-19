"""Devine si un mot écrit en hébreu est un nom d'origine hébraïque ou arabe.

Score > 0 : plutôt hébreu ; < 0 : plutôt arabe ; 0 : aucun indice.
"""
from ..scripts import APOS

HEBREW_ENDINGS = (("וביץ", 3), ("ביץ", 2), ("סקי", 3), ("מן", 1), ("אל", 2))
ARABIC_ENDINGS = (("אווי", 3), ("אוי", 3), ("ווי", 2), ("ארין", 1), ("אוה", 2))


def origin_hint(tok):
    tok = tok.strip()
    if len(tok) < 2:
        return 0
    score = 0
    if any(c in APOS for c in tok):          # ח' ג' ע' : sons arabes
        score -= 2
    if "צ" in tok or "ץ" in tok:
        score += 1
    if "ע" in tok and "א" in tok:
        score -= 1
    for end, w in HEBREW_ENDINGS:
        if len(tok) > len(end) + 1 and tok.endswith(end):
            score += w
            break
    for end, w in ARABIC_ENDINGS:
        if len(tok) > len(end) and tok.endswith(end):
            score -= w
            break
    # א au milieu du mot pour noter le son "a" (סאמי, ג'אבר) : graphie typique des noms arabes
    core = tok[:-2] if tok.endswith("אל") else tok
    if "א" in core[1:]:
        score -= 1
    if tok.startswith("אל") and len(tok) >= 5 and not tok.endswith("אל"):
        score -= 1
    return score


def decide_style(tok, context=0):
    """'he', 'ar' ou None (indécis) à partir du mot et du contexte (autres mots du nom)."""
    total = origin_hint(tok) + context
    if total > 0:
        return "he"
    if total < 0:
        return "ar"
    return None
