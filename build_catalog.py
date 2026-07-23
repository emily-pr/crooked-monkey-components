"""build_catalog.py — Crooked Monkey component catalog.

A visual, browsable library that also shows how to CALL each component. It extends
the pattern from build_styleguide.py: everything is sourced from cm_kit.py (tokens +
component *_css()/render helpers), and the output is fully self-contained HTML
(only external dependency: Google Fonts — Poppins 900 + Inter).

The whole catalog is driven by ONE list: REGISTRY (bottom of file). Each entry is a
component descriptor; the build loop turns it into (a) a card on the index page and
(b) its own per-component page — automatically. Add an entry -> a card + page appear.

    python3 build_catalog.py     # writes index.html + one <slug>.html per component

See README.md -> "Add a component" for the full one-step flow.
"""
import os, html, re
import cm_kit as cm

_HERE = os.path.dirname(os.path.abspath(__file__))
def _asset(name):
    return os.path.join(_HERE, "assets", name)

esc = html.escape

# Cream logo, inlined as a data URI for the nav/footer demos (keeps output self-contained).
_logo_svg = open(_asset("cm_logo_cream.svg")).read()
import urllib.parse, json
LOGO_URI = "data:image/svg+xml," + urllib.parse.quote(_logo_svg, safe="")
IMG = json.load(open(_asset("imgs.json")))        # product photos as data URIs
MONKEY = open(_asset("monkey_inner.svg")).read()  # brand mark inner markup

# Bright surface -> matching deep accent (design-system: deep accent = text on that bright).
DEEP = {"yellow": "yellow-deep", "blue": "blue-deep", "pink": "pink-deep", "mint": "mint-deep"}

# One color per atomic tier, so every card in a section reads as a set.
# (TOKENS lives on its own collection page, so sharing pink with TEMPLATE never
# collides — Atoms/Molecules/Organisms/Templates are all distinct on a page.)
TIER_COLOR = {"TOKENS": "pink", "ATOM": "blue", "MOLECULE": "mint",
              "ORGANISM": "yellow", "TEMPLATE": "pink"}
def tier_color(eyebrow):
    return TIER_COLOR.get(eyebrow, "blue")

def entry_call(e):
    """The primary cm.* call for a component (or the page function for templates)."""
    if e["slug"].startswith("template-"):
        return "render_brand_page(config)"
    calls = []
    for _lab, snippet in e.get("api", []):
        calls += re.findall(r'cm\.[a-z_]+', snippet)
    pick = [c for c in calls if not c.endswith("_css")] or calls  # prefer the render helper
    return (pick[0] + "(…)") if pick else None

# ---------------------------------------------------------------------------
# Page chrome (layout CSS lives in the build script; tokens+components in the kit)
# ---------------------------------------------------------------------------
BASE_CSS = """
*{box-sizing:border-box;margin:0}
body{background:var(--bg);color:var(--fg);font-family:Inter,system-ui,sans-serif;-webkit-font-smoothing:antialiased;line-height:1.5}
a{color:inherit}
img{display:block;max-width:100%}
.top{position:sticky;top:0;z-index:20;background:var(--ink);color:var(--cream);display:flex;align-items:baseline;gap:16px;flex-wrap:wrap;padding:18px clamp(20px,5vw,64px)}
.top .brand{font-family:Poppins,sans-serif;font-weight:900;font-size:19px;letter-spacing:-.01em;color:var(--cream);text-decoration:none}
.top .brand:hover{color:var(--yellow)}
.top .tag{font-size:12px;letter-spacing:.16em;text-transform:uppercase;opacity:.7}
.wrap{max-width:1180px;margin:0 auto;padding:clamp(40px,6vw,80px) clamp(20px,5vw,64px) clamp(80px,10vw,140px)}
.eyebrow{font-size:13px;font-weight:800;letter-spacing:.16em;text-transform:uppercase;color:rgba(4,18,2,.5)}
.h-display{font-family:Poppins,sans-serif;font-weight:900;text-transform:uppercase;letter-spacing:-.02em;line-height:.98;color:var(--ink)}

/* ---- Index: hero + card grid (modelled on the brand's card-grid nav) ---- */
.hero{max-width:52ch;margin-bottom:clamp(40px,6vw,72px)}
.hero h1{font-size:clamp(44px,7vw,96px)}
.hero .lead{margin-top:22px;font:500 clamp(16px,1.4vw,20px)/1.55 Inter;color:rgba(4,18,2,.66);max-width:44ch}
.cat-group{margin-top:clamp(36px,5vw,56px)}
.cat-group > h2{font-size:clamp(22px,2.4vw,30px);margin-bottom:20px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(272px,1fr));gap:clamp(16px,1.8vw,26px)}
.grid-lg{grid-template-columns:repeat(auto-fill,minmax(320px,1fr))}
.col-card{min-height:300px}
.col-card .c-title{font-size:clamp(28px,2.8vw,40px)}
.p-pages{margin-top:16px;font:600 13px/1.4 Inter;color:rgba(4,18,2,.55)}
.p-pages a{color:var(--ink);text-decoration:underline;text-underline-offset:3px}
.p-handle{display:flex;flex-wrap:wrap;align-items:center;gap:10px;margin-top:18px}
.p-handle .lab{font:700 11px/1 Inter;letter-spacing:.14em;text-transform:uppercase;color:rgba(4,18,2,.5)}
.p-handle code{background:var(--ink);color:var(--cream);border-radius:8px;padding:8px 12px;font:600 14px/1 ui-monospace,SFMono-Regular,Menlo,monospace}
.p-handle .call{background:rgba(4,18,2,.07);color:var(--ink);border-radius:8px;padding:8px 12px;font:600 13px/1 ui-monospace,SFMono-Regular,Menlo,monospace}
.card{position:relative;display:flex;flex-direction:column;min-height:230px;border-radius:var(--r-card-lg);padding:clamp(22px,2vw,30px);text-decoration:none;color:var(--ink);overflow:hidden;transition:transform .22s cubic-bezier(.2,.75,.2,1),box-shadow .22s ease}
.card:hover{transform:translateY(-5px) rotate(-1deg);box-shadow:0 30px 50px -30px rgba(4,18,2,.5)}
.card:focus-visible{outline:3px solid var(--ink);outline-offset:3px}
.card .c-eyebrow{font-size:12px;font-weight:800;letter-spacing:.16em;text-transform:uppercase}
.card .c-title{font-family:Poppins,sans-serif;font-weight:900;text-transform:uppercase;letter-spacing:-.02em;line-height:1.0;font-size:clamp(24px,2.3vw,32px);margin-top:12px;color:var(--ink)}
.card .c-blurb{margin-top:12px;font:500 14.5px/1.5 Inter;color:rgba(4,18,2,.72);max-width:34ch}
.card .c-go{margin-top:auto;padding-top:18px;font:800 12px/1 Inter;letter-spacing:.14em;text-transform:uppercase;display:inline-flex;align-items:center;gap:8px}
.card .c-go .ar{transition:transform .22s ease}
.card:hover .c-go .ar{transform:translateX(5px)}

/* ---- Component page ---- */
.back{display:inline-flex;align-items:center;gap:8px;font:800 12px/1 Inter;letter-spacing:.14em;text-transform:uppercase;color:rgba(4,18,2,.6);text-decoration:none;margin-bottom:clamp(26px,4vw,44px)}
.back:hover{color:var(--ink)}
.p-head{margin-bottom:clamp(36px,5vw,60px);max-width:60ch}
.p-head h1{font-size:clamp(38px,5.2vw,72px);margin-top:12px}
.p-head .lead{margin-top:18px;font:500 clamp(16px,1.3vw,19px)/1.55 Inter;color:rgba(4,18,2,.66)}
.sect{padding-top:clamp(34px,4.5vw,54px);margin-top:clamp(34px,4.5vw,54px);border-top:1.5px solid rgba(4,18,2,.12)}
.sect-lab{font-size:13px;font-weight:800;letter-spacing:.16em;text-transform:uppercase;color:rgba(4,18,2,.5);margin-bottom:6px}
.sect > h2{font-family:Poppins,sans-serif;font-weight:900;text-transform:uppercase;letter-spacing:-.02em;font-size:clamp(24px,2.6vw,34px);margin-bottom:24px;color:var(--ink)}

/* demo canvas */
.demo{background:#fff;border:1.5px solid rgba(4,18,2,.14);border-radius:var(--r-card);padding:clamp(24px,3vw,40px);display:flex;flex-wrap:wrap;gap:clamp(18px,2vw,32px);align-items:flex-start}
.demo.col{flex-direction:column;align-items:stretch}
.demo.pad0{padding:0;overflow:hidden}
.demo.bleed{padding:0;display:block;overflow:hidden;background:transparent}
.demo-iframe{width:100%;height:660px;border:0;display:block;background:var(--cream)}
.demo-item{display:flex;flex-direction:column;gap:10px}
.demo-item .cap{font:700 11px/1 Inter;letter-spacing:.13em;text-transform:uppercase;color:rgba(4,18,2,.5)}

/* specimens (tokens) */
.g-sw{display:grid;grid-template-columns:repeat(auto-fill,minmax(128px,1fr));gap:16px;width:100%}
.sw .chip{height:74px;border-radius:12px;border:1px solid rgba(4,18,2,.08)}
.sw-n{font:600 13px/1.3 Inter;margin-top:8px}
.sw-h{font-size:12px;color:rgba(4,18,2,.55);font-variant-numeric:tabular-nums}
.g-pair{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:16px;width:100%}
.pair{border-radius:16px;padding:20px;min-height:118px;display:flex;flex-direction:column;justify-content:space-between}
.pair-deep{font-family:Poppins,sans-serif;font-weight:900;font-size:34px;line-height:1}
.pair-lab{font-size:12px;font-weight:600}
.trow{display:grid;grid-template-columns:190px 1fr;gap:20px;align-items:baseline;padding-block:16px;border-top:1px solid rgba(4,18,2,.08);width:100%}
.trow:first-child{border-top:0}
.tmeta{display:flex;flex-direction:column;gap:3px}
.tname{font-weight:700;font-size:14px}
.tspec{font-size:12px;color:rgba(4,18,2,.55)}
.tsample{color:var(--ink);overflow:hidden}
.srow{display:flex;align-items:center;gap:14px;margin-bottom:8px;width:100%}
.sbar{height:16px;background:var(--pink);border-radius:3px}
.slab{font-size:12px;color:rgba(4,18,2,.6);font-variant-numeric:tabular-nums}
.g-r{display:grid;grid-template-columns:repeat(auto-fill,minmax(128px,1fr));gap:16px;width:100%}
.rbox .rsq{height:80px;background:var(--blue);border:1.5px solid var(--ink)}

/* notch demo helpers */
.nc-demo{color:var(--ink);min-height:150px;width:230px}
.nc-pad{padding:22px 48px}
.nc-k{font-family:Poppins,sans-serif;font-weight:900;font-size:28px;line-height:1}
.nc-h{font-size:16px;font-weight:700;margin-top:8px}
.nc-b{font-size:13px;opacity:.72;margin-top:6px;line-height:1.4}

/* nav demo sits in-flow (production nav is position:fixed) */
.demo-nav{width:100%;border-radius:var(--r-card);overflow:hidden;border:1.5px solid rgba(4,18,2,.14)}

/* code block */
.code{position:relative;background:var(--ink);color:var(--cream);border-radius:var(--r-card);padding:22px 24px;margin-top:16px;overflow-x:auto}
.code pre{margin:0;font:500 13.5px/1.7 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;white-space:pre;color:var(--cream)}
.code .tok-c{color:rgba(253,249,234,.5)}
.code-copy{position:absolute;top:12px;right:12px;background:rgba(253,249,234,.1);color:var(--cream);border:0;border-radius:999px;padding:7px 14px;font:700 11px/1 Inter;letter-spacing:.1em;text-transform:uppercase;cursor:pointer;transition:background .18s ease}
.code-copy:hover{background:rgba(253,249,234,.2)}
.code-copy:focus-visible{outline:2px solid var(--yellow);outline-offset:2px}
.code-lab{font:700 11px/1 Inter;letter-spacing:.13em;text-transform:uppercase;color:rgba(4,18,2,.5);margin:22px 0 0}

/* notes */
.notes{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:16px;max-width:70ch}
.notes li{position:relative;padding-left:26px;font:500 15.5px/1.6 Inter;color:rgba(4,18,2,.8)}
.notes li::before{content:"";position:absolute;left:0;top:.55em;width:12px;height:12px;border-radius:3px;background:var(--pink)}
.notes li b{font-weight:700;color:var(--ink)}
.notes code{background:rgba(4,18,2,.08);border-radius:6px;padding:2px 7px;font:600 13.5px/1 ui-monospace,SFMono-Regular,Menlo,monospace}

@media (prefers-reduced-motion:reduce){
  *{transition:none!important;animation:none!important}
  .card:hover{transform:none}
}
@media (max-width:620px){.trow{grid-template-columns:1fr;gap:8px}}
"""

COPY_JS = (
    "[].slice.call(document.querySelectorAll('.code-copy')).forEach(function(b){"
    "b.addEventListener('click',function(){var c=b.closest('.code').querySelector('pre');"
    "var t=c.innerText;if(navigator.clipboard){navigator.clipboard.writeText(t);}"
    "var o=b.textContent;b.textContent='Copied';setTimeout(function(){b.textContent=o;},1400);});});"
)

def topbar():
    return ('<header class="top"><a class="brand" href="index.html">CROOKED MONKEY</a>'
            '<span class="tag">Component Library</span></header>')

def page(title, body, extra_css="", extra_js=""):
    return ("<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\">"
            "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
            "<title>" + esc(title) + " — Crooked Monkey Components</title>"
            "<link rel=\"preconnect\" href=\"https://fonts.googleapis.com\">"
            "<link rel=\"preconnect\" href=\"https://fonts.gstatic.com\" crossorigin>"
            "<link href=\"https://fonts.googleapis.com/css2?family=Poppins:wght@900&"
            "family=Inter:wght@400;500;600;700;800&display=swap\" rel=\"stylesheet\">"
            "<style>" + cm.root_css() + BASE_CSS + extra_css + "</style></head><body>"
            + topbar() + body
            + "<script>(function(){" + COPY_JS + extra_js + "})();</script>"
            "</body></html>")

def code(snippet, lang_lab="python"):
    """Render an escaped, copyable code block."""
    return ('<div class="code"><button class="code-copy" type="button" '
            'aria-label="Copy code">Copy</button><pre>' + esc(snippet) + '</pre></div>')

def code_lab(text):
    return '<p class="code-lab">' + esc(text) + '</p>'

