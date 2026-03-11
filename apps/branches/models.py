from django.db import models
import uuid


class Branch(models.Model):
    """Branch model for courier company locations"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, unique=True)
    city = models.CharField(max_length=100)
    address = models.TextField()
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    contact_phone = models.CharField(max_length=20)
    contact_email = models.EmailField()
    manager_email = models.EmailField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'branches'
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def staff_count(self):
        """Get total staff at this branch"""
        from apps.staff.models import StaffProfile
        return StaffProfile.objects.filter(branch=self, is_active=True).count()

    @property
    def driver_count(self):
        """Get total drivers at this branch"""
        from apps.drivers.models import DriverProfile
        return DriverProfile.objects.filter(branch=self, is_active=True).count()
