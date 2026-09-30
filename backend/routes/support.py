from urllib.parse import urlparse

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from backend.config import BUYMEACOFFEE_MODE, BUYMEACOFFEE_URL

router = APIRouter()
DEMO_CHECKOUT_PATH = "/support/test-checkout"
DEMO_CHECKOUT_URL = "/api" + DEMO_CHECKOUT_PATH


def get_valid_support_url() -> str | None:
    """Allow only an HTTPS Buy Me a Coffee profile URL."""
    if not BUYMEACOFFEE_URL:
        return None

    parsed = urlparse(BUYMEACOFFEE_URL)
    hostname = (parsed.hostname or "").lower().rstrip(".")
    path_parts = parsed.path.strip("/").split("/")
    if (
        parsed.scheme != "https"
        or parsed.username
        or parsed.password
        or hostname not in {"buymeacoffee.com", "www.buymeacoffee.com"}
        or len(path_parts) != 1
        or not path_parts[0]
    ):
        return None
    return BUYMEACOFFEE_URL


def get_support_checkout_url() -> str | None:
    if BUYMEACOFFEE_MODE == "demo":
        return DEMO_CHECKOUT_URL
    if BUYMEACOFFEE_MODE == "live":
        return get_valid_support_url()
    return None


@router.get("/support")
async def support_configuration():
    """Expose only the public Buy Me a Coffee profile URL."""
    support_url = get_support_checkout_url()
    return {
        "enabled": support_url is not None,
        "checkout_url": support_url,
        "mode": "demo" if BUYMEACOFFEE_MODE == "demo" else "live",
    }


@router.get(DEMO_CHECKOUT_PATH, response_class=HTMLResponse, include_in_schema=False)
async def demo_checkout():
    """Provide a local, non-payment flow for testing the hosted-link integration."""
    return HTMLResponse(
                """
                <!doctype html>
                <html lang="en">
                <head>
                    <meta charset="utf-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1">
                    <title>YT Cuts Buy Me a Coffee Test</title>
                    <style>
                        :root { color-scheme: dark; font-family: system-ui, sans-serif; }
                        body { display: grid; min-height: 100vh; place-items: center; margin: 0; background: #111; color: #f5f5f5; }
                        main { width: min(30rem, calc(100% - 2rem)); padding: 2rem; border: 1px solid #444; border-radius: 16px; background: #1b1b1b; text-align: center; }
                        h1 { margin-top: 0; }
                        p { color: #bbb; line-height: 1.5; }
                        button, a { display: inline-block; margin: .35rem; padding: .7rem 1rem; border: 1px solid #666; border-radius: 8px; background: #f5f5f5; color: #111; font: inherit; text-decoration: none; cursor: pointer; }
                        button:hover, a:hover { background: #ef4444; color: #fff; border-color: #ef4444; }
                        #result { min-height: 1.5em; color: #86efac; font-weight: 600; }
                    </style>
                </head>
                <body>
                    <main>
                        <h1>Buy Me a Coffee Test</h1>
                        <p>This is a local integration test only. No contribution is collected or recorded.</p>
                        <button id="simulate" type="button">Simulate contribution</button>
                        <a href="/">Return to YT Cuts</a>
                        <p id="result" aria-live="polite"></p>
                    </main>
                    <script>
                        document.getElementById('simulate').addEventListener('click', () => {
                            document.getElementById('result').textContent = 'Test completed. No payment was processed.';
                        });
                    </script>
                </body>
                </html>
                """
    )