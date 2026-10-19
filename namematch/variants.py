"""Génération des variantes d'un nom : N orthographes anglaises + arabe + hébreu."""
import itertools

from . import lexicon
from .matching import Name, score_names
from .scripts import prep_light, script_of, split_raw
from .translit.cross import arabic_to_hebrew, hebrew_to_arabic
from .translit.from_latin import latin_to_script
from .translit.latin_spelling import spelling_variants
from .translit.to_latin import arabic_to_latin, hebrew_to_latin

MIN_TOKEN_SCORE = 80      # une variante générée doit matcher l'original au moins à ce score
POOL = 8                  # variantes gardées par token avant combinaison


def dedupe(seq):
    seen, out = set(), []
    for x in seq:
        if x and x not in seen:
            seen.add(x)
            out.append(x)
    return out


def _keep_matching(source, candidates):
    """Filtre les candidats qui matchent bien la forme d'origine (garantie de rapprochement)."""
    ref = Name(source)
    return [c for c in candidates if score_names(ref, Name(c))[0] >= MIN_TOKEN_SCORE]


def _with_article(stem_vars):
    """Ajoute l'article arabe (Al-/ال/אל) aux variantes d'une racine."""
    la = stem_vars["latin"]
    latin = ["Al-" + la[0], "El-" + la[0], la[0]] + ["Al-" + x for x in la[1:]] if la else []
    return {"source": stem_vars["source"], "latin": latin,
            "arabic": ["ال" + x for x in stem_vars["arabic"]],
            "hebrew": ["אל" + x for x in stem_vars["hebrew"]]}


def _from_lexicon(tok, entry_id):
    sc = script_of(tok)
    forms = {s: list(lexicon.entry_forms(entry_id, s)) for s in ("la", "ar", "he")}
    forms[sc] = [tok[:1].upper() + tok[1:] if sc == "la" else tok] + forms[sc]
    rules = None
    for s in ("la", "ar", "he"):           # écriture absente du lexique -> règles
        if not forms[s]:
            rules = rules or _from_rules(tok)
            forms[s] = rules[{"la": "latin", "ar": "arabic", "he": "hebrew"}[s]]
    return {"source": "lexicon", "latin": dedupe(forms["la"]),
            "arabic": dedupe(forms["ar"]), "hebrew": dedupe(forms["he"])}


def _from_rules(tok):
    sc = script_of(tok)
    if sc == "he":
        latin = hebrew_to_latin(tok, limit=POOL * 2)
        arabic, hebrew = [hebrew_to_arabic(tok)], [tok]
    elif sc == "ar":
        latin = arabic_to_latin(tok, limit=POOL * 2)
        arabic, hebrew = [tok], [arabic_to_hebrew(tok)]
    else:
        arabic = latin_to_script(tok, "ar")
        hebrew = latin_to_script(tok, "he")
        first = tok[:1].upper() + tok[1:]
        latin = [first] + arabic_to_latin(arabic[0], limit=POOL) + spelling_variants(tok)
    latin = dedupe(latin[:1] + _keep_matching(tok, latin[1:]))
    arabic = dedupe(arabic[:1] + _keep_matching(tok, arabic[1:]))
    hebrew = dedupe(hebrew[:1] + _keep_matching(tok, hebrew[1:]))
    return {"source": "rules", "latin": latin[:POOL], "arabic": arabic, "hebrew": hebrew}


def token_variants(tok):
    """dict : source ('lexicon' | 'rules'), latin, arabic, hebrew (listes classées)."""
    ids = lexicon.lookup(tok)
    if ids:
        return _from_lexicon(tok, ids[0])
    sc = script_of(tok)
    if (sc == "ar" and tok.startswith("ال") and len(tok) > 4) or \
       (sc == "he" and tok.startswith("אל") and len(tok) >= 5):
        stem = tok[2:]
        if sc == "ar" or lexicon.lookup(stem) or len(tok) >= 6:
            return _with_article(token_variants(stem))
    return _from_rules(tok)


def _group_tokens(raw):
    """Découpe le nom en tokens en recollant les expressions du lexique (Abdel Rahman)."""
    toks = split_raw(prep_light(raw))
    out, i = [], 0
    while i < len(toks):
        entry_id, n = lexicon.lookup_phrase(toks, i)
        if entry_id:
            out.append((" ".join(toks[i:i + n]), entry_id))
        else:
            out.append((toks[i], None))
        i += n
    return out


def _combine(lists, weights, n):
    """Meilleures combinaisons de variantes : on fait varier d'abord le premier token."""
    lists = [lst[:POOL] or [""] for lst in lists]
    combos = []
    for idx in itertools.product(*(range(len(lst)) for lst in lists)):
        cost = sum(i * w for i, w in zip(idx, weights))
        combos.append((cost, tuple(reversed(idx)), " ".join(lst[i] for lst, i in zip(lists, idx))))
        if len(combos) > 20000:
            break
    combos.sort()
    return dedupe(c[2].strip() for c in combos)[:n]


def name_variants(raw, n=3):
    """Variantes d'un nom complet.

    Retourne {"input", "tokens": [...], "latin": [n noms], "arabic": [...], "hebrew": [...]}.
    """
    tokens = []
    for text, entry_id in _group_tokens(raw):
        v = _from_lexicon(text, entry_id) if entry_id else token_variants(text)
        v["text"] = text
        v["particle"] = lexicon.is_particle(text)
        tokens.append(v)
    # le prénom varie en premier (Mohammad / Mohammed / Muhammad), le nom de famille ensuite
    weights = [5 if t["particle"] else (1 if i == 0 else 2.5) for i, t in enumerate(tokens)]
    return {
        "input": raw,
        "tokens": tokens,
        "latin": _combine([t["latin"] for t in tokens], weights, n),
        "arabic": _combine([t["arabic"] for t in tokens], weights, max(1, min(n, 2))),
        "hebrew": _combine([t["hebrew"] for t in tokens], weights, max(1, min(n, 2))),
    }
