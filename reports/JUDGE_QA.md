# THE PROCUREMENT DESK: JUDGES' TECHNICAL Q&A
**Team:** BEYOND LIMITS  
**Competition:** Kaggle: The Procurement Desk — Agents That Negotiate For You  
**Public Score:** **1.00000** (Rank #1) | Baseline V1: `0.90375` | V2: `0.97063` | V3: `0.98205`  
**Presentation Date:** 25 November 2026  

---

## 1. Architectural Philosophy: Why Deterministic Agents?

### Question:
**"Why did you choose a deterministic, rule-grounded multi-agent architecture instead of an end-to-end Large Language Model (like GPT-4 or Gemini)?"**

### Answer:
1. **The Evaluation Metric is Exact String Match:**  
   Kaggle evaluates exact equality on `ACTION:REASON:COUNTER_PRICE`. A single invented reason label or a 1-rupee rounding variance yields a score of 0. Stochastic LLMs exhibit token probability drift, causing unacceptable error rates.
2. **Mathematical Precision & Rounding Rules:**  
   The playbook specifies integer half-up rupee rounding ($\lfloor x + 0.5 \rfloor$), non-linear concession curves ($L(r)$ with fractional exponent $\beta$), currency conversions, and volume discount thresholds. Neural networks are fundamentally unreliable at multi-step integer arithmetic; deterministic Python code guarantees zero numerical error.
3. **Prompt Injection Immunity:**  
   Supplier emails in this competition contain adversarial prompt injections designed to hijack LLM system prompts. A purely deterministic pipeline with dedicated security filtering isolates code execution from text prompt manipulation.
4. **Latency and Compute Efficiency:**  
   Our entire agentic engine evaluates all 2,000 official threads in under 1.5 seconds with zero GPU cost and zero API token dependencies.

---

## 2. Policy Precedence: How Does Precedence Gating Work?

### Question:
**"How does your engine enforce policy precedence when multiple conditions are triggered simultaneously?"**

### Answer:
Our **Decision Validation Agent** implements the exact 7-step ordered procedure specified in Acme’s `policies/decision-procedure.md`. Precedence is enforced by strict short-circuit logic:

1. **Step 1: Missing Information:**  
   If the quote lacks required units, currency, or billing period $\to$ `ESCALATE:MISSING_INFO:`.
2. **Step 2: Blacklisted Supplier:**  
   If the supplier registry indicates `BLACKLISTED` $\to$ `REJECT:BLACKLISTED_SUPPLIER:`. (Preempts price decisions).
3. **Step 3: Prompt Injection:**  
   If an adversarial injection is detected anywhere in the thread $\to$ `ESCALATE:PROMPT_INJECTION:`. (Preempts banned terms and pricing).
4. **Step 4: Banned Contract Terms:**  
   If the latest message includes auto-renewal, >30% upfront advance, Acme unlimited liability, or exclusivity $\to$ `ESCALATE:BANNED_TERM:`.
5. **Step 5: Price Acceptability:**  
   Compares normalized INR price $p$ against concession threshold $L(r)$.
   - If $p > L(r)$ and $r \ge R$ $\to$ `REJECT:ABOVE_WALKAWAY:`.
   - If $p > L(r)$ and $r < R$ $\to$ `COUNTER:COUNTER_OFFER:<price>`.
6. **Step 6: Approval Limit:**  
   If $p \le L(r)$, calculates total deal value $V = p \times \text{quantity}$.
   - If $V > \text{approval\_limit}$ $\to$ `ESCALATE:OVER_APPROVAL_LIMIT:`.
   - If $V \le \text{approval\_limit}$ $\to$ `ACCEPT:ACCEPTABLE_PRICE:`.
7. **Step 7: Probation Rules:**  
   For suppliers on probation, $L(r) = \text{target}$ across all rounds.

---

## 3. Score Trajectory & The V4 1.00000 Breakthrough

### Question:
**"What was your score trajectory, and what exact technical defect did you fix to reach 1.00000?"**

### Answer:
- **V1 Baseline (0.90375):** Initial heuristic parser.
- **V2 Candidate (0.97063):** Integrated 6-agent blackboard, chronological amendments, and supplier overrides (+134).
- **V3 Candidate (0.98205):** Added exclusivity negation filters and refined GST-inclusive normalization (+23).
- **V4 Candidate (1.00000):** Fixed regex token prefix shadowing in word-to-number parsing (+30).

**The V4 Breakthrough:**  
In `units-and-currency.md`, policy states: *"amounts may be written in words"*. In V3, single-digit regex tokens (`seven`, `eight`) preceded compound decades and teens (`seventy`, `eighty`). A phrase like `"seventy-one thousand seven hundred"` was prematurely truncated by Python's regex engine to `"seven"` ($\to$ ₹7.00 instead of ₹71,700). Because ₹7.00 was below target, V3 erroneously output `ACCEPT:ACCEPTABLE_PRICE:` for 30 threads that were actually above walk-away, over approval limits, or required counter-offers. Sorting regex tokens by length completely resolved all 30 threads without hardcoding.

---

## 4. Generalization to Private Leaderboard

### Question:
**"How do you know your 1.00000 score will hold on the private leaderboard?"**

### Answer:
Our architecture is **100% deductive, not empirical**:
1. **Zero Thread Hardcoding:** Not a single thread ID, prompt, or test label is hardcoded.
2. **First-Principles Policy Derivation:** Every rule is derived directly from the competition playbook and verified across 41 automated pytest unit tests.
3. **V5 Invariant Audit:** An exhaustive audit across all 2,000 threads revealed zero policy discrepancies (0 changed predictions between V4 and V5). Because the private test split is sampled from the exact same 2,000 threads, our deterministic rules are mathematically invariant across public and private splits.

---

## 5. Security & Prompt Injection Defense

### Question:
**"How does your Prompt Injection Defense Agent work without an LLM?"**

### Answer:
We employ a **two-phase deterministic security filter**:
1. **Sanitization Phase:** Procurement terms that resemble injection phrases (e.g., *"AI-powered route planning"*, *"system integration team"*, *"assistant manager"*) are safely whitelisted.
2. **Adversarial Screening Phase:** The entire conversation history is audited across 5 threat patterns:
   - Instruction overrides (*"ignore previous instructions"*, *"admin override"*).
   - Multilingual Devanagari Hindi jailbreaks (*`AI सहायक के लिए निर्देश`*).
   - Executive spoofing (*"pre-approved by Acme's CFO"*).
   - Bot directives (*"to whichever bot screens these"*).
   - System impersonation (*"SYSTEM NOTE TO AI AGENT"*).
