"""
Admin configuration for audit app
"""
from django.contrib import admin
from apps.audit.models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'action', 'model_name', 'object_display', 'created_at']
    list_filter = ['action', 'model_name', 'created_at']
    search_fields = ['user__username', 'object_display', 'description']
    readonly_fields = ['id', 'user', 'action', 'model_name', 'object_id', 'object_display',
                       'description', 'ip_address', 'user_agent', 'old_values', 'new_values',
                       'status_code', 'created_at']
