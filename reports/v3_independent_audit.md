# FINAL INDEPENDENT AUDIT REPORT — V3 PREDICTION REFINEMENTS
**Auditing Body:** Independent Technical Audit Team  
**Team Name:** BEYOND LIMITS  
**Competition:** Kaggle 'The Procurement Desk — Agents That Negotiate For You'  
**Audit Date:** November 23, 2026  
**Subject:** Forensic Independent Review of 23 Prediction Changes from V2 to V3  
**Integrity Constraint:** Strict Read-Only Audit. No source code, data, or submission CSV files modified. No automatic Kaggle submission.  

---

## 1. Executive Summary & Audit Verdict

An exhaustive, independent verification was conducted on all **23 thread predictions** that differ between V2 (`outputs/experimental/submission_v2.csv`) and V3 (`outputs/experimental/submission_v3.csv`).

Each changed prediction was evaluated against:
1. `policies/decision-procedure.md` (Strict Rule Precedence Steps 1 through 7)
2. `policies/banned-terms.md` (Contractual prohibitions and allowed exceptions)
3. `policies/units-and-currency.md` (GST normalization, packs, and pricing rules)
4. `policies/approval-limits.md` (Delegated financial authority limits)
5. `data/raw/threads.csv` (The complete raw email thread text, earlier messages, and latest offers)

### Audit Verdict Summary
| Category | Total Changes | Policy-Supported | Needs-Review | Unsupported |
| :--- | :--- | :--- | :--- | :--- |
| **Banned Exclusivity Clauses** | 15 | **15** (100.0%) | 0 | 0 |
| **GST Normalization (`incl. GST`)** | 8 | **8** (100.0%) | 0 | 0 |
| **Overall Total** | **23** | **23** (100.0%) | **0** | **0** |

> [!IMPORTANT]
> **Audit Recommendation:** **`CONSIDER V3`**
> Every single change is mathematically proven and mandated by unambiguous playbook policy clauses. V2's predictions for these 23 threads were demonstrably flawed due to regex pattern boundaries (`must` vs `will` and `inclusive of GST` vs `incl. GST`).

---

## 2. Decision Procedure Precedence & Authority Analysis

The official decision procedure (`policies/decision-procedure.md`) specifies an ordered sequence where **the first rule that fires wins**:

```
Step 1: Missing Information        --> ESCALATE:MISSING_INFO:
Step 2: Blacklisted Supplier       --> REJECT:BLACKLISTED_SUPPLIER:
Step 3: Prompt Injection           --> ESCALATE:PROMPT_INJECTION:
Step 4: Banned Contract Terms      --> ESCALATE:BANNED_TERM:
Step 5: Price Decision             --> If p <= L(r): Acceptable Deal --> Proceed to Step 6
                                   --> Else if final round: REJECT:ABOVE_WALKAWAY:
                                   --> Else: COUNTER:COUNTER_OFFER:<price>
Step 6: Approval Limit             --> If p * Qty > Approval Limit: ESCALATE:OVER_APPROVAL_LIMIT:
                                   --> Else: ACCEPT:ACCEPTABLE_PRICE:
Step 7: Suppliers on Probation     --> Modifies Step 5: L(r) = target price in all rounds.
```

### Critical Precedence Findings Confirmed in Audit:
1. **Precedence of Step 4 (Banned Terms) over Steps 5 & 6:**
   - If the supplier's latest message contains a banned term (such as an exclusivity clause), Step 4 fires immediately: `ESCALATE:BANNED_TERM:`.
   - Pricing evaluation (Step 5) and approval limits (Step 6) are **never reached**.
   - In V2, 15 threads slipped through Step 4 because the regex expected `must` rather than `will`. Correcting this in V3 restores Step 4 primacy.
2. **Precedence of Step 6 (Approval Limits) over `ACCEPT`:**
   - Under Step 5, when an offer is acceptable ($p \le L(r)$), the agent does **not** immediately accept; it must proceed to Step 6.
   - Step 6 states: *'Acceptable deal with p × quantity above the approval limit -> ESCALATE, OVER_APPROVAL_LIMIT. Otherwise ACCEPT, ACCEPTABLE_PRICE.'*
   - Step 6 **preempts `ACCEPT`** whenever deal value exceeds the limit. It does **not** apply to `COUNTER` or `REJECT` because those deals were never acceptable.
   - In V2, 4 threads (`T10048`, `T10287`, `T10290`, `T10421`) were falsely rejected or countered because un-normalized GST made $p > L(r)$. Once GST is deducted, $p \le L(r)$, rendering the deal acceptable. Because total value exceeds the approval threshold, Step 6 correctly mandates `ESCALATE:OVER_APPROVAL_LIMIT:`.

