# THE PROCUREMENT DESK: JUDGES' TECHNICAL Q&A
**Team:** BEYOND LIMITS  
**Competition:** Kaggle: The Procurement Desk — Agents That Negotiate For You  
**Public Score:** `0.97063` (Submission V2) | Baseline: `0.90375` (Submission V1)  

---

## 1. Architectural Philosophy: Why Deterministic Agents?

### Question:
**"Why did you choose a deterministic, rule-grounded multi-agent architecture instead of an end-to-end Large Language Model (like GPT-4 or Gemini)?"**

### Answer:
1. **The Evaluation Metric is Exact String Match:**  
   Kaggle evaluates exact equality on `ACTION:REASON:COUNTER_PRICE`. A single invented reason label (e.g., `REJECT:PRICE_TOO_HIGH` instead of `REJECT:ABOVE_WALKAWAY`) or a 1-rupee rounding variance yields a score of 0. Stochastic LLMs exhibit token probability drift, causing unacceptable error rates.
2. **Mathematical Precision & Rounding Rules:**  
   The playbook specifies integer half-up rupee rounding ($\lfloor x + 0.5 \rfloor$), non-linear concession curves ($L(r)$ with fractional exponent $\beta$), currency conversions, and volume discount thresholds. Neural networks are fundamentally unreliable at multi-step integer arithmetic; deterministic Python code guarantees zero numerical error.
3. **Prompt Injection Immunity:**  
   Supplier emails in this competition contain adversarial prompt injections designed to hijack LLM system prompts. A purely deterministic pipeline with dedicated security filtering isolates code execution from text prompt manipulation.
4. **Latency and Compute Efficiency:**  
   Our entire agentic engine evaluates all 2,000 official threads in under 2 seconds (0.30s for 21 comprehensive unit tests) with zero GPU cost and zero API token dependencies.

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

## 3. Pricing Mechanics: How are Prices and Concession Schedules Calculated?

### Question:
**"Walk us through the exact pricing mathematics, currency conversion, and volume discount logic."**

### Answer:
1. **Currency Normalization:**  
   Supplier quotes in foreign currencies (USD, EUR, GBP) are converted to INR excl. GST using contracted custom exchange rates if specified in `supplier_registry.json`, or the standard table (USD=84.5, EUR=91.0, GBP=106.0). Unlisted currencies trigger `MISSING_INFO`.
2. **Volume Discounts:**  
   When a quote specifies `"with a further D% off for orders of N or more"` and the thread order quantity $Q \ge N$, our `ThreadUnderstandingAgent` discounts the unit price: $p_{\text{effective}} = p_{\text{base}} \times (1 - D/100)$.
3. **Concession Schedule Formula:**  
   $$L(r) = T + (W - T) \times \left(\frac{r - 1}{R - 1}\right)^\beta$$
   Where $T$ is target price, $W$ is walkaway price, $R$ is maximum negotiation rounds, and $\beta$ is category concession curvature (e.g., $\beta = 1.0$ linear, $\beta = 2.0$ quadratic, $\beta = 3.0$ aggressive back-loaded concession).
4. **Price Comparison & Counter-Offer Rounding:**  
   The decision whether $p \le L(r)$ is evaluated with full IEEE 754 float precision. If a counter-offer is required, it is rounded to the nearest integer rupee using half-up arithmetic:
   $$\text{counter} = \lfloor L(r) + 0.5 \rfloor$$

---

## 4. Security Engineering: How is Prompt Injection Detected?

### Question:
**"How does your Prompt Injection Defense Agent differentiate between an actual attack and legitimate procurement correspondence?"**

### Answer:
Our `PromptInjectionDefenseAgent` uses a two-stage filter:
1. **Benign Exception Whitelist:**  
   Procurement threads frequently contain phrases like *"prompt delivery"* or *"system configuration"*. We first sanitize known false-positive phrases so legitimate business terms are not flagged.
