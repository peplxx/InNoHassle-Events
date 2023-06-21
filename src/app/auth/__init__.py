__all__ = ["oauth", "router", "get_current_user_email"]

from authlib.integrations.starlette_client import OAuth
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette import status

from src.app.auth.jwt import verify_token

router = APIRouter(prefix="/auth", tags=["Auth"])
oauth = OAuth()
bearer_scheme = HTTPBearer(
    scheme_name="Bearer token",
    description="Your JSON Web Token (JWT)",
)


def get_current_user_email(auth: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    return verify_token(auth.credentials, credentials_exception).email


# Register all OAuth applications and routes
import src.app.auth.innopolis  # noqa
import src.app.auth.dev  # noqa