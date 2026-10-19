import unittest

from namematch.matching import score_names
from namematch.variants import name_variants

# (entrée, 1re variante anglaise attendue, arabe attendu)
EXPECTED = [
    ("מוחמד עדוי", "Mohammad Adawi", "محمد عدوي"),
    ("محمد عدوي", "Mohammad Adawi", "محمد عدوي"),
    ("Mohammad Adawi", "Mohammad Adawi", "محمد عدوي"),
    ("ג'בארין", "Jabarin", "جبارين"),
    ("מסארוה", "Masarwa", "مصاروة"),
]

# noms hors lexique : la translittération par règles doit donner ceci en premier
RULES = [("עדאווי", "Adawi"), ("ג'אבר", "Jaber"), ("מחאג'נה", "Mahajna"), ("חמדאן", "Hamdan"),
         ("זיאד", "Ziad"), ("סעיד", "Saeed"), ("דראושה", "Darawsha"), ("מרואן", "Marwan")]

SAMPLES = [
    "מוחמד עדוי", "עדוי חוסיין אבו ג'אבר", "אחמד אלעדוי", "עבד אלרחמן מסארוה", "זיאד אגבאריה",
    "محمد عدوي", "الخطيب يوسف", "ابراهيم مصاروة", "Mohammad Adawi", "Nizar Shalaby",
    "David Cohen", "Yossi Ben David", "Khaled Mahajna", "סאמי טאהא", "ראאד מחאמיד",
    "נאדר חדאד", "عمر الزعبي", "Fadi Bishara", "ח'אלד ג'בארין", "מאהר קעדאן",
]


class TestVariants(unittest.TestCase):
    def test_expected_first_variant(self):
        for raw, latin, arabic in EXPECTED:
            r = name_variants(raw)
            self.assertEqual(r["latin"][0], latin, raw)
            self.assertEqual(r["arabic"][0], arabic, raw)

    def test_three_latin_variants(self):
        for raw in SAMPLES:
            self.assertEqual(len(name_variants(raw, n=3)["latin"]), 3, raw)

    def test_rules(self):
        from namematch.translit.to_latin import hebrew_to_latin
        for he, latin in RULES:
            self.assertEqual(hebrew_to_latin(he)[0], latin, he)

    def test_every_variant_matches_source(self):
        """Toute variante générée (latin, arabe, hébreu) doit matcher le nom d'origine."""
        for raw in SAMPLES:
            r = name_variants(raw, n=5)
            for form in r["latin"] + r["arabic"] + r["hebrew"]:
                s, _ = score_names(raw, form)
                self.assertGreaterEqual(s, 80, f"{raw!r} vs {form!r} = {s}")


class TestScore(unittest.TestCase):
    def test_cross_script(self):
        for a, b in [("Mohammed Elbaz", "מוחמד אלבז"), ("Mohammad Adawi", "מוחמד עדוי"),
                     ("محمد عدوي", "מוחמד עדוי"), ("Agbaria Ziad", "زياد اغبارية"),
                     ("Avraham Cohen", "אברהם כהן"), ("Khatib Yousef", "יוסף אל-ח'טיב")]:
            self.assertGreaterEqual(score_names(a, b)[0], 85, (a, b))

    def test_different_names(self):
        for a, b in [("Mohammad Adawi", "Ahmad Jabarin"), ("David Cohen", "Omar Khatib")]:
            self.assertLess(score_names(a, b)[0], 60, (a, b))


if __name__ == "__main__":
    unittest.main()
