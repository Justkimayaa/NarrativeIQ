import json
from fastapi import APIRouter, Depends, HTTPException, status

from app.middleware.auth import get_current_user
from app.db.supabase import deduct_credits, get_user_credits, log_analysis, add_credits
from app.config import settings
from app.models.schemas import EvolutionRequest, EvolutionResponse
from app.services.llm import run_llm

router = APIRouter()

COST = settings.CREDIT_COST["evolution"]  # 2 credits

SYSTEM_PROMPT = """You are a character development analyst.
Track how the specified character evolves throughout the narrative.

Return ONLY valid JSON:
{
  "character": "<character name>",
  "arc": [
    {
      "stage": <integer starting at 1>,
      "trait": "<dominant trait at this stage, 1-3 words>",
      "evidence": "<specific quote or event from the text that shows this trait>"
    }
  ],
  "evolution_type": "positive_growth | negative_descent | flat | cyclical | complex"
}

Guidelines:
- Identify 3-6 distinct stages in the character's journey
- Each stage must be grounded in actual text evidence
- Traits should be vivid and specific (e.g. "Recklessly Brave" not just "Brave")
- evolution_type describes the overall arc shape
"""


@router.post("", response_model=EvolutionResponse)
async def evolution(
    body: EvolutionRequest,
    user=Depends(get_current_user),
):
    """
    Character evolution tracker — maps how a character changes across the narrative.
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
            user_prompt=(
                f"Track the character evolution of '{body.character_name}' "
                f"in the following text:\n\n{body.text}"
            ),
            json_mode=True,
        )
        result = json.loads(result_str)
    except Exception as e:
        await add_credits(user_id, COST)
        raise HTTPException(status_code=500, detail=f"Evolution tracking failed: {str(e)}")

    credits_remaining = await get_user_credits(user_id)

    await log_analysis(
        user_id=user_id,
        feature="evolution",
        input_text=body.text,
        output_json=result,
        credits_used=COST,
    )

    return {
        "character": result.get("character", body.character_name),
        "arc": result.get("arc", []),
        "evolution_type": result.get("evolution_type", "complex"),
        "credits_remaining": credits_remaining,
    }