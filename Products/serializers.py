from rest_framework import serializers
from .models import *

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class SubCategorySerializer(serializers.ModelSerializer):
    # product = ProductSerializer(many=True, read_only=True)
    class Meta:
        model = SubCategory
        fields = '__all__'

class CategorySerializer(serializers.ModelSerializer):
    # subcategory = SubCategorySerializer(many=True, read_only=True)
    class Meta:
        model = Category
        fields = '__all__'
        