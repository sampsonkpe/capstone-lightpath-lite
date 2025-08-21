from rest_framework import serializers
from .models import (
    User, Role, Passenger, Conductor,
    Bus, Route, Trip, Booking, Ticket, Payment
)

# User & Role
class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ("id", "name")

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "role", "is_active", "is_staff", "date_joined")

class PassengerSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = Passenger
        fields = ("id", "user", "phone_number")

class ConductorSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = Conductor
        fields = ("id", "user", "employee_id")


# Transport Models
class BusSerializer(serializers.ModelSerializer):
    conductor = ConductorSerializer(read_only=True)
    class Meta:
        model = Bus
        fields = ("id", "number_plate", "capacity", "conductor")


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = ("id", "start_point", "end_point", "description")


class TripSerializer(serializers.ModelSerializer):
    bus = BusSerializer(read_only=True)
    route = RouteSerializer(read_only=True)
    conductor = ConductorSerializer(read_only=True)

    class Meta:
        model = Trip
        fields = ("id", "bus", "route", "conductor", "departure_time", "arrival_time")


class BookingSerializer(serializers.ModelSerializer):
    passenger = PassengerSerializer(read_only=True)
    trip = TripSerializer(read_only=True)

    class Meta:
        model = Booking
        fields = ("id", "passenger", "trip", "booking_time", "status")


class TicketSerializer(serializers.ModelSerializer):
    booking = BookingSerializer(read_only=True)

    class Meta:
        model = Ticket
        fields = ("id", "booking", "issue_date", "seat_number")


class PaymentSerializer(serializers.ModelSerializer):
    booking = BookingSerializer(read_only=True)

    class Meta:
        model = Payment
        fields = ("id", "booking", "amount", "payment_date", "status")