# ---------------------------------------------------------------------------
# Specimen builders (tokens) — adapted from build_styleguide.py
# ---------------------------------------------------------------------------
def swatch(name, hexv):
    return (f'<div class="sw"><div class="chip" style="background:{hexv}"></div>'
            f'<div class="sw-n">--{name}</div><div class="sw-h">{hexv}</div></div>')

def pair(b, bh, d, dh):
    return (f'<div class="pair" style="background:{bh}">'
            f'<div class="pair-deep" style="color:{dh}">Aa</div>'
            f'<div class="pair-lab" style="color:{dh}">--{b} + --{d}</div></div>')

def type_row(name, size, fam, wt, tr, sample):
    return (f'<div class="trow"><div class="tmeta"><span class="tname">{name}</span>'
            f'<span class="tspec">{fam.split(",")[0]} {wt} · {size}</span></div>'
            f'<div class="tsample" style="font-family:{fam};font-weight:{wt};'
            f'font-size:{size};letter-spacing:{tr};line-height:1.05">{sample}</div></div>')

def space_row(v):
    return (f'<div class="srow"><div class="sbar" style="width:{min(v,120)*2}px"></div>'
            f'<span class="slab">{v}px</span></div>')

def radius_box(name, val):
    return (f'<div class="rbox"><div class="rsq" style="border-radius:{val}"></div>'
            f'<div class="sw-n">--{name}</div><div class="sw-h">{val}</div></div>')

# ---------------------------------------------------------------------------
# Per-component demo builders. Each returns (demo_html, css, js).
# ---------------------------------------------------------------------------
def demo_item(cap, inner):
    return f'<div class="demo-item"><div class="cap">{esc(cap)}</div>{inner}</div>'

def build_color():
    prim = "".join(swatch(n, h) for n, h in [
        ("cream", "#FDF9EA"), ("ink", "#041202"), ("yellow", "#FBF79E"),
        ("blue", "#94DFFA"), ("pink", "#F580B1"), ("mint", "#6EE8BE")])
    pairs = "".join(pair(*b) for b in [
        ("yellow", "#FBF79E", "yellow-deep", "#474400"),
        ("blue", "#94DFFA", "blue-deep", "#003547"),
        ("pink", "#F580B1", "pink-deep", "#47001E"),
        ("mint", "#6EE8BE", "mint-deep", "#05432D")])
    demo = ('<div class="demo col">'
            '<div class="cap">Primitives</div><div class="g-sw">' + prim + '</div>'
            '<div class="cap" style="margin-top:8px">Bright + deep-accent pairs '
            '(deep accent = title/link on that surface; body text stays ink)</div>'
            '<div class="g-pair">' + pairs + '</div></div>')
    return demo, "", ""

def build_type():
    TYPE = [("Display XL", "clamp(30px,6vw,72px)", "Poppins,sans-serif", "900", "-.02em", "BRANDED SWAG"),
            ("Display L", "clamp(26px,4vw,52px)", "Poppins,sans-serif", "900", "-.02em", "How it works"),
            ("Heading", "clamp(22px,3vw,34px)", "Poppins,sans-serif", "900", "-.02em", "We kit, store &amp; ship"),
            ("Subhead", "clamp(17px,2vw,24px)", "Inter,sans-serif", "600", "0", "Mocks back in one business day."),
            ("Body", "16px", "Inter,sans-serif", "400", "0", "Quote in 30 minutes; we'll recommend blanks."),
            ("Label", "13px", "Inter,sans-serif", "700", ".14em", "MARKETING &amp; BRAND TEAMS")]
    demo = '<div class="demo col">' + "".join(type_row(*t) for t in TYPE) + '</div>'
    return demo, "", ""

def build_space():
    demo = '<div class="demo col">' + "".join(space_row(v) for v in
           [4, 8, 12, 16, 20, 24, 32, 40, 56, 64, 72, 96, 120]) + '</div>'
    return demo, "", ""

def build_radius():
    RADII = [("r-pill", "999px"), ("r-card-lg", "40px"), ("r-card", "24px"),
             ("r-sm", "10px"), ("r-flat", "6px")]
    demo = '<div class="demo"><div class="g-r">' + "".join(radius_box(n, v) for n, v in RADII) + '</div></div>'
    return demo, "", ""

def _nc_inner(num, head, body):
    return (f'<div class="nc-pad"><div class="nc-k">{num}</div>'
            f'<h4 class="nc-h">{head}</h4><p class="nc-b">{body}</p></div>')

def build_notch():
    inner = _nc_inner("03", "We produce in-house", "Screen print, embroidery, DTG.")
    r = cm.notch_card(inner=inner, side="r", bg="var(--blue)", cls="nc-demo")
    l = cm.notch_card(inner=_nc_inner("02", "We design your art", "PMS-matched, retail-grade."),
                      side="l", bg="var(--mint)", cls="nc-demo")
    b = cm.notch_card(inner=_nc_inner("01", "Tell us what you need", "Quote in 30 minutes."),
                      side="both", bg="var(--pink)", cls="nc-demo")
    tall = ('<article class="k-fill" style="background:var(--yellow);width:230px;height:300px;color:var(--ink)">'
            + _nc_inner("H", "Fill height mode", "notch_h=\"100%\" — the cut runs edge-to-edge; "
            "depth stays fixed so it never ovalizes on tall cards.") + '</article>')
    demo = ('<div class="demo">'
            + demo_item('side="r" (fixed height)', r)
            + demo_item('side="l" (fixed height)', l)
            + demo_item('side="both" (fixed height)', b)
            + demo_item('notch_h="100%" (fill height)', tall)
            + '</div>')
    css = cm.notch_css() + cm.notch_layer_css(".k-fill", "r", notch_h="100%")
    return demo, css, ""

def build_button():
    demo = ('<div class="demo">' + cm.button("Request a quote", variant="primary")
            + cm.button("See all services", variant="outline") + '</div>')
    return demo, cm.button_css(), ""

def build_pill():
    demo = ('<div class="demo">' + cm.pill("PATAGONIA") + cm.pill("YETI")
            + cm.pill("LULULEMON", bg="var(--blue)") + cm.pill("STANLEY", bg="var(--mint)") + '</div>')
    return demo, cm.pill_css(), ""

def build_input():
    demo = ('<div class="demo col">'
            + cm.field("Email", name="email", type="email", placeholder="you@company.com")
            + cm.field("Company", name="company", placeholder="Company or org") + '</div>')
    return demo, cm.input_css(), ""

def build_faq():
    items = [("What is the minimum order for custom merch?",
              "MOQs vary by item: apparel from 25 pieces, hard goods from 50, swag kits from 25 boxes."),
             ("How fast can you produce custom merch?",
              "Standard production runs about two weeks after art approval; rush is 5 business days or less."),
             ("Can you match my exact brand colors?",
              "Yes — we PMS-match colors and proof every decoration method, so the mock is what ships.")]
    demo = '<div class="demo col">' + cm.faq(items) + '</div>'
    return demo, cm.faq_css(), cm.faq_js()

def build_nav():
    demo = ('<div class="demo pad0"><div class="demo-nav">' + cm.nav(
        LOGO_URI,
        links=["Products"],
        services=["Custom Screen Printing", "Embroidery & DTG", "Cut & Sew Manufacturing"],
        brands=["Patagonia", "YETI", "Lululemon", "The North Face"],
    ) + '</div></div>')
    # In-flow override for the demo (production nav is position:fixed).
    css = cm.nav_css() + ".demo-nav .cm-nav{position:static}"
    return demo, css, cm.nav_js()

# ---- new atoms ----
def build_eyebrow():
    demo = ('<div class="demo">' + cm.eyebrow("COMPONENT")
            + cm.eyebrow("TOKENS", color="var(--pink-deep)") + cm.eyebrow("New · 2026") + '</div>')
    return demo, cm.eyebrow_css(), ""

def build_arrow():
    demo = ('<div class="demo">' + cm.arrow_link("Browse premium brands")
            + cm.arrow_link("See all services", color="var(--blue-deep)") + '</div>')
    return demo, cm.arrow_css(), ""

def build_badge():
    demo = ('<div class="demo">' + cm.badge(MONKEY, size="150px")
            + cm.badge(MONKEY, size="96px", spin=False) + '</div>')
    return demo, cm.badge_css(), ""

# ---- new molecules ----
def build_heading():
    demo = ('<div class="demo col">' + cm.heading(
        "Custom merch services<br>for every format", eyebrow="What we do",
        sub="Six buyer-intent categories, each linking into a leaf service page with scope and minimums.") + '</div>')
    return demo, cm.heading_css(), ""

def build_media():
    demo = ('<div class="demo">'
            + cm.media_card(IMG["chief"], "Marketing & Brand Teams",
                            "Campaign launches and client gifts that look retail-quality.",
                            eyebrow="Buyer type", accent="var(--yellow)", link="Learn more")
            + cm.media_card(IMG["sonoma"], "HR & People Teams",
                            "Onboarding kits and culture swag people actually keep.",
                            eyebrow="Buyer type", accent="var(--mint)")
            + '</div>')
    return demo, cm.media_css(), ""

def build_feature():
    demo = ('<div class="demo">'
            + cm.feature_card("01", "Tell us what you need",
                              "Quote in 30 minutes; we recommend blanks and a timeline.", side="r", bg="var(--blue)")
            + cm.feature_card("02", "We design your art",
                              "Mocks back in one business day. PMS-matched.", side="l", bg="var(--mint)")
            + '</div>')
    return demo, cm.feature_css(), ""

def build_checklist():
    demo = ('<div class="demo">' + cm.checklist(
        ["Reply within 1 business hour", "Dedicated account rep", "No commitment to quote"]) + '</div>')
    return demo, cm.check_css(), ""

def build_pillgroup():
    demo = ('<div class="demo">' + cm.pill_group(
        ["Patagonia", "YETI", "Lululemon", "The North Face", "Stanley", "Cotopaxi"]) + '</div>')
    return demo, cm.pill_css() + cm.pillgroup_css(), ""

def build_level():
    demo = ('<div class="demo bleed" style="padding:clamp(18px,3vw,32px);background:#fff">'
            + cm.level_card("01 / 04", "Decorate", "Print, embroider, DTG on premium blanks",
              "Screen printing, embroidery, DTG, sublimation, and laser etch — all in-house at every US studio.",
              "Screen printing", IMG["chief"], color="blue") + '</div>')
    return demo, cm.level_css(), ""

# ---- new organisms ----
def build_hero():
    demo = ('<div class="demo bleed">' + cm.hero(
        'CUSTOM MERCH &amp;<br><span class="cm-hero-hl">BRANDED SWAG</span><br>FOR COMPANIES AND TEAMS',
        "Crooked Monkey is a full-service custom merch agency. In-house screen printing, embroidery and DTG; "
        "design, kitting, fulfillment, and premium retail brands — shipped from studios across the US.") + '</div>')
    return demo, cm.hero_css(), ""

def build_services():
    items = [
        (IMG["chief"], "Fully Custom Branded Merch", "Unique pieces, built from scratch.", "Cut &amp; sew", "yellow"),
        (IMG["hoodie"], "Swag Storage, Kitting &amp; Distribution", "Stored, kitted and shipped worldwide.", "Swag fulfillment", "blue"),
        (IMG["duffel"], "Merch Design That Elevates Your Brand", "Your brand, on every detail.", "Design &amp; packaging", "pink"),
        (IMG["sonoma"], "Custom Employee &amp; Client Swag Kits", "Curated unboxing, delivered.", "Custom swag kits", "mint"),
    ]
    demo = '<div class="demo col">' + cm.services_grid(items) + '</div>'
    return demo, cm.service_css(), ""

def build_premium():
    demo = ('<div class="demo bleed">' + cm.premium_section(
        'PREMIUM RETAIL<br>BRANDS YOU CAN<br><span class="acc">CO-BRAND</span>',
        "We partner with a wide selection of premium retail brands so your merch feels bought, not made.",
        ["Patagonia", "YETI", "Lululemon", "The North Face", "Under Armour", "Stanley",
         "Hydro Flask", "Cotopaxi", "Carhartt", "Herschel"]) + '</div>')
    return demo, cm.premium_css(), ""

def build_faqsection():
    items = [
        ("What is the minimum order for custom merch?", "MOQs vary by item: apparel from 25 pieces, hard goods from 50, swag kits from 25 boxes."),
        ("How fast can you produce custom merch?", "Standard production runs about two weeks after art approval; rush is 5 business days or less."),
        ("Can you match my exact brand colors?", "Yes — we PMS-match colors and proof every decoration method."),
        ("Do you ship internationally?", "Yes, we ship worldwide and can stage inventory regionally to cut transit time."),
    ]
    demo = ('<div class="demo bleed">'
            + cm.faq_section('CUSTOM<br>MERCH <span class="pink">FAQ.</span>', items) + '</div>')
    return demo, cm.faqsection_css(), cm.faq_js()

def build_form():
    demo = ('<div class="demo bleed" style="padding:clamp(20px,3vw,40px);background:var(--cream)">'
            + cm.contact_form() + '</div>')
    return demo, cm.form_css(), cm.form_js()

def build_footer():
    demo = '<div class="demo bleed">' + cm.footer(LOGO_URI) + '</div>'
    return demo, cm.footer_css(), ""

def build_ticker():
    demo = ('<div class="demo bleed">' + cm.ticker(
        [IMG["chief"], IMG["hoodie"], IMG["duffel"], IMG["sonoma"]]) + '</div>')
    return demo, cm.ticker_css(), ""

def build_gallery():
    demo = ('<div class="demo bleed">' + cm.gallery(
        ["Transforming", "Companies", "Into Brands"],
        [IMG["chief"], IMG["hoodie"], IMG["duffel"], IMG["sonoma"], IMG["chief"], IMG["sonoma"]]) + '</div>')
    return demo, cm.gallery_css(), ""

def build_fourlevels():
    levels = [
        ("01 / 04", "Decorate", "Print, embroider, DTG on premium blanks",
         "Screen printing, embroidery, DTG, sublimation, and laser etch — all in-house.", "Screen printing", IMG["chief"], "blue"),
        ("02 / 04", "Co-Brand", "Your logo on Patagonia, YETI, Lululemon",
         "Add your mark to the brands your team already wears.", "Browse premium brands", IMG["hoodie"], "yellow"),
        ("03 / 04", "Dupe", "Recreate a retail favorite, your way",
         "Your fabric, your fit, your finish — without the licensing.", "See custom dupes", IMG["sonoma"], "mint"),
        ("04 / 04", "Cut &amp; Sew", "Designed from a flat pattern",
         "Custom hats, hoodies, jackets, bags — built from scratch.", "Cut &amp; sew", IMG["duffel"], "pink"),
    ]
    demo = ('<div class="demo bleed" style="padding:clamp(18px,3vw,32px);background:#fff">'
            + cm.four_levels('<span class="hl">Four</span> Levels Of Custom',
              "Most agencies stop at level one. We go all the way to pattern-up cut & sew when the project deserves it.",
              levels) + '</div>')
    return demo, cm.level_css(), ""

