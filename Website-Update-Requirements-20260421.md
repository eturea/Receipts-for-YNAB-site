# Website Update Requirements — April 2026

**Created:** April 21, 2026
**Previous Website Update:** March 4, 2026 (reflecting v1.0.6/v1.0.7)
**Current App Version:** v1.0.9 (released April 21, 2026)
**Status:** Ready for implementation

---

## Scope

Implement all items in this document. Delayed items are listed at the end for future reference only — do not implement them.

**Files to modify:**
- `index.html` — main page (Changes 1–7)
- `README.md` — update version number (Change 8)

**No changes needed:**
- `privacy.html` — no data handling changes since March 2026
- `terms.html` — no service changes since March 2026

---

## Terminology Guidelines (unchanged from March)

These rules apply to ALL text changes. Violating these will require rework.

| Term | Use? | Reason |
|------|------|--------|
| **Apple Intelligence** | Yes — lead term | Premium brand association, our key differentiator |
| **Neural Engine** | Yes | Hardware acceleration story, accuracy improvements |
| **On-device AI** | Yes | Privacy angle, no cloud processing |
| **On-device learning** | Yes | For category personalization feature |
| **OCR** | **NEVER** | Generic association with low-quality scanner apps |
| **Machine Learning / ML** | **Avoid** | Dilutes Apple Intelligence association. Use "on-device learning" instead |

---

## Change 1 — New Feature Card: Bank Import Matching (index.html)

**File:** `index.html`
**Location:** Inside `.features-grid`, after the "Seamless YNAB Sync" card (after line ~1520)

**Add new feature card:**
```html
<div class="feature-card scroll-reveal">
    <div class="feature-icon sync">
        <span>&#128179;</span>
    </div>
    <h3>Bank Import Matching</h3>
    <p>Receipts automatically match with your bank imports in YNAB — no more duplicates cluttering your budget. Detailed line items replace vague bank descriptions.</p>
</div>
```

**Why:** This is a major feature currently live in the app but completely absent from the website. It solves a real YNAB pain point (duplicate transactions when entering receipts manually alongside bank imports).

**Note:** The features grid currently has 8 cards. Adding this makes 9 (3 full rows of 3). Adding Change 2 makes 10. Verify the grid layout looks balanced. Consider whether 10 cards warrants a layout adjustment.

---

## Change 2 — New Feature Card: Works Offline (index.html)

**File:** `index.html`
**Location:** Inside `.features-grid`, after the new Bank Import Matching card

**Add new feature card:**
```html
<div class="feature-card scroll-reveal">
    <div class="feature-icon scan">
        <span>&#9992;&#65039;</span>
    </div>
    <h3>Works Offline</h3>
    <p>Scan receipts anywhere — airplane, subway, camping trip. All processing happens on-device. Sync to YNAB when you're back online.</p>
</div>
```

**Why:** The App Store description leads with this feature. Currently buried in the FAQ as a yes/no answer. Deserves its own feature card to match App Store messaging.

**Note:** With this card, the grid has 10 cards. This creates 3 rows of 3 + 1 orphan card. Options:
- Accept the asymmetry (the orphan card centers on mobile, looks fine)
- Remove or merge a less impactful card to get back to 9 (3x3)
- Verify layout at desktop, tablet, and mobile breakpoints

---

## Change 3 — Update Receipt Vault Card (index.html)

**File:** `index.html`
**Lines:** ~1554-1560

**Current:**
```html
<div class="feature-card scroll-reveal">
    <div class="feature-icon privacy">
        <span>&#128451;</span>
    </div>
    <h3>Receipt Vault</h3>
    <p>Store receipts locally for warranties, returns, and expense tracking — even without a YNAB account. Your personal receipt archive, always on your device.</p>
</div>
```

**Change to:**
```html
<div class="feature-card scroll-reveal">
    <div class="feature-icon privacy">
        <span>&#128451;</span>
    </div>
    <h3>Receipt Vault</h3>
    <p>Browse receipts by merchant, date, or amount. Search your purchase history for warranties, returns, and expenses — even without a YNAB account. Always on your device.</p>
</div>
```

**Why:** The current card undersells the vault. The app now has full search and browse capabilities that aren't mentioned.

---

## Change 4 — Update Seamless YNAB Sync Card (index.html)

**File:** `index.html`
**Lines:** ~1514-1520

**Current:**
```html
<div class="feature-card scroll-reveal">
    <div class="feature-icon sync">
        <span>&#128260;</span>
    </div>
    <h3>Seamless YNAB Sync</h3>
    <p>Save receipts locally and upload to YNAB when you're ready. Line items become subtransactions with categories from your budget.</p>
</div>
```

**Change to:**
```html
<div class="feature-card scroll-reveal">
    <div class="feature-icon sync">
        <span>&#128260;</span>
    </div>
    <h3>Seamless YNAB Sync</h3>
    <p>Save receipts locally and upload to YNAB when you're ready. Line items become subtransactions with categories from your budget. Matches with bank imports automatically.</p>
</div>
```

**Why:** Reinforces the bank import matching feature within the existing sync card. This complements the dedicated Bank Import Matching card (Change 1) — users may read one or the other.

---

## Change 5 — Update Keywords Meta (index.html)

**File:** `index.html`
**Line:** ~19

**Current:**
```html
<meta name="keywords" content="YNAB, receipt scanner, Apple Intelligence, iOS app, budgeting, expense tracking, receipt to YNAB, on-device AI, iPad receipt scanner, multi-budget YNAB, receipt vault, receipt storage, grocery receipt scanner, line item splitting, YNAB categories, Neural Engine">
```

