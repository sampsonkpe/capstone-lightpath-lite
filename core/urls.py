from django.urls import path
from .views import (
    BusListCreateView, BusRetrieveUpdateDestroyView,
    RouteListCreateView, RouteRetrieveUpdateDestroyView,
    TripListCreateView, TripRetrieveUpdateDestroyView,
    BookingListCreateView, BookingRetrieveUpdateDestroyView,
    TicketListCreateView, TicketRetrieveUpdateDestroyView,
    PaymentListCreateView, PaymentRetrieveUpdateDestroyView,
)

urlpatterns = [
    # Bus
    path("buses/", BusListCreateView.as_view(), name="bus-list-create"),
    path("buses/<int:pk>/", BusRetrieveUpdateDestroyView.as_view(), name="bus-detail"),

    # Route
    path("routes/", RouteListCreateView.as_view(), name="route-list-create"),
    path("routes/<int:pk>/", RouteRetrieveUpdateDestroyView.as_view(), name="route-detail"),

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
]

