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
    ordering = ['name']
    queryset = Category.objects.all()


class SubcategoryListView(generics.ListAPIView):
    serializer_class = SubCategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = {'category'}
    ordering = ['name'] 
    queryset = SubCategory.objects.all()
