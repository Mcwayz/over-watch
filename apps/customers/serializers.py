"""
Serializers for customers app
"""
from rest_framework import serializers
from apps.customers.models import CustomerProfile
from apps.authentication.models import CustomUser


class CustomerUserSerializer(serializers.ModelSerializer):
    """Serializer for user related fields in customer profile"""

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'phone_number']
        read_only_fields = ['id']


class CustomerProfileSerializer(serializers.ModelSerializer):
    """Serializer for CustomerProfile model"""
    user = CustomerUserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.filter(role__id='customer'),
        write_only=True,
        required=False
    )
    branch_name = serializers.CharField(source='preferred_branch.name', read_only=True)

    class Meta:
        model = CustomerProfile
        fields = [
            'id', 'user', 'user_id', 'customer_id', 'phone_number', 'address',
            'city', 'postal_code', 'country', 'latitude', 'longitude',
            'preferred_branch', 'branch_name', 'total_parcels_sent', 'total_spent',
            'is_verified', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'customer_id', 'created_at', 'updated_at', 'branch_name',
            'total_parcels_sent', 'total_spent', 'is_verified'
        ]


class CustomerCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating customer"""
    first_name = serializers.CharField(write_only=True)
    last_name = serializers.CharField(write_only=True)
    email = serializers.EmailField(write_only=True)
    username = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = CustomerProfile
        fields = [
            'customer_id', 'phone_number', 'address', 'city', 'postal_code',
            'country', 'latitude', 'longitude', 'preferred_branch',
            'username', 'email', 'password', 'first_name', 'last_name'
        ]
        read_only_fields = ['customer_id']

    def create(self, validated_data):
        from utils.helpers import generate_customer_id
        # Create user first
        user = CustomUser.objects.create_user(
            username=validated_data.pop('username'),
            email=validated_data.pop('email'),
            password=validated_data.pop('password', None),
            first_name=validated_data.pop('first_name'),
            last_name=validated_data.pop('last_name'),
            role_id='customer'
        )
        # Create customer profile
        customer = CustomerProfile.objects.create(
            user=user,
            customer_id=generate_customer_id(),
            **validated_data
        )
        return customer
