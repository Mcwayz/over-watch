"""
URL configuration for vehicles app
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.vehicles.views import VehicleViewSet, VehicleMaintenanceViewSet

router = DefaultRouter()
router.register(r'vehicles', VehicleViewSet, basename='vehicle')
router.register(r'maintenance', VehicleMaintenanceViewSet, basename='maintenance')

urlpatterns = [
    path('', include(router.urls)),
]

