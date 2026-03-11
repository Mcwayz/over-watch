from django.db import models
import uuid


class AuditLog(models.Model):
    """Audit logging model for tracking all system actions"""
    ACTION_CHOICES = [
        ('CREATE', 'Create'),
        ('UPDATE', 'Update'),
        ('DELETE', 'Delete'),
        ('VIEW', 'View'),
        ('LOGIN', 'Login'),
        ('LOGOUT', 'Logout'),
        ('PARCEL_STATUS_CHANGE', 'Parcel Status Change'),
        ('IMAGE_UPLOAD', 'Image Upload'),
        ('QR_SCAN', 'QR Code Scan'),
        ('TRANSIT_UPDATE', 'Transit Update'),
        ('PICKUP_REQUEST', 'Pickup Request'),
        ('DELIVERY_CONFIRMATION', 'Delivery Confirmation'),
        ('REPORT_GENERATED', 'Report Generated'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        'authentication.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        related_name='audit_logs'
    )
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    model_name = models.CharField(max_length=100)
    object_id = models.CharField(max_length=500, null=True, blank=True)
    object_display = models.CharField(max_length=500)
    description = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    old_values = models.JSONField(null=True, blank=True)
    new_values = models.JSONField(null=True, blank=True)
    status_code = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = 'audit_logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['action', '-created_at']),
            models.Index(fields=['model_name', '-created_at']),
        ]

    def __str__(self):
        return f"{self.action} - {self.model_name} ({self.object_display})"
