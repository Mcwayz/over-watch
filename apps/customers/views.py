"""
Views for customers app
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from apps.customers.models import CustomerProfile
from apps.customers.serializers import CustomerProfileSerializer, CustomerCreateUpdateSerializer
from utils.audit import AuditLogger
from utils.helpers import get_client_ip, generate_customer_id


class CustomerViewSet(viewsets.ModelViewSet):
    """Customer management viewset"""
    queryset = CustomerProfile.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['city', 'preferred_branch', 'is_verified']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'customer_id', 'phone_number']
    ordering_fields = ['total_parcels_sent', 'total_spent', 'created_at']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return CustomerCreateUpdateSerializer
        return CustomerProfileSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        return super().get_permissions()

    def perform_create(self, serializer):
        customer = serializer.save()
        ip_address = get_client_ip(self.request)
        AuditLogger.log_action(
            user=None,
            action='CREATE',
            model_name='CustomerProfile',
            object_id=str(customer.id),
            object_display=customer.customer_id,
            description=f"Customer {customer.user.get_full_name()} registered",
            ip_address=ip_address
        )

    def perform_update(self, serializer):
        customer = serializer.save()
        ip_address = get_client_ip(self.request)
        AuditLogger.log_action(
            user=self.request.user,
            action='UPDATE',
            model_name='CustomerProfile',
            object_id=str(customer.id),
            object_display=customer.customer_id,
            description=f"Customer profile updated",
            ip_address=ip_address
        )

    @action(detail=False, methods=['get'])
    def my_profile(self, request):
        """Get current customer's profile"""
        try:
            customer = request.user.customer_profile
            serializer = self.get_serializer(customer)
            return Response(serializer.data)
        except:
            return Response({'detail': 'Not a customer'}, status=status.HTTP_403_FORBIDDEN)
