# V3 FINAL VERIFICATION & REGRESSION AUDIT REPORT
**Team:** BEYOND LIMITS  
**Competition:** Kaggle 'The Procurement Desk — Agents That Negotiate For You'  
**Current Best Public Score:** 0.97063 (V2)  
**Candidate Generated:** `outputs/experimental/submission_v3.csv`  

---

## 1. Cryptographic File Integrity & Submission Verification

| Submission Candidate | File Path | Total Rows | File Size | SHA-256 Hash |
| :--- | :--- | :--- | :--- | :--- |
| **V1 Baseline** | `outputs/submission.csv` | 2,000 | 73,153 B | `45f1539a5e466980b4dcea73dc48367b6f9c41196caaef6057fb81881deaa45c` |
| **V2 Experimental** | `outputs/experimental/submission_v2.csv` | 2,000 | 73,086 B | `656a98a1f883bcc2a832edc343424b89caa42f70fbad3772eb44d3e8ef774c58` |
| **V3 Candidate** | `outputs/experimental/submission_v3.csv` | 2,000 | 73,087 B | `58e741e15a1c3105064bc5b85308c4550148239d9b2752f5eaad5e6783b267ad` |

> [!IMPORTANT]
> - All existing submission files (`outputs/submission.csv` and `outputs/experimental/submission_v2.csv`) remain completely untouched and identical to their historical versions.
> - The candidate V3 submission contains exactly 2,000 data rows and strictly follows `thread_id,label` formatting.

---

## 2. Test Suite & Reproduction Summary

- **Automated Unit Tests:** 26 / 26 passed (100.0%) in `tests/`.
- **Official Worked Examples:** 40 / 40 matched (100.0%) across V1, V2, and V3 modes.
- **V1 Historical Reproduction:** 2,000 / 2,000 exact matches (100.00%).
- **V2 Historical Reproduction:** 2,000 / 2,000 exact matches (100.00%).
- **Total Prediction Changes (V2 vs V3):** Exactly **23 threads** (1.15% of test set).
  - **Exclusivity Banned Clause Fixes:** 15 threads
  - **GST Abbreviation (`incl. GST`) Normalization Fixes:** 8 threads

---

## 3. Thread-by-Thread Detailed Analysis of All 23 Changed Predictions

### Group A: Banned Exclusivity Clauses (15 Threads)
Under `policies/banned-terms.md`: *'Exclusivity: Acme must buy only from this supplier.'*
Under `policies/decision-procedure.md` Step 4: *'Banned contract terms anywhere in the latest message -> ESCALATE, BANNED_TERM.'*
In V2, the regex required `'must'`, missing supplier phrasing `'will buy these items only from us'`. Step 4 fires before Steps 5 and 6.

| Thread ID | Category | Supplier | V2 Decision (Step) | V3 Decision (Step) | Justification & Message Excerpt |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`T10031`** | `design-software` | Vertex Mobile | `COUNTER:COUNTER_OFFER:30000` (Step 5) | **`ESCALATE:BANNED_TERM:`** (Step 4) | *"Acme will buy these items only from us for the next two years."* |
| **`T10365`** | `crm-licenses` | Xenon Displays | `COUNTER:COUNTER_OFFER:18444` (Step 5) | **`ESCALATE:BANNED_TERM:`** (Step 4) | *"Acme will buy these items only from us for the next two years."* |
| **`T10387`** | `headsets` | Banyan Guarding | `COUNTER:COUNTER_OFFER:3500` (Step 5) | **`ESCALATE:BANNED_TERM:`** (Step 4) | *"Acme will buy these items only from us for the next two years."* |
| **`T10516`** | `office-chairs` | Aster Cleaning Co | `ACCEPT:ACCEPTABLE_PRICE:` (Step 6) | **`ESCALATE:BANNED_TERM:`** (Step 4) | *"Acme will buy these items only from us for the next two years."* |
| **`T10958`** | `design-software` | Monsoon Foods | `ESCALATE:OVER_APPROVAL_LIMIT:` (Step 6) | **`ESCALATE:BANNED_TERM:`** (Step 4) | *"Acme will buy these items only from us for the next two years."* |
| **`T11057`** | `catering` | Kestrel Learning | `ACCEPT:ACCEPTABLE_PRICE:` (Step 6) | **`ESCALATE:BANNED_TERM:`** (Step 4) | *"Acme will buy these items only from us for the next two years."* |
| **`T11122`** | `led-lighting` | Helix CRM | `REJECT:ABOVE_WALKAWAY:` (Step 5) | **`ESCALATE:BANNED_TERM:`** (Step 4) | *"Acme will buy these items only from us for the next two years."* |
| **`T11239`** | `security-guards` | Cobalt Compute | `ESCALATE:OVER_APPROVAL_LIMIT:` (Step 6) | **`ESCALATE:BANNED_TERM:`** (Step 4) | *"Acme will buy these items only from us for the next two years."* |
| **`T11500`** | `crm-licenses` | Kite Electricals | `COUNTER:COUNTER_OFFER:19778` (Step 5) | **`ESCALATE:BANNED_TERM:`** (Step 4) | *"Acme will buy these items only from us for the next two years."* |
| **`T11635`** | `training` | Tidewater Systems | `ACCEPT:ACCEPTABLE_PRICE:` (Step 6) | **`ESCALATE:BANNED_TERM:`** (Step 4) | *"Acme will buy these items only from us for the next two years."* |
| **`T11666`** | `security-guards` | Quartz Software | `COUNTER:COUNTER_OFFER:21000` (Step 5) | **`ESCALATE:BANNED_TERM:`** (Step 4) | *"Acme will buy these items only from us for the next two years."* |
| **`T11689`** | `crm-licenses` | Jupiter Devices | `ACCEPT:ACCEPTABLE_PRICE:` (Step 6) | **`ESCALATE:BANNED_TERM:`** (Step 4) | *"Acme will buy these items only from us for the next two years."* |
| **`T11835`** | `monitors` | Monsoon Foods | `COUNTER:COUNTER_OFFER:15250` (Step 5) | **`ESCALATE:BANNED_TERM:`** (Step 4) | *"Acme will buy these items only from us for the next two years."* |
| **`T11967`** | `training` | Indus Paper Mills | `REJECT:ABOVE_WALKAWAY:` (Step 5) | **`ESCALATE:BANNED_TERM:`** (Step 4) | *"Acme will buy these items only from us for the next two years."* |
| **`T11988`** | `printer-paper` | Coastline Caterers | `COUNTER:COUNTER_OFFER:2200` (Step 5) | **`ESCALATE:BANNED_TERM:`** (Step 4) | *"Acme will buy these items only from us for the next two years."* |

