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

_NAV_CART = ("<svg viewBox='0 0 24 24' width='22' height='22' fill='none' stroke='currentColor' "
             "stroke-width='1.7' stroke-linecap='round' stroke-linejoin='round' aria-hidden='true'>"
             "<circle cx='9' cy='20' r='1.4'/><circle cx='18' cy='20' r='1.4'/>"
             "<path d='M2 3h2.2l2.3 11.4a1.5 1.5 0 0 0 1.5 1.2h8.7a1.5 1.5 0 0 0 1.5-1.2L21 7H6.2'/></svg>")

def nav_css():
    """CSS for .cm-nav (ink bar, dropdowns, sign-in + cart, mobile drawer).
    Fixed by default; on a real page add top nav clearance to the first section."""
    return (
        "/* ---- CM: nav ---- */"
        ".cm-nav{position:fixed;top:0;left:0;right:0;z-index:100;background:var(--ink);color:var(--cream);"
        "border-bottom:1px solid rgba(253,249,234,.1)}"
        ".cm-nav-in{max-width:1480px;margin:0 auto;display:flex;align-items:center;"
        "gap:clamp(16px,1.8vw,28px);padding:0 clamp(18px,4vw,56px);height:clamp(62px,8vh,76px)}"
        ".cm-nav-logo{flex:none;display:flex;align-items:center}"
        ".cm-nav-logo img{height:clamp(22px,1.9vw,28px);width:auto;display:block}"
        ".cm-nav-drawer{display:contents}"
        ".cm-nav-mid{display:flex;align-items:center;gap:clamp(16px,1.9vw,30px);margin-left:auto}"
        ".cm-nav-actions{display:flex;align-items:center;gap:clamp(16px,1.6vw,24px);margin-left:auto}"
        ".cm-nav-link,.cm-nav-trigger{font:900 12.5px/1 Poppins,sans-serif;letter-spacing:.05em;"
        "text-transform:uppercase;color:var(--cream);text-decoration:none;background:none;border:0;"
        "cursor:pointer;display:inline-flex;align-items:center;gap:7px;padding:10px 0;white-space:nowrap;"
        "transition:color .18s ease}"
        ".cm-nav-link:hover,.cm-nav-trigger:hover,.cm-nav-trigger[aria-expanded=true]{color:var(--yellow)}"
        ".cm-nav-caret{width:9px;height:6px;transition:transform .22s ease}"
        ".cm-nav-dd{position:relative}"
        ".cm-nav-dd.open .cm-nav-caret{transform:rotate(180deg)}"
        ".cm-nav-menu{position:absolute;top:calc(100% + 9px);left:50%;min-width:248px;background:var(--cream);"
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
        ".cm-nav-signin{font:900 12.5px/1 Poppins,sans-serif;letter-spacing:.05em;text-transform:uppercase;"
        "color:var(--cream);text-decoration:none;white-space:nowrap;transition:color .18s ease}"
        ".cm-nav-signin:hover{color:var(--yellow)}"
        ".cm-nav-cart{color:var(--cream);display:inline-flex;align-items:center;transition:color .18s ease}"
        ".cm-nav-cart:hover{color:var(--yellow)}"
        ".cm-nav-link:focus-visible,.cm-nav-trigger:focus-visible,.cm-nav-cta:focus-visible,"
        ".cm-nav-signin:focus-visible,.cm-nav-cart:focus-visible,.cm-nav-logo:focus-visible,"
        ".cm-nav-burger:focus-visible,.cm-nav-menu a:focus-visible{outline:3px solid var(--yellow);"
        "outline-offset:3px;border-radius:6px}"
        ".cm-nav-burger{display:none;flex:none;width:42px;height:42px;background:none;border:0;cursor:pointer;"
        "flex-direction:column;align-items:center;justify-content:center;gap:5px;margin-left:auto;color:var(--cream)}"
        ".cm-nav-burger span{display:block;width:24px;height:2px;background:currentColor;border-radius:2px;"
        "transition:transform .25s ease,opacity .2s ease}"
        ".cm-nav.open .cm-nav-burger span:nth-child(1){transform:translateY(7px) rotate(45deg)}"
        ".cm-nav.open .cm-nav-burger span:nth-child(2){opacity:0}"
        ".cm-nav.open .cm-nav-burger span:nth-child(3){transform:translateY(-7px) rotate(-45deg)}"
        "@media (max-width:980px){"
        ".cm-nav-burger{display:flex}"
        ".cm-nav-drawer{position:absolute;top:100%;left:0;right:0;background:var(--ink);"
        "border-bottom:1px solid rgba(253,249,234,.1);display:flex;flex-direction:column;align-items:stretch;"
        "gap:4px;padding:14px clamp(18px,4vw,40px) 24px;opacity:0;visibility:hidden;transform:translateY(-10px);"
        "transition:opacity .22s ease,transform .22s ease,visibility .22s;max-height:calc(100vh - 62px);overflow:auto}"
        ".cm-nav.open .cm-nav-drawer{opacity:1;visibility:visible;transform:none}"
        ".cm-nav-mid{flex-direction:column;align-items:stretch;gap:2px;margin-left:0}"
        ".cm-nav-actions{margin:12px 0 0;padding-top:14px;border-top:1px solid rgba(253,249,234,.1);"
        "justify-content:flex-start;gap:26px}"
        ".cm-nav-link,.cm-nav-trigger{font-size:15px;padding:14px 2px;width:100%;justify-content:space-between}"
        ".cm-nav-dd{width:100%}"
        ".cm-nav-menu{position:static;min-width:0;transform:none;opacity:1;visibility:visible;display:none;"
        "box-shadow:none;background:rgba(253,249,234,.05);color:var(--cream);margin:0}"
        ".cm-nav-dd.open .cm-nav-menu{display:flex}.cm-nav-menu a{color:rgba(253,249,234,.82)}"
        ".cm-nav-cta{text-align:center;margin-top:10px}}"
    )

def nav(logo_src, links=None, services=None, brands=None, cta="Request a quote",
        signin=True, cart=True):
    """Render the nav bar. logo_src = data URI / path to the cream logo.
    signin/cart add the secondary actions (as on the live site)."""
    links = links or ["Products"]
    services = services or ["Custom Screen Printing", "Embroidery & DTG", "Cut & Sew Manufacturing"]
    brands = brands or ["Patagonia", "YETI", "Lululemon", "The North Face"]
    def _menu(mid, label, items):
        a = "".join(f'<a role="menuitem" href="#">{_html.escape(t)}</a>' for t in items)
        return (f'<div class="cm-nav-dd"><button class="cm-nav-trigger" aria-expanded="false" '
                f'aria-haspopup="true" aria-controls="{mid}">{_html.escape(label)}{_NAV_CARET}</button>'
                f'<div class="cm-nav-menu" id="{mid}" role="menu">{a}</div></div>')
    plain = "".join(f'<a class="cm-nav-link" href="#">{_html.escape(t)}</a>' for t in links)
    actions = ""
    if signin or cart:
        a = ('<a class="cm-nav-signin" href="#">Sign in</a>' if signin else "")
        c = (f'<a class="cm-nav-cart" href="#" aria-label="Cart">{_NAV_CART}</a>' if cart else "")
        actions = f'<div class="cm-nav-actions">{a}{c}</div>'
    return (
        '<header class="cm-nav"><div class="cm-nav-in">'
        f'<a class="cm-nav-logo" href="#" aria-label="Crooked Monkey home">'
        f'<img src="{logo_src}" alt="Crooked Monkey"></a>'
        '<div class="cm-nav-drawer">'
        '<nav class="cm-nav-mid" aria-label="Primary">'
        + plain
        + _menu("cm-dd-services", "Services", services)
        + _menu("cm-dd-brands", "Premium brands", brands)
        + f'<a class="cm-nav-cta" href="#">{_html.escape(cta)}</a>'
        + '</nav>' + actions + '</div>'
        '<button class="cm-nav-burger" aria-label="Open menu" aria-expanded="false" aria-controls="cm-nav">'
        '<span></span><span></span><span></span></button>'
        '</div></header>'
    )

def nav_js():
    """JS wiring for .cm-nav: click-to-pin dropdowns + mobile drawer; Escape closes."""
    return (
        "/* CM nav: dropdowns (click to pin) + mobile drawer. */"
        "var cmDD=[].slice.call(document.querySelectorAll('.cm-nav-dd'));"
        "function cmClose(x){cmDD.forEach(function(d){if(d!==x){d.classList.remove('open');"
        "var t=d.querySelector('.cm-nav-trigger');if(t)t.setAttribute('aria-expanded','false');}});}"
        "cmDD.forEach(function(dd){var t=dd.querySelector('.cm-nav-trigger');"
        "t.addEventListener('click',function(e){e.preventDefault();"
        "var o=dd.classList.toggle('open');t.setAttribute('aria-expanded',o?'true':'false');cmClose(dd);});});"
        "var cmNav=document.querySelector('.cm-nav'),cmB=document.querySelector('.cm-nav-burger');"
        "if(cmB){cmB.addEventListener('click',function(){var o=cmNav.classList.toggle('open');"
        "cmB.setAttribute('aria-expanded',o?'true':'false');if(!o)cmClose(null);});}"
        "document.addEventListener('click',function(e){if(!e.target.closest('.cm-nav-dd'))cmClose(null);"
        "if(cmNav&&cmNav.classList.contains('open')&&!e.target.closest('.cm-nav')){cmNav.classList.remove('open');}});"
        "document.addEventListener('keydown',function(e){if(e.key==='Escape'){cmClose(null);if(cmNav)cmNav.classList.remove('open');}});"
    )


# ===========================================================================
# ATOMS — eyebrow + arrow link
# ===========================================================================
def eyebrow_css():
    return ("/* ---- CM: eyebrow / label ---- */"
            ".cm-eyebrow{display:inline-block;font:800 12px/1 Inter,system-ui,sans-serif;"
            "letter-spacing:.16em;text-transform:uppercase;color:rgba(4,18,2,.55)}")

def eyebrow(text, color=None):
    st = f' style="color:{color}"' if color else ""
    return f'<span class="cm-eyebrow"{st}>{_html.escape(text)}</span>'

def arrow_css():
    return ("/* ---- CM: arrow link ---- */"
            ".cm-arrow{display:inline-flex;align-items:center;gap:.45em;font:700 13px/1 Inter,system-ui,sans-serif;"
            "letter-spacing:.13em;text-transform:uppercase;color:var(--ink);text-decoration:none;"
            "border-bottom:2px solid currentColor;padding-bottom:4px;transition:opacity .2s ease}"
            ".cm-arrow:hover{opacity:.62}.cm-arrow .ar{transition:transform .2s ease}"
            ".cm-arrow:hover .ar{transform:translateX(4px)}")

def arrow_link(label, href="#", color=None):
    st = f' style="color:{color}"' if color else ""
    return f'<a class="cm-arrow" href="{href}"{st}>{_html.escape(label)} <span class="ar">→</span></a>'

# ===========================================================================
# MOLECULES — section heading, media card, feature card, checklist, pill group
# ===========================================================================
def heading_css():
    return ("/* ---- CM: section heading ---- */"
            ".cm-heading{max-width:60ch}.cm-heading.center{text-align:center;margin-inline:auto}"
            ".cm-heading .cm-h-eyebrow{display:block;font:800 12px/1 Inter;letter-spacing:.16em;"
            "text-transform:uppercase;color:rgba(4,18,2,.55);margin-bottom:12px}"
            ".cm-heading h2{font-family:Poppins,sans-serif;font-weight:900;text-transform:uppercase;"
            "letter-spacing:-.02em;line-height:1.0;font-size:clamp(28px,3.6vw,46px);color:var(--ink)}"
            ".cm-heading .cm-h-sub{margin-top:16px;font:500 clamp(15px,1.2vw,18px)/1.55 Inter;"
            "color:rgba(4,18,2,.66)}.cm-heading.center .cm-h-sub{margin-inline:auto}")

def heading(title, eyebrow=None, sub=None, center=False):
    eb = f'<span class="cm-h-eyebrow">{_html.escape(eyebrow)}</span>' if eyebrow else ""
    sb = f'<p class="cm-h-sub">{_html.escape(sub)}</p>' if sub else ""
    return f'<div class="cm-heading{" center" if center else ""}">{eb}<h2>{title}</h2>{sb}</div>'

def media_css():
    return ("/* ---- CM: media card (image + text) ---- */"
            ".cm-media{border-radius:var(--r-card);overflow:hidden;background:var(--cream);"
            "max-width:420px;margin:0}"
            ".cm-media-photo{aspect-ratio:3/2;background:var(--cream)}"
            ".cm-media-photo img{width:100%;height:100%;object-fit:cover;display:block}"
            ".cm-media-cap{background:var(--accent,var(--yellow));color:var(--ink);padding:22px 24px}"
            ".cm-media-eyebrow{display:block;font:800 12px/1 Inter;letter-spacing:.13em;"
            "text-transform:uppercase;opacity:.66;margin-bottom:10px}"
            ".cm-media-cap h3{font-family:Poppins,sans-serif;font-weight:900;text-transform:uppercase;"
            "letter-spacing:-.01em;line-height:1.06;font-size:clamp(19px,1.7vw,24px)}"
            ".cm-media-cap p{margin-top:10px;font:500 15px/1.45 Inter;color:rgba(4,18,2,.8);max-width:36ch}"
            ".cm-media-link{display:inline-flex;align-items:center;gap:.4em;margin-top:16px;"
            "font:700 12px/1 Inter;letter-spacing:.13em;text-transform:uppercase;color:var(--ink);"
            "text-decoration:none;border-bottom:2px solid currentColor;padding-bottom:4px}"
            ".cm-media-link .ar{transition:transform .2s ease}.cm-media-link:hover .ar{transform:translateX(4px)}")

def media_card(img, title, meta, eyebrow=None, accent="var(--yellow)", alt="", link=None):
    eb = f'<span class="cm-media-eyebrow">{_html.escape(eyebrow)}</span>' if eyebrow else ""
    lk = f'<a class="cm-media-link" href="#">{_html.escape(link)} <span class="ar">→</span></a>' if link else ""
    return (f'<figure class="cm-media" style="--accent:{accent}">'
            f'<div class="cm-media-photo"><img src="{img}" alt="{_html.escape(alt or title)}" loading="lazy"></div>'
            f'<figcaption class="cm-media-cap">{eb}<h3>{_html.escape(title)}</h3>'
            f'<p>{_html.escape(meta)}</p>{lk}</figcaption></figure>')

def feature_css():
    # inherits the K-notch cut from the kit; adds the number/title/body layout
    return (notch_css() + "/* ---- CM: feature card ---- */"
            ".cm-feat{color:var(--ink);min-height:200px}"
            ".cm-feat .cm-feat-in{height:100%;display:flex;flex-direction:column;padding:28px 48px}"
            ".cm-feat-num{font-family:Poppins,sans-serif;font-weight:900;font-size:clamp(32px,3vw,48px);"
            "line-height:1;letter-spacing:-.02em;color:var(--ink)}"
            ".cm-feat-tx{margin-top:auto;padding-top:22px}"
            ".cm-feat-t{font:800 clamp(17px,1.4vw,22px)/1.16 Inter;letter-spacing:-.015em;color:var(--ink)}"
            ".cm-feat-b{margin-top:12px;font:500 14px/1.5 Inter;color:rgba(4,18,2,.66);max-width:32ch}")

def feature_card(num, title, body, side="r", bg="var(--blue)"):
    inner = (f'<div class="cm-feat-in"><span class="cm-feat-num">{_html.escape(num)}</span>'
             f'<div class="cm-feat-tx"><h3 class="cm-feat-t">{_html.escape(title)}</h3>'
             f'<p class="cm-feat-b">{_html.escape(body)}</p></div></div>')
    return notch_card(inner=inner, side=side, bg=bg, cls="cm-feat", style="width:300px")

_CM_CK = ("<svg class='cm-ck' viewBox='0 0 30 30' aria-hidden='true'>"
          "<circle cx='15' cy='15' r='15' fill='#041202'/>"
          "<path d='M8.5 15.4l4 4 9-9.6' fill='none' stroke='#FBF79E' stroke-width='2.6' "
          "stroke-linecap='round' stroke-linejoin='round'/></svg>")

def check_css():
    return ("/* ---- CM: checklist ---- */"
            ".cm-check{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:16px}"
            ".cm-check li{display:flex;align-items:center;gap:14px;font:700 clamp(15px,1.1vw,18px)/1.2 Inter;color:var(--ink)}"
            ".cm-ck{flex:none;width:30px;height:30px;display:block}")

def checklist(items):
    return ('<ul class="cm-check">'
            + "".join(f'<li>{_CM_CK}<span>{_html.escape(t)}</span></li>' for t in items)
            + '</ul>')

def pillgroup_css():
    return "/* ---- CM: pill group ---- */.cm-pillgroup{display:flex;flex-wrap:wrap;gap:12px}"

def pill_group(labels, bg=None):
    return '<div class="cm-pillgroup">' + "".join(pill(l, bg=bg) for l in labels) + '</div>'

# ===========================================================================
# ORGANISMS — hero, service cards, text+pills, faq+title, form, footer
# ===========================================================================
def hero_css():
    return (button_css() + "/* ---- CM: hero ---- */"
            ".cm-hero{background:var(--cream);color:var(--ink);padding:clamp(56px,8vw,104px) clamp(24px,5vw,64px)}"
            ".cm-hero-wrap{max-width:1180px;margin:0 auto}"
            ".cm-hero-title{font-family:Poppins,sans-serif;font-weight:900;text-transform:uppercase;"
            "line-height:.95;letter-spacing:-.025em;font-size:clamp(38px,4.9vw,74px)}"
            ".cm-hero-hl{position:relative;display:inline-block}"
            ".cm-hero-hl::before{content:'';position:absolute;left:-.05em;right:-.05em;top:.12em;bottom:.05em;"
            "background:var(--blue);z-index:-1}"
            ".cm-hero-sub{margin-top:clamp(20px,3vh,34px);font:500 clamp(16px,1.3vw,21px)/1.5 Inter;"
            "color:var(--ink);max-width:46ch}"
            ".cm-hero-actions{display:flex;flex-wrap:wrap;gap:14px;margin-top:clamp(26px,4vh,42px)}")

def hero(title_html, sub, primary="Start a project", secondary="See all services"):
    return ('<section class="cm-hero"><div class="cm-hero-wrap">'
            f'<h1 class="cm-hero-title">{title_html}</h1>'
            f'<p class="cm-hero-sub">{_html.escape(sub)}</p>'
            '<div class="cm-hero-actions">'
            + button(primary, "primary") + button(secondary, "outline")
            + '</div></div></section>')

# service card colored background = a fixed K-notch mask (rounded-left, notch-right)
# that slides on hover — lifted from the home page's service grid.
_SVC_K = ("M344.01,292.26c1.56,0,2.93-.57,4.1-1.76,1.17-1.16,1.77-2.53,1.77-4.08-.81-33.92-7.4-62.4-19.82-85.48"
          "-12.42-23.09-28.5-41.35-48.25-54.8,19.75-13.44,35.83-31.73,48.25-54.8,12.42-23.1,19.01-51.6,19.82-85.5,"
          "0-1.55-.6-2.92-1.77-4.08-1.17-1.18-2.54-1.76-4.1-1.76H5.88c-1.77,0-3.19.52-4.27,1.6C.53,2.68,0,4.08,0,5.84"
          "v280.58c0,1.76.53,3.17,1.61,4.24,1.08,1.07,2.5,1.6,4.27,1.6h338.13Z")
_SVC_W = 320
_svc_svg = ("<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 " + f"{_SVC_W+349.87:.2f}" + " 292.26' "
            "preserveAspectRatio='none'><rect x='0' y='0' width='" + f"{_SVC_W+6}" + "' height='292.26' fill='white'/>"
            "<path transform='translate(" + str(_SVC_W) + ",0)' d='" + _SVC_K + "' fill='white'/></svg>")
_SVC_MASK = "data:image/svg+xml," + urllib.parse.quote(_svc_svg, safe="")

def service_css():
    return ("/* ---- CM: service card (image + text, K-notch) ---- */"
            ".cm-svc-grid{display:grid;grid-template-columns:1fr 1fr;gap:clamp(20px,2vw,32px)}"
            ".cm-svc-card{position:relative;height:clamp(260px,24vw,340px);cursor:pointer;outline:none}"
            ".cm-svc-color{position:absolute;inset:0;background:var(--c);border-radius:24px;"
            "-webkit-mask:url(\"" + _SVC_MASK + "\") no-repeat;mask:url(\"" + _SVC_MASK + "\") no-repeat;"
            "-webkit-mask-size:112% 100%;mask-size:112% 100%;-webkit-mask-position:0% 50%;mask-position:0% 50%;"
            "transition:-webkit-mask-position .6s cubic-bezier(.62,0,.14,1),mask-position .6s cubic-bezier(.62,0,.14,1)}"
            ".cm-svc-card:hover .cm-svc-color,.cm-svc-card:focus-visible .cm-svc-color{-webkit-mask-position:100% 50%;mask-position:100% 50%}"
            ".cm-svc-photo{position:absolute;left:0;top:0;bottom:0;width:44%;border-radius:24px 0 0 24px;"
            "overflow:hidden;z-index:2;background:var(--cream)}"
            ".cm-svc-photo img{width:100%;height:100%;object-fit:cover;transition:transform .7s cubic-bezier(.2,.7,.2,1)}"
            ".cm-svc-card:hover .cm-svc-photo img{transform:scale(1.04)}"
            ".cm-svc-body{position:absolute;left:44%;top:0;bottom:0;right:0;z-index:3;display:flex;flex-direction:column;"
            "justify-content:space-between;padding:clamp(24px,2.4vw,40px);padding-right:clamp(64px,6.5vw,104px)}"
            ".cm-svc-t{font:800 clamp(18px,1.4vw,24px)/1.14 Inter;letter-spacing:-.02em;color:var(--cd,var(--ink))}"
            ".cm-svc-m{margin-top:12px;font:500 15px/1.45 Inter;color:rgba(4,18,2,.64);max-width:26ch}"
            ".cm-svc-link{align-self:flex-start;font:700 12px/1 Inter;letter-spacing:.13em;text-transform:uppercase;"
            "color:var(--cd,var(--ink));text-decoration:none;border-bottom:2px solid currentColor;padding-bottom:5px}"
            ".cm-svc-link:hover{opacity:.65}"
            "@media(max-width:640px){.cm-svc-grid{grid-template-columns:1fr}"
            ".cm-svc-card{height:auto;min-height:172px;display:flex}"
            ".cm-svc-photo{position:relative;left:auto;top:auto;bottom:auto;flex:0 0 40%;width:40%;border-radius:20px 0 0 20px}"
            ".cm-svc-body{position:relative;left:auto;right:auto;top:auto;bottom:auto;flex:1;padding:22px}}")

