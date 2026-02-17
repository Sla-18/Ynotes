import urllib.request
import urllib.parse
import urllib.error
import json
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from wsgiref.simple_server import make_server, WSGIRequestHandler

# ── Credenciais do app ────────────────────────────────────────
USER_NAME = "Edy"
USER_PASS  = "tor12.nado"

# ── Configuração Supabase ─────────────────────────────────────
SUPABASE_URL = "https://lmafzsfqqvrivmqyracj.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxtYWZ6c2ZxcXZyaXZtcXlyYWNqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzEzMzI4NjIsImV4cCI6MjA4NjkwODg2Mn0.c1FfB3xprl9B-EysU94-hOeQwllso-Oarhg48Agi9lU"

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

# ── Funções Supabase ──────────────────────────────────────────

def sb_request(method, endpoint, data=None):
    url  = f"{SUPABASE_URL}/rest/v1/{endpoint}"
    body = json.dumps(data).encode() if data else None
    req  = urllib.request.Request(url, data=body, headers=HEADERS, method=method)
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        print(f"[Supabase erro {e.code}]: {e.read().decode()}")
        return None
    except Exception as e:
        print(f"[Supabase erro]: {e}")
        return None

def get_notas():
    result = sb_request("GET", "notas?order=criada_em.desc&select=*")
    return result if result else []

def add_nota(titulo, conteudo):
    return sb_request("POST", "notas", {"titulo": titulo, "conteudo": conteudo})

def delete_nota(nota_id):
    url = f"{SUPABASE_URL}/rest/v1/notas?id=eq.{nota_id}"
    req = urllib.request.Request(url, headers=HEADERS, method="DELETE")
    try:
        with urllib.request.urlopen(req, timeout=10):
            return True
    except Exception as e:
        print(f"[Supabase delete erro]: {e}")
        return False

# ── HTML Login ────────────────────────────────────────────────

