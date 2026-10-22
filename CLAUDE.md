# CLAUDE.md

## Project

Marketing and support website for **Receipts for YNAB** (iOS receipt-scanning
app, `~/projects/rfy/app`). Static site served via GitHub Pages
(https://eturea.github.io/Receipts-for-YNAB-site/) — no build step, no
framework, no Xcode tooling. The app repo's `CLAUDE.md` carries the app-side
context; this repo is site content only.

The HTML pages (`index.html`, `privacy.html`, `terms.html`, `licenses.html`,
`changelog.html`) are canonical and share `assets/site.css` and `assets/site.js`
(the "2b" design, 2026-09-27; spec in `TICKET_SITE_REDESIGN_2B`). The pre-redesign
site is preserved in tag `site-legacy-2026` and branch `archive/2026-legacy`.
**`.nojekyll` is present, so GitHub Pages serves every committed file as-is:**
an `_`-prefixed folder or a `_config.yml` `exclude:` hides nothing. Keep
private or draft material out of `main`.

## Work tracking

Since 2026-10-21 the site's work is tracked as **GitHub issues in the app's private repo,
`eturea/Receipts-for-YNAB`, with Area = Site**, on the Work Project
(https://github.com/users/eturea/projects/4). This repo is public, so its issues would be too; file
site work there instead, with its Project fields:
`python3 ~/projects/workbench/tracker/issue.py new --repo eturea/Receipts-for-YNAB --area Site ...`. A commit or PR here closes it with `Fixes eturea/Receipts-for-YNAB#N`.

`docs/Planning/Tickets/` is the archive: `done/` and `wontfix/` keep the closed site tickets, and an
imported ticket's file is a pointer to its issue. `tickets.json` is frozen, and
`tools/regenerate-tickets-json.py` no longer runs.
