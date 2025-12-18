# views.py
from rest_framework import generics, permissions, views, status
from rest_framework.response import Response
from django.db.models import Sum, F, DecimalField, Case, When
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
from .helper import create_checkout_session
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
        
        fees_percent = Decimal(str(partner.fees))
        other_charges_percent = Decimal(str(partner.other_charges))
        multiplier = (Decimal('100') - (fees_percent + other_charges_percent)) / Decimal('100')

        current_month_orders = Order.objects.filter(
            partner=partner,
            created_at__gte=current_month_start,
            created_at__lte=current_month_end
        ).exclude(status='pending').annotate(
            effective_net=Case(
                When(net_amount__gt=0, then=F('net_amount')),
                default=F('quantity') * F('price') * multiplier,
                output_field=DecimalField()
            )
        ).aggregate(
            total_sales=Sum('effective_net')
        )
        
        current_month_sales = current_month_orders['total_sales'] or Decimal('0.00')
        
        last_month_orders = Order.objects.filter(
            partner=partner,
            created_at__gte=last_month_start,
            created_at__lte=last_month_end
        ).exclude(status='pending').annotate(
            effective_net=Case(
                When(net_amount__gt=0, then=F('net_amount')),
                default=F('quantity') * F('price') * multiplier,
                output_field=DecimalField()
            )
        ).aggregate(
            total_sales=Sum('effective_net')
        )
        
        last_month_sales = last_month_orders['total_sales'] or Decimal('0.00')
        
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
        new = Order.objects.filter(partner=self.request.user,status='completed').count()
        packaging = Order.objects.filter(partner=self.request.user,status='packaging').count()
        shipping = Order.objects.filter(partner=self.request.user,status='shipping').count()
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

