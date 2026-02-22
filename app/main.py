from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from app.config import settings

# Routers
from app.routers import credits, enhance, mindmap, consistency, evolution

security = HTTPBearer()

app = FastAPI(
    title="NarrativeIQ API",
    description="AI-powered narrative intelligence platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    swagger_ui_parameters={"persistAuthorization": True},
)

# ─── CORS ────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.FRONTEND_URL,
        "http://localhost:3000",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Routers ─────────────────────────────────────────────────────────────────
app.include_router(credits.router,     prefix="/credits",     tags=["Credits & Payments"])
app.include_router(enhance.router,     prefix="/enhance",     tags=["Enhance"])
app.include_router(mindmap.router,     prefix="/mindmap",     tags=["Mindmap"])
app.include_router(consistency.router, prefix="/consistency", tags=["Consistency"])
app.include_router(evolution.router,   prefix="/evolution",   tags=["Evolution"])


# ─── Health ──────────────────────────────────────────────────────────────────
@app.get("/", tags=["Health"])
async def root():
    return {"status": "NarrativeIQ backend is live 🚀"}

@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok", "env": settings.APP_ENV}