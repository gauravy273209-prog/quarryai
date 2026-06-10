import httpx
from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.config import settings

security = HTTPBearer()

CLERK_JWKS_URL = "https://api.clerk.com/v1/jwks"

async def get_jwks():
    async with httpx.AsyncClient() as client:
        response = await client.get(
            CLERK_JWKS_URL,
            headers={"Authorization": f"Bearer {settings.CLERK_SECRET_KEY}"}
        )
        return response.json()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    try:
        jwks = await get_jwks()
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")

        key = next((k for k in jwks["keys"] if k["kid"] == kid), None)
        if not key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: key not found"
            )

        payload = jwt.decode(
            token,
            key,
            algorithms=["RS256"],
            options={"verify_aud": False}
        )
        return payload

    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Auth error: {str(e)}"
        )