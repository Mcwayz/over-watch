"""
Admin configuration for customers app
"""
from django.contrib import admin
from apps.customers.models import CustomerProfile


@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ['customer_id', 'user', 'city', 'total_parcels_sent', 'is_verified', 'created_at']
    list_filter = ['city', 'is_verified', 'created_at']
    search_fields = ['customer_id', 'user__username', 'user__first_name', 'user__last_name', 'phone_number']
