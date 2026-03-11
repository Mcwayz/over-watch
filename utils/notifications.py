"""
Notification utility module for sending notifications
"""
from apps.notifications.models import Notification, NotificationPreference
from apps.notifications.views import create_notification as create_notification_util


class NotificationService:
    """Service for creating and sending notifications"""
    
    @staticmethod
    def notify_parcel_dispatched(parcel):
        """Send notification when parcel is dispatched"""
        recipient = parcel.sender.user
        pref = NotificationPreference.objects.filter(user=recipient).first()
        
        if pref and not pref.email_dispatched:
            return None
            
        return create_notification_util(
            recipient=recipient,
            notification_type='parcel_dispatched',
            title='Parcel Dispatched',
            message=f'Your parcel {parcel.tracking_number} has been dispatched and is on its way.',
            priority='normal',
            related_object_id=str(parcel.id),
            related_object_type='parcel'
        )
    
    @staticmethod
    def notify_parcel_arrived(parcel):
        """Send notification when parcel arrives at destination branch"""
        recipient = parcel.sender.user
        pref = NotificationPreference.objects.filter(user=recipient).first()
        
        if pref and not pref.email_arrived:
            return None
            
        return create_notification_util(
            recipient=recipient,
            notification_type='parcel_arrived',
            title='Parcel Arrived',
            message=f'Your parcel {parcel.tracking_number} has arrived at the destination branch.',
            priority='normal',
            related_object_id=str(parcel.id),
            related_object_type='parcel'
        )
    
    @staticmethod
    def notify_parcel_out_for_delivery(parcel):
        """Send notification when parcel is out for delivery"""
        recipient = parcel.sender.user
        pref = NotificationPreference.objects.filter(user=recipient).first()
        
        if pref and not pref.email_out_for_delivery:
            return None
            
        return create_notification_util(
            recipient=recipient,
            notification_type='parcel_out_for_delivery',
            title='Out for Delivery',
            message=f'Your parcel {parcel.tracking_number} is out for delivery.',
            priority='high',
            related_object_id=str(parcel.id),
            related_object_type='parcel'
        )
    
    @staticmethod
    def notify_parcel_delivered(parcel):
        """Send notification when parcel is delivered"""
        recipient = parcel.sender.user
        pref = NotificationPreference.objects.filter(user=recipient).first()
        
        if pref and not pref.email_delivered:
            return None
            
        return create_notification_util(
            recipient=recipient,
            notification_type='parcel_delivered',
            title='Parcel Delivered',
            message=f'Your parcel {parcel.tracking_number} has been delivered successfully.',
            priority='normal',
            related_object_id=str(parcel.id),
            related_object_type='parcel'
        )
    
    @staticmethod
    def notify_pickup_scheduled(pickup_request):
        """Send notification when pickup is scheduled"""
        recipient = pickup_request.customer.user
        pref = NotificationPreference.objects.filter(user=recipient).first()
        
        if pref and not pref.email_pickup:
            return None
            
        return create_notification_util(
            recipient=recipient,
            notification_type='pickup_scheduled',
            title='Pickup Scheduled',
            message=f'Your pickup request has been scheduled. Driver will collect your parcel on {pickup_request.preferred_pickup_date}.',
            priority='normal',
            related_object_id=str(pickup_request.id),
            related_object_type='pickup_request'
        )
    
    @staticmethod
    def notify_pickup_completed(pickup_request, parcel):
        """Send notification when pickup is completed"""
        recipient = pickup_request.customer.user
        pref = NotificationPreference.objects.filter(user=recipient).first()
        
        if pref and not pref.email_pickup:
            return None
            
        return create_notification_util(
            recipient=recipient,
            notification_type='pickup_completed',
            title='Pickup Completed',
            message=f'Your parcel has been collected. Tracking number: {parcel.tracking_number}',
            priority='normal',
            related_object_id=str(pickup_request.id),
            related_object_type='pickup_request'
        )
    
    @staticmethod
    def notify_status_update(parcel, old_status, new_status):
        """Send notification for status update"""
        recipient = parcel.sender.user
        pref = NotificationPreference.objects.filter(user=recipient).first()
        
        if pref and not pref.inapp_status_update:
            return None
            
        return create_notification_util(
            recipient=recipient,
            notification_type='status_update',
            title='Parcel Status Update',
            message=f'Your parcel {parcel.tracking_number} status: {old_status} → {new_status}',
            priority='low',
            related_object_id=str(parcel.id),
            related_object_type='parcel'
        )
    
    @staticmethod
    def send_bulk_notification(user_ids, notification_type, title, message, priority='normal'):
        """Send notification to multiple users"""
        notifications = []
        for user_id in user_ids:
            from apps.authentication.models import CustomUser
            try:
                user = CustomUser.objects.get(id=user_id)
                notification = create_notification_util(
                    recipient=user,
                    notification_type=notification_type,
                    title=title,
                    message=message,
                    priority=priority
                )
                notifications.append(notification)
            except CustomUser.DoesNotExist:
                continue
        return notifications

