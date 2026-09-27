# Receipts for YNAB - Website Files

The public website for **Receipts for YNAB**, served by GitHub Pages from `main`:
https://eturea.github.io/Receipts-for-YNAB-site/

## Files

- **index.html** - Home page: hero with the screen recording, how it works, pricing, FAQ
- **privacy.html** - Privacy Policy (canonical)
- **terms.html** - Terms of Service
- **licenses.html** - Third-party software licenses and attributions
- **changelog.html** - What's New / release notes
- **assets/site.css** - Shared stylesheet for all five pages (dark first, light via `data-theme`)
- **assets/site.js** - Theme toggle, FAQ accordion, hero video, license expander
- **assets/** - App icon, favicon, og-image, screenshots, `screenrecording01.mp4` and its two still frames (`rec-still-dark.png`, `rec-still-light.png`)

Plain static HTML: no framework, no build step. `.nojekyll` is present, so every committed file is published as-is.

The pre-redesign site (and the obsolete `.md` versions of the pages) is preserved in tag `site-legacy-2026` and branch `archive/2026-legacy`, never on `main`.

## Keeping Files Up to Date

**Important for AI Agents:** When making changes to the app that affect:
- Privacy practices
- Data handling
- OAuth/YNAB integration
- Apple Intelligence features
- Subscription/pricing
- App capabilities or requirements

**You must update the relevant files in this directory:**
1. Update `privacy.html` for any data handling changes
2. Update `terms.html` for service changes
3. Update `licenses.html` when adding/removing dependencies
4. Update `index.html` for feature additions or changes (the hero's "vX.Y.Z is out" line on feature releases; keep the `FAQPage` JSON-LD in sync with the visible FAQ)
5. Update `changelog.html` when shipping a new release

## Contact

For questions about the website content, contact: eTurea

---

**Last Updated:** 2026-09-27
**Status:** Live on App Store
**App Store:** https://apps.apple.com/us/app/receipts-for-ynab/id6755055273
