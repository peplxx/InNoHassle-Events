__all__ = []

from fastapi import status, HTTPException
from starlette.requests import Request

from src.app.auth import router, oauth
from src.app.auth.jwt import create_access_token, Token
from src.config import settings

enabled = bool(settings.INNOPOLIS_SSO_CLIENT_ID.get_secret_value())
redirect_uri = settings.AUTH_REDIRECT_URI_PREFIX + "/innopolis"

if enabled:
    innopolis_sso = oauth.register(
        "innopolis",
        client_id=settings.INNOPOLIS_SSO_CLIENT_ID.get_secret_value(),
        client_secret=settings.INNOPOLIS_SSO_CLIENT_SECRET.get_secret_value(),
        # OAuth client will fetch configuration on first request
        server_metadata_url="https://sso.university.innopolis.ru/adfs/.well-known/openid-configuration",
        client_kwargs={"scope": "openid"},
    )


def check_enabled():
    if not enabled:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Auth provider is not enabled",
        )


@router.get("/innopolis/login")
async def login_via_innopolis(request: Request):
    check_enabled()
    return await oauth.innopolis.authorize_redirect(request, redirect_uri)


@router.get("/innopolis/token")
async def auth_via_innopolis(request: Request) -> Token:
    check_enabled()
    token = await oauth.innopolis.authorize_access_token(request)
    user_info = token["userinfo"]
    email = user_info["email"]
    return create_access_token(email)