import hmac
import os
import secrets
import time
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

router = APIRouter()
# auto_error=False so we can return 401 (not 403) when header is missing
security = HTTPBearer(auto_error=False)

# {token: expiry_timestamp}
_tokens: dict[str, float] = {}
TOKEN_TTL = 30 * 24 * 60 * 60  # 30 days


class LoginRequest(BaseModel):
    password: str


def _purge_expired():
    now = time.time()
    for t in [t for t, exp in _tokens.items() if exp < now]:
        del _tokens[t]


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    if credentials is None:
        raise HTTPException(status_code=401, detail={"error": "No token provided"})
    _purge_expired()
    token = credentials.credentials
    if token not in _tokens or _tokens[token] < time.time():
        raise HTTPException(status_code=401, detail={"error": "Invalid or expired token"})
    return token


@router.post("/api/login")
def login(req: LoginRequest):
    expected = os.environ.get("APP_PASSWORD", "")
    if not expected or not hmac.compare_digest(req.password, expected):
        raise HTTPException(status_code=401, detail={"error": "Invalid password"})
    token = secrets.token_urlsafe(32)
    _tokens[token] = time.time() + TOKEN_TTL
    return {"token": token}
