"""
Helper utilities for common operations
"""
import uuid
from django.utils import timezone


def generate_tracking_number():
    """Generate a unique tracking number"""
    timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
    unique_id = str(uuid.uuid4())[:8].upper()
    return f"TRK{timestamp}{unique_id}"


def generate_employee_id(role):
    """Generate employee ID based on role"""
    timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
    unique_id = str(uuid.uuid4())[:4].upper()
    role_prefix = {
        'staff': 'STF',
        'driver': 'DRV',
    }
    prefix = role_prefix.get(role, 'EMP')
    return f"{prefix}{timestamp[-6:]}{unique_id}"


def generate_customer_id():
    """Generate unique customer ID"""
    timestamp = timezone.now().strftime('%Y%m%d')
    unique_id = str(uuid.uuid4())[:6].upper()
    return f"CUST{timestamp}{unique_id}"


def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