def service_card(img, title, meta, link, color="blue", alt=""):
    return (f'<article class="cm-svc-card" style="--c:var(--{color});--cd:var(--{color}-deep)" tabindex="0">'
            f'<div class="cm-svc-color"></div>'
            f'<div class="cm-svc-photo"><img src="{img}" alt="{_html.escape(alt or title)}" loading="lazy"></div>'
            f'<div class="cm-svc-body"><div class="cm-svc-top">'
            f'<h3 class="cm-svc-t">{title}</h3><p class="cm-svc-m">{meta}</p></div>'
            f'<a class="cm-svc-link" href="#">{link} &rsaquo;</a></div></article>')

def services_grid(items):
    """items = list of (img, title, meta, link, color)."""
    return '<div class="cm-svc-grid">' + "".join(service_card(*it) for it in items) + '</div>'

_PR_ACC = ["yellow", "blue", "pink", "mint"]
def premium_css():
    return ("/* ---- CM: text + pills (premium brands) ---- */"
            ".cm-pr{background:var(--ink);color:var(--cream);"
            "padding:clamp(48px,7vw,88px) clamp(28px,5vw,72px)}"
            ".cm-pr-grid{display:grid;grid-template-columns:minmax(0,.92fr) minmax(0,1.08fr);"
            "gap:clamp(32px,5vw,72px);align-items:center;max-width:1180px;margin:0 auto}"
            ".cm-pr-title{font-family:Poppins,sans-serif;font-weight:900;text-transform:uppercase;"
            "letter-spacing:-.02em;line-height:1.0;font-size:clamp(28px,3.6vw,48px);color:var(--cream)}"
            ".cm-pr-title .acc{color:var(--yellow)}"
            ".cm-pr-sub{margin-top:20px;font:500 clamp(15px,1.1vw,18px)/1.55 Inter;color:rgba(253,249,234,.66);max-width:46ch}"
            ".cm-pr-pills{display:flex;flex-wrap:wrap;gap:12px}"
            ".cm-pr-pill{display:inline-flex;align-items:center;background:var(--cream);color:var(--ink);"
            "border-radius:999px;padding:clamp(12px,1.2vw,16px) clamp(18px,1.6vw,26px);"
            "font:900 clamp(12px,1vw,15px)/1 Poppins,sans-serif;letter-spacing:.02em;text-transform:uppercase;"
            "white-space:nowrap;transition:background .25s ease,transform .32s cubic-bezier(.2,.75,.2,1),color .25s ease}"
            ".cm-pr-more{display:inline-block;margin-top:clamp(24px,4vh,40px);font:800 clamp(13px,1vw,15px)/1 Inter;"
            "letter-spacing:.14em;text-transform:uppercase;color:var(--mint);text-decoration:none}"
            ".cm-pr-more .ar{display:inline-block;margin-left:.3em;transition:transform .2s ease}"
            ".cm-pr-more:hover .ar{transform:translateX(5px)}"
            "@media (prefers-reduced-motion:no-preference){"
            ".cm-pr-pill:hover{background:var(--pa,var(--yellow));transform:scale(1.06) rotate(-2.6deg)}}"
            "@media(max-width:760px){.cm-pr-grid{grid-template-columns:1fr;gap:28px}}")

def premium_section(title_html, sub, brands, cta="Browse all premium brands"):
    pills = "".join(f'<span class="cm-pr-pill" style="--pa:var(--{_PR_ACC[i%4]})">{_html.escape(b)}</span>'
                    for i, b in enumerate(brands))
    return ('<section class="cm-pr"><div class="cm-pr-grid">'
            f'<div><h2 class="cm-pr-title">{title_html}</h2>'
            f'<p class="cm-pr-sub">{_html.escape(sub)}</p></div>'
            f'<div><div class="cm-pr-pills">{pills}</div>'
            f'<a class="cm-pr-more" href="#">{_html.escape(cta)} <span class="ar">›</span></a>'
            '</div></div></section>')

def faqsection_css():
    return (faq_css() + "/* ---- CM: FAQ + title ---- */"
            ".cm-faqs{background:var(--cream);color:var(--ink);padding:clamp(48px,7vw,90px) clamp(24px,5vw,64px)}"
            ".cm-faqs-grid{display:grid;grid-template-columns:minmax(0,.82fr) minmax(0,1.18fr);"
            "gap:clamp(32px,5vw,72px);align-items:start;max-width:1180px;margin:0 auto}"
            ".cm-faqs-title{font-family:Poppins,sans-serif;font-weight:900;text-transform:uppercase;"
            "line-height:1.0;letter-spacing:-.02em;font-size:clamp(34px,4.4vw,64px)}"
            ".cm-faqs-title .pink{color:var(--pink)}"
            "@media(max-width:760px){.cm-faqs-grid{grid-template-columns:1fr;gap:28px}}")

def faq_section(title_html, items):
    return ('<section class="cm-faqs"><div class="cm-faqs-grid">'
            f'<h2 class="cm-faqs-title">{title_html}</h2>'
            f'<div>{faq(items)}</div></div></section>')

_CM_CHEV = "data:image/svg+xml," + urllib.parse.quote(
    "<svg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 16 16'>"
    "<path d='M4 6l4 4 4-4' fill='none' stroke='#041202' stroke-width='2' "
    "stroke-linecap='round' stroke-linejoin='round'/></svg>", safe="")

def form_css():
    return (check_css() + "/* ---- CM: contact form ---- */"
            ".cm-cta{background:var(--blue);border-radius:var(--r-card-lg);padding:clamp(34px,4.6vw,72px);"
            "max-width:var(--maxw,1340px);margin-inline:auto}"
            ".cm-cta-grid{display:grid;grid-template-columns:minmax(0,.9fr) minmax(0,1.1fr);"
            "gap:clamp(32px,5vw,80px);align-items:center;max-width:1180px;margin:0 auto}"
            ".cm-cta-title{font-family:Poppins,sans-serif;font-weight:900;text-transform:uppercase;"
            "line-height:.98;letter-spacing:-.02em;font-size:clamp(34px,4.6vw,64px);color:var(--ink)}"
            ".cm-cta-hl{position:relative;display:inline-block}"
            ".cm-cta-hl::before{content:'';position:absolute;left:-.08em;right:-.08em;top:.16em;bottom:.06em;"
            "background:var(--pink);z-index:-1}"
            ".cm-cta-sub{margin-top:20px;font:500 clamp(15px,1.15vw,18px)/1.5 Inter;color:var(--ink);max-width:40ch}"
            ".cm-cta .cm-check{margin-top:clamp(24px,3.4vh,40px)}"
            ".cm-cta-form{display:flex;flex-direction:column;gap:clamp(14px,1.7vh,20px)}"
            ".cm-cta-row{display:grid;grid-template-columns:1fr 1fr;gap:clamp(14px,1.4vw,20px)}"
            ".cm-cta-field{display:flex;flex-direction:column;gap:8px;min-width:0}"
            ".cm-cta-label{font:700 11px/1 Inter;letter-spacing:.16em;text-transform:uppercase;color:rgba(4,18,2,.55)}"
            ".cm-cta-input{width:100%;background:#fff;color:var(--ink);border:2px solid transparent;border-radius:14px;"
            "padding:clamp(14px,1.1vw,17px) clamp(15px,1.2vw,19px);font:500 clamp(15px,1.05vw,16px)/1.3 Inter;"
            "transition:border-color .18s ease}"
            ".cm-cta-input::placeholder{color:rgba(4,18,2,.42)}.cm-cta-input:focus{outline:none;border-color:var(--ink)}"
            "textarea.cm-cta-input{min-height:110px;resize:vertical}"
            ".cm-cta-select{appearance:none;-webkit-appearance:none;cursor:pointer;"
            "background-image:url(\"" + _CM_CHEV + "\");background-repeat:no-repeat;"
            "background-position:right 18px center;padding-right:46px}"
            ".cm-cta-submit{margin-top:6px;width:100%;background:var(--ink);color:var(--cream);border:0;border-radius:999px;"
            "padding:clamp(18px,1.5vw,22px);font:800 clamp(13px,1vw,15px)/1 Inter;letter-spacing:.16em;text-transform:uppercase;"
            "cursor:pointer;transition:transform .2s ease}"
            ".cm-cta-submit:hover{transform:translateY(-2px)}.cm-cta-submit:focus-visible{outline:3px solid var(--ink);outline-offset:3px}"
            ".cm-cta-fine{margin-top:2px;font:500 13px/1.5 Inter;color:rgba(4,18,2,.55)}"
            "@media(max-width:760px){.cm-cta-grid{grid-template-columns:1fr;gap:32px}.cm-cta-row{grid-template-columns:1fr}}")

def contact_form(title_html=None, sub=None, checks=None, quantities=None):
    title_html = title_html or 'READY TO<br>START?<br><span class="cm-cta-hl">LET&rsquo;S TALK</span>'
    sub = sub or "Tell us about your project. A real human — not a form bot — will get back to you within one business hour."
    checks = checks or ["Reply within 1 business hour", "Dedicated account rep", "No commitment to quote"]
    quantities = quantities or ["25–100", "100–250", "250–500", "500–1,000", "1,000+"]
    qopts = "".join(f"<option>{_html.escape(q)}</option>" for q in quantities)
    return ('<section class="cm-cta"><div class="cm-cta-grid">'
            f'<div><h2 class="cm-cta-title">{title_html}</h2>'
            f'<p class="cm-cta-sub">{_html.escape(sub)}</p>{checklist(checks)}</div>'
            '<form class="cm-cta-form" novalidate>'
            '<div class="cm-cta-row">'
            '<div class="cm-cta-field"><label class="cm-cta-label" for="cm-name">Name</label>'
            '<input class="cm-cta-input" id="cm-name" type="text" placeholder="Full name" autocomplete="name"></div>'
            '<div class="cm-cta-field"><label class="cm-cta-label" for="cm-company">Company</label>'
            '<input class="cm-cta-input" id="cm-company" type="text" placeholder="Company or org" autocomplete="organization"></div>'
            '</div>'
            '<div class="cm-cta-field"><label class="cm-cta-label" for="cm-email">Email</label>'
            '<input class="cm-cta-input" id="cm-email" type="email" placeholder="you@company.com" autocomplete="email"></div>'
            '<div class="cm-cta-field"><label class="cm-cta-label" for="cm-qty">Quantity</label>'
            '<select class="cm-cta-input cm-cta-select" id="cm-qty">'
            f'<option value="" selected disabled>Choose range</option>{qopts}</select></div>'
            '<div class="cm-cta-field"><label class="cm-cta-label" for="cm-msg">What are you making?</label>'
            '<textarea class="cm-cta-input" id="cm-msg" rows="3" placeholder="Items, decoration, deadline — the more detail the better."></textarea></div>'
            '<button class="cm-cta-submit" type="submit">Talk to a merch expert</button>'
            '<p class="cm-cta-fine">By submitting you agree to our privacy policy. We never share your info.</p>'
            '</form></div></section>')

