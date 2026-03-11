from django.contrib import admin
from apps.vehicles.models import Vehicle, VehicleMaintenance


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ['vehicle_number', 'vehicle_name', 'vehicle_type', 'license_plate', 'current_branch', 'status', 'is_active']
    list_filter = ['vehicle_type', 'status', 'is_active', 'current_branch']
    search_fields = ['vehicle_number', 'vehicle_name', 'license_plate']
    raw_id_fields = ['current_branch', 'assigned_driver']


@admin.register(VehicleMaintenance)
class VehicleMaintenanceAdmin(admin.ModelAdmin):
    list_display = ['vehicle', 'maintenance_type', 'performed_date', 'cost', 'performed_by']
    list_filter = ['maintenance_type', 'performed_date']
    search_fields = ['vehicle__vehicle_number', 'description']
    raw_id_fields = ['vehicle']

