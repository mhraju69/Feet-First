from django.shortcuts import render
from rest_framework import generics
from .models import *
from rest_framework import permissions
from .serializers import *
# Create your views here.

class BrandListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
