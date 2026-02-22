import json
from fastapi import APIRouter, Depends, HTTPException, status

from app.middleware.auth import get_current_user
from app.db.supabase import deduct_credits, get_user_credits, log_analysis, add_credits
from app.config import settings
from app.models.schemas import ConsistencyRequest, ConsistencyResponse
from app.services.llm import run_llm

router = APIRouter()

COST = settings.CREDIT_COST["consistency"]  # 2 credits

SYSTEM_PROMPT = """You are a narrative consistency analysis engine.
Analyze the provided text for inconsistencies, plot gaps, and continuity errors.

Return ONLY valid JSON:
{
  "issues": [
    {
      "type": "character_inconsistency | plot_gap | timeline_error | tone_shift | factual_error | continuity_error",
      "description": "Clear description of the issue",
      "severity": "low | medium | high"
    }
  ],
  "score": <integer 0-100, where 100 = perfectly consistent>,
  "summary": "2-3 sentence overall assessment"
}

Be thorough. Look for:
- Characters whose traits, ages, or backgrounds change without explanation
- Events that contradict earlier established facts
- Missing transitions or unexplained jumps
- Tone or style shifts that feel unintentional
- Timeline inconsistencies
"""


@router.post("", response_model=ConsistencyResponse)
async def consistency(
    body: ConsistencyRequest,
    user=Depends(get_current_user),
):
    """
    Deep consistency scan. Detects character, plot, timeline, and tone issues.
    Costs 2 credits.
    """
    user_id = user["id"]

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
        result_str = await run_llm(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=f"Analyze this text for consistency issues:\n\n{body.text}",
            json_mode=True,
        )
        result = json.loads(result_str)
    except Exception as e:
        await add_credits(user_id, COST)
        raise HTTPException(status_code=500, detail=f"Consistency scan failed: {str(e)}")

    credits_remaining = await get_user_credits(user_id)

    await log_analysis(
        user_id=user_id,
        feature="consistency",
        input_text=body.text,
        output_json=result,
        credits_used=COST,
    )

    return {
        "issues": result.get("issues", []),
        "score": result.get("score", 50),
        "summary": result.get("summary", ""),
        "credits_remaining": credits_remaining,
    }