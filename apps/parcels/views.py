from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema

from apps.parcels.models import DeliveryProof, Parcel, ParcelImage, ParcelTrackingHistory, ParcelTransitUpdate, PickupRequest
from apps.parcels.serializers import (
    DeliveryProofSerializer,
    ParcelCreateSerializer,
    ParcelImageSerializer,
    ParcelListSerializer,
    ParcelDetailSerializer,
    ParcelTrackingHistorySerializer,
    ParcelTransitUpdateSerializer,
    PickupRequestSerializer
)
from utils.audit import AuditLogger
from utils.helpers import get_client_ip, generate_tracking_number


@extend_schema(tags=["parcels"])
class ParcelViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["status", "origin_branch", "destination_branch", "assigned_driver", "submission_type"]
    search_fields = ["tracking_number", "receiver_name", "receiver_phone"]
    ordering_fields = ["created_at", "status"]
    ordering = ["-created_at"]

    def get_queryset(self):
        user = self.request.user
        role_id = getattr(user.role, "id", None)

        if role_id == "driver":
            return Parcel.objects.filter(assigned_driver__user=user)

        if role_id == "staff":
            try:
                branch = user.staff_profile.branch
                return Parcel.objects.filter(origin_branch=branch)
            except Exception:
                return Parcel.objects.none()

        return Parcel.objects.all()

    def get_serializer_class(self):
        if self.action == "create":
            return ParcelCreateSerializer
        if self.action == "retrieve":
            return ParcelDetailSerializer
        if self.action == "list":
            return ParcelListSerializer
        return ParcelDetailSerializer

    def perform_create(self, serializer):
        data = serializer.validated_data
        if not data.get("tracking_number"):
            data["tracking_number"] = generate_tracking_number()
        parcel = serializer.save()
        ip_address = get_client_ip(self.request)
        AuditLogger.log_action(
            user=self.request.user,
            action="CREATE",
            model_name="Parcel",
            object_id=str(parcel.id),
            object_display=parcel.tracking_number,
            description="Parcel created",
            ip_address=ip_address
        )
        # create initial tracking history
        ParcelTrackingHistory.objects.create(
            parcel=parcel,
            status=parcel.status,
            updated_by=self.request.user,
            notes="Parcel registered"
        )

    @action(detail=True, methods=["post"])
    def assign_driver(self, request, pk=None):
        parcel = self.get_object()
        driver_id = request.data.get("driver_id")
        if not driver_id:
            return Response({"detail": "driver_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        from apps.drivers.models import DriverProfile

        try:
            driver = DriverProfile.objects.get(id=driver_id)
            parcel.assigned_driver = driver
            parcel.transition_to_status("RECEIVED")  # proper transition
            parcel.save()

            ParcelTrackingHistory.objects.create(
                parcel=parcel,
                status=parcel.status,
                updated_by=request.user,
                notes=f"Assigned to driver {driver.user.get_full_name()}"
            )

            AuditLogger.log_action(
                user=request.user,
                action="UPDATE",
                model_name="Parcel",
                object_id=str(parcel.id),
                object_display=parcel.tracking_number,
                description="Driver assigned",
                ip_address=get_client_ip(request)
            )

            return Response({"detail": "Driver assigned successfully"})

        except DriverProfile.DoesNotExist:
            return Response({"detail": "Driver not found"}, status=status.HTTP_404_NOT_FOUND)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    def mark_in_transit(self, request, pk=None):
        parcel = self.get_object()
        try:
            parcel.transition_to_status("IN_TRANSIT")
            ParcelTrackingHistory.objects.create(
                parcel=parcel,
                status=parcel.status,
                updated_by=request.user,
                notes="Parcel in transit"
            )
            return Response({"detail": "Parcel marked as in transit"})
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    def deliver(self, request, pk=None):
        parcel = self.get_object()
        try:
            parcel.transition_to_status("DELIVERED")
            ParcelTrackingHistory.objects.create(
                parcel=parcel,
                status=parcel.status,
                updated_by=request.user,
                notes="Parcel delivered"
            )
            return Response({"detail": "Parcel delivered successfully"})
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["get"])
    def tracking(self, request, pk=None):
        parcel = self.get_object()
        history = ParcelTrackingHistory.objects.filter(parcel=parcel)
        serializer = ParcelTrackingHistorySerializer(history, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["post"])
    def bulk_assign_vehicle(self, request):
        vehicle_id = request.data.get("vehicle_id")
        parcel_ids = request.data.get("parcel_ids", [])

        if not vehicle_id or not parcel_ids:
            return Response({"detail": "vehicle_id and parcel_ids are required"}, status=status.HTTP_400_BAD_REQUEST)

        from apps.vehicles.models import Vehicle

        try:
            vehicle = Vehicle.objects.get(id=vehicle_id)
        except Vehicle.DoesNotExist:
            return Response({"detail": "Vehicle not found"}, status=status.HTTP_404_NOT_FOUND)

        parcels = Parcel.objects.filter(id__in=parcel_ids)
        for parcel in parcels:
            try:
                parcel.assigned_vehicle = vehicle
                parcel.transition_to_status("LOADED")
            except ValueError:
                continue  # skip invalid transitions

        return Response({"detail": f"{parcels.count()} parcels assigned to vehicle"})

    @action(detail=False, methods=["get"])
    def stats(self, request):
        stats = {
            "total_parcels": Parcel.objects.count(),
            "registered": Parcel.objects.filter(status="REGISTERED").count(),
            "received": Parcel.objects.filter(status="RECEIVED").count(),
            "loaded": Parcel.objects.filter(status="LOADED").count(),
            "in_transit": Parcel.objects.filter(status="IN_TRANSIT").count(),
            "delivered": Parcel.objects.filter(status="DELIVERED").count(),
        }
        return Response(stats)
    
    
@extend_schema(tags=["parcel-images"])
class ParcelImageViewSet(viewsets.ModelViewSet):
    """Manage images associated with parcels"""
    queryset = ParcelImage.objects.all()
    serializer_class = ParcelImageSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["parcel", "image_type", "uploaded_by"]
    search_fields = ["parcel__tracking_number", "description"]
    ordering_fields = ["created_at"]
    ordering = ["-created_at"]

    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)
        AuditLogger.log_action(
            user=self.request.user,
            action="CREATE",
            model_name="ParcelImage",
            object_id=str(serializer.instance.id),
            object_display=f"{serializer.instance.parcel.tracking_number} - {serializer.instance.get_image_type_display()}",
            description="Parcel image uploaded",
            ip_address=get_client_ip(self.request)
        )


