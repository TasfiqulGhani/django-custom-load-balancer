from django.urls import path
from .apis import ProxyForwardView

urlpatterns = [
   path("process/", ProxyForwardView.as_view(), name="proxy_forward"),
]
