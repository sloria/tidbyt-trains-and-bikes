import httpx

DEFAULT_TIMEOUT = httpx.Timeout(10.0, connect=5.0)
DEFAULT_RETRIES = 2


def make_client(**kwargs) -> httpx.AsyncClient:
    """Create an httpx.AsyncClient with retries and timeouts."""
    kwargs.setdefault("timeout", DEFAULT_TIMEOUT)
    transport = httpx.AsyncHTTPTransport(retries=DEFAULT_RETRIES)
    kwargs.setdefault("transport", transport)
    return httpx.AsyncClient(**kwargs)
