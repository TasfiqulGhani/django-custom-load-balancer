from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def process_request(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            return JsonResponse(data, status=200)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
    return JsonResponse({"error": "Only POST allowed"}, status=405)

@csrf_exempt
def health_check(request):
    """ ✅ Health Check Endpoint for Application Instances """
    return JsonResponse({"status": "healthy"}, status=200) 