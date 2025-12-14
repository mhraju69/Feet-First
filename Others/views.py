# views.py
from rest_framework import generics, permissions, views, status
from rest_framework.response import Response
from django.db.models import Sum, F, DecimalField
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

    def monthly_sales(self):

        now = timezone.now()
        
        current_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        current_month_end = now
        
        last_month_end = current_month_start - timedelta(days=1)
        last_month_start = last_month_end.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        current_month_orders = Order.objects.filter(
            created_at__gte=current_month_start,
            created_at__lte=current_month_end
        ).exclude(status='pending').annotate(
            total_price=F('quantity') * F('price')
        ).aggregate(
            total_sales=Sum('total_price', output_field=DecimalField())
        )
        
        current_month_sales = current_month_orders['total_sales'] or Decimal('0.00')
        
        last_month_orders = Order.objects.filter(
            created_at__gte=last_month_start,
            created_at__lte=last_month_end
        ).exclude(status='pending').annotate(
            total_price=F('quantity') * F('price')
        ).aggregate(
            total_sales=Sum('total_price', output_field=DecimalField())
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

    def best_selling_low_stock_alert(self, partner):
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
        
        # Get partner products for best sellers
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
        
        # Get inactive products grouped by brand and subcategory
        from django.db.models import Count
        
        inactive_products = PartnerProduct.objects.filter(
            partner=partner,
            is_active=False
        ).select_related(
            'product',
            'product__brand',
            'product__sub_category'
        ).prefetch_related('size_quantities')
        
        # Filter those with stock > 0
        inactive_with_stock = [pp for pp in inactive_products if pp.total_stock_quantity > 0]
        
        # Group by brand and subcategory
        from collections import defaultdict
        grouped = defaultdict(int)
        for pp in inactive_with_stock:
            key = (pp.product.brand.name if pp.product.brand else 'Unknown Brand',
                   pp.product.sub_category.name if pp.product.sub_category else 'Unknown Category')
            grouped[key] += 1
        
        # Sort by count
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
        
        # Seasonal marketing recommendations
        import random
        month = now.month
        
        # Define seasonal subcategory recommendations
        seasonal_recommendations = {
            # Spring (March, April, May)
            'spring': {
                'months': [3, 4, 5],
                'subcategories': ['Laufschuh', 'Trailschuh', 'Wanderschuh', 'Freizeitschuh'],
                'title_de': 'Frühlings-Trend nutzen',
                'title_it': 'Sfrutta il trend primaverile',
                'message_de': 'Laufschuhe und Outdoor-Modelle zeigen steigendes Interesse. Erwägen Sie zusätzliche Marketingaktionen.',
                'message_it': 'Le scarpe da corsa e i modelli outdoor mostrano un crescente interesse. Considerate azioni di marketing aggiuntive.'
            },
            # Summer (June, July, August)
            'summer': {
                'months': [6, 7, 8],
                'subcategories': ['Laufschuh', 'Trailschuh', 'Barfußschuh', 'Sandale', 'Freizeitschuh'],
                'title_de': 'Sommer-Trend nutzen',
                'title_it': 'Sfrutta il trend estivo',
                'message_de': 'Sneaker und leichte Sportschuhe zeigen steigendes Interesse. Erwägen Sie zusätzliche Marketingaktionen.',
                'message_it': 'Sneaker e scarpe sportive leggere mostrano un crescente interesse. Considerate azioni di marketing aggiuntive.'
            },
            # Fall (September, October, November)
            'fall': {
                'months': [9, 10, 11],
                'subcategories': ['Wanderschuh', 'Trailschuh', 'Laufschuh', 'Winterschuh'],
                'title_de': 'Herbst-Trend nutzen',
                'title_it': 'Sfrutta il trend autunnale',
                'message_de': 'Wanderschuhe und robuste Outdoor-Modelle zeigen steigendes Interesse. Erwägen Sie zusätzliche Marketingaktionen.',
                'message_it': 'Scarpe da trekking e modelli outdoor robusti mostrano un crescente interesse. Considerate azioni di marketing aggiuntive.'
            },
            # Winter (December, January, February)
            'winter': {
                'months': [12, 1, 2],
                'subcategories': ['Winterschuh', 'Wanderschuh', 'Freizeitschuh'],
                'title_de': 'Winter-Trend nutzen',
                'title_it': 'Sfrutta il trend invernale',
                'message_de': 'Winterschuhe und wärmende Modelle zeigen steigendes Interesse. Erwägen Sie zusätzliche Marketingaktionen.',
                'message_it': 'Scarpe invernali e modelli caldi mostrano un crescente interesse. Considerate azioni di marketing aggiuntive.'
            }
        }
        
        # Find current season
        current_season = None
        for season, data in seasonal_recommendations.items():
            if month in data['months']:
                current_season = data
                break
        
        marketing_recommendations = []
        if current_season:
            # Get partner's available subcategories that match seasonal recommendations
            partner_products_seasonal = PartnerProduct.objects.filter(
                partner=partner,
                is_active=True,
                product__sub_category__name__in=current_season['subcategories']
            ).select_related('product__sub_category').prefetch_related('size_quantities')
            
            # Filter those with stock > 0
            partner_subcategories = set()
            for pp in partner_products_seasonal:
                if pp.total_stock_quantity > 0:
                    partner_subcategories.add(pp.product.sub_category.name)
            
            available_subcategories = list(partner_subcategories)
            
            if available_subcategories:
                # Randomly select one subcategory from available ones
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
        
        return {
            'best_selling': alerts,
            'inactive_product': inactive_alerts,
            'seasonal_marketing': marketing_recommendations
        }

    def get(self, request):
        sales_data = self.monthly_sales()
        orders_data = self.weekly_orders()
        products_data = self.partner_products(request.user)
        low_stock_data = self.low_stock_products(request.user)
        recent_orders_data = self.recent_orders(request)
        best_selling_alerts = self.best_selling_low_stock_alert(request.user)
        
        return Response({
            'monthly_sales': sales_data,
            'weekly_orders': orders_data,
            'partner_products': products_data,
            'low_stock_products': low_stock_data,
            'recent_orders': recent_orders_data,
            'alerts': best_selling_alerts,
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

        # Phase 1: Validate ALL items first
        for index, item in enumerate(products):
            try:
                product_id = item.get('product')
                partner_id = item.get('partner')
                quantity = int(item.get('quantity', 1))
                size_str = item.get('size')
                color = item.get('color')
                
                if not all([product_id, partner_id, size_str, color]):
                    return Response({
                        "error": f"Missing fields in item {index+1} (product, partner, size, color required)"
                    }, status=status.HTTP_400_BAD_REQUEST)

                # 1. Validate Product & Partner
                try:
                    product = Product.objects.get(id=product_id)
                    partner = User.objects.get(id=partner_id)
                except (Product.DoesNotExist, User.DoesNotExist):
                    return Response({
                        "error": f"Invalid product or partner ID in item {index+1}"
                    }, status=status.HTTP_400_BAD_REQUEST)

                # 2. Validate Partner Sells Product (Active)
                partner_product = PartnerProduct.objects.filter(
                    product=product, 
                    partner=partner, 
                    is_active=True
                ).first()
                
                if not partner_product:
                    return Response({
                        "error": f"Product '{product.name}' is not currently available from {partner.name or partner.email}"
                    }, status=status.HTTP_400_BAD_REQUEST)

                # 3. Validate Stock Availability
                # Find matching size in partner inventory
                pp_sizes = PartnerProductSize.objects.filter(partner_product=partner_product).select_related('size')
                target_stock_item = None
                
                for pps in pp_sizes:
                    # Match against "EU 42", "42", etc.
                    s_obj = pps.size
                    if (str(s_obj) == str(size_str)) or \
                       (str(s_obj.value) == str(size_str)) or \
                       (f"{s_obj.type} {s_obj.value}" == str(size_str)):
                        target_stock_item = pps
                        break
                
                if not target_stock_item:
                    # If strictly checking availability, not finding the size is an error
                    return Response({
                        "error": f"Size '{size_str}' is not listed for '{product.name}' by this partner"
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                if target_stock_item.quantity < quantity:
                    return Response({
                        "error": f"Insufficient stock for '{product.name}' size {size_str}. Available: {target_stock_item.quantity}"
                    }, status=status.HTTP_400_BAD_REQUEST)

                # 4. Prepare Validated Item
                customer_name = request.user.name if hasattr(request.user, 'name') and request.user.name else request.user.email
                
                validated_items.append({
                    'user': request.user,
                    'partner': partner,
                    'product': product,
                    'price': partner_product.price,
                    'quantity': quantity,
                    'size': size_str,
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
                
        except Exception as e:
             return Response({"error": f"Failed to create orders: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({
            "message": "Orders created successfully", 
            "created_count": len(created_ids),
            "order_ids": created_ids,
            "total_amount": total_amount
        }, status=status.HTTP_201_CREATED)