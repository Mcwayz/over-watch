from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import EmailValidator
import uuid


class Role(models.Model):
    """Role model for role-based access control"""
    MANAGER = 'manager'
    STAFF = 'staff'
    DRIVER = 'driver'
    CUSTOMER = 'customer'

    ROLE_CHOICES = [
        (MANAGER, 'Manager'),
        (STAFF, 'Staff'),
        (DRIVER, 'Driver'),
        (CUSTOMER, 'Customer'),
    ]

    id = models.CharField(max_length=50, choices=ROLE_CHOICES, primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'roles'
        verbose_name = 'Role'
        verbose_name_plural = 'Roles'

    def __str__(self):
        return self.name


class CustomUser(AbstractUser):
    """Custom user model with role-based access"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, validators=[EmailValidator()])
    role = models.ForeignKey(Role, on_delete=models.PROTECT)
    is_active = models.BooleanField(default=True)
    phone_number = models.CharField(max_length=20, blank=True)
    profile_image = models.ImageField(upload_to='profile_images/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    def get_role_display(self):
        return self.role.get_id_display()


class Permission(models.Model):
    """Permissions model for fine-grained access control"""
    PERMISSION_CHOICES = [
        ('can_create_staff', 'Can Create Staff'),
        ('can_update_staff', 'Can Update Staff'),
        ('can_delete_staff', 'Can Delete Staff'),
        ('can_view_staff', 'Can View Staff'),
        ('can_create_driver', 'Can Create Driver'),
        ('can_update_driver', 'Can Update Driver'),
        ('can_delete_driver', 'Can Delete Driver'),
        ('can_view_driver', 'Can View Driver'),
        ('can_register_parcel', 'Can Register Parcel'),
        ('can_update_parcel_status', 'Can Update Parcel Status'),
        ('can_view_parcel', 'Can View Parcel'),
        ('can_upload_parcel_image', 'Can Upload Parcel Image'),
        ('can_scan_qr_code', 'Can Scan QR Code'),
        ('can_track_parcel', 'Can Track Parcel'),
        ('can_request_pickup', 'Can Request Pickup'),
        ('can_view_audit_logs', 'Can View Audit Logs'),
        ('can_view_reports', 'Can View Reports'),
    ]

    id = models.CharField(max_length=50, choices=PERMISSION_CHOICES, primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        db_table = 'permissions'

    def __str__(self):
        return self.name


class RolePermission(models.Model):
    """Through model for many-to-many relationship between Role and Permission"""
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='permissions')
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('role', 'permission')
        db_table = 'role_permissions'

    def __str__(self):
        return f"{self.role.name} - {self.permission.name}"
