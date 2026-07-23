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
import os, html
import cm_kit as cm

_HERE = os.path.dirname(os.path.abspath(__file__))
def _asset(name):
    return os.path.join(_HERE, "assets", name)

esc = html.escape

# Cream logo, inlined as a data URI for the nav demo (keeps output self-contained).
_logo_svg = open(_asset("cm_logo_cream.svg")).read()
import urllib.parse
LOGO_URI = "data:image/svg+xml," + urllib.parse.quote(_logo_svg, safe="")

# Bright surface -> matching deep accent (design-system: deep accent = text on that bright).
DEEP = {"yellow": "yellow-deep", "blue": "blue-deep", "pink": "pink-deep", "mint": "mint-deep"}

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
.sect h2{font-family:Poppins,sans-serif;font-weight:900;text-transform:uppercase;letter-spacing:-.02em;font-size:clamp(24px,2.6vw,34px);margin-bottom:24px;color:var(--ink)}

/* demo canvas */
.demo{background:#fff;border:1.5px solid rgba(4,18,2,.14);border-radius:var(--r-card);padding:clamp(24px,3vw,40px);display:flex;flex-wrap:wrap;gap:clamp(18px,2vw,32px);align-items:flex-start}
.demo.col{flex-direction:column}
.demo.pad0{padding:0;overflow:hidden}
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
        "slug": "notch-card", "name": "K-Notch Card", "eyebrow": "COMPONENT", "color": "blue",
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
        "slug": "button", "name": "Buttons", "eyebrow": "COMPONENT", "color": "yellow",
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
        "slug": "pill", "name": "Premium Pill", "eyebrow": "COMPONENT", "color": "pink",
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
        "slug": "input", "name": "Form Input", "eyebrow": "COMPONENT", "color": "mint",
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
        "slug": "faq", "name": "FAQ Accordion", "eyebrow": "COMPONENT", "color": "mint",
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
        "slug": "nav", "name": "Nav", "eyebrow": "COMPONENT", "color": "blue",
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

# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------
def render_index():
    order = ["TOKENS", "COMPONENT", "PATTERN"]
    groups = {}
    for e in REGISTRY:
        groups.setdefault(e["eyebrow"], []).append(e)
    blocks = []
    for cat in order:
        items = groups.get(cat)
        if not items:
            continue
        cards = []
        for e in items:
            col, deep = e["color"], DEEP[e["color"]]
            cards.append(
                f'<a class="card" href="{e["slug"]}.html" style="background:var(--{col})">'
                f'<span class="c-eyebrow" style="color:var(--{deep})">{esc(e["eyebrow"])}</span>'
                f'<span class="c-title">{esc(e["name"])}</span>'
                f'<span class="c-blurb">{esc(e["blurb"])}</span>'
                f'<span class="c-go" style="color:var(--{deep})">View <span class="ar">→</span></span></a>')
        label = {"TOKENS": "Tokens", "COMPONENT": "Components", "PATTERN": "Patterns"}[cat]
        blocks.append(f'<div class="cat-group"><h2 class="h-display">{label}</h2>'
                      f'<div class="grid">{"".join(cards)}</div></div>')
    body = ('<div class="wrap"><div class="hero">'
            '<h1 class="h-display">Component<br>Library</h1>'
            '<p class="lead">The Crooked Monkey design system, browsable. Every card is a live demo '
            'plus the exact <code>cm_kit</code> call to reuse it on a new page. Built self-contained '
            'from <code>cm_kit.py</code> — the only external dependency is Google Fonts.</p></div>'
            + "".join(blocks) + '</div>')
    return page("Component Library", body)

def render_component(e):
    demo, css, js = e["builder"]()
    col, deep = e["color"], DEEP[e["color"]]
    # section 2: how to call it
    api_html = ""
    for i, (lab, snippet) in enumerate(e["api"]):
        api_html += code_lab(lab) + code(snippet)
    notes_html = "".join(f'<li>{n}</li>' for n in e["notes"])
    body = ('<div class="wrap">'
            '<a class="back" href="index.html">← All components</a>'
            f'<header class="p-head"><span class="eyebrow" style="color:var(--{deep})">{esc(e["eyebrow"])}</span>'
            f'<h1 class="h-display">{esc(e["name"])}</h1>'
            f'<p class="lead">{esc(e["blurb"])}</p></header>'
            '<section class="sect"><div class="sect-lab">01 — Live demo</div>'
            '<h2>Every variant, rendered</h2>' + demo + '</section>'
            '<section class="sect"><div class="sect-lab">02 — How to call it</div>'
            '<h2>Reuse it on a new page</h2>' + api_html + '</section>'
            '<section class="sect"><div class="sect-lab">03 — When to use it</div>'
            '<h2>Notes &amp; gotchas</h2><ul class="notes">' + notes_html + '</ul></section>'
            '</div>')
    return page(e["name"], body, extra_css=css, extra_js=js)

def main():
    n = 0
    open(os.path.join(_HERE, "index.html"), "w").write(render_index())
    n += 1
    for e in REGISTRY:
        open(os.path.join(_HERE, e["slug"] + ".html"), "w").write(render_component(e))
        n += 1
    print(f"written {n} pages: index.html + {len(REGISTRY)} components")

if __name__ == "__main__":
    main()
