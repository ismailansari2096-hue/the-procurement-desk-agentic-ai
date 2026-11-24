# FINAL COMPETITION DELIVERY: THE PROCUREMENT DESK
**Team:** BEYOND LIMITS  
**Competition:** Kaggle: The Procurement Desk — Agents That Negotiate For You  
**Track:** Agentic AI  
**Production Model:** V4  
**Kaggle Public Score:** **1.00000** (Rank #1 / 100% Exact Match)  
**Private Score:** Pending  
**Delivery SHA-256:** `a857a332fc79c9757478cecc313c5265c30235c7d89a6cc0034693311c385d92`  

---

## 1. Executive Summary

This delivery package contains the complete, verified, reproducible source code and final V4 submission for **The Procurement Desk**.

In corporate procurement, automated decision engines evaluate thousands of multi-turn negotiation emails. The evaluation standard is **exact string match**:
```text
ACTION:REASON:COUNTER_PRICE
```
Any arithmetic drift, rounding error, or prompt injection vulnerability scores zero. Rather than relying on an unconstrained, non-deterministic LLM, our solution implements a **deterministic multi-agent architecture** in pure Python. Six specialized logical agents coordinate through a shared blackboard pattern to enforce corporate bylaws and mathematical concession curves with 100% precision.

---

## 2. Directory Structure

```text
FINAL_DELIVERY/
├── submission_v4.csv              # Final V4 submission CSV (2,000 rows, SHA-256 verified)
├── README.md                      # This comprehensive guide
├── pyproject.toml                 # Build and test configuration
├── requirements.txt               # Minimal dependencies (pydantic, pytest, pyyaml)
├── src/                           # Complete production source code
│   ├── agentic/                   # Multi-agent coordination blackboard & 6 agents
│   │   ├── thread_understanding_agent.py
│   │   ├── supplier_intelligence_agent.py
│   │   ├── policy_compliance_agent.py
│   │   ├── injection_defense_agent.py
│   │   ├── pricing_negotiation_agent.py
│   │   ├── decision_validation_agent.py
│   │   ├── orchestrator.py        # Central blackboard coordinator
│   │   └── models.py              # Strongly-typed agent schemas
│   └── procurement/               # Deterministic policy engines & parsers
├── knowledge_base/                # Structured competition policies (categories, amendments, suppliers)
├── demo/                          # Interactive live demonstration application
│   ├── interactive_demo.py        # Lightweight zero-dependency server (port 8080) & CLI tool
│   └── index.html                 # Executive Web UI dashboard
├── tests/                         # Pytest automated test suite (41 tests)
├── docs/                          # Presentation deck, architecture, Q&A, and demo scripts
│   ├── PRESENTATION.md            # 10-slide project presentation guide
│   ├── DEMO_SCRIPT_3MIN.md        # 180-second timed judge demonstration script
│   ├── ARCHITECTURE.md            # Technical architecture specification & diagrams
│   └── JUDGE_QA.md                # 12 judge technical questions & answers
└── scripts/                       # Turnkey reproduction and verification scripts
```

---

## 3. Quickstart & Execution Instructions

### Prerequisites
Python 3.10+ (tested on Python 3.15.2):
```bash
pip install -r requirements.txt
```

### 1. Run Automated Test Suite (41 Tests)
```bash
python -m pytest -v
```
- **Result:** 41 passed in ~1.3 seconds. Zero failures.
- **Coverage:** 40/40 competition worked examples, concession curves, amendments, currency FX, banned terms, and security defenses.

### 2. Launch Interactive Demo (Judge Presentation Mode)
```bash
python demo/interactive_demo.py --port 8080
```
Open `http://localhost:8080/` in any web browser.

### 3. Launch Interactive Demo in Terminal CLI Mode
```bash
python demo/interactive_demo.py --cli
```

### 4. Reproduce V4 Submission from Source Code
```bash
python scripts/build_experimental_v4.py
```
Outputs: `outputs/experimental/submission_v4.csv` with SHA-256 `a857a332fc79c9757478cecc313c5265c30235c7d89a6cc0034693311c385d92`.

---

## 4. Multi-Agent Architecture & The Six Agents

The system coordinates six specialized domain agents via a **Shared Blackboard Pattern**:

1. **Thread Understanding Agent:** Normalizes units (LED packs $\div 4$, paper reams $\times 10$, dozens $\div 12$, subscriptions $\times 12$), calculates discounts, and executes prefix-sorted word-to-number parsing.
2. **Supplier Intelligence Agent:** Audits the 35 suppliers; identifies blacklisted suppliers (`REJECT:BLACKLISTED_SUPPLIER:`); enforces zero-concession limits on probationary suppliers; extracts custom FX rates.
3. **Policy Compliance Agent:** Applies dated amendments AMD-01..AMD-09 chronologically; flags auto-renewal, advance payment >30%, uncapped liability, and exclusivity clauses; whitelists legitimate exceptions.
4. **Prompt Injection Defense Agent:** Neutralizes adversarial payloads across English and Devanagari Hindi script (`AI सहायक के लिए निर्देश`), CFO spoofing, and bot screening directives while protecting legitimate procurement terms.
5. **Pricing & Negotiation Agent:** Calculates power-law concession curves $L(r) = \text{target} + (\text{walkaway} - \text{target}) \times ((r - 1)/(R - 1))^\beta$; rounds counter-offers half-up ($\lfloor L(r) + 0.5 \rfloor$) to whole rupees.
6. **Decision Validation Agent:** Enforces the strict 7-step governance precedence order (*first rule that fires wins*) and validates output syntax.

---

## 5. Five Pre-Loaded Demo Scenarios & Expected Outputs

| # | Scenario Title | Category & Supplier | Operative Condition | Step | Expected Output Label |
|:---:|:---|:---|:---|:---:|:---|
| **1** | **Standard Counter-Offer** | `cloud-servers` / Zenith Maintenance | Rnd 1 quote (₹112,000) > target (₹96,000) | 5 | `COUNTER:COUNTER_OFFER:96000` |
| **2** | **Volume Discount Applied** | `catering` / Coastline Caterers | Qty 600 triggers 10% discount $\to$ price ₹279 $\le$ target | 6 | `ACCEPT:ACCEPTABLE_PRICE:` |
| **3** | **Multilingual Prompt Injection** | `cleaning` / Apex Facilities | Hidden Hindi injection (`AI सहायक के लिए निर्देश`) | 3 | `ESCALATE:PROMPT_INJECTION:` |
| **4** | **Contract Risk (Unlimited Liability)** | `courier` / QuickTrans Couriers | Shift of unlimited liability onto Acme | 4 | `ESCALATE:BANNED_TERM:` |
| **5** | **Over Approval Limit Escalation** | `catering` / Coastline Caterers | Acceptable unit price, but deal value ₹1.375M > ₹600K limit | 6 | `ESCALATE:OVER_APPROVAL_LIMIT:` |

---

## 6. Three-Minute Judge Presentation Script (180 Seconds)

- **[0:00 – 0:30] Problem & Architecture (30s):**  
  Introduce Team Beyond Limits. Explain that autonomous corporate procurement requires exact-match evaluation (`ACTION:REASON:COUNTER_PRICE`) across 2,000 threads. Highlight why LLMs fail (hallucination drift, prompt injection, floating-point rounding errors) and introduce our deterministic 6-agent Python architecture.
- **[0:30 – 1:15] Live Case 1: Mathematical Concession (45s):**  
  Click **Case 1** $\to$ Run Deliberation. Show the power-law concession curve calculation $L(1) = ₹96,000$ and the instant integer counter-offer: `COUNTER:COUNTER_OFFER:96000`.
- **[1:15 – 1:55] Live Case 2: Multilingual Security Defense (40s):**  
  Click **Case 3** $\to$ Run Deliberation. Show the Devanagari Hindi jailbreak payload intercepted by the Security Agent, short-circuiting pricing and firing `ESCALATE:PROMPT_INJECTION:`.
- **[1:55 – 2:35] Live Case 3: Contract Risk & Banned Terms (40s):**  
  Click **Case 4** $\to$ Run Deliberation. Show how an attractive unit price of ₹180 is halted under Step 4 because of the unlimited liability clause, firing `ESCALATE:BANNED_TERM:`.
- **[2:35 – 3:00] Live Case 5 & Conclusion (25s):**  
  Click **Case 5** $\to$ Run Deliberation. Show deal value ₹1.375M exceeding category approval limit ₹600K $\to$ `ESCALATE:OVER_APPROVAL_LIMIT:`. Conclude with **1.00000 public score on Kaggle**, 41/41 passing unit tests, sub-2ms latency, and zero token costs.

---

## 7. Submission Checksum & Verification

- **File Path:** `submission_v4.csv`
- **Total Rows:** Exactly 2,001 lines (1 header `thread_id,label` + 2,000 unique data rows `T10001`..`T12000`)
- **SHA-256 Digest:** `a857a332fc79c9757478cecc313c5265c30235c7d89a6cc0034693311c385d92`
- **Verification Command:**
  ```powershell
  (Get-FileHash submission_v4.csv -Algorithm SHA256).Hash
  ```
