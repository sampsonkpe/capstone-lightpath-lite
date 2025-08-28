from rest_framework import serializers
from django.db import transaction
from rest_framework.exceptions import ValidationError

from .models import (
    User, Role, Passenger, Conductor,
    Bus, Route, Trip, Booking, Ticket, Payment, Weather
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
        fields = ("id", "user", "user_id", "full_name", "username", "contact_number")


class ConductorSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source="user", write_only=True
    )

    class Meta:
        model = Conductor
        fields = ("id", "user", "user_id", "full_name", "contact_number")


# Transport Models
class BusSerializer(serializers.ModelSerializer):
    conductor = ConductorSerializer(read_only=True)
    conductor_id = serializers.PrimaryKeyRelatedField(
        queryset=Conductor.objects.all(), source="conductor", write_only=True, required=False, allow_null=True
    )

    class Meta:
        model = Bus
        fields = ("id", "registration_number", "capacity", "conductor", "conductor_id")

    def validate_capacity(self, value):
        if value <= 0:
            raise ValidationError("Bus capacity must be greater than zero.")
        return value


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = ("id", "name", "start_point", "end_point")

class WeatherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Weather
        fields = ("id", "condition", "temperature", "timestamp")

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
    weather = WeatherSerializer(read_only=True)
    weather_id = serializers.PrimaryKeyRelatedField(
        queryset=Weather.objects.all(), source="weather", write_only=True, required=False, allow_null=True
    )

    class Meta:
        model = Trip
        fields = (
            "id",
            "bus", "bus_id",
            "route", "route_id",
            "conductor", "conductor_id",
            "weather", "weather_id",
            "start_time", "end_time",
        )

    def validate(self, attrs):
        start = attrs.get("start_time")
        end = attrs.get("end_time")
        if start and end and end <= start:
            raise ValidationError("End time must be after start time.")
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
        fields = ("id", "passenger", "passenger_id", "trip", "trip_id", "booking_time")
        read_only_fields = ("booking_time",)

    def validate(self, attrs):
        passenger = attrs.get("passenger")
        trip = attrs.get("trip")

        request = self.context.get("request") if self.context else None
        user = getattr(request, "user", None)

        # Prevent duplicate bookings for same passenger & trip
        if passenger and trip:
            exists = Booking.objects.filter(passenger=passenger, trip=trip).exists()
            if exists:
                raise ValidationError("This passenger already has a booking for the selected trip.")

        # Role-based restriction: non-admins cannot create bookings for others
        if passenger and user and user.is_authenticated:
            role_name = getattr(getattr(user, "role", None), "name", "").lower()
            if role_name != "admin":
                # Non-admins must book only for themselves
                if not hasattr(user, "passenger_profile") or passenger not in user.passenger_profiles.all():
                    raise ValidationError("You cannot create a booking for another passenger.")
        return attrs

    def create(self, validated_data):
        # Allow views to set passenger automatically if needed
        return super().create(validated_data)


class TicketSerializer(serializers.ModelSerializer):
    booking = BookingSerializer(read_only=True)
    booking_id = serializers.PrimaryKeyRelatedField(
        queryset=Booking.objects.all(), source="booking", write_only=True
    )

    class Meta:
        model = Ticket
        fields = ("id", "booking", "booking_id", "seat_number")

    def validate(self, attrs):
        booking = attrs.get("booking")
        seat = attrs.get("seat_number")
        if booking and seat and Ticket.objects.filter(booking__trip=booking.trip, seat_number=seat).exists():
            raise ValidationError("This seat is already taken for the selected trip.")
        return attrs


class PaymentSerializer(serializers.ModelSerializer):
    booking = BookingSerializer(read_only=True)
    booking_id = serializers.PrimaryKeyRelatedField(
        queryset=Booking.objects.all(), source="booking", write_only=True
    )

    class Meta:
        model = Payment
        fields = ("id", "booking", "booking_id", "amount", "status", "payment_date")
        read_only_fields = ("payment_date",)

    def validate_amount(self, value):
        if value <= 0:
            raise ValidationError("Payment amount must be positive.")
        return value
