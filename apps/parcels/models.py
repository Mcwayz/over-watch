from django.db import models
from django.core.validators import MinValueValidator
import uuid
import qrcode
from io import BytesIO
from django.core.files import File
from django.utils import timezone


class Parcel(models.Model):
    """Parcel model for managing parcels"""
    STATUS_CHOICES = [
        ('REGISTERED', 'Registered'),
        ('RECEIVED', 'Received'),
        ('LOADED', 'Loaded'),
        ('DISPATCHED', 'Dispatched'),
        ('IN_TRANSIT', 'In Transit'),
        ('ARRIVED', 'Arrived'),
        ('OUT_FOR_DELIVERY', 'Out for Delivery'),
        ('DELIVERED', 'Delivered'),
    ]
    
    SUBMISSION_TYPE_CHOICES = [
        ('BRANCH_DROPOFF', 'Branch Drop-Off'),
        ('PICKUP', 'Pickup Request'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tracking_number = models.CharField(max_length=50, unique=True)
    submission_type = models.CharField(max_length=20, choices=SUBMISSION_TYPE_CHOICES, default='BRANCH_DROPOFF')
    sender = models.ForeignKey(
        'customers.CustomerProfile',
        on_delete=models.PROTECT,
        related_name='sent_parcels'
    )
    receiver_name = models.CharField(max_length=200)
    receiver_phone = models.CharField(max_length=20)
    receiver_address = models.TextField()
    receiver_city = models.CharField(max_length=100)
    receiver_postal_code = models.CharField(max_length=20)
    origin_branch = models.ForeignKey(
        'branches.Branch',
        on_delete=models.PROTECT,
        related_name='origin_parcels'
    )
    destination_branch = models.ForeignKey(
        'branches.Branch',
        on_delete=models.PROTECT,
        related_name='destination_parcels'
    )
    current_branch = models.ForeignKey(
        'branches.Branch',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='current_parcels'
    )
    weight_kg = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.1)])
    declared_value = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    delivery_price = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    pickup_fee = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)], default=0)
    total_price = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)], default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='REGISTERED')
    assigned_driver = models.ForeignKey(
        'drivers.DriverProfile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_parcels'
    )
    assigned_vehicle = models.ForeignKey(
        'vehicles.Vehicle',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='parcels'
    )
    qr_code = models.ImageField(upload_to='qr_codes/', null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    delivered_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'parcels'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tracking_number']),
            models.Index(fields=['status']),
            models.Index(fields=['sender']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.tracking_number} - {self.receiver_name}"

    def save(self, *args, **kwargs):
        """Generate QR code on save"""
        is_new = self.pk is None
        super().save(*args, **kwargs)

        # Generate QR code if not exists
        if not self.qr_code:
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(self.tracking_number)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")

            # Save to file
            buf = BytesIO()
            img.save(buf, format='PNG')
            buf.seek(0)
            self.qr_code.save(f'qr_{self.tracking_number}.png', File(buf), save=False)
            super().save(update_fields=['qr_code'])

    def transition_to_status(self, new_status):
        """Validate and transition to new status"""
        valid_transitions = {
            'REGISTERED': ['RECEIVED'],
            'RECEIVED': ['LOADED'],
            'LOADED': ['DISPATCHED'],
            'DISPATCHED': ['IN_TRANSIT'],
            'IN_TRANSIT': ['ARRIVED'],
            'ARRIVED': ['OUT_FOR_DELIVERY'],
            'OUT_FOR_DELIVERY': ['DELIVERED'],
        }

        if new_status not in valid_transitions.get(self.status, []):
            raise ValueError(f"Cannot transition from {self.status} to {new_status}")

        self.status = new_status
        if new_status == 'DELIVERED':
            self.delivered_at = timezone.now()
        self.save()


class ParcelImage(models.Model):
    """Model for parcel images"""
    IMAGE_TYPE_CHOICES = [
        ('receipt', 'Receipt Confirmation'),
        ('packaging', 'Packaging'),
        ('loading', 'Loading Confirmation'),
        ('damage', 'Damage Evidence'),
        ('delivery', 'Delivery Proof'),
        ('other', 'Other'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    parcel = models.ForeignKey(Parcel, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='parcel_images/')
    image_type = models.CharField(max_length=20, choices=IMAGE_TYPE_CHOICES)
    uploaded_by = models.ForeignKey(
        'authentication.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        related_name='uploaded_parcel_images'
    )
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'parcel_images'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.parcel.tracking_number} - {self.get_image_type_display()}"


class ParcelTrackingHistory(models.Model):
    """Model to track parcel status history"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    parcel = models.ForeignKey(Parcel, on_delete=models.CASCADE, related_name='tracking_history')
    status = models.CharField(max_length=20, choices=Parcel.STATUS_CHOICES)
    branch = models.ForeignKey(
        'branches.Branch',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tracking_histories'
    )
    updated_by = models.ForeignKey(
        'authentication.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        related_name='parcel_status_updates'
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'parcel_tracking_history'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.parcel.tracking_number} - {self.status}"


class ParcelTransitUpdate(models.Model):
    """Model for parcel transit updates by drivers"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    parcel = models.ForeignKey(Parcel, on_delete=models.CASCADE, related_name='transit_updates')
    driver = models.ForeignKey(
        'drivers.DriverProfile',
        on_delete=models.SET_NULL,
        null=True,
        related_name='transit_updates'
    )
    location_name = models.CharField(max_length=200)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    transit_status = models.CharField(max_length=100, choices=[
        ('picked_up', 'Picked Up'),
        ('in_transit', 'In Transit'),
        ('reached_destination', 'Reached Destination'),
    ])
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'parcel_transit_updates'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.parcel.tracking_number} - {self.transit_status}"


class PickupRequest(models.Model):
    """Model for customer parcel pickup requests"""
    REQUEST_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('SCHEDULED', 'Scheduled'),
        ('PICKED_UP', 'Picked Up'),
        ('CANCELLED', 'Cancelled'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(
        'customers.CustomerProfile',
        on_delete=models.CASCADE,
        related_name='pickup_requests'
    )
    pickup_address = models.TextField()
    parcel_description = models.TextField()
    weight_kg = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.1)])
    destination_branch = models.ForeignKey(
        'branches.Branch',
        on_delete=models.PROTECT,
        related_name='requested_pickups'
    )
    status = models.CharField(max_length=20, choices=REQUEST_STATUS_CHOICES, default='PENDING')
    preferred_pickup_date = models.DateField()
    preferred_pickup_time = models.TimeField(null=True, blank=True)
    assigned_driver = models.ForeignKey(
        'drivers.DriverProfile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_pickups'
    )
    pickup_date = models.DateField(null=True, blank=True)
    estimated_parcel = models.OneToOneField(
        Parcel,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pickup_request'
    )
    rejection_reason = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'pickup_requests'
        ordering = ['-created_at']

    def __str__(self):
        return f"Pickup Request - {self.customer.customer_id} ({self.status})"


class DeliveryProof(models.Model):
    """Model for delivery proof"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    parcel = models.ForeignKey(Parcel, on_delete=models.CASCADE, related_name='delivery_proofs')
    proof_image = models.ImageField(upload_to='delivery_proofs/')
    uploaded_by = models.ForeignKey(
        'authentication.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        related_name='delivery_proofs'
    )
    delivery_notes = models.TextField(blank=True)
    signature_required = models.BooleanField(default=False)
    signature_image = models.ImageField(upload_to='signatures/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'delivery_proofs'
        ordering = ['-created_at']

    def __str__(self):
        return f"Delivery Proof - {self.parcel.tracking_number}"
