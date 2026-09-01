# Order Recon

A full-stack revenue reconciliation dashboard that ingests orders and payments CSVs, runs a deterministic reconciliation engine, and presents discrepancies with AI-powered explanations.

**Live URL:** [https://order-recon.onrender.com](https://order-recon.onrender.com) *(update after deployment)*  
**GitHub:** [https://github.com/Amannsingh02/order-recon](https://github.com/Amannsingh02/order-recon)

---

## Test Credentials

You can sign up at `/register` or use the pre-seeded demo account:

- **Username:** `demo`
- **Password:** `demo1234`

*(Create the demo user after deployment with `python manage.py shell` and `User.objects.create_user(...)`)*

---

## Local Setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL (local or Docker)
- Groq API key (free tier at [console.groq.com](https://console.groq.com/keys))

### 1. Clone and enter the repo

```bash
git clone https://github.com/Amannsingh02/order-recon.git
cd order-recon
```

### 2. Backend setup

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cd ..
cp .env.example .env
# Edit .env and fill in your real values (see .env.example)
```

### 3. Database setup

With Docker (recommended for local dev):

```bash
docker-compose up -d db
```

Or use your own PostgreSQL instance and update `DATABASE_URL` in `.env`.

### 4. Run migrations and start server

```bash
cd backend
source venv/bin/activate
python manage.py migrate
python manage.py runserver
```

Backend runs at `http://localhost:8000`.

### 5. Frontend setup

In a new terminal:

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at `http://localhost:5173` and proxies API calls to `:8000`.

### 6. Using Docker Compose (one command)

```bash
docker-compose up --build
```

This spins up PostgreSQL + Django + Vue with hot reload.

---

## Architecture Overview

```
┌─────────────┐     ┌─────────────────────┐     ┌─────────────────┐
│   Browser   │────▶│  Next.js / Vue SPA  │────▶│  Django REST    │
│             │◀────│  (via WhiteNoise)   │◀────│  API Routes     │
└─────────────┘     └─────────────────────┘     └─────────────────┘
                                                        │
                                                        ▼
                                                  ┌─────────────┐
                                                  │  PostgreSQL │
                                                  │   (Neon)    │
                                                  └─────────────┘
                                                        │
                                                        ▼
                                                  ┌─────────────┐
                                                  │  Groq LLM   │
                                                  │  (backend)    │
                                                  └─────────────┘
```

**Key design choices:**

- **Monorepo:** One Git repository with `backend/` (Django) and `frontend/` (Vue). Easier to deploy as a single unit.
- **WhiteNoise:** Django serves the Vue SPA build directly. No separate frontend server needed in production.
- **Docker multi-stage build:** Stage 1 builds Vue assets, Stage 2 serves them via Django/Gunicorn.
- **JWT Auth:** Stateless tokens via `djangorestframework-simplejwt`. No server-side sessions to manage.
- **Per-user data isolation:** Every query is scoped to `request.user`. Users never see each other’s data.

---

## Reconciliation Logic

### Discrepancy Types

| Type | What it means | Example from data |
|------|---------------|-------------------|
| **Fully Reconciled** | Order and payment agree on reference, amount (within tolerance), and currency. | ORD-1001 ↔ TXN700000 |
| **Amount Mismatch** | Matched by reference, but payment amount ≠ order net amount (outside $0.01 tolerance). | ORD-1903: order says $154.96, payment says $154.97 |
| **Currency Mismatch** | Matched by reference, but currencies differ. | ORD-1602: order is EUR, payment is USD |
| **Missing Payment** | Order exists, no payment found after normalizing reference. | ORD-1076 appears in orders but no matching payment |
| **Orphan Payment** | Payment exists, but references an unknown order ID. | TXN700162 references ORD-1302 which has no order |
| **Duplicate Payment** | Multiple payments for the same order. | ORD-1502 has two identical payments (TXN700169, TXN700170) |
| **Status Mismatch** | Order status conflicts with payment reality. | ORD-1701 is "cancelled" but charged; ORD-2001 is "completed" but payment "failed" |
| **Data Quality Issue** | Duplicate order IDs in the CSV, missing fields, or malformed rows. | ORD-1004 appears twice; ORD-2201 has empty email |

### Matching Rules

1. **Reference normalization:** Order IDs and payment references are matched case-insensitively with whitespace trimmed. `ord-1802` and ` ord-1801 ` in payments normalize to `ORD-1802` and `ORD-1801`.
2. **Amount tolerance:** Payments within **$0.01** of the order `net_amount` are considered matched. This handles rounding differences like ORD-1903 ($154.96 vs $154.97).
3. **Currency exact match:** Currencies must match exactly after normalization. `EUR` vs `USD` is always flagged.
4. **Status hierarchy:** If a record has both an amount mismatch and a status mismatch, the **status mismatch** takes precedence because it indicates a deeper business process failure.

### Why these tolerances?

- **$0.01:** Common in payment processing due to rounding at the gateway. Any larger would hide real errors; any smaller would create false positives.
- **Case-insensitive matching:** Real-world payment exports often have inconsistent casing.
- **Whitespace trimming:** Payment CSVs contain leading/trailing spaces (e.g., ` ord-1801 `).

---

## What We Found in the Data

After running the reconciliation engine on the provided CSVs, here are the real problems:

| Issue | Count | Business Impact |
|-------|-------|-----------------|
| Duplicate order IDs in CSV | 1 (ORD-1004) | Risk of double-shipping or double-charging |
| Orphan payments | 3 (ORD-1301, ORD-1302, ORD-1303) | Money recorded with no corresponding sale — possible fraud or unlinked refunds |
| Currency mismatch | 2 (ORD-1601 EUR↔USD, ORD-1602 EUR↔USD) | Revenue reported in wrong currency; FX risk unaccounted for |
| Amount mismatch | ~5 | Small rounding errors, but ORD-1903 is off by $0.01 and ORD-1702 has partial refund mismatch |
| Status mismatches | 3 | Cancelled/refunded orders still charged; completed orders with failed payments |
| Duplicate payments | 1 (ORD-1502) | Customer may have been double-charged; $128.74 at risk |
| Missing payments | ~3 | Revenue booked but never collected |

**Total money at risk:** ~$2,178 (based on reconciliation output).

This means the store is leaking revenue through uncollected payments, double charges, and currency mismatches. The dashboard lets a revenue manager see exactly which orders need investigation.

---

## LLM Approach

### Model & Provider

- **Provider:** Groq (OpenAI-compatible API)
- **Model:** `openai/gpt-oss-20b` (fast, cost-effective, generous free tier)
- **Base URL:** `https://api.groq.com/openai/v1`

### Temperature: 0.1

I chose **temperature = 0.1** (very low). Reasons:

1. **Determinism:** We want the LLM to explain what *already happened* (a factual discrepancy), not to hallucinate causes. Low temperature keeps outputs focused and consistent.
2. **Structured output:** Lower temperature increases the probability that the model returns valid JSON matching our Pydantic schema.
3. **Consistency:** Interviewers or reviewers clicking "Explain" twice on the same discrepancy should see substantively the same analysis.

### Structured Output with Pydantic Validation

The LLM is asked to return JSON matching a strict Pydantic schema:

```python
class DiscrepancyExplanation(BaseModel):
    discrepancy_type: str
    order_id: Optional[str]
    what_happened: str  # 20-500 chars
    recommended_action: str  # 20-500 chars
    severity: str  # "low" | "medium" | "high"

class LLMExplanationResponse(BaseModel):
    summary: str  # 30-300 chars
    discrepancies: List[DiscrepancyExplanation]  # min 1 item
```

**Why Pydantic?**

- The prompt includes the JSON schema so the model knows the exact expected structure.
- After parsing the response, we validate it with Pydantic. If validation fails (malformed JSON, wrong types, missing fields), we fall back to a plain-text LLM call.
- This means the system never crashes on bad LLM output — it gracefully degrades.

### Prompt Engineering

The prompt is deliberately layered:

1. **Role definition:** "Senior financial operations analyst at an e-commerce company" — sets domain expertise and tone.
2. **Task breakdown:** Explicitly asks for WHAT HAPPENED, CONCRETE ACTIONS, and SEVERITY.
3. **Schema injection:** The JSON schema is appended to the prompt so the model sees the exact field names and constraints.
4. **Constraint:** "Return ONLY valid JSON... Do not add markdown fences" — prevents the model from wrapping output in ```json blocks.
5. **Fallback:** If structured output fails validation, we retry with a simpler plain-text prompt.

### Malformed Response Handling

```
Primary attempt  →  Request JSON + validate with Pydantic
        ↓
If JSONDecodeError or ValidationError:
        ↓
Fallback attempt →  Plain text explanation (no schema constraint)
        ↓
If both fail:
        ↓
Return 503 with error details to frontend
```

---

## Testing

Run backend tests:

```bash
cd backend
source venv/bin/activate
python manage.py test api
```

Tests cover:
- Fully reconciled orders
- Amount mismatches
- Missing payments
- Orphan payments
- Duplicate order detection
- Currency mismatches
- Status mismatches (cancelled with charge, completed with failed payment)
- Duplicate payments

*(Note: Full authenticated API tests would require JWT setup in test client; the test suite focuses on the core deterministic engine logic.)*

---

## What to Improve with More Time

1. **Pagination on discrepancy table:** Currently loads up to 100 rows. For production datasets, implement cursor-based infinite scroll.
2. **Export reports:** Add PDF/CSV export of reconciliation results for sharing with finance teams.
3. **Bulk explain:** Let users select multiple discrepancies and get one combined LLM summary.
4. **Real-time ingestion:** WebSocket or polling for progress bars on large CSV uploads.
5. **Data lineage:** Track which CSV version produced which reconciliation run, so users can compare over time.
6. **Admin analytics:** Aggregate across users to show platform-level revenue leakage trends.

---

## How AI Tools Were Used

This project was built with assistance from **Claude Code** (Anthropic). The tool helped with:

- Scaffolding the Django + Vue monorepo structure
- Writing the reconciliation engine logic based on CSV data inspection
- Drafting the Pydantic schemas and LLM prompts
- CSS/Tailwind styling for the dashboard components
- Docker configuration for local and production builds

I reviewed, modified, and tested every piece of code before committing. The reconciliation rules, tolerance values, and discrepancy classifications are my own decisions based on inspecting the actual data.

---

## Environment Variables

See `.env.example` for all required variables. Never commit real secrets.

```
DATABASE_URL=postgres://user:pass@host:port/dbname
SECRET_KEY=change-me-in-production
DEBUG=False
ALLOWED_HOSTS=your-domain.com
CORS_ALLOWED_ORIGINS=https://your-domain.com
LLM_API_KEY=your-groq-key
LLM_BASE_URL=https://api.groq.com/openai/v1
LLM_MODEL=openai/gpt-oss-20b
LLM_TEMPERATURE=0.1
```
