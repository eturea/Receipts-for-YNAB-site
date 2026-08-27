---
status: done
severity: P2
opened: 2026-08-27
closed: 2026-08-27
title: Update site copy for the v1.1.4 release
area: site
milestone: v1.1.4
effort: evening
risk: low
---

# TICKET — Update site copy for the v1.1.4 release

**Opened:** 2026-08-27
**Priority:** P2 — marketing accuracy. The live site advertised v1.1.3 while v1.1.4 shipped.
**Related:** app repo `CHANGELOG.md` `[1.1.4]`, `docs_vault/Releases/AppStore/v1.1.4_WHATS_NEW.md` (the App Store text, live in ASC). Precedent: `done/TICKET_SITE_RELEASE_V1_1_3.md`.

---

## Problem

The site led with v1.1.3 copy after v1.1.4 (Build 40, "Truthful Results") was released
to the App Store on 2026-08-26, all at once rather than phased. `changelog.html` topped
out at the v1.1.3 entry (July 31, 2026) holding the "Latest" badge, the `index.html`
hero callout read "New in v1.1.3", and the JSON-LD structured data still declared
`softwareVersion: 1.1.3`. Visitors and search engines saw a release behind.

## Proposed fix

Add the v1.1.4 changelog entry, move the "Latest" badge, and refresh the homepage
version references. Content only, no structural or CSS changes. Copy is drawn only
from the two sources of truth above and must not contradict the App Store text. The
headline is deletion: Delete All Data reported success while receipt photographs
stored outside the main database survived, and the promise text was narrowed from
device-level erasure to app scope. Stated plainly, neither softened nor dramatized,
in the same honest-context voice as the v1.1.0 through v1.1.3 entries.

## Acceptance

- [x] `changelog.html` carries a v1.1.4 entry (August 26, 2026) above v1.1.3, reusing the existing `version-entry` / `version-header` / `change-tag` markup.
- [x] "Latest" badge moved from v1.1.3 to v1.1.4; exactly one badge on the page.
- [x] `index.html` hero callout updated to v1.1.4 copy, markup and link behavior unchanged.
- [x] `index.html` JSON-LD `softwareVersion` bumped to `1.1.4`.
- [x] `changelog/CHANGELOG.md` (untracked working copy) carries a matching `[1.1.4]` entry.
- [x] Every remaining `1.1.3` hit in the repo is a deliberate historical reference, not a stale current-version claim.
- [x] No em-dashes in the new copy. Nothing from the release runbook (test tiers, gate counts, beta metrics) on the public site.
- [x] Renders correctly in both light and dark themes.
- [x] Commit references this ticket ID.

## Resolution

Shipped in one commit on `main`, pushed to `origin/main`. Two tracked site files plus this ticket and the regenerated `tickets.json`.

**Changes**

- `changelog.html`: new `v1.1.4` entry (August 26, 2026) inserted above v1.1.3, reusing the existing `version-entry latest` / `version-header` / `change-tag` markup and the three tag classes already in the file (`tag-fixed`, `tag-improved`, `tag-new`). v1.1.3 demoted to a plain `version-entry` with its badge removed. Eleven bullets tracking the App Store text line by line: receipt photographs removed by Delete All Data, deletion wording scoped to the app, honest sign-out, nothing lingering between sessions (plus the backfill stopping on session end), offline cache dropping monetary figures, bank-matched receipts staying in sync, conflicting edits surfacing, accessibility, smaller fixes, new app icon, reliability.
- `index.html`: hero callout text updated to v1.1.4; JSON-LD `softwareVersion` bumped to `1.1.4`. Pricing, FAQ, screenshots, and the feature list untouched.
- `changelog/CHANGELOG.md` (gitignored working copy): matching `[1.1.4]` entry added above `[1.1.0]`. Note that v1.1.1 through v1.1.3 were never added to this file; the gap is left as found.

**Verification**

- Precondition checked before editing: v1.1.3 / July 31, 2026 / `badge-latest` confirmed as the prior top entry.
- Copy drawn only from `v1.1.4_WHATS_NEW.md` and the app `CHANGELOG.md` `[1.1.4]` section; nothing from the release runbook. Added lines grepped for the em-dash character (zero hits) and for test-tier, gate, beta and TestFlight terms (zero hits).
- Headless Chrome renders of both files in light and dark themes. New entry shows the accent border and gradient wash in both; `FIXED`, `IMPROVED` and `NEW` chips legible on both backgrounds.
- Repo grep for `1.1.3`: the only hits outside the ticket files are the comment and `version-number` span of the demoted v1.1.3 entry, both deliberate.
- `regenerate-tickets-json.py --check` passes.

**Not in scope**

`TICKET_SITE_SYNC_CURRENT_VERSION` stays open. Its acceptance items (duplicate site tree in the app repo, obsolete `.md` files, privacy/terms verification, `Website-Update-Requirements-*.md` backlog) are untouched by this work.
