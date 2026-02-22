# NarrativeIQ 

> AI-powered writing intelligence — enhance scripts, analyze consistency, track characters, and map narratives.

NarrativeIQ is a full-stack SaaS platform that gives writers, screenwriters, and storytellers a suite of AI tools to craft better narratives. It combines a React + TypeScript frontend with a Python FastAPI backend, Supabase for auth and storage, and Stripe for payments.

---

## Screenshots

<table>
  <tr>
    <td align="center"><b>Workspace — Persona Enhancement</b></td>
    <td align="center"><b>Narrative Memory Graph (Mindmap)</b></td>
  </tr>
  <tr>
    <td><img src="images/workspace.png" alt="Workspace" width="100%"/></td>
    <td><img src="images/memorymap.png" alt="Mindmap" width="100%"/></td>
  </tr>
  <tr>
    <td align="center"><b>Story Completion</b></td>
    <td align="center"><b>Analysis History</b></td>
  </tr>
  <tr>
    <td><img src="images/storyC.png" alt="Story Completion" width="100%"/></td>
    <td><img src="images/history.png" alt="History" width="100%"/></td>
  </tr>
</table>

---

## Features

### 🔐 1. Authentication & User Management
- JWT-based user registration and login
- Secure token authentication
- Profile updates and password change
- Persistent user accounts via Supabase

---

### 💳 2. Credit-Based Usage System
- New users receive default credits on signup
- Credits deducted atomically per feature call (no race conditions)
- Real-time credit balance shown in the sidebar
- Credit top-up via Stripe payments
- Per-feature pricing configured centrally in `config.py`

---

### ✍️ 3. Persona-Driven Text Enhancement

Rewrites your text in 6 distinct voices:

| Persona | Style |
|---|---|
| Technical | Structured, jargon-aware, logically sequenced |
| Business | Persuasive, executive-ready, results-oriented |
| Finance | Analytical, data-oriented, objective |
| Simplified | Clear enough for a 12-year-old, no jargon |
| Comedian | Witty, punchy, light without losing the message |
| Poet | Lyrical, metaphor-rich, emotionally resonant |

Capabilities: clarity improvement, structural refinement, tone transformation, meaning preservation. Delivered via **SSE streaming** so results appear in real time.

---

### 🔍 4. Narrative Consistency Analysis

Detects: character inconsistencies, timeline conflicts, logical contradictions, tone shifts, setting conflicts, and plot holes.

Outputs: issue classification, severity scoring (low / medium / high), and an overall consistency score out of 100.

---

### 📊 5. Structure & Clarity Analysis

Evaluates structural quality, clarity, flow coherence, writing strengths, and improvement suggestions. Produces individual scores for structure, clarity, and flow.

---

### 🧠 6. Character Evolution Tracking

Tracks emotional progression, behavioral changes, and narrative arc shape across the full text. Identifies trigger events and outputs a staged arc (3–6 stages) grounded in direct text evidence.

Arc types: positive growth, negative descent, flat, cyclical, or complex.

---

### 🧩 7. Narrative Memory Graph (Mindmap Generation) ⭐

Extracts characters, locations, organizations, themes, time references, and relationships from your narrative using a hybrid **spaCy NER + LLM** pipeline.

Generates React Flow–compatible graph nodes and edges with relationship mapping and narrative summary metrics.

---

### 🖼 8. Mindmap Visualization Engine

Converts the extracted graph into a visual image using NetworkX for layout. Applies entity-type color coding (characters, locations, themes, organizations). Produces a **downloadable PNG mindmap**.

---

### 🧾 9. Explainable AI Modifications

Every enhancement includes: change detection, word-level diff computation, similarity scoring, and a reason for each modification. Makes AI decisions transparent and interpretable.

---

### 📚 10. Document Management System

Save, retrieve, and preview documents. Tracks enhancement history per document with full input/output storage.

---

### 📜 11. Enhancement History & Audit Trail

Every operation is logged with: operation type, credits used, persona applied, and input vs. output content — accessible from the History page.

---

### 📁 12. File Upload & Text Extraction

Supports PDF, TXT, and Markdown (`.md`) uploads. Extracts raw text, word count, and character count automatically on upload.

---

### 📖 13. AI Story Completion Engine ⭐

Completes partial stories and scripts with genre-aware continuation. Outputs a structured story arc with character detection.

Configurable options:

