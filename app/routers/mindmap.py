from fastapi import APIRouter, Depends, HTTPException, status

from app.middleware.auth import get_current_user
from app.db.supabase import deduct_credits, get_user_credits, log_analysis
from app.config import settings
from app.models.schemas import MindmapRequest, MindmapResponse
from app.services.graph import build_graph

router = APIRouter()

COST = settings.CREDIT_COST["mindmap"]  # 2 credits


@router.post("", response_model=MindmapResponse)
async def mindmap(
    body: MindmapRequest,
    user=Depends(get_current_user),
):
    """
    Narrative Memory Graph — entity extraction + relationship mapping.
    Returns React Flow compatible nodes/edges.
    Costs 2 credits.
    """
    user_id = user["id"]

    # 1. Deduct credits atomically
    success = await deduct_credits(user_id, COST)
    if not success:
        current = await get_user_credits(user_id)
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail={
                "error": "insufficient_credits",
                "credits_needed": COST,
                "current_credits": current,
            },
        )

    try:
        # 2. Run the full graph pipeline (spaCy + LLM)
        graph_data = await build_graph(body.text)
    except Exception as e:
        # Refund on failure
        from app.db.supabase import add_credits
        await add_credits(user_id, COST)
        raise HTTPException(status_code=500, detail=f"Mindmap generation failed: {str(e)}")

    credits_remaining = await get_user_credits(user_id)

    # 3. Log
    await log_analysis(
        user_id=user_id,
        feature="mindmap",
        input_text=body.text,
        output_json=graph_data,
        credits_used=COST,
    )

    return {
        **graph_data,
        "credits_remaining": credits_remaining,
    }