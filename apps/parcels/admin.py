"""
Admin configuration for parcels app
"""
from django.contrib import admin
from apps.parcels.models import Parcel, ParcelImage, ParcelTrackingHistory, ParcelTransitUpdate, PickupRequest, DeliveryProof


@admin.register(Parcel)
class ParcelAdmin(admin.ModelAdmin):
    list_display = ['tracking_number', 'sender', 'receiver_name', 'status', 'delivery_price', 'created_at']
    list_filter = ['status', 'origin_branch', 'destination_branch', 'created_at']
    search_fields = ['tracking_number', 'receiver_name', 'receiver_phone']
    readonly_fields = ['tracking_number', 'qr_code', 'created_at', 'updated_at']


@admin.register(ParcelImage)
class ParcelImageAdmin(admin.ModelAdmin):
    list_display = ['parcel', 'image_type', 'uploaded_by', 'created_at']
    list_filter = ['image_type', 'created_at']
    search_fields = ['parcel__tracking_number']


@admin.register(ParcelTrackingHistory)
class ParcelTrackingHistoryAdmin(admin.ModelAdmin):
    list_display = ['parcel', 'status', 'branch', 'updated_by', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['parcel__tracking_number']


@admin.register(ParcelTransitUpdate)
class ParcelTransitUpdateAdmin(admin.ModelAdmin):
    list_display = ['parcel', 'driver', 'location_name', 'transit_status', 'created_at']
    list_filter = ['transit_status', 'created_at']
    search_fields = ['parcel__tracking_number', 'location_name']


@admin.register(PickupRequest)
class PickupRequestAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'status', 'preferred_pickup_date', 'assigned_driver', 'created_at']
    list_filter = ['status', 'destination_branch', 'created_at']
    search_fields = ['customer__customer_id', 'parcel_description']


@admin.register(DeliveryProof)
class DeliveryProofAdmin(admin.ModelAdmin):
    list_display = ['parcel', 'uploaded_by', 'created_at']
    list_filter = ['created_at']
    search_fields = ['parcel__tracking_number']
