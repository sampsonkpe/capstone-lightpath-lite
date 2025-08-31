from django.http import JsonResponse
from rest_framework import generics, status, permissions
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .services import get_current_weather
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Bus, Role, Route, Trip, Booking, Ticket, Payment, Conductor, Weather, Passenger
from .serializers import (
    BusSerializer, RouteSerializer, TripSerializer,
    BookingSerializer, TicketSerializer, PaymentSerializer,
    ConductorSerializer, WeatherSerializer
)
from .permissions import (
    IsAdmin, IsConductor, IsPassenger, IsOwnerOrAdmin,
    IsAdminOrReadOnly, IsAdminOrConductorOrReadOnly
)

User = get_user_model()

@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
    data = request.data
    if User.objects.filter(email=data.get("email")).exists():
        return Response({"error": "Email already exists"}, status=status.HTTP_400_BAD_REQUEST)
    
    # Get the Role instance
    role_name = data.get("role", "passenger")
    try:
        role_instance = Role.objects.get(name__iexact=role_name)
    except Role.DoesNotExist:
        return Response({"error": f"Role '{role_name}' does not exist."}, status=400)
    
    user = User.objects.create(
        email=data.get("email"),
        password=make_password(data.get("password")),
        role=role_instance
    )

    if role_instance.name.lower() == "passenger":
        Passenger.objects.create(user=user)

    refresh = RefreshToken.for_user(user)

    return Response({
        "message": "User registered successfully",
        "user": {
            "id": user.id,
            "email": user.email,
            "role": user.role.name
        },
        "token": {
            "refresh": str(refresh),
            "access": str(refresh.access_token)
        }
    }, status=status.HTTP_201_CREATED)

@api_view(["GET", "PATCH"])
@permission_classes([IsAuthenticated])
def profile(request):
    user = request.user
    passenger = getattr(user, "passenger_profile", None)

    if request.method == 'GET':
        # Return user + passenger info
        data = {
            "email": user.email,
            "full_name": passenger.full_name if passenger else "",
            "contact_number": passenger.contact_number if passenger else "",
            "username": passenger.username if passenger else ""
        }
        return Response(data)

    elif request.method == 'PATCH':
        # Update passenger profile
        if not passenger:
            return Response({"error": "Passenger profile does not exist."}, status=400)
        
        full_name = request.data.get("full_name")
        contact_number = request.data.get("contact_number")
        username = request.data.get("username")

        if full_name:
            passenger.full_name = full_name
        if contact_number:
            passenger.contact_number = contact_number
        if username:
            passenger.username = username

        passenger.save()
        return Response({
            "full_name": passenger.full_name,
            "contact_number": passenger.contact_number,
            "username": passenger.username
        })

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
class AdminRouteListCreateView(generics.ListCreateAPIView):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer
    permission_classes = [permissions.IsAdminUser]

class AdminRouteRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer
    permission_classes = [permissions.IsAdminUser]
 
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

@api_view(['GET'])
def current_weather(request):
    city = request.GET.get('city', 'Accra')
    try:
        data = get_current_weather(city)
        result = {
            "city": data.get("name"),
            "temperature": data["main"]["temp"],
            "feels_like": data["main"]["feels_like"],
            "humidity": data["main"]["humidity"],
            "weather": data["weather"][0]["description"],
            "wind_speed": data["wind"]["speed"]
        }
        return Response(result)
    except Exception as e:
        return Response({"error": str(e)}, status=400)
    

def core_root(request):
    return JsonResponse({
        "message": "Welcome to the LightPath Lite Core API",
        "available_endpoints": {
            "buses": "/api/core/buses/",
            "routes": "/api/core/routes/",
            "trips": "/api/core/trips/",
            "bookings": "/api/core/bookings/",
            "tickets": "/api/core/tickets/",
            "payments": "/api/core/payments/",
            "conductors": "/api/core/conductors/",
            "weather": "/api/core/weather/"
        }
    })