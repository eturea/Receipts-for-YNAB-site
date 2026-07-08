# CLAUDE.md

## Project

Marketing and support website for **Receipts for YNAB** (iOS receipt-scanning
app, `~/my_works/Receipts for YNAB`). Static site served via GitHub Pages
(https://eturea.github.io/Receipts-for-YNAB-site/) — no build step, no
framework, no Xcode tooling. The app repo's `CLAUDE.md` carries the app-side
context; this repo is site content only.

The HTML pages (`index.html`, `privacy.html`, `terms.html`, `licenses.html`,
`changelog.html`) are canonical; the sibling `.md` files are obsolete Jekyll
sources kept only until the site-sync ticket removes them — edit the HTML.

## Ticket System

The single source of truth for outstanding **site** work is
`docs/Planning/Tickets/`. Three folders by status: top-level (`open` /
`in-progress` / `deferred`), `done/`, `wontfix/`. **Folder must match
frontmatter `status:`** — enforced. Site tickets live HERE, in this repo — not
in the app repo (rule reversed 2026-07-08; app-repo tickets that predate that
carry a pointer).

```bash
./tools/regenerate-tickets-json.py --new <SLUG>   # scaffold a new ticket
./tools/regenerate-tickets-json.py                # validate + write tickets.json + refresh dashboard
./tools/regenerate-tickets-json.py --check        # CI mode: exit 1 if json would change
```

The regen script also refreshes the **combined two-app dashboard** at
`~/my_works/tickets-dashboard/index.html` (via `tickets-dashboard/merge-tickets.py`),
which maps this repo's tickets onto the parent app (`rfy`) with `area: site`
default — so tickets here may omit `area:`. **Never edit `tickets.json` by
hand** — edit the source `TICKET_*.md` and re-run.

**Frontmatter schema + validator behavior**: `docs/Planning/Tickets/README.md`
— canonical and byte-identical across all four repos (Beheld, Receipts for
YNAB, and both site repos). Edit all four copies together.
