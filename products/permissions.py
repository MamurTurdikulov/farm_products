from rest_framework import permissions

class IsSellerOrReadOnly(permissions.BasePermission):
    """
    Allows read-only access to any user (including unauthenticated).
    Write access is restricted to authenticated users with `is_seller=True`.
    Object-level write access is further restricted to the object's owner (seller).
    """

    def has_permission(self, request, view):
        # Allow read-only methods for everyone
        if request.method in permissions.SAFE_METHODS:
            return True

        # Require authentication and seller status for write operations
        return (
            request.user.is_authenticated
            and hasattr(request.user, 'is_seller')
            and request.user.is_seller
        )

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed for any request
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the seller who owns the object
        return (
            hasattr(obj, 'seller')
            and obj.seller == request.user
        )