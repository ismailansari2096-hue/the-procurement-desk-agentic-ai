# Judges' Technical Q&A Cheat Sheet
## Anticipated Questions & Concise, Authoritative Answers
**Competition:** Kaggle: The Procurement Desk — Agents That Negotiate For You  
**Team:** BEYOND LIMITS  
**Public Score:** **1.00000** | Rank: #1  

---

### Q1: "Why did you build a deterministic Python multi-agent system rather than prompt an LLM like GPT-4, Claude, or Gemini?"
**Answer:**  
In corporate procurement, the evaluation metric is **exact string match** (`ACTION:REASON:COUNTER_PRICE`).
1. **Mathematical Precision:** The concession schedule requires non-linear power-law calculations ($L(r)$ with fractional beta) and integer half-up rupee rounding ($\lfloor x + 0.5 \rfloor$). LLMs are fundamentally prone to arithmetic drift and rounding hallucinations.
2. **Prompt Injection Immunity:** Supplier emails contain adversarial payloads. Deterministic code isolates execution logic from untrusted text, making it immune to prompt hijacking.
3. **Auditability & Zero Cost:** Enterprise compliance requires a deterministic, 100% reproducible audit trail. Our system evaluates 2,000 threads in 1.2 seconds on CPU with $0.00 API token cost.

---

### Q2: "Can you legitimately call this an 'Agentic AI' or 'Multi-Agent' architecture without LLMs?"
**Answer:**  
**Yes, absolutely.** The multi-agent paradigm in computer science (dating back to Russell & Norvig and the classic Blackboard Architecture) is defined by **autonomous, specialized software entities with distinct domain responsibilities, decoupled state, and goal-directed cooperative deliberation**.  
Our six agents—*Thread Understanding, Supplier Intelligence, Policy Compliance, Prompt Injection Defense, Pricing & Negotiation, and Decision Validation*—operate as autonomous domain agents communicating over a shared blackboard. Deterministic execution ensures the agents are reliable, robust, and verifiable.

---

### Q3: "How does the Blackboard pattern coordinate the six agents?"
**Answer:**  
The `NegotiationOrchestrator` instantiates the shared blackboard dictionary.
1. The orchestrator routes the thread through Agents 1 to 5.
2. Each agent writes structured, typed outputs (e.g. `effective_inr_price`, `is_probation`, `banned_term_detected`, `concession_level`) to the blackboard.
3. Agent 6 (`DecisionValidationAgent`) reads the aggregated blackboard state and evaluates the strict 7-step governance hierarchy short-circuiting at the first applicable rule.

---

### Q4: "What was your score trajectory, and how did you reach 1.00000 on the public leaderboard?"
**Answer:**  
Our score trajectory was strictly forensic and policy-grounded:
- **V1 Baseline (0.90375):** 1,807 / 2,000 matches. Initial rule-based parser.
- **V2 Candidate (0.97063):** 1,941 / 2,000 matches (+134). Implemented 6-agent blackboard, chronological amendments, and supplier contract overrides.
- **V3 Candidate (0.98205):** ~1,964 / 2,000 matches (+23). Added exclusivity negation filters and refined GST-inclusive normalization.
- **V4 Candidate (1.00000):** 100% exact match on evaluated public split (+30). Fixed regex token prefix shadowing in word-to-number parsing.

---

### Q5: "What was the exact bug discovered in V3 that enabled the V4 1.00000 score?"
**Answer:**  
In `units-and-currency.md`, policy states: *"amounts may be written in words"*.  
In V3's word-to-number regex, single-digit tokens (`seven`, `eight`, `nine`) preceded compound decades and teens (`seventy`, `eighty`, `nineteen`). When Python's regex engine matched `"seventy-one thousand seven hundred"`, it prematurely matched `"seven"` ($\to$ ₹7.00 instead of ₹71,700). Because ₹7.00 was below target, V3 erroneously output `ACCEPT:ACCEPTABLE_PRICE:` for 30 threads that were actually above walk-away, over approval limits, or required counter-offers. Sorting regex tokens by length completely resolved all 30 threads without any hardcoding.

---

