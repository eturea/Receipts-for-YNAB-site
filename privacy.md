# Privacy Policy for YNAB Receipts

**Effective Date:** October 15, 2025
**Last Updated:** October 15, 2025

Thank you for using **YNAB Receipts** ("the App"), developed by **eTurea** ("we", "our", or "us"). Your privacy is extremely important to us. This Privacy Policy explains what information we collect, how we use it, how we protect it, and your rights regarding your personal data.

By using YNAB Receipts, you agree to the collection and use of information in accordance with this Privacy Policy.

---

## 1. Overview: Our Privacy Commitment

YNAB Receipts is designed with **privacy-first principles**:

- **All receipt processing happens on your device** using Apple Intelligence
- **We never see your receipt images or extracted data**
- **No analytics, tracking, or advertising**
- **No data is sent to our servers** - we don't have any
- **Your YNAB credentials are stored securely** in your device's Keychain
- **You control all data sync** with YNAB

---

## 2. Information We Collect and Process

### 2.1 Receipt Data (On-Device Only)

When you scan a receipt, the following information is processed and stored **entirely on your device**:

- **Receipt images** (photos you capture or import)
- **Extracted receipt information** including:
  - Merchant name
  - Transaction date
  - Total amount
  - Individual line items and prices
  - Suggested YNAB categories (matched using your budget data)
