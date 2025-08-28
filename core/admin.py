from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (User, Role, Passenger, Conductor, Bus, Route, Trip, Booking, Payment, Ticket, Weather)


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ("email", "role", "is_staff", "is_active", "date_joined")
    list_filter = ("role", "is_staff", "is_active")
    search_fields = ("email",)
    ordering = ("email",)
    readonly_fields = ("date_joined",)


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Passenger)
class PassengerAdmin(admin.ModelAdmin):
    list_display = ("passenger_id", "user", "full_name", "username", "contact_number")
    search_fields = ("full_name", "username", "user__email")


@admin.register(Conductor)
class ConductorAdmin(admin.ModelAdmin):
    list_display = ("conductor_id", "user", "full_name", "contact_number")
    search_fields = ("full_name", "user__email")


@admin.register(Bus)
class BusAdmin(admin.ModelAdmin):
    list_display = ("bus_id", "registration_number", "capacity", "conductor")
    search_fields = ("registration_number", "conductor__full_name")
    list_filter = ("conductor",)


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ("route_id", "name", "start_point", "end_point")
    search_fields = ("name", "start_point", "end_point")


@admin.register(Weather)
class WeatherAdmin(admin.ModelAdmin):
    list_display = ("weather_id", "condition", "temperature", "timestamp")
    search_fields = ("condition",)
    list_filter = ("condition",)


@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = ("trip_id", "route", "bus", "conductor", "weather", "start_time", "end_time")
    search_fields = ("route__name", "bus__registration_number", "conductor__full_name")
    list_filter = ("route", "conductor", "bus")


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("booking_id", "passenger", "trip", "booking_time")
    search_fields = ("passenger__full_name", "trip__route__name")
    list_filter = ("trip",)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("payment_id", "booking", "amount", "status", "payment_date")
    search_fields = ("booking__passenger__full_name",)
    list_filter = ("status",)


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ("ticket_id", "booking", "seat_number")
    search_fields = ("booking__passenger__full_name", "seat_number")
    list_filter = ("booking__trip",)

