"""EcoSphere visual theme: layered background, ambient animation, landscape hero, CSS."""
import html as _html
from urllib.parse import quote


def _uri(svg: str) -> str:
    return "data:image/svg+xml," + quote(svg.replace("\n", ""), safe="")


def esc(x) -> str:
    return _html.escape(str(x))


# ---------- page background layers (fixed behind everything) ----------
_PINES = "".join(
    f"<path d='M{x} {y} l-12 26 h24z M{x} {y - 14} l-9 20 h18z'/>"
    for x, y in [(70, 178), (130, 170), (300, 182), (520, 176), (760, 184),
                 (980, 172), (1100, 180), (1180, 170), (1340, 176)])
HILLS = _uri(
    "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1440 240' preserveAspectRatio='xMidYMax slice'>"
    "<path fill='#7fc8d9' fill-opacity='.22' d='M0 110 C240 50 440 140 720 100 C1000 60 1220 130 1440 80 L1440 240 L0 240Z'/>"
    "<path fill='#6cc08f' fill-opacity='.26' d='M0 160 C220 120 460 190 760 150 C1040 112 1240 180 1440 140 L1440 240 L0 240Z'/>"
    f"<g fill='#2e8b57' fill-opacity='.28'>{_PINES}</g>"
    "<path fill='#1f7a49' fill-opacity='.30' d='M0 212 C300 186 600 232 900 206 C1100 188 1300 222 1440 202 L1440 240 L0 240Z'/>"
    "</svg>")

PATTERN = _uri(
    "<svg xmlns='http://www.w3.org/2000/svg' width='160' height='160' viewBox='0 0 160 160'>"
    "<g fill='none' stroke='#2e9e5b' stroke-opacity='.10' stroke-width='1.2' stroke-linecap='round'>"
    "<path d='M24 128 C24 88 54 66 90 66 C90 106 60 128 24 128Z'/><path d='M24 128 L82 74'/>"
    "<path d='M112 44 C112 22 128 8 148 8 C148 30 132 44 112 44Z'/><path d='M112 44 L142 14'/>"
    "<path d='M120 150 C132 130 150 124 160 126'/><path d='M0 36 C14 24 30 22 42 28'/></g></svg>")


# ---------- hero landscape illustration ----------
def _tree(x, y):
    return (f"<g transform='translate({x} {y})'><rect x='-2.5' y='0' width='5' height='16' fill='#6b4f2a'/>"
            "<circle cx='0' cy='-4' r='13' fill='#1f7a49'/><circle cx='-8' cy='4' r='9' fill='#2a8c55'/>"
            "<circle cx='8' cy='4' r='9' fill='#2a8c55'/></g>")


def _pine(x, y):
    return (f"<path transform='translate({x} {y})' fill='#14653a' "
            "d='M0 -26 l-12 24 h24z M0 -14 l-15 26 h30z M-2 12 h4 v8 h-4z'/>")


def scene_svg():
    return ("<svg viewBox='0 0 1200 200' preserveAspectRatio='xMidYMax slice' xmlns='http://www.w3.org/2000/svg'>"
            "<path fill='#b9e3c6' d='M0 90 C180 40 380 110 600 75 C820 40 1000 100 1200 60 L1200 200 L0 200Z'/>"
            "<path d='M930 112 L930 30' stroke='#ffffff' stroke-width='3' stroke-linecap='round'/>"
            "<g class='blades' style='transform-origin:930px 30px'>"
            "<path d='M930 30 L930 4 M930 30 L952 43 M930 30 L908 43' stroke='#ffffff' stroke-width='3' stroke-linecap='round'/></g>"
            "<circle cx='930' cy='30' r='3.5' fill='#ffffff'/>"
            "<path fill='#7ccf95' d='M0 130 C200 90 420 150 640 115 C860 80 1040 140 1200 105 L1200 200 L0 200Z'/>"
            + _tree(150, 112) + _tree(330, 124) + _tree(810, 104) + _tree(1010, 116)
            + "<path fill='#2e9e5b' d='M0 165 C220 135 440 185 700 155 C920 130 1060 175 1200 150 L1200 200 L0 200Z'/>"
            + _pine(85, 148) + _pine(115, 154) + _pine(560, 160) + _pine(1110, 146) + _pine(1145, 152)
            + "<path fill='#17804b' d='M0 188 C300 170 620 200 900 182 C1050 174 1140 190 1200 184 L1200 200 L0 200Z'/>"
            "</svg>")