@extend_schema(tags=["parcel-transit-updates"])
class ParcelTransitUpdateViewSet(viewsets.ModelViewSet):
    """Manage driver transit updates for parcels"""
    queryset = ParcelTransitUpdate.objects.all()
    serializer_class = ParcelTransitUpdateSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["parcel", "driver", "transit_status"]
    search_fields = ["parcel__tracking_number", "location_name", "notes"]
    ordering_fields = ["created_at"]
    ordering = ["-created_at"]

    def perform_create(self, serializer):
        serializer.save(driver=self.request.user.driver_profile)
        AuditLogger.log_action(
            user=self.request.user,
            action="CREATE",
            model_name="ParcelTransitUpdate",
            object_id=str(serializer.instance.id),
            object_display=f"{serializer.instance.parcel.tracking_number} - {serializer.instance.transit_status}",
            description="Transit update created",
            ip_address=get_client_ip(self.request)
        )


@extend_schema(tags=["pickup-requests"])
class PickupRequestViewSet(viewsets.ModelViewSet):
    """Manage customer pickup requests"""
    queryset = PickupRequest.objects.all()
    serializer_class = PickupRequestSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["status", "customer", "assigned_driver", "destination_branch"]
    search_fields = ["customer__user__email", "pickup_address", "parcel_description"]
    ordering_fields = ["created_at", "preferred_pickup_date"]
    ordering = ["-created_at"]

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        """Approve a pickup request"""
        pickup_request = self.get_object()
        pickup_request.status = "APPROVED"
        pickup_request.save()
        return Response({"detail": "Pickup request approved"})

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        """Reject a pickup request"""
        pickup_request = self.get_object()
        reason = request.data.get("reason", "")
        pickup_request.status = "REJECTED"
        pickup_request.rejection_reason = reason
        pickup_request.save()
        return Response({"detail": "Pickup request rejected"})


@extend_schema(tags=["delivery-proofs"])
class DeliveryProofViewSet(viewsets.ModelViewSet):
    """Manage delivery proof images"""
    queryset = DeliveryProof.objects.all()
    serializer_class = DeliveryProofSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["parcel", "uploaded_by", "signature_required"]
    search_fields = ["parcel__tracking_number", "delivery_notes"]
    ordering_fields = ["created_at"]
    ordering = ["-created_at"]

    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)
        AuditLogger.log_action(
            user=self.request.user,
            action="CREATE",
            model_name="DeliveryProof",
            object_id=str(serializer.instance.id),
            object_display=f"{serializer.instance.parcel.tracking_number}",
            description="Delivery proof uploaded",
            ip_address=get_client_ip(self.request)
        )