# Receipts for YNAB - Website Files

This directory contains the legal and informational pages for the **Receipts for YNAB** public website, which will be published via GitHub Pages.

## Files

- **index.html** - Main landing page with app overview and features
- **privacy.html** - Privacy Policy (canonical)
- **terms.html** - Terms of Service
- **licenses.html** - Third-party software licenses and attributions
- **changelog.html** - What's New / release notes

> **Note:** The `.md` versions of these files (`index.md`, `privacy.md`, `terms.md`, `licenses.md`) are obsolete. Do not edit them — they are excluded from the Jekyll build via `_config.yml`. The hand-written `.html` files above are what's served at the public URLs.

## Publishing

These files are managed manually by the repository owner. They are kept in this directory to maintain separation from the app's internal documentation.

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
4. Update `index.html` for feature additions or changes
5. Update `changelog.html` when shipping a new release

## Contact

For questions about the website content, contact: eTurea

---

**Last Updated:** 2026-04-21
**App Version:** 1.0.9
**Status:** Live on App Store
**App Store:** https://apps.apple.com/us/app/receipts-for-ynab/id6755055273