**Change to:**
```html
<meta name="keywords" content="YNAB, receipt scanner, Apple Intelligence, iOS app, budgeting, expense tracking, receipt to YNAB, on-device AI, iPad receipt scanner, multi-budget YNAB, receipt vault, receipt storage, grocery receipt scanner, line item splitting, YNAB categories, Neural Engine, bank import matching, offline receipt scanner, receipt search">
```

**Why:** Add keywords for the new features: bank import matching, offline scanning, receipt search, and multilingual support.

---

## Change 6 — Update MobileApplication Schema: softwareVersion (index.html)

**File:** `index.html`
**Lines:** ~1936-1953

**Current:**
```json
{
    "@context": "https://schema.org",
    "@type": "MobileApplication",
    "name": "Receipts for YNAB",
    "operatingSystem": "iOS 26+, iPadOS 26+",
    "applicationCategory": "FinanceApplication",
    "description": "Transform paper receipts into YNAB transactions with Apple Intelligence. 100% on-device AI processing for privacy.",
    "offers": {
        "@type": "Offer",
        "price": "0",
        "priceCurrency": "USD"
    },
    "author": {
        "@type": "Organization",
        "name": "eTurea"
    }
}
```

**Change to:**
```json
{
    "@context": "https://schema.org",
    "@type": "MobileApplication",
    "name": "Receipts for YNAB",
    "operatingSystem": "iOS 26+, iPadOS 26+",
    "applicationCategory": "FinanceApplication",
    "softwareVersion": "1.0.9",
    "description": "Transform paper receipts into YNAB transactions with Apple Intelligence. 100% on-device AI processing for privacy. Auto-matches with bank imports.",
    "offers": {
        "@type": "Offer",
        "price": "0",
        "priceCurrency": "USD"
    },
    "author": {
        "@type": "Organization",
        "name": "eTurea"
    }
}
```

**Two changes:** Added `softwareVersion` field, updated `description` to mention bank import matching.

---

## Change 7 — Add FAQ: Bank Import Matching (index.html)

**File:** `index.html`
**Location:** Inside FAQ `.features-grid`, after "What data goes to YNAB?" card (after line ~1841)

**Add new FAQ card:**
```html
<div class="feature-card scroll-reveal">
    <h3>Will receipts create duplicate transactions?</h3>
    <p>No. When you sync a receipt, it automatically matches with existing bank imports in YNAB. Your receipt's detailed line items replace the vague bank description — no duplicates.</p>
</div>
```

**Also add to FAQ schema** (inside `mainEntity` array, after the "What data is sent to YNAB?" question):
```json
,
{
    "@type": "Question",
    "name": "Will syncing receipts create duplicate transactions in YNAB?",
    "acceptedAnswer": {
        "@type": "Answer",
        "text": "No. When you sync a receipt to YNAB, it automatically matches with existing bank imports. Your receipt's detailed line items and categories replace the vague bank description, so you never get duplicate transactions."
    }
}
```

**Why:** Duplicate transactions is a top concern for YNAB users who use bank imports. This FAQ directly addresses it and is good for SEO (rich snippet).

---

## Change 8 — Update README Version (README.md)

**File:** `README.md`
**Lines:** ~38-39

**Current:**
```
**Last Updated:** 2026-01-15
**App Version:** 1.0.1 (Build 13)
```

**Change to:**
```
**Last Updated:** 2026-04-21
**App Version:** 1.0.9
```

---

## Verification Checklist

After all changes, verify:

- [ ] Feature cards grid layout is balanced (now 10 cards — check at desktop, tablet, mobile; or 9 if one card merged/removed)
- [ ] New feature cards use correct icon classes (`sync`, `scan`, `privacy`)
- [ ] All new text follows Terminology Guidelines (no OCR, no ML)
- [ ] FAQ card reads naturally alongside existing FAQs
- [ ] Structured data is valid JSON (use Google Rich Results Test)
- [ ] Keywords meta doesn't exceed reasonable length
- [ ] No broken links
- [ ] Light mode and dark mode both render correctly
- [ ] Mobile responsive — check at 375px, 768px widths
- [ ] Scroll-reveal animations work on new cards

---

## Delayed Items (Do Not Implement)

| Item | Status | Reason |
|------|--------|--------|
| Screenshots refresh | Delayed | UI has changed (toolbar, categories, accounts) — needs new captures from v1.0.9. Will capture separately. |
| Real user testimonials | Delayed | Still blocked on user permission (OptimusPrimatePrime, Steven). Currently showing Reddit pain-point quotes. |
| Stats banner (releases, crash-free) | Delayed | Will implement alongside testimonials |
| AI Model Status Indicator mention | Not planned | Too implementation-specific for marketing page |
| UI polish details (amount fields, currency symbols) | Not planned | Too granular for website |

### Quotes Still Pending Permission (from March doc)

| User | Quote | Source | Permission Status |
|------|-------|--------|-------------------|
| OptimusPrimatePrime | "Entering receipts has actually become fun lol" | Reddit DM, Feb 7, 2026 | Not yet asked |
| OptimusPrimatePrime | "Receipts for YNAB has become an important part of my YNAB workflow" | Reddit DM, Feb 7, 2026 | Not yet asked |
| OptimusPrimatePrime | "Can definitely see use case for storing receipts for warranties, basically like in a database" | Reddit DM, Feb 7, 2026 | Not yet asked |
| OptimusPrimatePrime | "The category grouping update is a big improvement" | Reddit DM, Feb 7, 2026 | Not yet asked |
| Steven | "I managed to upload my first receipt! AI scanning worked well" | Email, Mar 4, 2026 | Not yet asked |
