# Crooked Monkey — Component Library

A visual, browsable catalog of the Crooked Monkey design system that **also shows how
to call each component**, so you can reuse it on a new page. It's generated from
`cm_kit.py` (the shared kit) by `build_catalog.py`, and every output page is
self-contained (only external dependency: Google Fonts — Poppins 900 + Inter).

## Build

```bash
python3 build_catalog.py
```

That writes `index.html` (the card-grid landing page) plus one `<slug>.html` per
component. Open `index.html` in a browser — no server, no npm.

## What's in it

The catalog is organized by **atomic design** — the index groups everything into five
tiers, smallest to largest:

| Tier | Components |
|---|---|
| **Tokens** | Color · Typography · Spacing · Radius |
| **Atoms** | K-Notch Card · Buttons · Premium Pill · Form Input · Eyebrow · Arrow Link · Monkey Badge |
| **Molecules** | Section Heading · Media Card · Feature Card · Checklist · Pill Group · Level Card · Image Ticker · FAQ Accordion |
| **Organisms** | Nav · Hero · Service Cards · Text + Pills · FAQ + Title · Form · Footer · Gallery · Four Levels · How It Works · Who We Make Merch For |
| **Templates** | Landing Page (organisms composed into a real page) |

- **Index / landing** — a bright card grid grouped by tier, modelled on the brand's
  card-grid navigation. Each card links to a component page.
- **Per-component page** — three things together:
  1. **Live demo** of every relevant variant (e.g. notch card `side="r"/"l"/"both"`
     and both height modes; service cards; the interactive Who tabs).
  2. **How to call it** — the exact `cm_kit` API snippet (the render helper + the
     `*_css()` you emit once, plus any `*_js()`), with underlying classes as a fallback.
  3. **When to use it / gotchas.**
- **Template preview** — the Landing Page composes Nav + Hero + Services + Text + Pills
  + FAQ + Form + Footer into a full page (`preview-landing.html`), shown inside an
  isolating `<iframe>` so its styles never touch the catalog chrome.

Everything is ported faithfully from the live home page, stays on-brand (brand tokens
only, Poppins 900 + Inter), keeps ARIA roles + focus states, and honors
`prefers-reduced-motion`.

## How it fits together

| File | Role |
|---|---|
| `cm_kit.py` | The shared kit. Each component is a `*_css()` returning a CSS string to embed once + a render helper returning HTML (interactive ones also expose a `*_js()`). Source of truth for tokens + components. |
| `build_catalog.py` | The catalog builder. A single `REGISTRY` list of component descriptors drives both the index cards and the per-component pages. |
| `assets/cm_logo_cream.svg` | Cream logo, inlined into the Nav demo. |
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
       "slug": "badge", "name": "Badge", "eyebrow": "COMPONENT", "color": "yellow",
       "blurb": "Small status chip.",
       "builder": build_badge,
       "api":   [("Emit CSS once, then render",
                  'cm.badge("NEW")\ncm.badge("SALE", bg="var(--pink)")')],
       "notes": ["<b>Keep it short</b> — one or two words."],
   })
   ```

3. **Rebuild:** `python3 build_catalog.py`. A `badge.html` page and a Badge card on the
   index appear automatically.

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
