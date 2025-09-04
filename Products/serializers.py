from rest_framework import serializers
from .models import *

class ProductSerializer(serializers.ModelSerializer):
    sizes = serializers.StringRelatedField(many=True)
    widths = serializers.StringRelatedField(many=True)
    class Meta:
        model = Product
        exclude = ['created_at', 'updated_at']

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

class PdfFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = PdfFile
        fields = ['id', 'user', 'pdf_file', 'uploaded_at']
        read_only_fields = ['id', 'uploaded_at', 'user']