def build_hiw():
    steps = [
        ("01", "Tell us what you need", "Quote in 30 minutes; we recommend blanks, methods, and a realistic timeline."),
        ("02", "We design or polish your art", "Mocks back in one business day. PMS-matched, retail-grade finishes."),
        ("03", "We produce in-house at a US studio", "Screen print, embroidery, DTG, sublimation. Standard 2 weeks; rush 5 days."),
        ("04", "We kit, store, and ship", "Drop-ship to homes, stage in our warehouses, or stand up a swag shop."),
    ]
    demo = ('<div class="demo bleed" style="padding:clamp(28px,4vw,52px);background:var(--cream)">'
            + cm.how_it_works(steps, monkey_svg=MONKEY) + '</div>')
    return demo, cm.hiw_css(), ""

def build_who():
    items = [
        ("Marketing & Brand Teams", "var(--yellow)", IMG["chief"], "Campaign launches, conference giveaways, and client gifts that look retail-quality."),
        ("Founders & Ops Leaders", "var(--blue)", IMG["duffel"], "Investor kits, all-hands swag, and milestone drops that punch above your headcount."),
        ("HR & People Teams", "var(--mint)", IMG["sonoma"], "Onboarding kits, work anniversaries, and culture swag people actually keep."),
        ("Agencies", "var(--pink)", IMG["hoodie"], "White-label production and client-ready merch you can put your own name on."),
    ]
    demo = ('<div class="demo bleed" style="padding:clamp(28px,4vw,52px);background:#fff">'
            + cm.who_section(items) + '</div>')
    return demo, cm.who_css(), cm.who_js()

# ---- template ----
def build_landing():
    demo = ('<div class="demo bleed"><iframe class="demo-iframe" src="preview-landing.html" '
            'title="Landing page template preview" loading="lazy"></iframe></div>')
    return demo, "", ""

# ---- premium-brands page builders ----
_IC = {
 "clock": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>',
 "box": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3l8 4.5v9L12 21l-8-4.5v-9L12 3z"/><path d="M12 12l8-4.5M12 12v9M12 12L4 7.5"/></svg>',
 "needle": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="9" r="5"/><path d="M9 13l-1.5 8L12 18l4.5 3L15 13"/></svg>',
 "bolt": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M13 3L4 14h7l-1 7 9-11h-7l1-7z"/></svg>',
 "gift": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="9" width="16" height="12" rx="1"/><path d="M4 13h16M12 9v12M12 9S10 4 7.5 5.5 9 9 12 9zM12 9s2-5 4.5-3.5S15 9 12 9z"/></svg>',
 "brief": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="7" width="18" height="13" rx="2"/><path d="M8 7V5a2 2 0 012-2h4a2 2 0 012 2v2"/></svg>',
 "users": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="9" cy="8" r="3"/><path d="M3 20a6 6 0 0112 0M16 5.5a3 3 0 010 5.8M21 20a6 6 0 00-4-5.6"/></svg>',
 "note": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="5" width="18" height="13" rx="2"/><path d="M7 9.5h10M7 13.5h6"/></svg>',
 "history": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 12a9 9 0 1 0 3-6.7L3 8"/><path d="M3 4v4h4"/><path d="M12 8v4l3 2"/></svg>',
 "heart": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 20s-7-4.5-9.5-9A5 5 0 0112 5a5 5 0 019.5 6c-2.5 4.5-9.5 9-9.5 9z"/></svg>',
 "trophy": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M7 4h10v4a5 5 0 01-10 0V4z"/><path d="M7 6H4v1a3 3 0 003 3M17 6h3v1a3 3 0 01-3 3M9 20h6M12 15v5"/></svg>',
 "shield": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3l7 3v5c0 4.4-3 7.6-7 9-4-1.4-7-4.6-7-9V6l7-3z"/></svg>',
 "flag": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 21V4M5 4h12l-2.5 4L17 12H5"/></svg>',
}

def build_brand_hero():
    demo = ('<div class="demo bleed">' + cm.brand_hero(
        '<span class="hl">Custom Patagonia</span> Embroidered<br>Apparel for Corporate Gifts',
        "Embroidery and patch decoration on every piece in Patagonia's catalog — fleece, softshells, hats, bags. "
        "Decorated in-house, the way the brand was meant to be.",
        [IMG["pat01"], IMG["pat02"], IMG["pat03"], IMG["pat04"]]) + '</div>')
    return demo, cm.brand_hero_css(), ""

def build_stat_strip():
    items = [(_IC["clock"], "Lead time", "5–8 days"), (_IC["box"], "Min. order", "12 pieces"),
             (_IC["needle"], "Signature", "Embroidery"), (_IC["bolt"], "Rush avail.", "3–5 days")]
    demo = '<div class="demo bleed">' + cm.stat_strip(items) + '</div>'
    return demo, cm.stat_strip_css(), ""

def build_statement():
    demo = ('<div class="demo bleed">' + cm.statement_band(
        "Why Custom Patagonia", "The brand your team actually wears.",
        ["If you own Patagonia, you know they're made to perfection — but they're not made for customization.",
         "Our team has worked hard to master the best embroidery techniques for each item in Patagonia's inventory."],
        IMG["pat04"],
        quote="&ldquo;Honestly the best embroidery work we've seen on Patagonia. Our whole team noticed.&rdquo;",
        cite="Dana K. · Head of People, Sonos", alt="Patagonia embroidery detail") + '</div>')
    return demo, cm.statement_css(), ""

def build_photo_card():
    items = [(IMG["pat01"], "Fleece &amp; Softshells", "Better Sweater, Synchilla, Retro-X, Nano Puff — the lineup on every corporate gift list.", "mint"),
             (IMG["pat02"], "Headwear &amp; Bags", "P-6 trucker hats, beanies, Black Hole bags. Tight registration on technical fabrics.", "blue"),
             (IMG["pat03"], "Tees &amp; Hoodies", "Responsibili-Tees, Uprisal hoodies. Water-based inks that match the brand's ethos.", "pink")]
    demo = '<div class="demo col">' + cm.photo_grid(items) + '</div>'
    return demo, cm.photo_card_css(), ""

def build_usecase():
    items = [(_IC["gift"], "Client gifts"), (_IC["brief"], "Executive merch"),
             (_IC["box"], "Onboarding kits"), (_IC["users"], "Field &amp; event teams")]
    demo = ('<div class="demo bleed" style="background:var(--ink);padding:clamp(28px,4vw,52px)">'
            + cm.usecase_grid(items) + '</div>')
    return demo, cm.usecase_css(), ""

def build_decoration():
    items = [
        (IMG["pat01"], "Embroidery", "Thread-stitched logos with tight digitizing. Our default for fleece and softshells.",
         ["Up to 15,000 stitches standard", "Metallic + tonal thread", "3D puff on demand"], "yellow", "Signature"),
        (IMG["pat04"], "Woven Patches", "Leather, felt, PVC, or fully-woven patches applied via heat or stitch.",
         ["Leather, felt, PVC, woven", "Stitch or heat-applied", "Rush-sampling available"], "mint", None),
        (IMG["pat03"], "Laser Etch", "Subtle, permanent, eye-catching on waxed canvas, leather, and synthetics.",
         ["Waxed canvas + leather", "Zero-ink, permanent", "Tonal, understated finish"], "blue", "New"),
        (IMG["pat02"], "Screen Print", "For tees, hoodies, and anywhere embroidery is too much.",
         ["Up to 6 colors", "Water-based + discharge inks", "Puff, metallic, glow"], "pink", None),
    ]
    demo = '<div class="demo col">' + cm.decoration_grid(items) + '</div>'
    return demo, cm.decoration_css(), ""

def build_product():
    items = [
        (IMG["pat01"], "Better Sweater Jacket", "Fleece", "from $139", ["#2b2b2b", "#a99b7d", "#d9d2c4"]),
        (IMG["pat02"], "Better Sweater Vest", "Vest", "from $119", ["#586460", "#9aa3a0", "#e4ded0"]),
        (IMG["pat03"], "Torrentshell 3L Jacket", "Jacket", "from $179", ["#1e3d52", "#20232a", "#7a2230"]),
        (IMG["pat04"], "Lightweight Synchilla Snap-T", "Quarter-zip", "from $129", ["#3e6b4e", "#c9b783", "#22303f"]),
    ]
    demo = '<div class="demo col">' + cm.product_grid(items) + '</div>'
    return demo, cm.product_css(), ""

def build_process():
    steps4 = [
        ("01", "Quote", "24 hr reply", "Tell us what you want. We come back with pricing, lead time, and honest recommendations."),
        ("02", "Sample", "3–5 days", "We stitch or print a physical sample. You sign off before a single blank is touched."),
        ("03", "Production", "5–8 days", "Your run is decorated in-house — embroidery, patches, whatever the brief calls for."),
        ("04", "Ship", "Any address", "Bulk, split-ship to employees, or into our fulfillment program. We handle it."),
    ]
    steps3 = [
        ("01", "Quote", "24 hr reply", "Tell us what you want. We come back with pricing, lead time, and honest recommendations."),
        ("02", "Produce", "1–2 weeks", "We sample, you sign off, and your run is decorated in-house — embroidery, patches, whatever fits."),
        ("03", "Ship", "Any address", "Bulk, split-ship to employees, or into our fulfillment program. We handle it."),
    ]
    _lab = 'font:700 11px/1 Inter;letter-spacing:.13em;text-transform:uppercase;color:rgba(4,18,2,.5)'
    demo = ('<div class="demo bleed" style="background:#fff;padding:clamp(28px,4vw,52px)">'
            f'<div style="{_lab};margin-bottom:14px">Four steps</div>' + cm.process_row(steps4)
            + f'<div style="{_lab};margin:30px 0 14px">Three steps (same component — pass 3)</div>' + cm.process_row(steps3)
            + '</div>')
    return demo, cm.process_css(), ""

def build_premium_template():
    demo = ('<div class="demo bleed"><iframe class="demo-iframe" src="preview-premium.html" '
            'title="Premium Brands page template preview" loading="lazy"></iframe></div>')
    return demo, "", ""

def build_info_card():
    items = [(_IC["note"], "Pricing model", "Retail cost + 10% sourcing fee + decoration — reach out for an exact quote.", "pink"),
             (_IC["box"], "MOQs vary", "Minimums depend on style, size run, and live inventory.", "yellow"),
             (_IC["history"], "Flexible timelines", "Plan four to six weeks from approval; not built for rush orders.", "mint")]
    demo = '<div class="demo col">' + cm.info_stack(items) + '</div>'
    return demo, cm.info_card_css(), ""

def build_callout():
    cards = [
        (_IC["note"], "Pricing model",
         "Retail cost + 10% sourcing fee + decoration (typically $10–15 per location), plus applicable tax and "
         "shipping. Reach out for an exact quote on your styles.", "pink"),
        (_IC["box"], "MOQs vary",
         "Minimums depend on style, size run, and live inventory. Smaller runs are possible on accessories and core "
         "styles like the Everywhere Belt Bag; larger size-spread orders need more lead time.", "yellow"),
        (_IC["history"], "Flexible timelines",
         "Inventory changes daily and isn't fully visible in real time. Plan four to six weeks from approval — "
         "Lululemon projects are not recommended for rush orders.", "mint"),
    ]
    demo = ('<div class="demo bleed">'
            + cm.callout_section(
                "What to know, before we get started",
                "LULULEMON IS A<br>PREMIUM RETAIL BRAND.",
                "We don't hold a wholesale account with Lululemon, and that shapes the project differently than a "
                "typical custom apparel order. We believe in being clear upfront so you can decide if it's the right fit.",
                cards) + '</div>')
    return demo, cm.callout_css(), ""

def build_lululemon_template():
    demo = ('<div class="demo bleed"><iframe class="demo-iframe" src="preview-lululemon.html" '
            'title="Custom Lululemon page template preview" loading="lazy"></iframe></div>')
    return demo, "", ""

def build_underarmour_template():
    demo = ('<div class="demo bleed"><iframe class="demo-iframe" src="preview-under-armour.html" '
            'title="Custom Under Armour page template preview" loading="lazy"></iframe></div>')
    return demo, "", ""

def build_layout():
    css = (cm.layout_css() +
           ".lay-tok{display:flex;gap:12px;flex-wrap:wrap;margin-bottom:20px}"
           ".lay-tok code{background:rgba(4,18,2,.06);border-radius:8px;padding:9px 13px;"
           "font:600 13px/1 ui-monospace,SFMono-Regular,Menlo,monospace}"
           ".lay-demo{width:100%;background:#fff;border:1.5px solid rgba(4,18,2,.14);border-radius:var(--r-card);overflow:hidden}"
           ".lay-band{position:relative;background:var(--cream);padding:26px var(--pad);border-bottom:1.5px dashed rgba(4,18,2,.18)}"
           ".lay-band:last-child{border-bottom:0}"
           ".lay-cont{max-width:var(--maxw);margin:0 auto;background:var(--blue);color:var(--blue-deep);border-radius:12px;"
           "padding:20px;font:800 12px/1.4 Inter;text-transform:uppercase;letter-spacing:.12em;text-align:center}"
           ".lay-gut{position:absolute;top:0;bottom:0;width:var(--pad);"
           "background:repeating-linear-gradient(45deg,rgba(245,128,177,.28),rgba(245,128,177,.28) 6px,transparent 6px,transparent 12px)}"
           ".lay-gut.l{left:0}.lay-gut.r{right:0}"
           ".lay-cap{font:700 11px/1 Inter;letter-spacing:.13em;text-transform:uppercase;color:rgba(4,18,2,.5);margin-bottom:10px}")
    bands = "".join('<div class="lay-band"><div class="lay-gut l"></div><div class="lay-gut r"></div>'
                    '<div class="lay-cont">.cm-container — max-width var(--maxw)</div></div>' for _ in range(3))
    demo = ('<div class="demo col">'
            '<div class="lay-tok"><code>--pad: clamp(24px, 5vw, 72px)</code><code>--maxw: 1340px</code></div>'
            '<div class="lay-cap">Pink = the shared gutter (--pad) · Blue = the max-width content column (--maxw)</div>'
            '<div class="lay-demo">' + bands + '</div></div>')
    return demo, css, ""

