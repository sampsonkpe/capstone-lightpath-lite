from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse, JsonResponse

def index(request):
    return HttpResponse("Hey, there! Welcome to LightPath-Lite API!")

def api_root(request):
    return JsonResponse({
        "buses": "/api/core/buses/",
        "routes": "/api/core/routes/",
        "trips": "/api/core/trips/",
        "bookings": "/api/core/bookings/",
        "tickets": "/api/core/tickets/",
        "payments": "/api/core/payments/",
        "conductors": "/api/core/conductors/"
    })

urlpatterns = [
    path("", index),
    path("admin/", admin.site.urls),
    path("api/core/", api_root),
    path("api/core/", include("core.urls")),
]
