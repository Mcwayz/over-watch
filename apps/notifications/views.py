"""
Views for notifications app
"""

from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from drf_spectacular.utils import extend_schema

from apps.notifications.models import (
    Notification,
    NotificationPreference,
    NotificationLog
)

from apps.notifications.serializers import (
    NotificationSerializer,
    NotificationPreferenceSerializer
)


@extend_schema(tags=["notifications"])
class NotificationViewSet(viewsets.ModelViewSet):
    """Notification management viewset"""

    permission_classes = [IsAuthenticated]
    serializer_class = NotificationSerializer

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    ]

    filterset_fields = ["notification_type", "is_read", "priority"]
    search_fields = ["title", "message"]
    ordering_fields = ["created_at", "priority"]
    ordering = ["-created_at"]

    def get_queryset(self):
        """Get notifications for current user"""
        return Notification.objects.filter(recipient=self.request.user)

    def perform_create(self, serializer):
        """Save notification with recipient"""
        notification = serializer.save(recipient=self.request.user)

        NotificationLog.objects.create(
            notification=notification,
            channel="inapp",
            status="sent"
            if self.request.user.notification_preference.inapp_dispatched
            else "pending"
        )

    @action(detail=True, methods=["post"])
    def mark_read(self, request, pk=None):
        """Mark notification as read"""
        notification = self.get_object()
        notification.is_read = True
        notification.read_at = timezone.now()
        notification.save()

        return Response({"detail": "Notification marked as read"})

    @action(detail=False, methods=["post"])
    def mark_all_read(self, request):
        """Mark all notifications as read"""
        notifications = self.get_queryset().filter(is_read=False)
        now = timezone.now()
        notifications.update(is_read=True, read_at=now)

        return Response({
            "detail": f"{notifications.count()} notifications marked as read"
        })

    @action(detail=False, methods=["get"])
    def unread_count(self, request):
        """Get count of unread notifications"""
        count = self.get_queryset().filter(is_read=False).count()
        return Response({"unread_count": count})

    @action(detail=False, methods=["get"])
    def unread(self, request):
        """Get all unread notifications"""
        notifications = self.get_queryset().filter(is_read=False)
        serializer = self.get_serializer(notifications, many=True)
        return Response(serializer.data)


@extend_schema(tags=["notifications"])
class NotificationPreferenceViewSet(viewsets.ModelViewSet):
    """Notification preference management viewset"""

    permission_classes = [IsAuthenticated]
    serializer_class = NotificationPreferenceSerializer

    def get_queryset(self):
        """Get preference for current user"""
        return NotificationPreference.objects.filter(user=self.request.user)

    def get_object(self):
        """Get or create preference for current user"""
        pref, created = NotificationPreference.objects.get_or_create(
            user=self.request.user
        )
        return pref

    def list(self, request, *args, **kwargs):
        """Get current user's preference"""
        return self.retrieve(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """Get preference"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        """Update preference"""
        partial = kwargs.pop("partial", False)
        instance = self.get_object()

        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=partial
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)


# Utility function to create notifications
def create_notification(
    recipient,
    notification_type,
    title,
    message,
    priority="normal",
    related_object_id=None,
    related_object_type=None,
):
    """Create a notification for a user"""

    notification = Notification.objects.create(
        recipient=recipient,
        notification_type=notification_type,
        title=title,
        message=message,
        priority=priority,
        related_object_id=related_object_id,
        related_object_type=related_object_type,
    )

    return notification