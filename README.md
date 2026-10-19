# NameMatch

Rapprochement et translittération de noms **hébreu ↔ arabe ↔ anglais**. Tout tourne en local :
pas d'API ni de dépendance obligatoire (Python 3.8+).

```
מוחמד עדוי  →  Mohammad Adawi · Mohammed Adawi · Muhammad Adawi
               محمد عدوي
               מוחמד עדוי
```

## Interface (recommandé)

```bash
python -m namematch ui          # ou : ממשק / واجهة / interface
```

Sous Windows, double-clique sur `lancer_interface.bat`. Sous macOS, double-clique sur `lancer_interface.command`.
Le navigateur s'ouvre sur `http://127.0.0.1:8765`.

- **Générer** : tape un nom en hébreu, en arabe ou en anglais pour obtenir N variantes anglaises,
  l'arabe et l'hébreu. Chaque nom a son bouton *Copier*.
- **Liste de noms** : colle une liste, ou charge un `.txt` / `.csv`. Tu obtiens toutes les variantes
  et le bouton **Télécharger le CSV** met tous les noms les uns sous les autres dans la colonne A.
- **Ma liste CSV** (panneau de droite) : ajoute des noms un par un avec *+ Liste*, puis télécharge le CSV.
- **Score** et **Comparer deux listes** : calculent la similarité entre deux noms ou deux listes.
- L'interface existe en français, anglais, hébreu et arabe, avec l'affichage de droite à gauche pour l'hébreu et l'arabe.

Les CSV sont en UTF-8 avec BOM, donc Excel affiche correctement l'hébreu et l'arabe.

## Ligne de commande

Chaque commande s'écrit en anglais, en français, en hébreu ou en arabe. La langue des messages suit celle
de la commande tapée. Pour la forcer, utilise `--lang fr|en|he|ar` ou la variable `NAMEMATCH_LANG`.

| Action | Anglais | Français | Hébreu | Arabe |
|---|---|---|---|---|
| Variantes d'un nom | `variants` / `v` | `variantes` | `וריאציות` / `תעתיק` | `متغيرات` / `ترجمة` |
| Score entre 2 noms | `score` / `s` | `note` | `ציון` / `התאמה` | `تقييم` / `تطابق` |
| Rapprocher 2 CSV | `compare` / `c` | `comparer` | `השווה` | `قارن` / `مقارنة` |
| Liste → CSV colonne A | `csv` | `liste` | `רשימה` | `قائمة` |
| Interface web | `ui` | `interface` | `ממשק` | `واجهة` |

```bash
python -m namematch וריאציות "מוחמד עדוי"                 # 3 variantes anglaises + arabe + hébreu
python -m namematch variants "محمد عدوي" -n 5 -d            # 5 variantes + détail mot par mot
python -m namematch variants "Mohammad Adawi" -o noms.csv   # .csv = noms en colonne A
python -m namematch تقييم "Mohammad Adawi" "מוחמד עדוי"     # -> 100/100
python -m namematch רשימה noms.txt -o variantes.csv --scripts en,ar
python -m namematch compare a.csv b.csv --col-a nom --col-b name --threshold 75 -o out.csv
```

Les options ont aussi des alias : `-n` = `--מספר` = `--عدد`, `-o` = `--פלט` = `--ملف`,
`--threshold` = `--סף` = `--عتبة`.

## Fonctionnement

1. **Lexique** (`namematch/data/lexicon.txt`) : environ 150 prénoms et noms courants (arabes et hébreux),
   écrits en latin, en arabe et en hébreu. Les 3 premières orthographes latines sont celles qui sont
   proposées en premier. **Pour corriger ou ajouter un nom, il suffit d'ajouter une ligne :**
   ```
   adawi | Adawi, Adwi, Adawy | عدوي, العدوي | עדוי, עדווי, עדאווי
   ```
2. **Règles de translittération** pour les noms absents du lexique. Le mot hébreu ou arabe est découpé en
   unités phonétiques (consonnes, alef, ayin, vav, yod, ה final…). On en déduit les orthographes anglaises
   les plus probables, avec plusieurs conventions :
   - la nisba **-awi** : עדוי → Adawi ;
   - le schème **CaaCiC** : ג'אבר → Jaber ;
   - la terminaison **-a / -eh** : מסארוה → Masarwa ;
   - le geresh : ח' = kh, ג' = j, ע' = gh ;
   - l'article **Al-**.

   Une variante n'est gardée que si elle matche le nom d'origine (score ≥ 80).
3. **Score** : chaque mot est réduit à un squelette consonantique qui ne dépend pas de l'écriture
   (clé fine et clé souple). Les mots sont appariés quel que soit leur ordre, et les particules
   (Abu, Bin, Al…) sont ignorées.

## Structure

```
namematch/
  scripts.py          détection d'écriture, normalisation, découpage
  lexicon.py          chargement du lexique + recherche
  data/lexicon.txt    le lexique (à enrichir)
  phonetic.py         squelettes consonantiques (clés de comparaison)
  matching.py         score entre deux noms
  translit/
    units.py          hébreu / arabe -> unités phonétiques
    to_latin.py       unités -> orthographes anglaises classées
    from_latin.py     latin -> arabe / hébreu
    cross.py          arabe <-> hébreu lettre à lettre
    latin_spelling.py variantes d'un nom déjà en latin
  variants.py         variantes d'un nom complet (N anglais + arabe + hébreu)
  csv_tools.py        lecture/écriture CSV, rapprochement de listes
  i18n.py             commandes et messages fr / en / he / ar
  cli.py              ligne de commande
  web/                serveur local + interface (HTML/CSS/JS)
tests/                python -m unittest
```

## Tests

```bash
python -m unittest -v
```
