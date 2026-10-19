"use strict";

// ---------------------------------------------------------------- textes
const I18N = {
  fr: {
    tagline: "Hébreu · Arabe · Anglais — 100 % local", tab_gen: "Générer", tab_batch: "Liste de noms",
    tab_score: "Score", tab_compare: "Comparer deux listes", ph_name: "Tape un nom : מוחמד עדוי, محمد عدوي, Mohammad Adawi…",
    count: "Variantes", generate: "Générer", english: "Anglais", arabic: "Arabe", hebrew: "Hébreu",
    details: "Détail par mot", copy: "Copier", copied: "Copié", copy_all: "Tout copier", add: "+ Liste",
    add_all_list: "Tout ajouter à ma liste", added: "Ajouté à la liste", my_list: "Ma liste CSV",
    list_hint: "Les noms ajoutés seront écrits les uns sous les autres dans la colonne A.",
    download_csv: "Télécharger le CSV", clear: "Vider", batch_hint: "Un nom par ligne (ou charge un fichier .txt / .csv).",
    ph_batch: "מוחמד עדוי\nAhmad Jabarin\nزياد اغبارية", load_file: "Charger un fichier",
    ph_a: "Nom A", ph_b: "Nom B", compute: "Calculer", compare_hint: "Colle deux listes (un nom par ligne) pour trouver les correspondances.",
    ph_list_a: "Liste A", ph_list_b: "Liste B", threshold: "Seuil", compare: "Comparer",
    source: "Nom saisi", variants: "Variantes", lexicon: "lexique", rules: "règles", empty: "Liste vide",
    names: "noms", no_match: "Aucune correspondance au-dessus du seuil.", error: "Erreur",
    fix: "Corriger", save: "Enregistrer", cancel: "Annuler", fixed: "Correction enregistrée", nothing: "Déjà la 1re variante",
  },
  en: {
    tagline: "Hebrew · Arabic · English — 100% local", tab_gen: "Generate", tab_batch: "Name list",
    tab_score: "Score", tab_compare: "Compare two lists", ph_name: "Type a name: מוחמד עדוי, محمد عدوي, Mohammad Adawi…",
    count: "Variants", generate: "Generate", english: "English", arabic: "Arabic", hebrew: "Hebrew",
    details: "Word by word", copy: "Copy", copied: "Copied", copy_all: "Copy all", add: "+ List",
    add_all_list: "Add all to my list", added: "Added to list", my_list: "My CSV list",
    list_hint: "Names you add are written one under another in column A.",
    download_csv: "Download CSV", clear: "Clear", batch_hint: "One name per line (or load a .txt / .csv file).",
    ph_batch: "מוחמד עדוי\nAhmad Jabarin\nزياد اغبارية", load_file: "Load a file",
    ph_a: "Name A", ph_b: "Name B", compute: "Compute", compare_hint: "Paste two lists (one name per line) to find matches.",
    ph_list_a: "List A", ph_list_b: "List B", threshold: "Threshold", compare: "Compare",
    source: "Input name", variants: "Variants", lexicon: "lexicon", rules: "rules", empty: "Empty list",
    names: "names", no_match: "No match above the threshold.", error: "Error",
    fix: "Fix", save: "Save", cancel: "Cancel", fixed: "Correction saved", nothing: "Already the first variant",
  },
  he: {
    tagline: "עברית · ערבית · אנגלית — מקומי לגמרי", tab_gen: "יצירה", tab_batch: "רשימת שמות",
    tab_score: "ציון", tab_compare: "השוואת רשימות", ph_name: "הקלד שם: מוחמד עדוי, محمد عدوي, Mohammad Adawi…",
    count: "גרסאות", generate: "צור", english: "אנגלית", arabic: "ערבית", hebrew: "עברית",
    details: "פירוט לפי מילה", copy: "העתק", copied: "הועתק", copy_all: "העתק הכל", add: "+ רשימה",
    add_all_list: "הוסף הכל לרשימה", added: "נוסף לרשימה", my_list: "רשימת CSV שלי",
    list_hint: "השמות שנוספו ייכתבו אחד מתחת לשני בעמודה A.",
    download_csv: "הורד CSV", clear: "נקה", batch_hint: "שם אחד בכל שורה (או טען קובץ ‎.txt / .csv).",
    ph_batch: "מוחמד עדוי\nAhmad Jabarin\nزياد اغبارية", load_file: "טען קובץ",
    ph_a: "שם א", ph_b: "שם ב", compute: "חשב", compare_hint: "הדבק שתי רשימות (שם בכל שורה) כדי למצוא התאמות.",
    ph_list_a: "רשימה א", ph_list_b: "רשימה ב", threshold: "סף", compare: "השווה",
    source: "השם שהוזן", variants: "גרסאות", lexicon: "מילון", rules: "כללים", empty: "הרשימה ריקה",
    names: "שמות", no_match: "אין התאמות מעל הסף.", error: "שגיאה",
    fix: "תקן", save: "שמור", cancel: "ביטול", fixed: "התיקון נשמר", nothing: "זו כבר הגרסה הראשונה",
  },
  ar: {
    tagline: "العبرية · العربية · الإنجليزية — محلي بالكامل", tab_gen: "توليد", tab_batch: "قائمة أسماء",
    tab_score: "الدرجة", tab_compare: "مقارنة قائمتين", ph_name: "اكتب اسماً: מוחמד עדוי، محمد عدوي، Mohammad Adawi…",
    count: "الصيغ", generate: "توليد", english: "الإنجليزية", arabic: "العربية", hebrew: "العبرية",
    details: "تفصيل كل كلمة", copy: "نسخ", copied: "تم النسخ", copy_all: "نسخ الكل", add: "+ قائمة",
    add_all_list: "إضافة الكل إلى قائمتي", added: "أضيف إلى القائمة", my_list: "قائمة CSV",
    list_hint: "تُكتب الأسماء المضافة واحداً تحت الآخر في العمود A.",
    download_csv: "تنزيل CSV", clear: "مسح", batch_hint: "اسم في كل سطر (أو حمّل ملف ‎.txt / .csv).",
    ph_batch: "מוחמד עדוי\nAhmad Jabarin\nزياد اغبارية", load_file: "تحميل ملف",
    ph_a: "الاسم أ", ph_b: "الاسم ب", compute: "احسب", compare_hint: "الصق قائمتين (اسم في كل سطر) للعثور على التطابقات.",
    ph_list_a: "القائمة أ", ph_list_b: "القائمة ب", threshold: "العتبة", compare: "قارن",
    source: "الاسم المدخل", variants: "الصيغ", lexicon: "قاموس", rules: "قواعد", empty: "القائمة فارغة",
    names: "أسماء", no_match: "لا توجد تطابقات فوق العتبة.", error: "خطأ",
    fix: "تصحيح", save: "حفظ", cancel: "إلغاء", fixed: "تم حفظ التصحيح", nothing: "إنها الصيغة الأولى بالفعل",
  },
};

