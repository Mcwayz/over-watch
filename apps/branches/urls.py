"""
URL configuration for branches app
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.branches.views import BranchViewSet

router = DefaultRouter()
router.register(r'', BranchViewSet, basename='branch')

urlpatterns = [
    path('', include(router.urls)),
]
