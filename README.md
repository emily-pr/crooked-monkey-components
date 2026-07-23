# Crooked Monkey — Component Library

A visual, browsable catalog of the Crooked Monkey design system that **also shows how
to call each component**, so you can reuse it on a new page. It's generated from
`cm_kit.py` (the shared kit) by `build_catalog.py`, and every output page is
self-contained (only external dependency: Google Fonts — Poppins 900 + Inter).

## Build

```bash
python3 build_catalog.py
```

That writes `index.html`, one collection page per page (`tokens.html`, `home.html`,
`premium-brands.html`), and one `<slug>.html` per component. Open `index.html` in a
browser — no server, no npm.

## How it's browsed — by page, not one long list

The landing page keeps navigation short by grouping into three **collections**:

- **Tokens** — the shared foundation (color, type, spacing, radius).
- **Home Page** — every component the home page is built from.
- **Premium Brands Page** — the brand landing template (Patagonia-style) and its parts.

Pick a collection and you see just that page's components, grouped by **atomic-design
tier** (Atoms → Molecules → Organisms → Templates). Components shared across pages
(Nav, Footer, Buttons, Form, FAQ, Text + Pills…) appear under each page they're used
on; each component page lists its pages under "Used on".

### Home Page components

| Tier | Components |
|---|---|
| **Atoms** | K-Notch Card · Buttons · Premium Pill · Form Input · Eyebrow · Arrow Link · Monkey Badge |
| **Molecules** | Section Heading · Media Card · Feature Card · Checklist · Pill Group · Level Card · Image Ticker · FAQ Accordion |
| **Organisms** | Nav · Hero · Service Cards · Text + Pills · FAQ + Title · Form · Footer · Gallery · Four Levels · How It Works · Who We Make Merch For |
| **Templates** | Landing Page |

### Premium Brands Page components

| Tier | Components |
|---|---|
| **Atoms** | K-Notch Card · Buttons · Premium Pill · Form Input · Eyebrow · Arrow Link *(shared)* |
| **Molecules** | Stat Strip · Photo Card · Use-Case Card · Decoration Card · Product Card · Info Card · Image Ticker · Pill Group · FAQ Accordion |
| **Organisms** | Nav · Brand Hero · Statement Band · Process Row · Callout Section · Text + Pills · FAQ + Title · Form · Footer |
| **Templates** | Premium Brands Page |

- **Per-component page** — three things together:
  1. **Live demo** of every relevant variant (e.g. notch card `side="r"/"l"/"both"`
     and both height modes; service cards; the interactive Who tabs).
  2. **How to call it** — the exact `cm_kit` API snippet (the render helper + the
     `*_css()` you emit once, plus any `*_js()`), with underlying classes as a fallback.
  3. **When to use it / gotchas.**
- **Template previews** — the Home *Landing Page* is composed live from kit organisms
  (`preview-landing.html`); the *Premium Brands Page* is the actual built page
  (`preview-premium.html`, scroll-pinning preserved). Both are shown inside an isolating
  `<iframe>` so their styles never touch the catalog chrome.

Everything is ported faithfully from the live pages, stays on-brand (brand tokens
only, Poppins 900 + Inter), keeps ARIA roles + focus states, and honors
`prefers-reduced-motion`.

## How it fits together

| File | Role |
|---|---|
| `cm_kit.py` | The shared kit. Each component is a `*_css()` returning a CSS string to embed once + a render helper returning HTML (interactive ones also expose a `*_js()`). Source of truth for tokens + components. |
| `build_catalog.py` | The catalog builder. One `REGISTRY` drives every component page; `COLLECTIONS` + `_assign(...)` drive the by-page navigation. |
| `assets/` | `cm_logo_cream.svg` + `monkey_inner.svg` (inlined into nav/footer/badge) and `imgs.json` (product photos as data URIs, home `chief…` + premium `pat…`). |
| `preview-landing.html` | The Home template, composed live from kit organisms. |
| `preview-premium.html` | The built Premium Brands (Patagonia) page — the actual deliverable, iframed by the template. |
| `index.html`, `*.html` | The built, self-contained catalog (this is what GitHub Pages serves). |

## Add a component later (one-step flow)

Everything is registry-driven, so adding a component is one edit to the kit and one
entry in the build — a new card **and** a new page appear automatically.

1. **Add it to the kit** (`cm_kit.py`) using the same shape as everything else — a
   `*_css()` that returns a CSS string to embed once, plus a render helper that
   returns HTML (and a `*_js()` if it's interactive):

   ```python
   def badge_css():
       return ".cm-badge{...}"
   def badge(label, bg="var(--yellow)"):
       return f'<span class="cm-badge" style="background:{bg}">{label}</span>'
   ```

2. **Register it** in `build_catalog.py` — write a tiny `build_badge()` returning
   `(demo_html, css, js)`, then append **one entry** to `REGISTRY`:

   ```python
   def build_badge():
       demo = '<div class="demo">' + cm.badge("NEW") + cm.badge("SALE", bg="var(--pink)") + '</div>'
       return demo, cm.badge_css(), ""

   REGISTRY.append({
       "slug": "badge", "name": "Badge", "eyebrow": "ATOM", "color": "yellow",
       "blurb": "Small status chip.",
       "builder": build_badge,
       "api":   [("Emit CSS once, then render",
                  'cm.badge("NEW")\ncm.badge("SALE", bg="var(--pink)")')],
       "notes": ["<b>Keep it short</b> — one or two words."],
   })
   ```

3. **Assign it to a page** so it shows in the right collection — add the slug to the
   relevant `_assign(...)` call in `build_catalog.py` (e.g. `["home", "premium-brands"]`
   for a shared component). Unassigned slugs default to the Home page.

4. **Rebuild:** `python3 build_catalog.py`. A `badge.html` page appears, and a Badge
   card shows up under its tier on every page it's assigned to.

**Descriptor fields:** `slug` (output filename + URL), `name`, `eyebrow` — the atomic
tier: `TOKENS` / `ATOM` / `MOLECULE` / `ORGANISM` / `TEMPLATE` (sets the index
grouping), `color` (a bright: `yellow`/`blue`/`pink`/`mint` — the card surface +
matching deep accent), `blurb`, `builder` (`() -> (demo_html, css, js)`), `api` (list
of `(label, code)`), `notes` (list of HTML bullet strings).

Interactive components also expose a `*_js()` from the kit — return it as the third
item of your `builder` tuple and it's wired into the page automatically (see the FAQ,
Nav, Form, and Who components).

## Brand rules (kept throughout)

Only brand tokens (no greys — dim ink with opacity for secondary text); ink is the
universal text color, cream is the page, brights are surfaces, deep accents are for
text on their matching bright surface. Fonts: Poppins **900 only** + Inter. ARIA roles
and focus states are preserved and everything honors `prefers-reduced-motion`.
