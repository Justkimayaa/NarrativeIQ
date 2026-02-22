# NarrativeIQ ✍️

> AI-powered writing intelligence — enhance scripts, analyze consistency, track characters, and map narratives.

NarrativeIQ is a full-stack SaaS platform that gives writers, screenwriters, and storytellers a suite of AI tools to craft better narratives. It combines a React + TypeScript frontend with a Python Flask backend and MongoDB for storage.

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
- JWT-based user registration and login (custom HS256 tokens)
- Password hashing with bcrypt
- Profile updates (name, email) with token re-issuance
- Password change with current password verification
- Persistent user accounts in MongoDB

---

### 💳 2. Credit-Based Usage System
- New users receive default credits on signup (configurable via `NEW_USER_CREDITS` env var)
- Credits deducted per feature call with automatic refund on AI failure
- Real-time credit balance tracking
- Feature pricing configured centrally in `FEATURE_PRICING`

---

### ✍️ 3. Persona-Driven Text Enhancement

Rewrites your text in 6 distinct voices:

| Persona | Style |
|---|---|
| Technical | Structured, jargon-aware, logically sequenced |
| Business | Persuasive, executive-ready, results-oriented |
| Finance | Analytical, data-oriented, objective |
| Simplified | Clear enough for a beginner, no jargon |
| Comedian | Witty, punchy, light without losing the message |
| Poet | Lyrical, metaphor-rich, emotionally resonant |

Capabilities: clarity improvement, structural refinement, tone transformation, meaning preservation. Returns enhanced text, word-level diff, similarity score, and a log of key changes with reasons.

---

### 🔍 4. Narrative Consistency Analysis

Detects: character inconsistencies, timeline conflicts, factual contradictions, tone shifts, plot holes, and setting conflicts.

Outputs: issue classification with type, description, excerpt, and severity (low / medium / high), plus an overall consistency score out of 100.

---

### 📊 5. Structure & Clarity Analysis

Evaluates structural quality, clarity, flow coherence, writing strengths, and improvement suggestions. Produces individual scores for structure, clarity, and flow, plus actionable suggestions by category.

---

### 🧠 6. Character Evolution Tracking

