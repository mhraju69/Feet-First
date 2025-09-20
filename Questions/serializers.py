# serializers.py
from rest_framework import serializers
from .models import *
class QuesSerializer(serializers.ModelSerializer):
    sub_category = serializers.CharField(source="parent.sub_category", read_only=True)

    class Meta:
        model = Ques
        fields = ("id", "questions", "sub_category")

class AnswerItemSerializer(serializers.ModelSerializer):
    question = serializers.PrimaryKeyRelatedField(queryset=Ques.objects.all())

    class Meta:
        model = AnswerItem
        fields = ("question", "answer_text")

class AnswerSerializer(serializers.ModelSerializer):
    items = AnswerItemSerializer(many=True)

    class Meta:
        model = Answer
        fields = ("id", "user", "items")
        read_only_fields = ("id", "user")

    def create(self, validated_data):
        user = self.context['request'].user
        items_data = validated_data.pop('items')
        # create parent Answer
        answer_parent, _ = Answer.objects.get_or_create(user=user)
        # create child AnswerItems
        for item in items_data:
            AnswerItem.objects.create(parent=answer_parent, **item)
        return answer_parent
