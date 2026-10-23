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

Work for this site is filed in `eturea/Receipts-for-YNAB` with Area = Site, on the Work Project
(https://github.com/users/eturea/projects/4); nothing is filed here. `docs/Planning/Tickets/` is
the archive.

Each issue gets its own branch from `main` (`gh ticket start N --worktree`, a neutral slug, never
the title) and lands by one PR into `main` from `gh ticket pr N`, whose body says
`Fixes eturea/Receipts-for-YNAB#N` and what changed in the site. The session merges it with
`gh ticket merge N` after a clean review and green checks. Nobody commits on `main`: the
`pre-commit`, `pre-push` and `reference-transaction` git hooks are the authority, the Claude
`git-policy` hook the early warning.