- **Verification status** (whether you've reviewed the receipt)
- **Confidence scores** (accuracy ratings for extracted data)
- **YNAB sync metadata** (transaction IDs, account IDs, sync timestamps)

**Important:** All receipt scanning and data extraction is performed using **Apple Intelligence** (on-device AI) and the **Vision framework**. Your receipt images never leave your device during the scanning process.

### 2.2 YNAB Account Information

To enable budget synchronization, we access the following from your YNAB account via the official YNAB API:

- **Budget information:**
  - Budget names and IDs
  - Account names and IDs (for selecting where to save transactions)
  - Category group names and category names
  - Category availability (to prevent overspending suggestions)
- **Transaction creation capability:**
  - The app creates new transactions in YNAB when you sync receipts
  - The app may update transactions you previously synced from the app

**What we do NOT access:**
- Existing transactions from other sources
- Account balances or net worth
- Personal identifiable information from your YNAB profile
- Banking credentials or financial institution data
- Payee lists or transaction history (beyond your synced receipts)

### 2.3 Authentication Credentials

- **YNAB OAuth2 access tokens** are stored securely in your device's **iOS Keychain** (the same secure storage used for passwords and payment information)
- **OAuth2 refresh tokens** are also stored in Keychain to maintain your connection
- We use the industry-standard **OAuth2 with PKCE** (Proof Key for Code Exchange) protocol for secure authentication
- Your YNAB password is **never** stored in the app - authentication is handled entirely by YNAB's servers

### 2.4 App Settings and Preferences

The following settings are stored locally on your device:

- Selected YNAB budget (if you have multiple budgets)
- Category selections and preferences (cached for faster receipt scanning)
- Onboarding completion status
- App appearance preferences

### 2.5 Camera and Photo Library Access

The app requests permission to access:

- **Camera** - to capture photos of receipts
- **Photo Library** - to import existing receipt images

These permissions are only used when you initiate a scan. Images are processed immediately on-device and are not uploaded anywhere unless you explicitly choose to sync the extracted transaction data to YNAB.

### 2.6 Siri and Shortcuts Integration

If you choose to use Siri or the Shortcuts app to scan receipts:

- The app provides App Intents that allow you to trigger receipt scanning via Siri voice commands or Shortcuts automations
- No data is sent to Apple's servers beyond the standard Siri processing
- Receipt data remains on your device

---

## 3. How We Use Your Information

We use the information described above **solely** for the following purposes:

### 3.1 Core Functionality
- **Receipt scanning:** Using Apple Intelligence to extract merchant names, dates, amounts, and line items from receipt photos
- **Data verification:** Calculating confidence scores to help you verify extracted information
- **Category matching:** Suggesting appropriate YNAB categories based on your budget structure
- **Transaction creation:** Syncing verified receipts to your YNAB budget as transactions
- **Receipt management:** Organizing and displaying your scanned receipts within the app

### 3.2 User Experience
- **Preference storage:** Remembering your category selections and settings
- **Onboarding:** Showing introductory screens only once
- **Error recovery:** Allowing you to retry failed syncs or save receipts locally

### 3.3 Security
- **Secure authentication:** Maintaining your YNAB connection using OAuth2 tokens
- **Automatic token refresh:** Keeping your connection active without requiring repeated logins

---

## 4. Data Storage and Security

### 4.1 Local Storage Only

**All your receipt data is stored exclusively on your device** using:
- **SwiftData** - Apple's modern data persistence framework
- **iOS Keychain** - For secure storage of authentication tokens

We **do not operate any servers** that collect, store, or process your data.

### 4.2 iCloud and Device Backups

- If you have **iCloud Backup** enabled on your device, your receipt data may be included in your encrypted iCloud backups
- If you restore your device from a backup, your receipt data will be restored
- **Apple's Privacy Policy** governs how backup data is handled
- We have no access to your backups

### 4.3 Security Measures

We implement the following security practices:

- **OAuth2 with PKCE** for secure YNAB authentication
- **iOS Keychain** for credential storage (hardware-encrypted on modern devices)
- **HTTPS only** for all network communication with YNAB's API
- **On-device AI processing** ensures receipt images never leave your device
- **No third-party analytics** or tracking SDKs

### 4.4 YNAB API Security

When you sync receipts to YNAB:
- Data is transmitted directly from your device to YNAB's servers using encrypted HTTPS
- We act as a client of YNAB's API and are subject to YNAB's security measures
- YNAB's Privacy Policy governs how they handle your budget data

---

## 5. Data Sharing and Third-Party Services

### 5.1 YNAB API

The **only** third-party service we communicate with is **YNAB (You Need A Budget)**:

- **Purpose:** To sync receipt transactions to your budget
- **Data shared:** Transaction details extracted from receipts (merchant, date, amount, category, line items)
- **When:** Only when you explicitly choose to save a receipt to YNAB
- **YNAB's Privacy Policy:** https://www.youneedabudget.com/privacy-policy/
- **YNAB's Terms of Service:** https://www.youneedabudget.com/terms/

### 5.2 Apple Services

The app uses the following Apple frameworks and services:

- **Apple Intelligence / Foundation Models:** On-device AI for receipt data extraction (iOS 18+)
- **Vision Framework:** On-device OCR for text recognition
- **Siri / App Intents:** Optional voice commands for scanning (if you choose to set them up)

These are **on-device services** - your data is processed locally and is not sent to Apple's servers (beyond standard iOS system operations).

### 5.3 No Other Third Parties

We **do not** use:
- Analytics services (e.g., Google Analytics, Mixpanel)
- Advertising networks
- Crash reporting services
- Social media integrations
- Payment processors (the app is free)
- AI/ML services from third parties (we use Apple's on-device AI only)

---

## 6. Data Retention

### 6.1 Receipt Data
- Receipts are stored on your device **indefinitely** until you delete them
- You can delete individual receipts at any time from the app
- Deleting the app removes all receipt data from your device

### 6.2 YNAB Connection
- Your OAuth2 tokens remain in Keychain until you disconnect your YNAB account
- Disconnecting from YNAB (Settings → YNAB Connection → Disconnect) immediately deletes all stored tokens
- Tokens are automatically refreshed as needed to maintain your connection

### 6.3 App Settings
- Settings are stored until you delete the app or reset the app data
- Onboarding status and preferences can be reset in Settings

---

## 7. Your Rights and Choices

You have full control over your data:

### 7.1 Access and Export
- All your receipt data is visible within the app
- Receipt images and details can be viewed, edited, or deleted at any time
- Currently, there is no bulk export feature (may be added in future updates)

### 7.2 Correction
- You can edit any extracted receipt information before or after syncing to YNAB
- Note: Due to YNAB API limitations, some fields (date, subtransactions) cannot be edited after syncing

### 7.3 Deletion
- **Delete individual receipts:** Swipe to delete in the Receipts list
- **Delete YNAB connection:** Settings → YNAB Connection → Disconnect
- **Delete all data:** Delete the app from your device

### 7.4 Data Portability
- Receipt data is stored locally on your device
- Data is included in iOS backups (subject to your backup settings)

### 7.5 Withdrawal of Consent
- You can revoke camera or photo library access in iOS Settings → YNAB Receipts
- You can disconnect from YNAB at any time
- You can delete the app entirely

---

## 8. Children's Privacy

YNAB Receipts is not intended for use by children under the age of 13, and we do not knowingly collect personal information from children under 13.

- The app requires a YNAB account, which has its own age restrictions
- If we learn that we have inadvertently collected information from a child under 13, we will take steps to delete such information
- Parents or guardians who believe their child has provided information to us should contact us

---

## 9. International Data Transfers

- **All data processing occurs on your device**, regardless of your location
- The only international data transfer occurs when **you** sync to YNAB, which transmits data to YNAB's servers (located in the United States)
- YNAB's Privacy Policy governs how they handle international data transfers

---

## 10. California Privacy Rights (CCPA)

If you are a California resident, you have additional rights under the California Consumer Privacy Act (CCPA):

- **Right to Know:** You can request what personal information we have collected (in this case, none - all data is on your device)
- **Right to Delete:** You can request deletion of your data (delete the app or individual receipts)
- **Right to Opt-Out of Sale:** We do not sell personal information
- **Right to Non-Discrimination:** We do not discriminate based on exercise of privacy rights

To exercise these rights, contact us at support@ynabreceipts.app.

---

## 11. European Privacy Rights (GDPR)

If you are located in the European Economic Area (EEA), you have rights under the General Data Protection Regulation (GDPR):

- **Legal Basis for Processing:** We process data based on your consent (when you use the app) and for contract performance (providing the service)
- **Right to Access:** You have full access to your data within the app
- **Right to Rectification:** You can edit receipt data at any time
- **Right to Erasure:** You can delete receipts or the entire app
- **Right to Data Portability:** Data is stored locally on your device
- **Right to Object:** You can stop using the app at any time
- **Right to Lodge a Complaint:** You can contact your local data protection authority

---

## 12. Changes to This Privacy Policy

We may update this Privacy Policy from time to time to reflect:

- Changes to our data practices
- New features in the app
- Legal or regulatory requirements

**When we make changes:**
- We will update the "Last Updated" date at the top of this policy
- Significant changes will be communicated via the app (e.g., a notice on app launch)
- Continued use of the app after changes constitutes acceptance of the updated policy

**Reviewing this policy:**
- You can view this policy at any time in Settings → Privacy Policy
- We encourage you to review this policy periodically

---

## 13. Contact Us

If you have any questions, concerns, or requests regarding this Privacy Policy or your data, please contact us:

**Email:** support@ynabreceipts.app
**Developer:** eTurea
**App Name:** YNAB Receipts

We will respond to privacy-related inquiries within 30 days.

---

## 14. Legal Compliance

This Privacy Policy complies with:
- Apple App Store Review Guidelines
- California Consumer Privacy Act (CCPA)
- General Data Protection Regulation (GDPR)
- Children's Online Privacy Protection Act (COPPA)

---

**© 2025 eTurea. All rights reserved.**

This Privacy Policy was last updated on October 15, 2025.