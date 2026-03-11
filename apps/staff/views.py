"""
Views for staff app
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from apps.staff.models import StaffProfile
from apps.staff.serializers import StaffProfileSerializer, StaffCreateUpdateSerializer
from utils.audit import AuditLogger
from utils.helpers import get_client_ip, generate_employee_id


class StaffViewSet(viewsets.ModelViewSet):
    """Staff management viewset"""
    queryset = StaffProfile.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['branch', 'position', 'is_active']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'employee_id']
    ordering_fields = ['hire_date', 'created_at']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return StaffCreateUpdateSerializer
        return StaffProfileSerializer

    def perform_create(self, serializer):
        # Auto-generate employee ID if not provided
        if 'employee_id' not in serializer.validated_data:
            serializer.validated_data['employee_id'] = generate_employee_id('staff')

        staff = serializer.save()
        ip_address = get_client_ip(self.request)
        AuditLogger.log_action(
            user=self.request.user,
            action='CREATE',
            model_name='StaffProfile',
            object_id=str(staff.id),
            object_display=staff.employee_id,
            description=f"Staff {staff.user.get_full_name()} created",
            ip_address=ip_address
        )

    def perform_update(self, serializer):
        staff = serializer.save()
        ip_address = get_client_ip(self.request)
        AuditLogger.log_action(
            user=self.request.user,
            action='UPDATE',
            model_name='StaffProfile',
            object_id=str(staff.id),
            object_display=staff.employee_id,
            description=f"Staff {staff.user.get_full_name()} updated",
            ip_address=ip_address
        )

    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Deactivate staff"""
        staff = self.get_object()
        staff.is_active = False
        staff.save()

        ip_address = get_client_ip(request)
        AuditLogger.log_action(
            user=request.user,
            action='UPDATE',
            model_name='StaffProfile',
            object_id=str(staff.id),
            object_display=staff.employee_id,
            description=f"Staff {staff.user.get_full_name()} deactivated",
            ip_address=ip_address
        )

        return Response({'detail': 'Staff deactivated'})
