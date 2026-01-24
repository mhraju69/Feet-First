# views.py
from rest_framework import generics, permissions, views, status
from rest_framework.response import Response
from django.db.models import Sum, F, DecimalField, Case, When, Q
from django.db.models.functions import ExtractMonth, ExtractYear
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
from .models import *
from .serializers import *
from core.permission import *
from Products.views import CustomLimitPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from Products.models import PartnerProduct, PartnerProductSize
from Accounts.models import Address
from .helper import *
import stripe
import ast

class FAQAPIView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]  
    queryset = FAQ.objects.all()
    serializer_class = FAQSerializer


class NewsAPIView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]  
    queryset = News.objects.all()
    serializer_class = NewsSerializer


class DashboardAPIView(views.APIView):
    permission_classes = [permissions.IsAuthenticated,IsPartner] 

    @staticmethod
    def monthly_sales(partner):

        now = timezone.now()
        
        current_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        current_month_end = now
        
        last_month_end = current_month_start - timedelta(days=1)
        last_month_start = last_month_end.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        current_month_payments = Payment.objects.filter(
            payment_to=partner,
            transaction_id__isnull=False,
            created_at__gte=current_month_start,
            created_at__lte=current_month_end
        ).aggregate(
            total_sales=Sum('net_amount')
        )
        
        current_month_sales = current_month_payments['total_sales'] or Decimal('0.00')
        
        last_month_payments = Payment.objects.filter(
            payment_to=partner,
            transaction_id__isnull=False,
            created_at__gte=last_month_start,
            created_at__lte=last_month_end
        ).aggregate(
            total_sales=Sum('net_amount')
        )
        
        last_month_sales = last_month_payments['total_sales'] or Decimal('0.00')
        
        difference = current_month_sales - last_month_sales
        
        if last_month_sales > 0:
            percentage_change = (difference / last_month_sales) * 100
            percentage_change = max(-100, min(100, percentage_change))
        else:
            percentage_change = 100 if current_month_sales > 0 else 0
        
        return {
            'current_month_sales': float(current_month_sales),
            'last_month_sales': float(last_month_sales),
            'percentage_change': round(float(percentage_change), 2),
        }

    def weekly_orders(self):
        
        now = timezone.now()
        
        # Current week date range (Monday to Sunday)
        current_week_start = now - timedelta(days=now.weekday())
        current_week_start = current_week_start.replace(hour=0, minute=0, second=0, microsecond=0)
        current_week_end = now
        
        # Last week date range
        last_week_end = current_week_start - timedelta(days=1)
        last_week_start = last_week_end - timedelta(days=6)
        last_week_start = last_week_start.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Count current week orders
        current_week_count = Order.objects.filter(
            created_at__gte=current_week_start,
            created_at__lte=current_week_end
        ).exclude(status='pending').count()
        
        # Count last week orders
        last_week_count = Order.objects.filter(
            created_at__gte=last_week_start,
            created_at__lte=last_week_end
        ).exclude(status='pending').count()
        
        # Calculate difference
        difference = current_week_count - last_week_count
        
        # Calculate percentage change (clamped between -100 and 100)
        if last_week_count > 0:
            percentage_change = (difference / last_week_count) * 100
            percentage_change = max(-100, min(100, percentage_change))
        else:
            percentage_change = 100 if current_week_count > 0 else 0
        
        return {
            'current_week_orders': current_week_count,
            'percentage_change': round(float(percentage_change), 2),
        }

    def partner_products(self, partner):
        
        # Get total products added by this partner
        total_products = PartnerProduct.objects.filter(partner=partner).count()
        
        # Get active products for this partner
        active_products = PartnerProduct.objects.filter(
            partner=partner,
            is_active=True
        ).count()
        
        return {
            'total_products': total_products,
            'active_products': active_products,
        }

    def low_stock_products(self, partner):
        
        LOW_STOCK_THRESHOLD = 10
        
        # Get all partner products with their total stock
        partner_products = PartnerProduct.objects.filter(
            partner=partner,
            is_active=True
        ).select_related('product', 'product__brand').prefetch_related('size_quantities')
        
        low_stock_list = []
        for pp in partner_products:
            total_stock = pp.total_stock_quantity
            if total_stock <= LOW_STOCK_THRESHOLD:
                low_stock_list.append({
                    'partner_product_id': pp.id,
                    'product_id': pp.product.id,
                    'product_name': pp.product.name,
                    'brand': pp.product.brand.name,
                    'stock_quantity': total_stock
                })
        
        return low_stock_list[:20]

    def recent_orders(self, request,*args,**kwargs):
        
        limit = kwargs.get('limit', 100)
        status_filter = kwargs.get('status', None)
        
        try:
            limit = int(limit)
            if limit <= 0:
                limit = 100
            if limit > 500:
                limit = 500
        except (ValueError, TypeError):
            limit = 100
        
        orders_query = Order.objects.all()
        
        if status_filter and status_filter in ['pending', 'confirmed', 'shipped', 'delivered']:
            orders_query = orders_query.filter(status=status_filter)
        
        orders = orders_query.select_related(
            'user', 'product', 'product__brand'
        ).order_by('-created_at')[:limit].values(
            'id',
            'order_id',
            'name',
            'product__name',
            'status'
        )
        
        orders_list = [
            {
                'id': order['id'],
                'order_id': order['order_id'],
                'customer_name': order['name'],
                'product_name': order['product__name'],
                'status': order['status']
            }
            for order in orders
        ]
        
        return orders_list

    def get_best_selling_low_stock_alerts(self, partner):
        now = timezone.now()
        current_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        current_month_end = now
        
        last_month_end = current_month_start - timedelta(days=1)
        last_month_start = last_month_end.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        best_sellers = Order.objects.filter(
            created_at__gte=last_month_start,
            created_at__lte=current_month_end
        ).exclude(status='pending').values(
            'product__id',
            'product__name'
        ).annotate(
            total_sold=Sum('quantity')
        ).order_by('-total_sold')[:10]  
        
        best_seller_product_ids = [item['product__id'] for item in best_sellers]
        
        LOW_STOCK_THRESHOLD = 20
        
        partner_products_best = PartnerProduct.objects.filter(
            partner=partner,
            product__id__in=best_seller_product_ids,
            is_active=True
        ).select_related('product', 'product__brand').prefetch_related('size_quantities')
        
        user_language = partner.language if hasattr(partner, 'language') else 'german'
        
        alerts = []
        for pp in partner_products_best:
            total_stock = pp.total_stock_quantity
            if total_stock < LOW_STOCK_THRESHOLD:
                product_name = pp.product.name
                brand_name = pp.product.brand.name if pp.product.brand else ''
                
                full_product_name = f"{brand_name} {product_name}" if brand_name else product_name
                
                if user_language == 'italian':
                    message = f"Il modello ha una forte richiesta e scorte ridotte. Riordino consigliato: 15–20 paia."
                else: 
                    message = f"Das Modell hat eine hohe Nachfrage und niedrige Bestände. Empfohlene Nachbestellung: 15-20 Paar."
                
                alerts.append({
                    'partner_product_id': pp.id,
                    'product_id': pp.product.id,
                    'product_name': full_product_name,
                    'current_stock': total_stock,
                    'message': message
                })
        return alerts

    def get_inactive_product_alerts(self, partner):
        from django.db.models import Count
        from collections import defaultdict
        
        user_language = partner.language if hasattr(partner, 'language') else 'german'
        
        inactive_products = PartnerProduct.objects.filter(
            partner=partner,
            is_active=False
        ).select_related(
            'product',
            'product__brand',
            'product__sub_category'
        ).prefetch_related('size_quantities')
        
        inactive_with_stock = [pp for pp in inactive_products if pp.total_stock_quantity > 0]
        
        grouped = defaultdict(int)
        for pp in inactive_with_stock:
            key = (pp.product.brand.name if pp.product.brand else 'Unknown Brand',
                   pp.product.sub_category.name if pp.product.sub_category else 'Unknown Category')
            grouped[key] += 1
        
        sorted_groups = sorted(grouped.items(), key=lambda x: -x[1])
        
        inactive_alerts = []
        for (brand_name, subcategory_name), count in sorted_groups:
            if user_language == 'italian':
                message = f"Avete {count} modelli di {subcategory_name} in magazzino che non sono ancora attivati nel Shoe Finder."
            else:
                message = f"Sie haben {count} {subcategory_name}-Modelle im Lager, die noch nicht im Shoe Finder aktiviert sind."
            
            inactive_alerts.append({
                'brand': brand_name,
                'subcategory': subcategory_name,
                'count': count,
                'message': message
            })
        return inactive_alerts

    def get_seasonal_recommendations(self, partner):
        import random
        now = timezone.now()
        month = now.month
        user_language = partner.language if hasattr(partner, 'language') else 'german'
        
        seasonal_recommendations = {
            'spring': {
                'months': [3, 4, 5],
                'subcategories': ['Laufschuh', 'Trailschuh', 'Wanderschuh', 'Freizeitschuh'],
                'title_de': 'Frühlings-Trend nutzen',
                'title_it': 'Sfrutta il trend primaverile',
                'message_de': 'Laufschuhe und Outdoor-Modelle zeigen steigendes Interesse. Erwägen Sie zusätzliche Marketingaktionen.',
                'message_it': 'Le scarpe da corsa e i modelli outdoor mostrano un crescente interesse. Considerate azioni di marketing aggiuntive.'
            },
            'summer': {
                'months': [6, 7, 8],
                'subcategories': ['Laufschuh', 'Trailschuh', 'Barfußschuh', 'Sandale', 'Freizeitschuh'],
                'title_de': 'Sommer-Trend nutzen',
                'title_it': 'Sfrutta il trend estivo',
                'message_de': 'Sneaker und leichte Sportschuhe zeigen steigendes Interesse. Erwägen Sie zusätzliche Marketingaktionen.',
                'message_it': 'Sneaker e scarpe sportive leggere mostrano un crescente interesse. Considerate azioni di marketing aggiuntive.'
            },
            'fall': {
                'months': [9, 10, 11],
                'subcategories': ['Wanderschuh', 'Trailschuh', 'Laufschuh', 'Winterschuh'],
                'title_de': 'Herbst-Trend nutzen',
                'title_it': 'Sfrutta il trend autunnale',
                'message_de': 'Wanderschuhe und robuste Outdoor-Modelle zeigen steigendes Interesse. Erwägen Sie zusätzliche Marketingaktionen.',
                'message_it': 'Scarpe da trekking e modelli outdoor robusti mostrano un crescente interesse. Considerate azioni di marketing aggiuntive.'
            },
            'winter': {
                'months': [12, 1, 2],
                'subcategories': ['Winterschuh', 'Wanderschuh', 'Freizeitschuh'],
                'title_de': 'Winter-Trend nutzen',
                'title_it': 'Sfrutta il trend invernale',
                'message_de': 'Winterschuhe und wärmende Modelle zeigen steigendes Interesse. Erwägen Sie zusätzliche Marketingaktionen.',
                'message_it': 'Scarpe invernali e modelli caldi mostrano un crescente interesse. Considerate azioni di marketing aggiuntive.'
            }
        }
        
        current_season = None
        for season, data in seasonal_recommendations.items():
            if month in data['months']:
                current_season = data
                break
        
        marketing_recommendations = []
        if current_season:
            partner_products_seasonal = PartnerProduct.objects.filter(
                partner=partner,
                is_active=True,
                product__sub_category__name__in=current_season['subcategories']
            ).select_related('product__sub_category').prefetch_related('size_quantities')
            
            partner_subcategories = set()
            for pp in partner_products_seasonal:
                if pp.total_stock_quantity > 0:
                    partner_subcategories.add(pp.product.sub_category.name)
            
            available_subcategories = list(partner_subcategories)
            
            if available_subcategories:
                selected_subcategory = random.choice(available_subcategories)
                
                if user_language == 'italian':
                    title = current_season['title_it']
                    message = current_season['message_it']
                else:
                    title = current_season['title_de']
                    message = current_season['message_de']
                
                marketing_recommendations.append({
                    'title': title,
                    'subcategory': selected_subcategory,
                    'message': message,
                    'season': list(seasonal_recommendations.keys())[list(seasonal_recommendations.values()).index(current_season)]
                })
        return marketing_recommendations

    def get(self, request):
        partner = request.user
        return Response({
            'monthly_sales': self.monthly_sales(partner),
            'weekly_orders': self.weekly_orders(),
            'partner_products': self.partner_products(partner),
            'low_stock_products': self.low_stock_products(partner),
            'recent_orders': self.recent_orders(partner),
            'best_selling_low_stock': self.get_best_selling_low_stock_alerts(request.user),
            'inactive_product': self.get_inactive_product_alerts(request.user),
            'seasonal_marketing': self.get_seasonal_recommendations(partner)
        })


