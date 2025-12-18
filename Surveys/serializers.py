from .models import *
from rest_framework import serializers


class SurveySerializer(serializers.ModelSerializer):
    class Meta:
        model = OnboardingSurvey
        fields = '__all__'
        read_only_fields = ["id", "created_at", "user"]
    
    