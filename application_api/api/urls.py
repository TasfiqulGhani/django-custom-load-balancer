from django.urls import path
from .views import process_request, health_check

urlpatterns = [
    path('process/', process_request, name='process_request'),
    path('process/health/', health_check, name='health_check'),
]