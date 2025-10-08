from rest_framework import serializers
from Brands.serializers import *
from .models import *
from Others.models import *

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image']

class SizeRecommendationSerializer(serializers.Serializer):
    """Serializer for individual size recommendations"""
    size = serializers.CharField(source='size_value')  # Just the value

class MatchAnalysisSerializer(serializers.Serializer):
    """Serializer for detailed match analysis"""
    score = serializers.FloatField()
    recommended_sizes = SizeRecommendationSerializer(many=True)

class ProductSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField() 
    match_data = serializers.SerializerMethodField()
    colors = serializers.SerializerMethodField()
    brand = serializers.SerializerMethodField()
    favourite = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'image', 'name', 'colors', 'gender', 'price', 
            'match_data', 'brand', 'favourite', 'sub_category'
        ]

    def get_image(self, obj):
        primary = obj.images.first()
        if primary:
            return ProductImageSerializer(primary).data
        return None
    
    def get_match_data(self, obj):
        """Return simplified match analysis with just score, sizes, and warnings"""
        scan = self.context.get("scan")
        if scan:
            match_result = obj.match_with_scan(scan)
            # Simplify to just return score, recommended sizes, and warnings
            if match_result:
                simplified_sizes = [size_rec['size_value'] for size_rec in match_result.get('recommended_sizes', [])]
                
                return {
                    'score': match_result.get('score'),
                }
        return None
    
    
    def get_brand(self, obj):
        return obj.brand.name
    
    def get_colors(self, obj):
        return [color.hex_code for color in obj.colors.all()]

    def get_favourite(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return Favorite.objects.filter(user=request.user, products=obj).exists()
        return False

class ProductDetailsSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True)
    sizes = serializers.SerializerMethodField()  # Simplified
    colors = serializers.SerializerMethodField()
    match_data = serializers.SerializerMethodField()
    brand = BrandSerializer(read_only=True)
    favourite = serializers.SerializerMethodField()
    qna = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id", "name", "colors", "images", "technical_data", 'description',
            "brand", "sub_category", "sizes",
            "further_information", "price", "discount", 
            "stock_quantity", "partner", "match_data", 'favourite', 'gender', 'qna'
        ]
    
    def get_match_data(self, obj):
        """Return simplified match analysis with just score, sizes, and warnings"""
        scan = self.context.get("scan")
        if scan:
            match_result = obj.match_with_scan(scan)
            # Simplify to just return score, recommended sizes, and warnings
            if match_result:
                simplified_sizes = [size_rec['size_value'] for size_rec in match_result.get('recommended_sizes', [])]
                
                return {
                    'score': match_result.get('score'),
                    'recommended_sizes': simplified_sizes,
                }
        return None
    
    def get_sizes(self, obj):
        """Return simple list of available sizes"""
        sizes = []
        for size_table in obj.sizes.all():
            for size in size_table.sizes.all():
                if size.value not in sizes:  # Avoid duplicates
                    sizes.append(size.value)
        return sorted(sizes)  # Return sorted list
    
    def get_favourite(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return Favorite.objects.filter(user=request.user, products=obj).exists()
        return False
    def get_colors(self, obj):
        return [color.hex_code for color in obj.colors.all()]

    def get_qna(self, obj):
        qna_list = []
        for pq in ProductQuestionAnswer.objects.filter(product=obj).select_related('question').prefetch_related('answers'):
            qna_list.append({
                'question': pq.question.label,
                'answers': [ans.label for ans in pq.answers.all()]
            })
        return qna_list

class FootScanSerializer(serializers.ModelSerializer):
    width_category = serializers.SerializerMethodField()
    toe_box_category = serializers.SerializerMethodField()
    foot_type = serializers.SerializerMethodField()
    
    class Meta:
        model = FootScan
        fields = [
            "id", "user", "created_at",
            "left_length", "right_length",
            "left_width", "right_width",
            "left_arch_index", "right_arch_index",
            "left_heel_angle", "right_heel_angle",
            "width_category", "toe_box_category", "foot_type"
        ]
        read_only_fields = ["id", "created_at", 'user']
    
    def get_width_category(self, obj):
        return obj.get_width_label()
    
    def get_toe_box_category(self, obj):
        return obj.toe_box_category()
    
    def get_foot_type(self, obj):
        return obj.get_foot_type()
    
    def create(self, validated_data):
        user = self.context['request'].user
        if FootScan.objects.filter(user=user).exists():
            raise serializers.ValidationError("User already has a foot scan.")
        
        validated_data.pop('user', None)
        scan = FootScan.objects.create(user=user, **validated_data)
        return scan

class FavoriteSerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True, read_only=True)

    class Meta:
        model = Favorite
        fields = ['id', 'user', 'products']
        read_only_fields = ['user']