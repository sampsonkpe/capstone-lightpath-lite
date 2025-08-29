from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse, JsonResponse
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

def index(request):
    return HttpResponse("Hey, there! Welcome to LightPath-Lite API!")

def api_root(request):
    return JsonResponse({
        "message": "Welcome to LightPath Lite API",
        "auth": {
            "login": "/api/token/",
            "refresh": "/api/token/refresh/"
        },
        "core_endpoints": "/api/core/"
    })

urlpatterns = [
    path("admin/", admin.site.urls),

    # Core App routes
    path("api/core/", include(("core.urls", "core"), namespace="core")),

    # Auth Routes (JWT)
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    # API root
    path("api/", api_root, name="api_root"),
]