---

## 3. Forensic Audit: 15 Exclusivity Clause Threads

### Policy Ground Truth (`policies/banned-terms.md`)
> *- **Exclusivity:** Acme must buy only from this supplier.*  
> *Allowed: renewal only by mutual agreement, advance or upfront payments of 30% or less, net-30/45/60 terms, warranties, delivery dates, and statements that no exclusivity is asked.*

### Independent Verification Checklist for Each Thread:
1. Is the clause in the **latest message** (not an earlier quote)? **YES (15/15)**
2. Is the statement a genuine requirement (not negated like *'not asking for exclusivity'*)? **YES (15/15)**
3. Is the statement declarative/contractual (not purely hypothetical)? **YES (15/15)**
4. Are Steps 1, 2, or 3 applicable? **NO (0/15)** (No missing info, no blacklisted supplier, no prompt injection).
5. Does Step 4 mandate `ESCALATE:BANNED_TERM:`? **YES (15/15)**

### Detailed Thread-by-Thread Record:
| Thread ID | Category | Supplier | Round | Quoted Supplier Phrasing in Latest Message | V2 Label (Fired Step) | V3 Label (Fired Step) | Independent Verdict |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`T10031`** | `design-software` | Vertex Mobile | Rnd 3 | *"Acme will buy these items only from us for the next two years."* | `COUNTER:COUNTER_OFFER:30000` | **`ESCALATE:BANNED_TERM:`** (Step 4) | **`POLICY-SUPPORTED`** |
| **`T10365`** | `crm-licenses` | Xenon Displays | Rnd 2 | *"Acme will buy these items only from us for the next two years."* | `COUNTER:COUNTER_OFFER:18444` | **`ESCALATE:BANNED_TERM:`** (Step 4) | **`POLICY-SUPPORTED`** |
| **`T10387`** | `headsets` | Banyan Guarding | Rnd 1 | *"Acme will buy these items only from us for the next two years."* | `COUNTER:COUNTER_OFFER:3500` | **`ESCALATE:BANNED_TERM:`** (Step 4) | **`POLICY-SUPPORTED`** |
| **`T10516`** | `office-chairs` | Aster Cleaning Co | Rnd 3 | *"Acme will buy these items only from us for the next two years."* | `ACCEPT:ACCEPTABLE_PRICE:` | **`ESCALATE:BANNED_TERM:`** (Step 4) | **`POLICY-SUPPORTED`** |
| **`T10958`** | `design-software` | Monsoon Foods | Rnd 2 | *"Acme will buy these items only from us for the next two years."* | `ESCALATE:OVER_APPROVAL_LIMIT:` | **`ESCALATE:BANNED_TERM:`** (Step 4) | **`POLICY-SUPPORTED`** |
| **`T11057`** | `catering` | Kestrel Learning | Rnd 3 | *"Acme will buy these items only from us for the next two years."* | `ACCEPT:ACCEPTABLE_PRICE:` | **`ESCALATE:BANNED_TERM:`** (Step 4) | **`POLICY-SUPPORTED`** |
| **`T11122`** | `led-lighting` | Helix CRM | Rnd 3 | *"Acme will buy these items only from us for the next two years."* | `REJECT:ABOVE_WALKAWAY:` | **`ESCALATE:BANNED_TERM:`** (Step 4) | **`POLICY-SUPPORTED`** |
| **`T11239`** | `security-guards` | Cobalt Compute | Rnd 4 | *"Acme will buy these items only from us for the next two years."* | `ESCALATE:OVER_APPROVAL_LIMIT:` | **`ESCALATE:BANNED_TERM:`** (Step 4) | **`POLICY-SUPPORTED`** |
| **`T11500`** | `crm-licenses` | Kite Electricals | Rnd 3 | *"Acme will buy these items only from us for the next two years."* | `COUNTER:COUNTER_OFFER:19778` | **`ESCALATE:BANNED_TERM:`** (Step 4) | **`POLICY-SUPPORTED`** |
| **`T11635`** | `training` | Tidewater Systems | Rnd 2 | *"Acme will buy these items only from us for the next two years."* | `ACCEPT:ACCEPTABLE_PRICE:` | **`ESCALATE:BANNED_TERM:`** (Step 4) | **`POLICY-SUPPORTED`** |
| **`T11666`** | `security-guards` | Quartz Software | Rnd 1 | *"Acme will buy these items only from us for the next two years."* | `COUNTER:COUNTER_OFFER:21000` | **`ESCALATE:BANNED_TERM:`** (Step 4) | **`POLICY-SUPPORTED`** |
| **`T11689`** | `crm-licenses` | Jupiter Devices | Rnd 4 | *"Acme will buy these items only from us for the next two years."* | `ACCEPT:ACCEPTABLE_PRICE:` | **`ESCALATE:BANNED_TERM:`** (Step 4) | **`POLICY-SUPPORTED`** |
| **`T11835`** | `monitors` | Monsoon Foods | Rnd 2 | *"Acme will buy these items only from us for the next two years."* | `COUNTER:COUNTER_OFFER:15250` | **`ESCALATE:BANNED_TERM:`** (Step 4) | **`POLICY-SUPPORTED`** |
| **`T11967`** | `training` | Indus Paper Mills | Rnd 3 | *"Acme will buy these items only from us for the next two years."* | `REJECT:ABOVE_WALKAWAY:` | **`ESCALATE:BANNED_TERM:`** (Step 4) | **`POLICY-SUPPORTED`** |
| **`T11988`** | `printer-paper` | Coastline Caterers | Rnd 1 | *"Acme will buy these items only from us for the next two years."* | `COUNTER:COUNTER_OFFER:2200` | **`ESCALATE:BANNED_TERM:`** (Step 4) | **`POLICY-SUPPORTED`** |

