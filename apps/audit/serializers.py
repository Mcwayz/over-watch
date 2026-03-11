"""
Serializers for audit app
"""
from rest_framework import serializers
from apps.audit.models import AuditLog


class AuditLogSerializer(serializers.ModelSerializer):
    """Serializer for AuditLog model"""
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    action_display = serializers.CharField(source='get_action_display', read_only=True)

    class Meta:
        model = AuditLog
        fields = [
            'id', 'user', 'user_name', 'action', 'action_display', 'model_name',
            'object_id', 'object_display', 'description', 'ip_address', 'user_agent',
            'old_values', 'new_values', 'status_code', 'created_at'
        ]
        read_only_fields = fields  # All fields are read-only for audit logs
