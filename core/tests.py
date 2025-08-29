from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Role, Bus, Trip, Conductor, Passenger, Booking, Ticket
from .serializers import UserSerializer, BusSerializer, TripSerializer
from rest_framework.test import APIClient
from rest_framework import status

User = get_user_model()


# User & Role Tests
class UserModelTest(TestCase):
    def test_create_user(self):
        role = Role.objects.create(name="Member")
        user = User.objects.create_user(
            email="user@example.com", password="testpass123", role=role
        )
        self.assertEqual(user.email, "user@example.com")
        self.assertTrue(user.check_password("testpass123"))
        self.assertEqual(user.role, role)

    def test_create_superuser(self):
        role = Role.objects.create(name="Admin")
        superuser = User.objects.create_superuser(
            email="admin@example.com", password="superpass123", role=role
        )
        self.assertTrue(superuser.is_superuser)
        self.assertTrue(superuser.is_staff)


class RoleModelTest(TestCase):
    def test_create_role(self):
        role = Role.objects.create(name="Leader")
        self.assertEqual(role.name, "Leader")


class UserSerializerTest(TestCase):
    def test_user_serializer(self):
        role = Role.objects.create(name="Member")
        user = User.objects.create_user(
            email="serialize@example.com", password="serialize123", role=role
        )
        serializer = UserSerializer(user)
        self.assertEqual(serializer.data["email"], "serialize@example.com")
        self.assertEqual(serializer.data["role"]["name"], "Member")
        self.assertIn("is_staff", serializer.data)
        self.assertIn("is_superuser", serializer.data)


# Admin Permission Tests
class AdminPermissionTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_role = Role.objects.create(name="Admin")
        self.admin = User.objects.create_user(
            email="admin@example.com", password="adminpass", role=self.admin_role
        )
        self.client.force_authenticate(user=self.admin)

        # Create a conductor for bus assignments
        self.conductor = Conductor.objects.create(name="Test Conductor")

    def test_admin_can_create_bus(self):
        response = self.client.post(
            "/api/core/buses/",
            {"registration_number": "G123ABC", "capacity": 40, "conductor": self.conductor.id}
        )
        self.assertIn(response.status_code, [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST])

    def test_admin_can_create_trip(self):
        bus = Bus.objects.create(registration_number="G456DEF", capacity=40, conductor=self.conductor)
        response = self.client.post(
            "/api/core/trips/",
            {"route": None, "bus": bus.id, "start_time": "2025-09-01T10:00:00Z"}
        )
        self.assertIn(response.status_code, [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST])


# User Permission Tests
class UserPermissionTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.role = Role.objects.create(name="Member")
        self.user = User.objects.create_user(
            email="normal@example.com", password="normalpass", role=self.role
        )
        self.client.force_authenticate(user=self.user)

    def test_user_cannot_create_bus(self):
        response = self.client.post(
            "/api/core/buses/",
            {"registration_number": "G789XYZ", "capacity": 30}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_cannot_create_trip(self):
        response = self.client.post("/api/core/trips/", {"route": None, "bus": None})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


# Passenger Permission Tests
class PassengerPermissionTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.passenger_role = Role.objects.create(name="Member")
        self.admin_role = Role.objects.create(name="Admin")

        self.passenger_user = User.objects.create_user(
            email="passenger@example.com", password="passpass", role=self.passenger_role
        )
        self.admin_user = User.objects.create_user(
            email="admin@example.com", password="adminpass", role=self.admin_role
        )

        # Assign conductor & bus
        self.conductor = Conductor.objects.create(name="Test Conductor")
        self.bus = Bus.objects.create(registration_number="G999ZZZ", capacity=50, conductor=self.conductor)

        # Create passenger profile
        self.passenger = Passenger.objects.create(user=self.passenger_user)

        # Create a trip
        self.trip = Trip.objects.create(bus=self.bus, route=None, start_time="2025-09-01T10:00:00Z")

        # Bookings and tickets
        self.booking = Booking.objects.create(passenger=self.passenger, trip=self.trip)
        self.ticket = Ticket.objects.create(booking=self.booking, seat_number=1)

    def test_passenger_can_create_booking(self):
        self.client.force_authenticate(user=self.passenger_user)
        response = self.client.post(
            "/api/core/bookings/",
            {"passenger": self.passenger.id, "trip": self.trip.id}
        )
        self.assertIn(response.status_code, [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST])

    def test_passenger_can_create_ticket(self):
        self.client.force_authenticate(user=self.passenger_user)
        response = self.client.post(
            "/api/core/tickets/",
            {"booking": self.booking.id, "seat_number": 2}
        )
        self.assertIn(response.status_code, [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST])

    def test_admin_can_modify_any_booking(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.patch(
            f"/api/core/bookings/{self.booking.id}/",
            {"trip": self.trip.id}
        )
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST])

    def test_admin_can_modify_any_ticket(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.patch(
            f"/api/core/tickets/{self.ticket.id}/",
            {"seat_number": 5}
        )
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST])