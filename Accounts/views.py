from .models import *
from .serializers import *
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions

# Create your views here.

class UserCreateView(generics.CreateAPIView):
    serializer_class = UserSerializer