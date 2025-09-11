from .models import *
from .serializers import *
from django.shortcuts import render
from rest_framework import generics
from rest_framework import permissions
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
# Create your views here.

class ProductListView(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]

    filterset_fields = {'category'}
    ordering = ['-created_at'] 
    
    queryset = Product.objects.filter(is_active = True)

class ProductDetailView(generics.RetrieveAPIView):
    serializer_class = ProductDetailsSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = Product.objects.filter(is_active = True)
    lookup_field = 'id'

class PDFFileUploadView(generics.CreateAPIView):
    queryset = PdfFile.objects.all()
    serializer_class = PdfFileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user) 