class OrderPageAPIView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated,IsPartner] 
    serializer_class = OrderSerializer
    pagination_class = CustomLimitPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['status']
    search_fields = ['order_id', 'name', 'product__name','product__brand__name','product__sub_category__name']

    def get_queryset(self):
        return Order.objects.filter(partner=self.request.user).select_related('user', 'product').order_by('-created_at')


class OrderAnalyticsAPIView(views.APIView):
    permission_classes = [permissions.IsAuthenticated,IsPartner]
    def get(self, request):
        new = Order.objects.filter(partner=self.request.user,status='confirmed').count()
        packaging = Order.objects.filter(partner=self.request.user,status='packaging').count()
        shipping = Order.objects.filter(partner=self.request.user,status='shipped').count()
        return Response({
            'new': new,
            'packaging': packaging,
            'shipping': shipping,
        })


class WarehouseAPIView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated,IsPartner] 
    serializer_class = WarehouseSerializer

    def get_queryset(self):
        return Warehouse.objects.filter(partner=self.request.user).select_related('partner').order_by('-created_at')
    
    def perform_create(self, serializer):
        serializer.save(partner=self.request.user)


class WarehouseUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated,IsPartner] 
    serializer_class = WarehouseSerializer

    def get_object(self):
        return Warehouse.objects.get(id=self.kwargs['pk'])