# ---------- ambient layer: clouds, leaves, particles (fixed, non-interactive) ----------
def ambient_html():
    leaves = "".join(
        f'<span class="lf" style="left:{(i * 37 + 11) % 96}%;font-size:{16 + (i * 5) % 14}px;'
        f'animation-duration:{26 + (i * 7) % 16}s;animation-delay:-{(i * 5) % 24}s">'
        f'{"🍃" if i % 2 else "🌿"}</span>' for i in range(9))
    dots = "".join(
        f'<span class="pt p{i % 3}" style="left:{(i * 23 + 5) % 98}%;width:{3 + (i % 3) * 2}px;'
        f'height:{3 + (i % 3) * 2}px;animation-duration:{18 + (i * 5) % 14}s;'
        f'animation-delay:-{(i * 3) % 18}s"></span>' for i in range(14))
    return f'<div class="ambient"><span class="cloud c1"></span><span class="cloud c2"></span>{leaves}{dots}</div>'


# ---------- hero ----------
def hero_html(icon, stage, xp, streak, area, aqi, aqi_label, aqi_colour, co2_kg):
    co2_sub = "from kWh you logged as saved" if co2_kg else "log a kWh action to start"
    return f'''
<div class="eco-hero">
<span class="cloud hc1"></span><span class="cloud hc2"></span>
<div class="eco-scene">{scene_svg()}</div>
<div class="eco-copy">
<div class="eco-h">Grow Your Impact.<br>Green Your World.</div>
<p class="eco-p">Check the air you breathe, shrink your carbon footprint, and join your neighbourhood in protecting the planet, one small action at a time.</p>
</div>
<div class="eco-cards">
<div class="stat"><div class="k"><span class="dot" style="--c:{aqi_colour}"></span>Air quality · {esc(area)}</div>
<div class="v">AQI {int(aqi)}</div><div class="s">{esc(aqi_label)}</div></div>
<div class="stat"><div class="k">🌍 CO₂ avoided</div>
<div class="v">{co2_kg:.1f} kg</div><div class="s">{co2_sub}</div></div>
<div class="stat"><div class="k">Your growth</div>
<div class="v"><span class="sway-ic">{icon}</span> {esc(stage)}</div>
<div class="s">{xp} XP · <span class="fire">🔥</span> {streak}-day streak</div></div>
</div>
</div>
'''


# Buttons live in a small iframe so they can switch tabs in the parent page.
CTA_HTML = """
<link href="https://fonts.googleapis.com/css2?family=Sora:wght@600;700&display=swap" rel="stylesheet">
<style>
body{margin:0;font-family:'Sora',system-ui,sans-serif}
.row{display:flex;gap:12px;flex-wrap:wrap;padding:6px 2px}
button{font:inherit;font-weight:700;font-size:.95rem;padding:12px 24px;border-radius:999px;cursor:pointer;transition:transform .15s,box-shadow .15s}
button:hover{transform:translateY(-2px)}
button:focus-visible{outline:3px solid #1fb5a8;outline-offset:2px}
.p{border:none;color:#fff;background:linear-gradient(90deg,#1f8f4e,#1fb5a8);box-shadow:0 8px 20px rgba(31,143,78,.35)}
.s{background:rgba(255,255,255,.85);color:#0f3d2e;border:2px solid #2e9e5b}
</style>
<div class="row">
<button class="p" onclick="go(2)">Start today's action</button>
<button class="s" onclick="go(0)">Check my air quality</button>
</div>
<script>
function go(i){
  try{
    var t=window.parent.document.querySelectorAll('button[data-baseweb="tab"]');
    if(t[i]) t[i].click();
    window.parent.scrollTo({top:0,behavior:'smooth'});
  }catch(e){}
}
</script>
"""

