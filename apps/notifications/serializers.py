"""
Serializers for notifications app
"""
from rest_framework import serializers
from apps.notifications.models import Notification, NotificationPreference, NotificationLog


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for Notification model"""
    notification_type_display = serializers.CharField(source='get_notification_type_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)

    class Meta:
        model = Notification
        fields = [
            'id', 'recipient', 'notification_type', 'notification_type_display',
            'title', 'message', 'priority', 'priority_display',
            'related_object_id', 'related_object_type',
            'is_read', 'read_at', 'email_sent', 'sms_sent', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'email_sent', 'sms_sent']


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    """Serializer for NotificationPreference model"""

    class Meta:
        model = NotificationPreference
        fields = [
            'id', 'user',
            # Email notifications
            'email_dispatched', 'email_arrived', 'email_out_for_delivery',
            'email_delivered', 'email_pickup', 'email_system',
            # In-app notifications
            'inapp_dispatched', 'inapp_arrived', 'inapp_out_for_delivery',
            'inapp_delivered', 'inapp_pickup', 'inapp_system',
            # SMS
            'sms_enabled',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class NotificationLogSerializer(serializers.ModelSerializer):
    """Serializer for NotificationLog model"""

    class Meta:
        model = NotificationLog
        fields = [
            'id', 'notification', 'channel', 'status',
            'error_message', 'sent_at', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

