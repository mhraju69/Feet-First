from rest_framework import serializers
from Brands.serializers import *
from .models import *

class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = ["color"]

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id','image']

class ProductSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField() 
    match_percentage = serializers.SerializerMethodField()
    colors = serializers.SerializerMethodField()
    brand = serializers.SerializerMethodField()
    favourite = serializers.SerializerMethodField()
    brand = BrandSerializer(read_only=True)
    class Meta:
        model = Product
        fields = ['id','image',"name","colors","gender","price","match_percentage","brand",'favourite','sub_category']

    def get_image(self, obj):
        primary = obj.images.filter().first()
        if primary:
            return ProductImageSerializer(primary).data
        return None
    
    def get_match_percentage(self, obj,):
        scan = self.context.get("scan")
        if scan:
            return obj.match_with_scan(scan)
        return None
    def get_brand(self, obj):
        return obj.brand.name
    
    def get_colors(self, obj):
        return [color.hex_code for color in obj.colors.all()]

    def get_favourite(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return Favorite.objects.filter(user=request.user,products=obj).exists()
        return False

class ProductDetailsSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True)
    sizes = serializers.SerializerMethodField()
    colors = serializers.SerializerMethodField()
    match_percentage = serializers.SerializerMethodField()
    brand = serializers.SerializerMethodField()
    favourite = serializers.SerializerMethodField()
    brand = BrandSerializer(read_only=True)


    class Meta:
        model = Product
        fields = [
            "id", "name", "colors", "images", "technical_data",'description',
            "brand", "main_category", "sub_category", "sizes",
            "toe_box", "further_information", "price", "discount", 
            "stock_quantity", "partner", "match_percentage", 'favourite'
        ]
    
    def get_match_percentage(self, obj):
        scan = self.context.get("scan")
        if scan:
            return obj.match_with_scan(scan)
        return None
    
    def get_sizes(self, obj):
        # Collect sizes from all linked SizeTables
        size_list = []
        for size_table in obj.sizes.all():  # SizeTable objects
            for size in size_table.sizes.all():  # related Size objects
                size_list.append(size.value)
        return size_list
    
    def get_colors(self, obj):
        return [color.hex_code for color in obj.colors.all()]
    
    def get_brand(self, obj):
        return obj.brand.name
    
    def get_favourite(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return Favorite.objects.filter(user=request.user,products=obj).exists()
        return False

class FootScanSerializer(serializers.ModelSerializer):
    class Meta:
        model = FootScan
        fields = "__all__"
        read_only_fields = ["id", "created_at",'user']

class FavoriteSerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True, read_only=True)

    class Meta:
        model = Favorite
        fields = ['id', 'user', 'products']
        read_only_fields = ['user']
