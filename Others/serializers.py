# serializers.py
from rest_framework import serializers
from .models import *
from Accounts.serializers import AddressSerializer
from django.db.models import Sum

class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = ("question_de", "question_it", "answer_de", "answer_it")

class NewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = ("title_de", "title_it", "image", "content_de", "content_it", "created_at")

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ("user", "amount", "created_at")

class OrderSerializer(serializers.ModelSerializer):
    customer = serializers.SerializerMethodField()
    product = serializers.CharField(source="product.name", read_only=True)
    price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    details = serializers.SerializerMethodField()
    partner_product_id = serializers.SerializerMethodField()
    sub_category = serializers.CharField(source="product.sub_category.slug", read_only=True)
    match_data = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ("id","order_id", "customer","product", "partner_product_id", "status", "price", "net_amount", "tracking", "created_at","details","match_data","sub_category")
        read_only_fields = ("id","order_id", "customer", "product", "price", "net_amount", "created_at", "details", "match_data", "sub_category")

    def get_customer(self, obj):
        return (obj.user.name if obj.user.name else obj.user.email)

    def get_partner_product_id(self, obj):
        user = obj.partner
        partner_product = PartnerProduct.objects.filter(partner=user,product=obj.product).first()
        return partner_product.id if partner_product else None

    def get_match_data(self, obj):
        """Return match score for ONLY the ordered size"""
        scan = self.context.get("scan")
        if not scan and hasattr(obj, 'user'):
            from .models import FootScan
            scan = FootScan.objects.filter(user=obj.user).first()

        if scan and obj.size and obj.product:
            match_result = obj.product.match_with_scan(scan)
            if match_result:
                size_label = str(obj.size.size)
                # Find the score for this specific ordered size
                size_scores = match_result.get('size_scores', [])
                ordered_size_score = next(
                    (item['score'] for item in size_scores if item['size'] == size_label),
                    None
                )
                return {
                    'score': ordered_size_score,
                }
        return None

    def get_details(self, obj):
        address = Address.objects.filter(user=obj.user).first()
        return {
            "color" : obj.color,
            "image" : obj.product.images.first().image.url,
            "size" : str(obj.size.size),
            "size_id" : obj.size_id,
            "quantity" : obj.quantity,
            "address" : AddressSerializer(address).data,
        }

class WarehouseSerializer(serializers.ModelSerializer):
    stock = serializers.SerializerMethodField()
    item = serializers.SerializerMethodField()

    class Meta:
        model = Warehouse
        fields = ("id","name", "address", "stock", "item", "created_at", "updated_at", "partner")
        read_only_fields = ("stock", "item", "partner")

    def get_stock(self, obj):
        partner_products = obj.product.all()

        total_stock = (
            PartnerProductSize.objects
            .filter(partner_product__in=partner_products)
            .aggregate(total=Sum("quantity"))
            .get("total")
        )

        return total_stock or 0

    def get_item(self, obj):
        return obj.product.count()

class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='partner_product.product.name', read_only=True)
    product_image = serializers.SerializerMethodField()
    price = serializers.DecimalField(source='partner_product.price', max_digits=12, decimal_places=2, read_only=True)
    size_label = serializers.CharField(source='size.size.value', read_only=True)
    size_type = serializers.CharField(source='size.size.type', read_only=True)
    partner_product_id = serializers.IntegerField(source='partner_product.id', read_only=True)
    size_id = serializers.IntegerField(source='size.id', read_only=True)
    
    class Meta:
        model = CartItem
        fields = ['id', 'partner_product_id', 'product_name', 'product_image', 'size_id', 'size_label', 'size_type', 'color', 'quantity', 'price', 'total_price']

    def get_product_image(self, obj):
        # Try to find image matching the color
        # This is a best effort, assumes Color name matches or similar mapping if needed. 
        # But for now just get first image or simple match if possible
        images = obj.partner_product.product.images.all()
        # If we had Color link in CartItem matching Image Color
        # But CartItem.color is CharField. 
        if images.exists():
            return images.first().image.url
        return None

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    count = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'items', 'total_price','count', 'updated_at']

    def get_count(self, obj):
        return obj.items.aggregate(total=Sum('quantity')).get('total')

class AccessoriesSerializer(serializers.ModelSerializer):
    brand = serializers.CharField(source='brand.name', read_only=True)
    warehouse = serializers.CharField(source='warehouse.name', read_only=True)
    status = serializers.SerializerMethodField()
    class Meta:
        model = Accessories
        fields = "__all__"
    
    def get_status(self, obj):
        return "In Stock" if obj.stock > 0 else "Out of Stock"