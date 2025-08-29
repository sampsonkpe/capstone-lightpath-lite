from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.apps import apps
from decimal import Decimal
import uuid


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


class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)
    
    class Meta:
        verbose_name = "Role"
        verbose_name_plural = "Roles"

    def __str__(self):
        return self.name


class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ("admin", "Admin"),
        ("passenger", "Passenger"),
        ("conductor", "Conductor"),
    )
    id = models.BigAutoField(primary_key=True)
    email = models.EmailField(unique=True)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
            
    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return self.email


class Passenger(models.Model):
    passenger_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="passenger_profile")
    full_name = models.CharField(max_length=100, default="Passenger")
    contact_number = models.CharField(max_length=20, default="UNKNOWN")
    username = models.CharField(max_length=50, unique=True, blank=True)
            
    class Meta:
        verbose_name = "Passenger"
        verbose_name_plural = "Passengers"

    def save(self, *args, **kwargs):
        # Auto-generate a unique username if not provided
        if not self.username:
            while True:
                candidate = f"passenger_{uuid.uuid4().hex[:8]}"
                if not self.__class__.objects.filter(username=candidate).exists():
                    self.username = candidate
                    break
        super().save(*args, **kwargs)

    def __str__(self):
        return self.full_name


class Conductor(models.Model):
    conductor_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="conductor_profile")
    full_name = models.CharField(max_length=100, default="Conductor")
    contact_number = models.CharField(max_length=20, default="UNKNOWN")
    employee_id = models.CharField(max_length=20, unique=True, blank=True)

    class Meta:
        verbose_name = "Conductor"
        verbose_name_plural = "Conductors"

    def save(self, *args, **kwargs):
        if not self.employee_id:
            while True:
                candidate = f"conductor_{uuid.uuid4().hex[:8]}"
                if not self.__class__.objects.filter(employee_id=candidate).exists():
                    self.employee_id = candidate
                    break
        super().save(*args, **kwargs)

    def __str__(self):
        return self.full_name


class Bus(models.Model):
    bus_id = models.AutoField(primary_key=True)
    conductor = models.OneToOneField(Conductor, on_delete=models.CASCADE, related_name="bus")
    registration_number = models.CharField(max_length=20, unique=True, default="BUS-UNKNOWN")
    capacity = models.PositiveIntegerField(default=20)
            
    class Meta:
        verbose_name = "Bus"
        verbose_name_plural = "Buses"

    def __str__(self):
        return f"{self.registration_number} - Capacity {self.capacity}"


class Route(models.Model):
    route_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, default="Route Name")
    start_point = models.CharField(max_length=100, default="Start")
    end_point = models.CharField(max_length=100, default="End")
            
    class Meta:
        verbose_name = "Route"
        verbose_name_plural = "Routes"

    def __str__(self):
        return f"{self.name}: {self.start_point} → {self.end_point}"


class Weather(models.Model):
    weather_id = models.AutoField(primary_key=True)
    condition = models.CharField(max_length=100, default="Clear")
    temperature = models.FloatField(default=25.0)
    timestamp = models.DateTimeField(default=timezone.now)
            
    class Meta:
        verbose_name = "Weather"
        verbose_name_plural = "Weather"

    def __str__(self):
        return f"{self.condition} at {self.temperature}°C ({self.timestamp})"


class Trip(models.Model):
    trip_id = models.AutoField(primary_key=True)
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, related_name="trips")
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name="trips")
    conductor = models.ForeignKey(Conductor, on_delete=models.CASCADE, related_name="trips")
    weather = models.ForeignKey(Weather, on_delete=models.SET_NULL, null=True, blank=True, related_name="trips")
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(default=timezone.now)
            
    class Meta:
        verbose_name = "Trip"
        verbose_name_plural = "Trips"

    def __str__(self):
        return f"Trip {self.trip_id} on {self.route.name}"


class Booking(models.Model):
    booking_id = models.AutoField(primary_key=True)
    passenger = models.ForeignKey(Passenger, on_delete=models.CASCADE, related_name="bookings")
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name="bookings")
    booking_time = models.DateTimeField(auto_now_add=True)
            
    class Meta:
        verbose_name = "Booking"
        verbose_name_plural = "Bookings"

    def __str__(self):
        return f"Booking {self.booking_id} by {self.passenger.full_name}"


class Payment(models.Model):
    payment_id = models.AutoField(primary_key=True)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name="payments")
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    status = models.CharField(max_length=50, default="PENDING")
    payment_date = models.DateTimeField(default=timezone.now)
            
    class Meta:
        verbose_name = "Payment"
        verbose_name_plural = "Payments"

    def __str__(self):
        return f"Payment {self.payment_id} - {self.status}"


class Ticket(models.Model):
    ticket_id = models.AutoField(primary_key=True)
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name="tickets")
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name="tickets")
    seat_number = models.CharField(max_length=10, default="0")

    class Meta:
        verbose_name = "Ticket"
        verbose_name_plural = "Tickets"
        constraints = [
            models.UniqueConstraint(fields=['trip', 'seat_number'], name='unique_trip_seat')
        ]

    def __str__(self):
        return f"Ticket {self.ticket_id} - Seat {self.seat_number}"
