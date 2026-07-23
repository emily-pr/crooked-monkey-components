"""cm_kit.py — Crooked Monkey shared component kit.

Import this from any page build script to reuse design tokens and components.
The generated HTML stays self-contained: emit_css()/root_css() return strings
you embed inside a single <style> block. Only the *source* depends on this kit.

Usage (in a page build script):
    import cm_kit as cm
    style = "<style>" + cm.root_css() + cm.notch_css() + my_page_css + "</style>"
    html  = cm.notch_card(inner="...", side="r", bg="var(--blue)")
"""
import urllib.parse
import html as _html

# ---------------------------------------------------------------------------
# Design tokens — single source of truth. Edit here, every page follows.
# ---------------------------------------------------------------------------
TOKENS = {
    "cream": "#FDF9EA", "ink": "#041202",
    "yellow": "#FBF79E", "blue": "#94DFFA", "pink": "#F580B1", "mint": "#6EE8BE",
    "yellow-deep": "#474400", "blue-deep": "#003547",
    "pink-deep": "#47001E", "mint-deep": "#05432D",
}

# Semantic aliases (roles) + radius scale — reference primitives, never raw hex.
SEMANTIC = {
    "bg": "var(--cream)", "fg": "var(--ink)", "cta": "var(--yellow)",
    "border": "var(--ink)",
    "surface-yellow": "var(--yellow)", "surface-blue": "var(--blue)",
    "surface-pink": "var(--pink)", "surface-mint": "var(--mint)",
    "on-yellow": "var(--yellow-deep)", "on-blue": "var(--blue-deep)",
    "on-pink": "var(--pink-deep)", "on-mint": "var(--mint-deep)",
    "r-pill": "999px", "r-card": "clamp(18px,1.6vw,26px)",
    "r-card-lg": "clamp(22px,2.4vw,40px)", "r-sm": "10px", "r-flat": "6px",
}

def root_css():
    """Return the :root{} block with all brand tokens (primitive + semantic)."""
    prim = "".join(f"--{k}:{v};" for k, v in TOKENS.items())
    sem = "".join(f"--{k}:{v};" for k, v in SEMANTIC.items())
    return ":root{" + prim + sem + "}"

# ---------------------------------------------------------------------------
# Adaptive K-notch card
# ---------------------------------------------------------------------------
# The "K" cut is a FIXED-SIZE SVG mask (px, not %) subtracted from one or both
# sides with mask-composite. Because its size is fixed, the cut keeps its drawn
# proportion at ANY card height — the straight body edges absorb the extra
# height and the notch stays vertically centered. Rounded corners use
# border-radius (native, never distorts).
#
# Trade-off: the notch is a fixed height (NOTCH_H px). On cards TALLER than that
# it centers nicely; on cards SHORTER than NOTCH_H it would clip — pass a smaller
# notch_h in that case. Browser note: needs mask-composite (Chrome/Edge/Firefox
# modern). Safari uses -webkit-mask-composite:source-out, already emitted below.

NOTCH_DEPTH = 40.29   # px the cut bites in from the edge
NOTCH_H     = 173.0   # native height of the cut shape (px)

# Half-curves of the tooth, lifted verbatim from the client's Card_Shape_1 art
# so the silhouette matches the original drawing exactly.
_UP   = "c11.69,-7.96 21.21,-18.78 28.56,-32.43 7.35,-13.67 11.25,-30.54 11.73,-50.61"
_DOWN = "c-.48,-20.08 -4.38,-36.93 -11.73,-50.6 -7.35,-13.67 -16.87,-24.47 -28.56,-32.43"

def notch_mask_uri(flip=False):
    """data: URI of the tooth to subtract. flip=True mirrors it to the left side."""
    d = (f"M0,86.51 {_UP} L{NOTCH_DEPTH:.2f},0 "
         f"L{NOTCH_DEPTH:.2f},173 L{NOTCH_DEPTH:.2f},169.53 {_DOWN} Z")
    g = f"<path fill='#000' d='{d}'/>"
    if flip:
        g = f"<g transform='translate({NOTCH_DEPTH:.2f},0) scale(-1,1)'>{g}</g>"
    s = (f"<svg xmlns='http://www.w3.org/2000/svg' "
         f"viewBox='0 0 {NOTCH_DEPTH:.2f} 173'>{g}</svg>")
    return "data:image/svg+xml," + urllib.parse.quote(s, safe="")

