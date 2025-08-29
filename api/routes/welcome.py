from fastapi import Depends, APIRouter
from fastapi.security.api_key import APIKeyCookie
from ..utils import require_auth

router = APIRouter(tags=["Welcome"])
cookie_scheme = APIKeyCookie(name="token")

@router.get(
    "/welcome",
    summary="Get authenticated user details",
    description=(
        "Returns the authenticated user's basic information (name and email).\n\n"
        "This endpoint requires a valid `token` cookie, which is set after successful login.\n\n"
        "If the cookie is missing or invalid, a `401 Unauthorized` error is returned."
    ),
    dependencies=[Depends(cookie_scheme)]
)
async def welcome(token: dict = Depends(require_auth)):
    return {"name": token['name'], "email": token['email']}
