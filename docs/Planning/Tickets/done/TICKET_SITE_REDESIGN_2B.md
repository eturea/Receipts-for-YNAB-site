---
status: done
severity: P2
opened: 2026-09-27
closed: 2026-09-27
title: Site redesign 2b, calm Apple-native design for all five pages
area: site
milestone: v1.1.5
effort: evening
risk: low
---

# Site redesign 2b, calm Apple-native design for all five pages

**Opened:** 2026-09-27
**Source:** owner design handoff `design_handoff_site_redesign` (README, HTML prototypes, reference screenshots), delivered as `docs/Receipts for YNAB website review.zip`. The zip stays local and gitignored; it is not published.

## Problem

The site used a generic SaaS look (gradient text, background blobs, emoji icons, card grids,
scroll animations) sized for a much bigger product than a small app that does one thing.

## Proposed fix

Rebuild `index.html`, `privacy.html`, `terms.html`, `licenses.html` and `changelog.html` as plain
static HTML at the same URLs, on a shared `assets/site.css` and `assets/site.js`, matching the
handoff's tokens, type, spacing and behavior. Legal and changelog text carried over verbatim.

## Acceptance

- [x] Legacy site archived without deleting anything: tag `site-legacy-2026` and branch `archive/2026-legacy` (`_archive/2026-legacy/` holding the five pages and the four obsolete `.md` files). Deviation from the handoff, owner-approved: the handoff assumed Jekyll hides `_archive/`, but `.nojekyll` makes Pages serve every committed file (measured: `_config.yml`, `privacy.md`, `README.md` all HTTP 200), so the archive lives off `main`.
- [x] Five pages rebuilt; shared `assets/site.css` and `assets/site.js`; no framework, no build step.
- [x] Privacy, Terms, Licenses and What's New `<main>` text identical to the legacy pages (tag-stripped text compared); all heading `id`s kept; inline `style` and `onclick` removed.
- [x] Every `<head>` meta, canonical, Open Graph, Twitter, smart-banner, favicon and touch-icon tag kept; Google Analytics kept; Google Fonts removed.
- [x] JSON-LD: `MobileApplication` unchanged; `FAQPage` regenerated from the visible FAQ in the new order (the old block paraphrased 9 of 10 questions and answers, which Google's FAQ guidelines disallow).
- [x] `rec-still-dark.png` and `rec-still-light.png` added to `assets/`.
- [x] Theme key `receipts-ynab-theme` reused; applied before paint by an inline `<head>` script; everything recolours on toggle.
- [x] No console errors; all internal links and anchors resolve; theme persists across pages; no horizontal scroll at 375, 768 and 1280 px in either theme.
- [ ] JSON-LD passes Google's Rich Results Test (owner, after deploy).

## Resolution

Pages generated from the legacy sources in tag `site-legacy-2026` by a one-off script (strip
the old `<style>` and font links, insert the theme script and `site.css`, carry `<main>` over
verbatim, wrap it in the new nav and footer). Verified in headless Chrome over the DevTools
protocol against a local server:

- 30 page loads (5 pages x 3 widths x 2 themes): zero console errors or exceptions, zero overflow.
- Theme: toggle on Home, persists to Privacy, toggled back persists to What's New.
- FAQ: first item open on load; opening the third closes the first; closing leaves none open; sign flips to minus.
- Video: muted; the still hides and the recording plays from 0; on `ended` the still returns.
- License expander: 220 px collapsed, full height expanded, label flips.
- Deep link `licenses.html#trademarks` lands 80 px below the top, clear of the sticky nav.

Also removed from `main`: `index.md`, `privacy.md`, `terms.md`, `licenses.md` (closes that
acceptance line of `TICKET_SITE_SYNC_CURRENT_VERSION`). No longer referenced but left in place:
the `*-light.png` and `*-web.png` screenshot variants and the three `Screenshot 2026-01-16` files.

**Not done, deliberately:** the official Apple "Download on the App Store" badge SVG. The button
ships as designed (text button); swapping in Apple's badge needs the artwork from Apple's
marketing tools.