# ---------------------------------------------------------------------------
# REGISTRY — the single place to add a component. Each entry -> card + page.
#   slug/name/eyebrow/color/blurb + a builder() -> (demo_html, css, js)
#   api  : list of (label, code_snippet)
#   notes: list of html bullet strings
# ---------------------------------------------------------------------------
REGISTRY = [
    {
        "slug": "color", "name": "Color", "eyebrow": "TOKENS", "color": "pink",
        "blurb": "Primitives, bright + deep-accent pairs, and the semantic roles that map onto them.",
        "builder": build_color,
        "api": [
            ("Emit the token block once (‹head›), then reference by var()",
             "import cm_kit as cm\n\nstyle = \"<style>\" + cm.root_css() + \"</style>\"\n# root_css() emits :root{ --cream … --mint-deep }\n\n# then in CSS, never raw hex:\n#   background: var(--blue);\n#   color:      var(--blue-deep);   /* title/link on a blue surface */"),
        ],
        "notes": [
            "<b>Ink is the universal text color.</b> Body + headings are ink on any bright or cream surface — never a deep accent for body text.",
            "<b>Cream is the page.</b> Brights are surfaces/accents, not whole-page backgrounds.",
            "<b>Deep accents are per-panel:</b> a pink panel uses <code>--pink-deep</code> for its title + link; match the accent to the surface.",
            "<b>Only brand tokens.</b> No greys or off-brand hues — dim ink with opacity (<code>rgba(4,18,2,.6)</code>) for secondary text.",
        ],
    },
    {
        "slug": "typography", "name": "Typography", "eyebrow": "TOKENS", "color": "yellow",
        "blurb": "Two families, sharp roles: Poppins 900 for display, Inter for everything else.",
        "builder": build_type,
        "api": [
            ("Font families",
             "/* Poppins 900 ONLY for display / nav / Premium pills */\nfont-family: Poppins, sans-serif; font-weight: 900;\n\n/* Inter (system-ui fallback) for body / UI / labels */\nfont-family: Inter, system-ui, sans-serif;   /* 400–700 */\n\n/* Load once via Google Fonts (the only external dependency): */\n/* Poppins:wght@900 + Inter:wght@400;500;600;700;800 */"),
        ],
        "notes": [
            "<b>Never set Poppins below 900.</b> If a heading needs to feel lighter, it becomes Inter — not lighter Poppins.",
            "<b>Tracking:</b> Poppins display <code>-0.02em</code>; uppercase labels <code>+0.13–0.16em</code>; nav/buttons <code>+0.04–0.05em</code>.",
            "Display sizes are fluid <code>clamp(min, vw, max)</code> so they shrink on mobile.",
        ],
    },
    {
        "slug": "spacing", "name": "Spacing", "eyebrow": "TOKENS", "color": "mint",
        "blurb": "A 4-based scale. Use the steps; don't invent in-between values.",
        "builder": build_space,
        "api": [
            ("The scale",
             "/* 4 · 8 · 12 · 16 · 20 · 24 · 32 · 40 · 56 · 64 · 72 · 96 · 120 */\n\n/* component padding lives in the 14–24 range (cards ~24, inputs ~16–18) */\n/* section rhythm uses the big end, fluid: */\npadding-block: clamp(40px, 6vw, 96px);"),
        ],
        "notes": [
            "<b>Don't invent in-between values</b> — stick to the steps for a consistent rhythm.",
            "Component padding: <code>14–24px</code>. Section rhythm: <code>72 / 96 / 120</code>, fluid between stacked sections.",
        ],
    },
    {
        "slug": "radius", "name": "Radius", "eyebrow": "TOKENS", "color": "blue",
        "blurb": "Five corner tokens, from full pill to the near-straight notch-card edge.",
        "builder": build_radius,
        "api": [
            ("Radius tokens",
             "--r-pill:    999px;                    /* buttons, pills, tags */\n--r-card:    clamp(18px,1.6vw,26px);   /* standard cards, form container */\n--r-card-lg: clamp(22px,2.4vw,40px);   /* large feature panels */\n--r-sm:      10px;                     /* small chips, inputs */\n--r-flat:    6px;                      /* near-straight edge (notch-card cut side) */\n\n/* use: border-radius: var(--r-card); */"),
        ],
        "notes": [
            "Pick by role: pills/tags → <code>--r-pill</code>; cards/inputs → <code>--r-card</code>/<code>--r-sm</code>; feature panels → <code>--r-card-lg</code>.",
            "<code>--r-flat</code> is the near-straight corner on the notch card's cut side.",
        ],
    },
    {
        "slug": "notch-card", "name": "K-Notch Card", "eyebrow": "ATOM", "color": "blue",
        "blurb": "The signature K-cut card. A fixed-size SVG mask keeps the cut's proportion at any card height.",
        "builder": build_notch,
        "api": [
            ("Emit the CSS once, then render a card",
             "import cm_kit as cm\n\nstyle = \"<style>\" + cm.root_css() + cm.notch_css() + \"</style>\"\n\ncard = cm.notch_card(inner=\"…\", side=\"r\", bg=\"var(--blue)\")\n#   side in {\"r\", \"l\", \"both\"}\n#   set width/height yourself via style= or a class in cls="),
            ("Fill-height mode (tall cards) — or fit existing markup",
             "# tall cards: cut fills the height, depth fixed (never ovalizes)\ncm.notch_layer_css(\".my-card\", \"r\", notch_h=\"100%\")\n\n# keep your own background layer, source the cut from the kit:\ncm.notch_layer_css(\".proc .proc-bg\", \"r\", notch_h=\"100%\", important=True)"),
            ("Underlying classes (write the HTML by hand)",
             "<article class=\"k-card k-r\">…</article>   <!-- notch right, rounded left -->\n<article class=\"k-card k-l\">…</article>   <!-- notch left,  rounded right -->\n<article class=\"k-card k-both\">…</article><!-- notch both sides -->"),
        ],
        "notes": [
            "<b>Two height modes.</b> <code>notch_h=\"100%\"</code> (fill) for tall cards — usually what you want on the real site; <code>notch_h=173</code> (fixed px) keeps the exact drawn proportion for small cards near native size.",
            "<b><code>mask-repeat:no-repeat</code> is mandatory</b> and already baked in — keep it if you re-author, or the tooth tiles down the side.",
            "<b>Safari:</b> needs <code>-webkit-mask-composite:source-out</code> (already emitted). Chrome/Edge/Firefox modern use <code>mask-composite:subtract</code>. Verify on Safari if in scope.",
            "The tooth geometry is lifted verbatim from the client's <code>Card_Shape_1</code> art, so the silhouette matches the original drawing exactly.",
        ],
    },
    {
        "slug": "button", "name": "Buttons", "eyebrow": "ATOM", "color": "yellow",
        "blurb": "Primary (yellow CTA) and outline. Pill radius, uppercase, visible focus ring.",
        "builder": build_button,
        "api": [
            ("Emit the CSS once, then render",
             "import cm_kit as cm\nstyle = \"<style>\" + cm.root_css() + cm.button_css() + \"</style>\"\n\ncm.button(\"Request a quote\")                    # primary (CTA)\ncm.button(\"See all services\", variant=\"outline\") # outline\n\n# classes:  .cm-btn.cm-btn--primary | .cm-btn.cm-btn--outline"),
        ],
        "notes": [
            "<b>Primary</b> fills <code>--cta</code> (yellow) with ink text; hover lifts slightly.",
            "<b>Outline</b> is a 1.5px ink border; hover fills ink, text turns cream.",
            "Both show a visible ink focus ring and honor <code>prefers-reduced-motion</code>.",
        ],
    },
    {
        "slug": "pill", "name": "Premium Pill", "eyebrow": "ATOM", "color": "pink",
        "blurb": "The Premium-brand pill: Poppins 900, uppercase, with the brand 'crooked' hover.",
        "builder": build_pill,
        "api": [
            ("Emit the CSS once, then render",
             "import cm_kit as cm\nstyle = \"<style>\" + cm.root_css() + cm.pill_css() + \"</style>\"\n\ncm.pill(\"PATAGONIA\")                 # ink outline\ncm.pill(\"LULULEMON\", bg=\"var(--blue)\") # filled with a bright\n\n# class: .cm-pill"),
        ],
        "notes": [
            "<b>Poppins 900, uppercase</b>, pill radius — ink outline or a bright fill.",
            "<b>Crooked hover:</b> a small rotate (≈-2°) + translate. Wrapped in <code>prefers-reduced-motion: no-preference</code>, so it's off when reduced motion is requested.",
        ],
    },
    {
        "slug": "input", "name": "Form Input", "eyebrow": "ATOM", "color": "mint",
        "blurb": "A labelled field: uppercase label above, white fill, ink focus ring.",
        "builder": build_input,
        "api": [
            ("Emit the CSS once, then render",
             "import cm_kit as cm\nstyle = \"<style>\" + cm.root_css() + cm.input_css() + \"</style>\"\n\ncm.field(\"Email\", name=\"email\", type=\"email\",\n         placeholder=\"you@company.com\")\n\n# class: .cm-field (label + input/textarea)"),
        ],
        "notes": [
            "<b>Label sits above</b> in uppercase Label style; white fill, <code>--r-sm</code> radius, ink text.",
            "<b>Focus:</b> ink border + soft ink ring. Placeholder is ink at ~45% opacity (no grey).",
        ],
    },
    {
        "slug": "faq", "name": "FAQ Accordion", "eyebrow": "MOLECULE", "color": "mint",
        "blurb": "Mint rows, ink titles, +/- indicator. One panel open at a time; height animates.",
        "builder": build_faq,
        "api": [
            ("CSS once, render, and wire the JS once",
             "import cm_kit as cm\nstyle  = \"<style>\" + cm.root_css() + cm.faq_css() + \"</style>\"\n\nhtml   = cm.faq([\n    (\"What is the minimum order?\", \"MOQs vary by item…\"),\n    (\"How fast can you produce?\",  \"About two weeks…\"),\n])\n\nscript = \"<script>\" + cm.faq_js() + \"</script>\"  # one open at a time"),
        ],
        "notes": [
            "<b>One open at a time</b> — opening a panel closes the others.",
            "<b>Mint surface</b> (<code>--surface-mint</code>), ink title; the <code>+</code> indicator flips to <code>−</code> when open.",
            "Answer height animates via <code>grid-template-rows: 0fr → 1fr</code>; each answer is an ARIA <code>region</code> labelled by its question.",
        ],
    },
    {
        "slug": "nav", "name": "Nav", "eyebrow": "ORGANISM", "color": "blue",
        "blurb": "Ink bar, cream logo, Poppins links, Services / Premium-brand dropdowns, yellow CTA.",
        "builder": build_nav,
        "api": [
            ("CSS once, render with your logo, wire the JS once",
             "import cm_kit as cm\nstyle  = \"<style>\" + cm.root_css() + cm.nav_css() + \"</style>\"\n\nhtml   = cm.nav(logo_src,                      # data URI / path to cream logo\n    links=[\"Products\"],\n    services=[\"Custom Screen Printing\", \"Embroidery & DTG\"],\n    brands=[\"Patagonia\", \"YETI\", \"Lululemon\"])\n\nscript = \"<script>\" + cm.nav_js() + \"</script>\"  # click-to-pin dropdowns"),
        ],
        "notes": [
            "<b>Production is <code>position:fixed</code>.</b> The kit CSS leaves positioning to you; the demo above overrides to <code>static</code> so it sits in the page.",
            "Dropdowns open on <b>hover</b> (CSS) and pin on <b>click</b> (JS); <code>Escape</code> closes. Triggers carry <code>aria-expanded</code> / <code>aria-haspopup</code>.",
            "Ink bar, cream logo, Poppins nav links (hover yellow), yellow CTA pill. Collapses toward a drawer on narrow screens.",
        ],
    },
]

