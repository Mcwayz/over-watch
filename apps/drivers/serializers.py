"""
Serializers for drivers app
"""
from rest_framework import serializers
from apps.drivers.models import DriverProfile
from apps.authentication.models import CustomUser


class DriverUserSerializer(serializers.ModelSerializer):
    """Serializer for user related fields in driver profile"""

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'phone_number']
        read_only_fields = ['id']


class DriverProfileSerializer(serializers.ModelSerializer):
    """Serializer for DriverProfile model"""
    user = DriverUserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.filter(role__id='driver'),
        write_only=True,
        required=False
    )
    branch_name = serializers.CharField(source='branch.name', read_only=True)
    vehicle_type_display = serializers.CharField(source='get_vehicle_type_display', read_only=True)

    class Meta:
        model = DriverProfile
        fields = [
            'id', 'user', 'user_id', 'branch', 'branch_name', 'driver_id',
            'license_number', 'license_expiry_date', 'phone_number',
            'vehicle_name', 'vehicle_number', 'vehicle_type', 'vehicle_type_display',
            'vehicle_capacity_kg', 'is_active', 'hire_date', 'rating',
            'total_deliveries', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'branch_name', 'vehicle_type_display', 'rating', 'total_deliveries']


class DriverCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating driver"""
    first_name = serializers.CharField(write_only=True)
    last_name = serializers.CharField(write_only=True)
    email = serializers.EmailField(write_only=True)
    username = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = DriverProfile
        fields = [
            'branch', 'driver_id', 'license_number', 'license_expiry_date',
            'phone_number', 'vehicle_name', 'vehicle_number', 'vehicle_type',
            'vehicle_capacity_kg', 'hire_date', 'username', 'email', 'password',
            'first_name', 'last_name'
        ]

    def create(self, validated_data):
        # Create user first
        user = CustomUser.objects.create_user(
            username=validated_data.pop('username'),
            email=validated_data.pop('email'),
            password=validated_data.pop('password', None),
            first_name=validated_data.pop('first_name'),
            last_name=validated_data.pop('last_name'),
            role_id='driver'
        )
        # Create driver profile
        driver = DriverProfile.objects.create(user=user, **validated_data)
        return driver
