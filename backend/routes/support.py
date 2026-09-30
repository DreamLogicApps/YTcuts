from urllib.parse import urlparse

from fastapi import APIRouter

from backend.config import LEMON_SQUEEZY_SUPPORT_URL

router = APIRouter()


def get_valid_support_url() -> str | None:
    """Allow only an HTTPS Lemon Squeezy hosted checkout URL."""
    if not LEMON_SQUEEZY_SUPPORT_URL:
        return None

    parsed = urlparse(LEMON_SQUEEZY_SUPPORT_URL)
    hostname = (parsed.hostname or "").lower().rstrip(".")
    if (
        parsed.scheme != "https"
        or parsed.username
        or parsed.password
        or not (hostname == "lemonsqueezy.com" or hostname.endswith(".lemonsqueezy.com"))
        or not parsed.path.startswith("/checkout/")
    ):
        return None
    return LEMON_SQUEEZY_SUPPORT_URL


@router.get("/support")
async def support_configuration():
    """Expose only the public hosted checkout URL, never Lemon Squeezy credentials."""
    support_url = get_valid_support_url()
    return {"enabled": support_url is not None, "checkout_url": support_url}