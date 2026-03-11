from django.db import models
from django.core.validators import RegexValidator
import uuid


class DriverProfile(models.Model):
    """Driver profile model"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField('authentication.CustomUser', on_delete=models.CASCADE, related_name='driver_profile')
    branch = models.ForeignKey('branches.Branch', on_delete=models.PROTECT, related_name='drivers')
    driver_id = models.CharField(max_length=50, unique=True)
    license_number = models.CharField(max_length=50, unique=True)
    license_expiry_date = models.DateField()
    phone_number = models.CharField(
        max_length=20,
        validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$')]
    )
    vehicle_name = models.CharField(max_length=200)
    vehicle_number = models.CharField(max_length=20, unique=True)
    vehicle_type = models.CharField(max_length=100, choices=[
        ('motorcycle', 'Motorcycle'),
        ('car', 'Car'),
        ('van', 'Van'),
        ('truck', 'Truck'),
    ])
    vehicle_capacity_kg = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)
    hire_date = models.DateField()
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=5.0)
    total_deliveries = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'driver_profiles'
        unique_together = ('branch', 'driver_id')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.vehicle_number}"
