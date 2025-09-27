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
    queryset = Questions.objects.all()
    serializer_class = FAQSerializer
    permission_classes = [permissions.IsAuthenticated]  