_NR = notch_mask_uri(False)   # tooth on the right
_NL = notch_mask_uri(True)    # tooth on the left

def _notch_decls(side, depth, notch_h, radius, flat):
    """Return the CSS declarations (no selector) for one notch variant.

    notch_h: number -> fixed px height (cut keeps exact proportion).
             "100%" (or any CSS length) -> cut fills the card height edge-to-edge
             while depth stays fixed (use this for tall cards).
    """
    D = f"{depth:.2f}"
    H = notch_h if isinstance(notch_h, str) else f"{notch_h:.2f}px"
    if side == "r":          # notch right, rounded left
        rad = f"border-radius:{radius}px {flat}px {flat}px {radius}px;"
        layers = (f"-webkit-mask-image:linear-gradient(#fff,#fff),url(\"{_NR}\");"
                  f"mask-image:linear-gradient(#fff,#fff),url(\"{_NR}\");"
                  f"-webkit-mask-size:100% 100%,{D}px {H};mask-size:100% 100%,{D}px {H};"
                  f"-webkit-mask-position:0 0,right center;mask-position:0 0,right center;"
                  f"-webkit-mask-composite:source-out;mask-composite:subtract")
    elif side == "l":        # notch left, rounded right
        rad = f"border-radius:{flat}px {radius}px {radius}px {flat}px;"
        layers = (f"-webkit-mask-image:linear-gradient(#fff,#fff),url(\"{_NL}\");"
                  f"mask-image:linear-gradient(#fff,#fff),url(\"{_NL}\");"
                  f"-webkit-mask-size:100% 100%,{D}px {H};mask-size:100% 100%,{D}px {H};"
                  f"-webkit-mask-position:0 0,left center;mask-position:0 0,left center;"
                  f"-webkit-mask-composite:source-out;mask-composite:subtract")
    else:                    # both sides
        rad = f"border-radius:{flat}px;"
        layers = (f"-webkit-mask-image:linear-gradient(#fff,#fff),url(\"{_NR}\"),url(\"{_NL}\");"
                  f"mask-image:linear-gradient(#fff,#fff),url(\"{_NR}\"),url(\"{_NL}\");"
                  f"-webkit-mask-size:100% 100%,{D}px {H},{D}px {H};"
                  f"mask-size:100% 100%,{D}px {H},{D}px {H};"
                  f"-webkit-mask-position:0 0,right center,left center;"
                  f"mask-position:0 0,right center,left center;"
                  f"-webkit-mask-composite:source-out,source-out;"
                  f"mask-composite:subtract,subtract")
    return rad + "-webkit-mask-repeat:no-repeat;mask-repeat:no-repeat;" + layers

def notch_css(depth=NOTCH_DEPTH, notch_h=NOTCH_H, radius=22, flat=6):
    """CSS for the notch-card component using the kit's own classes.

    radius = rounded corner radius (px); flat = near-straight corner (px).
    Classes:  .k-card.k-r (notch right) | .k-l (notch left) | .k-both (both).
    Apply background, width and height yourself on the element.
    """
    return (
        "/* ---- CM: adaptive K-notch card (keeps cut proportion at any height) ---- */"
        + ".k-card.k-r{"   + _notch_decls("r",    depth, notch_h, radius, flat) + "}"
        + ".k-card.k-l{"   + _notch_decls("l",    depth, notch_h, radius, flat) + "}"
        + ".k-card.k-both{" + _notch_decls("both", depth, notch_h, radius, flat) + "}"
    )

def notch_layer_css(selector, side, depth=NOTCH_DEPTH, notch_h=NOTCH_H,
                    radius=22, flat=6, important=False):
    """Emit the notch rules for an ARBITRARY selector (e.g. '.proc.m1 .proc-bg').

    Lets you keep your own markup (a separate background layer) while still
    sourcing the cut from the kit. side in {'r','l','both'}.
    """
    decls = _notch_decls(side, depth, notch_h, radius, flat)
    if important:
        decls = decls.replace(";", " !important;")
    return f"{selector}{{{decls}}}"

