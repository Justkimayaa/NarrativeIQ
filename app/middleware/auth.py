from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.db.supabase import get_client

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """
    Dependency — verifies Supabase JWT from Authorization header.
    Swagger UI will now show a lock icon and Authorize button.

    Usage in routes:
        @router.post("/enhance")
        async def enhance(req: EnhanceRequest, user=Depends(get_current_user)):
            user_id = user["id"]
    """
    token = credentials.credentials  # extracts the token after "Bearer "

    try:
        client = get_client()
        response = client.auth.get_user(token)
        if not response or not response.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
            )
        return {"id": response.user.id, "email": response.user.email}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token verification failed: {str(e)}",
        )