from supabase import create_client, Client
from app.config import settings

# Single shared client using service role key (bypasses RLS — safe for backend only)
supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)


def get_client() -> Client:
    return supabase


async def get_user_credits(user_id: str) -> int:
    """Fetch current credit balance for a user."""
    res = (
        supabase.table("profiles")
        .select("credits")
        .eq("user_id", user_id)
        .single()
        .execute()
    )
    if res.data:
        return res.data["credits"]
    return 0


async def deduct_credits(user_id: str, amount: int) -> bool:
    """
    Atomically deduct credits using the Postgres RPC function.
    Returns True if deduction succeeded, False if insufficient credits.
    """
    res = supabase.rpc("deduct_credits", {"uid": user_id, "amount": amount}).execute()
    return res.data is True


async def add_credits(user_id: str, amount: int) -> int:
    """Add credits after successful Razorpay payment. Returns new balance."""
    res = (
        supabase.table("profiles")
        .update({"credits": supabase.raw(f"credits + {amount}")})
        .eq("user_id", user_id)
        .select("credits")
        .single()
        .execute()
    )
    return res.data["credits"] if res.data else 0


async def log_analysis(
    user_id: str,
    feature: str,
    input_text: str,
    output_json: dict,
    credits_used: int,
    persona: str | None = None,
):
    """Store a completed analysis in the analyses table."""
    supabase.table("analyses").insert(
        {
            "user_id": user_id,
            "feature": feature,
            "persona": persona,
            "input_text": input_text[:5000],  # cap stored input to 5k chars
            "output_json": output_json,
            "credits_used": credits_used,
        }
    ).execute()