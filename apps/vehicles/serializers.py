"""
Serializers for vehicles app
"""
from rest_framework import serializers
from apps.vehicles.models import Vehicle, VehicleMaintenance


class VehicleMaintenanceSerializer(serializers.ModelSerializer):
    """Serializer for VehicleMaintenance model"""
    vehicle_name = serializers.CharField(source='vehicle.vehicle_name', read_only=True)
    maintenance_type_display = serializers.CharField(source='get_maintenance_type_display', read_only=True)

    class Meta:
        model = VehicleMaintenance
        fields = [
            'id', 'vehicle', 'vehicle_name', 'maintenance_type', 'maintenance_type_display',
            'description', 'cost', 'performed_by', 'performed_date', 'next_due_date', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'vehicle_name', 'maintenance_type_display']


class VehicleSerializer(serializers.ModelSerializer):
    """Serializer for Vehicle model"""
    current_branch_name = serializers.CharField(source='current_branch.name', read_only=True)
    assigned_driver_name = serializers.CharField(source='assigned_driver.user.get_full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    vehicle_type_display = serializers.CharField(source='get_vehicle_type_display', read_only=True)
    parcel_count = serializers.IntegerField(read_only=True)
    total_weight_kg = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Vehicle
        fields = [
            'id', 'vehicle_number', 'vehicle_name', 'vehicle_type', 'vehicle_type_display',
            'license_plate', 'capacity_kg', 'current_branch', 'current_branch_name',
            'assigned_driver', 'assigned_driver_name', 'status', 'status_display',
            'current_latitude', 'current_longitude', 'current_location', 'fuel_level',
            'is_active', 'last_maintenance_date', 'next_maintenance_date',
            'parcel_count', 'total_weight_kg', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'current_branch_name',
            'assigned_driver_name', 'status_display', 'vehicle_type_display',
            'parcel_count', 'total_weight_kg'
        ]


class VehicleListSerializer(serializers.ModelSerializer):
    """Light serializer for listing vehicles"""
    current_branch_name = serializers.CharField(source='current_branch.name', read_only=True)
    assigned_driver_name = serializers.CharField(source='assigned_driver.user.get_full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Vehicle
        fields = [
            'id', 'vehicle_number', 'vehicle_name', 'vehicle_type',
            'license_plate', 'status', 'status_display', 'current_branch_name',
            'assigned_driver_name', 'is_active'
        ]
        read_only_fields = ['id', 'created_at']


class VehicleDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for Vehicle with parcel information"""
    current_branch_name = serializers.CharField(source='current_branch.name', read_only=True)
    assigned_driver_name = serializers.CharField(source='assigned_driver.user.get_full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    vehicle_type_display = serializers.CharField(source='get_vehicle_type_display', read_only=True)
    parcel_count = serializers.IntegerField(read_only=True)
    total_weight_kg = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    maintenance_records = VehicleMaintenanceSerializer(many=True, read_only=True)

    class Meta:
        model = Vehicle
        fields = [
            'id', 'vehicle_number', 'vehicle_name', 'vehicle_type', 'vehicle_type_display',
            'license_plate', 'capacity_kg', 'current_branch', 'current_branch_name',
            'assigned_driver', 'assigned_driver_name', 'status', 'status_display',
            'current_latitude', 'current_longitude', 'current_location', 'fuel_level',
            'is_active', 'last_maintenance_date', 'next_maintenance_date',
            'parcel_count', 'total_weight_kg', 'maintenance_records', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'current_branch_name',
            'assigned_driver_name', 'status_display', 'vehicle_type_display',
            'parcel_count', 'total_weight_kg', 'maintenance_records'
        ]