- **Genre:** General, Fantasy, Sci-Fi, Romance, Thriller, Horror, Comedy, Drama
- **Style:** Narrative, Screenplay, First-Person, Third-Person
- **Length:** Short, Medium, Long

Supports both direct text input and file-based completion.

---

### 🧪 14. Deep Consistency Scan

Combines consistency analysis and structural evaluation in a single pass. Returns an aggregate score and unified issue report.

---

### 🛠 15. Debug & Health Utilities

- `GET /` — service liveness check
- `GET /health` — environment and config status
- Active model verification via LiteLLM

---

## Tech Stack

### Frontend
- **React 18** + **TypeScript** + **Vite**
- **Tailwind CSS** + **shadcn/ui** for components
- **Framer Motion** for animations
- **React Router** for navigation
- **Supabase JS** for auth (JWT)
- **Stripe.js** for payments

### Backend
- **FastAPI** (Python 3.10+) — async, fully typed
- **LiteLLM** — unified LLM gateway (provider-agnostic)
- **spaCy** — local NER for entity extraction in the mindmap pipeline
- **Supabase** — PostgreSQL database + Auth + Row Level Security
- **Stripe** — payment processing with webhook support

---

## Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI app, CORS, router registration
│   ├── config.py            # Environment settings, credit costs, pricing
│   ├── middleware/
│   │   └── auth.py          # Supabase JWT verification dependency
│   ├── db/
│   │   └── supabase.py      # Credit ops, analysis logging, Supabase client
│   ├── models/
│   │   └── schemas.py       # Pydantic request/response models
│   ├── routers/
│   │   ├── enhance.py       # POST /enhance — streaming SSE persona rewrite
│   │   ├── consistency.py   # POST /consistency — plot/timeline analysis
│   │   ├── evolution.py     # POST /evolution — character arc tracking
│   │   ├── mindmap.py       # POST /mindmap — entity graph generation
│   │   └── credits.py       # GET/POST /credits — balance, Stripe, webhooks
│   └── services/
│       ├── llm.py           # LLM calls (enhance, stream, generic run_llm)
│       ├── graph.py         # Mindmap pipeline: spaCy → LLM → graph
│       ├── nlp.py           # spaCy NER + heuristic theme extraction
│       └── diff.py          # Word-level diff for enhance results

frontend/
├── src/
│   ├── pages/
│   │   ├── Index.tsx        # Landing page with feature cards
│   │   ├── Dashboard.tsx    # Main workspace
│   │   ├── Auth.tsx         # Login / signup
│   │   └── Credits.tsx      # Credit purchase page
│   ├── components/
│   │   ├── DiffView.tsx     # Highlighted before/after diff
│   │   └── AnalysisPanel.tsx
│   ├── contexts/
│   │   └── AuthContext.tsx  # Supabase session + user state
│   └── lib/
│       └── api.ts           # All API calls to FastAPI backend
```

---

## Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+
- A [Supabase](https://supabase.com) project
- A [Stripe](https://stripe.com) account

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

Create a `.env` file:

```env
# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your-service-role-key

# LLM
LLM_PROVIDER=gemini/gemini-1.5-flash
LLM_API_KEY=your-api-key

# Stripe
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# App
FRONTEND_URL=http://localhost:5173
APP_ENV=development
```

Run the server:

```bash
uvicorn app.main:app --reload
```

API docs available at `http://localhost:8000/docs`

### Frontend Setup

```bash
cd frontend
npm install
```

Create a `.env.local` file:

```env
VITE_API_URL=http://localhost:8000
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key
VITE_STRIPE_PUBLISHABLE_KEY=pk_test_...
```

```bash
npm run dev
```

---


---

## Credit Packs

| Pack | Credits | Price |
|---|---|---|
| Starter | 20 | ₹99 |
| Pro | 60 | ₹249 |
| Unlimited | 150 | ₹499 |

---

## API Overview

All endpoints require a `Authorization: Bearer <supabase_jwt>` header.

```
GET  /credits                    → current balance
POST /credits/create-order       → create Stripe PaymentIntent
POST /credits/verify-payment     → verify & credit after payment
POST /credits/webhook            → Stripe webhook handler

POST /enhance                    → persona rewrite (SSE streaming)
POST /consistency                → consistency analysis
POST /evolution                  → character arc tracking
POST /mindmap                    → narrative knowledge graph
```

---

