# serializers.py
from rest_framework import serializers
from .models import *
# class QuesSerializer(serializers.ModelSerializer):
#     sub_category = serializers.CharField(source="parent.sub_category", read_only=True)

#     class Meta:
#         model = Ans
#         fields = ("id", "questions", "sub_category")


class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = ("question_de", "question_it", "answer_de", "answer_it")

class NewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = ("title_de", "title_it", "image", "content_de", "content_it", "created_at")

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ("user", "amount", "created_at")