from django.urls import path
from . import views
from .views import (
    BusListCreateView, BusRetrieveUpdateDestroyView,
    RouteListCreateView, RouteRetrieveUpdateDestroyView,
    AdminRouteListCreateView, WeatherRetrieveUpdateDestroyView,
    TripListCreateView, TripRetrieveUpdateDestroyView,
    BookingListCreateView, BookingRetrieveUpdateDestroyView,
    TicketListCreateView, TicketRetrieveUpdateDestroyView,
    PaymentListCreateView, PaymentRetrieveUpdateDestroyView,
    ConductorListCreateView, ConductorRetrieveUpdateDestroyView,
    WeatherListCreateView, AdminRouteRetrieveUpdateDestroyView, core_root,
)
from .views import register, profile
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

app_name = "core"

urlpatterns = [
    path("", core_root, name="core-root"),

    #Auth Endpoints
    path("auth/register/", register, name="register"),
    path("auth/profile/", profile, name="profile"),
    path("auth/login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    # Bus
    path("buses/", BusListCreateView.as_view(), name="bus-list-create"),
    path("buses/<int:pk>/", BusRetrieveUpdateDestroyView.as_view(), name="bus-detail"),

    # Route
    path('admin/routes/', AdminRouteListCreateView.as_view(), name='admin-routes'),
    path('routes/', RouteListCreateView.as_view(), name='routes-list-create'),
    path('routes/<int:pk>/', RouteRetrieveUpdateDestroyView.as_view(), name='routes-detail'),
    path('admin/routes/<int:pk>/', AdminRouteRetrieveUpdateDestroyView.as_view(), name='admin-route-detail'),

    # Trip
    path("trips/", TripListCreateView.as_view(), name="trip-list-create"),
    path("trips/<int:pk>/", TripRetrieveUpdateDestroyView.as_view(), name="trip-detail"),

    # Booking
    path("bookings/", BookingListCreateView.as_view(), name="booking-list-create"),
    path("bookings/<int:pk>/", BookingRetrieveUpdateDestroyView.as_view(), name="booking-detail"),

    # Ticket
    path("tickets/", TicketListCreateView.as_view(), name="ticket-list-create"),
    path("tickets/<int:pk>/", TicketRetrieveUpdateDestroyView.as_view(), name="ticket-detail"),

    # Payment
    path("payments/", PaymentListCreateView.as_view(), name="payment-list-create"),
    path("payments/<int:pk>/", PaymentRetrieveUpdateDestroyView.as_view(), name="payment-detail"),

    # Conductor
    path("conductors/", ConductorListCreateView.as_view(), name="conductor-list-create"),
    path("conductors/<int:pk>/", ConductorRetrieveUpdateDestroyView.as_view(), name="conductor-detail"),

    # Weather
    path("weather/", WeatherListCreateView.as_view(), name="weather-list-create"),
    path("weather/<int:pk>/", WeatherRetrieveUpdateDestroyView.as_view(), name="weather-detail"),
    path('weather/current/', views.current_weather, name='current-weather'),
]
