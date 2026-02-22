from fastapi import APIRouter, Depends, HTTPException, status, Request
import stripe

from app.middleware.auth import get_current_user
from app.db.supabase import get_client, get_user_credits, add_credits
from app.config import settings
from app.models.schemas import (
    CreditsResponse,
    CreateOrderRequest,
    CreateOrderResponse,
    VerifyPaymentRequest,
    VerifyPaymentResponse,
)

router = APIRouter()

stripe.api_key = settings.STRIPE_SECRET_KEY


# ─── GET /credits ─────────────────────────────────────────────────────────────

@router.get("", response_model=CreditsResponse)
async def get_credits(user=Depends(get_current_user)):
    """Return current credit balance for the authenticated user."""
    credits = await get_user_credits(user["id"])
    return {"credits": credits}


# ─── POST /credits/create-order ───────────────────────────────────────────────

@router.post("/create-order", response_model=CreateOrderResponse)
async def create_order(
    body: CreateOrderRequest,
    user=Depends(get_current_user),
):
    """
    Creates a Stripe PaymentIntent for the selected credit pack.
    Frontend uses the returned client_secret to open Stripe's payment sheet.
    """
    pack = settings.CREDIT_PACKS.get(body.pack.value)
    if not pack:
        raise HTTPException(status_code=400, detail="Invalid pack selected")

    try:
        intent = stripe.PaymentIntent.create(
            amount=pack["amount_paise"],          # Stripe uses smallest unit (paise for INR)
            currency="inr",
            metadata={
                "user_id": user["id"],
                "pack": body.pack.value,
                "credits": pack["credits"],
            },
        )
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=500, detail=f"Stripe error: {str(e)}")

    # Store as pending transaction
    get_client().table("transactions").insert(
        {
            "user_id": user["id"],
            "stripe_payment_intent_id": intent["id"],
            "credits_purchased": pack["credits"],
            "amount_paise": pack["amount_paise"],
            "status": "pending",
        }
    ).execute()

    return {
        "order_id": intent["id"],
        "client_secret": intent["client_secret"],  # frontend needs this for Stripe UI
        "amount": pack["amount_paise"],
        "currency": "INR",
        "credits_to_receive": pack["credits"],
    }


# ─── POST /credits/verify-payment ─────────────────────────────────────────────

@router.post("/verify-payment", response_model=VerifyPaymentResponse)
async def verify_payment(
    body: VerifyPaymentRequest,
    user=Depends(get_current_user),
):
    """
    Verifies payment by checking PaymentIntent status directly with Stripe.
    Credits ONLY added after Stripe confirms — never trust the frontend.
    """
    try:
        intent = stripe.PaymentIntent.retrieve(body.stripe_payment_intent_id)
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=f"Could not retrieve payment: {str(e)}")

    if intent["status"] != "succeeded":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Payment not completed. Status: {intent['status']}",
        )

    # Security: make sure this intent belongs to this user
    if intent["metadata"].get("user_id") != user["id"]:
        raise HTTPException(status_code=403, detail="Payment does not belong to this user")

    # Fetch the pending transaction
    tx_res = (
        get_client()
        .table("transactions")
        .select("*")
        .eq("stripe_payment_intent_id", body.stripe_payment_intent_id)
        .eq("user_id", user["id"])
        .eq("status", "pending")
        .single()
        .execute()
    )

    if not tx_res.data:
        raise HTTPException(
            status_code=400,
            detail="Transaction not found or already processed",
        )

    credits_to_add = tx_res.data["credits_purchased"]

    # Add credits + mark success
    new_balance = await add_credits(user["id"], credits_to_add)

    get_client().table("transactions").update({"status": "success"}).eq(
        "stripe_payment_intent_id", body.stripe_payment_intent_id
    ).execute()

    return {
        "success": True,
        "credits_added": credits_to_add,
        "new_balance": new_balance,
    }


# ─── POST /credits/webhook ────────────────────────────────────────────────────
# Stripe calls this automatically when payment succeeds —
# handles cases where user closes browser mid-checkout

@router.post("/webhook")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except (ValueError, stripe.error.SignatureVerificationError):
        raise HTTPException(status_code=400, detail="Invalid webhook signature")

    if event["type"] == "payment_intent.succeeded":
        intent = event["data"]["object"]
        user_id = intent["metadata"].get("user_id")
        credits = int(intent["metadata"].get("credits", 0))

        if user_id and credits:
            tx = (
                get_client()
                .table("transactions")
                .select("status")
                .eq("stripe_payment_intent_id", intent["id"])
                .single()
                .execute()
            )
            if tx.data and tx.data["status"] == "pending":
                await add_credits(user_id, credits)
                get_client().table("transactions").update({"status": "success"}).eq(
                    "stripe_payment_intent_id", intent["id"]
                ).execute()

    return {"received": True}