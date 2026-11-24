# THE PROCUREMENT DESK: INTERACTIVE DEMO USER GUIDE
**Team: BEYOND LIMITS | Data Sprint 2.0 — Agentic AI**  
**Document:** Operator Manual, Architecture & Usage Guide for Demo UI  

---

## 1. Overview & Launch Instructions

The Procurement Desk Interactive Demo provides both a **modern Web UI** and a **CLI terminal inspection tool** to demonstrate the multi-agent deliberation process in real-time.

### 1.1 Web UI Launch
To start the web application (using Python's built-in `http.server` with zero external heavy dependencies):
```bash
python demo/interactive_demo.py --port 8080
```
Open your browser and navigate to:
```text
http://localhost:8080/
```

### 1.2 CLI Terminal Launch
To run in terminal interactive mode:
```bash
python demo/interactive_demo.py --cli
```

---

## 2. Interactive Features & Layout

The Web UI features a dark executive design with real-time feedback:

1. **Top Header & Status:** Shows the active model (`V4 Model • Kaggle Public Score: 1.00000 | Public Leaderboard Score — Private Score Pending`) and team attribution (`BEYOND LIMITS`).
2. **Pre-Loaded Test Cases:** 5 one-click realistic procurement scenarios covering all primary decision paths. Clicking any pill populates the form and instantly triggers multi-agent deliberation.
3. **Editable Negotiation Thread Form:** Allows modifying `Thread ID`, `Date`, `Category ID`, `Supplier Name`, `Quantity`, `Round`, and the full email body text.
4. **Hero Decision Banner:** Displays the final competition string:
   - Green badge for `ACCEPT`
   - Blue badge for `COUNTER`
   - Red badge for `REJECT`
   - Amber badge for `ESCALATE`
5. **The 6 Logical Agent Cards:**
   - **Thread Understanding:** Displays extracted unit price, currency, quantity, volume discount calculations, and missing info flags.
   - **Supplier Intelligence:** Displays supplier registration status (`Approved`, `PROBATION`, `BLACKLISTED`), price caps, and FX rates.
   - **Policy Compliance:** Displays category baseline target/walkaway, max rounds, active amendments, and banned terms audit.
   - **Prompt Injection Defense:** Displays real-time security scanning, attack categorization, and audit log.
   - **Pricing & Negotiation:** Displays mathematical concession curve $L(r)$, acceptability test, counter-offer rupee amount, and deal value vs. approval limit.
   - **Decision Validation:** Displays the triggered procedure step (Steps 1–6), precedence reason, and grammar validation confirmation.

---

## 3. Walkthrough of the 5 Pre-Loaded Test Cases

| Case ID | Title | Scenario | Triggered Step | Final Label |
| :--- | :--- | :--- | :--- | :--- |
| **Case 1** | Standard Counter-Offer | Round 1 negotiation where supplier quote (₹112,000) exceeds target (₹96,000). System computes exact integer counter. | Step 5 (Price Decision) | `COUNTER:COUNTER_OFFER:96000` |
| **Case 2** | Volume Discount Applied | Supplier quotes ₹310/meal with 10% discount for orders $\ge 500$. Order qty is 600, bringing price to ₹279 (below target ₹280). | Step 6 (Approval Check) | `ACCEPT:ACCEPTABLE_PRICE:` |
| **Case 3** | Multilingual Prompt Injection | Adversarial supplier embeds Hindi system instructions attempting to hijack the AI decision agent. | Step 3 (Prompt Injection) | `ESCALATE:PROMPT_INJECTION:` |
| **Case 4** | Contract Risk - Banned Clause | Supplier attempts to introduce an unacceptable legal clause shifting unlimited liability onto Acme. | Step 4 (Banned Terms) | `ESCALATE:BANNED_TERM:` |
| **Case 5** | Escalation - Over Approval Limit | Per-unit price is acceptable (₹275 $\le$ ₹280 target), but total deal value (₹1,375,000) exceeds category approval limit (₹600,000). | Step 6 (Approval Limit) | `ESCALATE:OVER_APPROVAL_LIMIT:` |