class CartAPIView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        cart, created = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        # Payload: { "product": 16, "size_id": 25, "color": "black", "quantity": 1 }
        product_id = request.data.get('product')
        size_id = request.data.get('size_id')
        color = request.data.get('color')
        quantity = request.data.get('quantity', 1)

        if not all([product_id, size_id, color]):
            return Response({"error": "product, size_id, and color are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            quantity = int(quantity)
            if quantity <= 0:
                raise ValueError
        except ValueError:
            return Response({"error": "Quantity must be a positive integer."}, status=status.HTTP_400_BAD_REQUEST)

        # distinct partner product check
        try:
            partner_product = PartnerProduct.objects.get(id=product_id) # The user passed "product" but context suggests partner product ID
        except PartnerProduct.DoesNotExist:
            # Fallback: maybe they passed raw product ID?
            # But we need PartnerProduct to know price and partner.
            # Start with strict check.
            return Response({"error": "Invalid Partner Product ID."}, status=status.HTTP_404_NOT_FOUND)

        try:
            partner_product_size = PartnerProductSize.objects.get(id=size_id, partner_product=partner_product)
        except PartnerProductSize.DoesNotExist:
             return Response({"error": "Invalid Size ID for this product."}, status=status.HTTP_404_NOT_FOUND)

        # Check stock
        if partner_product_size.quantity < quantity:
             return Response({"error": f"Insufficient stock. Available: {partner_product_size.quantity}"}, status=status.HTTP_400_BAD_REQUEST)

        cart, _ = Cart.objects.get_or_create(user=request.user)

        # Update or Create Item
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            partner_product=partner_product,
            size=partner_product_size,
            color=color,
            defaults={'quantity': 0} 
        )

        # If existing, add quantity
        new_quantity = cart_item.quantity + quantity
        
        # Check overall stock again
        if partner_product_size.quantity < new_quantity:
             return Response({"error": f"Insufficient stock. You already have {cart_item.quantity}, cannot add {quantity} more. Available: {partner_product_size.quantity}"}, status=status.HTTP_400_BAD_REQUEST)

        cart_item.quantity = new_quantity
        cart_item.save()

        return Response({"message": "Item added to cart", "cart": CartSerializer(cart).data}, status=status.HTTP_200_OK)


class CartItemUpdateDeleteView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk, *args, **kwargs):
        # Update quantity
        try:
            cart_item = CartItem.objects.get(pk=pk, cart__user=request.user)
        except CartItem.DoesNotExist:
             return Response({"error": "Cart Item not found."}, status=status.HTTP_404_NOT_FOUND)

        quantity = request.data.get('quantity')
        if quantity is None:
             return Response({"error": "quantity is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            quantity = int(quantity)
            if quantity < 0:
                 raise ValueError
        except ValueError:
             return Response({"error": "Quantity must be a non-negative integer."}, status=status.HTTP_400_BAD_REQUEST)

        if quantity == 0:
            cart_item.delete()
            return Response({"message": "Item removed from cart"}, status=status.HTTP_200_OK)

        # Check stock
        if cart_item.size.quantity < quantity:
             return Response({"error": f"Insufficient stock. Available: {cart_item.size.quantity}"}, status=status.HTTP_400_BAD_REQUEST)

        cart_item.quantity = quantity
        cart_item.save()
        
        return Response({"message": "Cart updated", "cart": CartSerializer(cart_item.cart).data}, status=status.HTTP_200_OK)

    def delete(self, request, pk, *args, **kwargs):
        try:
            cart_item = CartItem.objects.get(pk=pk, cart__user=request.user)
            cart = cart_item.cart
            cart_item.delete()
            return Response({"message": "Item removed from cart", "cart": CartSerializer(cart).data}, status=status.HTTP_200_OK)
        except CartItem.DoesNotExist:
             return Response({"error": "Cart Item not found."}, status=status.HTTP_404_NOT_FOUND)


class UpdateOrderView(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated, IsPartner]
    serializer_class = OrderSerializer
    queryset = Order.objects.all()

    def get_queryset(self):
        return Order.objects.filter(partner=self.request.user)


class CreateOrderView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        # Pull products from user's cart instead of request data
        try:
            cart = Cart.objects.get(user=request.user)
            cart_items = CartItem.objects.filter(cart=cart).select_related('partner_product', 'partner_product__partner', 'partner_product__product', 'size', 'size__size')
        except Cart.DoesNotExist:
            return Response({"error": "Your cart is empty"}, status=status.HTTP_400_BAD_REQUEST)

        if not cart_items.exists():
             return Response({"error": "Your cart is empty"}, status=status.HTTP_400_BAD_REQUEST)

        validated_items = []
        total_amount = Decimal('0.00')
        
        try:
            address = Address.objects.filter(user=request.user).first()
            if not address:
                return Response({"error": "Please complete your address first."}, status=status.HTTP_400_BAD_REQUEST)
            # Validate required fields as per user request
            required_fields = {
                'first_name': address.first_name,
                'last_name': address.last_name,
                'street_address': address.street_address,
                'address_line2': address.address_line2,
                'postal_code': address.postal_code,
                'city': address.city,
                'phone_number': address.phone_number,
                'country': address.country
            }
            
            missing_or_empty = [field for field, value in required_fields.items() if not value or str(value).strip() == '']
            
            if missing_or_empty:
                return Response({
                    "error": f"Please complete your address. Missing fields: {', '.join(missing_or_empty)}"
                }, status=status.HTTP_400_BAD_REQUEST)

        except Address.DoesNotExist:
             return Response({"error": "Invalid Address ID"}, status=status.HTTP_400_BAD_REQUEST)

        # Phase 1: Validate ALL items from cart
        customer_name = request.user.name if hasattr(request.user, 'name') and request.user.name else request.user.email

        for index, item in enumerate(cart_items):
            try:
                partner_product = item.partner_product
                quantity = item.quantity
                partner_product_size = item.size
                color = item.color
                partner = partner_product.partner
                product = partner_product.product
                
                # Check Stock Availability
                if partner_product_size.quantity < quantity:
                    return Response({
                        "error": f"Insufficient stock for '{product.name}' size {partner_product_size.size}. Available: {partner_product_size.quantity}"
                    }, status=status.HTTP_400_BAD_REQUEST)

                # Prepare Validated Item
                validated_items.append({
                    'user': request.user,
                    'partner': partner,
                    'product': product,
                    'price': partner_product.price,
                    'partner_product': partner_product,
                    'quantity': quantity,
                    'size': partner_product_size,
                    'color': color,
                    'name': customer_name
                })
                
                total_amount += (partner_product.price * quantity)

            except Exception as e:
                return Response({"error": f"Validation error for item {index+1}: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


        # Phase 2: Create Orders
        created_ids = []
        payments_ids = []
        try:
            for v_item in validated_items:
                order = Order.objects.create(
                    user=v_item['user'],
                    partner=v_item['partner'],
                    product=v_item['product'],
                    price=v_item['price'],
                    quantity=v_item['quantity'],
                    size=v_item['size'],
                    color=v_item['color'],
                    status='pending',
                    name=v_item['name']
                )
                created_ids.append(order.id)
                # Note: Stock is NOT deducted here. Stock usually deducted after payment confirmation.
                payment = Payment.objects.create(
                    order=order,
                    payment_from=request.user,
                    payment_to=order.partner,
                    product=v_item['partner_product'], # I should make sure this is in v_item
                    quantity=order.quantity,
                    amount=order.price * order.quantity,
                    created_at=timezone.now()
                )
                payments_ids.append(payment.id)
                
        except Exception as e:
             return Response({"error": f"Failed to create orders: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # checkout_session_url = create_checkout_session(request, created_ids, payments_ids, total_amount)
        intent = create_payment_intent_data(request, created_ids, payments_ids, total_amount, customer_email=request.user.email)
        
        # Clear cart after order is created and payment is initiated
        # cart_items.delete()

        return Response({
            "message": "Orders created successfully", 
            # "checkout_session_url": checkout_session_url,
            "intent": intent
        }, status=status.HTTP_201_CREATED)


class stripe_webhook(views.APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request):
        try:
            payload = request.body
            sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
            event = None
            
            try:
                event = stripe.Webhook.construct_event(
                    payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
                )
            except ValueError as e:
                print(f"Stripe webhook - Invalid payload: {str(e)}")
                return Response({"error": f"Invalid payload: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
            except stripe.error.SignatureVerificationError as e:
                print(f"Stripe webhook - Invalid signature: {str(e)}")
                return Response({"error": f"Invalid signature: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
            
            if event['type'] == 'checkout.session.completed':
                session = event['data']['object']
                orders_metadata = session.get('metadata', {}).get('orders')
                txn_id = session.get('payment_intent') or session.get('id') or "N/A"
                print(f"Stripe webhook - Checkout session completed: {session.get('id')}")
                
                # Retrieve invoice URL if available
                invoice_url = ""
                invoice_id = session.get('invoice')
                if invoice_id:
                    try:
                        inv = stripe.Invoice.retrieve(invoice_id)
                        invoice_url = inv.get('hosted_invoice_url') or inv.get('invoice_pdf') or ""
                    except Exception as e:
                        print(f"Stripe webhook - Error fetching invoice: {e}")

                # If no invoice, try to fetch receipt_url from the charge
                if not invoice_url:
                    pi_id = session.get('payment_intent')
                    if pi_id:
                        try:
                            pi = stripe.PaymentIntent.retrieve(pi_id)
                            charge_id = pi.get('latest_charge')
                            if charge_id:
                                charge = stripe.Charge.retrieve(charge_id)
                                invoice_url = charge.get('receipt_url', '')
                        except Exception as e:
                            print(f"Stripe webhook - Error fetching receipt: {e}")

                if not invoice_url:
                    invoice_url = session.get('success_url', '')

                self._handle_payment_success(orders_metadata, txn_id, invoice_url)

            elif event['type'] == 'payment_intent.succeeded':
                intent = event['data']['object']
                orders_metadata = intent.get('metadata', {}).get('orders')
                txn_id = intent.get('id')
                
                # Retrieve receipt URL from the charge
                invoice_url = ""
                charge_id = intent.get('latest_charge')
                if charge_id:
                    try:
                        charge = stripe.Charge.retrieve(charge_id)
                        invoice_url = charge.get('receipt_url', '')
                    except Exception as e:
                        print(f"Stripe webhook - Error fetching receipt for PI: {e}")
                
                print(f"Stripe webhook - Payment intent succeeded: {txn_id}")
                self._handle_payment_success(orders_metadata, txn_id, invoice_url)
            
            return Response({"message": "Webhook processed successfully"}, status=status.HTTP_200_OK)
        
        except Exception as e:
            print(f"Stripe webhook - CRITICAL ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
            return Response({"error": f"Webhook error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _handle_payment_success(self, orders_metadata, txn_id, invoice_url=""):
        if not orders_metadata:
            print("Stripe webhook - No orders metadata found in success event")
            return

        try:
            from django.db import transaction
            import ast
            
            # orders_metadata is usually a string representation of a list like "[2]" or "2"
            try:
                orders_list = ast.literal_eval(orders_metadata)
                if isinstance(orders_list, int):
                    orders_list = [orders_list]
            except:
                # Fallback for simple string IDs
                if isinstance(orders_metadata, str) and orders_metadata.isdigit():
                    orders_list = [int(orders_metadata)]
                else:
                    print(f"Stripe webhook - Could not parse orders metadata: {orders_metadata}")
                    return

            with transaction.atomic():
                # Fetch orders with related data
                orders_qs = Order.objects.filter(id__in=orders_list).select_related('user', 'partner', 'size')
                
                if not orders_qs.exists():
                    print(f"Stripe webhook - No orders found for IDs: {orders_list}")
                    return

                current_date = timezone.now()
                total_invoice_amount = Decimal('0.00')
                
                for order in orders_qs:
                    # Deduct stock
                    if order.size:
                        PartnerProductSize.objects.filter(id=order.size.id).update(quantity=F('quantity') - order.quantity)
                    
                    # Calculate net amount
                    partner = order.partner
                    total_amount = order.price * order.quantity
                    
                    fees_percent = Decimal(str(getattr(partner, 'fees', 0)))
                    other_charges_percent = Decimal(str(getattr(partner, 'other_charges', 0)))
                    
                    deduction_amount = total_amount * ((fees_percent + other_charges_percent) / 100)
                    net_amount = total_amount - deduction_amount
                    
                    order.net_amount = net_amount
                    order.save(update_fields=['net_amount'])
                    
                    total_invoice_amount += total_amount

                    # Update Payment record
                    Payment.objects.filter(order=order).update(
                        net_amount=net_amount,
                        transaction_id=txn_id
                    )

                    # Update Finance record
                    finance, created = Finance.objects.get_or_create(
                        partner=partner,
                        year=current_date.year,
                        month=current_date.month,
                        defaults={
                            'balance': Decimal('0.00'),
                            'this_month_revenue': Decimal('0.00'),
                        }
                    )
                    
                    if created:
                        prev_finance = Finance.objects.filter(partner=partner).exclude(
                            year=current_date.year, month=current_date.month
                        ).order_by('-year', '-month').first()
                        
                        if prev_finance:
                            finance.balance = prev_finance.balance
                            finance.save()

                    finance.balance = F('balance') + net_amount
                    finance.this_month_revenue = F('this_month_revenue') + net_amount
                    finance.save()

                # Update all orders to confirmed
                updated_count = orders_qs.update(status='confirmed')
                
                # Create OrderInvoice record
                first_order = orders_qs.first()
                order_invoice = OrderInvoice.objects.create(
                    user=first_order.user,
                    partner=first_order.partner,
                    amount=total_invoice_amount,
                    invoice_url=invoice_url,
                    payments=txn_id
                )
                order_invoice.orders.set(orders_qs)
                
                print(f"Stripe webhook - Successfully processed payment. Updated {updated_count} orders. Txn ID: {txn_id}")
        except Exception as e:
            print(f"Stripe webhook - error in _handle_payment_success: {str(e)}")
            import traceback
            traceback.print_exc()


class FinanceDashboardView(views.APIView):
    permission_classes = [permissions.IsAuthenticated,IsPartner]
    def get(self, request):
        partner = request.user

        now = timezone.now()
        finance, created = Finance.objects.get_or_create(
            partner=partner,
            year=now.year,
            month=now.month,
            defaults={
                'balance': 0,
                'this_month_revenue': 0,
                'next_payout': 0,
                'last_payout': 0,
                'reserved_amount': 0,
            }
        )
        
        if created:
            # Carry over balance from most recent previous record
            prev_finance = Finance.objects.filter(
                partner=partner
            ).exclude(year=now.year, month=now.month).order_by('-year', '-month').first()
            
            if prev_finance:
                finance.balance = prev_finance.balance
                finance.save()
        data = DashboardAPIView.monthly_sales(partner)
        return Response({
            "current_balance": finance.balance,
            "this_month_revenue": {
                "balance": data['current_month_sales'],
                "change": data['percentage_change']
            },
            "next_payout": data['last_month_sales'],
            "last_payout": finance.last_payout,
            "reserved_amount": finance.reserved_amount,
            "line_chart": self.get_line_chart_data(partner),
            "pie_chart": self.get_pie_chart_data(partner)
        }, status=status.HTTP_200_OK)

    def get_line_chart_data(self, partner):
        now = timezone.now()
        
        # Get list of last 12 months (including current)
        months_to_show = []
        for i in range(11, -1, -1):
            target_month = now.month - i
            target_year = now.year
            while target_month <= 0:
                target_month += 12
                target_year -= 1
            months_to_show.append((target_year, target_month))
            
        # Aggregate Payment for this partner grouped by month/year
        stats = Payment.objects.filter(
            payment_to=partner,
            transaction_id__isnull=False
        ).annotate(
            month=ExtractMonth('created_at'),
            year=ExtractYear('created_at')
        ).values('year', 'month').annotate(
            total_rev=Sum('net_amount')
        )
        
        # Map stats for easier lookup: {(year, month): total_revenue}
        stats_map = {(s['year'], s['month']): s['total_rev'] for s in stats}
        
        result = []
        month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        
        for year, month in months_to_show:
            revenue = stats_map.get((year, month), 0)
            result.append({
                "month": month_names[month-1],
                "revenue": float(revenue)
            })
            
        return result

    def get_pie_chart_data(self, partner):
        # 1. Get ALL sub-categories from the system
        all_subcategories = SubCategory.objects.all()

        # 2. Aggregate revenue by subcategory from Payments for THIS partner
        stats = Payment.objects.filter(
            payment_to=partner,
            transaction_id__isnull=False
        ).values(
            'product__product__sub_category_id'
        ).annotate(
            revenue=Sum('net_amount')
        )

        stats_map = {item['product__product__sub_category_id']: item['revenue'] for item in stats}
        total_revenue = sum(stats_map.values()) if stats_map else 0
        
        result = []
        seen_ids = set()

        # 3. Add all subcategories with their revenue (or 0)
        for sc in all_subcategories:
            revenue = stats_map.get(sc.id, 0) or 0
            percentage = 0
            if total_revenue > 0:
                percentage = (revenue / total_revenue) * 100
            
            result.append({
                "category": sc.name,
                "percentage": round(float(percentage), 2)
            })
            seen_ids.add(sc.id)

        # 4. Handle any remaining revenue (e.g. products without a subcategory)
        other_revenue = sum(rev for sid, rev in stats_map.items() if sid not in seen_ids)
        if other_revenue > 0:
            percentage = (other_revenue / total_revenue) * 100
            result.append({
                "category": "Other",
                "percentage": round(float(percentage), 2)
            })

        # Sort by percentage descending, then by name
        result.sort(key=lambda x: (-x['percentage'], x['category']))
        return result


class PartnerIncomeView(views.APIView):
    permission_classes = [permissions.IsAuthenticated, IsPartner]
    pagination_class = CustomLimitPagination

    def get(self, request):
        partner = request.user
        payments = Payment.objects.filter(payment_to=partner,transaction_id__isnull=False).order_by('-created_at')

        # Initialize paginator
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(payments, request)

        data = [
            {
                "date": payment.created_at.strftime('%Y-%m-%d'),
                "tnx_id": payment.transaction_id,
                "amount": payment.amount,
                "fees": partner.fees,
                "other": partner.other_charges,
                "revenue": payment.net_amount,
                "status": "Bestätigt"
            }
            for payment in page
        ]

        return paginator.get_paginated_response(data)


class OrderView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        scan = FootScan.objects.filter(user=request.user).first()
        orders = Order.objects.filter(user=request.user).exclude(status='pending').select_related('product', 'size__size')
        return Response(OrderSerializer(orders, many=True, context={'scan': scan}).data, status=status.HTTP_200_OK)


class ClearCartView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        cart = Cart.objects.get(user=request.user)
        cart.items.all().delete()
        return Response({'message': 'Cart cleared successfully'},status=status.HTTP_200_OK)


class AccessoriesAPIView(views.APIView):
    permission_classes = [permissions.IsAuthenticated, IsPartner]

    def post(self, request):
        try:
            name = request.data.get('name')
            brand_name = request.data.get('brand')
            price = request.data.get('price', 0)
            eanc = request.data.get('eanc', None)
            article = request.data.get('article', None)
            warehouse = request.data.get('warehouse', None)
            stock = request.data.get('stock')
            online = request.data.get('online', True)
            local = request.data.get('local', True)
            
            
            if not name:
                return Response({"error": "Name is required."}, status=status.HTTP_400_BAD_REQUEST)

            # 1. Resolve Brand
            brand = Brand.objects.filter(name__iexact=brand_name).first()
            if not brand:
                brand = Brand.objects.create(name=brand_name)

            # 2. Resolve or Create Product
            product, created = Accessories.objects.get_or_create(
                partner=request.user,
                name=name,
                brand=brand,
                defaults={
                    'description': ' ',
                    'price': price,
                    'online': online,
                    'local': local,
                    'eanc': eanc,
                    'article': article,
                    'stock': stock,
                    'warehouse': Warehouse.objects.filter(id=warehouse).first()
                }
            )
            return Response(AccessoriesSerializer(product).data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        search_query = request.query_params.get('q')
        warehouse_id = request.query_params.get('warehouse')
        accessories = Accessories.objects.filter(partner=request.user).order_by('-created_at').select_related('brand', 'warehouse')
        
        if search_query:
            accessories = accessories.filter(
                Q(name__icontains=search_query) |
                Q(brand__name__icontains=search_query) |
                Q(eanc__icontains=search_query) |
                Q(article__icontains=search_query)
            )
        
        if warehouse_id:
            accessories = accessories.filter(warehouse_id=warehouse_id)
            
        return Response(AccessoriesSerializer(accessories, many=True).data, status=status.HTTP_200_OK)

    def delete(self, request):
        pk = request.data.get('id')
        if not pk:
            return Response({"error": "ID is required."}, status=status.HTTP_400_BAD_REQUEST)
        accessories = Accessories.objects.filter(id=pk)

        if not accessories.exists():
            return Response({"error": "Accessories not found."}, status=status.HTTP_404_NOT_FOUND)

        accessories.delete()
        return Response({'message': 'Accessories deleted successfully'}, status=status.HTTP_200_OK)
    
    def patch(self, request):
        try:
            pk = request.data.get('id')
            if not pk:
                return Response({"error": "ID is required."}, status=status.HTTP_400_BAD_REQUEST)
            accessories = Accessories.objects.filter(id=pk)
            if not accessories.exists():
                return Response({"error": "Accessories not found."}, status=status.HTTP_404_NOT_FOUND)
            accessories = accessories.first()
            accessories.name = request.data.get('name', accessories.name)
            brand_name = request.data.get('brand')
            if brand_name:
                brand = Brand.objects.filter(name__iexact=brand_name).first()
                if not brand:
                    brand = Brand.objects.create(name=brand_name)
                accessories.brand = brand
            accessories.price = request.data.get('price', accessories.price)
            accessories.eanc = request.data.get('eanc', accessories.eanc)
            accessories.article = request.data.get('article', accessories.article)
            accessories.stock = request.data.get('stock', accessories.stock)
            accessories.online = request.data.get('online', accessories.online)
            accessories.local = request.data.get('local', accessories.local)
            accessories.warehouse = Warehouse.objects.filter(id=request.data.get('warehouse', accessories.warehouse.id)).first()
            accessories.save()
            return Response(AccessoriesSerializer(accessories).data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