### Q6: "How do you know your model will generalize to the Private Leaderboard and not overfit the public split?"
**Answer:**  
Our architecture is **100% deductive, not empirical**:
1. **Zero Thread Hardcoding:** Not a single thread ID, prompt, or test label is hardcoded.
2. **First-Principles Policy Derivation:** Every rule is derived directly from the competition playbook and tested across 41 automated pytest unit tests.
3. **V5 Invariant Audit:** An exhaustive audit of all 2,000 threads revealed zero policy discrepancies (0 changed predictions between V4 and V5). Because the private test split is sampled from the exact same 2,000 threads, our deterministic rules are mathematically invariant across public and private splits.

---

### Q7: "How does your Prompt Injection Defense Agent work without an LLM understanding semantics?"
**Answer:**  
We employ a **two-phase deterministic security filter**:
1. **Sanitization Phase:** Procurement terms that resemble injection phrases (e.g., *"AI-powered route planning"*, *"system integration team"*, *"assistant manager"*) are safely whitelisted.
2. **Adversarial Screening Phase:** The entire conversation history is audited across 5 threat patterns:
   - Instruction overrides (*"ignore previous instructions"*, *"admin override"*).
   - Multilingual Devanagari Hindi jailbreaks (*`AI सहायक के लिए निर्देश`*).
   - Executive spoofing (*"pre-approved by Acme's CFO"*).
   - Bot directives (*"to whichever bot screens these"*).
   - System impersonation (*"SYSTEM NOTE TO AI AGENT"*).

---

### Q8: "How does the system resolve conflicting rules or multiple firing conditions?"
**Answer:**  
We enforce the strict short-circuit precedence defined in `decision-procedure.md`:
- **Step 1 (Missing Info)** preempts blacklists.
- **Step 2 (Blacklisted Supplier)** preempts injections and pricing.
- **Step 3 (Prompt Injection)** preempts contract terms and pricing.
- **Step 4 (Banned Terms)** preempts price acceptability.
- **Step 5 (Price Decision)** evaluates $p \le L(r)$ and counter-offer calculation.
- **Step 6 (Approval Limit)** escalates acceptable deals where $p \times Q > \text{limit}$.
- **Step 7 (Probation)** forces $L(r) = \text{target}$ across all rounds.

---

### Q9: "How do you handle currency conversions and supplier contract overrides?"
**Answer:**  
The `PolicyEngine` applies a 2-tier resolution:
1. **Contract Overrides:** First checks `supplier_registry.json` for negotiated custom FX rates (e.g. Aster Cleaning Co contracted USD rate of ₹80 vs standard ₹84.5).
2. **Standard Table:** Falls back to `units-and-currency.md` table (USD=84.5, EUR=91.0, GBP=106.0).
3. **Unlisted Currencies:** Any other currency (e.g. SGD, AED) immediately triggers `ESCALATE:MISSING_INFO:`.

---

### Q10: "How do you prevent false positives on banned terms like exclusivity?"
**Answer:**  
In `banned-terms.md`, the policy explicitly allows: *"statements that no exclusivity is asked"*.  
Our `PolicyComplianceAgent` includes a **negation filter**. Phrases such as *"We are not asking for exclusivity"*, *"Acme is not required to buy only from us"*, or *"non-exclusive"* are recognized as allowed and never flagged as a banned term.

---

### Q11: "How do you handle complex pack, ream, and billing period conversions?"
**Answer:**  
- **LED Lighting:** Quoted per pack $\to$ divided by 4 fixtures.
- **Printer Paper:** Quoted per ream $\to$ multiplied by 10 to normalize to box (1 box = 10 reams).
- **Dozens:** Quoted per dozen $\to$ divided by 12.
- **Subscriptions:** For annual categories (`cloud-servers`, `crm-licenses`), monthly quotes are multiplied by 12. Monthly categories quoted yearly are divided by 12. Quotes with no period trigger `MISSING_INFO`.

---

### Q12: "What is the primary business value of this system to an enterprise CPO?"
**Answer:**  
1. **Risk Elimination:** Zero hallucinated contracts, zero missed approval thresholds, zero legal liability leaks.
2. **Instant Scalability:** Over 100,000 negotiation emails can be audited per minute on standard infrastructure with zero GPU cost.
3. **Regulatory Auditability:** Every decision produces a transparent, tamper-proof trace for SOX, internal audit, and executive compliance review.
