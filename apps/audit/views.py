from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from apps.audit.models import AuditLog
from apps.audit.serializers import AuditLogSerializer


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Audit log viewset - read-only.
    Provides filtering, searching, and ordering for audit logs.
    """
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated]

    # Filtering, search, and ordering
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['user', 'action', 'model_name']
    search_fields = ['object_display', 'description']
    ordering_fields = ['created_at', 'action']
    ordering = ['-created_at']

    # Optional: disable pagination
    pagination_class = None