from abc import ABC, abstractmethod


class HttpClientAdapter(ABC):
    """Abstract Adapter for HTTP clients"""

    @abstractmethod
    async def post(self, url: str, json: dict):
        """Sends a POST request and returns response"""
        pass
