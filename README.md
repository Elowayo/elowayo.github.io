# elowa.github.io

Public site for **Elowa** — the introduction page plus the legal documents
(Privacy Policy, Terms of Service). Static HTML, served by GitHub Pages.

```
index.html                 home / introduction
privacy.html               generated from content/privacy-policy.md
terms.html                 generated from content/terms-of-service.md
content/                   markdown sources, pulled from the Elowa app repo
tools/build.py             markdown -> HTML page generator (no dependencies)
tools/md2html.py           the tiny markdown converter it uses
assets/css/style.css       Blush & Mulberry palette from the app's docs/BRAND.md
assets/img/logo.svg        the "Profile & Glow" mark
```

## Updating the legal pages

The markdown in `content/` is the source of truth for this site. When the
documents change in the app repo, copy them over and rebuild:

```bash
cp "../Elowa/Privacy Policy.md" content/privacy-policy.md && cp "../Elowa/Terms of Service.md" content/terms-of-service.md && python3 tools/build.py
```

`tools/build.py` regenerates all three pages. It deliberately strips two kinds
of internal drafting commentary from the published output — the "starting
draft / not reviewed by a licensed attorney" footnote, and the aside in Terms
§13 about which BC arbitration language a lawyer still needs to confirm.
Neither belongs on a live legal page. They stay in the markdown.

## Preview locally

```bash
python3 -m http.server 4173
```