_SIDE = {"r": "k-r", "l": "k-l", "both": "k-both"}

def notch_card(inner="", side="r", bg="var(--blue)", cls="", style=""):
    """Render a notch-card <article>. side in {'r','l','both'}.

    Set width/height via `style` or your own CSS on `cls`. Background defaults
    to a brand token; pass any color/var.
    """
    return (f'<article class="k-card {_SIDE[side]} {cls}" '
            f'style="background:{bg};{style}">{inner}</article>')


# ===========================================================================
# Seed components — every one follows the SAME shape as the notch card:
#   a *_css() that returns a CSS string you embed ONCE, plus a render helper
#   that returns an HTML string. (Interactive ones also expose a *_js() string.)
# This is the pattern to copy when adding a new component — see the catalog
# README's "Add a component" flow.
# ===========================================================================

# ---------------------------------------------------------------------------
# Button — primary (CTA) + outline
# ---------------------------------------------------------------------------
def button_css():
    """CSS for .cm-btn (+ --primary / --outline). Emit once."""
    return (
        "/* ---- CM: button ---- */"
        ".cm-btn{display:inline-flex;align-items:center;justify-content:center;"
        "border-radius:var(--r-pill);padding:14px 28px;"
        "font:700 14px/1 Inter,system-ui,sans-serif;letter-spacing:.04em;"
        "text-transform:uppercase;cursor:pointer;text-decoration:none;"
        "border:1.5px solid var(--ink);"
        "transition:transform .2s ease,background .2s ease,color .2s ease}"
        ".cm-btn:focus-visible{outline:3px solid var(--ink);outline-offset:3px}"
        ".cm-btn--primary{background:var(--cta);color:var(--ink);border-color:transparent}"
        ".cm-btn--outline{background:transparent;color:var(--ink)}"
        ".cm-btn--outline:hover{background:var(--ink);color:var(--cream)}"
        "@media (prefers-reduced-motion:no-preference){"
        ".cm-btn--primary:hover{transform:translateY(-2px)}}"
    )

def button(label, variant="primary", href="#", cls="", style=""):
    """Render a button link. variant in {'primary','outline'}."""
    v = "cm-btn--outline" if variant == "outline" else "cm-btn--primary"
    return f'<a class="cm-btn {v} {cls}" href="{href}" style="{style}">{_html.escape(label)}</a>'

# ---------------------------------------------------------------------------
# Premium pill (Poppins 900, "crooked" hover)
# ---------------------------------------------------------------------------
def pill_css():
    """CSS for .cm-pill. Emit once. Hover is the brand 'crooked' tilt."""
    return (
        "/* ---- CM: premium pill ---- */"
        ".cm-pill{display:inline-block;font-family:Poppins,sans-serif;font-weight:900;"
        "font-size:13px;letter-spacing:.02em;text-transform:uppercase;color:var(--ink);"
        "border:1.5px solid var(--ink);border-radius:var(--r-pill);padding:11px 20px;"
        "background:transparent;white-space:nowrap;"
        "transition:transform .15s ease,background .15s ease,color .15s ease}"
        "@media (prefers-reduced-motion:no-preference){"
        ".cm-pill:hover{transform:rotate(-2deg) translateY(-2px)}}"
    )

def pill(label, bg=None, cls="", style=""):
    """Render a Premium-brand pill. Pass bg=a bright token for a filled pill."""
    st = f"background:{bg};border-color:transparent;{style}" if bg else style
    return f'<span class="cm-pill {cls}" style="{st}">{_html.escape(label)}</span>'