REGISTRY.extend([
    # ---- ATOMS ----
    {"slug": "eyebrow", "name": "Eyebrow", "eyebrow": "ATOM", "color": "pink",
     "blurb": "The small uppercase label that sits above titles and on cards.",
     "builder": build_eyebrow,
     "api": [("Emit CSS once, then render",
              'cm.eyebrow("What we do")\ncm.eyebrow("TOKENS", color="var(--pink-deep)")')],
     "notes": ["Inter 800, uppercase, <code>+0.16em</code> tracking — the Label type role.",
               "Defaults to dim ink; pass a deep accent when it sits on a matching bright surface."]},
    {"slug": "arrow-link", "name": "Arrow Link", "eyebrow": "ATOM", "color": "mint",
     "blurb": "The underlined uppercase link with a nudging arrow, used across cards and sections.",
     "builder": build_arrow,
     "api": [("Emit CSS once, then render",
              'cm.arrow_link("Browse premium brands")\ncm.arrow_link("See all services", color="var(--blue-deep)")')],
     "notes": ["Arrow slides on hover; underline is the current text color.",
               "Use the matching deep accent when placed on a bright surface."]},
    {"slug": "badge", "name": "Monkey Badge", "eyebrow": "ATOM", "color": "yellow",
     "blurb": "The Crooked Monkey emblem — the circular 'we are here for you, always' lockup.",
     "builder": build_badge,
     "api": [("Emit CSS once, then render (pass the SVG markup)",
              'monkey = open("assets/monkey_inner.svg").read()\ncm.badge(monkey, size="140px")        # slow spin\ncm.badge(monkey, size="96px", spin=False)')],
     "notes": ["Recolored to ink via <code>currentColor</code>; scales to any size.",
               "Spins slowly by default; the animation is off under <code>prefers-reduced-motion</code>."]},

    # ---- MOLECULES ----
    {"slug": "section-heading", "name": "Section Heading", "eyebrow": "MOLECULE", "color": "blue",
     "blurb": "Eyebrow + Poppins 900 title + intro — the standard section lead-in.",
     "builder": build_heading,
     "api": [("Emit CSS once, then render",
              'cm.heading("Custom merch services",\n           eyebrow="What we do",\n           sub="Six buyer-intent categories…",\n           center=False)')],
     "notes": ["Title accepts inline HTML (<code>&lt;br&gt;</code>, highlight spans).",
               "Pass <code>center=True</code> for centered section intros."]},
    {"slug": "media-card", "name": "Media Card", "eyebrow": "MOLECULE", "color": "yellow",
     "blurb": "Image on top, bright caption below (eyebrow + title + meta + optional link).",
     "builder": build_media,
     "api": [("Emit CSS once, then render",
              'cm.media_card(img_src, "Marketing & Brand Teams",\n    "Client gifts that look retail-quality.",\n    eyebrow="Buyer type", accent="var(--yellow)", link="Learn more")')],
     "notes": ["The caption surface is a bright (<code>accent</code>); title + text stay ink.",
               "3:2 photo, object-fit cover — pass any image; the card sizes to it."]},
    {"slug": "feature-card", "name": "Feature Card", "eyebrow": "MOLECULE", "color": "blue",
     "blurb": "A numbered step card built on the K-notch atom — number, title, body.",
     "builder": build_feature,
     "api": [("Emit CSS once, then render (composes the notch card)",
              'cm.feature_card("01", "Tell us what you need",\n    "Quote in 30 minutes…", side="r", bg="var(--blue)")')],
     "notes": ["Reuses <code>notch_card</code>, so it inherits the signature K-cut.",
               "<code>side</code> in {r, l, both}; padding clears the cut on either side."]},
    {"slug": "checklist", "name": "Checklist", "eyebrow": "MOLECULE", "color": "mint",
     "blurb": "Reassurance list — ink check badges (yellow tick) beside short bold lines.",
     "builder": build_checklist,
     "api": [("Emit CSS once, then render",
              'cm.checklist(["Reply within 1 business hour",\n              "Dedicated account rep",\n              "No commitment to quote"])')],
     "notes": ["Check badge is ink with a yellow tick — on-brand, no green.",
               "Keep lines short; they read as promises, not paragraphs."]},
    {"slug": "pill-group", "name": "Pill Group", "eyebrow": "MOLECULE", "color": "pink",
     "blurb": "A wrapping cluster of Premium pills — the reusable 'text + brands' unit.",
     "builder": build_pillgroup,
     "api": [("Emit pill + group CSS once, then render",
              'cm.pill_group(["Patagonia", "YETI", "Lululemon"])\ncm.pill_group(["NEW", "SALE"], bg="var(--blue)")  # filled')],
     "notes": ["Wraps responsively; each pill keeps the brand 'crooked' hover.",
               "Used inside the Text + Pills organism."]},
    {"slug": "level-card", "name": "Level Card", "eyebrow": "MOLECULE", "color": "blue",
     "blurb": "The 'Four Levels' content card — K-silhouette background, image + copy.",
     "builder": build_level,
     "api": [("Emit CSS once, then render",
              'cm.level_card("01 / 04", "Decorate",\n    "Print, embroider, DTG on premium blanks",\n    "Screen printing, embroidery, DTG…",\n    "Screen printing", img_src, color="blue")')],
     "notes": ["The colored background is the full K silhouette (<code>preserveAspectRatio=none</code>).",
               "Building block of the Four Levels organism."]},

    # ---- ORGANISMS ----
    {"slug": "hero", "name": "Hero", "eyebrow": "ORGANISM", "color": "blue",
     "blurb": "Top-of-page headline (highlighted phrase), subtitle, and two CTAs.",
     "builder": build_hero,
     "api": [("Emit CSS once, then render",
              'cm.hero(\'CUSTOM MERCH &amp;<br>\'\n        \'<span class="cm-hero-hl">BRANDED SWAG</span>\',\n        "Crooked Monkey is a full-service merch agency…",\n        primary="Start a project", secondary="See all services")')],
     "notes": ["Title accepts HTML; wrap a phrase in <code>.cm-hero-hl</code> for the blue highlight.",
               "On the live site the hero pins on scroll; the component itself is static — add the pin at the page level."]},
    {"slug": "service-cards", "name": "Service Cards", "eyebrow": "ORGANISM", "color": "yellow",
     "blurb": "The signature grid: photo + copy cards whose K-notch color panel slides on hover.",
     "builder": build_services,
     "api": [("Emit CSS once, then render a grid",
              'cm.services_grid([\n  (img, "Fully Custom Branded Merch", "Built from scratch.", "Cut & sew", "yellow"),\n  (img, "Swag Fulfillment", "Shipped worldwide.", "Fulfillment", "blue"),\n])')],
     "notes": ["Each card: photo (44%) + copy; the bright panel is a K-notch mask that slides on hover/focus.",
               "<code>color</code> sets the surface; the matching deep accent colors the title + link.",
               "Fully keyboard-focusable (<code>tabindex=0</code>, focus-visible triggers the same reveal)."]},
    {"slug": "text-pills", "name": "Text + Pills", "eyebrow": "ORGANISM", "color": "pink",
     "blurb": "Ink section: headline + intro on the left, a cluster of brand pills on the right.",
     "builder": build_premium,
     "api": [("Emit CSS once, then render",
              'cm.premium_section(\n  \'PREMIUM RETAIL<br>BRANDS YOU CAN<br><span class="acc">CO-BRAND</span>\',\n  "We partner with premium retail brands…",\n  ["Patagonia", "YETI", "Lululemon", …])')],
     "notes": ["Dark (ink) surface; cream pills tint to a brand bright + tilt on hover (reduced-motion safe).",
               "Wrap the accent word in <code>.acc</code> for the yellow highlight."]},
    {"slug": "faq-title", "name": "FAQ + Title", "eyebrow": "ORGANISM", "color": "mint",
     "blurb": "The full FAQ section — display title on the left, the accordion on the right.",
     "builder": build_faqsection,
     "api": [("Emit CSS once, render, wire the JS once",
              'style  = cm.faqsection_css()\nhtml   = cm.faq_section(\'CUSTOM<br>MERCH <span class="pink">FAQ.</span>\',\n    [("Minimum order?", "MOQs vary…"), …])\nscript = cm.faq_js()   # one open at a time')],
     "notes": ["Composes the FAQ Accordion molecule under a Poppins 900 title.",
               "Two-column on desktop, stacks on mobile; wrap the accent word in <code>.pink</code>."]},
    {"slug": "form", "name": "Form (Contact)", "eyebrow": "ORGANISM", "color": "blue",
     "blurb": "The 'Ready to start?' block — headline + checklist beside an accessible quote form.",
     "builder": build_form,
     "api": [("Emit CSS once, render, wire the JS once",
              'style  = cm.form_css()\nhtml   = cm.contact_form()   # name/company/email/quantity/message\nscript = cm.form_js()        # prototype: no-op submit')],
     "notes": ["Blue card on cream; every field has a label + visible ink focus ring.",
               "The select uses a custom brand chevron; submit is a prototype no-op.",
               "Pass <code>title_html</code>, <code>checks</code>, <code>quantities</code> to customize."]},
    {"slug": "footer", "name": "Footer", "eyebrow": "ORGANISM", "color": "yellow",
     "blurb": "Ink footer — brand lockup + description, link columns, and a legal bar.",
     "builder": build_footer,
     "api": [("Emit CSS once, then render with your logo",
              'cm.footer(logo_src,\n    columns=[("Services", [...]), ("Locations", [...]), ("Resources", [...])],\n    email="hello@crookedmonkey.com")')],
     "notes": ["Cream logo on ink; column headers in yellow; links dim-cream → cream on hover.",
               "Columns collapse 4 → 2 → 1 across breakpoints."]},
    {"slug": "ticker", "name": "Image Ticker", "eyebrow": "MOLECULE", "color": "mint",
     "blurb": "An infinite marquee of tilted product photos with edge fade; pauses on hover.",
     "builder": build_ticker,
     "api": [("Emit CSS once, then render",
              'cm.ticker([img1, img2, img3, img4])  # duplicated internally for a seamless loop')],
     "notes": ["Pure CSS loop (<code>@keyframes</code>); the list is duplicated for the −50% seam.",
               "Animation stops under <code>prefers-reduced-motion</code>."]},
    {"slug": "gallery", "name": "Gallery", "eyebrow": "ORGANISM", "color": "pink",
     "blurb": "Oversized background wordmark behind the image ticker, with a CTA.",
     "builder": build_gallery,
     "api": [("Emit CSS once, then render",
              'cm.gallery(["Transforming", "Companies", "Into Brands"],\n           [img1, img2, img3, img4], cta="Start a project")')],
     "notes": ["Composes the Image Ticker over a Display-XL Poppins wordmark.",
               "Fully self-contained; images are the only content you pass."]},
    {"slug": "four-levels", "name": "Four Levels", "eyebrow": "ORGANISM", "color": "blue",
     "blurb": "The intro + four Level Cards — the 'we go all the way to cut & sew' sequence.",
     "builder": build_fourlevels,
     "api": [("Emit CSS once, then render",
              'cm.four_levels(\'<span class="hl">Four</span> Levels Of Custom\',\n  "Most agencies stop at level one…",\n  [("01 / 04", "Decorate", "…", "…", "Screen printing", img, "blue"), …])')],
     "notes": ["Composes the Level Card molecule; each card carries its own bright K-silhouette.",
               "On the live site these pin and slide on scroll; here they stack statically."]},
    {"slug": "how-it-works", "name": "How It Works", "eyebrow": "ORGANISM", "color": "blue",
     "blurb": "Process line — a 2×2 of Feature Cards (blue ramp) under a title, with the spinning badge.",
     "builder": build_hiw,
     "api": [("Emit CSS once, then render",
              'cm.how_it_works(\n  [("01", "Tell us what you need", "Quote in 30 minutes…"), …],\n  monkey_svg=monkey_markup)')],
     "notes": ["Steps are Feature Cards with a light→dark blue ramp and alternating notch sides.",
               "The Monkey Badge sits in the header; pass its SVG markup (optional)."]},
    {"slug": "who", "name": "Who We Make Merch For", "eyebrow": "ORGANISM", "color": "mint",
     "blurb": "Buyer-type selector — an accessible vertical tablist that cross-fades a media card.",
     "builder": build_who,
     "api": [("Emit CSS once, render, wire the JS once",
              'style  = cm.who_css()\nhtml   = cm.who_section([\n    ("Marketing & Brand Teams", "var(--yellow)", img, "Campaign launches…"), …])\nscript = cm.who_js()   # click + arrow keys, cross-fade')],
     "notes": ["Proper ARIA tabs: <code>role=tablist/tab/tabpanel</code>, roving <code>tabindex</code>, arrow-key + Home/End nav.",
               "The panel cross-fades on change; fade is skipped under reduced motion.",
               "Each tab carries its own accent, image, and copy via data-attributes."]},

    # ---- TEMPLATE ----
    {"slug": "template-landing", "name": "Landing Page", "eyebrow": "TEMPLATE", "color": "yellow",
     "blurb": "A full page composed from the organisms — Nav, Hero, Services, Text + Pills, FAQ, Form, Footer.",
     "builder": build_landing,
     "api": [("Compose organisms into a page (excerpt — see preview-landing.html)",
              'body = cm.nav(logo) + cm.hero(...) + cm.services_grid(...) \\\n     + cm.premium_section(...) + cm.faq_section(...) \\\n     + cm.contact_form() + cm.footer(logo)\nstyle = (cm.root_css() + cm.nav_css() + cm.hero_css() + cm.service_css()\n         + cm.premium_css() + cm.faqsection_css() + cm.form_css() + cm.footer_css())\nscript = cm.nav_js() + cm.faq_js() + cm.form_js()')],
     "notes": ["Templates show how organisms compose into a real page — each is emitted once, CSS + JS concatenated.",
               "Shown here in an isolating <code>&lt;iframe&gt;</code> so its styles never touch the catalog chrome.",
               "This is the blueprint for building any new page from the kit."]},
])