def form_js():
    return ("/* CM contact form: prototype — don't navigate on submit. */"
            "[].slice.call(document.querySelectorAll('.cm-cta-form')).forEach(function(f){"
            "f.addEventListener('submit',function(e){e.preventDefault();});});")

def footer_css():
    return ("/* ---- CM: footer ---- */"
            ".cm-ft{background:var(--ink);color:var(--cream);padding:clamp(56px,8vw,96px) clamp(28px,5vw,72px) clamp(28px,4vh,44px)}"
            ".cm-ft-wrap{max-width:1180px;margin:0 auto}"
            ".cm-ft-top{display:grid;grid-template-columns:1.5fr 1fr 1fr 1fr;gap:clamp(28px,3vw,48px)}"
            ".cm-ft-brand{max-width:34ch}.cm-ft-logo{width:clamp(200px,20vw,256px);height:auto;display:block}"
            ".cm-ft-desc{margin-top:22px;font:500 14.5px/1.62 Inter;color:rgba(253,249,234,.58)}"
            ".cm-ft-mail{display:inline-block;margin-top:18px;font:500 14.5px/1.4 Inter;color:rgba(253,249,234,.86);"
            "text-decoration:none;transition:color .18s ease}.cm-ft-mail:hover{color:var(--yellow)}"
            ".cm-ft-h{font:800 12px/1 Inter;letter-spacing:.15em;text-transform:uppercase;color:var(--yellow);margin:0 0 20px}"
            ".cm-ft-list{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:13px}"
            ".cm-ft-list a{font:500 15px/1.3 Inter;color:rgba(253,249,234,.72);text-decoration:none;transition:color .18s ease}"
            ".cm-ft-list a:hover{color:var(--cream)}"
            ".cm-ft-bottom{display:flex;justify-content:space-between;align-items:center;gap:18px;flex-wrap:wrap;"
            "margin-top:clamp(36px,6vh,64px);padding-top:clamp(20px,3vh,30px);border-top:1px solid rgba(253,249,234,.14)}"
            ".cm-ft-copy{margin:0;font:500 13.5px/1.4 Inter;color:rgba(253,249,234,.5)}"
            ".cm-ft-legal{display:flex;gap:clamp(16px,2vw,28px)}"
            ".cm-ft-legal a{font:500 13.5px/1.4 Inter;color:rgba(253,249,234,.5);text-decoration:none;transition:color .18s ease}"
            ".cm-ft-legal a:hover{color:var(--cream)}"
            "@media(max-width:1024px){.cm-ft-top{grid-template-columns:1fr 1fr}.cm-ft-brand{grid-column:1/-1;max-width:54ch}}"
            "@media(max-width:560px){.cm-ft-top{grid-template-columns:1fr;gap:28px}"
            ".cm-ft-bottom{flex-direction:column;align-items:flex-start;gap:12px}}")

def footer(logo_src, columns=None, desc=None, email="hello@crookedmonkey.com", legal=None):
    columns = columns or [
        ("Services", ["Custom Screen Printing", "Cut & Sew Manufacturing", "On-Demand Swag Stores", "Swag Fulfillment", "Rush Orders"]),
        ("Locations", ["Louisville", "Washington DC", "Denver", "Miami", "New York"]),
        ("Resources", ["FAQ", "Merch Glossary", "Request a Quote", "Custom Design"]),
    ]
    desc = desc or "Breaking the mold since 2005. Full-service merch, fulfillment, and premium-brand customization for companies and teams."
    legal = legal or ["Privacy", "Terms", "Returns", "Guarantee"]
    cols = ""
    for title, items in columns:
        links = "".join(f'<li><a href="#">{_html.escape(t)}</a></li>' for t in items)
        cols += (f'<nav class="cm-ft-col" aria-label="{_html.escape(title)}">'
                 f'<h3 class="cm-ft-h">{_html.escape(title)}</h3><ul class="cm-ft-list">{links}</ul></nav>')
    legal_html = "".join(f'<a href="#">{_html.escape(t)}</a>' for t in legal)
    return ('<footer class="cm-ft"><div class="cm-ft-wrap"><div class="cm-ft-top">'
            '<div class="cm-ft-brand">'
            f'<img class="cm-ft-logo" src="{logo_src}" alt="Crooked Monkey" width="871" height="118">'
            f'<p class="cm-ft-desc">{_html.escape(desc)}</p>'
            f'<a class="cm-ft-mail" href="mailto:{email}">{email}</a></div>'
            + cols + '</div>'
            '<div class="cm-ft-bottom"><p class="cm-ft-copy">© 2026 Crooked Monkey. All rights reserved.</p>'
            f'<nav class="cm-ft-legal" aria-label="Legal">{legal_html}</nav></div></div></footer>')


# ---------------------------------------------------------------------------
# Monkey badge (brand mark) — atom
# ---------------------------------------------------------------------------
def badge_css():
    return ("/* ---- CM: monkey badge ---- */"
            ".cm-badge{display:block}.cm-badge svg{width:100%;height:100%;display:block;color:var(--ink)}"
            "@keyframes cm-spin{to{transform:rotate(360deg)}}"
            "@media (prefers-reduced-motion:no-preference){"
            ".cm-badge.spin svg{animation:cm-spin 26s linear infinite;transform-origin:50% 50%}}")

def badge(monkey_svg, size="140px", spin=True):
    """monkey_svg = inner markup of monkey_inner.svg (uses fill=currentColor)."""
    return (f'<div class="cm-badge{" spin" if spin else ""}" style="width:{size};height:{size}" '
            f'aria-label="Crooked Monkey — we are here for you, always" role="img">'
            f'<svg viewBox="0 0 640 640">{monkey_svg}</svg></div>')

# ---------------------------------------------------------------------------
# Image ticker / marquee — molecule
# ---------------------------------------------------------------------------
def ticker_css():
    return ("/* ---- CM: image ticker ---- */"
            # vertical padding MUST leave room for the tilted cards' drop-shadow, or
            # overflow:hidden clips it (and the shorter gallery throws off hero centering).
            ".cm-ticker{position:relative;overflow:hidden;width:100%;padding:clamp(40px,6vh,64px) 0;"
            "-webkit-mask-image:linear-gradient(90deg,transparent,#000 6%,#000 94%,transparent);"
            "mask-image:linear-gradient(90deg,transparent,#000 6%,#000 94%,transparent)}"
            ".cm-ticker-track{display:flex;gap:clamp(34px,4vw,72px);width:max-content;animation:cm-tick 46s linear infinite}"
            ".cm-ticker:hover .cm-ticker-track{animation-play-state:paused}"
            ".cm-ticker .tp{flex:0 0 auto;height:clamp(180px,30vh,340px);aspect-ratio:4/3;border-radius:16px;"
            "overflow:hidden;box-shadow:0 32px 60px -32px rgba(4,18,2,.45)}"
            ".cm-ticker .tp:nth-child(odd){transform:rotate(-2deg)}.cm-ticker .tp:nth-child(even){transform:rotate(1.6deg)}"
            ".cm-ticker .tp img{width:100%;height:100%;object-fit:cover}"
            "@keyframes cm-tick{to{transform:translateX(-50%)}}"
            "@media (prefers-reduced-motion:reduce){.cm-ticker-track{animation:none}}")

def ticker(images):
    """images = list of src strings. Duplicated internally for a seamless loop."""
    one = "".join(f'<figure class="tp"><img src="{s}" alt="" loading="lazy"></figure>' for s in images)
    return f'<div class="cm-ticker"><div class="cm-ticker-track">{one}{one}</div></div>'

# ---------------------------------------------------------------------------
# Gallery — big background type + ticker + CTA — organism
# ---------------------------------------------------------------------------
def gallery_css():
    return (ticker_css() + button_css() + "/* ---- CM: gallery ---- */"
            ".cm-gal{position:relative;background:var(--cream);overflow:hidden;padding:clamp(48px,7vw,90px) 0;"
            "display:flex;flex-direction:column;justify-content:center;align-items:center}"
            ".cm-gal-bg{position:absolute;inset:0;z-index:0;display:flex;flex-direction:column;justify-content:center;"
            "align-items:center;text-align:center;pointer-events:none}"
            ".cm-gal-bg span{display:block;font-family:Poppins,sans-serif;font-weight:900;text-transform:uppercase;"
            "line-height:.84;letter-spacing:-.02em;color:var(--ink);font-size:clamp(46px,11vw,150px);white-space:nowrap}"
            ".cm-gal .cm-ticker{position:relative;z-index:1}"
            ".cm-gal-cta{position:relative;z-index:2;margin-top:clamp(28px,5vh,52px)}"
            "@media(max-width:760px){.cm-gal-bg{position:relative;margin-bottom:20px}"
            ".cm-gal-bg span{font-size:clamp(38px,13vw,80px);white-space:normal}}")

def gallery(words, images, cta="Start a project"):
    bg = "".join(f"<span>{_html.escape(w)}</span>" for w in words)
    return ('<section class="cm-gal">'
            f'<div class="cm-gal-bg" aria-hidden="true">{bg}</div>'
            + ticker(images)
            + f'<div class="cm-gal-cta">{button(cta, "primary")}</div>'
            '</section>')

