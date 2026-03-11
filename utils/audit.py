"""
Audit logging utility module
"""
from apps.audit.models import AuditLog
import json


class AuditLogger:
    """Audit logging utility"""

    @staticmethod
    def log_action(user, action, model_name, object_id, object_display,
                   description='', ip_address=None, user_agent='',
                   old_values=None, new_values=None, status_code=None):
        """
        Log an action to the audit trail

        Args:
            user: User performing the action
            action: Action type (CREATE, UPDATE, DELETE, etc.)
            model_name: Name of the model being acted upon
            object_id: ID of the object
            object_display: String representation of the object
            description: Detailed description of the action
            ip_address: IP address of the user
            user_agent: User agent string
            old_values: Previous values (for UPDATE actions)
            new_values: New values (for UPDATE actions)
            status_code: HTTP status code
        """
        audit_log = AuditLog.objects.create(
            user=user,
            action=action,
            model_name=model_name,
            object_id=str(object_id) if object_id else None,
            object_display=object_display,
            description=description,
            ip_address=ip_address,
            user_agent=user_agent,
            old_values=old_values,
            new_values=new_values,
            status_code=status_code,
        )
        return audit_log

    @staticmethod
    def log_parcel_status_change(parcel, user, old_status, new_status, ip_address=None):
        """Log parcel status change"""
        description = f"Parcel status changed from {old_status} to {new_status}"
        return AuditLogger.log_action(
            user=user,
            action='PARCEL_STATUS_CHANGE',
            model_name='Parcel',
            object_id=str(parcel.id),
            object_display=parcel.tracking_number,
            description=description,
            ip_address=ip_address,
            old_values={'status': old_status},
            new_values={'status': new_status},
        )

    @staticmethod
    def log_image_upload(image, user, ip_address=None):
        """Log image upload"""
        description = f"Image uploaded for parcel {image.parcel.tracking_number}"
        return AuditLogger.log_action(
            user=user,
            action='IMAGE_UPLOAD',
            model_name='ParcelImage',
            object_id=str(image.id),
            object_display=f"{image.parcel.tracking_number} - {image.get_image_type_display()}",
            description=description,
            ip_address=ip_address,
        )

    @staticmethod
    def log_qr_scan(parcel, user, ip_address=None):
        """Log QR code scan"""
        description = f"QR code scanned for parcel {parcel.tracking_number}"
        return AuditLogger.log_action(
            user=user,
            action='QR_SCAN',
            model_name='Parcel',
            object_id=str(parcel.id),
            object_display=parcel.tracking_number,
            description=description,
            ip_address=ip_address,
        )

    @staticmethod
    def log_transit_update(transit_update, user, ip_address=None):
        """Log transit update"""
        description = f"Transit update for parcel {transit_update.parcel.tracking_number}"
        return AuditLogger.log_action(
            user=user,
            action='TRANSIT_UPDATE',
            model_name='ParcelTransitUpdate',
            object_id=str(transit_update.id),
            object_display=transit_update.parcel.tracking_number,
            description=description,
            ip_address=ip_address,
        )

    @staticmethod
    def log_login(user, ip_address=None):
        """Log user login"""
        return AuditLogger.log_action(
            user=user,
            action='LOGIN',
            model_name='CustomUser',
            object_id=str(user.id),
            object_display=user.username,
            description=f"User {user.username} logged in",
            ip_address=ip_address,
        )

    @staticmethod
    def log_logout(user, ip_address=None):
        """Log user logout"""
        return AuditLogger.log_action(
            user=user,
            action='LOGOUT',
            model_name='CustomUser',
            object_id=str(user.id),
            object_display=user.username,
            description=f"User {user.username} logged out",
            ip_address=ip_address,
        )
