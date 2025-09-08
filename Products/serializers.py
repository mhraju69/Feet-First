from rest_framework import serializers
from .models import *

class SubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = ['color' ,'code']

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id','image']

class ProductSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()  

    class Meta:
        model = Product
        fields = ['id','image',"name_de","name_it","price",]

    def get_image(self, obj):
        primary = obj.images.filter(is_primary=True).first()
        if primary:
            return ProductImageSerializer(primary).data
        return None
    
class ProductDetailsSerializer(serializers.ModelSerializer):
    sizes = serializers.StringRelatedField(many=True)
    widths = serializers.StringRelatedField(many=True)
    colors =SubCategorySerializer(many=True)
    images = ProductImageSerializer(many=True)

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

class PdfFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = PdfFile
        fields = ['id', 'user', 'pdf_file', 'uploaded_at']
        read_only_fields = ['id', 'uploaded_at', 'user']