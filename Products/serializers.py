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
    sub_category = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'image', 'name', 'colors', 'gender', 'price', 
            'match_data', 'brand', 'favourite', 'sub_category'
        ]

    def get_sub_category(self, obj):
        try:
            return obj.sub_category.slug
        except SubCategory.DoesNotExist:
            return None

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
        if obj.brand:
            return {
                "name": obj.brand.name,
                "image": obj.brand.image.url if obj.brand.image else None  # assuming your Brand model has a 'logo' ImageField
            }
        return None
    
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
    sub_category = serializers.SerializerMethodField()
    favourite = serializers.SerializerMethodField()
    qna = serializers.SerializerMethodField()
    features = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id", "name", "colors", "images", "technical_data", 'description',
            "brand", "sub_category","features",
            "further_information", "price", "discount", 
             "match_data", 'favourite', 'gender','sizes', 'qna'
        ]

    def get_features(self, obj):
        try:
            features = obj.features.all()
            return [
                {
                    "title": f.title,
                    "details" : f.details,
                    "image": f.image.url if f.image else None
                }
                for f in features
            ]
        except Exception:
            return []
    
    
    def get_sub_category(self, obj):
        try:
            return obj.sub_category.slug
        except SubCategory.DoesNotExist:
            return None
            
    def get_match_data(self, obj):
        """Return simplified match analysis with just score, sizes, and warnings"""
        scan = self.context.get("scan")
        if scan:
            match_result = obj.match_with_scan(scan)
            if match_result:
                score_dict = {}

                size_scores = match_result.get('size_scores', [])

                for size_score in size_scores:
                    size_name = size_score.get('size', '')
                    score_value = size_score.get('score', 0)

                    # ✅ KEEP ORIGINAL FRACTIONS BUT EXTRACT SIZE PART
                    size_parts = size_name.split()
                    if len(size_parts) >= 2:
                        # Join all parts after the first one (to keep fractions intact)
                        size_key = ' '.join(size_parts[1:])
                    else:
                        size_key = size_name

                    score_dict[size_key] = f"{score_value}"

                return score_dict

        return {}
        
    def get_sizes(self, obj):
        sizes_list = []

        quantities = obj.quantities.select_related('size', 'size__brand').all()
        for q in quantities:
            # Get all size values from the related SizeTable
            size_values = list(q.size.sizes.values_list('value', flat=True))
            sizes_list.append({
                "size": size_values,
                "quantity": q.quantity
            })

        return sizes_list

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

class QnASerializer(serializers.ModelSerializer):
    question = serializers.CharField(source='question.label')
    answers = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='label'
    )

    class Meta:
        model = ProductQuestionAnswer
        fields = ['question', 'answers']

class PartnerProductSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    brand = serializers.SerializerMethodField()
    sub_category = serializers.SerializerMethodField()
    class Meta:
        model = PartnerProduct
        fields = ['id', 'price','stock_quantity', 'is_active', 'name', 'brand', 'sub_category']

    def get_name(self, obj):
        return obj.product.name
    def get_brand(self, obj):
        return obj.product.brand.name
    def get_sub_category(self, obj):
        return obj.product.sub_category.name
