"""
URL configuration for parcels app
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.parcels.views import (
    ParcelViewSet, ParcelImageViewSet, ParcelTransitUpdateViewSet,
    PickupRequestViewSet, DeliveryProofViewSet
)

router = DefaultRouter()
router.register(r'parcels', ParcelViewSet, basename='parcel')
router.register(r'parcel-images', ParcelImageViewSet, basename='parcel-image')
router.register(r'transit-updates', ParcelTransitUpdateViewSet, basename='transit-update')
router.register(r'pickup-requests', PickupRequestViewSet, basename='pickup-request')
router.register(r'delivery-proofs', DeliveryProofViewSet, basename='delivery-proof')

urlpatterns = [
    path('', include(router.urls)),
]
