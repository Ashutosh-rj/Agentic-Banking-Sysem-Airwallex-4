# KAIZEN FinTech

> **"Every Payment Accounted For. Every Decision Explained."**

**KAIZEN FinTech** is an agentic treasury operations command center and payment reliability platform. It detects payment incidents, investigates ambiguous transaction states (e.g. gateway timeouts), reconciles multi-currency bank ledgers, enforces strict internal controls to prevent duplicate transfers, and generates an auditable, explainable trail of every operational decision.

---

## 1. System Architecture

```
                    ┌─────────────────────────────────────────┐
                    │          Frontend (React + Vite)        │
                    │   Tailwind CSS • TanStack Query • Zod   │
                    └────────────────────┬────────────────────┘
                                         │ JSON API (HTTP/1.1)
                                         ▼
                    ┌─────────────────────────────────────────┐
                    │        Backend (FastAPI + Python)       │
                    │   Pydantic v2 • Deterministic Agents    │
                    └──────┬─────────────┬─────────────┬──────┘
                           │             │             │
              ┌────────────▼───┐  ┌──────▼──────┐  ┌───▼────────────┐
              │ SQLite / Async │  │ 7-Stage AI  │  │ Rails Adapters │
              │   SQLAlchemy   │  │   Pipeline  │  │ Airwallex / UK │
              │   Ledger DB    │  │  Workspace  │  │ Open Banking   │
              └────────────────┘  └─────────────┘  └────────────────┘
```

---

## 2. Key Capabilities & The 6 MBA Business Principles

1. **Treasury & Cash Management**:
   - Precise decimal arithmetic across segregated operating accounts (USD, EUR, GBP, SGD).
   - Real-time available liquidity = *Confirmed balance minus active reservations*.
2. **Payment Reconciliation**:
   - Multi-parameter matching algorithm evaluating UETR references, exact amounts, currency, and timestamps.
   - Categorization into Exact Matches (99%+), Probable Matches (60-98%), and Unmatched Exceptions with operator sign-off.
3. **Risk Management & Internal Controls**:
   - Strict payment state machine: `CREATED → VALIDATING → SUBMITTED → PENDING → SUCCEEDED / FAILED / UNKNOWN / REQUIRES_REVIEW`.
   - Automated duplicate protection blocking identical transfers to the same beneficiary within 24 hours.
   - Enforced 4-eyes approval for transfers exceeding $100,000 USD.
4. **Working Capital Management**:
   - Supplier payment obligations ranked by contractual due date and vendor criticality.
5. **Operations Management & SLA Prioritization**:
   - Automated countdown clocks and escalation rules before deadlines incur supplier disruption penalties.
6. **Cost-Benefit & Operational ROI**:
   - Quantified calculations of prevented duplicate exposure ($125,000 USD), operator hours saved, and automation ROI.

---

## 3. The 7-Stage Agentic Investigation Pipeline

When an ambiguous payment outcome occurs (e.g. gateway timeout), the transaction is flagged and processed through a deterministic multi-agent pipeline:

1. **Incident Intake Agent**: Validates incident payload, classifies category, and assigns baseline SLA countdown.
2. **Payment Investigation Agent**: Audits state machine transitions, gateway response logs, and idempotency locks.
3. **Reconciliation & Risk Agent**: Cross-references internal ledger entries against bank statement records.
4. **Root Cause Analysis Agent**: Performs deterministic heuristic anomaly detection and classifies failure etiology.
5. **Treasury Decision Agent**: Evaluates available liquidity headroom, reserve deductions, and cash hold policies.
6. **Action Planning & Escalation Agent**: Determines safe retry feasibility and requires dual-operator authorization.
7. **Business Impact Agent**: Quantifies financial exposure prevented and calculates operational time saved.

*The agentic pipeline is fully deterministic and requires zero external LLM API keys to run reliably in demo/sandbox mode.*

---

## 4. Demo Accounts & Personas

Four pre-seeded enterprise accounts are available for local evaluation:

| Persona | Name | Role | Email | Password |
|---|---|---|---|---|
| **Treasury Manager** | Marcus Wells | `treasury_manager` | `treasury@kaizen.dev` | `Demo1234!` |
| **Administrator** | Sarah Chen | `admin` | `admin@kaizen.dev` | `Demo1234!` |
| **Payment Ops Analyst** | Priya Patel | `payment_ops` | `ops@kaizen.dev` | `Demo1234!` |
| **Auditor** | James Rodriguez | `auditor` | `auditor@kaizen.dev` | `Demo1234!` |

*(A 1-click Quick Persona Switcher is accessible directly on the Login screen and top navigation bar).*

---

## 5. Quickstart & Local Run Commands

### Prerequisites
- Python 3.11+
- Node.js 20+ & npm

### Backend Setup
```bash
cd backend

# Create virtual environment & install dependencies
python -m venv .venv
source .venv/bin/activate       # On Windows: .venv\Scripts\activate
pip install -e .

# Seed demo database (runs automatically on clean launch in DEMO_MODE)
python seed.py

# Start the FastAPI server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
- API Docs: `http://localhost:8000/docs`
- Health Probe: `http://localhost:8000/health/ready`

### Frontend Setup
```bash
cd frontend

# Install packages
npm install --legacy-peer-deps

# Start Vite development server
npm run dev
```
- Web Application: `http://localhost:5173`

---

## 6. Docker Compose Deployment

To run both services in containerized mode:
```bash
docker-compose up --build
```
- Frontend: `http://localhost:80` (or `http://localhost:5173`)
- Backend API: `http://localhost:8000`

---

## 7. Automated Test Suite

To run the backend integration test suite:
```bash
cd backend
pytest tests/test_core.py -v
```
All 9 core end-to-end integration tests verify:
- Health and readiness endpoints
- Authentication and role tokens
- Real-time dashboard KPI summaries
- Payment state transitions and safe retry controls
- 7-stage AI investigation pipeline execution
- Multi-currency treasury positions
- Duplicate payment risk detection
- Immutable audit trail generation and CSV export
- Gateway integration connection tests

To verify the frontend production build:
```bash
cd frontend
npm run build
```
*(Compiles cleanly with TypeScript strict checks and Vite bundler).*
