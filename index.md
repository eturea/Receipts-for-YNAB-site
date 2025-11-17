# Receipts for YNAB

### Transform Your Paper Receipts into YNAB Transactions with Apple Intelligence

**Receipts for YNAB** is the intelligent receipt scanner for YNAB users. Capture receipts with your iPhone, let Apple Intelligence extract the details, and sync transactions to your budget—all while keeping your data private and secure on your device.

[Download on the App Store](#) | [Privacy Policy](./privacy.md) | [Terms of Service](./terms.md)

---

## Why Receipts for YNAB?

### Powered by Apple Intelligence

Receipts for YNAB harnesses **Apple Intelligence** (iOS 26+) to process receipts entirely on your device. No cloud uploads, no external servers—just fast, accurate, and private receipt scanning.

✨ **AI-Powered Extraction** - Automatically detects merchant names, dates, amounts, and line items
🔒 **100% On-Device** - All processing happens on your iPhone using Apple's Vision and Foundation Models
🎯 **Smart Category Matching** - Suggests YNAB categories based on your budget structure
📊 **Confidence Scoring** - Know how accurate the extracted data is before syncing

---

## Key Features

### 📸 Intelligent Receipt Scanning

Capture receipts using multiple methods:
- **Camera** - Take photos directly in the app
- **Photo Library** - Import existing receipt images
- **Document Scanner** - Use iOS's built-in document scanner for perfect crops

**Quality Validation** ensures your photos are clear enough for accurate scanning:
- Lens smudge detection
- Document clarity assessment
- Automatic photo quality scoring

### 🧠 AI-Powered Data Extraction

Apple Intelligence reads your receipts and extracts:
- **Merchant Name** - Who you paid
- **Transaction Date** - When the purchase occurred
- **Total Amount** - What you spent
- **Line Items** - Individual purchases (synced as YNAB subtransactions)
- **Suggested Categories** - Matched to your YNAB budget

All extraction happens **on-device** using iOS 26's Foundation Models—your receipts never leave your iPhone.

### 📊 Confidence Scoring

Every scanned receipt includes a confidence score based on:
- OCR accuracy (10%)
- Data completeness (40%)
- Category matching (30%)
- Validation checks (10%)
- Photo quality (10%)

Review the breakdown to understand extraction quality before syncing to YNAB.

### 🔄 Seamless YNAB Integration

**OAuth2 Secure Connection:**
- Safe authentication—we never see your YNAB password
- Access tokens stored in iOS Keychain
- Automatic token refresh for seamless sync

**Smart Syncing:**
- Create transactions with line items (subtransactions)
- Assign to specific YNAB accounts
- Auto-match categories from your budget
- Option to save receipts locally without syncing

**YNAB API Features:**
- Fetch budgets, accounts, and categories
- Create new transactions with subtransactions
- Update previously synced receipts (with limitations)
- No access to account balances or existing transactions

### 🗂️ Receipt Management

**Organize Your Receipts:**
- Browse all scanned receipts in one place
- View detailed transaction breakdowns
- See original receipt images
- Track sync status (YNAB or local-only)
- Edit extracted data before or after syncing

**Search and Filter:**
- Find receipts by merchant, date, or amount
- Filter by verification status
- Sort by confidence score

### 🛡️ Privacy-First Design

**Your Data Stays Yours:**
- All receipt processing happens on-device
- No analytics, tracking, or advertising
- No external servers collecting your data
- SwiftData for local storage only

**What We DON'T Collect:**
- Receipt images or extracted data
- YNAB account balances or transactions
- Personal identifiable information
- Location data or usage analytics

Learn more in our [Privacy Policy](./privacy.md).

### 🎙️ Siri and Shortcuts Integration

**Voice-Activated Scanning:**
- "Hey Siri, scan a receipt in Receipts for YNAB"
- Add to Shortcuts app for automation
- Quick Actions from Home Screen
- App Intents for advanced workflows

### ⚙️ Additional Features

**User Experience:**
- Beautiful, native SwiftUI interface
- Dark mode support
- Onboarding guide for new users
- Category selection caching for faster scanning

**Error Handling:**
- Graceful sync failure recovery
- Retry failed transactions
- Save locally if YNAB is unavailable
- Clear error messages and guidance

---

## How It Works

### 1️⃣ Scan Your Receipt
Capture a photo using the camera, photo library, or document scanner. The app validates photo quality before processing.

### 2️⃣ AI Extracts the Details
Apple Intelligence analyzes the receipt on-device, extracting merchant name, date, total, and individual line items.

### 3️⃣ Review and Verify
Check the confidence score and extracted data. Edit any fields as needed. The app suggests YNAB categories automatically.

### 4️⃣ Sync to YNAB
Choose a YNAB account and sync. The transaction appears in your budget with all line items as subtransactions. Or save locally to sync later.

---

## System Requirements

**Device:**
- iPhone or iPad with **Apple Intelligence** support
- **A17 Pro chip or later** (iPhone 15 Pro, iPhone 16, iPad with M-series chip)

**Software:**
- **iOS 26.0 or later**
- Active **YNAB subscription** (required for syncing)

**Permissions:**
- Camera access (for capturing receipts)
- Photo library access (for importing images)

**Note:** The app will not appear in the App Store for incompatible devices (enforced by `UIRequiredDeviceCapabilities: apple-intelligence`).

---

## Pricing

**Receipts for YNAB is completely free.**

No in-app purchases, no subscriptions, no ads. Just a powerful receipt scanner for YNAB users.

*(A YNAB subscription is required separately to sync receipts to your budget.)*

---

## Privacy & Security

### On-Device AI Processing
All receipt scanning and data extraction uses Apple's Vision and Foundation Models frameworks, processing entirely on your device. Your receipt images **never leave your iPhone**.

### Secure Authentication
OAuth2 with PKCE (Proof Key for Code Exchange) ensures secure YNAB authentication. Tokens are stored in iOS Keychain, the same secure storage used for passwords and payment information.

### No Data Collection
We don't operate servers, use analytics tools, or track your behavior. The only external service we communicate with is YNAB's API—and only when you choose to sync.

### Compliance
Receipts for YNAB complies with:
- GDPR (European Union)
- CCPA (California, USA)
- COPPA (USA)
- Apple App Store Review Guidelines

Read our full [Privacy Policy](./privacy.md) for details.

---

## Frequently Asked Questions

### General Questions

**Q: What is Receipts for YNAB?**
A: Receipts for YNAB is an iOS app that uses Apple Intelligence to scan paper receipts and create transactions in your YNAB (You Need A Budget) account. It's built for YNAB users who want to digitize receipts and track purchases with line-item detail.

**Q: Do I need a YNAB account?**
A: Yes. Receipts for YNAB requires an active YNAB subscription to sync receipts. You can scan and store receipts locally without YNAB, but syncing requires authentication.

**Q: Is Receipts for YNAB affiliated with YNAB?**
A: No. Receipts for YNAB is an independent app developed by eTurea. We are not affiliated with, endorsed by, or sponsored by YNAB (Steine LLC).

**Q: How much does it cost?**
A: Receipts for YNAB is **completely free**. No in-app purchases, no subscriptions, no ads.

### Privacy & Data

**Q: Are my receipts uploaded to the cloud?**
A: **No.** All receipt processing happens entirely on your device using Apple Intelligence. We do not operate any servers that collect or store your data.

**Q: Does the app track my usage or show ads?**
A: **No.** We do not use analytics tools, advertising networks, or any form of user tracking. Your privacy is paramount.

**Q: What data is sent to YNAB?**
A: Only transaction details (merchant, date, amount, category, line items) and only when you explicitly choose to sync a receipt. We never send your entire receipt image to YNAB.

**Q: Where is my data stored?**
A: Receipts are stored locally on your device using SwiftData (Apple's data persistence framework). OAuth tokens are stored in iOS Keychain. If you have iCloud Backup enabled, your receipt data may be included in encrypted backups.

**Q: Can I delete my data?**
A: Yes. You can delete individual receipts anytime, disconnect your YNAB account in Settings, or delete the app entirely to remove all local data.

### Features & Functionality

**Q: What information does the app extract from receipts?**
A: The app uses Apple Intelligence to extract:
- Merchant name
- Transaction date
- Total amount
- Individual line items (with quantities and prices)
- Suggested YNAB categories (matched from your budget)

**Q: How accurate is the AI extraction?**
A: Accuracy depends on receipt quality, formatting, and legibility. The app provides a confidence score to help you assess extraction quality. You should always review extracted data before syncing to YNAB.

**Q: Can I edit extracted information?**
A: Yes. You can edit any extracted field before syncing. After syncing, most fields can be updated except transaction dates and subtransactions (YNAB API limitation).

**Q: Does the app support line items?**
A: Yes! Extracted line items are synced to YNAB as subtransactions, giving you detailed purchase breakdowns in your budget.

**Q: Can I save receipts without syncing to YNAB?**
A: Yes. You can save receipts locally-only and sync them later, or keep them as local records indefinitely.

**Q: What happens if a receipt scan fails?**
A: The app validates photo quality before scanning and provides helpful feedback. If extraction fails or is inaccurate, you can manually edit the data or retake the photo.

### YNAB Integration

**Q: Does Receipts for YNAB modify my existing transactions?**
A: No. The app only creates new transactions that you approve or updates transactions previously created by this app.

**Q: Can I choose which YNAB account to use?**
A: Yes. When syncing a receipt, you select which YNAB account (checking, credit card, etc.) to create the transaction in.

**Q: What YNAB data does the app access?**
A: The app accesses:
- Budget names and IDs
- Account names and IDs
- Category groups and categories
- Category availability (to prevent overspending)

The app does **not** access:
- Account balances or net worth
- Existing transactions from other sources
- Banking credentials
- Personal profile information

**Q: What are the YNAB API limitations?**
A: Due to YNAB API restrictions:
- **Transaction dates cannot be changed** after syncing (you must delete and re-scan)
- **Subtransactions cannot be edited** after syncing (delete and re-scan required)
- The app directs you to YNAB's web/mobile app for these edits

**Q: How do I disconnect from YNAB?**
A: Go to Settings → YNAB Connection → Disconnect. This immediately removes your OAuth tokens from iOS Keychain. Your locally saved receipts remain on your device.

### Technical Questions

**Q: What devices are supported?**
A: Receipts for YNAB requires:
- iPhone or iPad with Apple Intelligence support
- A17 Pro chip or later (iPhone 15 Pro, iPhone 16 series, or M-series iPad)
- iOS 26.0 or later

The app will not appear in the App Store for incompatible devices.

**Q: Why does the app require Apple Intelligence?**
A: Apple Intelligence (Foundation Models framework) provides the on-device AI that extracts structured data from receipts. This ensures your receipt images never leave your device.

**Q: Can I use Siri to scan receipts?**
A: Yes! The app supports Siri voice commands and Shortcuts integration. You can say "Hey Siri, scan a receipt in Receipts for YNAB" or create custom automation workflows.

**Q: Does the app work offline?**
A: Receipt scanning works completely offline (on-device AI). Syncing to YNAB requires an internet connection.

### Troubleshooting

**Q: The app says "Apple Intelligence Required"—what does this mean?**
A: Your device doesn't support Apple Intelligence. You need an iPhone 15 Pro or later, or an iPad with an M-series chip running iOS 26+. Check Settings → Apple Intelligence & Siri to verify availability.

**Q: OAuth fails with "invalid_client"—how do I fix this?**
A: This usually means:
- Invalid YNAB client credentials (developer-side issue—contact support)
- Incorrect redirect URI configuration
- Try disconnecting and reconnecting your YNAB account

**Q: Receipt scanning quality is poor—what can I do?**
A: Ensure:
- Good lighting (natural light works best)
- Clean camera lens (app validates this)
- Receipt is flat and fully visible
- High-contrast background (dark receipts on light background or vice versa)
- Check the photo quality validation feedback

**Q: Categories aren't being suggested—why?**
A: Make sure:
- You're connected to YNAB and have selected a budget
- Your budget has active categories
- You have an internet connection (categories are fetched from YNAB)
- Category caching is working (check Settings)

---

## Support

### Need Help?

If you have questions, encounter issues, or want to provide feedback:

**Email:** receiptsforynab.app@gmail.com
**Response Time:** Within 30 days

### Report a Bug

When reporting bugs, please include:
- Device model and iOS version
- App version
- Steps to reproduce the issue
- Screenshots (if applicable)

### Feature Requests

We love hearing from users! If you have ideas for new features or improvements, email us at receiptsforynab.app@gmail.com.

---

## Legal

### Documentation

- [Privacy Policy](./privacy.md) - How we handle your data
- [Terms of Service](./terms.md) - User agreement and legal terms
- [Licenses](./licenses.md) - Third-party software and attributions

### Open Source

Receipts for YNAB is built with:
- **Swift** (Apache 2.0 License)
- **Apple iOS Frameworks** (SwiftUI, SwiftData, Vision, Foundation Models, Combine, Security)

See our [Licenses](./licenses.md) page for complete attributions.

### Compliance

Receipts for YNAB complies with:
- Apple App Store Review Guidelines
- GDPR (General Data Protection Regulation)
- CCPA (California Consumer Privacy Act)
- COPPA (Children's Online Privacy Protection Act)

---

## About eTurea

**Receipts for YNAB** is developed by **eTurea**, an independent software developer passionate about building privacy-first productivity tools.

Our mission is to create apps that:
- Respect user privacy
- Use on-device AI whenever possible
- Integrate seamlessly with existing workflows
- Remain free and accessible

### Contact

**Developer:** eTurea
**Email:** receiptsforynab.app@gmail.com
**App Store:** [Receipts for YNAB](#)

---

## Stay Updated

### Version History

**Version 1.0** (October 2025)
- 🎉 Initial release
- 🧠 Apple Intelligence integration for receipt scanning
- 📸 Camera, photo library, and document scanner support
- 🔄 YNAB OAuth2 authentication and transaction syncing
- 📊 Confidence scoring for extraction quality
- 🗂️ Receipt management with local storage
- 🎙️ Siri and Shortcuts integration
- 🌙 Dark mode support
- 🛡️ Privacy-first design with on-device processing

### Coming Soon

We're constantly improving Receipts for YNAB. Future updates may include:
- Bulk receipt export
- Advanced search and filtering
- Receipt templates for recurring purchases
- Enhanced category learning
- Widget support
- iPad-optimized interface

Follow us for updates and announcements!

---

## Download

**Receipts for YNAB is available now on the App Store.**

[Download on the App Store](#)

**Requirements:** iPhone/iPad with Apple Intelligence (A17 Pro+), iOS 26.0+

---

## Screenshots

*[App screenshots would be displayed here on the actual website]*

### Receipt Scanning
Capture receipts with intelligent photo quality validation.

### AI Extraction
Apple Intelligence extracts merchant, date, amount, and line items—all on-device.

### Confidence Scoring
See detailed accuracy breakdowns before syncing.

### YNAB Integration
Seamlessly create transactions with categories and subtransactions.

### Receipt Management
Browse, search, and manage all your scanned receipts.

---

**© 2025 eTurea. All rights reserved.**

We are not affiliated, associated, or in any way officially connected with YNAB or any of its subsidiaries or affiliates. The official YNAB website can be found at [https://www.ynab.com](https://www.ynab.com).

The names YNAB and You Need A Budget, as well as related names, tradenames, marks, trademarks, emblems, and images are registered trademarks of YNAB.

[Privacy Policy](./privacy.md) | [Terms of Service](./terms.md) | [Licenses](./licenses.md) | [Contact](mailto:receiptsforynab.app@gmail.com)