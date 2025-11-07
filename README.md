# Receipts for YNAB

An iOS 26+ app that uses Apple Intelligence (Vision + Foundation Models) to scan paper receipts and automatically create transactions in your [You Need A Budget (YNAB)](https://www.ynab.com) account using OAuth2.

![iOS](https://img.shields.io/badge/iOS-26.0%2B-blue)
![Swift](https://img.shields.io/badge/Swift-6.0-orange)
![License](https://img.shields.io/badge/license-MIT-green)
![Version](https://img.shields.io/badge/version-1.0-blue)
![Status](https://img.shields.io/badge/status-beta-yellow)

---

## Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Architecture](#architecture)
- [How It Works](#how-it-works)
- [Setup](#setup)
- [Usage](#usage)
- [Subscription Tiers](#subscription-tiers)
- [Testing](#testing)
- [API Reference](#api-reference)
- [Known Limitations](#known-limitations)
- [Performance](#performance)
- [Documentation](#documentation)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [Roadmap](#roadmap)
- [License](#license)

---

## Features

### 🎯 Core Functionality

- **AI-Powered Receipt Scanning**: Uses Apple's Vision framework (iOS 26) and Foundation Models to extract receipt details automatically
  - Intelligent OCR with `RecognizeDocumentsRequest` for document/table detection
  - Structured data extraction using `@Generable` protocol
  - On-device processing with SystemLanguageModel
- **Photo Quality Validation**: Validates photo quality before scanning using Vision's lens smudge detection and aesthetic scoring
- **YNAB Integration**: Seamlessly creates transactions in your YNAB budget with OAuth2 PKCE authentication
- **Multi-Item Line Items**: Automatically breaks down receipts into individual items as YNAB subtransactions
- **Dual Save Modes**: Save receipts locally-only OR sync to YNAB with intelligent sync tracking
- **Confidence Scoring**: Weighted confidence scores (OCR quality, data completeness, category matching)

### 📱 User Experience

- **Modern Scan Interface**: Card-based UI with 4 scan methods (Scan Document, Take Photo, Choose from Photos, Choose File)
- **Adaptive Scanning Feedback**: Duration-based progress display with Apple Intelligence branding
  - Quick scans (<3s): Minimal UI for snappy feel
  - Medium scans (3-7s): Progress bar with phase indicators
  - Long scans (7s+): Educational messages explaining AI processing
- **Rotating Tips System**: 15 contextual tips across scanning, receipt types, features, and troubleshooting
- **AI-Generated Greetings**: Time-aware welcome messages with typewriter animation
- **Scan Usage Indicator**: Progressive visual feedback for Free tier scan limits
- **Receipt Management**: View, edit, and delete scanned receipts with full SwiftData persistence
- **Transaction Verification**: Review and edit extracted data before sending to YNAB
- **Account Selection**: Choose which YNAB account to post transactions to
- **Network Resilience**: Offline/online detection with graceful degradation
- **Subscription System**: Free, Manual, and AI tiers with StoreKit 2 integration
- **Enhanced Accessibility**: VoiceOver announcements, Reduce Motion support, and haptic feedback

### 🔒 Security & Privacy

- **Secure OAuth2 Flow**: PKCE-enabled authorization code flow
- **Keychain Storage**: Access tokens securely stored in iOS Keychain
- **Privacy-First**: All AI processing happens on-device using Apple Intelligence
- **No Cloud Dependencies**: Receipt images stored locally only

---

## Requirements

### Device Requirements

- **iOS 26.0+** (required)
- **Apple Intelligence capable device** (recommended for AI features):
  - iPhone 15 Pro / Pro Max
  - iPhone 16 / Plus / Pro / Pro Max
  - Future A17 Pro+ devices
- **Apple Intelligence enabled** in Settings → Apple Intelligence & Siri

> **Note**: The app runs on any iOS 26+ device, but AI scanning features require Apple Intelligence. Manual entry is available on all devices.

### Development Requirements

- **Xcode 16.0+**
- **Swift 6.0+**
- **macOS 15.0+** (for Xcode 16)
- **YNAB account** with API access

---

## Architecture

### Tech Stack

| Layer | Technology |
|-------|-----------|
| **UI Framework** | SwiftUI (iOS 26) |
| **Persistence** | SwiftData with migration support (V1→V2→V3) |
| **OCR** | Vision Framework (`RecognizeDocumentsRequest`, `DetectLensSmudgeRequest`) |
| **AI Extraction** | FoundationModels (`SystemLanguageModel`, `@Generable` protocol) |
| **State Management** | Combine + `@Observable` macro |
| **Networking** | URLSession with async/await |
| **Authentication** | OAuth2 PKCE with Keychain storage |
| **Monetization** | StoreKit 2 subscriptions |
| **Concurrency** | Swift 6.0 concurrency (`@MainActor`, structured tasks) |

### MVVM Architecture

The app follows Model-View-ViewModel pattern with specialized ViewModels:

```
User → View → ViewModel → Service → External APIs
  ↑                          ↓
  └──────── Updates ──────────┘
```

**Key ViewModels:**
- `ReceiptScanViewModel`: Orchestrates scanning workflow (idle → validating → scanning → success)
- `PhotoQualityViewModel`: Validates image quality using Vision
- `OCRProcessorViewModel`: Extracts text using Vision framework
- `AIExtractionViewModel`: Processes OCR text with Apple Intelligence
- `ReceiptVerificationViewModel`: Manages edit/save flow with AlertState pattern

### Project Structure

```
Receipts for YNAB/                      # 108 Swift files
├── Models/                        # Data models
│   ├── Receipt.swift              # SwiftData receipt model
│   ├── YNABModels.swift           # YNAB API response models
│   ├── AIReceipt.swift            # @Generable model for AI extraction
│   ├── AIGreeting.swift           # @Generable greeting model
│   ├── ReceiptConfidenceScore.swift
│   ├── CategorySelection.swift
│   ├── StoreKit/
│   │   └── SubscriptionProduct.swift
│   └── Migration/                 # SwiftData schema versions
│       ├── ReceiptSchemaV1.swift
│       ├── ReceiptSchemaV2.swift
│       ├── ReceiptSchemaV3.swift
│       └── ReceiptMigrationPlan.swift
│
├── Views/                         # SwiftUI views (45+ files)
│   ├── AuthenticationView.swift   # OAuth2 sign-in screen
│   ├── RootView.swift             # App root with onboarding
│   ├── MainTabView.swift          # Tab container (Receipts/Scan/Settings)
│   ├── ScanReceiptView.swift      # Camera/photo picker + AI scanning
│   ├── ReceiptVerificationView.swift  # Edit before save
│   ├── ReceiptsListView.swift     # List of scanned receipts
│   ├── ReceiptDetailView.swift    # Individual receipt details
│   ├── SettingsView.swift         # App settings & preferences
│   ├── Onboarding/                # Onboarding flow (4 pages + paywall)
│   │   ├── OnboardingView.swift
│   │   ├── OnboardingPage1View.swift
│   │   ├── OnboardingPage2View.swift
│   │   ├── OnboardingPage3View.swift
│   │   └── OnboardingPaywallPage.swift
│   ├── Paywall/
│   │   ├── SubscriptionPaywallView.swift
│   │   └── StoreKitComponents.swift
│   ├── Debug/
│   │   └── StoreKitDebugMenu.swift
│   ├── Receipts/Components/       # Receipt form sections
│   │   ├── ReceiptFormStyle.swift
│   │   ├── ReceiptMerchantSection.swift
│   │   └── ReceiptSectionMessage.swift
│   └── Components/                # Reusable UI components
│       ├── ScanActionsGridView.swift    # 2×2 scan method grid
│       ├── ScanTileButton.swift         # Card tile button
│       ├── TipView.swift                # Rotating tips
│       ├── GreetingView.swift           # AI greeting with typewriter
│       ├── ScanUsageIndicator.swift     # Free tier progress
│       ├── SubscriptionStatusBanner.swift
│       ├── OfflineNotificationBanner.swift
│       ├── ConfidenceFactorRow.swift
│       ├── LoadingOverlay.swift
│       └── NotificationBanner.swift
│
├── ViewModels/                    # MVVM ViewModels (14 total)
│   ├── ReceiptScanViewModel.swift
│   ├── PhotoQualityViewModel.swift
│   ├── OCRProcessorViewModel.swift
│   ├── AIExtractionViewModel.swift
│   ├── ReceiptsListViewModel.swift
│   ├── SettingsViewModel.swift
│   ├── SubscriptionPaywallViewModel.swift
│   └── Receipts/
│       ├── ReceiptVerificationViewModel.swift
│       ├── ReceiptVerificationAlertState.swift  # AlertState enum pattern
│       └── EditableLineItem.swift
│
├── Services/                      # Business logic (20+ services)
│   ├── AppServices.swift          # DI container
│   ├── YNABOAuthService.swift     # OAuth2 PKCE flow
│   ├── YNABService.swift          # YNAB API client
│   ├── PhotoQualityValidator.swift # Vision quality checks
│   ├── OCRProcessor.swift         # Vision OCR
│   ├── AIExtractor.swift          # Apple Intelligence extraction
│   ├── ConfidenceScoreCalculator.swift
│   ├── CategorySelectionService.swift
│   ├── SubscriptionManager.swift  # StoreKit 2 management
│   ├── SubscriptionUsageStore.swift # Usage tracking
│   ├── SubscriptionProductCache.swift
│   ├── NetworkMonitor.swift       # Connectivity monitoring
│   ├── OnboardingState.swift
│   ├── ReceiptManager.swift
│   ├── ReceiptCleanupService.swift
│   ├── ReceiptPreferencesService.swift
│   ├── StorageService.swift       # SwiftData operations
│   └── Config.swift               # Credentials loader
│
├── AppIntents/                    # Siri/Shortcuts/Quick Actions
│   └── ScanReceiptIntents.swift   # 4 quick actions (iOS 26)
│
├── Tools/                         # AI Tools
│   └── CategoryTool.swift         # YNAB category retrieval tool
│
├── Utilities/                     # Helpers & extensions
│   ├── Constants.swift            # Design tokens & constants
│   ├── GreetingsProvider.swift    # AI greeting generation
│   ├── HapticFeedback.swift
│   ├── Logger+Extensions.swift
│   └── PerformanceTimer.swift
│
├── Resources/
│   ├── Localization/
│   │   └── Localizable.xcstrings  # String Catalog (1,657+ keys)
│   └── Documentation/             # 45+ implementation docs
│
└── Receipts for YNABApp.swift          # App entry point

Receipts for YNABTests/                 # 45 test files (~75% coverage)
├── OAuth/                         # Auth tests
├── Services/                      # Service layer tests (15+ files)
├── ViewModels/                    # ViewModel tests (14 files)
├── Views/                         # View tests
├── Models/                        # Data model tests
├── Integration/                   # Integration tests (4 files)
├── Mocks/                         # Test doubles (10+ mocks)
└── Fixtures/                      # Test data
```

### Key Design Patterns

1. **MVVM**: Clear separation between Views, ViewModels, and Models
2. **Dependency Injection**: Centralized `AppServices` for service management
3. **AlertState Enum**: Single source of truth for complex alert states (prevents stale state bugs)
4. **Tool-Augmented Generation**: AI uses `RetrieveYNABCategoriesTool` to fetch categories dynamically
5. **SwiftData External Storage**: Images stored as files, lazy-loaded on access (99.7% memory reduction)
6. **Dual-Image Strategy**: Thumbnails for display, full images for zoom (97.5% memory reduction)
7. **@State Image Caching**: Views decode once, cache across refreshes (prevents constant re-decoding)
8. **Dual Save Paths**: Local-only OR YNAB sync with per-receipt tracking
9. **OAuth2 PKCE**: Secure authorization code flow with automatic token refresh
10. **Home Screen Quick Actions**: 4 App Intents + NotificationCenter routing
11. **Per-Receipt Line Items Tracking**: `syncedWithLineItems` field tracks original upload mode
12. **Network Resilience**: `NetworkMonitor` combines connectivity + reachability checks

---

## How It Works

### Receipt Scanning Flow

```
1. Photo Capture
   ├── Take Photo (camera)
   ├── Scan Document (document scanner)
   ├── Choose from Photos (photo library)
   └── Choose File (file picker)
          ↓
2. Quality Validation (PhotoQualityValidator)
   ├── DetectLensSmudgeRequest (blur/smudge detection)
   └── CalculateImageAestheticsScoresRequest (document classification)
          ↓
3. Document Recognition (OCRProcessor)
   └── RecognizeDocumentsRequest (iOS 26 OCR with table detection)
          ↓
4. AI Extraction (AIExtractor)
   ├── SystemLanguageModel.default
   ├── @Generable protocol (AIReceipt)
   └── RetrieveYNABCategoriesTool (category matching)
          ↓
5. Confidence Scoring (ConfidenceScoreCalculator)
   ├── OCR confidence (10%)
   ├── Data completeness (40%)
   ├── Category matching (30%)
   ├── Validation checks (10%)
   └── Photo quality (10%)
          ↓
6. User Verification (ReceiptVerificationView)
   ├── Review/edit extracted data
   ├── Select YNAB account
   └── Choose: Save to YNAB or Save Locally
          ↓
7. YNAB Sync (YNABService)
   └── Create transaction with subtransactions
```

**Processing Time**: 2-5 seconds on iPhone 16 Pro

### YNAB Integration

- **OAuth2 Authorization Code Flow** with PKCE
- **Automatic Token Refresh** to maintain authentication
- **Budget & Account Management** for multi-budget users
- **Split Transactions** using YNAB's subtransactions feature
- **Import ID Tracking** for duplicate detection
- **3-Way Merge**: Syncs line items respecting original upload mode

### Data Models

#### Receipt (SwiftData V3)

```swift
@Model
final class Receipt {
    var id: UUID

    // Images stored externally for memory efficiency
    @Attribute(.externalStorage) var imageData: Data        // Full 2048×2048
    @Attribute(.externalStorage) var thumbnailData: Data    // 400×400 thumbnail

    var merchantName: String
    var date: Date
    var totalAmount: Double
    var items: [ReceiptItem]           // Relationship
    var isVerified: Bool

    // YNAB sync tracking
    var ynabTransactionId: String?
    var ynabAccountId: String?
    var lastSyncedAt: Date?
    var isLocalOnly: Bool = false

    // Per-receipt line items sync mode tracking (iOS 26 feature)
    // nil = not synced OR old receipt (before feature)
    // true = uploaded WITH subtransactions
    // false = uploaded WITHOUT subtransactions
    var syncedWithLineItems: Bool?

    // Confidence scoring
    var confidenceScore: ReceiptConfidenceScore?
}

@Model
final class ReceiptItem {
    var name: String
    var quantity: Int
    var price: Double
    var category: String?
    var ynabSubtransactionId: String?
    var isDeleted: Bool  // Soft delete flag
}
```

**Why two images:**
- **thumbnailData**: Used for 76×76pt display in list/detail views (200KB memory)
- **imageData**: Used only for full-screen zoom/pan preview (8MB memory)
- **Memory optimization**: 97.5% reduction with @State caching
- **External storage**: Images stored as files, not loaded with @Query

**Image processing:**
- Max dimension: 2048px (downsample before storage)
- JPEG quality: 0.8 for both full and thumbnail
- Orientation: Fixed based on EXIF data
- Thumbnail: Preserves aspect ratio with constraints (max 3:1)

**Migration:** V1→V2→V3 supported via `ReceiptMigrationPlan`

#### AI Receipt (@Generable)

```swift
@Generable
struct AIReceipt {
    @Guide(description: "The name of the merchant")
    var merchantName: String

    @Guide(description: "The date in YYYY-MM-DD format")
    var dateString: String

    @Guide(description: "The total amount")
    var totalAmount: Double

    @Guide(description: "List of all purchased items...")
    var items: [AIReceiptItem]
}
```

The `@Generable` protocol enables Apple Intelligence to return structured data from unstructured OCR text.

#### YNAB Transaction

```swift
struct YNABTransactionWithSubs {
    let account_id: String
    let payee_name: String?
    let amount: Int               // YNAB uses milliunits (1000 = $1.00)
    let date: String              // "YYYY-MM-DD"
    let subtransactions: [YNABSubTransaction]?
    let import_id: String?        // For duplicate detection
}
```

---

## Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/Receipts for YNAB.git
cd Receipts for YNAB
```

### 2. Configure YNAB API Credentials

⚠️ **Important**: API credentials are stored securely and NOT committed to git.

1. **Get YNAB credentials** at [YNAB Developer Portal](https://app.youneedabudget.com/settings/developer)
   - Set redirect URI to: `Receipts for YNAB://oauth-callback`

2. **Create your secrets file**:
   ```bash
   cd Receipts for YNAB
   cp Secrets.plist.template Secrets.plist
   ```

3. **Edit `Receipts for YNAB/Secrets.plist`** with your credentials:
   ```xml
   <key>YNAB_CLIENT_ID</key>
   <string>your_client_id_here</string>
   <key>YNAB_CLIENT_SECRET</key>
   <string>your_client_secret_here</string>
   ```

📖 **Detailed setup instructions**: See [SETUP.md](SETUP.md)

### 3. Enable Apple Intelligence (Optional)

For AI scanning features:
- Ensure your device has Apple Intelligence enabled
- Go to Settings → Apple Intelligence & Siri → Enable Apple Intelligence

> **Note**: Manual entry works without Apple Intelligence on any iOS 26+ device.

### 4. Build and Run

```bash
open Receipts for YNAB.xcodeproj
# Clean build folder (⌘⇧K)
# Build and run on iOS 26+ device or simulator (⌘R)
```

**Simulator Testing**: Use iPhone 16 simulator or newer for Apple Intelligence features.

---

## Usage

### First-Time Setup

1. Launch the app (automatic onboarding flow)
2. Complete 3-page feature introduction
3. Review subscription tiers (optional - Free tier available)
4. Tap "Sign In with YNAB"
5. Authorize the app in Safari
6. Select your default budget

### Scanning a Receipt

1. Tap the **Scan** tab
2. Choose scan method:
   - **Scan Document**: iOS document scanner with edge detection
   - **Take Photo**: Standard camera interface
   - **Choose from Photos**: Photo library picker
   - **Choose File**: File picker for PDFs/images
3. Wait for AI processing (2-5 seconds)
4. Review extracted details (merchant, date, total, items)
5. Edit if needed
6. Select YNAB account OR "Save Locally Only"
7. Tap **Save to YNAB** or **Save Locally**

### Home Screen Quick Actions

Long-press the app icon for quick access:
- Scan Document
- Take Photo
- Choose from Photos
- Choose File

### Managing Receipts

- View all receipts in the **Receipts** tab
- Tap any receipt to view details
- Edit synced receipts (merchant name and total only - date/items are immutable)
- Swipe left to delete
- Tap confidence score badge to see breakdown

### Settings

The Settings screen is organized into logical sections for easy navigation:

1. **Account**: YNAB connection status and sign-in/out
2. **Preferences**:
   - Subscription tier management
   - Input mode selection (AI Scanning vs Manual Entry)
   - Line items toggle (save receipt items to YNAB as subtransactions)
3. **Budget** (when authenticated):
   - Select default budget
   - View accounts and categories
   - Manage category selections
4. **Storage**:
   - View app data and cache usage
   - Refresh storage calculation
   - Clear cache (when available)
5. **Support**: Contact support via email
6. **App**: Version information
7. **Legal**: Privacy policy, terms of service, open source licenses
8. **Debug** (DEBUG builds only): StoreKit configuration and testing

---

## Subscription Tiers

The app offers three subscription tiers:

| Feature | Free | Manual | AI |
|---------|------|--------|-----|
| **Scans per month** | 10 | ∞ manual | ∞ AI |
| **YNAB uploads** | 5 | ∞ | ∞ |
| **AI extraction** | ✅ (limited) | ❌ | ✅ |
| **Manual entry** | ✅ | ✅ | ✅ |
| **Local storage** | ✅ | ✅ | ✅ |
| **Price** | Free | $X.XX/mo | $X.XX/mo |

### Product IDs

- `com.eturea.ynabreceipts.manual.monthly`
- `com.eturea.ynabreceipts.manual.yearly`
- `com.eturea.ynabreceipts.ai.monthly`
- `com.eturea.ynabreceipts.ai.yearly`

### Testing Subscriptions

Use `Resources/StoreKit/Receipts for YNABSubscriptionsManual.storekit` for local testing.

See [Subscription Testing Guide](docs/testing/subscription-testing.md) for detailed testing workflows.

---

## Testing

### Test Coverage Summary

| Layer | Coverage | Test Count |
|-------|----------|------------|
| **Services** | ~85% | 15+ test files |
| **ViewModels** | ~80% | 14 test files |
| **Models** | ~90% | 3 test files |
| **Views** | ~40% | 3 test files |
| **Integration** | Custom | 4 test files |
| **Overall** | **~75%** | **45 test files** |

### Test Organization

```bash
Receipts for YNABTests/
├── OAuth/                     # OAuth2 flow tests
├── Services/                  # Service layer (YNABService, NetworkMonitor, etc.)
├── ViewModels/                # MVVM workflow tests
├── Views/                     # SwiftUI view tests
├── Models/                    # SwiftData model tests
├── Integration/               # End-to-end workflows
├── Mocks/                     # Test doubles (MockYNABService, etc.)
└── Fixtures/                  # Test data generators
```

### Running Tests

```bash
# All tests
xcodebuild test -scheme Receipts for YNAB \
  -destination 'platform=iOS Simulator,name=iPhone 16'

# Or use Xcode: ⌘U
```

### Testing Requirements

**Simulator (✅ Recommended for most testing):**
- UI navigation and layout
- API integration with mocks
- Business logic
- State management
- Error handling
- Subscription flows (with StoreKit configuration)

**Physical Device (⚠️ Required for AI features):**
- Apple Intelligence scanning accuracy
- Camera integration
- Photo quality validation with real lens conditions
- Apple Intelligence availability detection
- Home screen quick actions
- Performance profiling with actual images

### Known Test Gaps

❌ **Not testable in simulator:**
- Apple Intelligence features (requires physical device with A17 Pro+)
- Camera/photo picker UI (simulator limitations)
- Real-world OCR accuracy (needs physical receipts)
- App Intents/Siri integration (manual testing only)

### Test Devices Used

- **Simulator**: iPhone 16 (iOS 26.0)
- **Physical**: iPhone 16 Pro (iOS 26.0) - for AI features

---

## API Reference

### YNAB API Endpoints Used

| Method | Endpoint | Purpose |
|--------|----------|---------|
| `GET` | `/budgets` | List user budgets |
| `GET` | `/budgets/{id}/accounts` | List accounts |
| `GET` | `/budgets/{id}/categories` | List categories |
| `POST` | `/budgets/{id}/transactions` | Create transaction |
| `PUT` | `/budgets/{id}/transactions/{id}` | Update transaction |
| `GET` | `/budgets/{id}/transactions/{id}` | Get transaction details |

**API Documentation**: [https://api.ynab.com/](https://api.ynab.com/)

### Vision Framework (iOS 26)

| API | Purpose |
|-----|---------|
| `RecognizeDocumentsRequest` | OCR with table/paragraph detection |
| `DetectLensSmudgeRequest` | Photo quality validation (blur/smudge) |
| `CalculateImageAestheticsScoresRequest` | Document classification |

### Foundation Models (iOS 26)

| API | Purpose |
|-----|---------|
| `SystemLanguageModel` | On-device AI model |
| `@Generable` protocol | Structured output from AI |
| `@Guide` property wrapper | Field descriptions for AI |

**Example:**

```swift
let model = try await SystemLanguageModel.default

let receipt = try await model.generate(
    prompt: ocrText,
    as: AIReceipt.self,
    tools: [categoryTool]
)
```

---

## Known Limitations

### Device & System Requirements

- **iOS 26.0+** required (no backward compatibility)
- **Apple Intelligence** recommended for AI features (works without it, but only manual entry)
- Receipt scanning accuracy depends on photo quality and lighting
- **No iCloud Sync**: Receipt data is stored locally only using SwiftData

### YNAB API Limitations

⚠️ **Critical**: The YNAB API has undocumented limitations when working with imported transactions (those created with `import_id`):

#### 1. Transaction Date is Immutable

- Once a receipt is synced to YNAB, the transaction date **cannot be changed** via the API
- The API returns HTTP 200 but **silently ignores** date field updates in PUT requests
- This affects all transactions created by this app since we use `import_id` for duplicate detection

**Workaround**: Manually edit the date in the YNAB web app or mobile app
**App Behavior**: Date field is displayed as **read-only** in edit mode for synced receipts

#### 2. Subtransactions are Immutable

- Receipt items (subtransactions) **cannot be edited** after syncing to YNAB
- The API allows updating the main transaction fields (merchant, total, memo) but not subtransactions
- You cannot add, remove, or modify individual items after the initial sync

**Workaround**: Delete the transaction in YNAB and rescan the receipt
**App Behavior**: Items section is displayed as **read-only cards** in edit mode for synced receipts

#### 3. Other Limitations

- **No Attachment Support**: YNAB API doesn't provide endpoints for uploading receipt images as transaction attachments. Receipt photos are stored locally in the app only.
- **Limited Category Support**: YNAB subtransactions support categories, but the parent transaction's category becomes "Split (Multiple Categories)" (expected YNAB behavior).
- **Merchant Name Sync**: YNAB stores merchants as `payee_id` (UUID references). If you change the payee in YNAB web app, the name won't sync back to the app. The app preserves the original merchant name from `import_payee_name` field.

For detailed technical documentation of these limitations, see [YNAB API Reference](docs/api-reference/ynab-api.md) and [Dual Save Mode](docs/features/dual-save-mode.md).

### Database Migration

- **Schema Evolution**: Adding new fields may require app reinstall during development
- **Migration Plan**: V1 → V2 → V3 supported
- **Data Backup**: No automatic backup - users should export important receipts

---

## Performance

Tested on **iPhone 16 Pro** (iOS 26.0):

| Metric | Value |
|--------|-------|
| **Receipt Scanning** | 2-5 seconds (end-to-end) |
| **OCR Processing** | 0.5-1.5 seconds |
| **AI Extraction** | 1-3 seconds |
| **Memory Usage (Peak)** | ~200MB |
| **Battery Impact** | <0.5% per receipt |
| **Max Receipt Items** | 50 items tested |
| **Image Size Limit** | 10MB recommended |

### Performance Optimizations

- Model prewarming on app launch
- In-memory product caching with storefront detection
- Efficient SwiftData queries with fetch limits
- Image compression for storage
- Background task management for OAuth refresh

### Memory Optimizations ✅

**SwiftData External Storage Implementation (Nov 2025):**

This is an **image-heavy app** with significant memory optimizations:

1. **External Storage**: Both images use `@Attribute(.externalStorage)` - stored as files, not in SQLite
2. **Dual-Image Strategy**: 400×400 thumbnails for display, 2048×2048 full images for zoom
3. **@State Caching**: Views decode images once, cache across refreshes (prevents 60 decodes/sec)
4. **Lazy Loading**: `@Query` loads metadata only, not image data

**Memory Impact:**
- List view (100 receipts): 30MB → 100KB (99.7% reduction)
- Detail view: 8MB → 200KB (97.5% reduction)
- Thumbnail display: 500ms → 20ms (25× faster)

**Storage Overhead:**
- +35KB per receipt (400×400 JPEG @ 0.8 quality)
- For 500 receipts: ~17.5MB total thumbnail overhead (acceptable)

**Additional Monitoring Areas:**
1. **Vision Requests**: Release resources after processing
2. **View Rebuilds**: Minimize unnecessary SwiftUI re-renders

See [Image Storage Architecture](docs/architecture/image-storage.md) for implementation details.
See [Professional Code Review Report](docs/architecture/code-review-2025-10-31.md) for additional performance recommendations.

---

## Documentation

Complete documentation is organized in [`/docs/`](docs/README.md):

### Quick Links

- **[Setup Guide](SETUP.md)** - Quick start installation and YNAB OAuth configuration
- **[Project Instructions](CLAUDE.md)** - AI agent guidance and development workflows

### Documentation Structure

- **[Features](docs/features/)** - Detailed feature documentation
  - [Receipt Scanning](docs/features/receipt-scanning.md) - AI-powered scanning workflow
  - [Dual Save Mode](docs/features/dual-save-mode.md) - Local vs YNAB sync modes
  - [Adaptive Scanning UX](docs/features/adaptive-scanning-ux.md) - Duration-based feedback
  - [Confidence Scoring](docs/features/confidence-scoring.md) - Quality assessment system
  - [Quick Actions](docs/features/quick-actions.md) - Home screen shortcuts

- **[Architecture](docs/architecture/)** - System design and patterns
  - [MVVM Pattern](docs/architecture/mvvm.md) - View-ViewModel architecture
  - [Dependency Injection](docs/architecture/dependency-injection.md) - AppServices container
  - [State Management](docs/architecture/state-management.md) - Combine + Observable patterns
  - [Code Review Report](docs/architecture/code-review-2025-10-31.md) - Professional audit

- **[API Reference](docs/api-reference/)** - Integration documentation
  - [YNAB API](docs/api-reference/ynab-api.md) - OAuth2 flow and API limitations
  - [Vision Framework](docs/api-reference/vision-framework.md) - iOS 26 OCR APIs
  - [Foundation Models](docs/api-reference/foundation-models.md) - Apple Intelligence integration
  - [StoreKit](docs/api-reference/storekit.md) - Subscription system

- **[Testing](docs/testing/)** - Testing guides and strategies
  - [Test Strategy](docs/testing/test-strategy.md) - Overall testing approach
  - [Test Coverage](docs/testing/test-coverage.md) - Coverage reports and gaps
  - [Subscription Testing](docs/testing/subscription-testing.md) - StoreKit testing workflows
  - [Mock Guidelines](docs/testing/mock-guidelines.md) - Test doubles and fixtures

- **[Localization](docs/localization/)** - Translation and internationalization
  - [Overview](docs/localization/README.md) - String Catalog guide
  - [Key Naming](docs/localization/key-naming.md) - Semantic key conventions
  - [Pluralization](docs/localization/pluralization.md) - Plural handling guide

### Additional Resources

- **[Archive](docs/archive/)** - Historical documentation, test reports, and bug fixes
- **[Legal](docs/legal/)** - Privacy policy, terms of service, licenses

---

## Troubleshooting

### "Apple Intelligence Required" Error

**Cause**: Trying to use AI scanning on incompatible device or with AI disabled

**Solutions**:
- Verify Apple Intelligence is enabled: Settings → Apple Intelligence & Siri → Enable
- Restart the app after enabling
- Use manual entry if device doesn't support Apple Intelligence
- Check device compatibility (requires A17 Pro or later)

### Authentication Fails with "invalid_client"

**Cause**: Incorrect OAuth credentials or configuration

**Solutions**:
- Verify credentials in `Secrets.plist` (no extra spaces/quotes)
- Check redirect URI matches exactly: `Receipts for YNAB://oauth-callback`
- Verify client ID and secret are from YNAB Developer Portal
- Clean build folder (⌘⇧K) and rebuild

### OAuth Callback Not Working

**Cause**: URL scheme not configured correctly

**Solutions**:
- Check `Info.plist` has `CFBundleURLSchemes` = `Receipts for YNAB`
- Verify YNAB Developer Portal has exact redirect URI
- Try signing out and back in

### Poor Scanning Results

**Cause**: Poor photo quality, lighting, or receipt condition

**Solutions**:
- Ensure good lighting (natural light preferred)
- Clean camera lens (app validates this automatically)
- Flatten receipt before photographing
- Use high-contrast background (white works best)
- Avoid shadows and glare
- Try "Scan Document" method for edge detection

### App Crashes on Launch

**Cause**: Database corruption or migration failure

**Solutions**:
- Check Xcode console for error messages
- Delete app and reinstall (⚠️ loses local data)
- Verify iOS version is 26.0+
- Check available storage space

### Receipts Not Syncing to YNAB

**Cause**: Network issues, expired token, or account selection

**Solutions**:
- Check network connection (look for offline banner)
- Try signing out and back in to refresh token
- Verify budget and account are selected
- Check YNAB API status: [https://status.youneedabudget.com/](https://status.youneedabudget.com/)

### Can't Edit Receipt Date After Syncing

**This is a known YNAB API limitation**, not a bug. See [Known Limitations](#ynab-api-limitations) above.

**Workaround**: Edit the transaction date directly in YNAB web/mobile app.

### Subscription Not Restoring

**Cause**: App Store account mismatch or pending transaction

**Solutions**:
- Sign out and back in to the App Store
- Wait 24-48 hours for pending transactions to complete
- Use "Restore Purchases" in Settings → Subscription
- Contact App Store support for purchase issues

### "Network Unavailable" Banner Won't Dismiss

**Cause**: Poor network connectivity or DNS issues

**Solutions**:
- Check Wi-Fi/cellular connection
- Toggle Airplane Mode on and off
- Restart the app
- Banner auto-dismisses when network is restored

---

## Contributing

Contributions are welcome! Please follow these guidelines:

### Development Workflow

1. Fork the repository
2. Create a feature branch:
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. Make your changes
4. Run tests:
   ```bash
   xcodebuild test -scheme Receipts for YNAB
   ```
5. Commit with descriptive messages:
   ```bash
   git commit -m "Add amazing feature"
   ```
6. Push to your fork:
   ```bash
   git push origin feature/amazing-feature
   ```
7. Open a Pull Request

### Code Style

- Follow Swift 6.0 conventions
- Use `@MainActor` for UI-related classes
- Prefer async/await over completion handlers
- Use SwiftUI previews for views
- Add tests for new features
- Document complex logic with comments

### Specialized Agents

This project uses 5 specialized Claude agents, all configured and active at `~/.claude/agents/`:

- **ios26-code-reviewer**: iOS 26 best practices, memory safety, concurrency patterns
- **swiftui-ux-polish**: Animations, accessibility, haptics, delightful UX
- **simulator-test-engineer**: XCTest, mocks, UI tests, performance benchmarks
- **ios-security-auditor**: Security audits, vulnerability reviews, OAuth/Keychain
- **beta-prep-specialist**: TestFlight, release notes, tester communication

See [CLAUDE.md](CLAUDE.md) for full agent documentation and usage guidelines.

---

## Roadmap

### Completed ✅

- [x] AI-powered receipt scanning with Apple Intelligence
- [x] YNAB OAuth2 integration with PKCE
- [x] SwiftData persistence with migration support
- [x] Subscription system (Free/Manual/AI tiers)
- [x] Network resilience with offline/online detection
- [x] Onboarding flow with paywall
- [x] AI-generated greetings with typewriter animation
- [x] Rotating tips system (15 tips)
- [x] Confidence scoring with detailed breakdown
- [x] Home screen quick actions (4 methods)
- [x] Per-receipt line items sync tracking
- [x] Comprehensive localization (String Catalogs)
- [x] 75% test coverage

### In Progress 🚧

- [ ] Beta testing on physical devices (iPhone 15 Pro+)
- [ ] Localization implementation (String Catalog complete, Swift file migration ongoing)
- [ ] Performance profiling for image-heavy workflows

### Planned 📋

**High Priority:**
- [ ] Receipt search and filtering
- [ ] Category suggestion using ML
- [ ] Export receipts to PDF
- [ ] Receipt analytics and insights (spending trends)

**Medium Priority:**
- [ ] iCloud sync for receipts
- [ ] Multi-receipt batch processing
- [ ] Receipt photo editing (crop/rotate)
- [ ] Duplicate receipt detection

**Low Priority:**
- [ ] Widget for recent receipts
- [ ] Apple Watch complication
- [ ] Siri shortcuts expansion
- [ ] Dark mode improvements

**Future Considerations:**
- [ ] Support for older iOS versions (requires non-AI fallback OCR)
- [ ] Android version (requires complete rewrite)

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2025 Receipts for YNAB

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## Acknowledgments

- [YNAB API](https://api.ynab.com/) for budget integration
- Apple's Vision and Foundation Models frameworks (iOS 26)
- SwiftUI and SwiftData for modern iOS development
- StoreKit 2 for subscription management

---

## Support

### Documentation Resources

- **Setup Guide**: [SETUP.md](SETUP.md)
- **Project Instructions**: [CLAUDE.md](CLAUDE.md)
- **Complete Documentation**: [docs/README.md](docs/README.md)
- **YNAB API**: [docs/api-reference/ynab-api.md](docs/api-reference/ynab-api.md)
- **Subscription Testing**: [docs/testing/subscription-testing.md](docs/testing/subscription-testing.md)
- **Code Review Report**: [docs/architecture/code-review-2025-10-31.md](docs/architecture/code-review-2025-10-31.md)

### Getting Help

For issues, questions, or suggestions:
- **GitHub Issues**: [Open an issue](https://github.com/yourusername/Receipts for YNAB/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/Receipts for YNAB/discussions)
- **Email**: your.email@example.com

### Reporting Bugs

Please include:
1. iOS version and device model
2. Steps to reproduce
3. Expected vs actual behavior
4. Xcode console logs if available
5. Screenshots if applicable

---

## Disclaimer

This is an **unofficial third-party app** and is not affiliated with or endorsed by YNAB (You Need A Budget). YNAB is a trademark of Steine LLC.

**Beta Status**: This app is currently in beta. While thoroughly tested, you may encounter bugs. Please report issues via GitHub.

**Data Privacy**: All receipt processing happens on-device. Receipt images are stored locally only and never uploaded to external servers (except as YNAB transactions, without images).

---

## Project Statistics

| Metric | Value |
|--------|-------|
| **Swift Files** | 108 (main) + 45 (tests) = 153 total |
| **Lines of Code** | ~15,000 (estimated) |
| **Test Coverage** | ~75% |
| **Localization Keys** | 1,657+ (English + Romanian) |
| **Supported Devices** | iPhone 15 Pro+ (iOS 26+) |
| **Version** | 1.0 (Build 1) |
| **Release Date** | Beta (2025) |

---

**Built with ❤️ using SwiftUI, SwiftData, and Apple Intelligence**

*Last updated: 2025-11-01*
