from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Role
from .serializers import UserSerializer
from rest_framework.test import APIClient
from rest_framework import status


User = get_user_model()


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


class PermissionTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.role = Role.objects.create(name="Member")
        self.user = User.objects.create_user(
            email="normal@example.com", password="normalpass", role=self.role
        )
        self.admin_role = Role.objects.create(name="Admin")
        self.admin = User.objects.create_superuser(
            email="admin@example.com", password="adminpass", role=self.admin_role
        )

    def test_admin_can_create_role(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post("/api/core/roles/", {"name": "NewRole"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_user_cannot_create_role(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post("/api/core/roles/", {"name": "BlockedRole"})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
