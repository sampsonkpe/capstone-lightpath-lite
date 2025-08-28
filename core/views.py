from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied

from .models import Bus, Route, Trip, Booking, Ticket, Payment, Conductor, Weather
from .serializers import (
    BusSerializer, RouteSerializer, TripSerializer,
    BookingSerializer, TicketSerializer, PaymentSerializer,
    ConductorSerializer, WeatherSerializer
)
from .permissions import (
    IsAdmin, IsConductor, IsPassenger, IsOwnerOrAdmin,
    IsAdminOrReadOnly, IsAdminOrConductorOrReadOnly
)

# Helper Mixins
class RoleMixin:
    def get_role_name(self):
        user = self.request.user
        role = getattr(user, "role", None)
        return getattr(role, "name", "").lower() if role else ""


# Bus Views (Admin only)
class BusListCreateView(RoleMixin, generics.ListCreateAPIView):
    queryset = Bus.objects.all()
    serializer_class = BusSerializer
    permission_classes = [IsAuthenticated, IsAdmin]


class BusRetrieveUpdateDestroyView(RoleMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = Bus.objects.all()
    serializer_class = BusSerializer
    permission_classes = [IsAuthenticated, IsAdmin]


# Route Views (Admins create; authenticated read)
class RouteListCreateView(RoleMixin, generics.ListCreateAPIView):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]


class RouteRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]


# Trip Views (Admin or Conductor can manage; auth can read)
class TripListCreateView(RoleMixin, generics.ListCreateAPIView):
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


class TripRetrieveUpdateDestroyView(RoleMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = Trip.objects.all()
    serializer_class = TripSerializer
    permission_classes = [IsAuthenticated, IsAdminOrConductorOrReadOnly]


# Booking Views (Passengers)
class BookingListCreateView(RoleMixin, generics.ListCreateAPIView):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        role_name = self.get_role_name()
        user = self.request.user
        if role_name == "admin":
            return Booking.objects.all()
        passenger = getattr(user, "passenger_profile", None)
        if passenger:
            return Booking.objects.filter(passenger=passenger)
        return Booking.objects.none()

    def perform_create(self, serializer):
        role_name = self.get_role_name()
        user = self.request.user
        if role_name == "admin":
            serializer.save()
        else:
            passenger = getattr(user, "passenger_profile", None)
            if not passenger:
                raise PermissionDenied("Only passengers can create bookings.")
            serializer.save(passenger=passenger)


class BookingRetrieveUpdateDestroyView(RoleMixin, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        role_name = self.get_role_name()
        user = self.request.user
        if role_name == "admin":
            return Booking.objects.all()
        passenger = getattr(user, "passenger_profile", None)
        if passenger:
            return Booking.objects.filter(passenger=passenger)
        return Booking.objects.none()


# Ticket Views
class TicketListCreateView(RoleMixin, generics.ListCreateAPIView):
    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        role_name = self.get_role_name()
        user = self.request.user
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
        role_name = self.get_role_name()
        user = self.request.user
        booking = serializer.validated_data.get("booking")
        if role_name == "admin":
            serializer.save()
        elif role_name == "passenger":
            passenger = getattr(user, "passenger_profile", None)
            if not passenger or booking.passenger != passenger:
                raise PermissionDenied("Passengers can only create tickets for their own bookings.")
            serializer.save()
        else:
            raise PermissionDenied("You do not have permission to create tickets.")


class TicketRetrieveUpdateDestroyView(RoleMixin, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        role_name = self.get_role_name()
        user = self.request.user
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
class PaymentListCreateView(RoleMixin, generics.ListCreateAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        role_name = self.get_role_name()
        user = self.request.user
        if role_name == "admin":
            return Payment.objects.all()
        passenger = getattr(user, "passenger_profile", None)
        if passenger:
            return Payment.objects.filter(booking__passenger=passenger)
        return Payment.objects.none()

    def perform_create(self, serializer):
        role_name = self.get_role_name()
        user = self.request.user
        booking = serializer.validated_data.get("booking")
        if role_name == "admin":
            serializer.save()
        elif role_name == "passenger":
            passenger = getattr(user, "passenger_profile", None)
            if not passenger or booking.passenger != passenger:
                raise PermissionDenied("Passengers can only make payments for their own bookings.")
            serializer.save()
        raise PermissionDenied("You do not have permission to create payments.")


class PaymentRetrieveUpdateDestroyView(RoleMixin, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        role_name = self.get_role_name()
        user = self.request.user
        if role_name == "admin":
            return Payment.objects.all()
        passenger = getattr(user, "passenger_profile", None)
        if passenger:
            return Payment.objects.filter(booking__passenger=passenger)
        return Payment.objects.none()


# Conductor Views (Admin-managed)
class ConductorListCreateView(RoleMixin, generics.ListCreateAPIView):
    queryset = Conductor.objects.all()
    serializer_class = ConductorSerializer
    permission_classes = [IsAuthenticated, IsAdmin]


class ConductorRetrieveUpdateDestroyView(RoleMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = Conductor.objects.all()
    serializer_class = ConductorSerializer
    permission_classes = [IsAuthenticated, IsAdmin]


# Weather Views (Admin-managed)
class WeatherListCreateView(RoleMixin, generics.ListCreateAPIView):
    queryset = Weather.objects.all()
    serializer_class = WeatherSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]


class WeatherRetrieveUpdateDestroyView(RoleMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = Weather.objects.all()
    serializer_class = WeatherSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]