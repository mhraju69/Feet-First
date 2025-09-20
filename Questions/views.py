# views.py
from rest_framework import generics, permissions
from .models import Ques, Answer
from .serializers import QuesSerializer, AnswerSerializer

# 1️⃣ Get all questions
class QuesListAPIView(generics.ListAPIView):
    queryset = Ques.objects.select_related('parent').all()
    serializer_class = QuesSerializer
    permission_classes = [permissions.IsAuthenticated]  # only logged-in users

# 2️⃣ Add answers for current user
class AnswerCreateAPIView(generics.CreateAPIView):
    serializer_class = AnswerSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