# ---------------------------------------------------------------------------
# Form input (labelled field)
# ---------------------------------------------------------------------------
def input_css():
    """CSS for .cm-field (label + input/textarea). Emit once."""
    return (
        "/* ---- CM: form field ---- */"
        ".cm-field{display:flex;flex-direction:column;gap:8px;max-width:360px}"
        ".cm-field label{font:700 12px/1 Inter,system-ui,sans-serif;letter-spacing:.14em;"
        "text-transform:uppercase;color:rgba(4,18,2,.6)}"
        ".cm-field input,.cm-field textarea{width:100%;background:#fff;color:var(--ink);"
        "border:1.5px solid rgba(4,18,2,.18);border-radius:var(--r-sm);padding:14px 16px;"
        "font:500 15px/1.4 Inter,system-ui,sans-serif;"
        "transition:border-color .18s ease,box-shadow .18s ease}"
        ".cm-field input::placeholder,.cm-field textarea::placeholder{color:rgba(4,18,2,.45)}"
        ".cm-field input:focus,.cm-field textarea:focus{outline:none;border-color:var(--ink);"
        "box-shadow:0 0 0 3px rgba(4,18,2,.12)}"
    )

def field(label, name="", type="text", placeholder="", cls="", style=""):
    """Render a labelled form field. Label sits above in uppercase Label style."""
    fid = "f-" + (name or label.lower().replace(" ", "-"))
    return (f'<div class="cm-field {cls}" style="{style}">'
            f'<label for="{fid}">{_html.escape(label)}</label>'
            f'<input id="{fid}" name="{name}" type="{type}" '
            f'placeholder="{_html.escape(placeholder)}"></div>')

# ---------------------------------------------------------------------------
# FAQ accordion (one open at a time; height animates via grid-rows)
# ---------------------------------------------------------------------------
def faq_css():
    """CSS for .cm-faq. Emit once. Mint surface, ink title, +/- indicator."""
    return (
        "/* ---- CM: FAQ accordion ---- */"
        ".cm-faq{display:flex;flex-direction:column;gap:14px;max-width:660px}"
        ".cm-faq-item{background:var(--surface-mint);border-radius:var(--r-card)}"
        ".cm-faq-q{display:flex;align-items:center;gap:20px;width:100%;text-align:left;"
        "background:none;border:0;cursor:pointer;font-family:Poppins,sans-serif;font-weight:900;"
        "text-transform:uppercase;letter-spacing:-.005em;line-height:1.14;font-size:16px;"
        "color:var(--ink);padding:22px 24px;border-radius:inherit}"
        ".cm-faq-q:focus-visible{outline:3px solid var(--ink);outline-offset:-3px}"
        ".cm-faq-q-tx{flex:1}"
        ".cm-faq-ico{flex:none;position:relative;width:24px;height:24px}"
        ".cm-faq-ico::before,.cm-faq-ico::after{content:'';position:absolute;background:var(--ink);border-radius:2px}"
        ".cm-faq-ico::before{left:0;right:0;top:50%;height:3px;margin-top:-1.5px}"
        ".cm-faq-ico::after{top:0;bottom:0;left:50%;width:3px;margin-left:-1.5px;"
        "transition:opacity .25s ease,transform .3s cubic-bezier(.2,.75,.2,1)}"
        ".cm-faq-item.open .cm-faq-ico::after{opacity:0;transform:scaleY(0)}"
        ".cm-faq-a{display:grid;grid-template-rows:0fr;transition:grid-template-rows .32s cubic-bezier(.2,.75,.2,1)}"
        ".cm-faq-item.open .cm-faq-a{grid-template-rows:1fr}"
        ".cm-faq-a-in{overflow:hidden}"
        ".cm-faq-a-in p{margin:0;padding:0 24px 22px;font:500 15px/1.55 Inter,system-ui,sans-serif;"
        "color:rgba(4,18,2,.72);max-width:60ch}"
    )

def faq(items):
    """Render an accordion. items = list of (question, answer). First is open."""
    rows = []
    for i, (q, a) in enumerate(items):
        op = (i == 0)
        rows.append(
            f'<div class="cm-faq-item{" open" if op else ""}">'
            f'<button class="cm-faq-q" id="cm-faq-q-{i}" aria-expanded="{"true" if op else "false"}" '
            f'aria-controls="cm-faq-a-{i}"><span class="cm-faq-q-tx">{_html.escape(q)}</span>'
            f'<span class="cm-faq-ico" aria-hidden="true"></span></button>'
            f'<div class="cm-faq-a" id="cm-faq-a-{i}" role="region" aria-labelledby="cm-faq-q-{i}">'
            f'<div class="cm-faq-a-in"><p>{_html.escape(a)}</p></div></div></div>')
    return '<div class="cm-faq">' + "".join(rows) + '</div>'

