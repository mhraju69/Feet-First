from .models import *
from .serializers import *
from django.shortcuts import render
from rest_framework import generics
from rest_framework import permissions
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
# Create your views here.

class CategoryListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CategorySerializer
    filter_backends = [OrderingFilter]
    queryset = Category.objects.all()


class SubcategoryListView(generics.ListAPIView):
    serializer_class = SubCategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = SubCategory.objects.all()


class ProductListView(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]

    filterset_fields = {'category'}
    ordering = ['-created_at'] 
    
    queryset = Product.objects.all()

class ProductDetailView(generics.RetrieveAPIView):
    serializer_class = ProductDetailsSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = Product.objects.all()
    lookup_field = 'id'

class PDFFileUploadView(generics.CreateAPIView):
    queryset = PdfFile.objects.all()
    serializer_class = PdfFileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user) 