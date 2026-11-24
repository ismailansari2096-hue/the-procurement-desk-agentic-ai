# Dataset Analysis Report — The Procurement Desk

**Date & Time:** 2026-11-23T12:58:30+05:30  
**Test Dataset:** `data/raw/threads.csv` (2,000 threads)  
**Sample Dataset:** `data/raw/sample_threads.csv` (40 threads)  
**Sample Ground Truth:** `data/raw/sample_answers.csv` (40 labels)  

---

## 1. Schema & Column Specifications

Both `threads.csv` and `sample_threads.csv` share identical schemas:

| Column Name | Data Type | Null Count | Description |
| :--- | :--- | :--- | :--- |
| `thread_id` | String (`T\d{5}`) | 0 (0.0%) | Unique identifier (`T10001` to `T12000` in test, `T00001` to `T00040` in sample) |
| `date` | Date (`YYYY-MM-DD`) | 0 (0.0%) | Date of the latest negotiation turn; used for amendment resolution |
| `supplier` | String | 0 (0.0%) | Supplier organization name (matches `suppliers/*.md`) |
| `category` | String | 0 (0.0%) | Procurement spend category (matches `categories/*.md`) |
| `quantity` | Integer | 0 (0.0%) | Order volume (units, boxes, seats, servers, etc.) |
| `round` | Integer ($r \ge 1$) | 0 (0.0%) | Current negotiation turn index of the supplier's offer |
| `our_last_counter` | Integer / Float | 0 (0.0%) | Acme's counteroffer from round $r-1$ (baseline/reference) |
| `supplier_message` | String (Multilingual text) | 0 (0.0%) | Full email conversation thread (may contain earlier turns and latest message) |

### Integrity Verification:
- **Duplicate IDs:** 0 duplicates found in either dataset.
- **Row Counts:** Exactly 2,000 test threads and exactly 40 sample threads.
- **Missing Values:** No missing fields in metadata columns.

---

## 2. Spend Category & Supplier Coverage in Test Data

All 15 playbook categories and all 35 playbook suppliers appear across the 2,000 test threads:
- **Categories (15):** catering, cleaning, cloud-servers, courier, crm-licenses, design-software, headsets, laptops, led-lighting, mobile-phones, monitors, office-chairs, printer-paper, security-guards, training.
- **Suppliers (35):** Fully mapped to the 35 supplier profiles.
- **Date Range:** Threads span from September 2026 through December 2026, intersecting with all 9 dated amendments.

---

## 3. Email Thread Structure & Parsing Characteristics

Inspection of the `supplier_message` column reveals distinct conversational patterns:

1. **Multi-turn Conversations:**
   - Preceded by explicit delimiter tags:
     `[Earlier message — <Sender>, <YYYY-MM-DD>]`
     `[Earlier message — Acme Procurement]`
     `[Latest message — <Sender>, <YYYY-MM-DD>]`
   - *Rule:* Only the supplier's *current/latest* offer counts for pricing.
2. **Corrections:**
   - E.g., *"CORRECTION — the price in my previous email should read Rs. X, not Y."*
   - Replaces the quoted price with the corrected figure.
3. **Discount on Previous Quote:**
   - E.g., *"We can offer 5% off our previous quote"* $\rightarrow$ applies to the supplier's previous quote within the thread.
4. **Volume / Tiered Pricing:**
   - Multiple tiers listed (e.g. "1-50 units: ₹X; 51-100 units: ₹Y"). The parser must match the thread's `quantity`.
5. **Pack Conversions:**
   - LED lighting (4 fixtures/pack), printer paper (10 reams/box).
6. **Currencies:**
   - Quoted in INR (₹, Rs., INR), USD ($), EUR (€), GBP (£), or unknown currencies (e.g. JPY, SGD $\rightarrow$ trigger `MISSING_INFO`).