def faq_js():
    """JS wiring for .cm-faq — one open at a time. Emit once (inside a <script>)."""
    return (
        "/* CM FAQ accordion: one panel open at a time. */"
        "[].slice.call(document.querySelectorAll('.cm-faq')).forEach(function(root){"
        "var items=[].slice.call(root.querySelectorAll('.cm-faq-item'));"
        "items.forEach(function(it){var btn=it.querySelector('.cm-faq-q');if(!btn)return;"
        "btn.addEventListener('click',function(){"
        "var willOpen=!it.classList.contains('open');"
        "items.forEach(function(o){o.classList.remove('open');"
        "o.querySelector('.cm-faq-q').setAttribute('aria-expanded','false');});"
        "if(willOpen){it.classList.add('open');btn.setAttribute('aria-expanded','true');}});});});"
    )

# ---------------------------------------------------------------------------
# Nav — ink bar, cream logo, Poppins links, dropdowns + mobile drawer
# ---------------------------------------------------------------------------
_NAV_CARET = ("<svg class='cm-nav-caret' viewBox='0 0 10 6' aria-hidden='true'>"
              "<path d='M1 1l4 4 4-4' fill='none' stroke='currentColor' stroke-width='1.6' "
              "stroke-linecap='round' stroke-linejoin='round'/></svg>")

def nav_css():
    """CSS for .cm-nav. Emit once. NOTE: on a real page use position:fixed
    (add .cm-nav{position:fixed;top:0;left:0;right:0} or wrap in your own)."""
    return (
        "/* ---- CM: nav ---- */"
        ".cm-nav{background:var(--ink);color:var(--cream);border-bottom:1px solid rgba(253,249,234,.1)}"
        ".cm-nav-in{max-width:1480px;margin:0 auto;display:flex;align-items:center;"
        "gap:clamp(16px,1.8vw,28px);padding:0 clamp(18px,4vw,40px);height:clamp(60px,8vh,74px)}"
        ".cm-nav-logo{flex:none;display:flex;align-items:center}"
        ".cm-nav-logo img{height:26px;width:auto;display:block}"
        ".cm-nav-mid{display:flex;align-items:center;gap:clamp(16px,1.9vw,30px);margin-left:auto}"
        ".cm-nav-link,.cm-nav-trigger{font:900 12.5px/1 Poppins,sans-serif;letter-spacing:.05em;"
        "text-transform:uppercase;color:var(--cream);text-decoration:none;background:none;border:0;"
        "cursor:pointer;display:inline-flex;align-items:center;gap:7px;padding:10px 0;white-space:nowrap;"
        "transition:color .18s ease}"
        ".cm-nav-link:hover,.cm-nav-trigger:hover,.cm-nav-trigger[aria-expanded=true]{color:var(--yellow)}"
        ".cm-nav-caret{width:9px;height:6px;transition:transform .22s ease}"
        ".cm-nav-dd{position:relative}"
        ".cm-nav-dd.open .cm-nav-caret{transform:rotate(180deg)}"
        ".cm-nav-menu{position:absolute;top:calc(100% + 9px);left:50%;min-width:240px;background:var(--cream);"
        "color:var(--ink);border-radius:16px;padding:10px;box-shadow:0 30px 60px -24px rgba(4,18,2,.55);"
        "display:flex;flex-direction:column;gap:2px;opacity:0;visibility:hidden;"
        "transform:translateX(-50%) translateY(8px);"
        "transition:opacity .18s ease,transform .18s ease,visibility .18s;z-index:10}"
        ".cm-nav-dd:hover .cm-nav-menu,.cm-nav-dd.open .cm-nav-menu{opacity:1;visibility:visible;"
        "transform:translateX(-50%) translateY(0)}"
        ".cm-nav-menu a{font:600 14px/1.2 Inter,system-ui,sans-serif;color:var(--ink);text-decoration:none;"
        "padding:11px 14px;border-radius:10px;white-space:nowrap;transition:background .15s ease}"
        ".cm-nav-menu a:hover{background:rgba(4,18,2,.06)}"
        ".cm-nav-cta{flex:none;background:var(--yellow);color:var(--ink);border-radius:999px;padding:11px 24px;"
        "font:900 12.5px/1 Poppins,sans-serif;letter-spacing:.04em;text-transform:uppercase;text-decoration:none;"
        "white-space:nowrap;transition:transform .2s ease,filter .2s ease}"
        ".cm-nav-cta:hover{transform:translateY(-1px);filter:brightness(1.03)}"
        ".cm-nav-link:focus-visible,.cm-nav-trigger:focus-visible,.cm-nav-cta:focus-visible,"
        ".cm-nav-logo:focus-visible,.cm-nav-menu a:focus-visible{outline:3px solid var(--yellow);"
        "outline-offset:3px;border-radius:6px}"
        "@media (max-width:820px){.cm-nav-mid{gap:14px}"
        ".cm-nav-menu{position:static;min-width:0;transform:none;opacity:1;visibility:visible;display:none;"
        "box-shadow:none;background:rgba(253,249,234,.05);color:var(--cream);margin:0}"
        ".cm-nav-dd.open .cm-nav-menu{display:flex}.cm-nav-menu a{color:rgba(253,249,234,.82)}}"
    )

