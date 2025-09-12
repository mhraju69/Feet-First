from django.shortcuts import get_object_or_404
from .models import *
from .serializers import *
from rest_framework import permissions
from rest_framework import generics,views
from rest_framework.response import Response
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from .utils import *

# Create your views here.

class ProductListView(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True)
        main = self.request.query_params.get("main_category")
        sub = self.request.query_params.get("sub_category")

        if main and sub:
            s = queryset.filter(sub_category=sub)
            m = queryset.filter(main_category=main)
            if s:
                queryset = s & m
            else:
                queryset = m
        else:
            queryset = queryset.all()

        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        scan_id = self.request.query_params.get("scan_id")
        
        if scan_id:
            try:
                # Get the scan object
                scan = get_object_or_404(FootScan,user=self.request.user, id=scan_id)
                context['scan'] = scan
            except FootScan.DoesNotExist:
                pass
                
        return context
    
class ProductDetailView(generics.RetrieveAPIView):
    serializer_class = ProductDetailsSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Product.objects.filter(is_active = True)
    lookup_field = 'id'
    def get_serializer_context(self):
        context = super().get_serializer_context()
        scan_id = self.request.query_params.get("scan_id")

        if scan_id:
            try:
                # Get the scan object
                scan = get_object_or_404(FootScan,user=self.request.user, id=scan_id)
                context['scan'] = scan
            except FootScan.DoesNotExist:
                pass
                
        return context

class FootScanListCreateView(generics.ListCreateAPIView):
    """List all foot scans or create a new one."""
    serializer_class = FootScanSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Customers only see their own scans
        user = self.request.user
        if user.role == "customer":
            return FootScan.objects.filter(user=user)
        # Admins/staff see all
        return FootScan.objects.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class FootScanDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a foot scan."""
    serializer_class = FootScanSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == "customer":
            return FootScan.objects.filter(user=user)
        return FootScan.objects.all()