Tracks emotional progression, behavioral changes, and narrative arc shape across the full text. Identifies trigger events and outputs a staged arc grounded in direct text evidence, with arc type classification (Hero's Journey, Redemption Arc, Static, etc.).

---

### 🧩 7. Narrative Memory Graph (Mindmap Generation) ⭐

Extracts characters, locations, organizations, themes, and time references from your narrative in a two-pass AI pipeline: entity extraction followed by relationship mapping.

Generates React Flow–compatible graph nodes and edges with relationship types, narrative summary metrics, and entity counts.

---

### 🖼 8. Mindmap Visualization Engine

Converts the extracted graph into a visual PNG image using **NetworkX** for spring layout and **Matplotlib** for rendering. Applies entity-type color coding (characters, locations, organizations, themes) on a dark background. Produces a **downloadable PNG mindmap** with edge labels.

---

### 🧾 9. Explainable AI Modifications

Every enhancement returns: word-level diff computation, similarity scoring, and a reason for each key change. Makes AI decisions transparent and interpretable.

---

### 📚 10. Document Management System

Save, retrieve, and preview documents. Up to 20 most recent documents per user, with content preview (first 200 characters) on the list view.

---

### 📜 11. Enhancement History & Audit Trail

Every operation is logged with: operation type, credits used, persona applied, input text, and output text — last 50 entries per user, accessible from the History page.

---

### 📁 12. File Upload & Text Extraction

Supports PDF, TXT, and Markdown (`.md`) uploads (max 16 MB). Extracts raw text, word count, and character count automatically on upload using **PyPDF2**.

---

### 📖 13. AI Story Completion Engine ⭐

Completes partial stories and scripts with genre-aware continuation. Outputs a full structured story with title, summary, character list, detected genre, word count, and a four-part story structure (setup, conflict, climax, resolution).

Configurable options:

- **Genre:** General, Fantasy, Sci-Fi, Romance, Thriller, Horror, Comedy, Drama
- **Style:** Narrative, Screenplay, First-Person, Third-Person
- **Length:** Short (500–800 words), Medium (1000–1500), Long (2000–3000)

Supports both direct text input and file-based completion. Completed story is auto-saved as a document.

---

### 🧪 14. Deep Consistency Scan

Combines consistency analysis and structural evaluation in a single pass. Returns both full reports plus a combined aggregate score.

---

### 🛠 15. Debug & Health Utilities

- `GET /api/health` — service liveness check
- `GET /api/debug/models` — active model and provider verification

---

## Tech Stack

### Frontend
- **React 18** + **TypeScript** + **Vite**
- **Tailwind CSS** + **shadcn/ui** for components
- **Framer Motion** for animations
- **React Router** for navigation

### Backend
- **Flask** (Python 3.10+) — single-file architecture
- **Flask-CORS** — cross-origin request handling
- **PyJWT** + **bcrypt** — custom JWT auth with secure password hashing
- **MongoDB** + **PyMongo** — database for users, documents, and history
- **NetworkX** + **Matplotlib** — graph layout and mindmap PNG generation
- **PyPDF2** — PDF text extraction

---

## Project Structure

```
backend/
└── app.py               # Entire Flask backend in one file
    ├── Auth routes       # /api/auth/*
    ├── Enhance routes    # /api/enhance/*
    ├── Analyze routes    # /api/analyze/*
    ├── Mindmap routes    # /api/mindmap/*
    ├── Story routes      # /api/story/*
    ├── Credits routes    # /api/credits/*
    └── Upload routes     # /api/upload/*

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
│   │   └── AuthContext.tsx  # Auth state management
│   └── lib/
│       └── api.ts           # All API calls to Flask backend
```

---

## Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+
- A running MongoDB instance ([MongoDB Atlas](https://www.mongodb.com/atlas) or local)
- An AI API key

### Backend Setup

```bash
pip install flask flask-cors pymongo bcrypt pyjwt python-dotenv \
            PyPDF2 networkx matplotlib groq
```

Create a `.env` file:

```env
# MongoDB
MONGODB_URI=mongodb://localhost:27017/narrativeiq

# Auth
SECRET_KEY=your-secret-key-here

# AI
GROQ_API_KEY=your-api-key

# App
NEW_USER_CREDITS=5
```

Run the server:

```bash
python app.py
```

API runs at `http://localhost:5000`

### Frontend Setup

```bash
cd frontend
npm install
```

Create a `.env.local` file:

```env
VITE_API_URL=http://localhost:5000
```

```bash
npm run dev
```

---

## API Overview

All protected endpoints require `Authorization: Bearer <token>`.

```
# Auth
POST /api/auth/register          → register & receive token
POST /api/auth/login             → login & receive token
GET  /api/auth/me                → current user info
PUT  /api/auth/update-profile    → update name / email
PUT  /api/auth/change-password   → change password

# Enhance
POST /api/enhance/persona        → persona-driven rewrite (1 credit)
GET  /api/enhance/personas       → list available personas
GET  /api/enhance/history        → enhancement & analysis history
POST /api/enhance/save           → save document
GET  /api/enhance/documents      → list documents
GET  /api/enhance/documents/:id  → get document

# Analyze
POST /api/analyze/consistency    → consistency check (1 credit)
POST /api/analyze/structure      → structure & clarity (1 credit)
POST /api/analyze/character      → character evolution (1 credit)
POST /api/analyze/deep-scan      → deep scan (2 credits)

# Mindmap
POST /api/mindmap/generate       → graph data (2 credits)
POST /api/mindmap/image          → downloadable PNG (2 credits)

# Story
POST /api/story/complete         → complete story from text (2 credits)
POST /api/story/complete-from-file → complete story from file (2 credits)

# Credits & Upload
GET  /api/credits/balance        → current balance
GET  /api/credits/pricing        → feature pricing list
POST /api/upload/extract         → extract text from PDF/TXT/MD
```

---

## Feature Pricing

| Feature | Credits |
|---|---|
| Text Enhancement (any persona) | 1 |
| Consistency Check | 1 |
| Structure & Clarity Analysis | 1 |
| Character Evolution Tracking | 1 |
| Mindmap Generation | 2 |
| Mindmap PNG Image | 2 |
| Story Completion | 2 |
| Deep Consistency Scan | 2 |