class CreateOrderView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        products = request.data.get('products',[])
        if not products:
             return Response({"error": "No products provided"}, status=status.HTTP_400_BAD_REQUEST)

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

        # Phase 1: Validate ALL items first
        for index, item in enumerate(products):
            try:
                product_id = item.get('product')
                quantity = int(item.get('quantity', 1))
                size_id = item.get('size_id')  # This is now PartnerProductSize ID
                color = item.get('color')
                
                if not all([product_id, size_id, color]):
                    return Response({
                        "error": f"Missing fields in item {index+1} (product, size_id, color required)"
                    }, status=status.HTTP_400_BAD_REQUEST)

                # 1. Validate Product & Partner
                try:
                    partner_product = PartnerProduct.objects.get(id=product_id)
                    partner = partner_product.partner
                    product = partner_product.product
                except (PartnerProduct.DoesNotExist):
                    return Response({
                        "error": f"Invalid product or partner ID in item {index+1}"
                    }, status=status.HTTP_400_BAD_REQUEST)

                # 3. Validate PartnerProductSize and Stock Availability
                try:
                    partner_product_size = PartnerProductSize.objects.select_related('size').get(
                        id=size_id,
                        partner_product=partner_product
                    )
                except PartnerProductSize.DoesNotExist:
                    return Response({
                        "error": f"Invalid size ID in item {index+1} or size doesn't belong to this partner's product"
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                if partner_product_size.quantity < quantity:
                    return Response({
                        "error": f"Insufficient stock for '{product.name}' size {partner_product_size.size}. Available: {partner_product_size.quantity}"
                    }, status=status.HTTP_400_BAD_REQUEST)

                # 4. Prepare Validated Item
                customer_name = request.user.name if hasattr(request.user, 'name') and request.user.name else request.user.email
                
                validated_items.append({
                    'user': request.user,
                    'partner': partner,
                    'product': product,
                    'price': partner_product.price,
                    'quantity': quantity,
                    'size': partner_product_size,  # Store the PartnerProductSize object
                    'color': color,
                    'name': customer_name
                })
                
                total_amount += (partner_product.price * quantity)

            except ValueError:
                return Response({"error": f"Invalid quantity format in item {index+1}"}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({"error": f"Validation error in item {index+1}: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
                    amount=order.price,
                    created_at=timezone.now()
                )
                payments_ids.append(payment.id)
                
        except Exception as e:
             return Response({"error": f"Failed to create orders: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        checkout_session_url = create_checkout_session(created_ids, payments_ids, total_amount)
        
        return Response({
            "message": "Orders created successfully", 
            "checkout_session_url": checkout_session_url,
        }, status=status.HTTP_201_CREATED)

class stripe_webhook(views.APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request):
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        event = None
        
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        except ValueError as e:
            return Response({"error": f"Invalid payload: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        except stripe.error.SignatureVerificationError as e:
            return Response({"error": f"Invalid signature: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        
        print(f"Webhook received: {event['type']}")
        
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            orders = session.metadata.get('orders')
            payments = session.metadata.get('payments')
            
            print(f"Session Metadata - Orders: {orders}, Payments: {payments}")
            
            if orders and payments:
                try:
                    orders_list = ast.literal_eval(orders)
                    payments_list = ast.literal_eval(payments)
                    
                    # Deduct quantity from sizes and Update MonthlySales
                    orders_qs = Order.objects.filter(id__in=orders_list)
                    current_date = timezone.now()
                    
                    for order in orders_qs:
                        # Deduct stock
                        if order.size_id:
                            PartnerProductSize.objects.filter(id=order.size_id).update(quantity=F('quantity') - order.quantity)
                        
                        # Calculate net amount based on partner's fees and other charges
                        partner = order.partner
                        total_amount = order.price * order.quantity
                        
                        fees_percent = Decimal(str(partner.fees))
                        other_charges_percent = Decimal(str(partner.other_charges))
                        total_deduction_percent = fees_percent + other_charges_percent
                        
                        deduction_amount = total_amount * (total_deduction_percent / 100)
                        net_amount = total_amount - (deduction_amount * order.quantity)
                        
                        order.net_amount = net_amount
                        order.save(update_fields=['net_amount'])

                        # Update MonthlySales
                        # Find the PartnerProduct
                        partner_product = None
                        if order.size:
                             partner_product = order.size.partner_product
                        elif order.product:
                             # Fallback: try to find PartnerProduct for this partner and product
                             partner_product = PartnerProduct.objects.filter(partner=order.partner, product=order.product).first()

                        if partner_product:
                            monthly_sales_obj, created = MonthlySales.objects.get_or_create(
                                partner=order.partner,
                                product=partner_product,
                                year=current_date.year,
                                month=current_date.month,
                                defaults={
                                    'sale_count': 0,
                                    'total_revenue': 0
                                }
                            )
                            # We use F expressions for atomic updates
                            monthly_sales_obj.sale_count = F('sale_count') + order.quantity
                            monthly_sales_obj.total_revenue = F('total_revenue') + net_amount
                            monthly_sales_obj.save()

                        # Update Partner Finance Balance
                        # Update Partner Finance Balance for current month
                        finance, created = Finance.objects.get_or_create(
                            partner=order.partner,
                            year=current_date.year,
                            month=current_date.month,
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
                                partner=order.partner
                            ).exclude(year=current_date.year, month=current_date.month).order_by('-year', '-month').first()
                            
                            if prev_finance:
                                finance.balance = prev_finance.balance
                                finance.save()

                        finance.balance = F('balance') + net_amount
                        finance.this_month_revenue = F('this_month_revenue') + net_amount
                        finance.save()

                    # Update all orders to confirmed
                    updated_orders = orders_qs.update(status='confirmed')
                    
                    # Update payments with transaction ID (prefer payment_intent, fallback to session id)
                    txn_id = session.get('payment_intent') or session.get('id')
                    updated_payments = Payment.objects.filter(id__in=payments_list).update(transaction_id=txn_id)
                    
                    print(f"Updated {updated_orders} orders and {updated_payments} payments. Txn ID: {txn_id}")
                except Exception as e:
                    print(f"Error updating orders/payments: {str(e)}")
                    return Response({"error": f"Error updating orders: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                print("Missing orders or payments in metadata")
        
        return Response({"message": "Webhook processed successfully"}, status=status.HTTP_200_OK)

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
            
        # Aggregate MonthlySales for this partner grouped by month/year
        stats = MonthlySales.objects.filter(
            partner=partner
        ).values('year', 'month').annotate(
            total_rev=Sum('total_revenue')
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
        # Aggregate revenue by subcategory
        stats = MonthlySales.objects.filter(
            partner=partner
        ).values(
            category_name=F('product__product__sub_category__name')
        ).annotate(
            revenue=Sum('total_revenue')
        ).order_by('-revenue')

        total_revenue = sum(item['revenue'] for item in stats) or 1 # Avoid division by zero
        
        result = []
        for item in stats:
            percentage = (item['revenue'] / total_revenue) * 100
            result.append({
                "category": item['category_name'],
                # "revenue": float(item['revenue']),
                "percentage": round(float(percentage), 2)
            })
            
        return result