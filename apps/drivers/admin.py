"""
Admin configuration for drivers app
"""
from django.contrib import admin
from apps.drivers.models import DriverProfile


@admin.register(DriverProfile)
class DriverProfileAdmin(admin.ModelAdmin):
    list_display = ['driver_id', 'user', 'branch', 'vehicle_number', 'is_active', 'rating', 'created_at']
    list_filter = ['branch', 'vehicle_type', 'is_active', 'created_at']
    search_fields = ['driver_id', 'user__username', 'vehicle_number', 'license_number']
