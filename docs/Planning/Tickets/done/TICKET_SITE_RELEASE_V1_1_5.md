---
status: done
severity: P2
opened: 2026-09-27
closed: 2026-09-27
title: Update site copy for the v1.1.5 release
area: site
milestone: v1.1.5
effort: evening
risk: low
---

# Update site copy for the v1.1.5 release

**Opened:** 2026-09-27
**Priority:** P2, marketing accuracy. The live site advertised v1.1.4 while v1.1.5 shipped.
**Related:** app repo `CHANGELOG.md` `[1.1.5]`, `docs_vault/Releases/AppStore/v1.1.5_WHATS_NEW.md` (the App Store text, live in ASC). Precedent: `done/TICKET_SITE_RELEASE_V1_1_4.md`.

---

## Problem

v1.1.5 (Build 42, "Deletion Made Honest") was released to the App Store on 2026-09-27,
all at once. The site still led with v1.1.4: `changelog.html` topped out at the v1.1.4
entry holding the "Latest" badge, the `index.html` hero callout read "New in v1.1.4",
and the JSON-LD declared `softwareVersion: 1.1.4`.

## Proposed fix

Add the v1.1.5 changelog entry, move the "Latest" badge, refresh the homepage version
references. Content only, no structural or CSS changes. Copy drawn only from the two
sources of truth above, in the same voice as the earlier entries.

## Acceptance

- [x] `changelog.html` carries a v1.1.5 entry (September 27, 2026) above v1.1.4, reusing the existing markup.
- [x] "Latest" badge moved from v1.1.4 to v1.1.5; exactly one badge on the page.
- [x] `index.html` hero callout updated to v1.1.5 copy, markup and link behavior unchanged.
- [x] `index.html` JSON-LD `softwareVersion` bumped to `1.1.5`.
- [x] `changelog/CHANGELOG.md` (gitignored working copy) carries a matching `[1.1.5]` entry.
- [x] No em-dashes in the new copy. Nothing from the release runbook (test tiers, gate counts, beta metrics) on the public site.
- [x] Renders correctly in both light and dark themes.
- [x] Commit references this ticket ID.

## Resolution

- `changelog.html`: new `v1.1.5` entry (September 27, 2026), twelve bullets tracking the App Store text line by line: Delete All Data finishing cleanly, failed deletion reported truthfully, reinstall asks for sign-in, long receipts on iOS 27, clear model messages on iOS 27, no crash on a retried deletion on iOS 27, unsaved line items refused, cleaner uploads to YNAB, no false budget warning, accessibility, privacy cover, reliability. v1.1.4 demoted to a plain `version-entry`.
- `index.html`: hero callout "New in v1.1.5 - Delete All Data finishes cleanly, and long receipts no longer fail on iOS 27"; JSON-LD `softwareVersion` `1.1.5`.
- `changelog/CHANGELOG.md`: matching `[1.1.5]` entry above `[1.1.4]`.

**Revision (2026-09-27, owner):** three bullets reworded to match the revised Reddit comment, describing only what the user sees. Removed: the overlapping-sections mechanism, the "54-00" example, and the interrupted-save detail. The iOS 27 retry bullet no longer frames it as a crash fix. The App Store What's New still carries the original wording; this page no longer mirrors it line by line on those three items.

**Verification**

- Precondition: v1.1.4 / August 26, 2026 / `badge-latest` confirmed as the prior top entry; hero and JSON-LD confirmed at 1.1.4.
- Added lines grepped for the em-dash character (0) and for TestFlight, beta, gate, tier terms (0). One `badge-latest` on the page.
- Headless Chrome renders of `changelog.html` and `index.html` in light and dark: new entry shows the accent border in both, chips legible.
- `regenerate-tickets-json.py --check` passes.
