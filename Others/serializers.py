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
    
    class Meta:
        model = Order
        fields = ("order_id", "customer","product", "status", "price", "tracking", "created_at","details")

    def get_customer(self, obj):
        return (obj.user.name if obj.user.name else obj.user.email)

    def get_details(self, obj):
        address = Address.objects.filter(user=obj.user).first()
        size_display = str(obj.size.size) if obj.size else "N/A"
        return {
            "color" : obj.color,
            "size" : size_display,
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