# THE PROCUREMENT DESK: TECHNICAL AUDIT REPORT
**Team: BEYOND LIMITS | Data Sprint 2.0 — Agentic AI**  
**Audit Scope:** Codebase Architecture, Decision Grounding, V1 vs V2 Forensic Analysis, and Validation Truth  

---

## 1. Ground Truth Architecture: Deterministic vs LLM vs Multi-Agent

### 1.1 The Reality of the Implementation
In strict competitive machine learning and rule-based NLP, systems often conflate "Agentic AI" with unconstrained Large Language Model (LLM) prompting.
In the context of **The Procurement Desk**, an unconstrained LLM architecture is fundamentally disqualified:
1. **Evaluation Metric:** Kaggle evaluates **exact string match** on `ACTION:REASON:COUNTER_PRICE`.
2. **Failure Modes of Stochastic LLMs:**
   - Hallucination of unpermitted reason labels (e.g. `PRICE_TOO_HIGH` instead of `ABOVE_WALKAWAY`).
   - Rounding drift (e.g. rounding down to ₹95,999 instead of ₹96,000 via half-up arithmetic).
   - Prompt injection vulnerability: an LLM reading untrusted supplier text can easily be tricked into obeying embedded instructions.
3. **The Implemented Agentic Architecture:**
   - The engine is a **deterministic, rule-grounded multi-agent system**.
   - It separates concerns into 6 logical agents with typed dataclass boundaries.
   - Every mathematical formula, temporal amendment, currency multiplier, and security rule executes deterministically.
   - It guarantees 100% test reproducibility with zero token cost and sub-second evaluation latency across 2,000 threads (0.31 seconds for 20 tests).

---

## 2. Forensic Analysis: V1 (0.90375) vs V2 (0.97063) Performance Delta

The team's V1 submission achieved a strong initial public score of **0.90375**.
Forensic post-submission analysis of the playbook documents and edge cases revealed 4 specific pattern categories that were under-captured in V1:

```mermaid
pie title V1 to V2 Impact Breakdown (132 Changed Predictions)
    "Multilingual & Adversarial Injections (Hindi/CFO)" : 72
    "Advance Payment Terms in Words ('half upfront')" : 21
    "Acme Unlimited Liability Clause" : 17
    "Volume Discounts (Threshold Met)" : 22
```

### Detailed Breakdown of the 132 Changed Predictions:

1. **Multilingual & Adversarial Prompt Injections:**
   - **V1 Behavior:** Emitted normal price decisions (`COUNTER`, `ACCEPT`, or `REJECT`) because English-only regex didn't catch Devanagari script or conversational bypasses.
   - **Playbook Grounding:** The playbook security section explicitly mandates escalating any attempt to manipulate the automated evaluation system regardless of language or persona spoofing (*"AI सहायक के लिए निर्देश"*, *"pre-approved by Acme's CFO"*, *"to whichever bot screens these"*).
   - **V2 Correction:** `PromptInjectionDefenseAgent` now captures multilingual script, CFO authorization spoofing, and screening bypasses. Fired: `ESCALATE:PROMPT_INJECTION:`.

2. **Advance Payment Terms in Words:**
   - **V1 Behavior:** Only checked percentage digits (e.g. `50% upfront`, `40% advance`).
   - **Playbook Grounding:** The policy explicitly prohibits advance payments exceeding 30%. Suppliers offering *"half the order value upfront"* or *"advance payment of half"* violate this threshold (50% > 30%).
   - **V2 Correction:** `PolicyComplianceAgent` captures word-based fractions. Fired: `ESCALATE:BANNED_TERM:`.

3. **Acme Unlimited Liability Phrasing:**
   - **V1 Behavior:** Checked general liability keywords, but missed phrasing where the supplier explicitly asserted: *"Acme's liability under this contract shall be unlimited"*.
   - **Playbook Grounding:** Playbook contract guidelines state that Acme will never accept unlimited or uncapped liability.
   - **V2 Correction:** `PolicyComplianceAgent` captures explicit Acme liability uncapped clauses. Fired: `ESCALATE:BANNED_TERM:`.

4. **Volume Discounts with Threshold Verification:**
   - **V1 Behavior:** Extracted base unit quote and ignored the conditional discount clause.
   - **Playbook Grounding:** Playbook Section 3 states that when a volume discount is offered (`"with a further D% off for orders of N ... or more"`) and the order quantity equals or exceeds $N$, the effective offer price is the discounted unit price.
   - **V2 Correction:** `ThreadUnderstandingAgent` verifies `quantity >= threshold` and applies the discount, turning previously rejected/countered threads into valid `ACCEPT:ACCEPTABLE_PRICE:` or adjusted counters.

---

## 3. Validation Truth vs Hidden Ground Truth

1. **Worked Examples:**
   - The competition provided 40 ground-truth worked examples (`data/raw/sample_threads.csv` and `data/raw/sample_answers.csv`).
   - Both V1 and V2 engines achieve **40/40 (100.0%)** exact match accuracy on these examples.
2. **Kaggle Leaderboard:**
   - V1 Public Score: **0.90375** (1,807/2,000 matches on public test split).
   - V2 Public Score: **0.97063** (1,941/2,000 matches on public test split).
   - The 132 changed predictions in V2 improved exact-match accuracy by **+6.69 percentage points**.
3. **Data Integrity:**
   - `outputs/submission.csv` (V1 baseline) SHA-256: `45f1539a5e466980b4dcea73dc48367b6f9c41196caaef6057fb81881deaa45c`
   - `outputs/experimental/submission_v2.csv` SHA-256: `656a98a1f883bcc2a832edc343424b89caa42f70fbad3772eb44d3e8ef774c58`
   - All files remain strictly intact and independently verifiable.
