---
status: done
severity: P3
opened: 2026-09-27
closed: 2026-09-27
title: Replace the old app icon in site assets with the v1.1.4 icon
area: site
milestone: v1.1.5
effort: evening
risk: low
---

# Replace the old app icon in site assets with the v1.1.4 icon

**Opened:** 2026-09-27
**Related:** app repo `Receipts for YNAB/AppIcon.icon` (Icon Composer source, shipping since v1.1.4).

## Problem

The app has shipped a new icon since v1.1.4 (2026-08-26), but the site still used the old
dark-teal icon in the favicon, the apple-touch-icon, and the og-image social preview card.

## Acceptance

- [x] `assets/favicon.png` (32x32) rendered from the new icon.
- [x] `assets/apple-touch-icon.png` (180x180, opaque; iOS applies its own mask) rendered from the new icon.
- [x] `assets/og-image.png` (1200x630) shows the new icon in place of the old one; layout and text unchanged.
- [x] No HTML changes needed (file names unchanged).

## Resolution

Renders exported from the Icon Composer document with Xcode 27's `ictool`
(`--platform iOS --rendition Default --width 1024 --height 1024 --scale 1`), then resized.
The og-image keeps the original background and text: the old icon and its glow were
painted out with a feathered background patch and the new icon placed at the same
position and size (220 px) with a soft teal glow. All three checked visually before commit.
Social platforms cache preview cards, so shared links may show the old card until their
caches refresh.
