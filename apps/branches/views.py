"""
Views for branches app
"""

from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema

from apps.branches.models import Branch
from apps.branches.serializers import BranchSerializer


@extend_schema(tags=["branches"])
class BranchViewSet(viewsets.ModelViewSet):
    """Branch management viewset"""

    queryset = Branch.objects.all()
    serializer_class = BranchSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    filterset_fields = ["city", "is_active"]
    search_fields = ["name", "city", "address"]
    ordering_fields = ["name", "created_at"]
    ordering = ["name"]