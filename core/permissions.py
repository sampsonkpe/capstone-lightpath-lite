from rest_framework import permissions
from rest_framework.permissions import SAFE_METHODS


def _role_name(request):
    """Helper to safely get the role name (lowercase) for the requesting user."""
    user = getattr(request, "user", None)
    if not user or not getattr(user, "is_authenticated", False):
        return ""
    role = getattr(user, "role", None)
    if not role:
        return ""
    return getattr(role, "name", "").lower()


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return _role_name(request) == "admin"


class IsConductor(permissions.BasePermission):
    def has_permission(self, request, view):
        return _role_name(request) == "conductor"


class IsPassenger(permissions.BasePermission):
    def has_permission(self, request, view):
        return _role_name(request) == "passenger"


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Allows object-level access to the owner (passenger or user) or an Admin.
    Works with objects that have one of these attributes:
      - user (User)
      - passenger (Passenger) -> booking passenger
      - booking (Booking) -> used to find owner via booking.passenger.user
    """
    def _get_owner_user(self, obj):
        # Booking has passenger -> passenger.user
        if hasattr(obj, "passenger"):
            return getattr(obj.passenger, "user", None)
        # Ticket has booking -> booking.passenger.user
        if hasattr(obj, "booking") and hasattr(obj.booking, "passenger"):
            return getattr(obj.booking.passenger, "user", None)
        # Payment has booking -> booking.passenger.user
        if hasattr(obj, "booking") and hasattr(obj.booking, "passenger"):
            return getattr(obj.booking.passenger, "user", None)
        # Some objects may have 'user' directly
        if hasattr(obj, "user"):
            return getattr(obj, "user", None)
        return None

    def has_object_permission(self, request, view, obj):
        if _role_name(request) == "admin":
            return True
        owner_user = self._get_owner_user(obj)
        return owner_user == getattr(request, "user", None)


class IsAdminOrReadOnly(permissions.BasePermission):
    """Allow safe methods for authenticated users; only Admins may perform unsafe methods."""
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return request.user.is_authenticated
        return _role_name(request) == "admin"


class IsAdminOrConductorOrReadOnly(permissions.BasePermission):
    """
    Allow safe methods for authenticated users;
    For unsafe methods, allow if Admin or Conductor.
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return request.user.is_authenticated
        rn = _role_name(request)
        return rn == "admin" or rn == "conductor"
