from dotenv import load_dotenv
import os

load_dotenv()

class Settings:
    # Supabase
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_SERVICE_KEY: str = os.getenv("SUPABASE_SERVICE_KEY", "")

    # LLM
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "gemini/gemini-1.5-flash")
    LLM_API_KEY: str = os.getenv("LLM_API_KEY", "")

    # Stripe
    STRIPE_SECRET_KEY: str = os.getenv("STRIPE_SECRET_KEY", "")         # sk_test_...
    STRIPE_PUBLISHABLE_KEY: str = os.getenv("STRIPE_PUBLISHABLE_KEY", "") # pk_test_...
    STRIPE_WEBHOOK_SECRET: str = os.getenv("STRIPE_WEBHOOK_SECRET", "")  # whsec_...

    # App
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")
    APP_ENV: str = os.getenv("APP_ENV", "development")

    # Credit costs per feature
    CREDIT_COST = {
        "enhance": 1,
        "mindmap": 2,
        "consistency": 2,
        "evolution": 2,
    }

    # Credit packs (credits, amount in paise — 100 paise = ₹1)
    CREDIT_PACKS = {
        "starter":   {"credits": 20,  "amount_paise": 9900},    # ₹99
        "pro":       {"credits": 60,  "amount_paise": 24900},   # ₹249
        "unlimited": {"credits": 150, "amount_paise": 49900},   # ₹499
    }

settings = Settings()