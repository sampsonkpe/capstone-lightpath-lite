from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied

from .models import Bus, Route, Trip, Booking, Ticket, Payment, Conductor
from .serializers import (
    BusSerializer, RouteSerializer, TripSerializer,
    BookingSerializer, TicketSerializer, PaymentSerializer,
    ConductorSerializer
)
from .permissions import (
    IsAdmin, IsConductor, IsPassenger, IsOwnerOrAdmin,
    IsAdminOrReadOnly, IsAdminOrConductorOrReadOnly
)


# Bus Views (Admin only)
class BusListCreateView(generics.ListCreateAPIView):
    queryset = Bus.objects.all()
    serializer_class = BusSerializer
    permission_classes = [IsAuthenticated, IsAdmin]


class BusRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Bus.objects.all()
    serializer_class = BusSerializer
    permission_classes = [IsAuthenticated, IsAdmin]


# Route Views (Admins create; authenticated read)
class RouteListCreateView(generics.ListCreateAPIView):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]


class RouteRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]


# Trip Views (Admin or Conductor can manage; auth can read)
class TripListCreateView(generics.ListCreateAPIView):
    queryset = Trip.objects.all()
    serializer_class = TripSerializer
    permission_classes = [IsAuthenticated, IsAdminOrConductorOrReadOnly]

    def perform_create(self, serializer):
        user = self.request.user
        role = getattr(user, "role", None)
        role_name = getattr(role, "name", "").lower() if role else ""
        if role_name == "admin":
            serializer.save()
        elif role_name == "conductor":
            conductor_profile = getattr(user, "conductor_profile", None)
            if not conductor_profile:
                raise PermissionDenied("Conductor profile not found for this user.")
            # ensure conductor cannot assign trips to someone else
            serializer.save(conductor=conductor_profile)
        else:
            raise PermissionDenied("Only Admins or Conductors can create trips.")


class TripRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Trip.objects.all()
    serializer_class = TripSerializer
    permission_classes = [IsAuthenticated, IsAdminOrConductorOrReadOnly]


# Booking Views (Passengers)
class BookingListCreateView(generics.ListCreateAPIView):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not getattr(user, "is_authenticated", False):
            return Booking.objects.none()
        role = getattr(user, "role", None)
        role_name = getattr(role, "name", "").lower() if role else ""
        if role_name == "admin":
            return Booking.objects.all()
        passenger = getattr(user, "passenger_profile", None)
        if passenger:
            return Booking.objects.filter(passenger=passenger)
        return Booking.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        role = getattr(user, "role", None)
        role_name = getattr(role, "name", "").lower() if role else ""
        if role_name == "admin":
            # allow admin to create bookings for any passenger (passenger_id may be supplied)
            serializer.save()
            return
        passenger = getattr(user, "passenger_profile", None)
        if not passenger:
            raise PermissionDenied("Only passengers can create bookings.")
        serializer.save(passenger=passenger)


class BookingRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        user = self.request.user
        if not getattr(user, "is_authenticated", False):
            return Booking.objects.none()
        role = getattr(user, "role", None)
        role_name = getattr(role, "name", "").lower() if role else ""
        if role_name == "admin":
            return Booking.objects.all()
        passenger = getattr(user, "passenger_profile", None)
        if passenger:
            return Booking.objects.filter(passenger=passenger)
        return Booking.objects.none()


# Ticket Views
class TicketListCreateView(generics.ListCreateAPIView):
    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not getattr(user, "is_authenticated", False):
            return Ticket.objects.none()
        role = getattr(user, "role", None)
        role_name = getattr(role, "name", "").lower() if role else ""
        if role_name == "admin":
            return Ticket.objects.all()
        if role_name == "conductor":
            conductor = getattr(user, "conductor_profile", None)
            if conductor:
                return Ticket.objects.filter(booking__trip__conductor=conductor)
            return Ticket.objects.none()
        # passenger
        passenger = getattr(user, "passenger_profile", None)
        if passenger:
            return Ticket.objects.filter(booking__passenger=passenger)
        return Ticket.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        role = getattr(user, "role", None)
        role_name = getattr(role, "name", "").lower() if role else ""
        booking = serializer.validated_data.get("booking")
        if role_name == "admin":
            serializer.save()
            return
        if role_name == "passenger":
            passenger = getattr(user, "passenger_profile", None)
            if not passenger or booking.passenger != passenger:
                raise PermissionDenied("Passengers can only create tickets for their own bookings.")
            serializer.save()
            return
        raise PermissionDenied("You do not have permission to create tickets.")


class TicketRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        user = self.request.user
        if not getattr(user, "is_authenticated", False):
            return Ticket.objects.none()
        role = getattr(user, "role", None)
        role_name = getattr(role, "name", "").lower() if role else ""
        if role_name == "admin":
            return Ticket.objects.all()
        if role_name == "conductor":
            conductor = getattr(user, "conductor_profile", None)
            if conductor:
                return Ticket.objects.filter(booking__trip__conductor=conductor)
            return Ticket.objects.none()
        passenger = getattr(user, "passenger_profile", None)
        if passenger:
            return Ticket.objects.filter(booking__passenger=passenger)
        return Ticket.objects.none()


# Payment Views
class PaymentListCreateView(generics.ListCreateAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not getattr(user, "is_authenticated", False):
            return Payment.objects.none()
        role = getattr(user, "role", None)
        role_name = getattr(role, "name", "").lower() if role else ""
        if role_name == "admin":
            return Payment.objects.all()
        passenger = getattr(user, "passenger_profile", None)
        if passenger:
            return Payment.objects.filter(booking__passenger=passenger)
        return Payment.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        role = getattr(user, "role", None)
        role_name = getattr(role, "name", "").lower() if role else ""
        booking = serializer.validated_data.get("booking")
        if role_name == "admin":
            serializer.save()
            return
        if role_name == "passenger":
            passenger = getattr(user, "passenger_profile", None)
            if not passenger or booking.passenger != passenger:
                raise PermissionDenied("Passengers can only make payments for their own bookings.")
            serializer.save()
            return
        raise PermissionDenied("You do not have permission to create payments.")


class PaymentRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        user = self.request.user
        if not getattr(user, "is_authenticated", False):
            return Payment.objects.none()
        role = getattr(user, "role", None)
        role_name = getattr(role, "name", "").lower() if role else ""
        if role_name == "admin":
            return Payment.objects.all()
        passenger = getattr(user, "passenger_profile", None)
        if passenger:
            return Payment.objects.filter(booking__passenger=passenger)
        return Payment.objects.none()


# Conductor Views (Admin-managed)
class ConductorListCreateView(generics.ListCreateAPIView):
    queryset = Conductor.objects.all()
    serializer_class = ConductorSerializer
    permission_classes = [IsAuthenticated, IsAdmin]


class ConductorRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Conductor.objects.all()
    serializer_class = ConductorSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
