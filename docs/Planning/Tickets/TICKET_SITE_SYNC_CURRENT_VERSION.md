---
status: open
severity: P2
opened: 2026-07-02
title: Verify RFY site currency and resolve the duplicate site directory
area: site
effort: evening
risk: low
---

# TICKET — Verify RFY site currency and resolve the duplicate site directory

**Priority:** P2 — marketing accuracy + a real drift risk (two site copies).
**Area:** site — tracked here in the site repo (its natural home, `~/my_works/Receipts-for-YNAB-site`).
**Live app:** v1.1.0 (`Receipts for YNAB.xcodeproj/project.pbxproj` `MARKETING_VERSION = 1.1.0`; app repo `CHANGELOG.md` `[1.1.0] - 2026-05-26`).
**Migrated:** 2026-07-08 from the RFY app repo (`docs/Planning/Tickets/TICKET_SITE_SYNC_CURRENT_VERSION.md`, opened 2026-07-02) as part of the PLAN-TIME Phase 0 rule reversal — site tickets now live in the site repos. Original closed with a pointer (`TICKET_SITE_SYNC_CURRENT_VERSION_MIGRATED.md` in the app repo's `wontfix/`). Full original history preserved below.
**Update 2026-07-08:** this repo is now a proper git repo reconnected to `github.com/eturea/Receipts-for-YNAB-site` (PLAN-TIME Phase 0.1); working material (reddit_users, app store assets, screen recording, old requirements docs) is intentionally untracked via `.gitignore`.

---

## Problem

The canonical site is **already current** for the live app — but there are **two copies** of it, one tracked inside the app repo, and they have drifted. That duplication is the real issue; the version sync is largely a verification pass.

## Audit findings (cited)

1. **Site content is current for v1.1.0 (trust-the-code note).** `~/my_works/Receipts-for-YNAB-site/index.html` leads with **"New in v1.1.0 — Private Receipt Links"** (line ~1390), `changelog.html`'s newest entry is **v1.1.0**, and the App Store link is `https://apps.apple.com/us/app/receipts-for-ynab/id6755055273`. So this is NOT a stale-version problem — the site already reflects the shipped v1.1.0 HF-H receipt-links feature.
2. **PRIMARY ISSUE — duplicate site tree tracked inside the app repo.** `Receipts for YNAB/Receipts-for-YNAB-site/` is a full second copy, **46 files tracked in git**, and it has **drifted** from canonical: in-repo `index.html` is 91,294 bytes (dated 2026-05-26) vs the canonical `~/my_works/Receipts-for-YNAB-site/index.html` at 91,760 bytes (updated 2026-05-27). Two sources of truth for one website → future edits will diverge.
3. **Light content verification.** `privacy.html` reads Effective Oct 15 2025 / Updated May 2026; `terms.html` Effective Oct 15 2025 / Updated March 2026 — confirm both cover the v1.1.0 receipt-link memo codes (on-device, no upload). The `Website-Update-Requirements-*.md` docs run through Apr 2026 (v1.0.9); confirm no post-v1.0.9 copy items remain unimplemented.

## Proposed action (owner decides — do NOT execute here)

- Make `~/my_works/Receipts-for-YNAB-site` the single source of truth. Either (a) remove the tracked `Receipts for YNAB/Receipts-for-YNAB-site/` copy from the app repo, or (b) replace it with a one-line pointer README to the canonical repo. Recommend (a).

## Obsolete legal `.md` files (folded in from the 2026-07-02 doc sweep)

`docs_vault/Technical-Debt.md` (Medium, May 13 2026) flags that Phase 1 Build 33 made `privacy.html` canonical and excluded the `.md` versions from Jekyll via `_config.yml`, but the obsolete `.md` files (`privacy.md`, `terms.md`, `licenses.md`, `index.md`) still sit in the site tree and risk future drift (agents may re-edit them despite the README pointer). Delete or sync them as part of this site pass.

## Acceptance

- [ ] Duplicate resolved: one canonical site, no drifted in-repo copy (owner picks remove vs. pointer).
- [ ] privacy.html / terms.html confirmed to cover v1.1.0; dates bumped only if copy changed.
- [ ] No outstanding items from the `Website-Update-Requirements-*.md` backlog.
- [ ] Obsolete `privacy.md` / `terms.md` / `licenses.md` / `index.md` deleted from this repo (or synced).
- [ ] Commit references this ticket ID.