REGISTRY.extend([
    # ---- Premium Brands page — new components ----
    {"slug": "brand-hero", "name": "Brand Hero", "eyebrow": "ORGANISM", "color": "blue",
     "blurb": "Centered brand headline over an image ticker, with an intro line and a mint CTA.",
     "builder": build_brand_hero,
     "api": [("Emit CSS once, then render",
              'cm.brand_hero(\n  \'Custom <span class="hl">Patagonia</span> Embroidered<br>Apparel for Corporate Gifts\',\n  "Embroidery and patch decoration on every piece…",\n  [img1, img2, img3, img4], cta="Talk to a Merch Expert")')],
     "notes": [
         "<b>Fills the viewport and centers.</b> On a page it must sit under <code>.cm-page</code> so <code>page_css()</code> gives it "
         "<code>min-height:100vh</code>, vertical centering, and top clearance under the fixed nav — that's the nav→title gap.",
         "<b>Built-in vertical rhythm (matches the brand pages):</b> title → gallery is "
         "<code>margin-top:clamp(44px,6.5vh,72px)</code>; gallery → text/button is <code>clamp(56px,8vh,96px)</code>. "
         "Don't add your own wrappers or padding around it — the spacing lives in the component.",
         "<b>Title = two lines, always.</b> Wrap the brand name in <code>.hl</code> for the blue highlight and place the "
         "<code>&lt;br&gt;</code> so <b>both lines fit</b> the ~1100px measure (e.g. break Lululemon after “Apparel”, not after “Gifts”). "
         "A line that overflows becomes a third line and breaks the rhythm.",
         "The gallery is the shared Image Ticker (tilted cards, edge fade, pauses on hover); pass 3–4 images — it loops seamlessly.",
         "<b>Don't shrink the gallery's vertical padding.</b> It's sized to clear the tilted cards' drop-shadow "
         "(<code>clamp(40px,6vh,64px)</code>); reduce it and <code>overflow:hidden</code> clips the shadow, "
         "the gallery gets shorter, and the viewport-centered hero drifts. This is what keeps two brand heroes identical.",
     ]},
    {"slug": "stat-strip", "name": "Stat Strip", "eyebrow": "MOLECULE", "color": "mint",
     "blurb": "Ink bar of quick facts — icon + label + value, evenly divided.",
     "builder": build_stat_strip,
     "api": [("Emit CSS once, then render (pass inline SVG icons)",
              'cm.stat_strip([\n  (clock_svg,  "Lead time",  "5–8 days"),\n  (box_svg,    "Min. order", "12 pieces"),\n  (needle_svg, "Signature",  "Embroidery"),\n])')],
     "notes": ["Icons render in mint; four across on desktop, 2×2 on mobile.",
               "Great directly under a hero to answer the first practical questions."]},
    {"slug": "statement-band", "name": "Statement Band", "eyebrow": "ORGANISM", "color": "mint",
     "blurb": "Eyebrow + big statement + copy + a mint pull-quote, beside a tall photo.",
     "builder": build_statement,
     "api": [("Emit CSS once, then render",
              'cm.statement_band("Why Custom Patagonia",\n  "The brand your team actually wears.",\n  ["Paragraph one…", "Paragraph two…"],\n  img, quote="&ldquo;Best embroidery…&rdquo;", cite="Dana K. · Sonos")')],
     "notes": ["Title + paragraphs accept inline HTML; quote is optional.",
               "White section; the pull-quote sits on a mint card with deep-mint text."]},
    {"slug": "photo-card", "name": "Photo Card", "eyebrow": "MOLECULE", "color": "blue",
     "blurb": "Photo on top, bright caption below (Poppins title + body). The 'what we customize' card.",
     "builder": build_photo_card,
     "api": [("Emit CSS once, render a grid",
              'cm.photo_grid([\n  (img, "Fleece &amp; Softshells", "Better Sweater, Synchilla…", "mint"),\n  (img, "Headwear &amp; Bags", "P-6 trucker hats…", "blue"),\n])')],
     "notes": ["<code>accent</code> sets the caption surface; the title uses its matching deep accent.",
               "Differs from Media Card: full-bright caption, no eyebrow."]},
    {"slug": "usecase-card", "name": "Use-Case Card", "eyebrow": "MOLECULE", "color": "blue",
     "blurb": "Blue K-cut chip card — icon badge + label, with a K silhouette that sweeps in on hover.",
     "builder": build_usecase,
     "api": [("Emit CSS once, render a grid (pass inline SVG icons)",
              'cm.usecase_grid([\n  (gift_svg,  "Client gifts"),\n  (brief_svg, "Executive merch"),\n  (box_svg,   "Onboarding kits"),\n])')],
     "notes": ["Rounded-left, near-straight right; the ink K silhouette scales in on hover/focus.",
               "Designed for a dark (ink) section — blue cards pop against it.",
               "Reduced-motion disables the sweep."]},
    {"slug": "decoration-card", "name": "Decoration Card", "eyebrow": "MOLECULE", "color": "yellow",
     "blurb": "Photo (optional badge) + bright caption with a title, description, and bullet list.",
     "builder": build_decoration,
     "api": [("Emit CSS once, render a grid",
              'cm.decoration_grid([\n  (img, "Embroidery", "Thread-stitched logos…",\n   ["Up to 15,000 stitches", "Metallic thread", "3D puff"], "yellow", "Signature"),\n])')],
     "notes": ["Optional corner <code>badge</code> (e.g. Signature / New) on the photo.",
               "Bullets use the caption's deep accent as the dot color."]},
    {"slug": "product-card", "name": "Product Card", "eyebrow": "MOLECULE", "color": "pink",
     "blurb": "Retail-style card: photo, category, name, price, and color swatches.",
     "builder": build_product,
     "api": [("Emit CSS once, render a grid",
              'cm.product_grid([\n  (img, "Better Sweater Jacket", "Fleece", "from $139",\n   ["#2b2b2b", "#a99b7d", "#d9d2c4"]),\n])')],
     "notes": ["Swatch hexes are <b>real garment colorways</b> — content, not brand tokens (the one place literal hex is right).",
               "4:5 photo; four across on desktop, down to one on mobile."]},
    {"slug": "process-row", "name": "Process Row", "eyebrow": "ORGANISM", "color": "blue",
     "blurb": "Four interlocking Card_Shape steps — number, title, a meta tag, and body. The 'quote → ship' line.",
     "builder": build_process,
     "api": [("Same component — pass 3 or 4 steps (no separate version needed)",
              'cm.process_row([   # 4 steps\n  ("01", "Quote",      "24 hr reply", "…"),\n  ("02", "Sample",     "3–5 days",    "…"),\n  ("03", "Production",  "5–8 days",    "…"),\n  ("04", "Ship",        "Any address", "…"),\n])\n\ncm.process_row([   # 3 steps — first still rounds left, last rounds right\n  ("01", "Quote",   "24 hr reply", "…"),\n  ("02", "Produce", "1–2 weeks",   "…"),\n  ("03", "Ship",    "Any address", "…"),\n])')],
     "notes": [
         "<b>Count-adaptive (2–4 steps).</b> Cards get a <b>role</b>, not a fixed index: first = round-left + tooth-right, "
         "middle = notch-left + tooth-right, last = notch-left + round-right. So the row <b>always closes</b> — pass 3 and "
         "it seals on the right, no editing needed. The blue ramp scales to the count (the 4-step ramp is unchanged).",
         "<b>The silhouettes are distinct, not mirrored</b> — each right-hand tooth seats into the next card's left notch; "
         "that's the interlock. The art is the original 346×173 <code>Card_Shape</code> drawing (same as the brand pages), "
         "stretched with <code>preserveAspectRatio=none</code>, so it matches Patagonia at any card width.",
         "<b>Self-contained:</b> <code>process_css()</code> carries every mask + the mobile fallback (single column, rounded-left). "
         "Card height is <code>min-height:300px</code>; the grid column count follows <code>--n</code>. Drop it into a <code>.cm-container</code> on any page.",
         "<b>Variants are inputs, not copies.</b> Need a 3-step version? Call the same <code>process-row</code> with 3 steps — one handle, one component.",
     ]},
    {"slug": "template-premium", "name": "Premium Brands Page", "eyebrow": "TEMPLATE", "color": "mint",
     "blurb": "The full brand landing (Patagonia) — hero, stat strip, statement, cards, process, FAQ, form, footer.",
     "builder": build_premium_template,
     "api": [("Compose the page from kit organisms (excerpt)",
              'body = cm.nav(logo) + cm.brand_hero(...) + cm.stat_strip(...) \\\n     + cm.statement_band(...) + cm.photo_grid(...) + cm.usecase_grid(...) \\\n     + cm.decoration_grid(...) + cm.product_grid(...) + cm.process_row(...) \\\n     + cm.faq_section(...) + cm.premium_section(...) + cm.contact_form() + cm.footer(logo)')],
     "notes": ["Shown here as the built page (its scroll-pinning is preserved) in an isolating <code>&lt;iframe&gt;</code>.",
               "Every component below the fold is catalogued individually on this page's collection.",
               "The blueprint for spinning up any new premium-brand page."]},
])

REGISTRY.extend([
    {"slug": "info-card", "name": "Info Card", "eyebrow": "MOLECULE", "color": "yellow",
     "blurb": "White card: a bright icon chip + an eyebrow label + a line of body. For facts, pricing notes, callouts.",
     "builder": build_info_card,
     "api": [("Emit CSS once, render a stack (pass inline SVG icons)",
              'cm.info_stack([\n  (note_svg, "Pricing model", "Retail cost + 10% sourcing fee…", "pink"),\n  (box_svg,  "MOQs vary",     "Minimums depend on style…",      "yellow"),\n  (clock_svg,"Flexible timelines","Plan four to six weeks…",     "mint"),\n])')],
     "notes": ["<code>accent</code> colors both the chip and the eyebrow (chip = bright, eyebrow = its deep accent).",
               "<b>Accessibility:</b> the eyebrow uses the deep accent, not the bright — a bright label on white/cream fails contrast.",
               "Body stays dim ink; keep each card to one idea."]},
    {"slug": "callout", "name": "Callout Section", "eyebrow": "ORGANISM", "color": "pink",
     "blurb": "Two-column 'what to know' — a section heading beside a stack of info cards. The brand-page primer block.",
     "builder": build_callout,
     "api": [("Emit CSS once, then render",
              'cm.callout_section(\n  "What to know, before we get started",\n  "LULULEMON IS A<br>PREMIUM RETAIL BRAND.",\n  "We don\'t hold a wholesale account...",\n  cards)   # cards = list of (icon, eyebrow, body, accent)')],
     "notes": ["Composes <code>heading</code> + the Info Card stack; heading title accepts inline HTML (<code>&lt;br&gt;</code>).",
               "The left eyebrow color is a param (default <code>--pink-deep</code>) — match it to the page's accent.",
               "Two columns on desktop, stacks on mobile; cream section, white cards."]},
    {"slug": "layout", "name": "Layout & Grid", "eyebrow": "TOKENS", "color": "blue",
     "blurb": "The page-level rules — one gutter, one max content width, viewport-filling sections. What makes a page cohesive.",
     "builder": build_layout,
     "api": [("Build any page with the shell",
              'style = cm.root_css() + cm.layout_css() + cm.page_css() + <component css…>\n\n'
              '# wrap the whole page:\n<body><div class="cm-page"> … sections … </div></body>\n\n'
              '# each content section:\n<section class="cm-section"><div class="cm-container"> … </div></section>')],
     "notes": [
         "<b>One gutter, one width.</b> Every section shares <code>--pad</code> (side margin) and <code>--maxw</code> (1340px), so content edges line up down the whole page.",
         "<b>Sections fill the viewport.</b> Under <code>.cm-page</code>, each content section is <code>min-height:100vh</code> and centers its content — nav / stat strip / footer are exempt.",
         "<b>Display headings: 2 lines max.</b> Keep hero/section titles tight or use <code>&lt;br&gt;</code>; never let one wrap to three.",
         "<b>Spacing scale is 4-based</b> (4·8·12·16·20·24·32·40·56·64·72·96·120); section rhythm lives at the big end via the section padding token.",
         "This is the layer that makes the two brand pages (Patagonia, Lululemon) read as one system — build every new page on it."]},
    {"slug": "template-lululemon", "name": "Custom Lululemon Page", "eyebrow": "TEMPLATE", "color": "pink",
     "blurb": "A second brand-page variant — same template skeleton as Patagonia; only Why (Statement Band) and What-to-know (Callout) change.",
     "builder": build_lululemon_template,
     "api": [("Same skeleton, two swapped sections (composed from the kit)",
              '# only these two change per brand:\nbody = ... hero + stat_strip \\\n  + cm.statement_band("Why Custom Lululemon", ...)      # section 3\n  + cm.callout_section("What to know…", ...)           # section 4\n  + photo_grid + usecase_grid + decoration_grid \\\n  + process_row + faq_section + premium_section + contact_form + footer')],
     "notes": ["Demonstrates <b>template variants</b>: reuse one page skeleton, swap the brand-specific sections.",
               "Composed live from kit components (unlike the Patagonia template, which iframes its built page).",
               "Shown in an isolating <code>&lt;iframe&gt;</code>; a real page adds hero-pin + scroll motion at the page level."]},
    {"slug": "template-under-armour", "name": "Custom Under Armour Page", "eyebrow": "TEMPLATE", "color": "blue",
     "blurb": "A third brand page — built from a content config alone, no layout work. Wholesale brand: skips the 'what to know' callout.",
     "builder": build_underarmour_template,
     "api": [("Content-only — same template, different config",
              'UNDER_ARMOUR = { "hero": {...}, "why": {...}, "customize": {...}, ... }  # content only\nrender_brand_page(UNDER_ARMOUR)   # layout guaranteed; nothing hand-composed')],
     "notes": ["<b>Proof of the content-only workflow:</b> this page is <code>render_brand_page(UNDER_ARMOUR)</code> — only the config changed.",
               "Optional sections in action: no <code>callout</code> key, so the 'what to know' section is skipped for this wholesale brand.",
               "The 'What We Customize' grid auto-fits — 4 cards here vs 3 on Lululemon, both in one clean row."]},
])

# ---------------------------------------------------------------------------
# Collections — the catalog is browsed by page, not as one long list.
#   tokens = shared foundations; home / premium-brands = per-page component sets.
# A component can belong to several pages (nav, footer, buttons… are shared).
# ---------------------------------------------------------------------------
COLLECTIONS = [
    ("tokens", "Tokens", "pink", "FOUNDATIONS",
     "The shared foundation — color, type, spacing, and radius. Everything else is built from these."),
    ("home", "Home Page", "blue", "PAGE",
     "Every component that makes up the Crooked Monkey home page."),
    ("premium-brands", "Premium Brands Page", "mint", "PAGE",
     "The brand landing template (Patagonia-style) and the components it's built from."),
]

_PAGE_OF = {}
def _assign(slugs, keys):
    for s in slugs:
        _PAGE_OF.setdefault(s, set()).update(keys)

_assign(["color", "typography", "spacing", "radius", "layout"], ["tokens"])
# shared across both pages
_assign(["nav", "button", "pill", "input", "eyebrow", "arrow-link", "pill-group",
         "section-heading", "text-pills", "faq-title", "form", "footer", "faq",
         "notch-card", "ticker"], ["home", "premium-brands"])
# home only
_assign(["badge", "media-card", "feature-card", "checklist", "level-card", "hero",
         "service-cards", "gallery", "four-levels", "how-it-works", "who",
         "template-landing"], ["home"])
# premium-brands only
_assign(["brand-hero", "stat-strip", "statement-band", "photo-card", "usecase-card",
         "decoration-card", "product-card", "process-row", "info-card", "callout",
         "template-premium", "template-lululemon", "template-under-armour"], ["premium-brands"])

def pages_of(slug):
    return _PAGE_OF.get(slug, {"home"})

def entries_for(key):
    return [e for e in REGISTRY if key in pages_of(e["slug"])]

# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------
def component_card(e):
    col = tier_color(e["eyebrow"]); deep = DEEP[col]
    return (f'<a class="card" href="{e["slug"]}.html" style="background:var(--{col})">'
            f'<span class="c-eyebrow" style="color:var(--{deep})">{esc(e["eyebrow"])}</span>'
            f'<span class="c-title">{esc(e["name"])}</span>'
            f'<span class="c-blurb">{esc(e["blurb"])}</span>'
            f'<span class="c-go" style="color:var(--{deep})">View <span class="ar">→</span></span></a>')

def _tier_blocks(items):
    order = ["TOKENS", "ATOM", "MOLECULE", "ORGANISM", "TEMPLATE"]
    label = {"TOKENS": "Tokens", "ATOM": "Atoms", "MOLECULE": "Molecules",
             "ORGANISM": "Organisms", "TEMPLATE": "Templates"}
    groups = {}
    for e in items:
        groups.setdefault(e["eyebrow"], []).append(e)
    blocks = []
    for cat in order:
        g = groups.get(cat)
        if not g:
            continue
        blocks.append(f'<div class="cat-group"><h2 class="h-display">{label[cat]}</h2>'
                      f'<div class="grid">{"".join(component_card(e) for e in g)}</div></div>')
    return "".join(blocks)

def render_index():
    cards = []
    for key, label, color, eyebrow, blurb in COLLECTIONS:
        deep = DEEP[color]
        n = len(entries_for(key))
        cards.append(
            f'<a class="card col-card" href="{key}.html" style="background:var(--{color})">'
            f'<span class="c-eyebrow" style="color:var(--{deep})">{eyebrow}</span>'
            f'<span class="c-title">{esc(label)}</span>'
            f'<span class="c-blurb">{esc(blurb)}</span>'
            f'<span class="c-go" style="color:var(--{deep})">{n} components <span class="ar">→</span></span></a>')
    body = ('<div class="wrap"><div class="hero">'
            '<h1 class="h-display">Component<br>Library</h1>'
            '<p class="lead">The Crooked Monkey design system, browsable. Start with the shared '
            '<b>tokens</b>, then dive into a <b>page</b> to see the components it\'s built from — '
            'each with a live demo and the exact <code>cm_kit</code> call. Self-contained from '
            '<code>cm_kit.py</code>; the only external dependency is Google Fonts.</p></div>'
            f'<div class="grid grid-lg">{"".join(cards)}</div></div>')
    return page("Component Library", body)

def render_collection(key, label, blurb):
    items = entries_for(key)
    body = ('<div class="wrap"><a class="back" href="index.html">← Library</a>'
            f'<div class="hero"><span class="eyebrow">Collection · {len(items)} components</span>'
            f'<h1 class="h-display">{esc(label)}</h1>'
            f'<p class="lead">{esc(blurb)}</p></div>'
            + _tier_blocks(items) + '</div>')
    return page(label, body)

