from .models import *
from .serializers import *
from rest_framework import generics
from rest_framework import permissions
from rest_framework.exceptions import ValidationError
# Create your views here.

class SurveyListCreateView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = OnboardingSurvey.objects.all()
    serializer_class = SurveySerializer
    def perform_create(self, serializer):
        if hasattr(self.request.user, "survey"):
            raise ValidationError({"detail": "You have already submitted a survey."})
        serializer.save(user=self.request.user)

class SurveyRetrieveUpdateDestroyView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = OnboardingSurvey.objects.all()
    serializer_class = SurveySerializer
    def get_object(self):
        try:
            return self.request.user.survey
        except OnboardingSurvey.DoesNotExist:
            raise ValidationError({"error": "Survey not found."})
