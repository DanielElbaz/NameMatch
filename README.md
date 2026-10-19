# NameMatch

Rapprochement et translittération de noms **hébreu ↔ arabe ↔ anglais**. Tout tourne en local :
pas d'API ni de dépendance obligatoire (Python 3.8+).

Un nom saisi en hébreu, en arabe ou en anglais donne N orthographes anglaises (3 par défaut),
la transcription arabe et la transcription hébraïque.

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
- **Corriger (✎)** : si une transcription est fausse, clique sur ✎, tape la bonne orthographe et
  valide avec Entrée. La correction est enregistrée et passe en tête la fois suivante (voir plus bas).
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
| Corriger une transcription | `correct` / `fix` | `corriger` | `תקן` / `תיקון` | `صحح` / `تصحيح` |
| Interface web | `ui` | `interface` | `ממשק` | `واجهة` |

```bash
python -m namematch וריאציות "NOM"                # 3 variantes anglaises + arabe + hébreu
python -m namematch variants "NOM" -n 5 -d          # 5 variantes + détail mot par mot
python -m namematch variants "NOM" -o noms.csv      # .csv = noms en colonne A
python -m namematch تقييم "NOM 1" "NOM 2"           # score de 0 à 100
python -m namematch רשימה noms.txt -o variantes.csv --scripts en,ar
python -m namematch compare a.csv b.csv --col-a nom --col-b name --threshold 75 -o out.csv
python -m namematch תקן "NOM EN HÉBREU" "BONNE ORTHOGRAPHE"   # anglais, arabe ou hébreu
```

Les options ont aussi des alias : `-n` = `--מספר` = `--عدد`, `-o` = `--פלט` = `--ملف`,
`--threshold` = `--סף` = `--عتبة`.

## Fonctionnement

1. **Lexique** : environ 390 prénoms et noms courants, écrits en latin, en arabe et en hébreu, répartis
   dans trois fichiers du dossier `namematch/data/` :

   | Fichier | Contenu | Priorité |
   |---|---|---|
   | `user_lexicon.txt` | tes corrections (créé par ✎ ou par la commande `correct`) | la plus haute |
   | `lexicon.txt` | noms d'origine arabe | |
   | `lexicon_he.txt` | noms d'origine hébraïque / juive | |

   Les 3 premières orthographes latines sont proposées en premier. Pour ajouter un nom à la main,
   ajoute une ligne (la colonne arabe peut rester vide, elle est alors générée) :
   ```
   identifiant | variantes latines | variantes arabes | variantes hébraïques
   ```
   Les deux lexiques de base ont été rédigés de mémoire, pas tirés d'une base officielle : ils sont à
   vérifier et à compléter.

2. **Origine du nom** : un nom écrit en hébreu ne se lit pas de la même façon selon qu'il est d'origine
   hébraïque ou arabe (ו = v ou ou, ב = v ou b, -אל = el ou al…). L'outil devine l'origine à partir
   d'indices dans le mot (geresh, terminaisons typiques, א au milieu du mot…) et des autres mots du nom
   (un prénom connu comme hébreu rend le nom de famille probablement hébreu, et inversement). S'il ne
   peut pas trancher, il propose les deux lectures.

3. **Règles de translittération** pour les noms absents du lexique. Le mot hébreu ou arabe est découpé en
   unités phonétiques (consonnes, alef, ayin, vav, yod, ה final…). On en déduit les orthographes anglaises
   les plus probables, avec deux jeux de conventions :
   - noms arabes : nisba **-awi**, schème **CaaCiC**, terminaison **-a / -eh**, geresh (ח' = kh, ג' = j,
     ע' = gh), article **Al-** ;
   - noms hébreux : ו et ב lus « v », כ = kh, פ = f, צ = tz, terminaison **-el**, **-vitz**.

   Pour un nom d'origine hébraïque, l'arabe est écrit d'après la prononciation, avec les voyelles.
   Une variante n'est gardée que si elle matche le nom d'origine (score ≥ 80).
4. **Score** : chaque mot est réduit à un squelette consonantique qui ne dépend pas de l'écriture
   (clé fine et clé souple). Les mots sont appariés quel que soit leur ordre, et les particules
   (article, « fils de »…) sont ignorées.

## Structure

```
namematch/
  scripts.py          détection d'écriture, normalisation, découpage
  lexicon.py          chargement des lexiques, recherche, enregistrement des corrections
  data/lexicon.txt    noms d'origine arabe
  data/lexicon_he.txt noms d'origine hébraïque
  data/user_lexicon.txt  tes corrections (créé automatiquement)
  phonetic.py         squelettes consonantiques (clés de comparaison)
  matching.py         score entre deux noms
  translit/
    units.py          hébreu / arabe -> unités phonétiques
    to_latin.py       unités -> orthographes anglaises classées
    from_latin.py     latin -> arabe / hébreu
    cross.py          arabe <-> hébreu lettre à lettre
    latin_spelling.py variantes d'un nom déjà en latin
    origin.py         devine si un mot hébreu est d'origine hébraïque ou arabe
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