LOGIN_PAGE = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>YNot&amp;S</title>
<style>
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  :root {
    --bg:#0a0a0f; --surface:#13131c; --border:#2a2a40;
    --accent:#c8ff00; --accent2:#6e4cff; --text:#e8e8f0; --muted:#5a5a78;
    --ft:Georgia,'Times New Roman',serif; --fb:'Courier New',Courier,monospace;
  }
  body { min-height:100vh; background:var(--bg); display:flex; align-items:center; justify-content:center; font-family:var(--fb); position:relative; overflow:hidden; }
  body::before { content:''; position:fixed; inset:0; background-image:linear-gradient(rgba(110,76,255,.08) 1px,transparent 1px),linear-gradient(90deg,rgba(110,76,255,.08) 1px,transparent 1px); background-size:40px 40px; pointer-events:none; }
  body::after { content:''; position:fixed; top:50%; left:50%; transform:translate(-50%,-50%); width:560px; height:360px; background:radial-gradient(ellipse,rgba(110,76,255,.22) 0%,transparent 70%); pointer-events:none; }
  .card { background:var(--surface); border:1px solid var(--border); border-radius:20px; padding:52px 44px 44px; width:360px; max-width:93vw; position:relative; z-index:1; box-shadow:0 0 60px rgba(110,76,255,.2),0 24px 48px rgba(0,0,0,.7); animation:rise .55s cubic-bezier(.22,1,.36,1) both; }
  @keyframes rise { from{opacity:0;transform:translateY(28px) scale(.97)} to{opacity:1;transform:translateY(0) scale(1)} }
  .card::before { content:''; position:absolute; top:-1px; left:36px; right:36px; height:3px; background:linear-gradient(90deg,var(--accent2),var(--accent)); border-radius:0 0 4px 4px; }
  .logo { font-family:var(--ft); font-size:2.6rem; font-weight:900; font-style:italic; color:var(--text); text-align:center; letter-spacing:-1px; margin-bottom:4px; }
  .logo span { color:var(--accent); font-style:normal; }
  .sub { text-align:center; color:var(--muted); font-size:.63rem; letter-spacing:.22em; text-transform:uppercase; margin-bottom:38px; }
  .field { margin-bottom:16px; }
  label { display:block; font-size:.62rem; letter-spacing:.18em; text-transform:uppercase; color:var(--muted); margin-bottom:7px; }
  input { width:100%; background:var(--bg); border:1px solid var(--border); border-radius:10px; padding:13px 15px; color:var(--text); font-family:var(--fb); font-size:.9rem; outline:none; transition:border-color .2s,box-shadow .2s; -webkit-appearance:none; }
  input:focus { border-color:var(--accent2); box-shadow:0 0 0 3px rgba(110,76,255,.2); }
  .btn { width:100%; margin-top:26px; padding:14px; background:var(--accent); color:#0a0a0f; border:none; border-radius:10px; font-family:var(--fb); font-size:.84rem; font-weight:700; letter-spacing:.1em; text-transform:uppercase; cursor:pointer; transition:transform .15s,box-shadow .15s; -webkit-appearance:none; }
  .btn:hover { transform:translateY(-2px); box-shadow:0 8px 24px rgba(200,255,0,.35); }
  .error { background:rgba(255,70,70,.1); border:1px solid rgba(255,70,70,.35); border-radius:8px; padding:9px 13px; color:#ff7070; font-size:.73rem; margin-top:14px; text-align:center; animation:shake .3s; }
  @keyframes shake { 0%,100%{transform:translateX(0)} 25%{transform:translateX(-7px)} 75%{transform:translateX(7px)} }
</style>
</head>
<body>
<div class="card">
  <div class="logo">YNot<span>&amp;</span>S</div>
  <div class="sub">acesso seguro</div>
  <form method="POST" action="/login">
    <div class="field"><label>Usuario</label><input type="text" name="username" placeholder="seu nome" autocomplete="off" required></div>
    <div class="field"><label>Senha</label><input type="password" name="password" placeholder="********" required></div>
    {ERROR}
    <button class="btn" type="submit">Entrar</button>
  </form>
</div>
</body></html>"""

ERROR_BLOCK = '<div class="error">&#9888; Usuario ou senha incorretos.</div>'

# ── HTML Notas ────────────────────────────────────────────────

def build_notes_page(notas, msg=""):
    cards = ""
    if not notas:
        cards = '<div class="empty">Nenhuma nota ainda. Crie a primeira acima &#10022;</div>'
    else:
        for n in notas:
            nid      = n.get("id", "")
            titulo   = (n.get("titulo") or "").replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
            conteudo = (n.get("conteudo") or "").replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
            data_raw = n.get("criada_em", "")[:16].replace("T", " ")
            cards += f"""<div class="note-card">
              <div class="note-card-title">{titulo}</div>
              <div class="note-card-body">{conteudo}</div>
              <div class="note-meta"><span>{data_raw}</span>
                <form method="POST" action="/delete" style="display:inline">
                  <input type="hidden" name="id" value="{nid}">
                  <button class="btn-del" type="submit">&#10005; apagar</button>
                </form>
              </div></div>"""

    msg_html = f'<div class="toast">{msg}</div>' if msg else ""
    count = len(notas)

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>YNot&amp;S</title>
<style>
  *, *::before, *::after {{ box-sizing:border-box; margin:0; padding:0; }}
  :root {{ --bg:#0a0a0f; --surface:#13131c; --card:#1a1a28; --border:#2a2a40; --accent:#c8ff00; --accent2:#6e4cff; --text:#e8e8f0; --muted:#5a5a78; --ft:Georgia,'Times New Roman',serif; --fb:'Courier New',Courier,monospace; }}
  body {{ min-height:100vh; background:var(--bg); font-family:var(--fb); color:var(--text); overflow-x:hidden; }}
  body::before {{ content:''; position:fixed; inset:0; background-image:linear-gradient(rgba(110,76,255,.05) 1px,transparent 1px),linear-gradient(90deg,rgba(110,76,255,.05) 1px,transparent 1px); background-size:40px 40px; pointer-events:none; z-index:0; }}
  header {{ position:sticky; top:0; z-index:100; background:rgba(10,10,15,.92); border-bottom:1px solid var(--border); padding:0 22px; display:flex; align-items:center; justify-content:space-between; height:62px; }}
  .brand {{ font-family:var(--ft); font-size:1.55rem; font-weight:900; font-style:italic; letter-spacing:-1px; color:var(--text); }}
  .brand span {{ color:var(--accent); font-style:normal; }}
  .tag {{ font-size:.6rem; letter-spacing:.18em; text-transform:uppercase; color:var(--muted); border:1px solid var(--border); border-radius:20px; padding:4px 12px; }}
  main {{ position:relative; z-index:1; max-width:860px; margin:0 auto; padding:34px 16px 80px; }}
  .toast {{ background:rgba(200,255,0,.1); border:1px solid rgba(200,255,0,.28); border-radius:8px; padding:9px 14px; color:var(--accent); font-size:.73rem; margin-bottom:18px; text-align:center; }}
  .new-note {{ background:var(--surface); border:1px solid var(--border); border-radius:16px; padding:22px; margin-bottom:30px; box-shadow:0 0 40px rgba(110,76,255,.08); }}
  .new-note h2 {{ font-family:var(--ft); font-size:.95rem; font-style:italic; color:var(--muted); margin-bottom:14px; }}
  .note-title-input {{ width:100%; background:var(--bg); border:1px solid var(--border); border-radius:10px; padding:11px 14px; color:var(--text); font-family:var(--ft); font-size:1rem; font-weight:700; outline:none; margin-bottom:9px; transition:border-color .2s,box-shadow .2s; -webkit-appearance:none; }}
  .note-title-input:focus {{ border-color:var(--accent2); box-shadow:0 0 0 3px rgba(110,76,255,.18); }}
  textarea {{ width:100%; min-height:108px; background:var(--bg); border:1px solid var(--border); border-radius:10px; padding:12px 14px; color:var(--text); font-family:var(--fb); font-size:.83rem; line-height:1.75; outline:none; resize:vertical; transition:border-color .2s,box-shadow .2s; -webkit-appearance:none; }}
  textarea:focus {{ border-color:var(--accent2); box-shadow:0 0 0 3px rgba(110,76,255,.18); }}
  .row {{ display:flex; justify-content:flex-end; margin-top:12px; }}
  .btn-add {{ background:var(--accent); color:#0a0a0f; border:none; border-radius:10px; padding:10px 26px; font-family:var(--fb); font-size:.78rem; font-weight:700; letter-spacing:.1em; text-transform:uppercase; cursor:pointer; transition:transform .15s,box-shadow .15s; -webkit-appearance:none; }}
  .btn-add:hover {{ transform:translateY(-2px); box-shadow:0 8px 20px rgba(200,255,0,.28); }}
  .section-title {{ font-size:.6rem; letter-spacing:.22em; text-transform:uppercase; color:var(--muted); margin-bottom:16px; display:flex; align-items:center; gap:10px; }}
  .section-title::after {{ content:''; flex:1; height:1px; background:var(--border); }}
  .notes-grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(230px,1fr)); gap:14px; }}
  .note-card {{ background:var(--card); border:1px solid var(--border); border-radius:13px; padding:18px 18px 14px; position:relative; overflow:hidden; animation:popIn .4s cubic-bezier(.22,1,.36,1) both; transition:transform .2s,box-shadow .2s; }}
  .note-card::before {{ content:''; position:absolute; top:0; left:0; right:0; height:3px; background:linear-gradient(90deg,var(--accent2),var(--accent)); }}
  .note-card:hover {{ transform:translateY(-4px); box-shadow:0 12px 30px rgba(0,0,0,.45); }}
  @keyframes popIn {{ from{{opacity:0;transform:scale(.93)}} to{{opacity:1;transform:scale(1)}} }}
  .note-card-title {{ font-family:var(--ft); font-size:.97rem; font-weight:700; margin-bottom:9px; word-break:break-word; color:var(--text); }}
  .note-card-body {{ font-size:.76rem; color:#9898b8; line-height:1.75; word-break:break-word; white-space:pre-wrap; }}
  .note-meta {{ font-size:.62rem; color:var(--muted); margin-top:13px; padding-top:9px; border-top:1px solid var(--border); display:flex; justify-content:space-between; align-items:center; }}
  .btn-del {{ background:none; border:none; color:var(--muted); cursor:pointer; font-size:.7rem; font-family:var(--fb); padding:2px 6px; border-radius:5px; transition:color .18s,background .18s; }}
  .btn-del:hover {{ color:#ff7070; background:rgba(255,70,70,.1); }}
  .empty {{ grid-column:1/-1; text-align:center; color:var(--muted); font-size:.78rem; padding:52px 0; letter-spacing:.08em; }}
</style>
</head>
<body>
<header>
  <div class="brand">YNot<span>&amp;</span>S</div>
  <div class="tag">suas notas</div>
</header>
<main>
  {msg_html}
  <div class="new-note">
    <h2>&#10022; Nova nota</h2>
    <form method="POST" action="/add">
      <input class="note-title-input" type="text" name="titulo" placeholder="Titulo da nota..." maxlength="80">
      <textarea name="conteudo" placeholder="Escreva aqui o conteudo da nota..."></textarea>
      <div class="row"><button class="btn-add" type="submit">+ Adicionar</button></div>
    </form>
  </div>
  <div class="section-title">Notas salvas ({count})</div>
  <div class="notes-grid">{cards}</div>
</main>
</body></html>"""

# ── App WSGI (compatível com gunicorn) ────────────────────────

def application(environ, start_response):
    method = environ["REQUEST_METHOD"]
    path   = environ.get("PATH_INFO", "/")

    def respond(html, code="200 OK"):
        body = html.encode("utf-8")
        start_response(code, [
            ("Content-Type", "text/html; charset=utf-8"),
            ("Content-Length", str(len(body)))
        ])
        return [body]

    def redirect(location):
        start_response("302 Found", [("Location", location)])
        return [b""]

    def parse_body():
        length = int(environ.get("CONTENT_LENGTH") or 0)
        raw    = environ["wsgi.input"].read(length).decode("utf-8")
        return urllib.parse.parse_qs(raw)

    if method == "GET":
        if path in ("/", "/login"):
            return respond(LOGIN_PAGE.replace("{ERROR}", ""))
        elif path == "/notas":
            notas = get_notas()
            return respond(build_notes_page(notas))
        else:
            return redirect("/")

    elif method == "POST":
        params = parse_body()

        if path == "/login":
            user = params.get("username", [""])[0]
            pwd  = params.get("password",  [""])[0]
            if user == USER_NAME and pwd == USER_PASS:
                return redirect("/notas")
            else:
                return respond(LOGIN_PAGE.replace("{ERROR}", ERROR_BLOCK))

        elif path == "/add":
            titulo   = params.get("titulo",   [""])[0].strip()
            conteudo = params.get("conteudo", [""])[0].strip()
            if titulo or conteudo:
                add_nota(titulo or "(sem titulo)", conteudo)
                msg = "Nota adicionada com sucesso!"
            else:
                msg = ""
            notas = get_notas()
            return respond(build_notes_page(notas, msg))

        elif path == "/delete":
            nota_id = params.get("id", [""])[0]
            if nota_id:
                delete_nota(nota_id)
            notas = get_notas()
            return respond(build_notes_page(notas, "Nota apagada."))

        else:
            return redirect("/")

    return redirect("/")

# ── Rodar localmente (Pydroid3) ───────────────────────────────

if __name__ == "__main__":
    import threading, webbrowser
    port = int(os.environ.get("PORT", 8080))

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *a): pass
        def do_GET(self):
            result = application(self._make_environ(), self._start_response)
            self.wfile.write(result[0])
        def do_POST(self):
            result = application(self._make_environ(), self._start_response)
            self.wfile.write(result[0])
        def _start_response(self, status, headers):
            code = int(status.split()[0])
            self.send_response(code)
            for k, v in headers:
                self.send_header(k, v)
            self.end_headers()
        def _make_environ(self):
            length = self.headers.get("Content-Length", 0)
            return {
                "REQUEST_METHOD": self.command,
                "PATH_INFO": self.path,
                "CONTENT_LENGTH": length,
                "wsgi.input": self.rfile,
            }

    server = HTTPServer(("0.0.0.0", port), Handler)
    print(f"YNot&S rodando em http://127.0.0.1:{port}")
    threading.Timer(0.8, lambda: webbrowser.open(f"http://127.0.0.1:{port}")).start()
    server.serve_forever()
