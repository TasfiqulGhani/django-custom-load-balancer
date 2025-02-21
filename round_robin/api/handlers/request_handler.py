class RequestHandler:
    """Handles API requests using an injected proxy"""

    def __init__(self, proxy):
        self.proxy = proxy

    async def handle_request(self, data):
        """Forwards request using the injected proxy strategy"""
        return await self.proxy.forward_request(data)