const $ = (s) => document.querySelector(s);
const store = {
  get(k, d) { try { const v = localStorage.getItem(k); return v === null ? d : JSON.parse(v); } catch { return d; } },
  set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch { /* stockage indisponible */ } },
};
let lang = new URLSearchParams(location.search).get("lang") || store.get("nm-lang", "fr");
if (!I18N[lang]) lang = "fr";
const T = (k) => I18N[lang][k] ?? I18N.en[k] ?? k;

function applyLang(l) {
  lang = I18N[l] ? l : "fr";
  store.set("nm-lang", lang);
  document.documentElement.lang = lang;
  document.documentElement.dir = lang === "he" || lang === "ar" ? "rtl" : "ltr";
  document.querySelectorAll("[data-i18n]").forEach((el) => { el.textContent = T(el.dataset.i18n); });
  document.querySelectorAll("[data-i18n-ph]").forEach((el) => { el.placeholder = T(el.dataset.i18nPh); });
  document.querySelectorAll(".langs button").forEach((b) => b.classList.toggle("on", b.dataset.lang === lang));
  if (lastGen) renderGen(lastGen);
}

// ---------------------------------------------------------------- utilitaires
async function api(path, body) {
  const r = await fetch(path, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
  const data = await r.json();
  if (!r.ok) throw new Error(data.error || r.statusText);
  return data;
}

function toast(msg) {
  const t = $("#toast");
  t.textContent = msg;
  t.classList.add("show");
  clearTimeout(toast.timer);
  toast.timer = setTimeout(() => t.classList.remove("show"), 1400);
}

async function copyText(text) {
  try {
    await navigator.clipboard.writeText(text);
  } catch {
    const ta = document.createElement("textarea");
    ta.value = text;
    document.body.appendChild(ta);
    ta.select();
    document.execCommand("copy");
    ta.remove();
  }
  toast(`${T("copied")} ✓`);
}

function el(tag, attrs = {}, ...children) {
  const e = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (k === "onclick") e.addEventListener("click", v);
    else if (k === "class") e.className = v;
    else e.setAttribute(k, v);
  }
  for (const c of children) e.append(c);
  return e;
}

