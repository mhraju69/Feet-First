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
    match_percentage = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id','image',"name_de","name_it","price","match_percentage"]

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
    colors = SubCategorySerializer(many=True)
    images = ProductImageSerializer(many=True)
    technical_data = serializers.SerializerMethodField()
    match_percentage = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ["id", "colors", "images", "technical_data", "name_de", "name_it", 
                  "brand", "main_category", "sub_category", "size_system", "size_value", 
                  "width_category", "toe_box", "further_information", "price", "discount", 
                  "stock_quantity", "partner", "match_percentage"]  # Added match_percentage
    
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
    
class FootScanSerializer(serializers.ModelSerializer):
    class Meta:
        model = FootScan
        fields = "__all__"
        read_only_fields = ["id", "created_at",'user']

class OrderSerializer(serializers.ModelSerializer):
    products = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), many=True
    )
    partner = serializers.PrimaryKeyRelatedField(
        read_only=True, many=True
    )

    class Meta:
        model = Order
        fields = [
            "id", "order_number", "products",
            "partner", "shipping_address", "billing_address",
            "total_amount", "status", "notes",  
            "created_at", "updated_at"
        ]
        read_only_fields = ["order_number", "total_amount", "customer", "partner", "created_at", "updated_at"]

    def create(self, validated_data):
        products = validated_data.pop("products", [])
        order = Order.objects.create(**validated_data)
        order.products.set(products)
        order.save()  # partners + total auto-updated
        return order

class FavouriteSerializer(serializers.ModelSerializer):
    product = ProductSerializer(many=True)
    class Meta:
        model = Favourite
        fields = ['id', 'user', 'product', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']
