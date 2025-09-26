# serializers.py
from rest_framework import serializers
from .models import *
class QuesSerializer(serializers.ModelSerializer):
    sub_category = serializers.CharField(source="parent.sub_category", read_only=True)

    class Meta:
        model = Ans
        fields = ("id", "questions", "sub_category")
