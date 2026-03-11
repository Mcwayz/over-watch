from django.db import models
from django.core.validators import RegexValidator
import uuid


class StaffProfile(models.Model):
    """Staff profile model"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField('authentication.CustomUser', on_delete=models.CASCADE, related_name='staff_profile')
    branch = models.ForeignKey('branches.Branch', on_delete=models.PROTECT, related_name='staff_members')
    employee_id = models.CharField(max_length=50, unique=True)
    position = models.CharField(max_length=100, choices=[
        ('operations_manager', 'Operations Manager'),
        ('parcel_clerk', 'Parcel Clerk'),
        ('loader', 'Loader'),
        ('dispatcher', 'Dispatcher'),
        ('other', 'Other'),
    ])
    phone_number = models.CharField(
        max_length=20,
        validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$')]
    )
    address = models.TextField()
    is_active = models.BooleanField(default=True)
    hire_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'staff_profiles'
        unique_together = ('branch', 'employee_id')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_position_display()}"
