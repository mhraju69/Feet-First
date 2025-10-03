# views.py
from rest_framework import generics, permissions
from .models import *
from .serializers import *

# 1️⃣ Get all questions
class QuesListAPIView(generics.ListAPIView):
    queryset = Ans.objects.select_related('parent').all()
    serializer_class = QuesSerializer
    permission_classes = [permissions.IsAuthenticated] 

class FAQAPIView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]  
    queryset = FAQ.objects.all()
    serializer_class = FAQSerializer

class NewsAPIView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]  
    queryset = News.objects.all()
    serializer_class = NewsSerializer