# ---------------------------------------------------------------------------
# Level card + Four Levels — molecule + organism
# ---------------------------------------------------------------------------
def level_css():
    return ("/* ---- CM: level card (K-silhouette, image + text) ---- */"
            ".cm-lvl{position:relative;overflow:hidden;min-height:290px;display:flex;align-items:center;border-radius:6px}"
            ".cm-lvl-bg{position:absolute;left:-3%;top:0;width:106%;height:100%;z-index:0}"
            ".cm-lvl-in{position:relative;z-index:1;display:grid;grid-template-columns:.8fr 1fr;gap:clamp(20px,3vw,48px);"
            "align-items:center;padding:clamp(24px,3vw,44px) clamp(28px,5vw,64px);width:100%;color:var(--ink)}"
            ".cm-lvl-frame{justify-self:center;width:min(210px,42vw);aspect-ratio:1;border-radius:18px;overflow:hidden;"
            "box-shadow:0 30px 60px -30px rgba(0,0,0,.5)}"
            ".cm-lvl-frame img{width:100%;height:100%;object-fit:cover}"
            ".cm-lvl-num{font:500 12px/1 Inter;letter-spacing:.16em;text-transform:uppercase;color:rgba(4,18,2,.5)}"
            ".cm-lvl-t{font-family:Poppins,sans-serif;font-weight:900;text-transform:uppercase;letter-spacing:-.02em;"
            "line-height:1;font-size:clamp(28px,3.4vw,46px);margin-top:10px}"
            ".cm-lvl-sub{margin-top:12px;font:600 clamp(16px,1.3vw,18px)/1.35 Inter;max-width:34ch}"
            ".cm-lvl-b{margin-top:14px;font:500 15px/1.6 Inter;color:rgba(4,18,2,.82);max-width:44ch}"
            ".cm-lvl-link{display:inline-flex;align-items:center;gap:.4em;margin-top:20px;font:700 12px/1 Inter;"
            "letter-spacing:.14em;text-transform:uppercase;color:var(--ink);text-decoration:none;"
            "border-bottom:2px solid currentColor;padding-bottom:4px}"
            ".cm-lvl-intro{background:var(--ink);color:var(--cream);border-radius:6px;padding:clamp(30px,4.5vw,60px)}"
            ".cm-lvl-intro h2{font-family:Poppins,sans-serif;font-weight:900;text-transform:uppercase;letter-spacing:-.02em;"
            "line-height:.95;font-size:clamp(34px,4.5vw,72px)}.cm-lvl-intro h2 .hl{color:var(--yellow)}"
            ".cm-lvl-intro p{margin-top:20px;font:500 clamp(16px,1.3vw,18px)/1.6 Inter;color:rgba(253,249,234,.78);max-width:44ch}"
            ".cm-fourlevels{display:flex;flex-direction:column;gap:14px}"
            "@media(max-width:640px){.cm-lvl-in{grid-template-columns:1fr;gap:20px}.cm-lvl-frame{width:70%}}")

def level_card(num, title, sub, body, link, img, color="blue", alt=""):
    bg = (f'<svg class="cm-lvl-bg" viewBox="0 0 349.87 292.26" preserveAspectRatio="none" aria-hidden="true">'
          f'<path d="{_SVC_K}" fill="var(--{color})"/></svg>')
    return (f'<article class="cm-lvl">{bg}<div class="cm-lvl-in">'
            f'<div class="cm-lvl-frame"><img src="{img}" alt="{_html.escape(alt or title)}" loading="lazy"></div>'
            f'<div class="cm-lvl-copy"><span class="cm-lvl-num">{num}</span>'
            f'<h3 class="cm-lvl-t">{title}</h3><p class="cm-lvl-sub">{sub}</p>'
            f'<p class="cm-lvl-b">{body}</p>'
            f'<a class="cm-lvl-link" href="#">{link} →</a></div></div></article>')

def four_levels(intro_html, lead, levels):
    """levels = list of (num, title, sub, body, link, img, color)."""
    intro = f'<div class="cm-lvl-intro"><h2>{intro_html}</h2><p>{_html.escape(lead)}</p></div>'
    cards = "".join(level_card(*lv) for lv in levels)
    return f'<div class="cm-fourlevels">{intro}{cards}</div>'

# ---------------------------------------------------------------------------
# How it works (process line) — organism
# ---------------------------------------------------------------------------
def hiw_css():
    return (feature_css() + badge_css() + "/* ---- CM: how it works ---- */"
            ".cm-hiw{background:var(--cream);color:var(--ink)}"
            ".cm-hiw-head{position:relative;display:grid;grid-template-columns:1fr auto;align-items:start;gap:40px;"
            "margin-bottom:clamp(32px,5vw,60px)}"
            ".cm-hiw-title{font-family:Poppins,sans-serif;font-weight:900;text-transform:uppercase;letter-spacing:-.02em;"
            "line-height:1.0;font-size:clamp(30px,4vw,60px);color:var(--ink)}"
            ".cm-hiw-title .hl{position:relative;display:inline-block;padding:0 .12em;margin:0 -.12em}"
            ".cm-hiw-title .hl::before{content:'';position:absolute;left:0;right:0;top:.20em;bottom:.10em;background:var(--pink);z-index:-1}"
            ".cm-hiw-badge{flex:none}"
            ".cm-hiw-grid{display:grid;grid-template-columns:1fr 1fr;gap:clamp(12px,1.4vw,20px)}"
            ".cm-hiw-grid .cm-feat{width:auto}"
            "@media(max-width:760px){.cm-hiw-head{grid-template-columns:1fr;gap:18px}.cm-hiw-grid{grid-template-columns:1fr}}")

def how_it_works(steps, monkey_svg=None, title_html=None):
    """steps = list of (num, title, body). Colors ramp light→dark blue."""
    title_html = title_html or 'HOW <span class="hl">CUSTOM MERCH</span><br>WITH CROOKED MONKEY WORKS'
    cols = ["#BCEDFC", "#9DE1FA", "#80D5F4", "#63C6EC"]
    sides = ["r", "both", "both", "l"]
    cards = "".join(feature_card(n, t, b, side=sides[i % 4], bg=cols[i % 4])
                    for i, (n, t, b) in enumerate(steps))
    bdg = f'<div class="cm-hiw-badge">{badge(monkey_svg, size="120px")}</div>' if monkey_svg else ""
    return ('<section class="cm-hiw"><div class="cm-hiw-head">'
            f'<h2 class="cm-hiw-title">{title_html}</h2>{bdg}</div>'
            f'<div class="cm-hiw-grid">{cards}</div></section>')

# ---------------------------------------------------------------------------
# Who we make merch for — buyer-type tabs (interactive) — organism
# ---------------------------------------------------------------------------
def who_css():
    return ("/* ---- CM: who we make merch for (tabs) ---- */"
            ".cm-who{background:#fff;color:var(--ink)}"
            ".cm-who-head{text-align:center;max-width:54ch;margin:0 auto clamp(28px,4vw,48px)}"
            ".cm-who-title{font-family:Poppins,sans-serif;font-weight:900;text-transform:uppercase;letter-spacing:-.02em;"
            "line-height:1;font-size:clamp(30px,4vw,52px)}"
            ".cm-who-sub{margin-top:14px;font:500 clamp(15px,1.1vw,17px)/1.5 Inter;color:rgba(4,18,2,.6)}"
            ".cm-who-grid{display:grid;grid-template-columns:1fr 1fr;gap:clamp(32px,5vw,72px);align-items:center;max-width:1180px;margin:0 auto}"
            ".cm-who-card{position:relative;border-radius:var(--r-card);overflow:hidden;background:var(--cream);transition:opacity .15s ease}"
            ".cm-who-photo{aspect-ratio:3/2;background:var(--cream)}.cm-who-photo img{width:100%;height:100%;object-fit:cover;display:block}"
            ".cm-who-cap{background:var(--accent,var(--yellow));color:var(--ink);padding:clamp(18px,2vw,28px)}"
            ".cm-who-eyebrow{display:block;font:800 12px/1 Inter;letter-spacing:.13em;text-transform:uppercase;opacity:.66;margin-bottom:8px}"
            ".cm-who-cap p{font:600 clamp(14px,1.1vw,18px)/1.4 Inter;max-width:38ch}"
            ".cm-who-list{display:flex;flex-direction:column;gap:clamp(2px,.4vw,8px)}"
            ".cm-who-tab{display:flex;align-items:baseline;gap:clamp(12px,1vw,18px);width:100%;padding:clamp(11px,1.1vh,16px) 8px;"
            "background:none;border:0;cursor:pointer;text-align:left;font-family:inherit;border-radius:10px;transition:transform .18s ease}"
            ".cm-who-idx{flex:none;font:700 13px/1 Inter;letter-spacing:.04em;color:rgba(4,18,2,.38);transform:translateY(-.35em);transition:color .18s ease}"
            ".cm-who-name{position:relative;font-family:Poppins,sans-serif;font-weight:900;text-transform:uppercase;letter-spacing:-.01em;"
            "line-height:1;font-size:clamp(19px,2.15vw,30px);color:rgba(4,18,2,.32);transition:color .18s ease}"
            ".cm-who-name::before{content:'';position:absolute;left:-.1em;right:-.1em;top:.18em;bottom:.06em;background:var(--accent,var(--yellow));"
            "z-index:-1;opacity:0;transform:scaleX(.55);transform-origin:left;transition:opacity .2s ease,transform .28s cubic-bezier(.2,.75,.2,1)}"
            ".cm-who-tab:hover .cm-who-name,.cm-who-tab:hover .cm-who-idx{color:rgba(4,18,2,.7)}"
            ".cm-who-tab.active .cm-who-name,.cm-who-tab.active .cm-who-idx{color:var(--ink)}"
            ".cm-who-tab.active .cm-who-name::before{opacity:1;transform:none}"
            ".cm-who-tab:focus-visible{outline:3px solid var(--ink);outline-offset:2px}"
            "@media(max-width:760px){.cm-who-grid{grid-template-columns:1fr;gap:24px;max-width:520px}"
            ".cm-who-list{order:1}.cm-who-card{order:2}}")

def who_section(items, title_html="WHO WE MAKE<br>MERCH FOR",
                sub="Six buyer types. Pick the closest match — we'll tailor scope when we quote."):
    """items = list of (name, accent, img_src, copy). First is shown by default."""
    tabs = []
    for i, (name, acc, img, copy) in enumerate(items):
        sel = "true" if i == 0 else "false"
        tabs.append(
            f'<button class="cm-who-tab{" active" if i == 0 else ""}" id="cm-who-tab-{i}" role="tab" '
            f'aria-selected="{sel}" aria-controls="cm-who-panel" tabindex="{0 if i == 0 else -1}" '
            f'data-src="{img}" data-accent="{acc}" data-copy="{_html.escape(copy, quote=True)}" '
            f'data-alt="{_html.escape(name, quote=True)} merch sample" style="--accent:{acc}">'
            f'<span class="cm-who-idx">{i+1:02d}</span><span class="cm-who-name">{_html.escape(name)}</span></button>')
    tablist = ('<div class="cm-who-list" role="tablist" aria-orientation="vertical" aria-label="Buyer types">'
               + "".join(tabs) + '</div>')
    n0, a0, i0, c0 = items[0]
    panel = (f'<figure class="cm-who-card" id="cm-who-panel" role="tabpanel" aria-labelledby="cm-who-tab-0" '
             f'tabindex="0" style="--accent:{a0}">'
             f'<div class="cm-who-photo"><img src="{i0}" alt="{_html.escape(n0)} merch sample" loading="lazy"></div>'
             f'<figcaption class="cm-who-cap"><span class="cm-who-eyebrow">{_html.escape(n0)}</span>'
             f'<p>{_html.escape(c0)}</p></figcaption></figure>')
    return ('<section class="cm-who"><header class="cm-who-head">'
            f'<h2 class="cm-who-title">{title_html}</h2><p class="cm-who-sub">{_html.escape(sub)}</p></header>'
            f'<div class="cm-who-grid">{panel}{tablist}</div></section>')