function csvColumnA(names) {
  const esc = (s) => (/[",\r\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s);
  return "﻿" + names.map(esc).join("\r\n") + "\r\n";
}

function csvTable(rows, fields) {
  const esc = (s) => { s = String(s ?? ""); return /[",\r\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s; };
  return "﻿" + [fields, ...rows.map((r) => fields.map((f) => r[f]))].map((r) => r.map(esc).join(",")).join("\r\n") + "\r\n";
}

function download(filename, text) {
  const url = URL.createObjectURL(new Blob([text], { type: "text/csv;charset=utf-8" }));
  const a = el("a", { href: url, download: filename });
  document.body.appendChild(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

function stamp() {
  return new Date().toISOString().slice(0, 16).replace(/[-:T]/g, "");
}

// ---------------------------------------------------------------- liste (panier)
let basket = store.get("nm-basket", []);

function saveBasket() {
  store.set("nm-basket", basket);
  renderBasket();
}

function addToBasket(names) {
  const before = basket.length;
  for (const n of names) if (n && !basket.includes(n)) basket.push(n);
  saveBasket();
  toast(`${T("added")} (+${basket.length - before})`);
}

function renderBasket() {
  const ol = $("#basket");
  ol.replaceChildren(...basket.map((n, i) => el("li", {},
    el("span", { dir: "auto" }, n),
    el("button", { title: "×", onclick: () => { basket.splice(i, 1); saveBasket(); } }, "×"))));
  $("#basket-count").textContent = basket.length;
}

// ---------------------------------------------------------------- onglet Générer
let lastGen = null;

function nameRow(text, first) {
  const row = el("div", { class: "name" + (first ? " first" : "") },
    el("span", { dir: "auto" }, text),
    el("div", { class: "acts" },
      el("button", { onclick: () => copyText(text) }, T("copy")),
      el("button", { onclick: () => addToBasket([text]) }, T("add")),
      el("button", { class: "fix", title: T("fix"), onclick: () => editRow(row, text) }, "✎")));
  return row;
}

// Corriger : la bonne orthographe est enregistrée (data/user_lexicon.txt) et passe en tête
function editRow(row, text) {
  const input = el("input", { dir: "auto", value: text });
  const save = async () => {
    const value = input.value.trim();
    if (!value || !lastGen) return;
    try {
      const r = await api("/api/correct", { source: lastGen.input, value, count: +$("#gen-count").value || 3 });
      toast(r.saved.length ? `${T("fixed")} ✓` : T("nothing"));
      renderGen(r.result);
    } catch (err) { toast(`${T("error")} : ${err.message}`); }
  };
  input.addEventListener("keydown", (e) => {
    if (e.key === "Enter") save();
    if (e.key === "Escape") renderGen(lastGen);
  });
  row.replaceChildren(input, el("div", { class: "acts" },
    el("button", { class: "primary", onclick: save }, T("save")),
    el("button", { onclick: () => renderGen(lastGen) }, T("cancel"))));
  row.classList.add("editing");
  input.focus();
  input.select();
}

function card(title, names) {
  return el("div", { class: "card" },
    el("div", { class: "card-head" },
      el("h3", {}, title),
      el("div", { class: "acts" },
        el("button", { onclick: () => copyText(names.join("\n")) }, T("copy_all")),
        el("button", { onclick: () => addToBasket(names) }, T("add")))),
    ...names.map((n, i) => nameRow(n, i === 0)));
}

function renderGen(r) {
  lastGen = r;
  $("#gen-out").replaceChildren(
    card(T("english"), r.latin), card(T("arabic"), r.arabic), card(T("hebrew"), r.hebrew));
  $("#gen-details").hidden = false;
  $("#gen-tokens").replaceChildren(...r.tokens.map((t) => el("div", { class: "tok" },
    el("b", { dir: "auto" }, t.text),
    el("span", { class: "tag " + t.source }, T(t.source)),
    el("div", { dir: "auto" }, `${T("english")} : ${t.latin.join(", ")}`),
    el("div", { dir: "auto" }, `${T("arabic")} : ${t.arabic.join("، ")}`),
    el("div", { dir: "auto" }, `${T("hebrew")} : ${t.hebrew.join(", ")}`))));
}

$("#gen-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const name = $("#gen-name").value.trim();
  if (!name) return;
  try {
    renderGen(await api("/api/variants", { name, count: +$("#gen-count").value || 3 }));
  } catch (err) { toast(`${T("error")} : ${err.message}`); }
});

// ---------------------------------------------------------------- onglet Liste
let batchNames = [];

function batchScripts() {
  return [["latin", "#inc-en"], ["arabic", "#inc-ar"], ["hebrew", "#inc-he"]]
    .filter(([, sel]) => $(sel).checked).map(([k]) => k);
}

$("#batch-file").addEventListener("change", async (e) => {
  const f = e.target.files[0];
  if (!f) return;
  let text = await f.text();
  if (f.name.toLowerCase().endsWith(".csv")) {
    text = text.split(/\r?\n/).map((l) => l.split(/[;,\t]/)[0].replace(/^"|"$/g, "")).join("\n");
  }
  $("#batch-input").value = text.replace(/^﻿/, "");
});

$("#batch-run").addEventListener("click", async () => {
  const names = $("#batch-input").value.split(/\r?\n/).map((s) => s.trim()).filter(Boolean);
  if (!names.length) return toast(T("empty"));
  try {
    const { results } = await api("/api/batch", { names, count: +$("#batch-count").value || 3 });
    const scripts = batchScripts();
    batchNames = results.flatMap((r) => scripts.flatMap((s) => r[s]));
    const head = el("tr", {}, el("th", {}, T("source")), ...scripts.map((s) => el("th", {}, T(s === "latin" ? "english" : s))));
    const rows = results.map((r) => el("tr", {},
      el("td", { dir: "auto" }, r.input),
      ...scripts.map((s) => el("td", { class: "names" },
        ...r[s].map((n) => el("span", { dir: "auto", title: T("copy"), onclick: () => copyText(n) }, n))))));
    $("#batch-table").replaceChildren(head, ...rows);
    $("#batch-actions").hidden = false;
    $("#batch-stats").textContent = `${batchNames.length} ${T("names")}`;
  } catch (err) { toast(`${T("error")} : ${err.message}`); }
});

$("#batch-csv").addEventListener("click", () => download(`namematch_${stamp()}.csv`, csvColumnA(batchNames)));
$("#batch-copy").addEventListener("click", () => copyText(batchNames.join("\n")));
$("#batch-add").addEventListener("click", () => addToBasket(batchNames));

// ---------------------------------------------------------------- onglet Score
$("#score-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const a = $("#score-a").value.trim(), b = $("#score-b").value.trim();
  if (!a || !b) return;
  try {
    const r = await api("/api/score", { a, b });
    const cls = r.score >= 85 ? "good" : r.score >= 70 ? "mid" : "bad";
    $("#score-out").replaceChildren(
      el("div", { class: `score-big ${cls}` }, `${r.score}`),
      el("div", { class: "bar" }, el("i", { style: `width:${r.score}%` })),
      el("table", {}, ...r.pairs.map((p) => el("tr", {},
        el("td", { dir: "auto" }, p.a), el("td", {}, "↔"), el("td", { dir: "auto" }, p.b), el("td", {}, `${p.score}`)))));
  } catch (err) { toast(`${T("error")} : ${err.message}`); }
});

// ---------------------------------------------------------------- onglet Comparer
let cmpRows = [];
$("#cmp-th").addEventListener("input", (e) => { $("#cmp-th-v").textContent = e.target.value; });
$("#cmp-run").addEventListener("click", async () => {
  const lines = (sel) => $(sel).value.split(/\r?\n/).map((s) => s.trim()).filter(Boolean);
  try {
    const r = await api("/api/compare", { a: lines("#cmp-a"), b: lines("#cmp-b"), threshold: +$("#cmp-th").value });
    cmpRows = r.rows;
    $("#cmp-csv").hidden = !cmpRows.length;
    if (!cmpRows.length) {
      $("#cmp-table").replaceChildren(el("tr", {}, el("td", {}, T("no_match"))));
      return;
    }
    $("#cmp-table").replaceChildren(
      el("tr", {}, el("th", {}, "A"), el("th", {}, "B"), el("th", {}, T("tab_score"))),
      ...cmpRows.map((x) => el("tr", {},
        el("td", { dir: "auto" }, x.nom_A), el("td", { dir: "auto" }, x.nom_B), el("td", {}, `${x.score}`))));
  } catch (err) { toast(`${T("error")} : ${err.message}`); }
});
$("#cmp-csv").addEventListener("click", () =>
  download(`namematch_compare_${stamp()}.csv`, csvTable(cmpRows, ["ligne_A", "nom_A", "ligne_B", "nom_B", "score", "détail"])));

// ---------------------------------------------------------------- panier, onglets, langue
$("#basket-csv").addEventListener("click", () => {
  if (!basket.length) return toast(T("empty"));
  download(`namematch_${stamp()}.csv`, csvColumnA(basket));
});
$("#basket-copy").addEventListener("click", () => copyText(basket.join("\n")));
$("#basket-clear").addEventListener("click", () => { basket = []; saveBasket(); });

function showTab(name) {
  document.querySelectorAll(".tabs button").forEach((b) => b.classList.toggle("on", b.dataset.tab === name));
  document.querySelectorAll(".panel").forEach((p) => { p.hidden = p.id !== `tab-${name}`; });
  store.set("nm-tab", name);
}
document.querySelectorAll(".tabs button").forEach((b) => b.addEventListener("click", () => showTab(b.dataset.tab)));
document.querySelectorAll(".langs button").forEach((b) => b.addEventListener("click", () => applyLang(b.dataset.lang)));

applyLang(lang);
showTab(store.get("nm-tab", "gen"));
renderBasket();