2. **Adversarial Pattern Screening:**  
   The remaining sanitized text is screened for five distinct threat categories:
   - **Instruction Overrides:** *"ignore previous instructions"*, *"disregard system constraints"*.
   - **Multilingual Attacks:** Devanagari script attacks such as *"AI सहायक के लिए निर्देश"* (*"instructions to AI assistant"*).
   - **Executive Persona Spoofing:** False authorization claims such as *"pre-approved by Acme's CFO"*.
   - **Bot Bypasses:** Automated screening directives such as *"to whichever bot screens these"* or *"if an automated system is reading this email"*.
   - **System Impersonation:** *"SYSTEM NOTE TO AI AGENT"*.
3. **Full-Thread Scope:**  
   Per security guidelines, prompt injection is audited across the **entire thread history** (earlier messages and latest message), unlike contract terms which apply only to the latest counter-offer.

---

## 5. Kaggle Score & V2 Reproduction: How was 0.97063 Achieved?

### Question:
**"What explains the performance jump from V1 (0.90375) to V2 (0.97063), and how do we know it is reproducible?"**

### Answer:
1. **Forensic Analysis of the 132 Changed Rows:**  
   Our post-submission audit of V1 revealed 4 specific playbook clauses that were under-captured:
   - **72 threads:** Multilingual (Devanagari) and CFO-spoofing prompt injections previously treated as normal quotes $\to$ corrected to `ESCALATE:PROMPT_INJECTION:`.
   - **21 threads:** Advance payment terms stated in words (*"half the order value upfront"*) $\to$ corrected to `ESCALATE:BANNED_TERM:`.
   - **17 threads:** Explicit Acme unlimited liability clauses $\to$ corrected to `ESCALATE:BANNED_TERM:`.
   - **22 threads:** Volume discount clauses where $Q \ge N$ brought the price below target $\to$ corrected to `ACCEPT:ACCEPTABLE_PRICE:` or adjusted counters.
2. **Exact Reproducibility:**  
   Running `scripts/verify_full_v2_reproduction.py` generates predictions for all 2,000 threads from scratch using our agentic architecture. Comparing the generated output against `submission_v2.csv` reveals:
   - Exact matching rows: **2,000 / 2,000 (100.00%)**.
   - SHA-256: `656a98a1f883bcc2a832edc343424b89caa42f70fbad3772eb44d3e8ef774c58` (Byte-for-byte exact match).
3. **Honest Accuracy Disclosure:**  
   We achieve 100% on the 40 local sample worked examples where ground truth exists. On the hidden Kaggle test split, our verified public score is **0.97063**. We do not claim 100% Kaggle test accuracy because hidden test ground truth is withheld by Kaggle.

---

## 6. Model Breakdown: Which Components Use LLMs vs Python Rules?

### Question:
**"To be completely transparent, which parts of your system use LLMs and which parts use deterministic Python rules?"**

### Answer:
* **Current Competition Engine (V2 - 0.97063 Score):**  
  The current competition engine is **100% deterministic Python rules, regex parsers, and mathematical algorithms**. We deliberately excluded stochastic LLM inference from the core prediction loop to eliminate hallucination risk, prevent prompt injection execution, and guarantee 100% reproducibility.
* **Orchestration Layer:**  
  The orchestration layer (`NegotiationOrchestrator`) is implemented as an asynchronous blackboard pattern with typed Pydantic/dataclass boundaries separating all 6 agents.
* **Future LLM Integration (Roadmap Phase):**  
  As outlined in `reports/DEVELOPMENT_ROADMAP.md`, our post-competition architecture incorporates small, fine-tuned reasoning models (e.g., Gemini 2.5 Flash / Llama-3-8B) exclusively for extracting structured JSON from messy colloquial emails. Crucially, the mathematical pricing, concession calculations, and policy precedence rules will **remain strictly deterministic Python code**.
