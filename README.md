# INCO — website prototype

Static site for INCO (S.A. de Ingeniería y Construcción Mecánica), published with GitHub Pages.

| URL | Page |
|---|---|
| `/` | English home |
| `/es/` | Spanish home |
| `/legal/` · `/es/legal/` | Legal notice, privacy & cookies |

## Editing

All text, projects, process-line stations and timeline steps live in **`build.py`**. Edit there, then run:

```bash
python3 build.py
```

This regenerates the four HTML pages. Styles are in `assets/css/site.css`, behaviour in `assets/js/site.js`. Fonts are self-hosted in `assets/fonts/` (no Google Fonts requests).

## Preview locally

Double-click `index.html` — no server needed.

## Before launch

- `NOINDEX = True` in `build.py` keeps the prototype out of search engines. Set to `False` at launch.
- Contact form: create a free key at web3forms.com and paste it in `WEB3FORMS_KEY`.
- Fill in the company tax ID and registry details (`COMPANY` in `build.py`) and have the legal text reviewed.
- Replace placeholder images (`IMG` and each project's `img`) with INCO's own photography, ideally stored in `assets/img/`.
- Confirm the certifications listed in `CERTS`.
