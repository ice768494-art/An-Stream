import html

CSS = """
:root{--bg:#0b0f17;--panel:#121826;--panel-2:#182033;--border:#232d45;--text:#e8ecf4;--muted:#8b95ab;
--accent:#4f8cff;--accent-2:#7c5cff;--ok:#34d399;--bad:#f87171;--radius:14px;color-scheme:dark}
*{box-sizing:border-box}
html,body{margin:0;background:var(--bg);color:var(--text);font-family:Inter,system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif;-webkit-font-smoothing:antialiased}
body{background:radial-gradient(1200px 500px at 50% -10%,#16213a 0%,var(--bg) 60%) no-repeat,var(--bg);min-height:100vh}
a{color:inherit;text-decoration:none}
.wrap{max-width:1040px;margin:0 auto;padding:0 20px}
header{border-bottom:1px solid var(--border);background:rgba(11,15,23,.7);backdrop-filter:blur(8px)}
.bar{display:flex;align-items:center;justify-content:space-between;height:64px}
.brand{display:flex;align-items:center;gap:12px}
.logo{width:36px;height:36px;border-radius:10px;display:grid;place-items:center;font-weight:800;font-size:18px;background:linear-gradient(135deg,var(--accent),var(--accent-2));box-shadow:0 6px 20px rgba(79,140,255,.35)}
.brand-name{font-weight:700;font-size:18px}
.pill{font-size:12px;color:var(--muted);border:1px solid var(--border);padding:6px 12px;border-radius:999px;background:var(--panel)}
.hero{text-align:center;padding:72px 20px 40px}
.badge{display:inline-block;font-size:12px;color:var(--accent);border:1px solid var(--border);background:var(--panel);padding:6px 14px;border-radius:999px;margin-bottom:20px}
.hero h1{font-size:clamp(28px,5vw,46px);line-height:1.15;margin:0 auto 16px;max-width:760px}
.hero p{color:var(--muted);font-size:16px;line-height:1.7;max-width:620px;margin:0 auto 28px}
.actions{display:flex;gap:12px;justify-content:center;flex-wrap:wrap}
.btn{display:inline-flex;align-items:center;justify-content:center;padding:12px 22px;border-radius:10px;background:var(--panel-2);border:1px solid var(--border);color:var(--text);font-size:14px;font-weight:600;cursor:pointer;transition:.15s;font-family:inherit}
.btn:hover{border-color:var(--accent);transform:translateY(-1px)}
.btn.primary{background:linear-gradient(135deg,var(--accent),var(--accent-2));border:0}
.btn.danger{background:#3b1d24;border-color:#5b2a35}
.grid3{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:14px;margin:20px 0 40px}
.card{background:var(--panel);border:1px solid var(--border);border-radius:var(--radius);padding:20px}
.card h3{margin:0 0 8px;font-size:16px}.card p{margin:0;color:var(--muted);font-size:14px;line-height:1.6}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:14px;margin:24px 0}
.stat .n{font-size:30px;font-weight:700}.stat .l{color:var(--muted);font-size:13px;margin-top:4px}
h2.s{font-size:12px;letter-spacing:1.2px;text-transform:uppercase;color:var(--muted);margin:0 0 12px;font-weight:600}
textarea,input[type=text]{width:100%;background:var(--panel-2);border:1px solid var(--border);color:var(--text);border-radius:10px;padding:12px;font-family:inherit;font-size:14px}
textarea{min-height:120px;resize:vertical}
.row{display:flex;gap:10px;flex-wrap:wrap;margin-top:12px}
.notice{background:#14304a;border:1px solid #1f4a73;padding:10px 14px;border-radius:10px;margin:16px 0;font-size:14px}
table{width:100%;border-collapse:collapse;font-size:13px}
th,td{text-align:left;padding:10px 8px;border-bottom:1px solid var(--border);word-break:break-word}
th{color:var(--muted);font-weight:600}
.tbl{overflow-x:auto}
.two{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:14px;margin-bottom:14px}
footer{border-top:1px solid var(--border);padding:22px 0;text-align:center;color:var(--muted);font-size:12px;margin-top:30px}
"""


def header(brand, right=""):
    b = html.escape(brand)
    return (
        '<header><div class="wrap bar"><div class="brand">'
        f'<div class="logo">{html.escape(brand[:1].upper() or "C")}</div><div class="brand-name">{b}</div></div>{right}</div></header>'
    )


def page(title, body, brand, right="", extra_head=""):
    return (
        '<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        f"<title>{html.escape(title)}</title>{extra_head}<style>{CSS}</style></head><body>"
        + header(brand, right)
        + body
        + f'<footer>&copy; {html.escape(brand)} &middot; All rights reserved</footer></body></html>'
    )


def landing(brand, bot_username="", channel_link=""):
    b = html.escape(brand)
    actions = ""
    if bot_username:
        actions += f'<a class="btn primary" href="https://t.me/{html.escape(bot_username)}" target="_blank" rel="noopener">Open Telegram Bot</a>'
    if channel_link:
        actions += f'<a class="btn" href="{html.escape(channel_link, quote=True)}" target="_blank" rel="noopener">Join {b}</a>'
    features = [
        ("Instant links", "Send any file to the bot and get a stream link and a download link in seconds."),
        ("Watch online", "A clean web player with seeking, plus one-tap open in VLC, MX Player and more."),
        ("Secure by design", "Every link carries a unique hash, so files cannot be guessed or enumerated."),
    ]
    cards = "".join(f'<div class="card"><h3>{t}</h3><p>{d}</p></div>' for t, d in features)
    body = (
        '<main><div class="wrap hero"><span class="badge">Fast &middot; Secure &middot; Simple</span>'
        "<h1>Stream and download Telegram files instantly</h1>"
        f"<p>{b} turns any file you send on Telegram into a shareable web link you can watch or download from any device.</p>"
        f'<div class="actions">{actions}</div></div><div class="wrap"><div class="grid3">{cards}</div></div></main>'
    )
    return page(f"{brand} | File to Link", body, brand)
