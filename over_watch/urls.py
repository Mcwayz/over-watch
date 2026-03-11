"""
URL configuration for over_watch project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # API routes
    path('api/auth/', include('apps.authentication.urls')),
    path('api/branches/', include('apps.branches.urls')),
    path('api/staff/', include('apps.staff.urls')),
    path('api/drivers/', include('apps.drivers.urls')),
    path('api/customers/', include('apps.customers.urls')),
    path('api/parcels/', include('apps.parcels.urls')),
    path('api/vehicles/', include('apps.vehicles.urls')),
    path('api/audit/', include('apps.audit.urls')),
    path('api/notifications/', include('apps.notifications.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

