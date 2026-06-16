from dataclasses import dataclass

from fastapi import Depends, Header, HTTPException, status

from app.core.config import settings


@dataclass(frozen=True)
class Principal:
    subject: str
    scopes: set[str]


async def authenticate(x_api_key: str | None = Header(default=None)) -> Principal:
    if not x_api_key or x_api_key != settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid API key.",
        )
    scopes = {scope.strip() for scope in settings.api_key_scopes.split(",") if scope.strip()}
    return Principal(subject="api-key-client", scopes=scopes)


def require_scope(scope: str):
    async def dependency(principal: Principal = Depends(authenticate)) -> Principal:
        if scope not in principal.scopes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Required scope missing: {scope}",
            )
        return principal

    return dependency