def who_js():
    return ("/* CM WHO tabs: click + arrow keys; cross-fades the card. */"
            "var reduceW=matchMedia('(prefers-reduced-motion:reduce)').matches;"
            "var wtabs=[].slice.call(document.querySelectorAll('.cm-who-tab'));"
            "if(wtabs.length){var wp=document.getElementById('cm-who-panel'),"
            "wimg=wp.querySelector('img'),weye=wp.querySelector('.cm-who-eyebrow'),wcopy=wp.querySelector('.cm-who-cap p');"
            "var cur=0,fadeT=null;"
            "function whoSel(i,focus){if(i===cur&&!focus)return;cur=i;"
            "for(var j=0;j<wtabs.length;j++){var on=j===i;wtabs[j].classList.toggle('active',on);"
            "wtabs[j].setAttribute('aria-selected',on?'true':'false');wtabs[j].tabIndex=on?0:-1;}"
            "var t=wtabs[i];function apply(){wimg.src=t.dataset.src;wimg.alt=t.dataset.alt;"
            "weye.textContent=t.querySelector('.cm-who-name').textContent;wcopy.textContent=t.dataset.copy;"
            "wp.style.setProperty('--accent',t.dataset.accent);wp.setAttribute('aria-labelledby',t.id);wp.style.opacity=1;}"
            "if(fadeT){clearTimeout(fadeT);fadeT=null;}"
            "if(reduceW){apply();}else{wp.style.opacity=0;fadeT=setTimeout(function(){apply();fadeT=null;},140);}"
            "if(focus)t.focus();}"
            "wtabs.forEach(function(t,i){t.addEventListener('click',function(){whoSel(i,false);});"
            "t.addEventListener('keydown',function(e){var k=e.key,ni=-1;"
            "if(k==='ArrowDown'||k==='ArrowRight')ni=(i+1)%wtabs.length;"
            "else if(k==='ArrowUp'||k==='ArrowLeft')ni=(i-1+wtabs.length)%wtabs.length;"
            "else if(k==='Home')ni=0;else if(k==='End')ni=wtabs.length-1;"
            "if(ni>=0){e.preventDefault();whoSel(ni,true);}});});}")


# ===========================================================================
# PREMIUM-BRAND PAGE components (Patagonia-style brand landing)
# ===========================================================================

# ---- Stat strip (ink bar of icon + label + value) — molecule ----
def stat_strip_css():
    return ("/* ---- CM: stat strip ---- */"
            ".cm-strip{background:var(--ink);color:var(--cream)}"
            ".cm-strip-in{display:grid;grid-template-columns:repeat(4,1fr);max-width:1340px;margin:0 auto}"
            ".cm-st{display:flex;align-items:center;gap:14px;padding:22px clamp(16px,2.4vw,36px);border-right:1px solid rgba(253,249,234,.16)}"
            ".cm-st:last-child{border-right:0}"
            ".cm-st .ic{color:var(--mint);flex:0 0 auto;width:26px;height:26px}.cm-st .ic svg{width:26px;height:26px}"
            ".cm-st .lab{font:600 11px/1 Inter;letter-spacing:.14em;text-transform:uppercase;color:rgba(253,249,234,.55);margin-bottom:7px}"
            ".cm-st .val{font:700 clamp(16px,1.4vw,20px)/1 Inter;letter-spacing:-.01em;color:var(--cream)}"
            "@media(max-width:640px){.cm-strip-in{grid-template-columns:1fr 1fr}"
            ".cm-st{border-bottom:1px solid rgba(253,249,234,.16)}.cm-st:nth-child(2){border-right:0}}")

def stat_strip(items):
    """items = list of (icon_svg, label, value)."""
    cells = "".join(f'<div class="cm-st"><span class="ic">{ic}</span>'
                    f'<div><div class="lab">{_html.escape(l)}</div><div class="val">{v}</div></div></div>'
                    for ic, l, v in items)
    return f'<div class="cm-strip"><div class="cm-strip-in">{cells}</div></div>'

# ---- Statement band (eyebrow + big statement + copy + quote + photo) — organism ----
def statement_css():
    return ("/* ---- CM: statement band ---- */"
            ".cm-stmt{background:#fff;color:var(--ink);padding:clamp(48px,7vw,90px) clamp(24px,5vw,64px)}"
            ".cm-stmt-in{max-width:1200px;margin:0 auto;display:grid;grid-template-columns:1fr 1fr;gap:clamp(28px,5vw,64px);align-items:center}"
            ".cm-stmt-eyebrow{display:inline-block;font:900 12px/1 Poppins,sans-serif;letter-spacing:.14em;text-transform:uppercase;color:var(--mint-deep);margin-bottom:18px}"
            ".cm-stmt-t{font:900 clamp(28px,4.4vw,52px)/1.02 Poppins,sans-serif;letter-spacing:-.02em;text-transform:uppercase;margin:0 0 22px;color:var(--ink)}"
            ".cm-stmt-b{font:500 clamp(15px,1.2vw,17px)/1.62 Inter;color:rgba(4,18,2,.72);margin:0 0 16px;max-width:48ch}"
            ".cm-quote{margin:28px 0 0;padding:20px 24px;background:var(--mint);border-radius:16px}"
            ".cm-quote p{font:600 clamp(15px,1.3vw,18px)/1.45 Inter;color:var(--mint-deep);margin:0 0 10px}"
            ".cm-quote cite{font:600 12px/1 Inter;letter-spacing:.06em;text-transform:uppercase;color:var(--mint-deep);opacity:.85;font-style:normal}"
            ".cm-stmt-photo{aspect-ratio:4/4.4;border-radius:16px;overflow:hidden;background:var(--blue);margin:0}"
            ".cm-stmt-photo img{width:100%;height:100%;object-fit:cover;display:block}"
            "@media(max-width:640px){.cm-stmt-in{grid-template-columns:1fr}.cm-stmt-photo{order:-1;aspect-ratio:4/3}}")

def statement_band(eyebrow, title, paras, img, quote=None, cite=None, alt=""):
    ps = "".join(f'<p class="cm-stmt-b">{p}</p>' for p in paras)
    q = ""
    if quote:
        c = f'<cite>{_html.escape(cite)}</cite>' if cite else ""
        q = f'<div class="cm-quote"><p>{quote}</p>{c}</div>'
    return ('<section class="cm-stmt"><div class="cm-stmt-in"><div>'
            f'<span class="cm-stmt-eyebrow">{_html.escape(eyebrow)}</span>'
            f'<h2 class="cm-stmt-t">{title}</h2>{ps}{q}</div>'
            f'<figure class="cm-stmt-photo"><img src="{img}" alt="{_html.escape(alt)}"></figure>'
            '</div></section>')

# ---- Photo caption card (photo + bright caption) — molecule ----
def photo_card_css():
    return ("/* ---- CM: photo caption card ---- */"
            # auto-fit so 3 or 4 cards each land in one clean row (1-up on mobile)
            ".cm-photocard-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:clamp(16px,2vw,26px)}"
            ".cm-photocard{border-radius:16px;overflow:hidden;background:#fff;display:flex;flex-direction:column;margin:0}"
            ".cm-photocard-photo{aspect-ratio:4/3.4;overflow:hidden;background:var(--cream)}"
            ".cm-photocard-photo img{width:100%;height:100%;object-fit:cover;display:block}"
            ".cm-photocard-cap{padding:clamp(20px,2vw,26px);flex:1;background:var(--accent,var(--mint))}"
            ".cm-photocard-cap h3{font:900 clamp(19px,1.8vw,25px)/1.05 Poppins,sans-serif;letter-spacing:-.01em;text-transform:uppercase;margin:0 0 12px;color:var(--on,var(--mint-deep))}"
            ".cm-photocard-cap p{font:500 clamp(14px,1.05vw,15.5px)/1.55 Inter;margin:0;color:var(--on,var(--mint-deep));opacity:.86}"
            "@media(max-width:760px){.cm-photocard-grid{grid-template-columns:1fr;max-width:420px;margin:0 auto}}")

def photo_card(img, title, body, accent="mint", alt=""):
    return (f'<article class="cm-photocard" style="--accent:var(--{accent});--on:var(--{accent}-deep)">'
            f'<div class="cm-photocard-photo"><img src="{img}" alt="{_html.escape(alt or title)}"></div>'
            f'<div class="cm-photocard-cap"><h3>{title}</h3><p>{body}</p></div></article>')

def photo_grid(items):
    """items = list of (img, title, body, accent)."""
    return '<div class="cm-photocard-grid">' + "".join(photo_card(*it) for it in items) + '</div>'

# ---- Use-case K-card (blue chip card with animated K sweep) — molecule ----
_CM_KX = ("<svg class='cm-kx' viewBox='0 0 40.29 173' preserveAspectRatio='none' aria-hidden='true'>"
          "<path fill='#041202' d='M0,86.51 c11.69,-7.96 21.21,-18.78 28.56,-32.43 7.35,-13.67 11.25,-30.54 11.73,-50.61 "
          "L40.29,0 L40.29,173 L40.29,169.53 c-.48,-20.08 -4.38,-36.93 -11.73,-50.6 -7.35,-13.67 -16.87,-24.47 -28.56,-32.43 Z'/></svg>")

def usecase_css():
    return ("/* ---- CM: use-case K-card ---- */"
            ".cm-usecase-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:clamp(14px,1.6vw,22px)}"
            ".cm-usecase{position:relative;background:var(--blue);color:var(--blue-deep);border-radius:22px 6px 6px 22px;"
            "overflow:hidden;min-height:220px;padding:24px;display:flex;flex-direction:column}"
            ".cm-usecase .cm-kx{position:absolute;top:0;right:0;height:100%;width:46px;transform:scaleX(0);"
            "transform-origin:right center;transition:transform .6s cubic-bezier(.2,.75,.2,1);pointer-events:none}"
            ".cm-usecase:hover .cm-kx,.cm-usecase:focus-within .cm-kx{transform:scaleX(1)}"
            ".cm-usecase-chip{width:44px;height:44px;border-radius:11px;background:var(--yellow);color:var(--yellow-deep);"
            "display:flex;align-items:center;justify-content:center}.cm-usecase-chip svg{width:22px;height:22px}"
            ".cm-usecase-t{margin-top:auto;font:800 clamp(16px,1.5vw,19px)/1.18 Inter;letter-spacing:-.01em;max-width:11ch;color:var(--blue-deep)}"
            "@media(max-width:820px){.cm-usecase-grid{grid-template-columns:1fr 1fr}}"
            "@media(max-width:460px){.cm-usecase-grid{grid-template-columns:1fr}}"
            "@media (prefers-reduced-motion:reduce){.cm-usecase .cm-kx{transition:none}}")

def usecase_card(icon_svg, title):
    return (f'<article class="cm-usecase">{_CM_KX}'
            f'<div class="cm-usecase-chip">{icon_svg}</div>'
            f'<h3 class="cm-usecase-t">{title}</h3></article>')

def usecase_grid(items):
    """items = list of (icon_svg, title)."""
    return '<div class="cm-usecase-grid">' + "".join(usecase_card(*it) for it in items) + '</div>'