def render_component(e):
    demo, css, js = e["builder"]()
    col = tier_color(e["eyebrow"]); deep = DEEP[col]
    _call = entry_call(e)
    # section 2: how to call it
    api_html = ""
    for i, (lab, snippet) in enumerate(e["api"]):
        api_html += code_lab(lab) + code(snippet)
    notes_html = "".join(f'<li>{n}</li>' for n in e["notes"])
    _pl = {"tokens": "Tokens", "home": "Home Page", "premium-brands": "Premium Brands Page"}
    chips = " · ".join(f'<a href="{p}.html">{_pl[p]}</a>' for p in sorted(pages_of(e["slug"])))
    body = ('<div class="wrap">'
            '<a class="back" href="index.html">← Library</a>'
            f'<header class="p-head"><span class="eyebrow" style="color:var(--{deep})">{esc(e["eyebrow"])}</span>'
            f'<h1 class="h-display">{esc(e["name"])}</h1>'
            f'<p class="lead">{esc(e["blurb"])}</p>'
            + '<div class="p-handle"><span class="lab">Handle</span>'
            + f'<code>{esc(e["slug"])}</code>'
            + (f'<span class="lab">Call</span><span class="call">{esc(_call)}</span>' if _call else "")
            + '</div>'
            f'<p class="p-pages">Used on: {chips}</p></header>'
            '<section class="sect"><div class="sect-lab">01 — Live demo</div>'
            '<h2>Every variant, rendered</h2>' + demo + '</section>'
            '<section class="sect"><div class="sect-lab">02 — How to call it</div>'
            '<h2>Reuse it on a new page</h2>' + api_html + '</section>'
            '<section class="sect"><div class="sect-lab">03 — When to use it</div>'
            '<h2>Notes &amp; gotchas</h2><ul class="notes">' + notes_html + '</ul></section>'
            '</div>')
    return page(e["name"], body, extra_css=css, extra_js=js)

def render_landing_preview():
    """A full page composed purely from kit organisms — the Template demo, in its own file."""
    body = (
        cm.nav(LOGO_URI, links=["Products"],
               services=["Custom Screen Printing", "Embroidery & DTG", "Cut & Sew Manufacturing"],
               brands=["Patagonia", "YETI", "Lululemon", "The North Face"])
        + cm.hero('CUSTOM MERCH &amp;<br><span class="cm-hero-hl">BRANDED SWAG</span><br>FOR COMPANIES AND TEAMS',
                  "Crooked Monkey is a full-service custom merch agency. In-house screen printing, embroidery "
                  "and DTG; design, kitting, fulfillment, and premium retail brands — shipped from studios across the US.")
        + '<section style="background:#fff;padding:clamp(48px,7vw,96px) clamp(24px,5vw,64px)">'
        + '<div style="max-width:1180px;margin:0 auto">'
        + cm.heading("Custom merch services<br>for every format", eyebrow="What we do", center=True)
        + '<div style="margin-top:clamp(32px,5vw,56px)"></div>'
        + cm.services_grid([
            (IMG["chief"], "Fully Custom Branded Merch", "Unique pieces, built from scratch.", "Cut &amp; sew", "yellow"),
            (IMG["hoodie"], "Swag Storage, Kitting &amp; Distribution", "Stored, kitted and shipped worldwide.", "Swag fulfillment", "blue"),
            (IMG["duffel"], "Merch Design That Elevates Your Brand", "Your brand, on every detail.", "Design &amp; packaging", "pink"),
            (IMG["sonoma"], "Custom Employee &amp; Client Swag Kits", "Curated unboxing, delivered.", "Custom swag kits", "mint"),
          ])
        + '</div></section>'
        + '<div style="background:var(--cream);padding:clamp(48px,7vw,90px) clamp(24px,5vw,64px)">'
        + cm.premium_section('PREMIUM RETAIL<br>BRANDS YOU CAN<br><span class="acc">CO-BRAND</span>',
                             "We partner with a wide selection of premium retail brands so your merch feels bought, not made.",
                             ["Patagonia", "YETI", "Lululemon", "The North Face", "Under Armour", "Stanley", "Hydro Flask", "Cotopaxi"])
        + '</div>'
        + '<div style="background:var(--cream);padding:clamp(24px,4vw,64px) clamp(24px,5vw,64px)">'
        + cm.faq_section('CUSTOM<br>MERCH <span class="pink">FAQ.</span>',
            [("What is the minimum order for custom merch?", "MOQs vary by item: apparel from 25 pieces, hard goods from 50, swag kits from 25 boxes."),
             ("How fast can you produce custom merch?", "Standard production runs about two weeks after art approval; rush is 5 business days or less."),
             ("Can you match my exact brand colors?", "Yes — we PMS-match colors and proof every decoration method."),
             ("Do you ship internationally?", "Yes, we ship worldwide and can stage inventory regionally.")])
        + '</div>'
        + '<div style="background:var(--cream);padding:clamp(24px,4vw,64px) clamp(24px,5vw,64px)">'
        + cm.contact_form() + '</div>'
        + cm.footer(LOGO_URI)
    )
    css = (cm.root_css() + cm.nav_css() + ".cm-nav{position:sticky;top:0;z-index:50}"
           + cm.hero_css() + cm.heading_css() + cm.service_css() + cm.premium_css()
           + cm.faqsection_css() + cm.form_css() + cm.footer_css())
    js = cm.nav_js() + cm.faq_js() + cm.form_js()
    return ("<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\">"
            "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
            "<title>Landing Page — Crooked Monkey (template preview)</title>"
            "<link rel=\"preconnect\" href=\"https://fonts.googleapis.com\">"
            "<link rel=\"preconnect\" href=\"https://fonts.gstatic.com\" crossorigin>"
            "<link href=\"https://fonts.googleapis.com/css2?family=Poppins:wght@900&"
            "family=Inter:wght@400;500;600;700;800&display=swap\" rel=\"stylesheet\">"
            "<style>*{box-sizing:border-box;margin:0}body{background:var(--cream);"
            "font-family:Inter,system-ui,sans-serif;-webkit-font-smoothing:antialiased}img{display:block;max-width:100%}"
            + css + "</style></head><body>" + body
            + "<script>(function(){" + js + "})();</script></body></html>")

# ===========================================================================
# BRAND PAGE TEMPLATE — the fixed skeleton. Pass a content config; layout is
# guaranteed. To add a brand page you ONLY edit content: copy a config like
# LULULEMON below, change the strings/keys, and call render_brand_page(NEW).
# Nothing about the composition/spacing changes — so pages can't drift.
#
# Config keys (all content; icons are keys into _IC, images are keys into IMG):
#   title, nav_brands,
#   hero{title, sub, images[], cta},
#   stats[(icon,label,value)],
#   why{eyebrow, title, paras[], img, quote?, cite?, alt?},          # Statement Band
#   callout{eyebrow, title, body, cards[(icon,eyebrow,body,accent)]},# Callout Section
#   customize{eyebrow, title, cards[(img,title,body,accent)]},       # Photo Cards
#   who{eyebrow, title, cards[(icon,label)]},                        # Use-Case Cards
#   decorate{eyebrow, title, cards[(img,title,desc,[bullets],accent,badge)]},
#   process{eyebrow, title, steps[(num,title,meta,body)]},
#   faq{title, items[(q,a)]},
#   alternatives{title, sub, brands[], cta},                         # Text + Pills
#   form{quantities[]},
#   footer{columns[(title,[items])]}
# ===========================================================================
def render_brand_page(cfg):
    def wrap(bg, inner):
        return f'<section class="cm-section" style="background:{bg}"><div class="cm-container">{inner}</div></section>'

    def heading(eyebrow, title, center=False, on_ink=False):
        cls = " center" if center else ""
        ec = "var(--mint)" if on_ink else "var(--pink-deep)"
        tc = "color:var(--cream)" if on_ink else ""
        return (f'<div class="cm-heading{cls}" style="margin-bottom:clamp(30px,4vw,48px)">'
                f'<span class="cm-h-eyebrow" style="color:{ec}">{eyebrow}</span>'
                f'<h2 style="{tc}">{title}</h2></div>')

    h, wy = cfg["hero"], cfg["why"]
    cu, wo, de = cfg["customize"], cfg["who"], cfg["decorate"]
    pr, fq, fm, ft = cfg["process"], cfg["faq"], cfg["form"], cfg["footer"]

    # Optional sections — rendered only if the config provides them, so a brand
    # can drop e.g. the "what to know" callout (wholesale brands don't need it)
    # without any change to the template.
    callout_html = ""
    if cfg.get("callout"):
        co = cfg["callout"]
        callout_html = cm.callout_section(co["eyebrow"], co["title"], co["body"],
                                          [(_IC[i], e, b, a) for (i, e, b, a) in co["cards"]])
    alt_html = ""
    if cfg.get("alternatives"):
        al = cfg["alternatives"]
        alt_html = cm.premium_section(al["title"], al["sub"], al["brands"], cta=al.get("cta", "Browse all premium brands"))

    body = (
        cm.nav(LOGO_URI, links=["Products"],
               services=["Custom Screen Printing", "Embroidery & DTG", "Cut & Sew Manufacturing"],
               brands=cfg.get("nav_brands", ["Patagonia", "YETI", "Lululemon", "The North Face"]))
        + cm.brand_hero(h["title"], h["sub"], [IMG[k] for k in h["images"]], cta=h.get("cta", "Talk to a Merch Expert"))
        + cm.stat_strip([(_IC[i], l, v) for (i, l, v) in cfg["stats"]])
        # variant section 1 — Why = Statement Band
        + cm.statement_band(wy["eyebrow"], wy["title"], wy["paras"], IMG[wy["img"]],
                            quote=wy.get("quote"), cite=wy.get("cite"), alt=wy.get("alt", ""))
        # variant section 2 — What to know = Callout (optional)
        + callout_html
        + wrap("#fff", heading(cu["eyebrow"], cu["title"])
               + cm.photo_grid([(IMG[im], t, b, a) for (im, t, b, a) in cu["cards"]]))
        + wrap("var(--ink)", heading(wo["eyebrow"], wo["title"], center=True, on_ink=True)
               + cm.usecase_grid([(_IC[i], l) for (i, l) in wo["cards"]]))
        + wrap("var(--cream)", heading(de["eyebrow"], de["title"], center=True)
               + cm.decoration_grid([(IMG[im], t, d, lst, a, bd) for (im, t, d, lst, a, bd) in de["cards"]]))
        + wrap("#fff", heading(pr["eyebrow"], pr["title"]) + cm.process_row(pr["steps"]))
        + cm.faq_section(fq["title"], fq["items"])
        + alt_html
        + '<section class="cm-section" style="background:var(--cream)">'
        + cm.contact_form(quantities=fm["quantities"]) + '</section>'
        + cm.footer(LOGO_URI, columns=ft["columns"])
    )
    css = (cm.root_css() + cm.layout_css() + cm.page_css() + cm.nav_css()
           + cm.brand_hero_css() + cm.stat_strip_css() + cm.statement_css() + cm.callout_css()
           + cm.heading_css() + cm.photo_card_css() + cm.usecase_css() + cm.decoration_css()
           + cm.process_css() + cm.faqsection_css() + cm.premium_css() + cm.pill_css()
           + cm.pillgroup_css() + cm.button_css() + cm.form_css() + cm.footer_css())
    js = cm.nav_js() + cm.faq_js() + cm.form_js()
    return ("<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\">"
            "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
            "<title>" + esc(cfg.get("title", "Custom Brand")) + " — Crooked Monkey (template preview)</title>"
            "<link rel=\"preconnect\" href=\"https://fonts.googleapis.com\">"
            "<link rel=\"preconnect\" href=\"https://fonts.gstatic.com\" crossorigin>"
            "<link href=\"https://fonts.googleapis.com/css2?family=Poppins:wght@900&"
            "family=Inter:wght@400;500;600;700;800&display=swap\" rel=\"stylesheet\">"
            "<style>*{box-sizing:border-box;margin:0}body{background:var(--cream);"
            "font-family:Inter,system-ui,sans-serif;-webkit-font-smoothing:antialiased}img{display:block;max-width:100%}"
            + css + "</style></head><body><div class=\"cm-page\">" + body
            + "</div><script>(function(){" + js + "})();</script></body></html>")

