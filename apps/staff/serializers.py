"""
Serializers for staff app
"""
from rest_framework import serializers
from apps.staff.models import StaffProfile
from apps.authentication.models import CustomUser


class StaffUserSerializer(serializers.ModelSerializer):
    """Serializer for user related fields in staff profile"""

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'phone_number']
        read_only_fields = ['id']


class StaffProfileSerializer(serializers.ModelSerializer):
    """Serializer for StaffProfile model"""
    user = StaffUserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.filter(role__id='staff'),
        write_only=True,
        required=False
    )
    branch_name = serializers.CharField(source='branch.name', read_only=True)
    position_display = serializers.CharField(source='get_position_display', read_only=True)

    class Meta:
        model = StaffProfile
        fields = [
            'id', 'user', 'user_id', 'branch', 'branch_name', 'employee_id',
            'position', 'position_display', 'phone_number', 'address',
            'is_active', 'hire_date', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'branch_name', 'position_display']


class StaffCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating staff"""
    first_name = serializers.CharField(write_only=True)
    last_name = serializers.CharField(write_only=True)
    email = serializers.EmailField(write_only=True)
    username = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = StaffProfile
        fields = [
            'branch', 'employee_id', 'position', 'phone_number', 'address',
            'hire_date', 'username', 'email', 'password', 'first_name', 'last_name'
        ]

    def create(self, validated_data):
        # Create user first
        user = CustomUser.objects.create_user(
            username=validated_data.pop('username'),
            email=validated_data.pop('email'),
            password=validated_data.pop('password', None),
            first_name=validated_data.pop('first_name'),
            last_name=validated_data.pop('last_name'),
            role_id='staff'
        )
        # Create staff profile
        staff = StaffProfile.objects.create(user=user, **validated_data)
        return staff