# ---- Decoration card (photo + badge + bright caption + bullet list) — molecule ----
def decoration_css():
    return ("/* ---- CM: decoration card ---- */"
            ".cm-dcard-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:clamp(14px,1.6vw,22px)}"
            ".cm-dcard{position:relative;border-radius:16px;overflow:hidden;background:#fff;display:flex;flex-direction:column;margin:0}"
            ".cm-dcard-photo{position:relative;aspect-ratio:4/2.7;overflow:hidden;background:var(--cream)}"
            ".cm-dcard-photo img{width:100%;height:100%;object-fit:cover;display:block}"
            ".cm-dcard-badge{position:absolute;top:12px;right:12px;background:var(--ink);color:var(--cream);border-radius:999px;"
            "padding:6px 13px;font:900 10px/1 Poppins,sans-serif;letter-spacing:.12em;text-transform:uppercase}"
            ".cm-dcard-cap{flex:1;padding:clamp(18px,1.6vw,24px);background:var(--accent,var(--yellow))}"
            ".cm-dcard-cap h3{font:900 clamp(18px,1.7vw,23px)/1.05 Poppins,sans-serif;letter-spacing:-.01em;text-transform:uppercase;margin:0 0 12px;color:var(--on,var(--yellow-deep))}"
            ".cm-dcard-desc{font:500 clamp(13.5px,1vw,15px)/1.5 Inter;color:rgba(4,18,2,.78);margin:0 0 16px}"
            ".cm-dcard-list{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:9px}"
            ".cm-dcard-list li{position:relative;padding-left:18px;font:600 clamp(13px,.95vw,14.5px)/1.35 Inter;color:var(--ink)}"
            ".cm-dcard-list li::before{content:'';position:absolute;left:0;top:.5em;width:6px;height:6px;border-radius:50%;background:var(--on,var(--yellow-deep))}"
            "@media(max-width:900px){.cm-dcard-grid{grid-template-columns:1fr 1fr}}"
            "@media(max-width:480px){.cm-dcard-grid{grid-template-columns:1fr;max-width:400px;margin:0 auto}}")

def decoration_card(img, title, desc, items, accent="yellow", badge=None, alt=""):
    bd = f'<span class="cm-dcard-badge">{_html.escape(badge)}</span>' if badge else ""
    lis = "".join(f'<li>{_html.escape(x)}</li>' for x in items)
    return (f'<article class="cm-dcard" style="--accent:var(--{accent});--on:var(--{accent}-deep)">'
            f'<div class="cm-dcard-photo"><img src="{img}" alt="{_html.escape(alt or title)}">{bd}</div>'
            f'<div class="cm-dcard-cap"><h3>{title}</h3><p class="cm-dcard-desc">{desc}</p>'
            f'<ul class="cm-dcard-list">{lis}</ul></div></article>')

def decoration_grid(items):
    """items = list of dicts/tuples (img, title, desc, [bullets], accent, badge)."""
    return '<div class="cm-dcard-grid">' + "".join(decoration_card(*it) for it in items) + '</div>'

# ---- Product card (photo + category + name + price + swatches) — molecule ----
def product_css():
    return ("/* ---- CM: product card ---- */"
            ".cm-product-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:clamp(14px,1.6vw,22px)}"
            ".cm-product{background:#fff;border-radius:16px;padding:10px 10px 4px;margin:0}"
            ".cm-product-photo{aspect-ratio:4/5;border-radius:10px;overflow:hidden;background:var(--cream);margin-bottom:14px}"
            ".cm-product-photo img{width:100%;height:100%;object-fit:cover;display:block}"
            ".cm-product-cat{font:600 11px/1 Inter;letter-spacing:.12em;text-transform:uppercase;color:rgba(4,18,2,.48);padding:0 6px;margin-bottom:8px}"
            ".cm-product-name{font:700 clamp(15px,1.2vw,17px)/1.2 Inter;color:var(--ink);padding:0 6px;margin:0 0 12px}"
            ".cm-product-foot{display:flex;align-items:center;justify-content:space-between;padding:0 6px 10px}"
            ".cm-product-price{font:700 clamp(14px,1.05vw,16px)/1 Inter;color:var(--ink)}"
            ".cm-product-sw{display:flex;gap:6px}"
            ".cm-product-sw span{width:13px;height:13px;border-radius:50%;box-shadow:inset 0 0 0 1px rgba(4,18,2,.12)}"
            "@media(max-width:900px){.cm-product-grid{grid-template-columns:1fr 1fr}}"
            "@media(max-width:460px){.cm-product-grid{grid-template-columns:1fr;max-width:320px;margin:0 auto}}")

def product_card(img, name, category, price, swatches=(), alt=""):
    sw = "".join(f'<span style="background:{c}"></span>' for c in swatches)
    return (f'<article class="cm-product"><div class="cm-product-photo"><img src="{img}" alt="{_html.escape(alt or name)}"></div>'
            f'<div class="cm-product-cat">{_html.escape(category)}</div>'
            f'<h3 class="cm-product-name">{_html.escape(name)}</h3>'
            f'<div class="cm-product-foot"><span class="cm-product-price">{price}</span>'
            f'<span class="cm-product-sw">{sw}</span></div></article>')

def product_grid(items):
    """items = list of (img, name, category, price, swatches)."""
    return '<div class="cm-product-grid">' + "".join(product_card(*it) for it in items) + '</div>'

# ---- Brand hero (centered title + image ticker + sub + CTA) — organism ----
def brand_hero_css():
    return (ticker_css() + button_css() + "/* ---- CM: brand hero ---- */"
            ".cm-bhero{background:var(--cream);color:var(--ink);overflow:hidden;padding:clamp(40px,6vw,72px) 0}"
            ".cm-bhero-title{text-align:center;font:900 clamp(30px,4.8vw,62px)/.98 Poppins,sans-serif;letter-spacing:-.02em;"
            "text-transform:uppercase;margin:0 auto;max-width:1100px;padding:0 clamp(16px,4vw,48px);color:var(--ink)}"
            ".cm-bhero-title .hl{position:relative;display:inline-block}"
            ".cm-bhero-title .hl::before{content:'';position:absolute;left:-.05em;right:-.05em;top:.12em;bottom:.05em;background:var(--blue);z-index:-1}"
            # hero vertical rhythm (matches the brand pages): title -> gallery -> text/button
            ".cm-bhero .cm-ticker{margin-top:clamp(44px,6.5vh,72px)}"
            ".cm-bhero-bottom{display:grid;grid-template-columns:1.35fr .65fr;gap:clamp(24px,4vw,56px);align-items:center;"
            "max-width:var(--maxw,1340px);margin:clamp(56px,8vh,96px) auto 0;padding:0 var(--pad,clamp(24px,5vw,72px))}"
            ".cm-bhero-sub{font:500 clamp(15px,1.4vw,19px)/1.55 Inter;color:rgba(4,18,2,.74);max-width:52ch;margin:0}"
            ".cm-bhero-cta{display:inline-flex;align-items:center;justify-content:center;background:var(--mint);color:var(--mint-deep);"
            "border-radius:999px;padding:17px 34px;font:800 14px/1 Inter;letter-spacing:.14em;text-transform:uppercase;text-decoration:none;"
            "transition:transform .15s ease}.cm-bhero-cta:hover{transform:translateY(-2px)}"
            "@media(max-width:640px){.cm-bhero-bottom{grid-template-columns:1fr}}")

def brand_hero(title_html, sub, images, cta="Talk to a Merch Expert"):
    return ('<section class="cm-bhero">'
            f'<h1 class="cm-bhero-title">{title_html}</h1>'
            + ticker(images)
            + f'<div class="cm-bhero-bottom"><p class="cm-bhero-sub">{_html.escape(sub)}</p>'
            f'<div><a class="cm-bhero-cta" href="#">{_html.escape(cta)}</a></div></div></section>')

# ---- Process row (drawn Card_Shape silhouettes, blue ramp) — organism ----
# Uses the original 346×173 silhouettes (same art as the home page), so the row
# matches the brand pages exactly — NOT the adaptive K-notch.
_PROC1 = ("M305.71,86.51c11.69-7.96,21.21-18.78,28.56-32.43,7.35-13.67,11.25-30.54,11.73-50.61,"
          "0-.92-.35-1.73-1.05-2.42-.69-.7-1.5-1.04-2.43-1.04H18.11C8.11,0,.01,8.1.01,18.1.01,51.32,0,121.66,0,154.87"
          "c0,10,8.1,18.09,18.1,18.09l324.43.03c.92,0,1.73-.34,2.43-1.04.69-.69,1.05-1.5,1.05-2.42"
          "-.48-20.08-4.38-36.93-11.73-50.6-7.35-13.67-16.87-24.47-28.56-32.43Z")
_PROC2 = ("M305.70,86.51c11.69-7.96,21.21-18.78,28.56-32.43,7.35-13.67,11.25-30.54,11.73-50.61,"
          "0-.92-.35-1.73-1.05-2.42-.69-.7-1.5-1.04-2.43-1.04H40.32c0,.99-.02,2.45-.02,3.37"
          "-.48,20.07-4.38,36.95-11.74,50.63-7.36,13.66-16.88,24.49-28.57,32.45,11.69,7.96,21.22,18.77,28.57,32.45,"
          "7.35,13.67,11.26,30.53,11.74,50.62,0,.92,0,3.45,0,3.45l302.21.03c.92,0,1.73-.34,2.43-1.04"
          ".69-.69,1.05-1.5,1.05-2.42-.48-20.08-4.38-36.93-11.73-50.6-7.35-13.67-16.87-24.47-28.56-32.43Z")
# Card 4 is NOT card 1 mirrored: it needs a concave notch on the LEFT (to receive
# card 3's tooth) + a rounded RIGHT. This is its own drawn silhouette.
_PROC4 = ("M40.32,0.74c0,.99-.02,2.45-.02,3.37-.48,20.07-4.38,36.95-11.74,50.63-7.36,13.66-16.88,24.49-28.57,32.45,"
          "11.69,7.96,21.22,18.77,28.57,32.45,7.35,13.67,11.26,30.53,11.74,50.62,0,.92,0,3.45,0,3.45"
          "L327.9,173.71C337.9,172.96 346,164.87 346,154.87C346,121.66 345.99,51.32 345.99,18.1"
          "C345.99,8.1 337.89,0 327.89,0L40.32,0.74Z")
def _proc_mask(d):
    s = ("<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 346 173' preserveAspectRatio='none'>"
         "<path fill='white' d='" + d + "'/></svg>")
    return "data:image/svg+xml," + urllib.parse.quote(s, safe="")
_PM1, _PM2, _PM4 = _proc_mask(_PROC1), _proc_mask(_PROC2), _proc_mask(_PROC4)

