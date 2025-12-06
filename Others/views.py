# views.py
from rest_framework import generics, permissions ,views
from .models import *
from .serializers import *
from django.views.decorators.csrf import csrf_exempt

class FAQAPIView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]  
    queryset = FAQ.objects.all()
    serializer_class = FAQSerializer

class NewsAPIView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]  
    queryset = News.objects.all()
    serializer_class = NewsSerializer