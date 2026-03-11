"""
URL configuration for authentication app
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.authentication.views import (
    CustomTokenObtainPairView, LoginView, RegisterView,
    UserViewSet, RoleViewSet
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'roles', RoleViewSet, basename='role')

urlpatterns = [
    path('', include(router.urls)),
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('login/', LoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
]
