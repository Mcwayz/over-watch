"""
Serializers for branches app
"""
from rest_framework import serializers
from apps.branches.models import Branch


class BranchSerializer(serializers.ModelSerializer):
    """Serializer for Branch model"""
    staff_count = serializers.SerializerMethodField()
    driver_count = serializers.SerializerMethodField()

    class Meta:
        model = Branch
        fields = [
            'id', 'name', 'city', 'address', 'latitude', 'longitude',
            'contact_phone', 'contact_email', 'manager_email', 'is_active',
            'staff_count', 'driver_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'staff_count', 'driver_count']

    def get_staff_count(self, obj):
        return obj.staff_count

    def get_driver_count(self, obj):
        return obj.driver_count
