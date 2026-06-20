import httpx
from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.config import settings
import time

security = HTTPBearer()

CLERK_JWKS_URL = 'https://api.clerk.com/v1/jwks'

# Simple in-memory JWKS cache to avoid a network call on every request
_jwks_cache: dict = {}
_jwks_cache_ttl = 0
_JWKS_CACHE_SECONDS = 3600  # refresh every hour


async def get_jwks() -> dict:
    global _jwks_cache, _jwks_cache_ttl
    if _jwks_cache and time.time() < _jwks_cache_ttl:
        return _jwks_cache
    async with httpx.AsyncClient() as client:
        response = await client.get(
            CLERK_JWKS_URL,
            headers={'Authorization': f'Bearer {settings.CLERK_SECRET_KEY}'}
        )
        response.raise_for_status()
        _jwks_cache = response.json()
        _jwks_cache_ttl = time.time() + _JWKS_CACHE_SECONDS
        return _jwks_cache


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    try:
        jwks = await get_jwks()
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get('kid')

        key = next((k for k in jwks['keys'] if k['kid'] == kid), None)
        if not key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Invalid token: key not found'
            )

        payload = jwt.decode(
            token,
            key,
            algorithms=['RS256'],
            options={'verify_aud': False}
        )
        return payload

    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f'Invalid token: {str(e)}'
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f'Auth error: {str(e)}'
        )
