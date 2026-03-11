"""
Admin configuration for staff app
"""
from django.contrib import admin
from apps.staff.models import StaffProfile


@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    list_display = ['employee_id', 'user', 'branch', 'position', 'is_active', 'created_at']
    list_filter = ['branch', 'position', 'is_active', 'created_at']
    search_fields = ['employee_id', 'user__username', 'user__first_name', 'user__last_name']
