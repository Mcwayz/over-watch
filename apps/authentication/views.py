"""Views for authentication app"""

from rest_framework import status, viewsets, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import AllowAny, IsAuthenticated
from drf_spectacular.utils import extend_schema

from apps.authentication.models import CustomUser, Role
from apps.authentication.serializers import (
    CustomTokenObtainPairSerializer,
    CustomUserSerializer,
    CustomUserCreateSerializer,
    LoginSerializer,
    ChangePasswordSerializer,
    RoleSerializer,
)

from utils.audit import AuditLogger
from utils.helpers import get_client_ip


@extend_schema(tags=["authentication"])
class CustomTokenObtainPairView(TokenObtainPairView):
    """Custom JWT token view"""
    serializer_class = CustomTokenObtainPairSerializer


@extend_schema(tags=["authentication"])
class LoginView(generics.GenericAPIView):
    """User login view"""
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]

        ip_address = get_client_ip(request)
        AuditLogger.log_login(user, ip_address=ip_address)

        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(user)

        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": CustomUserSerializer(user).data
        })


@extend_schema(tags=["authentication"])
class RegisterView(generics.CreateAPIView):
    """User registration view"""
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserCreateSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        user = serializer.save()

        ip_address = get_client_ip(self.request)

        AuditLogger.log_action(
            user=None,
            action="CREATE",
            model_name="CustomUser",
            object_id=str(user.id),
            object_display=user.username,
            description=f"New user {user.username} registered",
            ip_address=ip_address
        )


class UserViewSet(viewsets.ModelViewSet):
    """User management viewset"""
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "create":
            return CustomUserCreateSerializer
        return CustomUserSerializer

    @action(detail=False, methods=["get"])
    def current_user(self, request):
        """Get current user details"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=["post"])
    def change_password(self, request):
        """Change user password"""

        user = request.user
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if not user.check_password(serializer.validated_data["old_password"]):
            return Response(
                {"old_password": "Invalid password"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.set_password(serializer.validated_data["new_password"])
        user.save()

        ip_address = get_client_ip(request)

        AuditLogger.log_action(
            user=user,
            action="UPDATE",
            model_name="CustomUser",
            object_id=str(user.id),
            object_display=user.username,
            description="Password changed",
            ip_address=ip_address
        )

        return Response({"detail": "Password changed successfully"})


class RoleViewSet(viewsets.ReadOnlyModelViewSet):
    """Role viewset"""
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated]