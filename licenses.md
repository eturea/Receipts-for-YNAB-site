# Legal Notices and Licenses

**Receipts for YNAB**
**Version:** 1.0
**Last Updated:** November 25, 2025

This document contains legal notices and license information for third-party software, frameworks, and services used in Receipts for YNAB.

---

## Table of Contents

1. [Receipts for YNAB License](#ynab-receipts-license)
2. [Apple Frameworks and SDKs](#apple-frameworks-and-sdks)
3. [Third-Party Services](#third-party-services)
4. [Open Source Components](#open-source-components)
5. [Trademarks](#trademarks)
6. [Contact Information](#contact-information)

---

## Receipts for YNAB License

**Copyright © 2025 eTurea. All rights reserved.**

Receipts for YNAB is proprietary software owned by eTurea. The app is licensed to end users under the terms specified in our [Terms of Service](./terms.md).

### License Summary

- **Type:** Proprietary
- **Usage:** Personal, non-commercial use only
- **Distribution:** Available exclusively through the Apple App Store
- **Restrictions:** No reverse engineering, modification, or redistribution

For full license terms, please refer to our [Terms of Service](./terms.md).

---

## Apple Frameworks and SDKs

Receipts for YNAB is built using Apple's iOS SDK and frameworks. All Apple frameworks are used under Apple's standard SDK license agreement.

### SwiftUI
- **Copyright:** © Apple Inc.
- **License:** Apple SDK License Agreement
- **Purpose:** User interface framework
- **Website:** https://developer.apple.com/xcode/swiftui/

### SwiftData
- **Copyright:** © Apple Inc.
- **License:** Apple SDK License Agreement
- **Purpose:** Data persistence and modeling framework
- **Website:** https://developer.apple.com/xcode/swiftdata/

### Vision Framework
- **Copyright:** © Apple Inc.
- **License:** Apple SDK License Agreement
- **Purpose:** On-device OCR and document recognition
- **Features Used:**
  - `RecognizeDocumentsRequest` - Text recognition
  - `DetectLensSmudgeRequest` - Photo quality validation
  - `CalculateImageAestheticsScoresRequest` - Document detection
- **Website:** https://developer.apple.com/documentation/vision

### Foundation Models (Apple Intelligence)
- **Copyright:** © Apple Inc.
- **License:** Apple SDK License Agreement
- **Purpose:** On-device AI for structured data extraction
- **Features Used:**
  - `SystemLanguageModel` - Natural language processing
  - `@Generable` protocol - Structured output generation
  - Tool calling for dynamic category retrieval
- **Website:** https://developer.apple.com/documentation/foundationmodels
- **Requirements:** iOS 26.0+, Apple Intelligence-capable devices (A17 Pro or later) for AI features; manual entry works on all iOS 26+ devices

### Combine
- **Copyright:** © Apple Inc.
- **License:** Apple SDK License Agreement
- **Purpose:** Reactive programming for authentication state management
- **Website:** https://developer.apple.com/documentation/combine

### Security Framework
- **Copyright:** © Apple Inc.
- **License:** Apple SDK License Agreement
- **Purpose:** iOS Keychain for secure credential storage
- **Website:** https://developer.apple.com/documentation/security

### UIKit
- **Copyright:** © Apple Inc.
- **License:** Apple SDK License Agreement
- **Purpose:** Camera, photo picker, and document scanner integrations
- **Website:** https://developer.apple.com/documentation/uikit

### App Intents
- **Copyright:** © Apple Inc.
- **License:** Apple SDK License Agreement
- **Purpose:** Siri and Shortcuts integration
- **Website:** https://developer.apple.com/documentation/appintents

### Swift Programming Language
- **Copyright:** © Apple Inc.
- **License:** Apache License 2.0 (Swift compiler and standard library)
- **Website:** https://swift.org
- **Open Source:** https://github.com/apple/swift

**Apple SDK License Agreement**

The Apple SDK and all frameworks listed above are used under the Apple SDK License Agreement. You can review the full agreement at:
https://developer.apple.com/support/terms/

**Important Notes:**
- All Apple frameworks are used as-is without modification
- On-device processing ensures data privacy (Vision, Foundation Models)
- Apple Intelligence features require compatible hardware (A17 Pro+) and iOS 26.0+

---

## Third-Party Services

### YNAB API (You Need A Budget)

**Service Provider:** Steine LLC (YNAB)
**Copyright:** © Steine LLC
**API Version:** v1
**Website:** https://api.youneedabudget.com

**Purpose:**
- OAuth2 authentication with YNAB accounts
- Retrieving plan, account, and category information
- Creating and updating transactions

**API License:**
The YNAB API is used under YNAB's API Terms of Service:
- **Terms:** https://www.ynab.com/terms
- **Privacy Policy:** https://www.ynab.com/privacy-policy/
- **API Documentation:** https://api.youneedabudget.com

**Authentication Protocol:**
- OAuth2 with PKCE (Proof Key for Code Exchange)
- Client credentials stored securely in iOS Keychain
- Tokens refreshed automatically as needed

**Disclaimer:**
Receipts for YNAB is an independent application and is not affiliated with, endorsed by, or sponsored by YNAB or Steine LLC.

---

## Open Source Components

### Swift Standard Library

**Copyright:** © Apple Inc. and the Swift project authors
**License:** Apache License 2.0
**Website:** https://swift.org
**Source Code:** https://github.com/apple/swift

**License Text:**

```
Apache License
Version 2.0, January 2004
http://www.apache.org/licenses/

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```

### Additional Open Source Dependencies

**Currently, Receipts for YNAB does not use any additional third-party open-source libraries beyond the Swift standard library and Apple frameworks.**

If open-source dependencies are added in future versions, they will be listed here with their respective licenses and attributions.

---

## Trademarks

### Receipts for YNAB

**"Receipts for YNAB"** and the Receipts for YNAB logo are trademarks of **eTurea**.

**Restrictions:**
- Unauthorized use of the Receipts for YNAB trademark is prohibited
- The app name and logo may not be used without written permission from eTurea

### YNAB (You Need A Budget)

**"YNAB"**, **"You Need A Budget"**, and the YNAB logo are trademarks of **Steine LLC**.

**Usage:**
- Used with permission to identify integration with YNAB's budgeting service
- Receipts for YNAB is not endorsed by or affiliated with YNAB
- All rights to the YNAB trademark remain with Steine LLC

### Apple

**"Apple"**, **"iPhone"**, **"iPad"**, **"iOS"**, **"App Store"**, **"Face ID"**, **"Touch ID"**, **"Siri"**, **"Shortcuts"**, **"SwiftUI"**, **"SwiftData"**, **"Apple Intelligence"**, and related trademarks are trademarks of **Apple Inc.**

**Usage:**
- Used to describe platform compatibility and features
- Receipts for YNAB is not endorsed by or affiliated with Apple Inc.
- All rights to Apple trademarks remain with Apple Inc.

---

## Copyright Notices

### Receipts for YNAB Source Code

**Copyright © 2025 eTurea. All rights reserved.**

The source code for Receipts for YNAB is proprietary and confidential. Unauthorized copying, modification, distribution, or reverse engineering is strictly prohibited.

### Receipt Data and User Content

**Users retain all ownership rights to their receipt images and data.**

By using Receipts for YNAB, users grant eTurea a limited license to:
- Process receipt images on-device using Apple Intelligence
- Store data locally on the user's device
- Transmit transaction data to YNAB when explicitly requested

This license does not grant eTurea ownership or commercial rights to user content. See our [Privacy Policy](./privacy.md) for details.

---

## Data Privacy and Security

### On-Device Processing

All receipt scanning and AI extraction is performed **entirely on your device** using Apple's frameworks:

- **Vision Framework:** OCR processing stays on-device
- **Foundation Models:** AI extraction occurs on-device (Apple Intelligence)
- **SwiftData:** Receipt data stored locally, never uploaded to external servers

### Third-Party Data Sharing

**The only external service that receives your data is YNAB**, and only when you explicitly choose to sync a receipt.

Data shared with YNAB includes:
- Transaction date, merchant name, amount
- Category assignments
- Line items (subtransactions)

YNAB's handling of your data is governed by their Privacy Policy:
https://www.ynab.com/privacy-policy/

### No Analytics or Tracking

Receipts for YNAB does **not** use:
- Analytics services (Google Analytics, Mixpanel, etc.)
- Advertising networks
- Crash reporting tools (Firebase, Sentry, etc.)
- User tracking or telemetry

For complete privacy details, see our [Privacy Policy](./privacy.md).

---

## Export Control

This software is subject to U.S. export control laws and regulations. By downloading or using Receipts for YNAB, you represent and warrant that:

- You are not located in a country subject to U.S. government embargo
- You are not listed on any U.S. government list of prohibited or restricted parties
- You will comply with all applicable export and re-export control laws and regulations

---

## Compliance Certifications

### Apple App Store Review Guidelines

Receipts for YNAB complies with Apple's App Store Review Guidelines:
https://developer.apple.com/app-store/review/guidelines/

**Key Compliance Areas:**
- Privacy (Guideline 5.1): On-device processing, transparent data handling
- Legal (Guideline 5.3): Complete Terms of Service and Privacy Policy
- Performance (Guideline 2.1): Optimized for iOS, no placeholder content
- User Interface (Guideline 4.0): Native iOS design with SwiftUI

### Privacy Regulations

Receipts for YNAB is designed to comply with:

- **GDPR** (General Data Protection Regulation) - European Union
- **CCPA** (California Consumer Privacy Act) - United States
- **COPPA** (Children's Online Privacy Protection Act) - United States

See our [Privacy Policy](./privacy.md) for full compliance details.

---

## License Updates

### Notification of Changes

If we add new third-party components or frameworks in future updates:
- This document will be updated accordingly
- Users will be notified of material changes
- The "Last Updated" date at the top will be revised

### Viewing Current Licenses

You can always view the most current version of this document:
- **In the App:** Settings → About → Licenses
- **Online:** Available at the app's website (if applicable)

---

## Acknowledgments

### Development Tools

Receipts for YNAB was built using:

- **Xcode** - Apple's integrated development environment
- **Swift** - Apple's programming language
- **iOS SDK** - Apple's iOS software development kit

### Inspiration and Thanks

We would like to thank:

- **The YNAB Team** for creating an excellent budgeting platform and providing a robust API
- **Apple** for their powerful on-device AI frameworks that enable privacy-first receipt scanning
- **Our Users** for trusting us with their financial data and providing valuable feedback

---

## Contact Information

If you have questions about licenses, attributions, or legal notices, please contact us:

**Email:** receiptsforynab.app@gmail.com
**Developer:** eTurea
**App Name:** Receipts for YNAB

For general support inquiries, please use the same contact email.

---

## Disclaimer

This license document is provided for informational purposes. While we make every effort to keep this information accurate and up-to-date, we make no warranties about the completeness or accuracy of this information.

For legally binding terms, please refer to:
- [Terms of Service](./terms.md) - User agreement
- [Privacy Policy](./privacy.md) - Data handling practices

---

**© 2025 eTurea. All rights reserved.**

This Legal Notices and Licenses document was last updated on November 25, 2025.

---

We are not affiliated, associated, or in any way officially connected with YNAB or any of its subsidiaries or affiliates. The official YNAB website can be found at [https://www.ynab.com](https://www.ynab.com).

The names YNAB and You Need A Budget, as well as related names, tradenames, marks, trademarks, emblems, and images are registered trademarks of YNAB.

---

## Full License Texts

### Apache License 2.0

The following is the full text of the Apache License 2.0, under which the Swift programming language is licensed:

```
                                 Apache License
                           Version 2.0, January 2004
                        http://www.apache.org/licenses/

   TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION

   1. Definitions.

      "License" shall mean the terms and conditions for use, reproduction,
      and distribution as defined by Sections 1 through 9 of this document.

      "Licensor" shall mean the copyright owner or entity authorized by
      the copyright owner that is granting the License.

      "Legal Entity" shall mean the union of the acting entity and all
      other entities that control, are controlled by, or are under common
      control with that entity. For the purposes of this definition,
      "control" means (i) the power, direct or indirect, to cause the
      direction or management of such entity, whether by contract or
      otherwise, or (ii) ownership of fifty percent (50%) or more of the
      outstanding shares, or (iii) beneficial ownership of such entity.

      "You" (or "Your") shall mean an individual or Legal Entity
      exercising permissions granted by this License.

      "Source" form shall mean the preferred form for making modifications,
      including but not limited to software source code, documentation
      source, and configuration files.

      "Object" form shall mean any form resulting from mechanical
      transformation or translation of a Source form, including but
      not limited to compiled object code, generated documentation,
      and conversions to other media types.

      "Work" shall mean the work of authorship, whether in Source or
      Object form, made available under the License, as indicated by a
      copyright notice that is included in or attached to the work
      (an example is provided in the Appendix below).

      "Derivative Works" shall mean any work, whether in Source or Object
      form, that is based on (or derived from) the Work and for which the
      editorial revisions, annotations, elaborations, or other modifications
      represent, as a whole, an original work of authorship. For the purposes
      of this License, Derivative Works shall not include works that remain
      separable from, or merely link (or bind by name) to the interfaces of,
      the Work and Derivative Works thereof.

      "Contribution" shall mean any work of authorship, including
      the original version of the Work and any modifications or additions
      to that Work or Derivative Works thereof, that is intentionally
      submitted to Licensor for inclusion in the Work by the copyright owner
      or by an individual or Legal Entity authorized to submit on behalf of
      the copyright owner. For the purposes of this definition, "submitted"
      means any form of electronic, verbal, or written communication sent
      to the Licensor or its representatives, including but not limited to
      communication on electronic mailing lists, source code control systems,
      and issue tracking systems that are managed by, or on behalf of, the
      Licensor for the purpose of discussing and improving the Work, but
      excluding communication that is conspicuously marked or otherwise
      designated in writing by the copyright owner as "Not a Contribution."

      "Contributor" shall mean Licensor and any individual or Legal Entity
      on behalf of whom a Contribution has been received by Licensor and
      subsequently incorporated within the Work.

   2. Grant of Copyright License. Subject to the terms and conditions of
      this License, each Contributor hereby grants to You a perpetual,
      worldwide, non-exclusive, no-charge, royalty-free, irrevocable
      copyright license to reproduce, prepare Derivative Works of,
      publicly display, publicly perform, sublicense, and distribute the
      Work and such Derivative Works in Source or Object form.

   3. Grant of Patent License. Subject to the terms and conditions of
      this License, each Contributor hereby grants to You a perpetual,
      worldwide, non-exclusive, no-charge, royalty-free, irrevocable
      (except as stated in this section) patent license to make, have made,
      use, offer to sell, sell, import, and otherwise transfer the Work,
      where such license applies only to those patent claims licensable
      by such Contributor that are necessarily infringed by their
      Contribution(s) alone or by combination of their Contribution(s)
      with the Work to which such Contribution(s) was submitted. If You
      institute patent litigation against any entity (including a
      cross-claim or counterclaim in a lawsuit) alleging that the Work
      or a Contribution incorporated within the Work constitutes direct
      or contributory patent infringement, then any patent licenses
      granted to You under this License for that Work shall terminate
      as of the date such litigation is filed.

   4. Redistribution. You may reproduce and distribute copies of the
      Work or Derivative Works thereof in any medium, with or without
      modifications, and in Source or Object form, provided that You
      meet the following conditions:

      (a) You must give any other recipients of the Work or
          Derivative Works a copy of this License; and

      (b) You must cause any modified files to carry prominent notices
          stating that You changed the files; and

      (c) You must retain, in the Source form of any Derivative Works
          that You distribute, all copyright, patent, trademark, and
          attribution notices from the Source form of the Work,
          excluding those notices that do not pertain to any part of
          the Derivative Works; and

      (d) If the Work includes a "NOTICE" text file as part of its
          distribution, then any Derivative Works that You distribute must
          include a readable copy of the attribution notices contained
          within such NOTICE file, excluding those notices that do not
          pertain to any part of the Derivative Works, in at least one
          of the following places: within a NOTICE text file distributed
          as part of the Derivative Works; within the Source form or
          documentation, if provided along with the Derivative Works; or,
          within a display generated by the Derivative Works, if and
          wherever such third-party notices normally appear. The contents
          of the NOTICE file are for informational purposes only and
          do not modify the License. You may add Your own attribution
          notices within Derivative Works that You distribute, alongside
          or as an addendum to the NOTICE text from the Work, provided
          that such additional attribution notices cannot be construed
          as modifying the License.

      You may add Your own copyright statement to Your modifications and
      may provide additional or different license terms and conditions
      for use, reproduction, or distribution of Your modifications, or
      for any such Derivative Works as a whole, provided Your use,
      reproduction, and distribution of the Work otherwise complies with
      the conditions stated in this License.

   5. Submission of Contributions. Unless You explicitly state otherwise,
      any Contribution intentionally submitted for inclusion in the Work
      by You to the Licensor shall be under the terms and conditions of
      this License, without any additional terms or conditions.
      Notwithstanding the above, nothing herein shall supersede or modify
      the terms of any separate license agreement you may have executed
      with Licensor regarding such Contributions.

   6. Trademarks. This License does not grant permission to use the trade
      names, trademarks, service marks, or product names of the Licensor,
      except as required for reasonable and customary use in describing the
      origin of the Work and reproducing the content of the NOTICE file.

   7. Disclaimer of Warranty. Unless required by applicable law or
      agreed to in writing, Licensor provides the Work (and each
      Contributor provides its Contributions) on an "AS IS" BASIS,
      WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
      implied, including, without limitation, any warranties or conditions
      of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A
      PARTICULAR PURPOSE. You are solely responsible for determining the
      appropriateness of using or redistributing the Work and assume any
      risks associated with Your exercise of permissions under this License.

   8. Limitation of Liability. In no event and under no legal theory,
      whether in tort (including negligence), contract, or otherwise,
      unless required by applicable law (such as deliberate and grossly
      negligent acts) or agreed to in writing, shall any Contributor be
      liable to You for damages, including any direct, indirect, special,
      incidental, or consequential damages of any character arising as a
      result of this License or out of the use or inability to use the
      Work (including but not limited to damages for loss of goodwill,
      work stoppage, computer failure or malfunction, or any and all
      other commercial damages or losses), even if such Contributor
      has been advised of the possibility of such damages.

   9. Accepting Warranty or Additional Liability. While redistributing
      the Work or Derivative Works thereof, You may choose to offer,
      and charge a fee for, acceptance of support, warranty, indemnity,
      or other liability obligations and/or rights consistent with this
      License. However, in accepting such obligations, You may act only
      on Your own behalf and on Your sole responsibility, not on behalf
      of any other Contributor, and only if You agree to indemnify,
      defend, and hold each Contributor harmless for any liability
      incurred by, or claims asserted against, such Contributor by reason
      of your accepting any such warranty or additional liability.

   END OF TERMS AND CONDITIONS
```

---

**End of Legal Notices and Licenses**