_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@500;700;800&display=swap');
:root{--forest:#0f3d2e;--emerald:#2e9e5b;--mint:#e7f8ee;--sky:#1fb5a8;--amber:#f2b134}
.stApp{background:url("__PATTERN__") 0 0/160px 160px repeat,url("__HILLS__") center bottom/100% 220px no-repeat,radial-gradient(circle at 10% 6%,rgba(31,181,168,.20),transparent 38%),radial-gradient(circle at 92% 22%,rgba(183,227,106,.26),transparent 36%),linear-gradient(180deg,#e3f3ff 0%,#e7f8ee 42%,#f7fbf2 100%) !important;background-attachment:fixed !important}
[data-testid="stAppViewContainer"],[data-testid="stMain"],[data-testid="stHeader"]{background:transparent !important}
.block-container{position:relative;z-index:1}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#d9f1e3 0%,#d4ecf7 100%) !important;border-right:1px solid rgba(46,158,91,.2)}
[data-testid="stSidebar"]>div:first-child{background:transparent}
h1,h2,h3,.eco-h,.g-num{font-family:'Sora',sans-serif !important;letter-spacing:-.01em}
h1,h2,h3{color:var(--forest)}
@keyframes cloudDrift{from{transform:translateX(-260px)}to{transform:translateX(calc(100vw + 260px))}}
@keyframes leafFall{0%{transform:translate3d(0,-10vh,0) rotate(0);opacity:0}10%{opacity:.5}90%{opacity:.5}100%{transform:translate3d(60px,110vh,0) rotate(300deg);opacity:0}}
@keyframes rise{0%{transform:translate3d(0,0,0);opacity:0}15%{opacity:.75}85%{opacity:.6}100%{transform:translate3d(30px,-110vh,0);opacity:0}}
@keyframes floatCard{0%,100%{transform:translateY(0)}50%{transform:translateY(-8px)}}
@keyframes dotGlow{0%,100%{box-shadow:0 0 4px 1px var(--c)}50%{box-shadow:0 0 12px 5px var(--c)}}
@keyframes spin{to{transform:rotate(360deg)}}
@keyframes sway{0%,100%{transform:rotate(-3deg)}50%{transform:rotate(3deg)}}
@keyframes flicker{0%,100%{transform:scale(1) rotate(-3deg)}50%{transform:scale(1.18) rotate(4deg)}}
@keyframes ring{0%{box-shadow:0 0 0 0 rgba(46,158,91,.55)}70%{box-shadow:0 0 0 14px rgba(46,158,91,0)}100%{box-shadow:0 0 0 0 rgba(46,158,91,0)}}
@keyframes gaugeSweep{from{stroke-dashoffset:251.33}}
@keyframes markerSlide{from{left:0}}
.ambient{position:fixed;inset:0;pointer-events:none;overflow:hidden;z-index:-1}
.cloud{position:absolute;left:0;width:190px;height:54px;border-radius:60px;background:rgba(255,255,255,.75);filter:blur(1.5px);animation:cloudDrift 120s linear infinite}
.cloud::before,.cloud::after{content:"";position:absolute;border-radius:50%;background:inherit}
.cloud::before{width:84px;height:84px;top:-38px;left:26px}
.cloud::after{width:64px;height:64px;top:-26px;left:96px}
.ambient .c1{top:9%}
.ambient .c2{top:22%;transform:scale(.7);animation-duration:170s;animation-delay:-80s;opacity:.7}
.lf{position:absolute;top:0;opacity:0;animation:leafFall linear infinite}
.pt{position:absolute;bottom:-12px;border-radius:50%;animation:rise linear infinite}
.p0{background:#b7e36a;box-shadow:0 0 8px #b7e36a}
.p1{background:#fff;box-shadow:0 0 8px #fff}
.p2{background:#7cd3f0;box-shadow:0 0 8px #7cd3f0}
.eco-hero{position:relative;overflow:hidden;border-radius:28px;min-height:430px;padding:44px 44px 160px;margin-bottom:8px;color:var(--forest);display:grid;grid-template-columns:minmax(0,1.15fr) minmax(0,1fr);gap:24px;align-items:start;background:radial-gradient(circle at 82% 12%,#fff6c9 0,#fff6c9 3.5%,rgba(255,236,170,.9) 4.5%,rgba(255,236,170,0) 22%),linear-gradient(180deg,#a9dcff 0%,#d3f0f0 55%,#e6f7dc 100%);box-shadow:0 18px 50px rgba(15,61,46,.22)}
.eco-hero .hc1{top:12%;animation-duration:110s}
.eco-hero .hc2{top:34%;transform:scale(.65);animation-duration:160s;animation-delay:-70s;opacity:.8}
.eco-scene{position:absolute;left:0;right:0;bottom:0;height:200px;z-index:1}
.eco-scene svg{width:100%;height:100%;display:block}
.blades{animation:spin 9s linear infinite}
.eco-copy{position:relative;z-index:3}
.eco-h{font-weight:800;font-size:3rem;line-height:1.05;margin:0 0 14px;color:var(--forest)}
.eco-p{font-size:1.05rem;line-height:1.55;max-width:30rem;color:#1d4a38;margin:0}
.eco-cards{position:relative;z-index:3;display:flex;flex-direction:column;gap:14px;align-items:flex-end}
.stat{width:min(285px,100%);background:rgba(255,255,255,.80);backdrop-filter:blur(10px);border-radius:18px;padding:14px 18px;box-shadow:0 10px 30px rgba(15,61,46,.18),0 0 0 1px rgba(255,255,255,.7) inset;animation:floatCard 7s ease-in-out infinite}
.stat:nth-child(2){margin-right:34px;animation-delay:-2.3s}
.stat:nth-child(3){animation-delay:-4.6s}
.stat .k{font-size:.8rem;font-weight:600;opacity:.75}
.stat .v{font-family:'Sora',sans-serif;font-weight:800;font-size:1.65rem;line-height:1.2}
.stat .s{font-size:.85rem;opacity:.75}
.dot{display:inline-block;width:10px;height:10px;border-radius:50%;margin-right:7px;background:var(--c);animation:dotGlow 2.2s ease-in-out infinite}
.sway-ic{display:inline-block;transform-origin:50% 100%;animation:sway 5s ease-in-out infinite}
.fire{display:inline-block;animation:flicker 1.4s ease-in-out infinite}
.side-tree{text-align:center;font-size:4rem;transform-origin:50% 100%;animation:sway 5s ease-in-out infinite}
.sec{display:flex;align-items:center;gap:14px;margin:2px 0 14px}
.sec-ic{font-size:1.6rem;width:48px;height:48px;display:grid;place-items:center;border-radius:14px;background:linear-gradient(135deg,rgba(46,158,91,.18),rgba(31,181,168,.18))}
.sec h2{margin:0;padding:0;font-size:1.55rem}
.sec p{margin:0;opacity:.7;font-size:.92rem}
[data-baseweb="tab-list"]{gap:6px;background:rgba(255,255,255,.7);padding:6px;border-radius:999px;backdrop-filter:blur(8px);box-shadow:0 6px 20px rgba(15,61,46,.10);width:fit-content;max-width:100%;overflow-x:auto}
button[data-baseweb="tab"]{border-radius:999px;padding:8px 18px;transition:background .2s}
button[data-baseweb="tab"]:hover{background:rgba(46,158,91,.12)}
button[data-baseweb="tab"][aria-selected="true"]{background:linear-gradient(90deg,#2e9e5b,#1fb5a8)}
button[data-baseweb="tab"][aria-selected="true"] p{color:#fff !important}
[data-baseweb="tab-highlight"],[data-baseweb="tab-border"]{display:none}
[data-baseweb="tab-panel"]{background:rgba(255,255,255,.62);border-radius:22px;padding:20px 24px 26px;margin-top:12px;backdrop-filter:blur(6px);box-shadow:0 10px 36px rgba(15,61,46,.10)}
[data-testid="stMetric"]{background:rgba(255,255,255,.85);border:1px solid rgba(46,158,91,.20);border-radius:16px;padding:12px 16px;box-shadow:0 6px 24px rgba(31,181,168,.14)}
[data-testid="stVerticalBlockBorderWrapper"]{border-radius:16px;background:rgba(255,255,255,.78);box-shadow:0 6px 22px rgba(46,158,91,.10)}
[data-testid="stExpander"]{background:rgba(255,255,255,.72);border-radius:14px;border:1px solid rgba(46,158,91,.2)}
button[kind="primary"],button[data-testid="stBaseButton-primary"]{background:linear-gradient(90deg,#2e9e5b,#1fb5a8);border:none;transition:transform .15s,box-shadow .15s}
button[kind="primary"]:hover,button[data-testid="stBaseButton-primary"]:hover{transform:scale(1.03);box-shadow:0 6px 18px rgba(46,158,91,.35)}
.gauge{position:relative;max-width:270px;margin:0 auto;text-align:center}
.gauge svg{width:100%;display:block}
.g-track,.g-fill{fill:none;stroke-width:16;stroke-linecap:round}
.g-track{stroke:rgba(15,61,46,.12)}
.g-fill{stroke-dasharray:251.33;stroke-dashoffset:var(--off);animation:gaugeSweep 1.6s cubic-bezier(.2,.8,.2,1)}
.g-num{position:absolute;left:0;right:0;top:38%;font-weight:800;font-size:2.6rem;line-height:1}
.g-lbl{font-weight:700;margin-top:-4px}
.scale{position:relative;display:flex;height:12px;border-radius:999px;margin:22px 0 4px}
.scale div{height:100%}
.scale div:first-child{border-radius:999px 0 0 999px}
.scale div:nth-child(6){border-radius:0 999px 999px 0}
.mark{position:absolute;top:-18px;left:var(--pos);transform:translateX(-50%);animation:markerSlide 1.6s cubic-bezier(.2,.8,.2,1);font-size:.9rem;line-height:1}
.scale-lbl{display:flex;justify-content:space-between;font-size:.75rem;opacity:.65}
.journey{display:flex;align-items:center;overflow-x:auto;padding:10px 4px 6px}
.step{text-align:center;min-width:84px;opacity:.45;filter:grayscale(1)}
.step.done{opacity:1;filter:none}
.bubble{width:62px;height:62px;margin:0 auto 6px;display:grid;place-items:center;font-size:1.9rem;border-radius:50%;background:rgba(46,158,91,.16)}
.step.now .bubble{background:rgba(46,158,91,.32);animation:ring 2s infinite}
.step .nm{font-weight:700;font-size:.88rem}
.step .xp{font-size:.75rem;opacity:.7}
.line{flex:1;min-width:22px;height:4px;border-radius:4px;background:rgba(15,61,46,.15)}
.line.done{background:linear-gradient(90deg,#2e9e5b,#b7e36a)}
.badge{display:inline-block;margin:0 8px 8px 0;padding:6px 14px;border-radius:999px;font-weight:600;background:rgba(242,177,52,.20);border:1px solid rgba(242,177,52,.6)}
.tag{display:inline-block;margin:0 8px 8px 0;padding:4px 12px;border-radius:999px;font-size:.85rem;font-weight:600;background:rgba(46,158,91,.14)}
.trees{font-size:1.5rem;line-height:1.7;word-break:break-all}
.stApp{color-scheme:light;color:#10372a}
.stApp h1,.stApp h2,.stApp h3,.stApp h4,.stApp p,.stApp li,.stApp label,.stApp [data-testid="stMarkdownContainer"],.stApp [data-testid="stCaptionContainer"],.stApp [data-testid="stMetricLabel"],.stApp [data-testid="stMetricValue"],.stApp [data-testid="stWidgetLabel"] p,[data-testid="stSidebar"] *{color:#10372a}
.stApp button[kind="primary"] p,.stApp button[data-testid="stBaseButton-primary"] p{color:#fff}
.stApp input,.stApp textarea{color:#10372a !important;background:#fff !important}
.stApp [data-baseweb="select"]>div,.stApp [data-baseweb="input"],.stApp [data-baseweb="base-input"]{background:#fff;color:#10372a}
@media (max-width:800px){.eco-hero{grid-template-columns:1fr;padding:28px 22px 170px}.eco-h{font-size:2.1rem}.eco-cards{align-items:stretch}.stat{width:100%}.stat:nth-child(2){margin-right:0}[data-baseweb="tab-panel"]{padding:14px 12px 20px}}
@media (prefers-reduced-motion:reduce){*,*::before,*::after{animation:none !important;transition:none !important}}
</style>
"""

CSS = _CSS.replace("__HILLS__", HILLS).replace("__PATTERN__", PATTERN)