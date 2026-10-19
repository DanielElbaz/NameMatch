"""Petit serveur web local (bibliothèque standard uniquement) pour l'interface NameMatch."""
import json
import os
import threading
import webbrowser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

from ..csv_tools import compare_lists
from ..i18n import t
from ..matching import score_names
from ..variants import correct_name, name_variants

STATIC = os.path.join(os.path.dirname(__file__), "static")
MAX_BATCH = 5000


def api_variants(body):
    return name_variants(str(body.get("name", "")), n=_count(body))


def api_batch(body):
    names = [str(x).strip() for x in body.get("names", []) if str(x).strip()][:MAX_BATCH]
    n = _count(body)
    return {"results": [name_variants(x, n=n) for x in names]}


def api_score(body):
    s, det = score_names(str(body.get("a", "")), str(body.get("b", "")))
    return {"score": s, "pairs": [{"a": a, "b": b, "score": round(x * 100, 1)} for a, b, x in det]}


def api_compare(body):
    rows_a = [{"nom": x} for x in body.get("a", []) if str(x).strip()][:MAX_BATCH]
    rows_b = [{"nom": x} for x in body.get("b", []) if str(x).strip()][:MAX_BATCH]
    threshold = float(body.get("threshold", 75))
    return {"rows": compare_lists(rows_a, "nom", rows_b, "nom", threshold, top=3)}


def api_correct(body):
    source, value = str(body.get("source", "")), str(body.get("value", ""))
    saved = correct_name(source, value)
    return {"saved": saved, "result": name_variants(source, n=_count(body))}


def _count(body):
    try:
        return max(1, min(int(body.get("count", 3)), 20))
    except (TypeError, ValueError):
        return 3


ROUTES = {"/api/variants": api_variants, "/api/batch": api_batch,
          "/api/score": api_score, "/api/compare": api_compare,
          "/api/correct": api_correct}


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=STATIC, **kw)

    def log_message(self, *args):
        pass

    def do_POST(self):
        fn = ROUTES.get(self.path)
        if not fn:
            self.send_error(404)
            return
        try:
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length) or b"{}")
            payload, status = fn(body), 200
        except Exception as e:  # renvoyé à l'interface plutôt que de couper la connexion
            payload, status = {"error": str(e)}, 400
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


def serve(port=8765, open_browser=True, lang="fr"):
    httpd = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    url = f"http://127.0.0.1:{port}/?lang={lang}"
    print(f"{t('ui_running', lang)} {url}  ({t('stop', lang)})")
    if open_browser:
        threading.Timer(0.5, webbrowser.open, args=(url,)).start()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()
