import json
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse

from app.middleware.auth import get_current_user
from app.db.supabase import deduct_credits, get_user_credits, log_analysis
from app.config import settings
from app.models.schemas import EnhanceRequest
from app.services.llm import stream_enhance_text, enhance_text
from app.services.diff import compute_diff

router = APIRouter()

COST = settings.CREDIT_COST["enhance"]  # 1 credit


@router.post("")
async def enhance(
    body: EnhanceRequest,
    user=Depends(get_current_user),
):
    """
    Persona-driven text enhancement with SSE streaming.
    Costs 1 credit per call.

    Frontend: Use EventSource or fetch + ReadableStream (NOT axios).
    Each SSE event: data: {"token": "...", "done": false}
    Final event:    data: {"done": true, "diff": [...], "credits_remaining": N}
    """
    user_id = user["id"]

    # 1. Deduct credits atomically before doing any work
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

    # 2. Stream the enhanced text back as SSE
    async def event_generator():
        full_enhanced = []

        try:
            async for token in stream_enhance_text(body.text, body.persona.value):
                full_enhanced.append(token)
                yield f"data: {json.dumps({'token': token, 'done': False})}\n\n"

            # 3. Once streaming is done, compute diff + get new balance
            enhanced_text = "".join(full_enhanced)
            diff = compute_diff(body.text, enhanced_text)
            credits_remaining = await get_user_credits(user_id)

            # 4. Log the analysis (async fire-and-forget style)
            await log_analysis(
                user_id=user_id,
                feature="enhance",
                input_text=body.text,
                output_json={"enhanced_text": enhanced_text, "diff": diff},
                credits_used=COST,
                persona=body.persona.value,
            )

            # 5. Final SSE event with diff + balance
            yield f"data: {json.dumps({'done': True, 'diff': diff, 'credits_remaining': credits_remaining})}\n\n"

        except Exception as e:
            # Refund credit on LLM failure
            from app.db.supabase import add_credits
            await add_credits(user_id, COST)
            yield f"data: {json.dumps({'error': str(e), 'done': True})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",  # Disables nginx buffering — critical for streaming
        },
    )