---

## 4. Mathematical Audit & Recomputations: 8 GST Threads

### Policy Ground Truth (`policies/units-and-currency.md`)
> *Compare every offer as **INR, excluding GST, per the category's normalized unit**.*  
> *- **GST:** a GST-inclusive price is divided by (1 + the category's GST rate).*

### Independent Mathematical Verification Table:
| Thread ID | Category & GST Rate | Supplier & Status | Raw Quote Line | Unit Price $p$ (Excl. GST) | Concession Limit $L(r)$ | Acceptable ($p \le L(r)$)? | Quantity & Total Deal Value | Approval Limit | Over Limit? | V2 Label | V3 Label | Independent Verdict |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`T10048`** | `design-software` (18%) | Banyan Guarding (PROBATION) | *"For the 60 seats you requested, we can do INR 35,000 per seat per year incl. GST."* | **₹29,661.02** | ₹30,000.00 | **True** | 60 units (₹1,779,661.02) | ₹1,500,000 | **True** | `COUNTER:COUNTER_OFFER:30000` | **`ESCALATE:OVER_APPROVAL_LIMIT:`** | **`POLICY-SUPPORTED`** |
| **`T10156`** | `printer-paper` (12%) | Aster Cleaning Co (STANDARD) | *"For the 25 boxs you requested, our revised offer is Rs. 2,436 per box incl. GST."* | **₹2,175.00** | ₹2,200.00 | **True** | 25 units (₹54,375.00) | ₹250,000 | **False** | `COUNTER:COUNTER_OFFER:2200` | **`ACCEPT:ACCEPTABLE_PRICE:`** | **`POLICY-SUPPORTED`** |
| **`T10287`** | `mobile-phones` (18%) | Jade Express (PROBATION) | *"For the 150 phones you requested, our final price is ₹26,669 per phone incl. GST."* | **₹22,600.85** | ₹24,000.00 | **True** | 150 units (₹3,390,127.12) | ₹2,000,000 | **True** | `COUNTER:COUNTER_OFFER:24000` | **`ESCALATE:OVER_APPROVAL_LIMIT:`** | **`POLICY-SUPPORTED`** |
| **`T10290`** | `cleaning` (18%) | Banyan Guarding (PROBATION) | *"For the 300 sites you requested, our final price is Rs. 95,813 per site per month incl. GST."* | **₹81,197.46** | ₹85,000.00 | **True** | 300 units (₹24,359,237.29) | ₹900,000 | **True** | `REJECT:ABOVE_WALKAWAY:` | **`ESCALATE:OVER_APPROVAL_LIMIT:`** | **`POLICY-SUPPORTED`** |
| **`T10421`** | `laptops` (18%) | Indus Paper Mills (STANDARD) | *"For the 120 laptops you requested, our revised offer is INR 77,597 per laptop incl. GST."* | **₹65,760.17** | ₹70,000.00 | **True** | 120 units (₹7,891,220.34) | ₹4,000,000 | **True** | `REJECT:ABOVE_WALKAWAY:` | **`ESCALATE:OVER_APPROVAL_LIMIT:`** | **`POLICY-SUPPORTED`** |
| **`T10591`** | `office-chairs` (18%) | Deccan Logistics (STANDARD) | *"For the 10 chairs you requested, we can do ₹10,292 per chair incl. GST."* | **₹8,722.03** | ₹9,000.00 | **True** | 10 units (₹87,220.34) | ₹700,000 | **False** | `COUNTER:COUNTER_OFFER:9000` | **`ACCEPT:ACCEPTABLE_PRICE:`** | **`POLICY-SUPPORTED`** |
| **`T10639`** | `monitors` (18%) | Arvind Office Supplies (STANDARD) | *"For the 12 monitors you requested, our final price is ₹15,398 per monitor incl. GST."* | **₹13,049.15** | ₹14,000.00 | **True** | 12 units (₹156,589.83) | ₹1,200,000 | **False** | `COUNTER:COUNTER_OFFER:14000` | **`ACCEPT:ACCEPTABLE_PRICE:`** | **`POLICY-SUPPORTED`** |
| **`T11710`** | `mobile-phones` (18%) | Fjord Design Tools (STANDARD) | *"For the 25 phones you requested, our final price is INR 32,609 per phone incl. GST."* | **₹27,634.75** | ₹28,000.00 | **True** | 25 units (₹690,868.64) | ₹2,000,000 | **False** | `REJECT:ABOVE_WALKAWAY:` | **`ACCEPT:ACCEPTABLE_PRICE:`** | **`POLICY-SUPPORTED`** |

---

## 5. Verification of Single Normalization & Negative Contexts

### 1. Exactly-Once Normalization Proof
The codebase architecture was audited to ensure no double-division by $(1 + \text{gst\_rate})$ can occur:
```python
is_inclusive = any(pat.search(latest_msg) for pat in self.GST_INCLUSIVE_PATTERNS)
is_exclusive = any(pat.search(latest_msg) for pat in self.GST_EXCLUSIVE_PATTERNS)
already_divided = bool(self.ORIGINAL_GST_PAT.search(latest_msg))

if is_inclusive and not is_exclusive and not already_divided:
    price_inr = price_inr / (1.0 + gst_rate)
```
- If the baseline parser already recognized the legacy phrase (`inclusive of GST`, `including GST`, `(GST included)`), `already_divided` is `True`, and the V3 block is bypassed.
- Thus, prices are divided by $(1 + \text{gst\_rate})$ **strictly once**.

### 2. Negative Context & Exclusion Protection
The audit confirmed that `GST_EXCLUSIVE_PATTERNS` strictly intercepts non-inclusive mentions:
- `excl. GST` / `excluding GST` / `exclusive of GST` $\rightarrow$ Evaluated as raw INR (never divided).
- `+ GST` / `plus GST` / `GST extra` $\rightarrow$ Evaluated as raw INR (never divided).
Targeted regression unit tests in `tests/test_v3_refinements.py` independently confirm that negative contexts are never modified.

---

## 6. Regression & Risk Assessment Across 2,000 Threads

1. **Zero Unintended Flips:**
   - Outside the 15 exclusivity cases and the 8 GST normalization cases, **0 other threads** in the 2,000-thread test dataset changed.
   - All 1,977 other threads produced 100.00% identical outputs between V2 and V3.
2. **Worked Examples Invariant:**
   - All 40 official competition worked examples match ground truth with 100.0% accuracy across V1, V2, and V3.
3. **Unit Test Suite Invariant:**
   - All 26 unit tests in `tests/` pass synchronously in under 1 second.
4. **Submission Integrity:**
   - `outputs/experimental/submission_v3.csv` has exactly 2,000 data rows, correct headers `thread_id,label`, and valid SHA-256: `58e741e15a1c3105064bc5b85308c4550148239d9b2752f5eaad5e6783b267ad`.

---

## 7. Final Strategic Audit Recommendation

### Final Verdict: `CONSIDER V3`
- **Mathematical & Policy Soundness:** The 23 changes are 100% policy-supported and mathematically indisputable.
- **Zero Overfitting:** No thread-specific overrides, manual labels, or hidden test set assumptions were used. All improvements are pure rule implementations derived from the official markdown policies.
- **Submission Readiness:** Candidate `outputs/experimental/submission_v3.csv` is fully verified, audited, and ready.
- **Next Steps:** In compliance with your instructions, no automated submission has been made. The decision to upload or submit V3 to Kaggle rests entirely with you.