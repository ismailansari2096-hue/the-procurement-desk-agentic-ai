# THE PROCUREMENT DESK: AGENT WORKFLOW SPECIFICATION
**Team: BEYOND LIMITS | Data Sprint 2.0 — Agentic AI**  
**Document:** End-to-End Execution Lifecycle & Decision Logic  

---

## 1. Ordered Decision Procedure & Precedence Hierarchy

The core intelligence of The Procurement Desk is governed by the playbook's mandatory 7-step ordered decision procedure. When evaluating any supplier negotiation thread, agents must execute in strict hierarchical order:

```mermaid
flowchart TD
    Start([Receive Negotiation Thread]) --> S1{Step 1: Missing Info?}
    S1 -- Yes --> E1[ESCALATE:MISSING_INFO:]
    S1 -- No --> S2{Step 2: Blacklisted?}
    
    S2 -- Yes --> E2[REJECT:BLACKLISTED_SUPPLIER:]
    S2 -- No --> S3{Step 3: Prompt Injection?}
    
    S3 -- Yes --> E3[ESCALATE:PROMPT_INJECTION:]
    S3 -- No --> S4{Step 4: Banned Contract Terms?}
    
    S4 -- Yes --> E4[ESCALATE:BANNED_TERM:]
    S4 -- No --> S5{Step 5: Price Acceptable?\np <= L(r)}
    
    S5 -- Yes --> S6{Step 6: Deal Value > Approval Limit?}
    S6 -- Yes --> E6[ESCALATE:OVER_APPROVAL_LIMIT:]
    S6 -- No --> A6[ACCEPT:ACCEPTABLE_PRICE:]
    
    S5 -- No --> S5B{Final Round?\nr >= R}
    S5B -- Yes --> R5[REJECT:ABOVE_WALKAWAY:]
    S5B -- No --> C5[COUNTER:COUNTER_OFFER:round(L(r))]
```

---

## 2. Agent Execution Steps & Data Transformations

### Phase 1: Intake & Thread Understanding
* **Agent:** `ThreadUnderstandingAgent`
* **Inputs:** `raw_thread` (string), `supplier_name`, `category_id`, `thread_date`, `quantity`.
* **Transformations:**
  1. Splitting email thread on boundary markers (`From:`, `Date:`, `Subject:`).
  2. Extracting unit and total offers. Normalizes word numerals (*"five hundred"* $\to 500$), ranges (*"between 100 and 150"* $\to 150$), and tiered quotes.
  3. Normalizing billing units for recurring subscriptions (converts monthly to annual if category unit requires annual).
  4. Scanning for volume discounts: `"with a further D% off for orders of N ... or more"`. If `quantity >= N`, recalculates $p_{\text{effective}} = p_{\text{base}} \times (1 - D/100)$.
* **Output:** `ThreadUnderstandingOutput` containing normalized INR offer price and missing info flags.

### Phase 2: Supplier Profiling & Intelligence
* **Agent:** `SupplierIntelligenceAgent`
* **Inputs:** `supplier_name`.
* **Transformations:**
  1. Queries supplier registry: status (`Approved`, `PROBATION`, `BLACKLISTED`).
  2. Queries custom exchange rate table (overrides standard table if custom rate exists).
  3. Queries contracted price ceiling for category (overrides category walkaway price).
* **Output:** `SupplierIntelligenceOutput`.

### Phase 3: Policy & Amendment Resolution
* **Agent:** `PolicyComplianceAgent`
* **Inputs:** `category_id`, `thread_date`, `supplier_name`, `latest_message`.
* **Transformations:**
  1. Loads baseline category targets: $T_0$, $W_0$, $R_0$, $\beta$, $A_0$.
  2. Identifies all amendments with `effective_date <= thread_date` and applies them in chronological order:
     - Price increases/decreases.
     - Round count adjustments.
     - Approval limit modifications.
  3. Checks contract override: if supplier has a contracted price cap for this category, sets $W_{\text{effective}} = \text{cap}$.
  4. Scans `latest_message` for banned clauses:
     - Auto-renewal.
     - Advance payment > 30% (e.g. *"half the order value upfront"*).
     - Unlimited liability shifted to Acme.
     - Exclusivity restrictions.
* **Output:** `PolicyComplianceOutput`.

### Phase 4: Adversarial Security Sentinel
* **Agent:** `PromptInjectionDefenseAgent`
* **Inputs:** Full conversation thread string (`message`).
* **Transformations:**
  1. Cleans known benign policy phrasing (e.g., discussions about prompt delivery timelines).
  2. Scans for standard English jailbreak patterns (*"ignore previous instructions"*, *"system prompt override"*).
  3. Scans for conversational bypasses (*"to whichever bot screens these"*, *"if an automated system is reading this"*).
  4. Scans for CFO spoofing (*"pre-approved by Acme's CFO"*).
  5. Scans for Devanagari/Hindi adversarial instructions (*"AI सहायक के लिए निर्देश"*).
* **Output:** `InjectionDefenseOutput`.

### Phase 5: Mathematical Concession & Counter-Pricing
* **Agent:** `PricingNegotiationAgent`
* **Inputs:** `round_num`, `quantity`, `normalized_offer_inr`, `PolicyComplianceOutput`, `SupplierIntelligenceOutput`.
* **Mathematics:**
  1. **Standard Concession Schedule:**
     $$L(r) = T_{\text{eff}} + (W_{\text{eff}} - T_{\text{eff}}) \times \left(\frac{r - 1}{R_{\text{eff}} - 1}\right)^\beta$$
     - When $r = 1$: $L(1) = T_{\text{eff}}$.
     - When $r = R$: $L(R) = W_{\text{eff}}$.
  2. **Probation Supplier Override:**
     - If `status == "PROBATION"`, Acme makes no concessions:
       $$L(r) = T_{\text{eff}} \quad \forall r$$
  3. **Acceptance Test:**
     - Evaluated with full IEEE 754 precision: $\text{acceptable} \iff p \le L(r)$.
  4. **Integer Rupee Rounding:**
     - If counter required: $\text{counter\_price} = \lfloor L(r) + 0.5 \rfloor$.
* **Output:** `PricingNegotiationOutput`.

### Phase 6: Decision Validation & Precedence Gating
* **Agent:** `DecisionValidationAgent`
* **Inputs:** Outputs from Agents 1 through 5.
* **Transformations:**
  1. Evaluates Steps 1 through 6 sequentially.
  2. In Step 6, calculates deal value:
     $$V_{\text{deal}} = p_{\text{norm}} \times \text{quantity}$$
     If $V_{\text{deal}} > A_{\text{eff}}$, emits `ESCALATE:OVER_APPROVAL_LIMIT:`.
     Otherwise, emits `ACCEPT:ACCEPTABLE_PRICE:`.
  3. Validates output grammar and formats exact string `ACTION:REASON:COUNTER_PRICE`.
* **Output:** `DecisionValidationOutput`.