def nav(logo_src, links=None, services=None, brands=None, cta="Request a quote"):
    """Render the nav bar. logo_src = data URI / path to the cream logo.
    links = plain links; services/brands = dropdown item lists."""
    links = links or ["Products"]
    services = services or ["Custom Screen Printing", "Embroidery & DTG", "Cut & Sew Manufacturing"]
    brands = brands or ["Patagonia", "YETI", "Lululemon", "The North Face"]
    def _menu(mid, label, items):
        a = "".join(f'<a role="menuitem" href="#">{_html.escape(t)}</a>' for t in items)
        return (f'<div class="cm-nav-dd"><button class="cm-nav-trigger" aria-expanded="false" '
                f'aria-haspopup="true" aria-controls="{mid}">{_html.escape(label)}{_NAV_CARET}</button>'
                f'<div class="cm-nav-menu" id="{mid}" role="menu">{a}</div></div>')
    plain = "".join(f'<a class="cm-nav-link" href="#">{_html.escape(t)}</a>' for t in links)
    return (
        '<header class="cm-nav"><div class="cm-nav-in">'
        f'<a class="cm-nav-logo" href="#" aria-label="Crooked Monkey home">'
        f'<img src="{logo_src}" alt="Crooked Monkey"></a>'
        '<nav class="cm-nav-mid" aria-label="Primary">'
        + plain
        + _menu("cm-dd-services", "Services", services)
        + _menu("cm-dd-brands", "Premium brands", brands)
        + f'<a class="cm-nav-cta" href="#">{_html.escape(cta)}</a>'
        + '</nav></div></header>'
    )

def nav_js():
    """JS wiring for .cm-nav dropdowns (click to pin; hover opens via CSS)."""
    return (
        "/* CM nav: click-to-pin dropdowns; Escape closes. */"
        "var cmDD=[].slice.call(document.querySelectorAll('.cm-nav-dd'));"
        "function cmClose(x){cmDD.forEach(function(d){if(d!==x){d.classList.remove('open');"
        "var t=d.querySelector('.cm-nav-trigger');if(t)t.setAttribute('aria-expanded','false');}});}"
        "cmDD.forEach(function(dd){var t=dd.querySelector('.cm-nav-trigger');"
        "t.addEventListener('click',function(e){e.preventDefault();"
        "var o=dd.classList.toggle('open');t.setAttribute('aria-expanded',o?'true':'false');cmClose(dd);});});"
        "document.addEventListener('click',function(e){if(!e.target.closest('.cm-nav-dd'))cmClose(null);});"
        "document.addEventListener('keydown',function(e){if(e.key==='Escape')cmClose(null);});"
    )


if __name__ == "__main__":
    # tiny smoke test
    print(root_css()[:60], "...")
    print("notch_css length:", len(notch_css()))
    print(notch_card("hi", side="both", bg="var(--pink)")[:80], "...")
    print("button:", button("Request a quote")[:60], "...")
    print("pill:", pill("PATAGONIA")[:60], "...")