def process_css():
    # Cards are assigned a ROLE (not a fixed index), so the row closes at any
    # count: .pf = first (round-left + tooth-right), .pm = middle (notch-left +
    # tooth-right), .pl = last (notch-left + round-right), .po = only (rounded).
    return ("/* ---- CM: process row (drawn silhouettes, blue ramp; 2–4 steps) ---- */"
            ".cm-proc-row{display:grid;grid-template-columns:repeat(var(--n,4),1fr);gap:8px}"
            ".cm-proc{position:relative;min-height:300px}"
            ".cm-proc-bg{position:absolute;inset:0;background:var(--c,#9DE1FA);-webkit-mask:no-repeat center/100% 100%;mask:no-repeat center/100% 100%}"
            ".cm-proc.pf .cm-proc-bg{-webkit-mask-image:url(\"" + _PM1 + "\");mask-image:url(\"" + _PM1 + "\")}"
            ".cm-proc.pm .cm-proc-bg{-webkit-mask-image:url(\"" + _PM2 + "\");mask-image:url(\"" + _PM2 + "\")}"
            ".cm-proc.pl .cm-proc-bg{-webkit-mask-image:url(\"" + _PM4 + "\");mask-image:url(\"" + _PM4 + "\")}"
            ".cm-proc.po .cm-proc-bg{-webkit-mask:none;mask:none;border-radius:28px 8px 8px 28px}"
            ".cm-proc-in{position:relative;z-index:1;height:100%;min-height:300px;display:flex;flex-direction:column;padding:30px}"
            ".cm-proc.tl .cm-proc-in{padding-left:52px}.cm-proc.nr .cm-proc-in{padding-right:52px}"
            ".cm-proc-num{font:900 clamp(38px,3.6vw,54px)/1 Poppins,sans-serif;letter-spacing:-.02em;color:var(--blue-deep);margin-bottom:16px}"
            ".cm-proc-t{font:900 clamp(17px,1.5vw,21px)/1.05 Poppins,sans-serif;letter-spacing:-.01em;text-transform:uppercase;color:var(--blue-deep);margin:auto 0 8px}"
            ".cm-proc-meta{font:700 11px/1 Inter;letter-spacing:.1em;text-transform:uppercase;color:rgba(0,53,71,.6);margin-bottom:12px}"
            ".cm-proc-b{font:500 clamp(13px,1vw,14.5px)/1.5 Inter;color:rgba(4,18,2,.72);margin:0}"
            "@media(max-width:1000px){.cm-proc-row{grid-template-columns:1fr;gap:16px}"
            ".cm-proc,.cm-proc-in{min-height:240px}.cm-proc-in{padding:34px 40px 34px 36px}.cm-proc-t{margin:26px 0 10px}"
            ".cm-proc-bg{-webkit-mask:none;mask:none;border-radius:28px 8px 8px 28px}}")

_PROC_RAMP4 = ["#BCEDFC", "#9DE1FA", "#80D5F4", "#63C6EC"]  # canonical 4-step ramp
def _blue_ramp(n):
    """n blue shades, light → dark. Keeps the exact 4-step ramp; interpolates otherwise."""
    if n <= 1:
        return [_PROC_RAMP4[0]]
    if n == 4:
        return list(_PROC_RAMP4)
    a, b = (0xBC, 0xED, 0xFC), (0x63, 0xC6, 0xEC)
    return ["#%02X%02X%02X" % tuple(round(a[k] + (b[k] - a[k]) * (i / (n - 1))) for k in range(3))
            for i in range(n)]

def process_row(steps):
    """steps = list of (num, title, meta, body). Works for 2–4 steps: the first
    card always rounds on the left and the last rounds on the right, so the row
    closes cleanly whether you pass 3 or 4. Blue ramp scales to the count."""
    n = len(steps)
    ramp = _blue_ramp(n)
    out = []
    for i, (num, title, meta, body) in enumerate(steps):
        if n == 1:
            cls = "po"
        elif i == 0:
            cls = "pf nr"
        elif i == n - 1:
            cls = "pl tl"
        else:
            cls = "pm tl nr"
        out.append(
            f'<article class="cm-proc {cls}" style="--c:{ramp[i]}"><div class="cm-proc-bg"></div>'
            f'<div class="cm-proc-in"><div class="cm-proc-num">{_html.escape(num)}</div>'
            f'<h3 class="cm-proc-t">{_html.escape(title)}</h3>'
            f'<div class="cm-proc-meta">{meta}</div><p class="cm-proc-b">{body}</p></div></article>')
    return f'<div class="cm-proc-row" style="--n:{n}">' + "".join(out) + '</div>'


# ---- Info card (icon chip + eyebrow + body) — molecule ----
def info_card_css():
    return ("/* ---- CM: info card ---- */"
            ".cm-info-stack{display:flex;flex-direction:column;gap:clamp(14px,1.4vw,20px)}"
            ".cm-info{background:#fff;border-radius:clamp(16px,1.4vw,22px);padding:clamp(22px,2vw,30px);"
            "display:flex;gap:18px;align-items:flex-start}"
            ".cm-info-chip{flex:none;width:48px;height:48px;border-radius:50%;background:var(--accent,var(--yellow));"
            "color:var(--on,var(--yellow-deep));display:flex;align-items:center;justify-content:center}"
            ".cm-info-chip svg{width:22px;height:22px}"
            ".cm-info-eyebrow{display:block;font:800 12px/1 Inter;letter-spacing:.14em;text-transform:uppercase;"
            "color:var(--on,var(--yellow-deep));margin-bottom:10px}"
            ".cm-info-b{font:500 clamp(14px,1.05vw,16px)/1.55 Inter;color:rgba(4,18,2,.72);margin:0;max-width:48ch}")

def info_card(icon_svg, eyebrow, body, accent="yellow"):
    return (f'<article class="cm-info" style="--accent:var(--{accent});--on:var(--{accent}-deep)">'
            f'<span class="cm-info-chip">{icon_svg}</span>'
            f'<div><span class="cm-info-eyebrow">{_html.escape(eyebrow)}</span>'
            f'<p class="cm-info-b">{body}</p></div></article>')

def info_stack(items):
    """items = list of (icon_svg, eyebrow, body, accent)."""
    return '<div class="cm-info-stack">' + "".join(info_card(*it) for it in items) + '</div>'

# ---- Callout section (heading left + info-card stack right) — organism ----
def callout_css():
    return (heading_css() + info_card_css() + "/* ---- CM: callout section ---- */"
            ".cm-callout{background:var(--cream);color:var(--ink);padding:clamp(48px,7vw,90px) clamp(24px,5vw,64px)}"
            ".cm-callout-in{max-width:1280px;margin:0 auto;display:grid;grid-template-columns:minmax(0,.9fr) minmax(0,1.1fr);"
            "gap:clamp(36px,6vw,88px);align-items:center}"
            "@media(max-width:820px){.cm-callout-in{grid-template-columns:1fr;gap:32px}}")

def callout_section(eyebrow, title, body, cards, eyebrow_color="var(--pink-deep)"):
    """Two-column 'what to know' callout: heading on the left, info cards on the right.
    cards = list of (icon_svg, eyebrow, body, accent)."""
    left = (f'<div class="cm-heading"><span class="cm-h-eyebrow" style="color:{eyebrow_color}">{_html.escape(eyebrow)}</span>'
            f'<h2>{title}</h2><p class="cm-h-sub">{_html.escape(body)}</p></div>')
    return f'<section class="cm-callout"><div class="cm-callout-in"><div>{left}</div>{info_stack(cards)}</div></section>'


# ===========================================================================
# LAYOUT SYSTEM — page-level rules (spacing, grid, section sizes)
# ===========================================================================
# Components own their look; the PAGE owns its rhythm. These rules are what make
# a page feel cohesive: one gutter, one max content width, sections that fill the
# viewport and center their content. Emit layout_css() everywhere; on a real page
# also emit page_css() and wrap the body in <div class="cm-page">.
#
# Tokens:
#   --pad   clamp(24px,5vw,72px)   the single horizontal gutter (side margin)
#   --maxw  1340px                 the single content max-width
# Utilities:
#   .cm-section    one section band — the gutter + standard vertical padding
#   .cm-container  the centered, max-width content column (use inside a section)
# Rules (guidelines that pair with the CSS):
#   • Every content section fills the viewport (min-height:100vh) and centers.
#   • One gutter (--pad) + one max-width (--maxw) across the whole page → aligned edges.
#   • Display headings: 2 lines max — constrain width or use <br>.

def layout_css():
    """Layout tokens + the .cm-section / .cm-container utilities. Safe anywhere."""
    return ("/* ---- CM: layout tokens + utilities ---- */"
            ":root{--pad:clamp(24px,5vw,72px);--maxw:1340px}"
            ".cm-section{padding:clamp(56px,9vh,96px) var(--pad)}"
            ".cm-container{width:100%;max-width:var(--maxw);margin-inline:auto}"
            ".cm-2line{overflow-wrap:break-word}")

# The kit section-level classes + their inner containers (page rules target these).
_SECT = ("cm-bhero", "cm-stmt", "cm-callout", "cm-faqs", "cm-pr", "cm-cta-band", "cm-section")
_INNER = ("cm-bhero-bottom", "cm-stmt-in", "cm-callout-in", "cm-faqs-grid", "cm-pr-grid",
          "cm-cta", "cm-section>.cm-container")

def page_css():
    """Page-shell rules. Emit on a real page and wrap the body in .cm-page:
    every content section fills the viewport, centers, and shares one gutter +
    max content width. (Nav / stat strip / footer are intentionally exempt.)"""
    sect = ",".join(f".cm-page .{c}" for c in _SECT)
    inner = ",".join((f".cm-page .{c}" if ">" not in c else f".cm-page .{c}") for c in _INNER)
    return (
        layout_css()
        + sect + "{min-height:100vh;display:flex;align-items:center;padding-inline:var(--pad)}"
        + inner + "{width:100%;max-width:var(--maxw);margin-inline:auto}"
        # hero: column layout + clearance under the fixed nav
        + ".cm-page .cm-bhero{flex-direction:column;justify-content:center;padding-inline:0;padding-top:clamp(94px,13vh,120px)}"
        # exempt bands: full-bleed, natural height
        + ".cm-page .cm-nav,.cm-page .cm-strip,.cm-page .cm-ft{min-height:0;display:block}"
        + "@media(max-width:820px){" + sect + "{min-height:auto;padding-block:clamp(56px,12vw,88px)}}"
    )


if __name__ == "__main__":
    # tiny smoke test
    print(root_css()[:60], "...")
    print("notch_css length:", len(notch_css()))
    print("button:", button("Request a quote")[:60], "...")
    print("info_card ok:", "cm-info" in info_card("<svg/>", "PRICING", "body"))
    print("callout ok:", "cm-callout" in callout_section("Eyebrow", "<b>T</b>", "body", [("<svg/>", "A", "b", "pink")]))
    print("layout ok:", "--pad" in layout_css() and ".cm-page" in page_css())
    print("nav actions:", "cm-nav-signin" in nav("x"))
    print("process silhouette:", "cm-proc-bg" in process_row([("01", "Quote", "24h", "b")]))
    print("media_card ok:", "cm-media" in media_card("x", "T", "m"))
    print("service_card ok:", "cm-svc" in service_card("x", "T", "m", "L"))
    print("footer ok:", "cm-ft" in footer("x"))
    print("who ok:", "cm-who" in who_section([("A", "var(--blue)", "x", "c")]))
    print("product_card ok:", "cm-product" in product_card("x", "N", "Cat", "$9", ["#000"]))
    print("usecase ok:", "cm-usecase" in usecase_card("<svg/>", "Client gifts"))
    print("stat_strip ok:", "cm-strip" in stat_strip([("<svg/>", "Lead time", "5-8 days")]))
    print("statement ok:", "cm-stmt" in statement_band("Why", "<b>T</b>", ["p"], "x"))
    print("decoration ok:", "cm-dcard" in decoration_card("x", "Emb", "d", ["a", "b"]))
    print("brand_hero ok:", "cm-bhero" in brand_hero("<b>T</b>", "s", ["x"]))
    print("process ok:", "cm-proc" in process_row([("01", "Quote", "24h", "b")]))