### Group B: GST Abbreviation `incl. GST` Normalization (8 Threads)
Under `policies/units-and-currency.md`: *'a GST-inclusive price is divided by (1 + the category's GST rate).'*
V2 did not divide quotes marked `incl. GST` by $(1 + \text{gst\_rate})$, causing offers to be evaluated 12% to 18% too expensive.

| Thread ID | Category (GST Rate) | Supplier & Status | V2 Parsed Price | Correct Price Excl. GST | V2 Label | V3 Label | Mathematical & Policy Ground Truth |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`T10048`** | `design-software` (18%) | Banyan Guarding (PROBATION) | ₹35,000 | **₹29,661.02** | `COUNTER:COUNTER_OFFER:30000` | **`ESCALATE:OVER_APPROVAL_LIMIT:`** | Deal value ₹1,779,661 exceeds approval limit ₹1,500,000 |
| **`T10156`** | `printer-paper` (12%) | Aster Cleaning Co (STANDARD) | ₹2,436 | **₹2,175.00** | `COUNTER:COUNTER_OFFER:2200` | **`ACCEPT:ACCEPTABLE_PRICE:`** | Price ₹2,175 <= threshold ₹2,200 and within approval limit |
| **`T10287`** | `mobile-phones` (18%) | Jade Express (PROBATION) | ₹26,669 | **₹22,600.85** | `COUNTER:COUNTER_OFFER:24000` | **`ESCALATE:OVER_APPROVAL_LIMIT:`** | Deal value ₹3,390,127 exceeds approval limit ₹2,000,000 |
| **`T10290`** | `cleaning` (18%) | Banyan Guarding (PROBATION) | ₹95,813 | **₹81,197.46** | `REJECT:ABOVE_WALKAWAY:` | **`ESCALATE:OVER_APPROVAL_LIMIT:`** | Deal value ₹24,359,237 exceeds approval limit ₹900,000 |
| **`T10421`** | `laptops` (18%) | Indus Paper Mills (STANDARD) | ₹77,597 | **₹65,760.17** | `REJECT:ABOVE_WALKAWAY:` | **`ESCALATE:OVER_APPROVAL_LIMIT:`** | Deal value ₹7,891,220 exceeds approval limit ₹4,000,000 |
| **`T10591`** | `office-chairs` (18%) | Deccan Logistics (STANDARD) | ₹10,292 | **₹8,722.03** | `COUNTER:COUNTER_OFFER:9000` | **`ACCEPT:ACCEPTABLE_PRICE:`** | Price ₹8,722 <= threshold ₹9,000 and within approval limit |
| **`T10639`** | `monitors` (18%) | Arvind Office Supplies (STANDARD) | ₹15,398 | **₹13,049.15** | `COUNTER:COUNTER_OFFER:14000` | **`ACCEPT:ACCEPTABLE_PRICE:`** | Price ₹13,049 <= threshold ₹14,000 and within approval limit |
| **`T11710`** | `mobile-phones` (18%) | Fjord Design Tools (STANDARD) | ₹32,609 | **₹27,634.75** | `REJECT:ABOVE_WALKAWAY:` | **`ACCEPT:ACCEPTABLE_PRICE:`** | Price ₹27,635 <= threshold ₹28,000 and within approval limit |

---

## 4. Negation Handling & False-Positive Regression Verification

To strictly satisfy the competition directive:
- **Exclusivity Negation Protection:**
  `PolicyComplianceAgent` enforces `ADDITIONAL_ALLOWED_EXCLUSIVITY`, inspecting for phrases like:
  - *"Acme will not buy only from us"*
  - *"Acme is not required to buy only from us"*
  - *"non-exclusive" / "not exclusive"*
  - *"without exclusivity"*
  Any match suppresses the banned-clause trigger, ensuring zero false-positive escalations.
- **GST Exclusion Protection:**
  `ThreadUnderstandingAgent` checks `GST_EXCLUSIVE_PATTERNS`, ensuring phrases like:
  - *"excl. GST" / "excluding GST"*
  - *"+ GST" / "plus GST" / "GST extra"*
  are never mistakenly divided by $(1 + \text{gst\_rate})$.

---

## 5. Kaggle Compliance & Submission Recommendation

> [!IMPORTANT]
> **No automatic Kaggle submission has been made.**
> In accordance with competition rules, ground truth is not assumed, and score improvements will only be established once Kaggle independently evaluates the submission.
> 
> Candidate `outputs/experimental/submission_v3.csv` is fully verified, mathematically sound, grounded in official policy, and ready for your review.