# ---- Content config for the Custom Lululemon page (content ONLY) ----
LULULEMON = {
    "title": "Custom Lululemon",
    "nav_brands": ["Lululemon", "Rhone", "Vuori", "Alo Yoga"],
    "hero": {
        "title": 'Custom <span class="hl">Lululemon</span> Apparel<br>&amp; Gifts with Logo Embroidery',
        "sub": "We embroider Lululemon ABC pants, Define jackets, Scuba hoodies, and Everywhere Belt Bags for corporate "
               "gifting programs that need the apparel to be recognized — and worn — long after the event.",
        "images": ["pat01", "pat02", "pat03", "pat04"], "cta": "Talk to a Merch Expert"},
    "stats": [("clock", "Lead time", "4–6 weeks"), ("box", "MOQ", "Varies by style"),
              ("needle", "Decoration", "Embroidery"), ("note", "Pricing", "Retail + 10% + dec.")],
    "why": {
        "eyebrow": "Why Custom Lululemon", "title": "Pieces people already trust.<br>Logos that don't get in the way.",
        "paras": [
            "Lululemon has built a reputation for performance, comfort, and design that simply works — clean silhouettes, "
            "technical fabrics, and pieces that move from workout to workday. That's a strong starting point for custom "
            "apparel that already feels premium before your logo shows up.",
            "When we add a logo with clean, low-profile embroidery, the result is subtle and intentional — never overdone. "
            "These are pieces your team and clients will actually wear: on travel days, at the gym, or between meetings.",
            "Custom Lululemon works hardest where the audience is brand-aware and the gift needs to feel earned — "
            "onboarding kits, wellness programs, executive retreats, and small-batch client thank-yous."],
        "img": "pat04", "alt": "Lululemon embroidery detail"},
    "callout": {
        "eyebrow": "What to know, before we get started", "title": "LULULEMON IS A<br>PREMIUM RETAIL BRAND.",
        "body": "Lululemon operates as a premium retail brand, which calls for a different approach than standard "
                "customization. We're clear upfront so you can decide if it's the right fit.",
        "cards": [
            ("note", "Pricing model", "Retail cost + 10% sourcing fee + decoration (typically $10–15 per location), "
             "plus applicable tax and shipping.", "pink"),
            ("box", "MOQs vary", "Minimums depend on style, size run, and live inventory. Smaller runs are possible on "
             "accessories and core styles like the Everywhere Belt Bag; larger size-spread orders need more lead time.", "yellow"),
            ("history", "Flexible timelines", "Inventory changes daily and isn't fully visible in real time. Plan four to "
             "six weeks from approval — not recommended for rush orders.", "mint")]},
    "customize": {
        "eyebrow": "What We Customize", "title": "Across Lululemon&rsquo;s catalog.",
        "cards": [
            ("pat01", "Men&rsquo;s Tops, Layers &amp; Bottoms",
             "Metal Vent Tech tees · Evolution polos · Steady State &amp; Scuba hoodies · Define &amp; City Sweat zips · "
             "ABC &amp; Commission pants · Pace Breaker shorts", "mint"),
            ("pat02", "Women&rsquo;s Tops, Layers &amp; Bottoms",
             "Swiftly Tech tees · Define jacket · Scuba oversized hoodie · Ever-Wear tee · Align leggings · "
             "Wunder Train tights · Groove flared pants", "blue"),
            ("pat03", "Accessories &amp; Gifting",
             "Everywhere Belt Bag (1L, 2L) · Daily Multi-Pocket &amp; Command the Day duffels · Yoga Mat 5mm · "
             "Wunder Puff vest / jacket", "pink")]},
    "who": {
        "eyebrow": "Who Orders Custom Lululemon", "title": "Built for brand-aware gifting moments.",
        "cards": [("gift", "Client &amp; VIP gifts"), ("heart", "Wellness programs"),
                  ("brief", "Executive retreats"), ("box", "Onboarding kits")]},
    "decorate": {
        "eyebrow": "How We Decorate", "title": "Four techniques. One signature.",
        "cards": [
            ("pat01", "Embroidery", "Thread-stitched logos with tight digitizing.",
             ["Up to 15,000 stitches standard", "Metallic / tonal thread available", "3D puff on demand"], "yellow", "Signature"),
            ("pat04", "Woven Patches", "Leather, felt, PVC, or fully-woven patches.",
             ["Leather, felt, PVC, woven", "Stitch or heat-applied", "Rush-sampling available"], "mint", "Signature"),
            ("pat03", "Laser Etch", "Subtle, permanent, eye-catching on waxed canvas, leather, and synthetics.",
             ["Waxed canvas + leather", "Zero-ink, permanent", "Tonal, understated finish"], "blue", "New"),
            ("pat02", "Screen Print", "For tees, hoodies, and anywhere embroidery is too much.",
             ["Up to 6 colors", "Water-based + discharge inks", "Puff, metallic, glow"], "pink", "Signature")]},
    "process": {
        "eyebrow": "The Process", "title": "Quote to doorstep, in under two weeks.",
        "steps": [
            ("01", "Quote", "24 hr reply", "Tell us what you want. We come back with pricing, lead time, and honest recommendations."),
            ("02", "Sample", "3–5 days", "We stitch or print a physical sample. You sign off before a single blank is touched."),
            ("03", "Production", "5–8 days", "Your run is decorated in-house — embroidery, patches, whatever the brief calls for."),
            ("04", "Ship", "Any address", "Bulk, split-ship to employees, or into our fulfillment program. We handle it.")]},
    "faq": {
        "title": 'WHAT PEOPLE ASK ABOUT<br>CUSTOM <span class="pink">LULULEMON.</span>',
        "items": [
            ("Can Lululemon be embroidered with our logo?",
             "Yes. Custom Lululemon is typically done with clean, low-profile embroidery that complements the garment's "
             "technical fabrics — never bulky or overpowering. Screen-print and heat-transfer are available on select styles."),
            ("What's the minimum order for Custom Lululemon?",
             "It varies by style, size run, and live inventory. Accessories and core styles like the Everywhere Belt Bag "
             "run smaller; broad size-spread orders need more. We confirm exact minimums in your quote."),
            ("How long does production take?",
             "Plan four to six weeks from art approval. Lululemon inventory shifts daily, so we build in time to source and "
             "decorate cleanly — it's not a rush-order program."),
            ("Which Lululemon styles can we customize?",
             "Most of the catalog — ABC and Commission pants, Define and City Sweat zips, Scuba and Steady State hoodies, "
             "Metal Vent tees, Align and Wunder Train bottoms, and the Everywhere Belt Bag."),
            ("Why is Lululemon priced differently than other custom apparel?",
             "Because we source it at retail rather than wholesale: retail cost + a 10% sourcing fee + decoration, plus tax "
             "and shipping. You're paying for genuine Lululemon your team will actually wear.")]},
    "alternatives": {
        "title": 'PREMIUM BRANDS WE<br>HAVE <span class="acc">WHOLESALE</span> ON',
        "sub": "If retail-plus pricing or rush timelines don't fit, we hold wholesale relationships with brands that compete "
               "directly with Lululemon — same premium feel, easier process, better inventory visibility.",
        "brands": ["Rhone", "Vuori", "Alo Yoga"], "cta": "Browse all premium brands"},
    "form": {"quantities": ["12–49", "50–199", "200–499", "500+"]},
    "footer": {"columns": [
        ("Services", ["Custom Screen Printing", "Cut & Sew", "Custom Dupes", "On-Demand Swag Stores", "Rush Orders", "Swag Fulfillment"]),
        ("Locations", ["Louisville", "Washington DC", "Detroit", "Denver", "Miami", "Nashville", "New York"]),
        ("Resources", ["FAQ", "Merch Glossary", "Request a Quote", "Custom Design", "Shopify Integration"])]},
}

def render_lululemon_preview():
    return render_brand_page(LULULEMON)

# ---- Content config for the Custom Under Armour page (content ONLY) ----
# Wholesale brand → no "what to know" callout; 4 "what we customize" cards.
UNDER_ARMOUR = {
    "title": "Custom Under Armour",
    "nav_brands": ["Patagonia", "Lululemon", "Under Armour", "Vuori"],
    "hero": {
        "title": 'Custom <span class="hl">Under Armour</span> Apparel<br>with Logo Embroidery',
        "sub": "Crooked Monkey decorates Under Armour for corporate teams, golf tournaments and athletic departments — "
               "Tech polos, Playoff polos, Storm fleece and Hustle backpacks with logo embroidery, ordered at wholesale.",
        "images": ["pat02", "pat04", "pat03", "pat01"], "cta": "Talk to a Merch Expert"},
    "stats": [("users", "Relationship", "Wholesale since '08"), ("clock", "Lead time", "2–3 weeks"),
              ("box", "MOQ", "24 pieces"), ("needle", "Decoration", "Embroidery")],
    "why": {
        "eyebrow": "Why brand with Under Armour", "title": "Performance gear teams<br>actually want to wear.",
        "paras": [
            "Founded in Baltimore in 1996, Under Armour built its reputation on the locker-room basics that changed how "
            "athletes dress — moisture-wicking Tech polos, Storm-treated fleece, and the Playoff polo that's become a "
            "fixture in pro-am golf bags. It's an athletic, performance-driven aesthetic, and that's exactly why it lands "
            "with corporate sports leagues, golf tournaments, and athletic departments.",
            "Embroidery is the signature on Tech polos, Playoff polos, Storm fleece, 1/4-zips, hats and Hustle backpacks. "
            "Heat transfer covers Tech 2.0 short-sleeves and Performance Tees where embroidery would compromise the "
            "technical fabric, and sublimation handles event-day jerseys — clean branding that respects how the garment was built.",
            "Because we hold a wholesale relationship with Under Armour, you get consistent inventory visibility, "
            "color-matched kits across men's and women's cuts, and pricing that works for tournament gifting, employee "
            "programs, and athletic-department uniforms."],
        "img": "pat02", "alt": "Under Armour embroidery detail"},
    # no "callout" key — wholesale brand, no retail-plus caveat to flag
    "customize": {
        "eyebrow": "What We Customize", "title": "Across Under Armour&rsquo;s performance catalog.",
        "cards": [
            ("pat02", "Tech &amp; Playoff Polos", "The Playoff polo is the golf-tournament signature; the Tech polo is the "
             "year-round corporate workhorse. Embroidered at left chest, sleeve, or back yoke.", "mint"),
            ("pat04", "Storm Fleece &amp; 1/4-Zips", "Storm-treated fleece, softshell jackets, and Tech 1/4-zips for "
             "cooler-weather programs. Embroidered logos and team identifiers hold up cleanly.", "blue"),
            ("pat03", "Tech 2.0 &amp; Performance Tees", "Tech 2.0 short-sleeves and Performance Tees decorated by heat "
             "transfer where embroidery would compromise the moisture-wicking build. Sublimation on event-day jerseys.", "pink"),
            ("pat01", "Hustle Backpacks, Hats &amp; Accessories", "Hustle backpacks and gym bags for travel kits and "
             "onboarding, plus the Signature Low-Profile cap and other Under Armour silhouettes — all embroidered.", "yellow")]},
    "who": {
        "eyebrow": "Who Orders Custom Under Armour", "title": "Built for athletic and team-driven moments.",
        "cards": [("trophy", "Golf tournaments"), ("users", "Corporate sports &amp; team-building"),
                  ("flag", "School athletic departments"), ("shield", "Military &amp; first-responder programs")]},
    "decorate": {
        "eyebrow": "How We Decorate", "title": "Four techniques. One signature.",
        "cards": [
            ("pat01", "Embroidery", "Thread-stitched logos with tight digitizing. Our default for fleece and softshells.",
             ["Up to 15,000 stitches standard", "Metallic + tonal thread available", "3D puff on demand"], "yellow", "Signature"),
            ("pat04", "Woven Patches", "Leather, felt, PVC, or fully-woven patches applied via heat or stitch.",
             ["Leather, felt, PVC, woven", "Stitch or heat-applied", "Rush-sampling available"], "mint", None),
            ("pat03", "Laser Etch", "Subtle, permanent, eye-catching on waxed canvas, leather, and synthetics.",
             ["Waxed canvas + leather", "Zero-ink, permanent", "Tonal, understated finish"], "blue", "New"),
            ("pat02", "Screen Print", "For tees, hoodies, and anywhere embroidery is too much.",
             ["Up to 6 colors", "Water-based + discharge inks", "Puff, metallic, glow"], "pink", None)]},
    "process": {
        "eyebrow": "The Process", "title": "Quote to doorstep, in under two weeks.",
        "steps": [
            ("01", "Quote", "24 hr reply", "Tell us what you want. We come back with pricing, lead time, and honest recommendations."),
            ("02", "Sample", "3–5 days", "We stitch or print a physical sample. You sign off before a single blank is touched."),
            ("03", "Production", "5–8 days", "Your run is decorated in-house — embroidery, patches, whatever the brief calls for."),
            ("04", "Ship", "Any address", "Bulk, split-ship to employees, or into our fulfillment program. We handle it.")]},
    "faq": {
        "title": 'WHAT PEOPLE ASK ABOUT<br>CUSTOM <span class="pink">UNDER ARMOUR.</span>',
        "items": [
            ("What's the standard decoration method on Under Armour?",
             "Embroidery is the signature on Tech polos, Playoff polos, Storm fleece, 1/4-zips, hats, and Hustle backpacks. "
             "Heat transfer is used on Tech 2.0 short-sleeves and Performance Tees where embroidery would compromise the "
             "technical fabric. Sublimation handles jerseys for event-day uniforms."),
            ("Can I mix men's and women's cuts on one order?",
             "Yes. Because we order at wholesale, we color-match kits across men's and women's cuts so a mixed team roster "
             "ships as one coordinated set."),
            ("What's the minimum order for custom Under Armour?",
             "Minimums start at 24 pieces and can flex by style and decoration method. We confirm the exact minimum for "
             "your garments in the quote."),
            ("How long does production take?",
             "About 2–3 weeks from art approval — faster than retail-sourced brands because we hold a wholesale account. "
             "Rush options are available on many styles."),
            ("Where does Under Armour sit on the premium ladder?",
             "It's the athletic, performance-driven pick — ideal for golf, corporate sports, and athletic departments. For a "
             "country-club or athleisure feel, Peter Millar, TravisMathew, or Vuori tend to land better.")]},
    "alternatives": {
        "title": 'OTHER PREMIUM BRANDS<br>WE <span class="acc">CUSTOMIZE</span>',
        "sub": "Under Armour leans athletic and performance-driven. If you want a country-club or heritage look, or a softer "
               "athleisure feel for client gifting, a few sibling brands tend to land better.",
        "brands": ["Peter Millar", "TravisMathew", "Vuori"], "cta": "Browse all premium brands"},
    "form": {"quantities": ["12–49", "50–199", "200–499", "500+"]},
    "footer": {"columns": [
        ("Services", ["Custom Screen Printing", "Cut & Sew Manufacturing", "Custom Apparel Dupes", "On-Demand Swag Stores", "Rush Orders", "Swag Fulfillment"]),
        ("Locations", ["Louisville", "Washington DC", "Detroit", "Denver", "Miami", "Nashville", "New York"]),
        ("Resources", ["FAQ", "Merch Glossary", "Request a Quote", "Custom Design", "Shopify Integration"])]},
}

def render_underarmour_preview():
    return render_brand_page(UNDER_ARMOUR)

def main():
    n = 0
    open(os.path.join(_HERE, "index.html"), "w").write(render_index())
    n += 1
    for key, label, color, eyebrow, blurb in COLLECTIONS:
        open(os.path.join(_HERE, key + ".html"), "w").write(render_collection(key, label, blurb))
        n += 1
    open(os.path.join(_HERE, "preview-landing.html"), "w").write(render_landing_preview())
    n += 1
    open(os.path.join(_HERE, "preview-lululemon.html"), "w").write(render_lululemon_preview())
    n += 1
    open(os.path.join(_HERE, "preview-under-armour.html"), "w").write(render_underarmour_preview())
    n += 1
    # preview-premium.html is a committed static copy of the built Patagonia page
    # (keeps its scroll-pinning); it is not regenerated here.
    for e in REGISTRY:
        open(os.path.join(_HERE, e["slug"] + ".html"), "w").write(render_component(e))
        n += 1

    # ---- Component manifest: the single lookup for "which component to call" ----
    # handle (kebab-case slug) is the stable name; call is the exact cm.* function.
    manifest = {"components": [
        {"handle": e["slug"], "name": e["name"], "tier": e["eyebrow"].title(),
         "color": tier_color(e["eyebrow"]), "pages": sorted(pages_of(e["slug"])),
         "call": entry_call(e), "url": e["slug"] + ".html"}
        for e in REGISTRY]}
    open(os.path.join(_HERE, "manifest.json"), "w").write(
        json.dumps(manifest, indent=2, ensure_ascii=False))
    n += 1
    print(f"written {n} files: index + {len(COLLECTIONS)} collections + 2 previews + "
          f"{len(REGISTRY)} components + manifest.json")

if __name__ == "__main__":
    main()
