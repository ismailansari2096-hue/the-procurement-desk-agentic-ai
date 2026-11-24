# Data Schema & Specification Report

**Date & Time**: 2026-11-23T12:44:30+05:30  
**Status**: BLOCKED PENDING INPUT DATASET ARRIVAL  
**Workspace**: `c:\Users\ismai\AI-POWERED SUPPLIER NEGOTIATION DECISION ENGINE`

---

## 1. Expected Data Schemas

Based on the competition specifications for **"The Procurement Desk — Agents That Negotiate For You"**, the following specifications and formats are established:

### 1.1 Input Negotiation Threads (Test Dataset)
* **File Target**: e.g., `test.csv` (or threads JSON / CSV)
* **Expected Features**:
  * `thread_id`: Unique negotiation thread identifier (e.g., `T10001`)
  * `supplier_id` / Supplier metadata: Vendor identifier or name
  * `category`: Product or service category under negotiation
  * `date` / `timestamp`: Date/time of messages for amendment resolution
  * `messages` / `email_thread`: Complete conversation sequence (multiple messages, quoted history, pricing mentions)

### 1.2 Target Output Specification (`outputs/submission.csv`)
* **File Format**: Standard CSV with header:
  ```csv
  thread_id,label
  ```
* **Label Format**:
  ```
  ACTION:REASON:COUNTER_PRICE
  ```
* **Allowed Actions**:
  - `ACCEPT`: When the supplier's offer complies with acceptable price/terms.
    - Example: `ACCEPT:ACCEPTABLE_PRICE:` (note mandatory trailing colon, empty price).
  - `COUNTER`: When negotiation rules dictate counteroffering.
    - Example: `COUNTER:COUNTER_OFFER:21500` (integer INR price, no commas/decimals).
  - `REJECT`: When negotiation limits or walkaway conditions are breached.
    - Example: `REJECT:ABOVE_WALKAWAY:` (mandatory trailing colon, empty price).
  - `ESCALATE`: When security policy, prompt injection, or contractual exceptions are triggered.
    - Example: `ESCALATE:PROMPT_INJECTION:` (mandatory trailing colon, empty price).

---

## 2. Dataset Quality Gates (To Be Verified Upon Ingestion)

Once the files are placed into `data/raw/` or the workspace root:

1. **Row Count & Uniqueness**:
   - Verify ~2,000 unique thread rows.
   - Assert zero duplicate `thread_id` values.
2. **Missing & Malformed Data**:
   - Identify nulls across timestamps, categories, or email bodies.
3. **Price Parsing Fidelity**:
   - Exact integer INR extraction without rounding corruption.
4. **Amendment Temporal Alignment**:
   - Verify date ranges against effective dates extracted from `amendments.json`.

---

## 3. Next Action
Awaiting user placement of `playbook.zip` and the competition test CSV.
