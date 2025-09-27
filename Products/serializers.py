from rest_framework import serializers
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

    class Meta:
        model = Product
        fields = ['id','image',"name","gender","price","match_percentage"]

    def get_image(self, obj):
        primary = obj.images.filter(is_primary=True).first()
        if primary:
            return ProductImageSerializer(primary).data
        return None
    
    def get_match_percentage(self, obj,):
        scan = self.context.get("scan")
        if scan:
            return obj.match_with_scan(scan)
        return None

class ProductDetailsSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True)
    sizes = serializers.SerializerMethodField()
    colors = serializers.SerializerMethodField()
    technical_data = serializers.SerializerMethodField()
    match_percentage = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id", "name", "colors", "images", "technical_data",
            "brand", "main_category", "sub_category", "sizes",
            "toe_box", "further_information", "price", "discount", 
            "stock_quantity", "partner", "match_percentage"
        ]
    
    def get_technical_data(self, obj):
        data = {}
        if obj.technical_data:
            for line in obj.technical_data.splitlines():
                if ':' in line:
                    key, value = line.split(':', 1)
                    data[key.strip()] = value.strip()
        return data
    
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
                size_list.append(
                    f"{size.type.upper()} {size.value} {size.insole_min_mm}-{size.insole_max_mm}"
                )
        return size_list
    
    def get_colors(self, obj):
        return [", ".join(color.color for color in obj.colors.all())
]

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
