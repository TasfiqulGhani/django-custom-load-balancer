import httpx
from django.conf import settings
from .http_client_adapter import HttpClientAdapter


class HttpxAdapter(HttpClientAdapter):
    """Adapter for HTTPX"""

    async def post(self, url: str, json: dict):
        async with httpx.AsyncClient(timeout=settings.REQUEST_TIMEOUT) as client:
            try:
                response = await client.post(url, json=json)
                return response
            except httpx.RequestError as e:
                print(f"🚨 HTTPX Request Failed: {url} | Error: {str(e)}", flush=True)
                return None
