"""Commandes et messages en français, anglais, hébreu et arabe."""
import os

LANGS = ("fr", "en", "he", "ar")

# commande -> {langue: [alias, ...]} ; le premier alias anglais est le nom officiel
COMMANDS = {
    "variants": {"en": ["variants", "v"], "fr": ["variantes"],
                 "he": ["וריאציות", "גרסאות", "תעתיק"], "ar": ["متغيرات", "تهجئات", "ترجمة"]},
    "score": {"en": ["score", "s"], "fr": ["note"],
              "he": ["ציון", "התאמה"], "ar": ["تقييم", "تطابق"]},
    "compare": {"en": ["compare", "c"], "fr": ["comparer"],
                "he": ["השווה", "השוואה"], "ar": ["قارن", "مقارنة"]},
    "csv": {"en": ["csv"], "fr": ["liste"], "he": ["רשימה", "טבלה"], "ar": ["قائمة", "جدول"]},
    "ui": {"en": ["ui", "web"], "fr": ["interface"], "he": ["ממשק"], "ar": ["واجهة"]},
}

# option -> alias supplémentaires (hébreu, arabe, français)
OPTIONS = {
    "--count": ["-n", "--nombre", "--מספר", "--عدد"],
    "--out": ["-o", "--sortie", "--פלט", "--ملف"],
    "--threshold": ["--seuil", "--סף", "--عتبة"],
    "--lang": ["--langue", "--שפה", "--لغة"],
    "--port": ["--פורט", "--منفذ"],
}

MESSAGES = {
    "lexicon": {"fr": "lexique", "en": "lexicon", "he": "מילון", "ar": "قاموس"},
    "rules": {"fr": "règles", "en": "rules", "he": "כללים", "ar": "قواعد"},
    "english": {"fr": "Anglais", "en": "English", "he": "אנגלית", "ar": "الإنجليزية"},
    "arabic": {"fr": "Arabe", "en": "Arabic", "he": "ערבית", "ar": "العربية"},
    "hebrew": {"fr": "Hébreu", "en": "Hebrew", "he": "עברית", "ar": "العبرية"},
    "full_name": {"fr": "Nom complet", "en": "Full name", "he": "שם מלא", "ar": "الاسم الكامل"},
    "score": {"fr": "Score", "en": "Score", "he": "ציון", "ar": "الدرجة"},
    "written": {"fr": "écrit dans", "en": "written to", "he": "נשמר בקובץ", "ar": "تم الحفظ في"},
    "matches": {"fr": "rapprochement(s)", "en": "match(es)", "he": "התאמות", "ar": "تطابقات"},
    "others": {"fr": "autres, voir le CSV", "en": "more, see the CSV",
               "he": "נוספים, ראו את הקובץ", "ar": "أخرى، راجع الملف"},
    "empty_file": {"fr": "fichier vide", "en": "empty file", "he": "קובץ ריק", "ar": "ملف فارغ"},
    "no_column": {"fr": "Colonne introuvable", "en": "Column not found",
                  "he": "העמודה לא נמצאה", "ar": "العمود غير موجود"},
    "names": {"fr": "noms", "en": "names", "he": "שמות", "ar": "أسماء"},
    "ui_running": {"fr": "Interface ouverte sur", "en": "UI running at",
                   "he": "הממשק פועל בכתובת", "ar": "الواجهة تعمل على"},
    "stop": {"fr": "Ctrl+C pour arrêter", "en": "Ctrl+C to stop",
             "he": "Ctrl+C לעצירה", "ar": "Ctrl+C للإيقاف"},
}


def command_lang(alias):
    """Langue déduite de l'alias tapé (ex. 'וריאציות' -> 'he')."""
    for langs in COMMANDS.values():
        for lang, aliases in langs.items():
            if alias in aliases:
                return lang
    return None


def resolve_lang(explicit, alias):
    if explicit in LANGS:
        return explicit
    env = os.environ.get("NAMEMATCH_LANG")
    if env in LANGS:
        return env
    return command_lang(alias) or "fr"


def t(key, lang):
    return MESSAGES[key].get(lang) or MESSAGES[key]["en"]
