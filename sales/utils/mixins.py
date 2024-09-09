from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication


class AuthenticatedViewMixin:
    """
    Enforces JWT authentication and `IsAuthenticated` permission on API views.
    """

    authentication_classes = [SessionAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated]
