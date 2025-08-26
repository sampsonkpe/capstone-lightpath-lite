from rest_framework import serializers
from django.db import transaction
from rest_framework.exceptions import ValidationError

from .models import (
    User, Role, Passenger, Conductor,
    Bus, Route, Trip, Booking, Ticket, Payment
)


# Role & User
class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ("id", "name")


class UserSerializer(serializers.ModelSerializer):
    # allow creating/updating password via this serializer (write-only)
    password = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ("id", "email", "password", "role", "is_active", "is_staff", "date_joined")
        read_only_fields = ("is_active", "is_staff", "date_joined")

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        for attr, val in validated_data.items():
            setattr(instance, attr, val)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


# Passenger & Conductor
class PassengerSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source="user", write_only=True
    )

    class Meta:
        model = Passenger
        fields = ("id", "user", "user_id", "phone_number")


class ConductorSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source="user", write_only=True
    )

    class Meta:
        model = Conductor
        fields = ("id", "user", "user_id", "employee_id")


# Transport Models
class BusSerializer(serializers.ModelSerializer):
    conductor = ConductorSerializer(read_only=True)
    conductor_id = serializers.PrimaryKeyRelatedField(
        queryset=Conductor.objects.all(), source="conductor", write_only=True, required=False, allow_null=True
    )

    class Meta:
        model = Bus
        fields = ("id", "number_plate", "capacity", "conductor", "conductor_id")

    def validate_capacity(self, value):
        if value <= 0:
            raise ValidationError("Bus capacity must be greater than zero.")
        return value


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = ("id", "start_point", "end_point", "description")


class TripSerializer(serializers.ModelSerializer):
    bus = BusSerializer(read_only=True)
    bus_id = serializers.PrimaryKeyRelatedField(
        queryset=Bus.objects.all(), source="bus", write_only=True
    )
    route = RouteSerializer(read_only=True)
    route_id = serializers.PrimaryKeyRelatedField(
        queryset=Route.objects.all(), source="route", write_only=True
    )
    conductor = ConductorSerializer(read_only=True)
    conductor_id = serializers.PrimaryKeyRelatedField(
        queryset=Conductor.objects.all(), source="conductor", write_only=True, required=False, allow_null=True
    )

    class Meta:
        model = Trip
        fields = (
            "id",
            "bus", "bus_id",
            "route", "route_id",
            "conductor", "conductor_id",
            "departure_time", "arrival_time",
        )

    def validate(self, attrs):
        dep = attrs.get("departure_time")
        arr = attrs.get("arrival_time")
        if dep and arr and arr <= dep:
            raise ValidationError("Arrival time must be after departure time.")
        return attrs


# Booking, Ticket, Payment
class BookingSerializer(serializers.ModelSerializer):
    passenger = PassengerSerializer(read_only=True)
    passenger_id = serializers.PrimaryKeyRelatedField(
        queryset=Passenger.objects.all(), source="passenger", write_only=True, required=False
    )
    trip = TripSerializer(read_only=True)
    trip_id = serializers.PrimaryKeyRelatedField(
        queryset=Trip.objects.all(), source="trip", write_only=True
    )

    class Meta:
        model = Booking
        fields = ("id", "passenger", "passenger_id", "trip", "trip_id", "booking_time", "status")
        read_only_fields = ("booking_time",)

    def validate(self, attrs):
        """
        - Prevent duplicate passenger->trip bookings.
        - Prevent non-admin users from creating bookings on behalf of others.
        """
        passenger = attrs.get("passenger")
        trip = attrs.get("trip")

        request = self.context.get("request") if self.context else None
        user = getattr(request, "user", None)

        # If passenger + trip are both supplied (write path),
        # ensure duplicates do not exist.
        if passenger and trip:
            exists = Booking.objects.filter(passenger=passenger, trip=trip).exists()
            if exists:
                raise ValidationError("This passenger already has a booking for the selected trip.")

        # If passenger provided by client, ensure client is admin or it's their own passenger profile
        if passenger and user and user.is_authenticated:
            role = getattr(user, "role", None)
            role_name = getattr(role, "name", "").lower() if role else ""
            if role_name != "admin":
                # non-admins cannot create bookings for others
                if not hasattr(user, "passenger_profile") or passenger != user.passenger_profile:
                    raise ValidationError("You cannot create a booking for another passenger.")
        return attrs

    def create(self, validated_data):
        # allow views to set passenger automatically (e.g. serializer.save(passenger=...))
        return super().create(validated_data)


class TicketSerializer(serializers.ModelSerializer):
    booking = BookingSerializer(read_only=True)
    booking_id = serializers.PrimaryKeyRelatedField(
        queryset=Booking.objects.all(), source="booking", write_only=True
    )

    class Meta:
        model = Ticket
        fields = ("id", "booking", "booking_id", "issue_date", "seat_number")
        read_only_fields = ("issue_date",)

    def validate(self, attrs):
        booking = attrs.get("booking")
        seat = attrs.get("seat_number")

        request = self.context.get("request") if self.context else None
        user = getattr(request, "user", None)

        if booking and seat:
            trip = booking.trip
            # check seat uniqueness for the trip
            if Ticket.objects.filter(booking__trip=trip, seat_number=seat).exists():
                raise ValidationError("This seat is already taken for the selected trip.")

        # If the requester is a passenger, ensure they own the booking
        if user and user.is_authenticated:
            role = getattr(user, "role", None)
            role_name = getattr(role, "name", "").lower() if role else ""
            if role_name == "passenger":
                # passenger may only create tickets for their own bookings
                if not hasattr(user, "passenger_profile") or booking.passenger != user.passenger_profile:
                    raise ValidationError("You cannot create/issue a ticket for someone else's booking.")
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        return super().create(validated_data)


class PaymentSerializer(serializers.ModelSerializer):
    booking = BookingSerializer(read_only=True)
    booking_id = serializers.PrimaryKeyRelatedField(
        queryset=Booking.objects.all(), source="booking", write_only=True
    )

    class Meta:
        model = Payment
        fields = ("id", "booking", "booking_id", "amount", "payment_date", "status")
        read_only_fields = ("payment_date",)

    def validate_amount(self, value):
        if value <= 0:
            raise ValidationError("Payment amount must be positive.")
        return value
