"""
Views for drivers app
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from apps.drivers.models import DriverProfile
from apps.drivers.serializers import DriverProfileSerializer, DriverCreateUpdateSerializer
from utils.audit import AuditLogger
from utils.helpers import get_client_ip, generate_employee_id


class DriverViewSet(viewsets.ModelViewSet):
    """Driver management viewset"""
    queryset = DriverProfile.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['branch', 'vehicle_type', 'is_active']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'driver_id', 'vehicle_number']
    ordering_fields = ['hire_date', 'rating', 'created_at']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return DriverCreateUpdateSerializer
        return DriverProfileSerializer

    def perform_create(self, serializer):
        # Auto-generate driver ID if not provided
        if 'driver_id' not in serializer.validated_data:
            serializer.validated_data['driver_id'] = generate_employee_id('driver')

        driver = serializer.save()
        ip_address = get_client_ip(self.request)
        AuditLogger.log_action(
            user=self.request.user,
            action='CREATE',
            model_name='DriverProfile',
            object_id=str(driver.id),
            object_display=driver.driver_id,
            description=f"Driver {driver.user.get_full_name()} created",
            ip_address=ip_address
        )

    def perform_update(self, serializer):
        driver = serializer.save()
        ip_address = get_client_ip(self.request)
        AuditLogger.log_action(
            user=self.request.user,
            action='UPDATE',
            model_name='DriverProfile',
            object_id=str(driver.id),
            object_display=driver.driver_id,
            description=f"Driver {driver.user.get_full_name()} updated",
            ip_address=ip_address
        )

    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Deactivate driver"""
        driver = self.get_object()
        driver.is_active = False
        driver.save()

        ip_address = get_client_ip(request)
        AuditLogger.log_action(
            user=request.user,
            action='UPDATE',
            model_name='DriverProfile',
            object_id=str(driver.id),
            object_display=driver.driver_id,
            description=f"Driver {driver.user.get_full_name()} deactivated",
            ip_address=ip_address
        )

        return Response({'detail': 'Driver deactivated'})

    @action(detail=False, methods=['get'])
    def my_deliveries(self, request):
        """Get current driver's deliveries"""
        try:
            driver = request.user.driver_profile
            deliveries = driver.assigned_parcels.all()
            serializer = self.get_serializer(deliveries, many=True)
            return Response(serializer.data)
        except:
            return Response({'detail': 'Not a driver'}, status=status.HTTP_403_FORBIDDEN)

    @action(detail=False, methods=['get'])
    def my_vehicle_parcels(self, request):
        """Get parcels assigned to driver's vehicle"""
        try:
            driver = request.user.driver_profile
            from apps.parcels.models import Parcel
            from apps.parcels.serializers import ParcelListSerializer
            
            # Get parcels assigned to this driver
            parcels = Parcel.objects.filter(
                assigned_driver=driver,
                status__in=['LOADED', 'DISPATCHED', 'IN_TRANSIT', 'OUT_FOR_DELIVERY']
            )
            serializer = ParcelListSerializer(parcels, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_403_FORBIDDEN)

    @action(detail=False, methods=['get'])
    def my_pending_pickups(self, request):
        """Get pending pickup requests assigned to driver"""
        try:
            driver = request.user.driver_profile
            from apps.parcels.models import PickupRequest
            from apps.parcels.serializers import PickupRequestSerializer
            
            pickups = PickupRequest.objects.filter(
                assigned_driver=driver,
                status='SCHEDULED'
            )
            serializer = PickupRequestSerializer(pickups, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_403_FORBIDDEN)
