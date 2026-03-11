"""
Vehicle models for managing vehicles in the courier system
"""
from django.db import models
from django.core.validators import RegexValidator
import uuid


class Vehicle(models.Model):
    """Vehicle model for managing delivery vehicles"""
    VEHICLE_TYPE_CHOICES = [
        ('motorcycle', 'Motorcycle'),
        ('car', 'Car'),
        ('van', 'Van'),
        ('truck', 'Truck'),
    ]
    
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('in_use', 'In Use'),
        ('maintenance', 'Under Maintenance'),
        ('retired', 'Retired'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vehicle_number = models.CharField(max_length=20, unique=True)
    vehicle_name = models.CharField(max_length=200)
    vehicle_type = models.CharField(max_length=20, choices=VEHICLE_TYPE_CHOICES)
    license_plate = models.CharField(max_length=20, unique=True)
    capacity_kg = models.PositiveIntegerField()
    current_branch = models.ForeignKey(
        'branches.Branch',
        on_delete=models.PROTECT,
        related_name='vehicles'
    )
    assigned_driver = models.ForeignKey(
        'drivers.DriverProfile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_vehicles'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    current_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    current_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    current_location = models.CharField(max_length=200, blank=True)
    fuel_level = models.PositiveIntegerField(default=100)  # Percentage
    is_active = models.BooleanField(default=True)
    last_maintenance_date = models.DateField(null=True, blank=True)
    next_maintenance_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'vehicles'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.vehicle_name} - {self.vehicle_number}"

    @property
    def parcel_count(self):
        """Get count of parcels currently on this vehicle"""
        return self.parcels.filter(status__in=['LOADED', 'DISPATCHED', 'IN_TRANSIT']).count()

    @property
    def total_weight_kg(self):
        """Get total weight of parcels on this vehicle"""
        from decimal import Decimal
        total = Decimal('0')
        for parcel in self.parcels.filter(status__in=['LOADED', 'DISPATCHED', 'IN_TRANSIT']):
            total += parcel.weight_kg
        return total


class VehicleMaintenance(models.Model):
    """Model for tracking vehicle maintenance records"""
    MAINTENANCE_TYPE_CHOICES = [
        ('oil_change', 'Oil Change'),
        ('tire_rotation', 'Tire Rotation'),
        ('brake_service', 'Brake Service'),
        ('general_checkup', 'General Checkup'),
        ('repair', 'Repair'),
        ('other', 'Other'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='maintenance_records')
    maintenance_type = models.CharField(max_length=30, choices=MAINTENANCE_TYPE_CHOICES)
    description = models.TextField()
    cost = models.DecimalField(max_digits=12, decimal_places=2)
    performed_by = models.CharField(max_length=200)
    performed_date = models.DateField()
    next_due_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'vehicle_maintenance'
        ordering = ['-performed_date']

    def __str__(self):
        return f"{self.vehicle.vehicle_number} - {self.get_maintenance_type_display()}"

