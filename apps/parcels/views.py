"""
Views for parcels app
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from apps.parcels.models import (
    Parcel, ParcelImage, ParcelTrackingHistory, ParcelTransitUpdate,
    PickupRequest, DeliveryProof
)
from apps.parcels.serializers import (
    ParcelDetailSerializer, ParcelListSerializer, ParcelCreateSerializer,
    ParcelImageSerializer, ParcelTransitUpdateSerializer, PickupRequestSerializer,
    DeliveryProofSerializer
)
from utils.audit import AuditLogger
from utils.helpers import get_client_ip, generate_tracking_number
from utils.pricing import PricingEngine


class ParcelViewSet(viewsets.ModelViewSet):
    """Parcel management viewset"""
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'origin_branch', 'destination_branch', 'assigned_driver', 'submission_type']
    search_fields = ['tracking_number', 'receiver_name', 'receiver_phone']
    ordering_fields = ['created_at', 'status']
    ordering = ['-created_at']

    def get_queryset(self):
        """Filter parcels based on user role"""
        user = self.request.user
        if user.role.id == 'customer':
            return Parcel.objects.filter(sender__user=user)
        elif user.role.id == 'driver':
            return Parcel.objects.filter(assigned_driver__user=user)
        elif user.role.id == 'staff':
            try:
                branch = user.staff_profile.branch
                return Parcel.objects.filter(
                    Q(origin_branch=branch) | Q(destination_branch=branch) | Q(current_branch=branch)
                )
            except:
                return Parcel.objects.none()
        return Parcel.objects.all()  # Managers see all

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ParcelDetailSerializer
        elif self.action == 'create':
            return ParcelCreateSerializer
        elif self.action == 'list':
            return ParcelListSerializer
        return ParcelDetailSerializer

    def perform_create(self, serializer):
        parcel = serializer.save()
        ip_address = get_client_ip(self.request)
        AuditLogger.log_action(
            user=self.request.user,
            action='CREATE',
            model_name='Parcel',
            object_id=str(parcel.id),
            object_display=parcel.tracking_number,
            description=f"Parcel {parcel.tracking_number} created via {parcel.get_submission_type_display()}",
            ip_address=ip_address
        )

    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """Update parcel status"""
        parcel = self.get_object()
        new_status = request.data.get('status')

        if not new_status:
            return Response({'detail': 'Status is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            old_status = parcel.status
            parcel.transition_to_status(new_status)

            # Create tracking history entry
            ParcelTrackingHistory.objects.create(
                parcel=parcel,
                status=new_status,
                branch=parcel.current_branch,
                updated_by=request.user,
                notes=request.data.get('notes', '')
            )

            # Log status change
            ip_address = get_client_ip(request)
            AuditLogger.log_parcel_status_change(
                parcel, request.user, old_status, new_status, ip_address=ip_address
            )

            return Response(
                {'detail': f'Parcel status updated to {new_status}'},
                status=status.HTTP_200_OK
            )
        except ValueError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def download_qr(self, request, pk=None):
        """Download parcel QR code"""
        parcel = self.get_object()
        if not parcel.qr_code:
            return Response({'detail': 'QR code not available'}, status=status.HTTP_404_NOT_FOUND)

        from django.http import FileResponse
        return FileResponse(parcel.qr_code.open('rb'), content_type='image/png')

    @action(detail=True, methods=['get'])
    def tracking(self, request, pk=None):
        """Get parcel tracking information"""
        parcel = self.get_object()
        serializer = ParcelDetailSerializer(parcel)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def assign_driver(self, request, pk=None):
        """Assign driver to parcel"""
        parcel = self.get_object()
        driver_id = request.data.get('driver_id')

        try:
            from apps.drivers.models import DriverProfile
            driver = DriverProfile.objects.get(id=driver_id)
            parcel.assigned_driver = driver
            parcel.save()

            ip_address = get_client_ip(request)
            AuditLogger.log_action(
                user=request.user,
                action='UPDATE',
                model_name='Parcel',
                object_id=str(parcel.id),
                object_display=parcel.tracking_number,
                description=f"Driver {driver.user.get_full_name()} assigned to parcel",
                ip_address=ip_address
            )

            return Response({'detail': 'Driver assigned'}, status=status.HTTP_200_OK)
        except:
            return Response({'detail': 'Driver not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'])
    def assign_vehicle(self, request, pk=None):
        """Assign vehicle to parcel (loading)"""
        parcel = self.get_object()
        vehicle_id = request.data.get('vehicle_id')

        try:
            from apps.vehicles.models import Vehicle
            vehicle = Vehicle.objects.get(id=vehicle_id)
            parcel.assigned_vehicle = vehicle
            parcel.save()

            ip_address = get_client_ip(request)
            AuditLogger.log_action(
                user=request.user,
                action='UPDATE',
                model_name='Parcel',
                object_id=str(parcel.id),
                object_display=parcel.tracking_number,
                description=f"Parcel loaded onto vehicle {vehicle.vehicle_number}",
                ip_address=ip_address
            )

            return Response({'detail': 'Vehicle assigned'}, status=status.HTTP_200_OK)
        except:
            return Response({'detail': 'Vehicle not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'])
    def load(self, request, pk=None):
        """Mark parcel as loaded (staff loads parcel to vehicle)"""
        parcel = self.get_object()
        
        if parcel.status != 'RECEIVED':
            return Response(
                {'detail': 'Parcel must be in RECEIVED status to be loaded'},
                status=status.HTTP_400_BAD_REQUEST
            )

        vehicle_id = request.data.get('vehicle_id')
        if vehicle_id:
            try:
                from apps.vehicles.models import Vehicle
                vehicle = Vehicle.objects.get(id=vehicle_id)
                parcel.assigned_vehicle = vehicle
            except:
                pass

        old_status = parcel.status
        parcel.status = 'LOADED'
        parcel.save()

        # Create tracking history
        ParcelTrackingHistory.objects.create(
            parcel=parcel,
            status='LOADED',
            branch=parcel.origin_branch,
            updated_by=request.user,
            notes=request.data.get('notes', 'Parcel loaded onto vehicle')
        )

        ip_address = get_client_ip(request)
        AuditLogger.log_parcel_status_change(
            parcel, request.user, old_status, 'LOADED', ip_address=ip_address
        )

        return Response({'detail': 'Parcel marked as LOADED'})

    @action(detail=True, methods=['post'])
    def dispatch(self, request, pk=None):
        """Mark parcel as dispatched (staff dispatches loaded parcels)"""
        parcel = self.get_object()
        
        if parcel.status != 'LOADED':
            return Response(
                {'detail': 'Parcel must be in LOADED status to be dispatched'},
                status=status.HTTP_400_BAD_REQUEST
            )

        old_status = parcel.status
        parcel.status = 'DISPATCHED'
        parcel.save()

        # Create tracking history
        ParcelTrackingHistory.objects.create(
            parcel=parcel,
            status='DISPATCHED',
            branch=parcel.origin_branch,
            updated_by=request.user,
            notes=request.data.get('notes', 'Parcel dispatched')
        )

        ip_address = get_client_ip(request)
        AuditLogger.log_parcel_status_change(
            parcel, request.user, old_status, 'DISPATCHED', ip_address=ip_address
        )

        return Response({'detail': 'Parcel marked as DISPATCHED'})

    @action(detail=True, methods=['post'])
    def mark_in_transit(self, request, pk=None):
        """Mark parcel as in transit (driver updates)"""
        parcel = self.get_object()
        
        if parcel.status not in ['DISPATCHED', 'LOADED']:
            return Response(
                {'detail': 'Parcel must be LOADED or DISPATCHED to be marked as in transit'},
                status=status.HTTP_400_BAD_REQUEST
            )

        old_status = parcel.status
        parcel.status = 'IN_TRANSIT'
        parcel.save()

        # Create tracking history
        ParcelTrackingHistory.objects.create(
            parcel=parcel,
            status='IN_TRANSIT',
            branch=parcel.current_branch,
            updated_by=request.user,
            notes=request.data.get('notes', 'Parcel in transit')
        )

        # Create transit update
        ParcelTransitUpdate.objects.create(
            parcel=parcel,
            driver=parcel.assigned_driver,
            location_name=request.data.get('location_name', ''),
            latitude=request.data.get('latitude', 0),
            longitude=request.data.get('longitude', 0),
            transit_status='in_transit',
            notes=request.data.get('notes', '')
        )

        ip_address = get_client_ip(request)
        AuditLogger.log_parcel_status_change(
            parcel, request.user, old_status, 'IN_TRANSIT', ip_address=ip_address
        )

        return Response({'detail': 'Parcel marked as IN_TRANSIT'})

    @action(detail=True, methods=['post'])
    def mark_arrived(self, request, pk=None):
        """Mark parcel as arrived at destination branch"""
        parcel = self.get_object()
        
        if parcel.status != 'IN_TRANSIT':
            return Response(
                {'detail': 'Parcel must be IN_TRANSIT to be marked as arrived'},
                status=status.HTTP_400_BAD_REQUEST
            )

        old_status = parcel.status
        parcel.status = 'ARRIVED'
        parcel.current_branch = parcel.destination_branch
        parcel.save()

        # Create tracking history
        ParcelTrackingHistory.objects.create(
            parcel=parcel,
            status='ARRIVED',
            branch=parcel.destination_branch,
            updated_by=request.user,
            notes=request.data.get('notes', 'Parcel arrived at destination branch')
        )

        ip_address = get_client_ip(request)
        AuditLogger.log_parcel_status_change(
            parcel, request.user, old_status, 'ARRIVED', ip_address=ip_address
        )

        return Response({'detail': 'Parcel marked as ARRIVED'})

    @action(detail=True, methods=['post'])
    def out_for_delivery(self, request, pk=None):
        """Mark parcel as out for delivery"""
        parcel = self.get_object()
        
        if parcel.status != 'ARRIVED':
            return Response(
                {'detail': 'Parcel must be ARRIVED to be marked as out for delivery'},
                status=status.HTTP_400_BAD_REQUEST
            )

        old_status = parcel.status
        parcel.status = 'OUT_FOR_DELIVERY'
        parcel.save()

        # Create tracking history
        ParcelTrackingHistory.objects.create(
            parcel=parcel,
            status='OUT_FOR_DELIVERY',
            branch=parcel.current_branch,
            updated_by=request.user,
            notes=request.data.get('notes', 'Parcel out for delivery')
        )

        ip_address = get_client_ip(request)
        AuditLogger.log_parcel_status_change(
            parcel, request.user, old_status, 'OUT_FOR_DELIVERY', ip_address=ip_address
        )

        return Response({'detail': 'Parcel marked as OUT_FOR_DELIVERY'})

    @action(detail=True, methods=['post'])
    def confirm_delivery(self, request, pk=None):
        """Confirm parcel delivery"""
        parcel = self.get_object()
        
        if parcel.status != 'OUT_FOR_DELIVERY':
            return Response(
                {'detail': 'Parcel must be OUT_FOR_DELIVERY to confirm delivery'},
                status=status.HTTP_400_BAD_REQUEST
            )

        old_status = parcel.status
        parcel.status = 'DELIVERED'
        parcel.save()

        # Create tracking history
        ParcelTrackingHistory.objects.create(
            parcel=parcel,
            status='DELIVERED',
            branch=parcel.current_branch,
            updated_by=request.user,
            notes=request.data.get('notes', 'Parcel delivered')
        )

        # Upload delivery proof if provided
        if request.FILES.get('proof_image'):
            DeliveryProof.objects.create(
                parcel=parcel,
                proof_image=request.FILES['proof_image'],
                uploaded_by=request.user,
                delivery_notes=request.data.get('delivery_notes', '')
            )

        ip_address = get_client_ip(request)
        AuditLogger.log_parcel_status_change(
            parcel, request.user, old_status, 'DELIVERED', ip_address=ip_address
        )
        AuditLogger.log_action(
            user=request.user,
            action='DELIVERY_CONFIRMATION',
            model_name='Parcel',
            object_id=str(parcel.id),
            object_display=parcel.tracking_number,
            description=f"Parcel {parcel.tracking_number} delivered",
            ip_address=ip_address
        )

        return Response({'detail': 'Parcel delivery confirmed'})

    @action(detail=False, methods=['post'])
    def bulk_in_transit(self, request):
        """Bulk update parcels to IN_TRANSIT status (driver scans/updates all at once)"""
        parcel_ids = request.data.get('parcel_ids', [])
        
        if not parcel_ids:
            return Response(
                {'detail': 'parcel_ids list is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        parcels = Parcel.objects.filter(
            id__in=parcel_ids,
            status__in=['DISPATCHED', 'LOADED']
        )

        updated_count = 0
        for parcel in parcels:
            old_status = parcel.status
            parcel.status = 'IN_TRANSIT'
            parcel.save()

            # Create tracking history
            ParcelTrackingHistory.objects.create(
                parcel=parcel,
                status='IN_TRANSIT',
                branch=parcel.current_branch,
                updated_by=request.user,
                notes='Bulk in-transit update'
            )

            # Create transit update
            ParcelTransitUpdate.objects.create(
                parcel=parcel,
                driver=parcel.assigned_driver,
                location_name=request.data.get('location_name', ''),
                latitude=request.data.get('latitude', 0),
                longitude=request.data.get('longitude', 0),
                transit_status='in_transit',
                notes='Bulk in-transit update'
            )

            updated_count += 1

        ip_address = get_client_ip(request)
        AuditLogger.log_action(
            user=request.user,
            action='BULK_IN_TRANSIT',
            model_name='Parcel',
            object_id=','.join([str(p.id) for p in parcels]),
            object_display=f'{updated_count} parcels',
            description=f'Bulk in-transit update for {updated_count} parcels',
            ip_address=ip_address
        )

        return Response({
            'detail': f'{updated_count} parcels marked as IN_TRANSIT',
            'updated_count': updated_count
        })

    @action(detail=False, methods=['post'])
    def bulk_load(self, request):
        """Bulk load parcels to vehicle"""
        parcel_ids = request.data.get('parcel_ids', [])
        vehicle_id = request.data.get('vehicle_id')
        
        if not parcel_ids:
            return Response(
                {'detail': 'parcel_ids list is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        from apps.vehicles.models import Vehicle
        vehicle = None
        if vehicle_id:
            try:
                vehicle = Vehicle.objects.get(id=vehicle_id)
            except:
                pass

        parcels = Parcel.objects.filter(
            id__in=parcel_ids,
            status='RECEIVED'
        )

        updated_count = 0
        for parcel in parcels:
            old_status = parcel.status
            parcel.status = 'LOADED'
            if vehicle:
                parcel.assigned_vehicle = vehicle
            parcel.save()

            # Create tracking history
            ParcelTrackingHistory.objects.create(
                parcel=parcel,
                status='LOADED',
                branch=parcel.origin_branch,
                updated_by=request.user,
                notes='Bulk load to vehicle'
            )

            updated_count += 1

        ip_address = get_client_ip(request)
        AuditLogger.log_action(
            user=request.user,
            action='BULK_LOAD',
            model_name='Parcel',
            object_id=','.join([str(p.id) for p in parcels]),
            object_display=f'{updated_count} parcels',
            description=f'Bulk load for {updated_count} parcels' + (f' to vehicle {vehicle.vehicle_number}' if vehicle else ''),
            ip_address=ip_address
        )

        return Response({
            'detail': f'{updated_count} parcels marked as LOADED',
            'updated_count': updated_count
        })

    @action(detail=False, methods=['post'])
    def bulk_dispatch(self, request):
        """Bulk dispatch parcels"""
        parcel_ids = request.data.get('parcel_ids', [])
        
        if not parcel_ids:
            return Response(
                {'detail': 'parcel_ids list is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        parcels = Parcel.objects.filter(
            id__in=parcel_ids,
            status='LOADED'
        )

        updated_count = 0
        for parcel in parcels:
            old_status = parcel.status
            parcel.status = 'DISPATCHED'
            parcel.save()

            # Create tracking history
            ParcelTrackingHistory.objects.create(
                parcel=parcel,
                status='DISPATCHED',
                branch=parcel.origin_branch,
                updated_by=request.user,
                notes='Bulk dispatch'
            )

            updated_count += 1

        ip_address = get_client_ip(request)
        AuditLogger.log_action(
            user=request.user,
            action='BULK_DISPATCH',
            model_name='Parcel',
            object_id=','.join([str(p.id) for p in parcels]),
            object_display=f'{updated_count} parcels',
            description=f'Bulk dispatch for {updated_count} parcels',
            ip_address=ip_address
        )

        return Response({
            'detail': f'{updated_count} parcels marked as DISPATCHED',
            'updated_count': updated_count
        })

    @action(detail=False, methods=['get'])
    def calculate_pickup_fee(self, request):
        """Calculate pickup fee"""
        distance_km = request.query_params.get('distance_km', 0)
        is_priority = request.query_params.get('is_priority', 'false').lower() == 'true'
        
        try:
            distance_km = float(distance_km)
        except ValueError:
            return Response({'detail': 'Invalid distance_km'}, status=status.HTTP_400_BAD_REQUEST)

        breakdown = PricingEngine.get_pickup_fee_breakdown(distance_km, is_priority)
        return Response(breakdown)

    @action(detail=False, methods=['get'])
    def calculate_pickup_fee_with_distance(self, request):
        """
        Calculate pickup fee using distance calculation from customer to branch.
        Accepts customer coordinates and branch ID to calculate distance.
        """
        from utils.distance import calculate_pickup_distance, DistanceCalculator
        
        customer_lat = request.query_params.get('customer_lat')
        customer_lon = request.query_params.get('customer_lon')
        branch_id = request.query_params.get('branch_id')
        is_priority = request.query_params.get('is_priority', 'false').lower() == 'true'
        
        # If coordinates are provided, calculate distance
        distance_km = None
        if customer_lat and customer_lon:
            try:
                customer_lat = float(customer_lat)
                customer_lon = float(customer_lon)
                
                # Get branch coordinates if branch_id provided
                if branch_id:
                    from apps.branches.models import Branch
                    try:
                        branch = Branch.objects.get(id=branch_id)
                        if branch.latitude and branch.longitude:
                            distance_km = calculate_pickup_distance(
                                customer_lat, customer_lon,
                                branch.latitude, branch.longitude
                            )
                    except Branch.DoesNotExist:
                        pass
            except ValueError:
                pass
        
        # If no calculated distance, use provided distance_km parameter
        if distance_km is None:
            distance_km = float(request.query_params.get('distance_km', 0))
        
        # Calculate pickup fee
        breakdown = PricingEngine.get_pickup_fee_breakdown(distance_km, is_priority)
        
        # Include distance info in response
        breakdown['distance_km'] = distance_km
        breakdown['distance_source'] = 'calculated' if distance_km else 'default'
        
        return Response(breakdown)

    @action(detail=False, methods=['get'])
    def track(self, request):
        """Public tracking by tracking number"""
        tracking_number = request.query_params.get('tracking_number')
        
        if not tracking_number:
            return Response(
                {'detail': 'tracking_number is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            parcel = Parcel.objects.get(tracking_number=tracking_number)
            serializer = ParcelDetailSerializer(parcel)
            return Response(serializer.data)
        except Parcel.DoesNotExist:
            return Response(
                {'detail': 'Parcel not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['get'])
    def scan_qr(self, request):
        """Scan QR code - get parcel by tracking number (for staff/driver scanning)"""
        tracking_number = request.query_params.get('tracking_number')
        
        if not tracking_number:
            return Response(
                {'detail': 'tracking_number is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            parcel = Parcel.objects.get(tracking_number=tracking_number)
            
            # Log QR scan
            ip_address = get_client_ip(request)
            AuditLogger.log_qr_scan(parcel, request.user, ip_address=ip_address)
            
            serializer = ParcelDetailSerializer(parcel)
            return Response(serializer.data)
        except Parcel.DoesNotExist:
            return Response(
                {'detail': 'Parcel not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['get'])
    def dashboard_stats(self, request):
        """Get dashboard statistics for manager"""
        from django.db.models import Count, Sum
        from django.utils import timezone
        from datetime import timedelta

        # Total parcels
        total_parcels = Parcel.objects.count()

        # Parcels by status
        parcels_by_status = dict(
            Parcel.objects.values('status').annotate(count=Count('id')).values_list('status', 'count')
        )

        # Today's parcels
        today = timezone.now().date()
        today_parcels = Parcel.objects.filter(created_at__date=today).count()

        # This week's parcels
        week_ago = timezone.now() - timedelta(days=7)
        week_parcels = Parcel.objects.filter(created_at__gte=week_ago).count()

        # Total revenue
        total_revenue = float(Parcel.objects.aggregate(total=Sum('total_price'))['total'] or 0)

        # Pending pickup requests
        pending_pickups = PickupRequest.objects.filter(status='PENDING').count()

        # Delivery rate
        delivered_count = Parcel.objects.filter(status='DELIVERED').count()
        delivery_rate = (delivered_count / total_parcels * 100) if total_parcels > 0 else 0

        return Response({
            'total_parcels': total_parcels,
            'parcels_by_status': parcels_by_status,
            'today_parcels': today_parcels,
            'week_parcels': week_parcels,
            'total_revenue': total_revenue,
            'pending_pickups': pending_pickups,
            'delivery_rate': round(delivery_rate, 2),
        })

    @action(detail=False, methods=['get'])
    def staff_dashboard_stats(self, request):
        """Get dashboard statistics for staff"""
        from django.db.models import Count
        from django.utils import timezone
        from datetime import timedelta

        user = request.user
        try:
            branch = user.staff_profile.branch
        except:
            return Response({'detail': 'Staff profile not found'}, status=status.HTTP_403_FORBIDDEN)

        # Incoming parcels at branch (from other branches, arrived or in transit)
        incoming_parcels = Parcel.objects.filter(
            destination_branch=branch,
            status__in=['IN_TRANSIT', 'ARRIVED']
        ).count()

        # Outgoing parcels from branch (origin branch)
        outgoing_parcels = Parcel.objects.filter(
            origin_branch=branch,
            status__in=['RECEIVED', 'LOADED', 'DISPATCHED']
        ).count()

        # Pending pickup requests for this branch
        pending_pickups = PickupRequest.objects.filter(
            destination_branch=branch,
            status__in=['PENDING', 'APPROVED', 'SCHEDULED']
        ).count()

        # Today's received parcels
        today = timezone.now().date()
        today_received = Parcel.objects.filter(
            origin_branch=branch,
            created_at__date=today
        ).count()

        return Response({
            'incoming_parcels': incoming_parcels,
            'outgoing_parcels': outgoing_parcels,
            'pending_pickups': pending_pickups,
            'today_received': today_received,
        })

    @action(detail=False, methods=['get'])
    def driver_dashboard_stats(self, request):
        """Get dashboard statistics for driver"""
        from django.db.models import Count
        from django.utils import timezone
        from datetime import timedelta

        user = request.user
        try:
            driver = user.driver_profile
        except:
            return Response({'detail': 'Driver profile not found'}, status=status.HTTP_403_FORBIDDEN)

        # Assigned parcels (loaded or dispatched)
        assigned_parcels = Parcel.objects.filter(
            assigned_driver=driver,
            status__in=['LOADED', 'DISPATCHED', 'IN_TRANSIT', 'OUT_FOR_DELIVERY']
        ).count()

        # Out for delivery
        out_for_delivery = Parcel.objects.filter(
            assigned_driver=driver,
            status='OUT_FOR_DELIVERY'
        ).count()

        # Delivered today
        today = timezone.now().date()
        delivered_today = Parcel.objects.filter(
            assigned_driver=driver,
            status='DELIVERED',
            delivered_at__date=today
        ).count()

        # Total deliveries
        total_deliveries = driver.total_deliveries

        return Response({
            'assigned_parcels': assigned_parcels,
            'out_for_delivery': out_for_delivery,
            'delivered_today': delivered_today,
            'total_deliveries': total_deliveries,
        })


class ParcelImageViewSet(viewsets.ModelViewSet):
    """Parcel image management viewset"""
    queryset = ParcelImage.objects.all()
    serializer_class = ParcelImageSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        image = serializer.save(uploaded_by=self.request.user)

        # Log image upload
        ip_address = get_client_ip(self.request)
        AuditLogger.log_image_upload(image, self.request.user, ip_address=ip_address)

    def get_queryset(self):
        """Filter images based on parcel access"""
        parcel_id = self.request.query_params.get('parcel_id')
        if parcel_id:
            return ParcelImage.objects.filter(parcel_id=parcel_id)
        return ParcelImage.objects.all()


class ParcelTransitUpdateViewSet(viewsets.ModelViewSet):
    """Parcel transit update viewset"""
    queryset = ParcelTransitUpdate.objects.all()
    serializer_class = ParcelTransitUpdateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        transit_update = serializer.save()

        # Log transit update
        ip_address = get_client_ip(self.request)
        AuditLogger.log_transit_update(transit_update, self.request.user, ip_address=ip_address)

    def get_queryset(self):
        """Filter transit updates based on parcel access"""
        parcel_id = self.request.query_params.get('parcel_id')
        if parcel_id:
            return ParcelTransitUpdate.objects.filter(parcel_id=parcel_id)
        return ParcelTransitUpdate.objects.all()


class PickupRequestViewSet(viewsets.ModelViewSet):
    """Pickup request management viewset"""
    permission_classes = [IsAuthenticated]
    serializer_class = PickupRequestSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'destination_branch']
    search_fields = ['customer__customer_id', 'parcel_description']
    ordering_fields = ['preferred_pickup_date', 'created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        """Filter pickup requests based on user role"""
        user = self.request.user
        if user.role.id == 'customer':
            return PickupRequest.objects.filter(customer__user=user)
        return PickupRequest.objects.all()

    def perform_create(self, serializer):
        pickup = serializer.save()
        ip_address = get_client_ip(self.request)
        AuditLogger.log_action(
            user=self.request.user,
            action='PICKUP_REQUEST',
            model_name='PickupRequest',
            object_id=str(pickup.id),
            object_display=pickup.customer.customer_id,
            description='Pickup request created',
            ip_address=ip_address
        )

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve pickup request"""
        pickup = self.get_object()
        pickup.status = 'APPROVED'
        pickup.save()

        ip_address = get_client_ip(request)
        AuditLogger.log_action(
            user=request.user,
            action='UPDATE',
            model_name='PickupRequest',
            object_id=str(pickup.id),
            object_display=pickup.customer.customer_id,
            description='Pickup request approved',
            ip_address=ip_address
        )

        return Response({'detail': 'Pickup request approved'})

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject pickup request"""
        pickup = self.get_object()
        pickup.status = 'REJECTED'
        pickup.rejection_reason = request.data.get('reason', '')
        pickup.save()

        ip_address = get_client_ip(request)
        AuditLogger.log_action(
            user=request.user,
            action='UPDATE',
            model_name='PickupRequest',
            object_id=str(pickup.id),
            object_display=pickup.customer.customer_id,
            description='Pickup request rejected',
            ip_address=ip_address
        )

        return Response({'detail': 'Pickup request rejected'})

    @action(detail=True, methods=['post'])
    def schedule_pickup(self, request, pk=None):
        """Schedule pickup - assign driver and set pickup date"""
        pickup = self.get_object()
        
        if pickup.status not in ['PENDING', 'APPROVED']:
            return Response(
                {'detail': 'Pickup request must be PENDING or APPROVED to be scheduled'},
                status=status.HTTP_400_BAD_REQUEST
            )

        driver_id = request.data.get('driver_id')
        pickup_date = request.data.get('pickup_date')
        
        if not driver_id:
            return Response({'detail': 'driver_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not pickup_date:
            return Response({'detail': 'pickup_date is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            from apps.drivers.models import DriverProfile
            driver = DriverProfile.objects.get(id=driver_id)
            pickup.assigned_driver = driver
            pickup.pickup_date = pickup_date
            pickup.status = 'SCHEDULED'
            pickup.save()

            ip_address = get_client_ip(request)
            AuditLogger.log_action(
                user=request.user,
                action='UPDATE',
                model_name='PickupRequest',
                object_id=str(pickup.id),
                object_display=pickup.customer.customer_id,
                description=f'Pickup scheduled for {pickup_date} with driver {driver.user.get_full_name()}',
                ip_address=ip_address
            )

            return Response({'detail': 'Pickup scheduled successfully'})
        except DriverProfile.DoesNotExist:
            return Response({'detail': 'Driver not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'])
    def confirm_pickup(self, request, pk=None):
        """Confirm pickup - driver confirms parcel collection"""
        pickup = self.get_object()
        
        if pickup.status != 'SCHEDULED':
            return Response(
                {'detail': 'Pickup must be SCHEDULED to be confirmed'},
                status=status.HTTP_400_BAD_REQUEST
            )

        pickup.status = 'PICKED_UP'
        pickup.save()

        ip_address = get_client_ip(request)
        AuditLogger.log_action(
            user=request.user,
            action='UPDATE',
            model_name='PickupRequest',
            object_id=str(pickup.id),
            object_display=pickup.customer.customer_id,
            description='Pickup confirmed - parcel collected',
            ip_address=ip_address
        )

        return Response({'detail': 'Pickup confirmed successfully'})

    @action(detail=True, methods=['post'])
    def create_parcel(self, request, pk=None):
        """Create parcel from confirmed pickup request"""
        pickup = self.get_object()
        
        if pickup.status != 'PICKED_UP':
            return Response(
                {'detail': 'Pickup must be PICKED_UP to create parcel'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get additional parcel details from request
        receiver_name = request.data.get('receiver_name')
        receiver_phone = request.data.get('receiver_phone')
        receiver_address = request.data.get('receiver_address')
        receiver_city = request.data.get('receiver_city')
        receiver_postal_code = request.data.get('receiver_postal_code')
        declared_value = request.data.get('declared_value', 0)

        if not all([receiver_name, receiver_phone, receiver_address, receiver_city, receiver_postal_code]):
            return Response(
                {'detail': 'receiver_name, receiver_phone, receiver_address, receiver_city, receiver_postal_code are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Calculate pickup fee if distance is provided
        distance_km = request.data.get('distance_km', 0)
        is_priority = request.data.get('is_priority', False)
        
        try:
            distance_km = float(distance_km)
        except ValueError:
            distance_km = 0

        pickup_fee_breakdown = PricingEngine.get_pickup_fee_breakdown(distance_km, is_priority)
        pickup_fee = pickup_fee_breakdown['total_pickup_fee']

        # Calculate delivery price
        delivery_breakdown = PricingEngine.calculate_delivery_price(
            weight_kg=float(pickup.weight_kg),
            distance_km=distance_km,
            declared_value=float(declared_value)
        )

        total_price = delivery_breakdown['total_price'] + pickup_fee

        # Create the parcel
        parcel = Parcel.objects.create(
            tracking_number=generate_tracking_number(),
            submission_type='PICKUP',
            sender=pickup.customer,
            receiver_name=receiver_name,
            receiver_phone=receiver_phone,
            receiver_address=receiver_address,
            receiver_city=receiver_city,
            receiver_postal_code=receiver_postal_code,
            origin_branch=pickup.destination_branch,  # Parcel comes TO destination, from customer
            destination_branch=request.data.get('destination_branch', pickup.destination_branch),
            current_branch=pickup.destination_branch,
            weight_kg=pickup.weight_kg,
            declared_value=declared_value,
            delivery_price=delivery_breakdown['total_price'],
            pickup_fee=pickup_fee,
            total_price=total_price,
            status='RECEIVED',
            notes=pickup.parcel_description
        )

        # Link pickup request to parcel
        pickup.estimated_parcel = parcel
        pickup.save()

        # Create initial tracking history
        ParcelTrackingHistory.objects.create(
            parcel=parcel,
            status='RECEIVED',
            branch=parcel.origin_branch,
            updated_by=request.user,
            notes='Parcel received from pickup'
        )

        ip_address = get_client_ip(request)
        AuditLogger.log_action(
            user=request.user,
            action='CREATE',
            model_name='Parcel',
            object_id=str(parcel.id),
            object_display=parcel.tracking_number,
            description=f'Parcel created from pickup request {pickup.id}',
            ip_address=ip_address
        )

        from apps.parcels.serializers import ParcelDetailSerializer
        serializer = ParcelDetailSerializer(parcel)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'])
    def pending_count(self, request):
        """Get count of pending pickup requests"""
        count = PickupRequest.objects.filter(status='PENDING').count()
        return Response({'pending_count': count})


class DeliveryProofViewSet(viewsets.ModelViewSet):
    """Delivery proof management viewset"""
    queryset = DeliveryProof.objects.all()
    serializer_class = DeliveryProofSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        proof = serializer.save(uploaded_by=self.request.user)
        ip_address = get_client_ip(self.request)
        AuditLogger.log_action(
            user=self.request.user,
            action='DELIVERY_CONFIRMATION',
            model_name='DeliveryProof',
            object_id=str(proof.id),
            object_display=proof.parcel.tracking_number,
            description='Delivery proof uploaded',
            ip_address=ip_address
        )

    def get_queryset(self):
        """Filter delivery proofs"""
        parcel_id = self.request.query_params.get('parcel_id')
        if parcel_id:
            return DeliveryProof.objects.filter(parcel_id=parcel_id)
        return DeliveryProof.objects.all()
