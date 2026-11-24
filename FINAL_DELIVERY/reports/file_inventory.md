# File Inventory Report — The Procurement Desk

**Date & Time:** 2026-11-23T12:58:00+05:30  
**Workspace:** `c:\Users\ismai\AI-POWERED SUPPLIER NEGOTIATION DECISION ENGINE`  
**Source Archive:** `data/raw/the-procurement-desk.zip` (136,413 bytes)  

---

## 1. Discovered Competition Files

The complete competition package was located, verified, and safely extracted into `data/raw/` and `data/processed/playbook/`.

### 1.1 Dataset Files (`data/raw/`)
| File Name | Size (Bytes) | Record Count | Description & Purpose |
| :--- | :--- | :--- | :--- |
| `threads.csv` | 647,620 | 2,000 | Competition test dataset containing 2,000 negotiation threads (`T10001` to `T12000`) |
| `sample_submission.csv` | 60,016 | 2,000 | Target submission format template (`thread_id,label`) for threads `T10001` to `T12000` |
| `sample_threads.csv` | 13,334 | 40 | Worked example threads (`T00001` to `T00040`) for policy grounding and regression testing |
| `sample_answers.csv` | 1,389 | 40 | Ground-truth labels for the 40 worked example threads |

### 1.2 Playbook Governance & Policy Documents (`data/processed/playbook/policies/`)
| File Name | Size (Bytes) | Key Content |
| :--- | :--- | :--- |
| `decision-procedure.md` | 2,057 | Master 7-step decision procedure, strict precedence order, and rule hierarchy |
| `approval-limits.md` | 255 | Order value cap ($p \times \text{quantity}$ excl. GST) requiring escalation to approval authority |
| `banned-terms.md` | 517 | Contract terms that must be escalated to Legal: auto-renewal, >30% advance, unlimited liability, exclusivity |
| `concession-schedule.md` | 272 | Concession formula: $L(r) = \text{target} + (\text{walkaway} - \text{target}) \times ((r - 1) / (R - 1))^\beta$ |
| `units-and-currency.md` | 1,202 | Normalization rules: USD (84.5), EUR (91), GBP (106), GST removal, list discounts, tiering, multi-turn quotes |
| `security-policy.md` | 485 | Prompt injection definitions, override claim handling, and legitimate business exception phrasing |
| `output-format.md` | 168 | Strict output format specification: `ACTION:REASON:COUNTER_PRICE` (whole rupees for COUNTER only) |

### 1.3 Category Policies (`data/processed/playbook/categories/` — 15 Categories)
Contains full procurement limits (Target, Walk-away, Rounds $R$, Exponent $\beta$, Approval Limit, GST %, Normalized Unit, and pack conversions):
- `catering.md`, `cleaning.md`, `cloud-servers.md`, `courier.md`, `crm-licenses.md`
- `design-software.md`, `headsets.md`, `laptops.md`, `led-lighting.md`, `mobile-phones.md`
- `monitors.md`, `office-chairs.md`, `printer-paper.md`, `security-guards.md`, `training.md`

### 1.4 Dated Amendments (`data/processed/playbook/amendments/` — 9 Amendments)
- `AMD-01.md`: Courier services walk-away ₹210 (eff. 2026-09-22)
- `AMD-02.md`: Cloud servers walk-away ₹1,19,990 (eff. 2026-11-11)
- `AMD-03.md`: Mobile phones walk-away ₹29,780 (eff. 2026-11-25)
- `AMD-04.md`: Catering target price ₹270 (eff. 2026-09-20)
- `AMD-05.md`: Printer paper walk-away ₹2,780 (eff. 2026-11-06)
- `AMD-06.md`: Headsets approval limit ₹3,20,000 (eff. 2026-11-09)
- `AMD-07.md`: LED lighting walk-away ₹2,360 (eff. 2026-12-05)
- `AMD-08.md`: LED lighting walk-away ₹2,330 (eff. 2026-12-04)
- `AMD-09.md`: Monitors approval limit ₹9,60,000 (eff. 2026-12-14)

### 1.5 Supplier Registry (`data/processed/playbook/suppliers/` — 35 Suppliers)
- **Blacklisted (3)**: GreenLeaf Facility Care, Lumen Workspace, Orbit Electronics.
- **Probation (4)**: Banyan Guarding, Jade Express, Vertex Mobile, Zephyr SaaS.
- **Contract Terms (10)**: Custom exchange rates (Arvind, Aster, Falcon, Kestrel) or custom price caps overriding walk-away (Helix, Ivory Events, Jupiter, Kite, Monsoon, Xenon).
- **Standard Approved (18)**: Bluepeak, Coastline, Cobalt, Deccan, Dune, Ember, Everbright, Fjord, Garnet, Horizon, Indus, Lotus, Meridian, Nimbus, Northstar, Pinnacle, Quartz, Redwood, Saffron, Tidewater, Umbra, Willow, Yamuna.

### 1.6 Precedents (`data/processed/playbook/precedents/` — 8 Precedents)
- `P-01` to `P-08`: Explicit rulings on ranges (take upper bound), "N free for M paid" deals, contract exchange rates, monthly vs annual subscriptions, auto-renewal escalation, and prompt injection detection.
