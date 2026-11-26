import html
import json

PAGE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="theme-color" content="#0b0f17">
<title>__NAME__ | __BRAND__</title>
<style>
:root{
  --bg:#0b0f17; --panel:#121826; --panel-2:#182033; --border:#232d45;
  --text:#e8ecf4; --muted:#8b95ab; --accent:#4f8cff; --accent-2:#7c5cff;
  --radius:14px; color-scheme:dark;
}
*{box-sizing:border-box}
html,body{margin:0;background:var(--bg);color:var(--text);
  font-family:Inter,system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif;
  -webkit-font-smoothing:antialiased}
body{background:radial-gradient(1200px 500px at 50% -10%,#16213a 0%,var(--bg) 60%) no-repeat,var(--bg);min-height:100vh}
a{color:inherit;text-decoration:none}
.wrap{max-width:1040px;margin:0 auto;padding:0 20px}
header{border-bottom:1px solid var(--border);background:rgba(11,15,23,.7);backdrop-filter:blur(8px);position:sticky;top:0;z-index:5}
.bar{display:flex;align-items:center;justify-content:space-between;height:64px}
.brand{display:flex;align-items:center;gap:12px}
.logo{width:36px;height:36px;border-radius:10px;display:grid;place-items:center;font-weight:800;font-size:18px;
  background:linear-gradient(135deg,var(--accent),var(--accent-2));box-shadow:0 6px 20px rgba(79,140,255,.35)}
.brand-name{font-weight:700;font-size:18px;letter-spacing:.2px}
.brand-sub{font-size:12px;color:var(--muted);margin-top:1px}
.pill{font-size:12px;color:var(--muted);border:1px solid var(--border);padding:6px 12px;border-radius:999px;background:var(--panel)}
.pill:hover{color:var(--text);border-color:var(--accent)}
main{padding:28px 0 40px}
.player{background:#000;border:1px solid var(--border);border-radius:var(--radius);overflow:hidden;
  box-shadow:0 20px 60px rgba(0,0,0,.45)}
.player video{display:block;width:100%;max-height:72vh;background:#000}
.player audio{display:block;width:100%;padding:24px;background:var(--panel)}
.info{margin-top:20px;background:var(--panel);border:1px solid var(--border);border-radius:var(--radius);padding:20px}
.title{font-size:20px;font-weight:650;line-height:1.35;word-break:break-word;margin:0 0 12px}
.meta{display:flex;flex-wrap:wrap;gap:8px}
.chip{font-size:12px;color:var(--muted);background:var(--panel-2);border:1px solid var(--border);padding:5px 10px;border-radius:8px}
.section{margin-top:22px}
.section h2{font-size:12px;font-weight:600;letter-spacing:1.2px;text-transform:uppercase;color:var(--muted);margin:0 0 12px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:10px}
.btn{display:flex;align-items:center;justify-content:center;gap:8px;padding:12px 14px;border-radius:10px;
  background:var(--panel-2);border:1px solid var(--border);color:var(--text);font-size:14px;font-weight:550;
  cursor:pointer;transition:.15s}
.btn:hover{border-color:var(--accent);transform:translateY(-1px);background:#1c2640}
.btn.primary{background:linear-gradient(135deg,var(--accent),var(--accent-2));border:0}
.btn.primary:hover{filter:brightness(1.1)}
.note{margin-top:12px;font-size:12px;color:var(--muted);line-height:1.6}
.toast{position:fixed;left:50%;bottom:28px;transform:translateX(-50%) translateY(20px);opacity:0;
  background:var(--panel-2);border:1px solid var(--border);padding:10px 18px;border-radius:10px;font-size:13px;
  transition:.25s;pointer-events:none}
.toast.show{opacity:1;transform:translateX(-50%) translateY(0)}
footer{border-top:1px solid var(--border);padding:22px 0;text-align:center;color:var(--muted);font-size:12px}
@media(max-width:560px){.title{font-size:17px}.grid{grid-template-columns:repeat(2,1fr)}}
</style>
</head>
<body>
<header><div class="wrap bar">
  <div class="brand">
    <div class="logo">__INITIAL__</div>
    <div><div class="brand-name">__BRAND__</div><div class="brand-sub">Secure file streaming</div></div>
  </div>
  __JOIN__
</div></header>

<main><div class="wrap">
  <div class="player">__PLAYER__</div>

  <div class="info">
    <h1 class="title">__NAME__</h1>
    <div class="meta"><span class="chip">__SIZE__</span><span class="chip">__MIME__</span><span class="chip">Streamed by __BRAND__</span></div>

    <div class="section">
      <h2>Download</h2>
      <div class="grid">
        <a class="btn primary" id="dl" href="#">Download file</a>
        <button class="btn" id="copy">Copy stream link</button>
      </div>
    </div>

    <div class="section">
      <h2>Open in external player</h2>
      <div class="grid">
        <a class="btn" id="vlc" href="#">VLC</a>
        <a class="btn" id="mx" href="#">MX Player</a>
        <a class="btn" id="pot" href="#">PotPlayer</a>
        <a class="btn" id="iina" href="#">IINA (Mac)</a>
        <a class="btn" id="infuse" href="#">Infuse (iOS)</a>
        <a class="btn" id="nplayer" href="#">nPlayer</a>
      </div>
      <p class="note">External players must be installed on your device. On desktop VLC, use <b>Copy stream link</b>, then Media &rarr; Open Network Stream.</p>
    </div>
  </div>
</div></main>

<footer>&copy; __BRAND__ &middot; All rights reserved</footer>
<div class="toast" id="toast"></div>

<script>
(function(){
  var STREAM = __STREAM_JSON__;
  var TITLE = __TITLE_JSON__;
  var u = new URL(STREAM);
  var enc = encodeURIComponent(STREAM);
  var proto = u.protocol.replace(':','');
  var hostPath = u.host + u.pathname + u.search;
  var ua = navigator.userAgent || '';
  var isAndroid = /Android/i.test(ua);
  var isIOS = /iPhone|iPad|iPod/i.test(ua);

  function intent(pkg){
    return 'intent://' + hostPath + '#Intent;scheme=' + proto + ';package=' + pkg +
           ';type=video/*;S.title=' + encodeURIComponent(TITLE) + ';end';
  }
  function set(id, href){ var el = document.getElementById(id); if(el) el.href = href; }

  set('dl', STREAM + '&dl=1');
  set('vlc', isAndroid ? intent('org.videolan.vlc')
           : isIOS ? 'vlc-x-callback://x-callback-url/stream?url=' + enc
           : 'vlc://' + STREAM);
  set('mx', isAndroid ? intent('com.mxtech.videoplayer.ad') : '#');
  set('pot', 'potplayer://' + STREAM);
  set('iina', 'iina://weblink?url=' + enc);
  set('infuse', 'infuse://x-callback-url/play?url=' + enc);
  set('nplayer', 'nplayer-' + STREAM);

  var toast = document.getElementById('toast');
  function show(msg){
    toast.textContent = msg; toast.classList.add('show');
    setTimeout(function(){ toast.classList.remove('show'); }, 2200);
  }
  document.getElementById('mx').addEventListener('click', function(e){
    if(!isAndroid){ e.preventDefault(); show('MX Player is available on Android only'); }
  });
  document.getElementById('copy').addEventListener('click', function(){
    function fallback(){
      var t = document.createElement('textarea'); t.value = STREAM; document.body.appendChild(t);
      t.select(); try{ document.execCommand('copy'); show('Link copied'); }catch(e){ show('Copy failed'); }
      document.body.removeChild(t);
    }
    if(navigator.clipboard && navigator.clipboard.writeText){
      navigator.clipboard.writeText(STREAM).then(function(){ show('Link copied'); }, fallback);
    } else { fallback(); }
  });
})();
</script>
</body>
</html>"""


def build_page(*, name, size, mime, stream_url, brand, channel_link=""):
    tag = "audio" if mime.startswith("audio") else "video"
    player = (
        f'<{tag} controls autoplay playsinline preload="metadata">'
        f'<source src="{html.escape(stream_url, quote=True)}" type="{html.escape(mime, quote=True)}">'
        f"Your browser does not support this player.</{tag}>"
    )
    join = ""
    if channel_link:
        join = f'<a class="pill" href="{html.escape(channel_link, quote=True)}" target="_blank" rel="noopener">Join {html.escape(brand)}</a>'
    return (
        PAGE.replace("__PLAYER__", player)
        .replace("__JOIN__", join)
        .replace("__STREAM_JSON__", json.dumps(stream_url).replace("</", "<\\/"))
        .replace("__TITLE_JSON__", json.dumps(name).replace("</", "<\\/"))
        .replace("__INITIAL__", html.escape(brand[:1].upper() or "C"))
        .replace("__BRAND__", html.escape(brand))
        .replace("__NAME__", html.escape(name))
        .replace("__SIZE__", html.escape(size))
        .replace("__MIME__", html.escape(mime))
    )
