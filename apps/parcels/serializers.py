"""
Serializers for parcels app
"""
from rest_framework import serializers
from apps.parcels.models import (
    Parcel, ParcelImage, ParcelTrackingHistory, ParcelTransitUpdate,
    PickupRequest, DeliveryProof
)
from utils.pricing import PricingEngine


class ParcelImageSerializer(serializers.ModelSerializer):
    """Serializer for ParcelImage model"""
    uploaded_by_name = serializers.CharField(source='uploaded_by.get_full_name', read_only=True)
    image_type_display = serializers.CharField(source='get_image_type_display', read_only=True)

    class Meta:
        model = ParcelImage
        fields = [
            'id', 'parcel', 'image', 'image_type', 'image_type_display',
            'uploaded_by', 'uploaded_by_name', 'description', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'uploaded_by_name', 'image_type_display']


class ParcelTrackingHistorySerializer(serializers.ModelSerializer):
    """Serializer for ParcelTrackingHistory model"""
    updated_by_name = serializers.CharField(source='updated_by.get_full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    branch_name = serializers.CharField(source='branch.name', read_only=True)

    class Meta:
        model = ParcelTrackingHistory
        fields = ['id', 'parcel', 'status', 'status_display', 'branch', 'branch_name',
                  'updated_by', 'updated_by_name', 'notes', 'created_at']
        read_only_fields = ['id', 'created_at', 'updated_by_name', 'status_display', 'branch_name']


class ParcelTransitUpdateSerializer(serializers.ModelSerializer):
    """Serializer for ParcelTransitUpdate model"""
    driver_name = serializers.CharField(source='driver.user.get_full_name', read_only=True)

    class Meta:
        model = ParcelTransitUpdate
        fields = ['id', 'parcel', 'driver', 'driver_name', 'location_name',
                  'latitude', 'longitude', 'transit_status', 'notes', 'created_at']
        read_only_fields = ['id', 'created_at', 'driver_name']


class ParcelDetailSerializer(serializers.ModelSerializer):
    """Extended parcel serializer with related data"""
    sender_name = serializers.CharField(source='sender.user.get_full_name', read_only=True)
    origin_branch_name = serializers.CharField(source='origin_branch.name', read_only=True)
    destination_branch_name = serializers.CharField(source='destination_branch.name', read_only=True)
    current_branch_name = serializers.CharField(source='current_branch.name', read_only=True)
    assigned_driver_name = serializers.CharField(source='assigned_driver.user.get_full_name', read_only=True)
    assigned_vehicle_info = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    submission_type_display = serializers.CharField(source='get_submission_type_display', read_only=True)
    images = ParcelImageSerializer(many=True, read_only=True)
    tracking_history = ParcelTrackingHistorySerializer(many=True, read_only=True)
    transit_updates = ParcelTransitUpdateSerializer(many=True, read_only=True)

    class Meta:
        model = Parcel
        fields = [
            'id', 'tracking_number', 'submission_type', 'submission_type_display',
            'sender', 'sender_name', 'receiver_name',
            'receiver_phone', 'receiver_address', 'receiver_city', 'receiver_postal_code',
            'origin_branch', 'origin_branch_name', 'destination_branch', 'destination_branch_name',
            'current_branch', 'current_branch_name', 'weight_kg', 'declared_value',
            'delivery_price', 'pickup_fee', 'total_price',
            'status', 'status_display', 'assigned_driver', 'assigned_driver_name',
            'assigned_vehicle', 'assigned_vehicle_info',
            'qr_code', 'notes', 'images', 'tracking_history',
            'transit_updates', 'created_at', 'updated_at', 'delivered_at'
        ]
        read_only_fields = [
            'id', 'tracking_number', 'qr_code', 'created_at', 'updated_at',
            'sender_name', 'origin_branch_name', 'destination_branch_name',
            'current_branch_name', 'assigned_driver_name', 'assigned_vehicle_info',
            'status_display', 'submission_type_display',
            'images', 'tracking_history', 'transit_updates'
        ]
    
    def get_assigned_vehicle_info(self, obj):
        if obj.assigned_vehicle:
            return {
                'id': str(obj.assigned_vehicle.id),
                'vehicle_number': obj.assigned_vehicle.vehicle_number,
                'vehicle_name': obj.assigned_vehicle.vehicle_name,
            }
        return None


class ParcelListSerializer(serializers.ModelSerializer):
    """List serializer for parcels (lighter version)"""
    sender_name = serializers.CharField(source='sender.user.get_full_name', read_only=True)
    origin_branch_name = serializers.CharField(source='origin_branch.name', read_only=True)
    destination_branch_name = serializers.CharField(source='destination_branch.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    submission_type_display = serializers.CharField(source='get_submission_type_display', read_only=True)
    assigned_driver_name = serializers.CharField(source='assigned_driver.user.get_full_name', read_only=True)

    class Meta:
        model = Parcel
        fields = [
            'id', 'tracking_number', 'submission_type', 'submission_type_display',
            'sender', 'sender_name', 'receiver_name',
            'origin_branch', 'origin_branch_name', 'destination_branch', 'destination_branch_name',
            'weight_kg', 'delivery_price', 'pickup_fee', 'total_price',
            'status', 'status_display', 'assigned_driver', 'assigned_driver_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'tracking_number', 'created_at', 'updated_at']


class ParcelCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating parcels"""

    class Meta:
        model = Parcel
        fields = [
            'submission_type', 'receiver_name', 'receiver_phone', 'receiver_address',
            'receiver_city', 'receiver_postal_code', 'destination_branch',
            'weight_kg', 'declared_value'
        ]

    def create(self, validated_data):
        from utils.helpers import generate_tracking_number
        request = self.context['request']
        sender = request.user.customer_profile

        # Get submission type
        submission_type = validated_data.get('submission_type', 'BRANCH_DROPOFF')
        
        # Calculate delivery price
        distance_km = 100  # Default distance, can be calculated from branch coordinates
        pricing = PricingEngine.calculate_delivery_price(
            weight_kg=float(validated_data['weight_kg']),
            distance_km=distance_km,
            declared_value=float(validated_data.get('declared_value', 0))
        )

        # For pickup requests, pickup_fee will be calculated separately
        pickup_fee = 0
        if submission_type == 'BRANCH_DROPOFF':
            pickup_fee = 0
        
        total_price = pricing['total_price'] + pickup_fee

        parcel = Parcel.objects.create(
            tracking_number=generate_tracking_number(),
            submission_type=submission_type,
            sender=sender,
            origin_branch=sender.preferred_branch,
            delivery_price=pricing['total_price'],
            pickup_fee=pickup_fee,
            total_price=total_price,
            **validated_data
        )
        return parcel


class PickupRequestSerializer(serializers.ModelSerializer):
    """Serializer for PickupRequest model"""
    customer_name = serializers.CharField(source='customer.user.get_full_name', read_only=True)
    driver_name = serializers.CharField(source='assigned_driver.user.get_full_name', read_only=True)
    destination_branch_name = serializers.CharField(source='destination_branch.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    pickup_fee_breakdown = serializers.SerializerMethodField()

    class Meta:
        model = PickupRequest
        fields = [
            'id', 'customer', 'customer_name', 'pickup_address', 'parcel_description',
            'weight_kg', 'destination_branch', 'destination_branch_name', 'status',
            'status_display', 'preferred_pickup_date', 'preferred_pickup_time',
            'assigned_driver', 'driver_name', 'pickup_date', 'estimated_parcel',
            'rejection_reason', 'notes', 'pickup_fee_breakdown', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'customer_name', 'driver_name', 'destination_branch_name',
            'status_display', 'created_at', 'updated_at', 'pickup_fee_breakdown'
        ]
    
    def get_pickup_fee_breakdown(self, obj):
        """Calculate pickup fee if distance is available"""
        # This would require distance calculation from pickup address to branch
        # For now, return None - can be calculated when needed
        return None


class DeliveryProofSerializer(serializers.ModelSerializer):
    """Serializer for DeliveryProof model"""
    uploaded_by_name = serializers.CharField(source='uploaded_by.get_full_name', read_only=True)

    class Meta:
        model = DeliveryProof
        fields = [
            'id', 'parcel', 'proof_image', 'uploaded_by', 'uploaded_by_name',
            'delivery_notes', 'signature_required', 'signature_image', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'uploaded_by_name']
