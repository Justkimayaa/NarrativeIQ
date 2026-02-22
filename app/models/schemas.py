from pydantic import BaseModel, Field
from typing import Any, Literal, Optional
from enum import Enum


# ─── Shared ──────────────────────────────────────────────────────────────────

class PersonaEnum(str, Enum):
    technical   = "technical"
    business    = "business"
    finance     = "finance"
    simplified  = "simplified"
    comedian    = "comedian"
    poet        = "poet"


class CreditPackEnum(str, Enum):
    starter   = "starter"
    pro       = "pro"
    unlimited = "unlimited"


# ─── Credits ─────────────────────────────────────────────────────────────────

class CreditsResponse(BaseModel):
    credits: int


class CreateOrderRequest(BaseModel):
    pack: CreditPackEnum


class CreateOrderResponse(BaseModel):
    order_id: str             # Stripe PaymentIntent ID
    client_secret: str        # Frontend uses this to open Stripe UI
    amount: int               # in paise
    currency: str = "INR"
    credits_to_receive: int


class VerifyPaymentRequest(BaseModel):
    stripe_payment_intent_id: str   # e.g. pi_3XXXXXXXXXX


class VerifyPaymentResponse(BaseModel):
    success: bool
    credits_added: int
    new_balance: int


# ─── Enhance ─────────────────────────────────────────────────────────────────

class EnhanceRequest(BaseModel):
    text: str = Field(..., min_length=10, max_length=20000)
    persona: PersonaEnum


class DiffChange(BaseModel):
    type: Literal["added", "removed", "unchanged"]
    content: str


# ─── Mindmap ─────────────────────────────────────────────────────────────────

class MindmapRequest(BaseModel):
    text: str = Field(..., min_length=10, max_length=30000)


class GraphNode(BaseModel):
    id: str
    label: str
    type: Literal["character", "location", "theme", "event", "object"]
    attributes: dict[str, Any] = {}


class GraphEdge(BaseModel):
    source: str
    target: str
    label: str


class MindmapResponse(BaseModel):
    nodes: list[GraphNode]
    edges: list[GraphEdge]
    summary: str
    themes: list[str]
    credits_remaining: int


# ─── Consistency ─────────────────────────────────────────────────────────────

class ConsistencyRequest(BaseModel):
    text: str = Field(..., min_length=10, max_length=30000)


class ConsistencyIssue(BaseModel):
    type: str
    description: str
    severity: Literal["low", "medium", "high"]


class ConsistencyResponse(BaseModel):
    issues: list[ConsistencyIssue]
    score: int = Field(..., ge=0, le=100)
    summary: str
    credits_remaining: int


# ─── Evolution ───────────────────────────────────────────────────────────────

class EvolutionRequest(BaseModel):
    text: str = Field(..., min_length=10, max_length=30000)
    character_name: str = Field(..., min_length=1, max_length=100)


class EvolutionStage(BaseModel):
    stage: int
    trait: str
    evidence: str


class EvolutionResponse(BaseModel):
    character: str
    arc: list[EvolutionStage]
    evolution_type: str
    credits_remaining: int


# ─── Error ───────────────────────────────────────────────────────────────────

class InsufficientCreditsError(BaseModel):
    error: str = "insufficient_credits"
    credits_needed: int
    current_credits: int