from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.apps import apps


# Custom User Manager
class UserManager(BaseUserManager):
    def create_user(self, email, password=None, role=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, role=role, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        try:
            RoleModel = apps.get_model("core", "Role")
            admin_role, _ = RoleModel.objects.get_or_create(name="Admin")
            extra_fields.setdefault("role", admin_role)
        except Exception:
            pass

        return self.create_user(email, password, **extra_fields)


# Core User + Role
class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email


# Passenger & Conductor
class Passenger(models.Model):
    passenger_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="passenger_profiles")
    full_name = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=20)
    username = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.full_name


class Conductor(models.Model):
    conductor_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="conductor_profiles")
    full_name = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=20)

    def __str__(self):
        return self.full_name


# Bus
class Bus(models.Model):
    bus_id = models.AutoField(primary_key=True)
    conductor = models.ForeignKey(Conductor, on_delete=models.CASCADE, related_name="buses")
    registration_number = models.CharField(max_length=50, unique=True)
    capacity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.registration_number} - Capacity {self.capacity}"


# Route
class Route(models.Model):
    route_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    start_point = models.CharField(max_length=100)
    end_point = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name}: {self.start_point} → {self.end_point}"


# Weather
class Weather(models.Model):
    weather_id = models.AutoField(primary_key=True)
    condition = models.CharField(max_length=100)
    temperature = models.FloatField()
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.condition} at {self.temperature}°C ({self.timestamp})"


# Trip
class Trip(models.Model):
    trip_id = models.AutoField(primary_key=True)
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, related_name="trips")
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name="trips")
    conductor = models.ForeignKey(Conductor, on_delete=models.CASCADE, related_name="trips")
    weather = models.ForeignKey(Weather, on_delete=models.SET_NULL, null=True, blank=True, related_name="trips")
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    def __str__(self):
        return f"Trip {self.trip_id} on {self.route.name}"


# Booking
class Booking(models.Model):
    booking_id = models.AutoField(primary_key=True)
    passenger = models.ForeignKey(Passenger, on_delete=models.CASCADE, related_name="bookings")
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name="bookings")
    booking_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Booking {self.booking_id} by {self.passenger.full_name}"


# Payment
class Payment(models.Model):
    payment_id = models.AutoField(primary_key=True)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name="payments")
    amount = models.FloatField()
    status = models.CharField(max_length=50)
    payment_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Payment {self.payment_id} - {self.status}"


# Ticket
class Ticket(models.Model):
    ticket_id = models.AutoField(primary_key=True)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name="tickets")
    seat_number = models.CharField(max_length=10)

    def __str__(self):
        return f"Ticket {self.ticket_id} - Seat {self.seat_number}"
