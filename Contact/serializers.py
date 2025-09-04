from .models import *
from rest_framework import serializers


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactUs
        exclude = ['read', 'created_at']
