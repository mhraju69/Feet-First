from rest_framework import serializers
from Brands.serializers import *
from .models import *
from Others.models import *

class ProductImageSerializer(serializers.ModelSerializer):
    color = serializers.CharField(source='color.color', read_only=True)
    hex_code = serializers.CharField(source='color.hex_code', read_only=True)
    class Meta:
        model = ProductImage
        fields = ['id','color','hex_code', 'image']

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
    sizes = serializers.SerializerMethodField()
    brand = serializers.SerializerMethodField()
    favourite = serializers.SerializerMethodField()
    sub_category = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'image', 'name', 'gender', 
            'match_data', 'sizes', 'brand', 'favourite', 'sub_category'
        ]

    def get_sub_category(self, obj):
        try:
            return obj.sub_category.slug
        except SubCategory.DoesNotExist:
            return None

    def get_image(self, obj):
        return ProductImageSerializer(obj.images.all(), many=True).data    
    
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
    
    def get_sizes(self, obj):
        sizes_list = []
        seen_sizes = set()

        for image in obj.images.all():
            for size_table in image.sizes.all():
                for size in size_table.sizes.all():
                    if size.id not in seen_sizes:
                        sizes_list.append({
                            "id": size.id,
                            "size": f"{size.type} {size.value}"
                        })
                        seen_sizes.add(size.id)
        return sizes_list
    
    def get_brand(self, obj):
        if obj.brand:
            return {
                "name": obj.brand.name,
                "image": obj.brand.image.url if obj.brand.image else None  # assuming your Brand model has a 'logo' ImageField
            }
        return None

    def get_favourite(self, obj):
        request = self.context.get("request")
        if not (request and request.user.is_authenticated):
            return False
            
        favorite_ids = self.context.get("favorite_ids")
        if favorite_ids is not None:
            return obj.id in favorite_ids
            
        return Favorite.objects.filter(user=request.user, products=obj).exists()

class ProductDetailsSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True)
    sizes = serializers.SerializerMethodField()  
    match_data = serializers.SerializerMethodField()
    brand = BrandSerializer(read_only=True)
    sub_category = serializers.SerializerMethodField()
    favourite = serializers.SerializerMethodField()
    qna = serializers.SerializerMethodField()
    features = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id", "name", "images", "technical_data", 'description',
            "brand", "sub_category","features",
            "further_information", 
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
        seen_tables = set()

        # Use sizes from related ProductImage
        for image in obj.images.all():
            for size_table in image.sizes.select_related('brand').all():
                if size_table.id not in seen_tables:
                    # Get all size values from the related SizeTable
                    size_values = list(size_table.sizes.values_list('value', flat=True))
                    sizes_list.append({
                        "size": size_values,
                        "table_name": size_table.name
                    })
                    seen_tables.add(size_table.id)

        return sizes_list

    def get_favourite(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return Favorite.objects.filter(user=request.user, products__product=obj).exists()
        return False

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

class PartnerProductSizeSerializer(serializers.ModelSerializer):
    """Serializer for size with quantity"""
    size = serializers.SerializerMethodField()
    # Return the PartnerProductSize ID as 'size_id' so the frontend uses the correct ID for ordering
    size_id = serializers.IntegerField(source='id') 
    color = serializers.SerializerMethodField()
    
    class Meta:
        model = PartnerProductSize
        fields = ['size_id', 'size', 'quantity', 'color']
    
    def get_color(self, obj):
        return obj.partner_product.color.color if obj.partner_product.color else "N/A"
    
    def get_size(self, obj):
        return obj.size.value

class PartnerProductSerializer(serializers.ModelSerializer):
    """Serializer for partner's dashboard/inventory management"""
    brand = serializers.CharField(source='product.brand.name', read_only=True)
    name = serializers.CharField(source='product.name', read_only=True)
    stock_status = serializers.SerializerMethodField()
    color = serializers.SerializerMethodField()
    size_data = serializers.SerializerMethodField()
    warehouse = serializers.SerializerMethodField()

    class Meta:
        model = PartnerProduct
        fields = [
            'id', 'brand', 'name', 'color','eanc', 'stock_status', 'price','buy_price',
            'local', 'online', 'size_data','warehouse'
        ]
    
    def get_warehouse(self, obj):
        warehouse = obj.warehouse.first()
        if not warehouse:
            return None
        return {
            "id": warehouse.id,
            "name": warehouse.name
        }
    
    def get_stock_status(self, obj):
        return "In Stock" if obj.total_stock_quantity > 0 else "Out of Stock"

    def get_color(self, obj):
        colors_list = []
        color = obj.color
        if color:
            relevant_img = obj.product.images.filter(color=color).first()
            colors_list.append({
                "id": color.id,
                "name": color.color,
                "hex": color.hex_code,
                "image": relevant_img.image.url if relevant_img and relevant_img.image else None,
                "variant_id": obj.id
            })
        return colors_list
        

    def get_size_data(self, obj):
        # Groups sizes by type for THIS specific variant
        data = {}
        for pps in obj.size_quantities.select_related('size').all():
            s_type = pps.size.type
            if s_type in ['USM', 'USW']:
                s_type = 'US'
            
            if s_type not in data:
                data[s_type] = []
            
            size_val = pps.size.value
            try:
                num_val = float(size_val)
                if num_val.is_integer():
                    size_val = int(num_val)
                else:
                    size_val = num_val
            except (ValueError, TypeError):
                pass

            data[s_type].append({
                "id": pps.id,
                "size": size_val,
                "quantity": pps.quantity
            })
        return data

    def get_stock_status(self, obj):
        return "In Stock" if obj.total_stock_quantity > 0 else "Out of Stock"

class PartnerProductListSerializer(serializers.ModelSerializer):
    """Serializer for customer-facing product listings (multi-vendor system)"""
    id = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    brand = serializers.SerializerMethodField()
    match_data = serializers.SerializerMethodField()
    favourite = serializers.SerializerMethodField()
    sub_category = serializers.SerializerMethodField()
    name = serializers.CharField(source='product.name')
    gender = serializers.CharField(source='product.gender')
    color = serializers.SerializerMethodField()

    
    class Meta:
        model = PartnerProduct
        fields = [
            'id', 'image', 'name', 'gender', 'price', 
            'match_data', 'brand', 'sub_category', 'favourite', 'color'
        ]

    def get_color(self, obj):
        # Global view: show color NAMES from ALL active partners for this product
        return list(PartnerProduct.objects.filter(
            product=obj.product, 
            is_active=True,
            online=True
        ).values_list('color__color', flat=True).distinct())
    
    def get_id(self, obj):
        # Return main Product ID instead of PartnerProduct ID
        return obj.product.id
    
    def get_price(self, obj):
        # Global view: show the minimum price available for this product
        min_price = PartnerProduct.objects.filter(
            product=obj.product,
            is_active=True,
            online=True
        ).aggregate(models.Min('price'))['price__min']
        return min_price or obj.price
    
    def get_sub_category(self, obj):
        try:
            return obj.product.sub_category.slug
        except:
            return None
    
    def get_image(self, obj):
        # Use primary image of the product
        primary = obj.product.images.first()
        if primary:
            return ProductImageSerializer(primary).data
        return None
    
    def get_brand(self, obj):
        if obj.product.brand:
            return {
                "name": obj.product.brand.name,
                "image": obj.product.brand.image.url if obj.product.brand.image else None
            }
        return None
    
    def get_match_data(self, obj):
        """Return match analysis based on foot scan"""
        scan = self.context.get("scan")
        if scan:
            match_result = obj.product.match_with_scan(scan)
            if match_result:
                return {
                    'score': match_result.get('score'),
                }
        return None
    
    def get_favourite(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return False

        favorite_ids = self.context.get("favorite_ids")
        if favorite_ids is not None:
            return obj.product.id in favorite_ids
            
        return Favorite.objects.filter(user=request.user, products=obj.product).exists()

class PartnerProductDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed product view in multi-vendor system"""
    id = serializers.SerializerMethodField()
    colors = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
    sizes = serializers.SerializerMethodField()
    match_data = serializers.SerializerMethodField()
    brand = BrandSerializer(source='product.brand', read_only=True)
    sub_category = serializers.SerializerMethodField()
    favourite = serializers.SerializerMethodField()
    qna = serializers.SerializerMethodField()
    features = serializers.SerializerMethodField()
    name = serializers.CharField(source='product.name')
    description = serializers.CharField(source='product.description')
    technical_data = serializers.CharField(source='product.technical_data')
    further_information = serializers.CharField(source='product.further_information')
    gender = serializers.CharField(source='product.gender')
    quantity = serializers.SerializerMethodField()
    
    class Meta:
        model = PartnerProduct
        fields = [
            "id", "name", "colors", "images", "technical_data", 'description',
            "brand", "sub_category", "features",
            "further_information", "price", 
            "match_data", 'favourite', 'gender', 'sizes','quantity','qna'
        ]
    
    def get_id(self, obj):
        # Return main Product ID
        return obj.product.id

    def get_colors(self, obj):
        # Return list of color names available globally for this product
        return list(PartnerProduct.objects.filter(
            product=obj.product,
            is_active=True,
            online=True
        ).values_list('color__color', flat=True).distinct())
    
    def get_images(self, obj):
        # Get images for all colors available globally for this product that are ONLINE
        active_color_ids = PartnerProduct.objects.filter(
            product=obj.product, 
            is_active=True,
            online=True
        ).values_list('color_id', flat=True)
        
        images = ProductImage.objects.filter(product=obj.product, color_id__in=active_color_ids)
        return ProductImageSerializer(images, many=True).data
    
    def get_sub_category(self, obj):
        try:
            return obj.product.sub_category.slug
        except:
            return None
    
    def get_features(self, obj):
        try:
            features = obj.product.features.all()
            return [
                {
                    "title": f.title,
                    "details": f.details,
                    "image": f.image.url if f.image else None
                }
                for f in features
            ]
        except:
            return []
    
    def get_price(self, obj):
        # Global view: show the minimum price available for this product
        min_price = PartnerProduct.objects.filter(
            product=obj.product,
            is_active=True,
            online=True
        ).aggregate(models.Min('price'))['price__min']
        return min_price or obj.price

    def get_sizes(self, obj):
        """Return sizes grouped by color variant for this product"""
        # Get all online variants for this product
        active_variants = PartnerProduct.objects.filter(
            product=obj.product, 
            is_active=True,
            online=True
        ).select_related('color').prefetch_related('size_quantities__size')
        
        results = []
        for variant in active_variants:
            sizes = variant.size_quantities.all()
            if sizes:
                results.append({
                    "color": variant.color.color,
                    "hex_code": variant.color.hex_code,
                    "variant_id": variant.id, 
                    "sizes": PartnerProductSizeSerializer(sizes, many=True).data
                })
        return results
    
    def get_quantity(self, obj):
        """Return total stock quantity across all partners"""
        # Calculate sum of stock from all active variants
        # Join with PartnerProductSize to sum quantity field
        return PartnerProductSize.objects.filter(
            partner_product__product=obj.product,
            partner_product__is_active=True,
            partner_product__online=True
        ).aggregate(total=models.Sum('quantity'))['total'] or 0
    
    def get_match_data(self, obj):
        """Return detailed match analysis"""
        scan = self.context.get("scan")
        if scan:
            match_result = obj.product.match_with_scan(scan)
            if match_result:
                score_dict = {}
                size_scores = match_result.get('size_scores', [])
                for size_score in size_scores:
                    size_name = size_score.get('size', '')
                    score_value = size_score.get('score', 0)
                    size_parts = size_name.split()
                    if len(size_parts) >= 2:
                        size_key = ' '.join(size_parts[1:])
                    else:
                        size_key = size_name
                    score_dict[size_key] = f"{score_value}"
                return score_dict
        return {}
    
    def get_favourite(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return False

        favorite_ids = self.context.get("favorite_ids")
        if favorite_ids is not None:
            return obj.product.id in favorite_ids
            
        return Favorite.objects.filter(user=request.user, products=obj.product).exists()
    
    def get_qna(self, obj):
        qna_list = []
        for pq in ProductQuestionAnswer.objects.filter(product=obj.product).select_related('question').prefetch_related('answers'):
            qna_list.append({
                'question': pq.question.label,
                'answers': [ans.label for ans in pq.answers.all()]
            })
        return qna_list

class FavoriteSerializer(serializers.ModelSerializer):
    products = serializers.SerializerMethodField()

    class Meta:
        model = Favorite
        fields = ['id', 'user', 'products']
        read_only_fields = ['user']

    def get_products(self, obj):
        from django.db.models import OuterRef, Subquery
        # result list of PartnerProducts
        product_ids = obj.products.filter(is_active=True).values_list('id', flat=True)

        # Find the best active variant for each favorited product in one query
        best_variant_sq = PartnerProduct.objects.filter(
            product=OuterRef('product'),
            is_active=True,
            online=True
        ).order_by('price', 'id').values('id')[:1]

        partner_products = PartnerProduct.objects.filter(
            product_id__in=product_ids,
            id=Subquery(best_variant_sq)
        ).select_related(
            'product', 'product__brand', 'product__sub_category'
        ).prefetch_related('product__images')

        return PartnerProductListSerializer(partner_products, many=True, context=self.context).data