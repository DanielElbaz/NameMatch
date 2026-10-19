"""Ligne de commande. Les commandes existent en anglais, français, hébreu et arabe :

  python -m namematch variants "מוחמד עדוי"        (= וריאציות / متغيرات / variantes)
  python -m namematch score "Mohammad Adawi" "محمد عدوي"   (= ציון / تقييم)
  python -m namematch compare a.csv b.csv -o out.csv       (= השווה / قارن)
  python -m namematch csv noms.txt -o sortie.csv            (= רשימה / قائمة)
  python -m namematch ui                                     (= ממשק / واجهة)
"""
import argparse
import sys

from . import csv_tools
from .i18n import COMMANDS, OPTIONS, resolve_lang, t
from .matching import Name, score_names
from .variants import correct_name, name_variants

SCRIPT_KEYS = {"en": "latin", "ar": "arabic", "he": "hebrew"}


def _add(parser, flag, **kw):
    parser.add_argument(flag, *OPTIONS.get(flag, []), **kw)


def generated_names(raw, count, scripts):
    """Liste plate des noms générés pour un nom (anglais puis arabe puis hébreu)."""
    r = name_variants(raw, n=count)
    return [x for s in scripts for x in r[SCRIPT_KEYS[s]]]


def cmd_variants(args, lang):
    r = name_variants(args.name, n=args.count)
    lines = []
    if args.details:
        for tok in r["tokens"]:
            lines.append(f"\n== {tok['text']}  [{t(tok['source'], lang)}]")
            lines.append(f"  {t('english', lang)} : " + ", ".join(tok["latin"][:8]))
            lines.append(f"  {t('arabic', lang)} : " + ", ".join(tok["arabic"][:4]))
            lines.append(f"  {t('hebrew', lang)} : " + ", ".join(tok["hebrew"][:4]))
        lines.append("")
    lines.append(f"{t('english', lang)} :")
    lines += [f"  {x}" for x in r["latin"]]
    lines.append(f"{t('arabic', lang)} :")
    lines += [f"  {x}" for x in r["arabic"]]
    lines.append(f"{t('hebrew', lang)} :")
    lines += [f"  {x}" for x in r["hebrew"]]
    print("\n".join(lines))
    if args.out:
        names = r["latin"] + r["arabic"] + r["hebrew"]
        if args.out.lower().endswith(".csv"):
            csv_tools.write_column_a(args.out, names)
        else:
            with open(args.out, "w", encoding="utf-8") as f:
                f.write("\n".join(names) + "\n")
        print(f"\n-> {t('written', lang)} {args.out}")


def cmd_score(args, lang):
    a, b = Name(args.a), Name(args.b)
    s, det = score_names(a, b)
    print(f"{t('score', lang)} : {s}/100")
    for ta, tb, ts in det:
        print(f"  {ta}  <->  {tb}   {round(ts * 100, 1)}")


def _load_for_compare(path, col, lang):
    rows = csv_tools.read_rows(path)
    if not rows:
        sys.exit(f"{path} : {t('empty_file', lang)}")
    cols = list(rows[0].keys())
    found = csv_tools.guess_column(cols, col)
    if found is None:
        sys.exit(f"{t('no_column', lang)} '{col}' ({path}) : {cols}")
    return rows, found


def cmd_compare(args, lang):
    rows_a, ca = _load_for_compare(args.file_a, args.col_a, lang)
    rows_b, cb = _load_for_compare(args.file_b, args.col_b, lang)
    out = csv_tools.compare_lists(rows_a, ca, rows_b, cb, args.threshold, args.top,
                                  blocking=not args.no_blocking)
    if args.out:
        csv_tools.write_rows(args.out, out, ["ligne_A", "nom_A", "ligne_B", "nom_B", "score", "détail"])
        print(f"{len(out)} {t('matches', lang)} >= {args.threshold} -> {args.out}")
    for r in out[:25]:
        print(f"{r['score']:>5}  {r['nom_A']}  <->  {r['nom_B']}")
    if len(out) > 25:
        print(f"... ({len(out) - 25} {t('others', lang)})")


def cmd_csv(args, lang):
    scripts = [s.strip() for s in args.scripts.split(",") if s.strip() in SCRIPT_KEYS]
    names = []
    for raw in csv_tools.read_name_list(args.file):
        names += generated_names(raw, args.count, scripts)
    out = args.out or "namematch_noms.csv"
    csv_tools.write_column_a(out, names)
    print(f"{len(names)} {t('names', lang)} -> {out}")


def cmd_correct(args, lang):
    try:
        saved = correct_name(args.source, args.value)
    except ValueError:
        sys.exit(t("word_count", lang))
    if not saved:
        print(t("nothing", lang))
    for tok, word in saved:
        print(f"{t('saved', lang)} : {tok} -> {word}")


def cmd_ui(args, lang):
    from .web.server import serve
    serve(port=args.port, open_browser=not args.no_browser, lang=lang)


def build_parser():
    p = argparse.ArgumentParser(prog="namematch",
                                description="NameMatch - noms hébreu / arabe / anglais (100% local)")
    sub = p.add_subparsers(dest="cmd", required=True, metavar="commande")

    def add_cmd(name, fn, help_):
        langs = COMMANDS[name]
        aliases = [a for l in ("en", "fr", "he", "ar") for a in langs[l]][1:]
        sp = sub.add_parser(langs["en"][0], aliases=aliases, help=help_)
        _add(sp, "--lang", choices=("fr", "en", "he", "ar"), help="langue des messages")
        sp.set_defaults(fn=fn)
        return sp

    v = add_cmd("variants", cmd_variants, "variantes d'un nom (N en anglais + arabe + hébreu)")
    v.add_argument("name")
    _add(v, "--count", type=int, default=3, help="nombre de variantes anglaises (défaut 3)")
    _add(v, "--out", help="fichier de sortie (.csv = noms en colonne A, sinon texte)")
    v.add_argument("--details", "-d", "--פירוט", "--تفاصيل", action="store_true",
                   help="détail token par token")

    s = add_cmd("score", cmd_score, "score de similarité entre deux noms")
    s.add_argument("a")
    s.add_argument("b")

    c = add_cmd("compare", cmd_compare, "rapprocher deux listes CSV")
    c.add_argument("file_a")
    c.add_argument("file_b")
    c.add_argument("--col-a")
    c.add_argument("--col-b")
    _add(c, "--threshold", type=float, default=75.0)
    c.add_argument("--top", type=int, default=3, help="meilleurs candidats par ligne de A")
    c.add_argument("--no-blocking", action="store_true", help="compare toutes les paires (lent)")
    _add(c, "--out")

    b = add_cmd("csv", cmd_csv, "liste de noms (.txt/.csv) -> CSV avec toutes les variantes en colonne A")
    b.add_argument("file")
    _add(b, "--count", type=int, default=3)
    _add(b, "--out")
    b.add_argument("--scripts", default="en,ar,he", help="écritures à inclure : en,ar,he")

    k = add_cmd("correct", cmd_correct,
                "corriger une transcription (enregistrée dans data/user_lexicon.txt)")
    k.add_argument("source", help="le nom tel qu'il est écrit (ex. en hébreu)")
    k.add_argument("value", help="la bonne orthographe (anglais, arabe ou hébreu)")

    u = add_cmd("ui", cmd_ui, "interface web locale")
    _add(u, "--port", type=int, default=8765)
    u.add_argument("--no-browser", action="store_true")
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    lang = resolve_lang(args.lang, args.cmd)
    args.fn(args, lang)


if __name__ == "__main__":
    main()
