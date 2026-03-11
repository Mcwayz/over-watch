from django.db import models
from django.conf import settings
import uuid


class Notification(models.Model):
    """Notification model for user notifications"""
    
    NOTIFICATION_TYPE_CHOICES = [
        ('parcel_dispatched', 'Parcel Dispatched'),
        ('parcel_arrived', 'Parcel Arrived'),
        ('parcel_out_for_delivery', 'Out for Delivery'),
        ('parcel_delivered', 'Parcel Delivered'),
        ('pickup_scheduled', 'Pickup Scheduled'),
        ('pickup_completed', 'Pickup Completed'),
        ('pickup_reminder', 'Pickup Reminder'),
        ('status_update', 'Status Update'),
        ('system', 'System Notification'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPE_CHOICES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='normal')
    
    # Related object (optional)
    related_object_id = models.CharField(max_length=100, null=True, blank=True)
    related_object_type = models.CharField(max_length=50, null=True, blank=True)
    
    # Read status
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    
    # Email/SMS status (for future use)
    email_sent = models.BooleanField(default=False)
    sms_sent = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', '-created_at']),
            models.Index(fields=['recipient', 'is_read']),
        ]

    def __str__(self):
        return f"{self.title} - {self.recipient.username}"


class NotificationPreference(models.Model):
    """User notification preferences"""
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notification_preference'
    )
    
    # Email notifications
    email_dispatched = models.BooleanField(default=True)
    email_arrived = models.BooleanField(default=True)
    email_out_for_delivery = models.BooleanField(default=True)
    email_delivered = models.BooleanField(default=True)
    email_pickup = models.BooleanField(default=True)
    email_system = models.BooleanField(default=True)
    
    # In-app notifications
    inapp_dispatched = models.BooleanField(default=True)
    inapp_arrived = models.BooleanField(default=True)
    inapp_out_for_delivery = models.BooleanField(default=True)
    inapp_delivered = models.BooleanField(default=True)
    inapp_pickup = models.BooleanField(default=True)
    inapp_system = models.BooleanField(default=True)
    
    # SMS notifications (future)
    sms_enabled = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'notification_preferences'

    def __str__(self):
        return f"Notification preferences for {self.user.username}"


class NotificationLog(models.Model):
    """Log of sent notifications"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    notification = models.ForeignKey(
        Notification,
        on_delete=models.CASCADE,
        related_name='logs'
    )
    channel = models.CharField(max_length=20)  # email, sms, inapp
    status = models.CharField(max_length=20)  # sent, failed, pending
    error_message = models.TextField(blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notification_logs'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.notification.title} - {self.channel} - {self.status}"

