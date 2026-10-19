"""Lecture / écriture CSV et rapprochement de deux listes."""
import csv
import io
from collections import defaultdict

from .matching import Name, score_names

NAME_COLUMNS = ("name", "nom", "full_name", "fullname", "שם", "שם מלא", "الاسم", "اسم")


def _sniff(sample):
    try:
        return csv.Sniffer().sniff(sample, delimiters=",;\t")
    except csv.Error:
        return csv.excel


def read_rows(path):
    """Lignes d'un CSV (dicts) avec détection du séparateur ; BOM Excel accepté."""
    with open(path, newline="", encoding="utf-8-sig") as f:
        text = f.read()
    return list(csv.DictReader(io.StringIO(text), dialect=_sniff(text[:4096])))


def guess_column(cols, wanted=None):
    if wanted:
        return wanted if wanted in cols else None
    guess = [c for c in cols if c and c.strip().lower() in NAME_COLUMNS]
    return guess[0] if guess else cols[0]


def read_name_list(path):
    """Noms d'un fichier .txt (un par ligne) ou de la 1re colonne / colonne 'nom' d'un CSV."""
    with open(path, encoding="utf-8-sig") as f:
        text = f.read()
    if not path.lower().endswith(".csv"):
        return [line.strip() for line in text.splitlines() if line.strip()]
    rows = list(csv.reader(io.StringIO(text), dialect=_sniff(text[:4096])))
    if not rows:
        return []
    header = [c.strip().lower() for c in rows[0]]
    col = next((i for i, c in enumerate(header) if c in NAME_COLUMNS), None)
    body = rows[1:] if col is not None else rows
    col = col or 0
    return [r[col].strip() for r in body if len(r) > col and r[col].strip()]


def column_a_csv(names):
    """Texte CSV : un nom par ligne dans la colonne A (BOM pour qu'Excel lise l'hébreu/arabe)."""
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\r\n")
    for n in names:
        w.writerow([n])
    return "﻿" + buf.getvalue()


def write_column_a(path, names):
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(column_a_csv(names))


def compare_lists(rows_a, col_a, rows_b, col_b, threshold=75.0, top=3, blocking=True):
    """Rapprochements entre deux listes : [{ligne_A, nom_A, ligne_B, nom_B, score, détail}]."""
    names_a = [Name(r[col_a] or "") for r in rows_a]
    names_b = [Name(r[col_b] or "") for r in rows_b]
    block = defaultdict(set)
    for j, nb in enumerate(names_b):
        for ch in nb.first_chars():
            block[ch].add(j)
    out = []
    for i, na in enumerate(names_a):
        if blocking:
            cands = set()
            for ch in na.first_chars():
                cands |= block.get(ch, set())
        else:
            cands = range(len(names_b))
        scored = []
        for j in cands:
            s, det = score_names(na, names_b[j])
            if s >= threshold:
                scored.append((s, j, det))
        scored.sort(key=lambda x: -x[0])
        for s, j, det in scored[:top]:
            out.append({
                "ligne_A": i + 2, "nom_A": rows_a[i][col_a], "ligne_B": j + 2,
                "nom_B": rows_b[j][col_b], "score": s,
                "détail": " | ".join(f"{x}~{y} ({round(z * 100)})" for x, y, z in det),
            })
    out.sort(key=lambda r: -r["score"])
    return out


def write_rows(path, rows, fields):
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
