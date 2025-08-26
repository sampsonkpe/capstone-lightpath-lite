from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.apps import apps


# Custom User Manager
class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Ensure superuser has is_staff and is_superuser, and assign Admin role by default.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        # Assign Admin role if not provided
        try:
            Role = apps.get_model("core", "Role")
            admin_role, _ = Role.objects.get_or_create(name="Admin")
            extra_fields.setdefault("role", admin_role)
        except Exception:
            # If Role model isn't ready (migrations etc.), continue without it;
            # caller can set role later via admin.
            pass

        return self.create_user(email, password, **extra_fields)


# Core User + Role
class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)  # e.g., Admin, Passenger, Conductor

    def __str__(self):
        return self.name


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email


# Passenger & Conductor Profiles
class Passenger(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="passenger_profile")
    phone_number = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"Passenger: {self.user.email}"


class Conductor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="conductor_profile")
    employee_id = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return f"Conductor: {self.user.email}"


# Transport Entities
class Bus(models.Model):
    number_plate = models.CharField(max_length=20, unique=True)
    capacity = models.PositiveIntegerField()
    conductor = models.ForeignKey(Conductor, on_delete=models.SET_NULL, null=True, related_name="buses")

    def __str__(self):
        return f"Bus {self.number_plate} (Capacity: {self.capacity})"


class Route(models.Model):
    start_point = models.CharField(max_length=100)
    end_point = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.start_point} → {self.end_point}"


class Trip(models.Model):
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, related_name="trips")
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name="trips")
    conductor = models.ForeignKey(Conductor, on_delete=models.SET_NULL, null=True, related_name="trips")
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()

    class Meta:
        ordering = ["departure_time"]

    def __str__(self):
        return f"Trip {self.id} | {self.route} | {self.departure_time}"


# Booking System
class Booking(models.Model):
    passenger = models.ForeignKey(Passenger, on_delete=models.CASCADE, related_name="bookings")
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name="bookings")
    booking_time = models.DateTimeField(default=timezone.now)
    status = models.CharField(
        max_length=20,
        choices=[("PENDING", "Pending"), ("CONFIRMED", "Confirmed"), ("CANCELLED", "Cancelled")],
        default="PENDING"
    )

    class Meta:
        unique_together = ("passenger", "trip")
        ordering = ["-booking_time"]

    def __str__(self):
        return f"Booking {self.id} by {self.passenger.user.email} ({self.get_status_display()})"


class Ticket(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name="ticket")
    issue_date = models.DateTimeField(default=timezone.now)
    seat_number = models.CharField(max_length=10)

    def clean(self):
        # ensure seat uniqueness for the trip (defensive check)
        trip = getattr(self.booking, "trip", None)
        if trip and Ticket.objects.filter(booking__trip=trip, seat_number=self.seat_number).exclude(pk=self.pk).exists():
            raise ValidationError("This seat is already taken for the selected trip.")

    def save(self, *args, **kwargs):
        # call clean to enforce the defensive check
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Ticket {self.id} | Seat {self.seat_number}"


class Payment(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name="payments")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(default=timezone.now)
    status = models.CharField(
        max_length=20,
        choices=[("PENDING", "Pending"), ("COMPLETED", "Completed"), ("FAILED", "Failed")],
        default="PENDING"
    )

    class Meta:
        ordering = ["-payment_date"]

    def __str__(self):
        return f"Payment {self.id} - {self.amount} ({self.status})"
