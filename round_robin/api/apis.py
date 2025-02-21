import json
from django.http import JsonResponse
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from asgiref.sync import async_to_sync  # Import async_to_sync
from .proxies.factory import ProxyFactory
from .handlers.request_handler import RequestHandler

# Create the proxy **once** when Django starts
proxy = ProxyFactory.get_proxy()

class ProxyForwardView(APIView):
    """
    Handles forwarding requests asynchronously through the proxy system.
    Uses dynamic proxy selection and automatic instance retrieval.
    - Implements API Throttling using DRF's built-in rate limit system.
    """
    permission_classes = [AllowAny]  # Allow any user to call this API
    throttle_classes = [AnonRateThrottle, UserRateThrottle]  # Apply IP-based throttling

    def post(self, request):  # Change from async def to def
        try:
            data = json.loads(request.body)
            handler = RequestHandler(proxy=proxy)
            
            # Convert async call to sync
            response_data, status = async_to_sync(handler.handle_request)(data)  

            return Response(response_data, status=status)
        except json.JSONDecodeError:
            return Response({"error": "Invalid JSON"}, status=400)

    def get(self, request):
        return Response({"error": "Only POST allowed"}, status=405)
