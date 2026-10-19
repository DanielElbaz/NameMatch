"""Génération des variantes d'un nom : N orthographes anglaises + arabe + hébreu."""
import itertools

from . import lexicon
from .matching import Name, score_names
from .scripts import prep_light, script_of, split_raw
from .translit.cross import arabic_to_hebrew, hebrew_to_arabic
from .translit.from_latin import latin_to_script
from .translit.latin_spelling import spelling_variants
from .translit.origin import decide_style, origin_hint
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


def _interleave(*lists):
    return dedupe(x for group in itertools.zip_longest(*lists) for x in group if x)


def _arabic_from_latin(latin_name):
    """Arabe d'un nom d'origine hébraïque, écrit d'après sa prononciation (Levin -> ليفين)."""
    words = latin_name.replace("-", " ").split()
    return " ".join(latin_to_script(w, "ar", 1, style="he")[0] for w in words)


def _from_lexicon(tok, entry_id, style=None):
    sc = script_of(tok)
    forms = {s: list(lexicon.entry_forms(entry_id, s)) for s in ("la", "ar", "he")}
    forms[sc] = [tok[:1].upper() + tok[1:] if sc == "la" else tok] + forms[sc]
    if not forms["ar"] and forms["la"] and lexicon.origin_of(entry_id) == "he":
        forms["ar"] = [_arabic_from_latin(forms["la"][0])]
    rules = None
    for s in ("la", "ar", "he"):           # écriture absente du lexique -> règles
        if not forms[s]:
            rules = rules or _from_rules(tok, style)
            forms[s] = rules[{"la": "latin", "ar": "arabic", "he": "hebrew"}[s]]
    return {"source": "lexicon", "latin": dedupe(forms["la"]),
            "arabic": dedupe(forms["ar"]), "hebrew": dedupe(forms["he"])}


def _from_rules(tok, style=None):
    """style : 'he' (nom hébreu), 'ar' (nom arabe) ou None (indécis : les deux lectures)."""
    sc = script_of(tok)
    if sc == "he":
        if style:
            latin = hebrew_to_latin(tok, limit=POOL * 2, style=style)
        else:
            latin = _interleave(hebrew_to_latin(tok, POOL, "he"), hebrew_to_latin(tok, POOL, "ar"))
        arabic, hebrew = [hebrew_to_arabic(tok)], [tok]
        if style == "he" and latin:
            arabic = [_arabic_from_latin(latin[0])] + arabic
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


def token_variants(tok, style=None):
    """dict : source ('lexicon' | 'rules'), latin, arabic, hebrew (listes classées).

    style ('he' / 'ar' / None) : origine supposée du nom, déduite du contexte.
    """
    ids = lexicon.lookup(tok, prefer=style)
    if ids:
        return _from_lexicon(tok, ids[0], style)
    sc = script_of(tok)
    if style != "he" and ((sc == "ar" and tok.startswith("ال") and len(tok) > 4) or
                          (sc == "he" and tok.startswith("אל") and len(tok) >= 5)):
        stem = tok[2:]
        if sc == "ar" or lexicon.lookup(stem) or (len(tok) >= 6 and style == "ar"):
            return _with_article(token_variants(stem, "ar"))
    return _from_rules(tok, style)


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


def _lexicon_origin(text, entry_id=None):
    """+2 si le mot est un nom hébreu connu, -2 s'il est arabe, 0 sinon (ou ambigu)."""
    ids = [entry_id] if entry_id else lexicon.lookup(text)
    origins = {lexicon.origin_of(i) for i in ids if not lexicon.BY_ID[i].particle
               or lexicon.BY_ID[i].source != "user"}
    origins.discard(None)
    if len(origins) != 1:
        return 0
    return 2 if origins == {"he"} else -2


def _token_signal(text, entry_id):
    """Indice d'origine apporté par un mot aux autres mots du nom."""
    lex = _lexicon_origin(text, entry_id)
    if lex:
        return lex
    if script_of(text) == "he":
        h = origin_hint(text)
        return (h > 0) - (h < 0)
    return 0


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
    groups = _group_tokens(raw)
    signals = [_token_signal(text, entry_id) for text, entry_id in groups]
    tokens = []
    for i, (text, entry_id) in enumerate(groups):
        context = sum(signals) - signals[i]          # ce que disent les autres mots du nom
        if script_of(text) == "he":
            style = decide_style(text, context)
        else:
            style = "he" if context > 0 else "ar" if context < 0 else None
        v = _from_lexicon(text, entry_id, style) if entry_id else token_variants(text, style)
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


def correct_name(source, value):
    """Enregistre une correction : 'source' (nom saisi) s'écrit 'value' dans l'écriture de value.

    Les mots sont associés un à un ; seuls ceux qui changent sont enregistrés.
    Retourne la liste des (mot d'origine, correction) enregistrés.
    """
    words = value.split()
    raw_toks = split_raw(prep_light(source))
    groups = [text for text, _ in _group_tokens(source)]
    if len(raw_toks) == len(words):
        pairs = list(zip(raw_toks, words))
    elif len(groups) == len(words):
        pairs = list(zip(groups, words))
    elif len(groups) == 1:
        pairs = [(groups[0], value.strip())]
    else:
        raise ValueError(f"{len(raw_toks)} != {len(words)}")
    field = {"la": "latin", "ar": "arabic", "he": "hebrew"}[script_of(value)]
    saved = []
    for tok, word in pairs:
        current = token_variants(tok)[field]
        if current and current[0] == word:
            continue
        lexicon.add_correction(tok, word)
        saved.append((tok, word))
    return saved
