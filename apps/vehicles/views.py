"""
Views for vehicles app
"""

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema

from apps.vehicles.models import Vehicle, VehicleMaintenance
from apps.vehicles.serializers import (
    VehicleSerializer,
    VehicleListSerializer,
    VehicleDetailSerializer,
    VehicleMaintenanceSerializer,
)

from utils.audit import AuditLogger
from utils.helpers import get_client_ip


@extend_schema(tags=["vehicles"])
class VehicleViewSet(viewsets.ModelViewSet):
    """Vehicle management viewset"""

    permission_classes = [IsAuthenticated]

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    filterset_fields = ["vehicle_type", "status", "current_branch", "assigned_driver"]
    search_fields = ["vehicle_number", "vehicle_name", "license_plate"]
    ordering_fields = ["vehicle_number", "created_at"]
    ordering = ["-created_at"]

    def get_queryset(self):
        """Filter vehicles based on user role"""
        user = self.request.user

        if getattr(user.role, "id", None) == "driver":
            return Vehicle.objects.filter(assigned_driver__user=user)

        if getattr(user.role, "id", None) == "staff":
            try:
                branch = user.staff_profile.branch
                return Vehicle.objects.filter(current_branch=branch)
            except Exception:
                return Vehicle.objects.none()

        return Vehicle.objects.all()

    def get_serializer_class(self):
        if self.action == "retrieve":
            return VehicleDetailSerializer
        elif self.action in ["create", "update", "partial_update"]:
            return VehicleSerializer
        return VehicleListSerializer

    def perform_create(self, serializer):
        vehicle = serializer.save()

        ip_address = get_client_ip(self.request)

        AuditLogger.log_action(
            user=self.request.user,
            action="CREATE",
            model_name="Vehicle",
            object_id=str(vehicle.id),
            object_display=vehicle.vehicle_number,
            description=f"Vehicle {vehicle.vehicle_name} created",
            ip_address=ip_address,
        )

    def perform_update(self, serializer):
        vehicle = serializer.save()

        ip_address = get_client_ip(self.request)

        AuditLogger.log_action(
            user=self.request.user,
            action="UPDATE",
            model_name="Vehicle",
            object_id=str(vehicle.id),
            object_display=vehicle.vehicle_number,
            description=f"Vehicle {vehicle.vehicle_name} updated",
            ip_address=ip_address,
        )

    @action(detail=True, methods=["post"])
    def assign_driver(self, request, pk=None):
        """Assign a driver to the vehicle"""

        vehicle = self.get_object()
        driver_id = request.data.get("driver_id")

        if not driver_id:
            return Response(
                {"detail": "driver_id is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        from apps.drivers.models import DriverProfile

        try:
            driver = DriverProfile.objects.get(id=driver_id)

            vehicle.assigned_driver = driver
            vehicle.status = "in_use"
            vehicle.save()

            ip_address = get_client_ip(request)

            AuditLogger.log_action(
                user=request.user,
                action="UPDATE",
                model_name="Vehicle",
                object_id=str(vehicle.id),
                object_display=vehicle.vehicle_number,
                description=f"Driver {driver.user.get_full_name()} assigned",
                ip_address=ip_address,
            )

            return Response({"detail": "Driver assigned successfully"})

        except DriverProfile.DoesNotExist:
            return Response(
                {"detail": "Driver not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

    @action(detail=True, methods=["post"])
    def unassign_driver(self, request, pk=None):
        """Unassign driver from vehicle"""

        vehicle = self.get_object()

        vehicle.assigned_driver = None
        vehicle.status = "available"
        vehicle.save()

        ip_address = get_client_ip(request)

        AuditLogger.log_action(
            user=request.user,
            action="UPDATE",
            model_name="Vehicle",
            object_id=str(vehicle.id),
            object_display=vehicle.vehicle_number,
            description="Driver unassigned from vehicle",
            ip_address=ip_address,
        )

        return Response({"detail": "Driver unassigned successfully"})

    @action(detail=True, methods=["post"])
    def update_location(self, request, pk=None):
        """Update vehicle current location"""

        vehicle = self.get_object()

        vehicle.current_latitude = request.data.get("latitude")
        vehicle.current_longitude = request.data.get("longitude")
        vehicle.current_location = request.data.get("location_name", "")

        vehicle.save()

        return Response({"detail": "Location updated successfully"})

    @action(detail=True, methods=["get"])
    def parcels(self, request, pk=None):
        """Get parcels on this vehicle"""

        vehicle = self.get_object()

        from apps.parcels.models import Parcel
        from apps.parcels.serializers import ParcelListSerializer

        parcels = vehicle.parcels.all()

        serializer = ParcelListSerializer(parcels, many=True)

        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def available(self, request):
        """Get available vehicles"""

        vehicles = Vehicle.objects.filter(status="available", is_active=True)

        serializer = VehicleListSerializer(vehicles, many=True)

        return Response(serializer.data)


@extend_schema(tags=["vehicles"])
class VehicleMaintenanceViewSet(viewsets.ModelViewSet):
    """Vehicle maintenance viewset"""

    queryset = VehicleMaintenance.objects.all()
    serializer_class = VehicleMaintenanceSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [
        DjangoFilterBackend,
        filters.OrderingFilter,
    ]

    filterset_fields = ["vehicle", "maintenance_type"]
    ordering_fields = ["performed_date", "created_at"]
    ordering = ["-performed_date"]

    def perform_create(self, serializer):
        maintenance = serializer.save()

        ip_address = get_client_ip(self.request)

        AuditLogger.log_action(
            user=self.request.user,
            action="CREATE",
            model_name="VehicleMaintenance",
            object_id=str(maintenance.id),
            object_display=f"{maintenance.vehicle.vehicle_number} - {maintenance.get_maintenance_type_display()}",
            description=f"Maintenance record created for {maintenance.vehicle.vehicle_number}",
            ip_address=ip_address,
        )