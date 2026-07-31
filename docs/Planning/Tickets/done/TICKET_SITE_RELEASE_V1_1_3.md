---
status: done
severity: P2
opened: 2026-07-31
closed: 2026-07-31
title: Update site copy for the v1.1.3 release
area: site
milestone: v1.1.3
effort: evening
risk: low
---

# TICKET — Update site copy for the v1.1.3 release

**Opened:** 2026-07-31
**Priority:** P2 — marketing accuracy. The live site advertised v1.1.2 while v1.1.3 shipped.
**Related:** commit `35819a7` (this repo, `main`).

---

## Problem

The site led with v1.1.2 copy after v1.1.3 shipped on 2026-07-31. `changelog.html`
topped out at the v1.1.2 entry (July 24, 2026) holding the "Latest" badge, the
`index.html` hero callout read "New in v1.1.2", and the JSON-LD structured data
still declared `softwareVersion: 1.1.2`. Visitors and search engines saw a
release behind.

Filed retroactively for traceability: the work was requested and completed in one
sitting, so this ticket opens and closes the same day.

## Proposed fix

Add the v1.1.3 changelog entry, move the "Latest" badge, and refresh the
homepage version references. Content only, no structural or CSS changes.

## Acceptance

- [x] `changelog.html` carries a v1.1.3 entry (July 31, 2026) above v1.1.2.
- [x] "Latest" badge moved from v1.1.2 to v1.1.3; exactly one badge on the page.
- [x] `index.html` hero callout updated to v1.1.3 copy, markup and link behavior unchanged.
- [x] No stale v1.1.2 references remain in `index.html`.
- [x] Renders correctly in both light and dark themes.
- [x] Privacy claims untouched; no iOS 27 promises beyond storage readiness.
- [n/a] Commit references this ticket ID. The shipping commit `35819a7` predates
  this retroactively filed ticket and does not name it; the link is recorded
  here instead, and the ticket-filing commit carries the ID.

## Resolution

Shipped in `35819a7` ("Update site for v1.1.3 release"), fast-forwarded onto
`main` and pushed to `origin/main`. Two files, +20/-4.

**Changes**

- `changelog.html` — new `v1.1.3` entry (July 31, 2026) inserted above v1.1.2,
  reusing the existing `version-entry latest` / `version-header` /
  `change-tag` markup and only the three tag classes already present in the file
  (`tag-fixed`, `tag-improved`). v1.1.2 demoted to a plain `version-entry` with
  its badge removed. Five bullets: accurate connection status, offline viewing
  plus restore after signing back in, iOS 27-ready line item storage migration,
  redirect validation, and dropping the date field from transaction updates.
- `index.html` — hero callout text updated to v1.1.3; JSON-LD `softwareVersion`
  bumped to `1.1.3`. Pricing, FAQ, screenshots, and the feature list untouched.

**Verification**

- Precondition checked before editing: v1.1.2 / July 24, 2026 / `badge-latest`
  confirmed as the prior top entry, so no earlier update had been skipped.
- Headless Chrome renders of both files in light and dark themes. New entry
  shows the accent border and gradient wash in both; `FIXED` and `IMPROVED`
  chips legible on both backgrounds.
- Post-deploy: live pages fetched from
  `https://eturea.github.io/Receipts-for-YNAB-site/` are byte-identical to the
  committed local files (`diff -q` clean), with `v1.1.3` holding the Latest
  badge and `softwareVersion: 1.1.3` served.
- Copy review: session-expiry wording frames sessions ending as normal by-design
  behavior rather than a YNAB fault; privacy claims (on-device processing, no
  data collection, images never leave the device) unchanged; iOS 27 language
  limited to storage format readiness.

**Not in scope**

The separate open ticket `TICKET_SITE_SYNC_CURRENT_VERSION` is unaffected. Its
acceptance items (duplicate site tree in the app repo, obsolete `.md` files,
privacy/terms verification, `Website-Update-Requirements-*.md` backlog) all
remain outstanding.
