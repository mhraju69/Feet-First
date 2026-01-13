from .utils import *
import csv
import openpyxl
from .models import *
from io import BytesIO
from .serializers import *
from core.permission import *
from datetime import datetime
from openpyxl import Workbook
from django.db.models import Q, F
from decimal import Decimal
from rest_framework import filters
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from openpyxl.styles import Font, PatternFill, Alignment
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, generics, views, status
from rest_framework.parsers import MultiPartParser, FormParser

class CustomLimitPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'limit'
    max_page_size = 50


class ProductListView(generics.ListAPIView):
    """
    Multi-vendor product listing.
    Shows products from PartnerProduct with partner-specific prices, sizes, and colors.
    """
    serializer_class = PartnerProductListSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = CustomLimitPagination    

    # enable filters + search
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['product__name', 'product__description', 'product__brand__name']
    filterset_fields = ['product__sub_category__slug', 'product__gender', 'product__brand']

    def get_queryset(self):
        """
        Build the queryset from PartnerProduct for multi-vendor system.
        Apply filters and optional match score sorting.
        """
        # Get only active partner products
        queryset = PartnerProduct.objects.filter(
            is_active=True,
            product__is_active=True
        ).select_related(
            'product', 'product__brand', 'product__sub_category',
            'partner'
        ).prefetch_related('product__images', 'size_quantities__size', 'color')
        
        # --- Brand filter ---
        brand = self.request.query_params.get("brandName")
        if brand:
            queryset = queryset.filter(product__brand__name__iexact=brand)
        else:
            # No brand requested, exclude Imotana by default
            queryset = queryset.exclude(product__brand__name__iexact="imotana")

        # --- Sub category filter ---
        sub = self.request.query_params.get("sub_category")
        if sub:
            queryset = queryset.filter(product__sub_category__slug=sub)

        # --- Gender filter ---
        gender = self.request.query_params.get("gender")
        if gender:
            queryset = queryset.filter(product__gender=gender)

        # --- Size filter ---
        size_id = self.request.query_params.get("size_id")
        if size_id:
            queryset = queryset.filter(size__id=size_id)

        # --- Color filter ---
        color_id = self.request.query_params.get("color_id")
        if color_id:
            queryset = queryset.filter(color__id=color_id)

        # --- Partner filter ---
        partner_id = self.request.query_params.get("partner_id")
        if partner_id:
            queryset = queryset.filter(partner_id=partner_id)

        # --- Match sorting ---
        match = self.request.query_params.get("match")
        scan = FootScan.objects.filter(user=self.request.user).first()

        if match and match.lower() == "true" and scan:
            partner_products = list(queryset)
            partner_products.sort(
                key=lambda pp: pp.product.match_with_scan(scan).get("score", 0),
                reverse=True  # higher score first
            )
            return partner_products

        # Default: order by latest (descending id)
        return queryset.order_by('-id')

    def list(self, request, *args, **kwargs):
        """
        Apply DRF search + filter backends even when get_queryset() returns a list.
        """
        queryset = self.get_queryset()

        # Apply search and filters manually
        if not isinstance(queryset, list):
            queryset = self.filter_queryset(queryset)

        # Handle pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        match = self.request.query_params.get("match")
        scan = FootScan.objects.filter(user=self.request.user).first()
        context["scan"] = scan
        context["match"] = match and match.lower() == "true"
        # Pre-fetch favorite IDs to avoid N+1 queries in serializer
        if self.request.user.is_authenticated:
            favorite_ids = Favorite.objects.filter(user=self.request.user).values_list('products__id', flat=True)
            context["favorite_ids"] = set(favorite_ids)
        else:
            context["favorite_ids"] = set()
        return context


class ProductsCountView(views.APIView):
    """Count available partner products (multi-vendor)"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        sub = request.query_params.get("sub_category")
        gender = request.query_params.get("gender")

        queryset = PartnerProduct.objects.filter(
            is_active=True,
            product__is_active=True
        )
        
        if sub:
            queryset = queryset.filter(product__sub_category__slug=sub)
        
        if gender:
            queryset = queryset.filter(product__gender=gender)
        
        count = queryset.count()

        return Response({"count": count}, status=200)


class ProductDetailView(generics.RetrieveAPIView):
    """
    Multi-vendor product detail view.
    Retrieves a specific PartnerProduct with partner-specific price, size, color.
    """
    serializer_class = PartnerProductDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = PartnerProduct.objects.filter(is_active=True, product__is_active=True)
    lookup_field = 'id'

    def get_queryset(self):
        return super().get_queryset().select_related(
            'product', 'product__brand', 'product__sub_category',
            'partner'
        ).prefetch_related('product__images', 'product__images__color', 'product__features', 'size_quantities__size', 'color')

    def get_serializer_context(self):
        context = super().get_serializer_context()
        scan = FootScan.objects.filter(user=self.request.user).first()
        context['scan'] = scan
        # Pre-fetch favorite IDs to avoid N+1 queries in serializer
        if self.request.user.is_authenticated:
            favorite_ids = Favorite.objects.filter(user=self.request.user).values_list('products__id', flat=True)
            context["favorite_ids"] = set(favorite_ids)
        else:
            context["favorite_ids"] = set()
        return context


class FootScanListCreateView(generics.ListCreateAPIView):
    """List all foot scans or create a new one."""
    serializer_class = FootScanSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return FootScan.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class FavoriteUpdateView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        favorite, created = Favorite.objects.get_or_create(user=request.user)
        favorite_ids = favorite.products.values_list('id', flat=True)
        serializer = FavoriteSerializer(favorite, context={'request': request, 'scan': None, 'match': False, 'favorite_ids': set(favorite_ids)})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        favorite, created = Favorite.objects.get_or_create(user=request.user)

        product_id = request.data.get('product_id')
        action = request.data.get('action')

        if not product_id or action not in ['add', 'remove']:
            return Response({"error": "Invalid request."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # The favorite model now stores PartnerProduct instances
            partner_product = PartnerProduct.objects.get(id=product_id, is_active=True)
        except (PartnerProduct.DoesNotExist, ValueError):
            return Response({"error": "Product not found in inventory."}, status=status.HTTP_404_NOT_FOUND)

        if action == 'add':
            favorite.products.add(partner_product)
            message = "Product added to favorites"
        else:
            favorite.products.remove(partner_product)
            message = "Product removed from favorites"
        
        return Response({"message": message}, status=status.HTTP_200_OK)


class SuggestedProductsView(generics.ListAPIView):
    """
    Suggest similar partner products based on a given partner product.
    Multi-vendor system: returns PartnerProducts with partner-specific pricing.
    """
    serializer_class = PartnerProductListSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = CustomLimitPagination

    def get_queryset(self):
        partner_product_id = self.kwargs.get("product_id")

        if not partner_product_id:
            return PartnerProduct.objects.none()

        try:
            partner_product = PartnerProduct.objects.select_related('product').get(
                id=partner_product_id, 
                is_active=True,
                product__is_active=True
            )
            product = partner_product.product
        except PartnerProduct.DoesNotExist:
            return PartnerProduct.objects.none()

        # Get all SizeTable IDs linked to this product via sizes ManyToMany
        size_table_ids = product.sizes.values_list('id', flat=True)

        # Prepare base queryset - find similar PartnerProducts
        queryset = PartnerProduct.objects.filter(
            is_active=True,
            product__is_active=True,
            product__sub_category=product.sub_category,
            product__gender=product.gender,
            product__sizes__id__in=size_table_ids,  # match same size tables
        ).exclude(
            id=partner_product_id
        ).select_related(
            'product', 'product__brand', 'product__sub_category',
            'partner'
        ).prefetch_related('product__images', 'size_quantities__size', 'color').distinct()

        # Add scan-based ranking (if exists)
        scan = FootScan.objects.filter(user=self.request.user).first()

        if scan:
            foot_width_cat = scan.width_category()
            foot_toe_box = scan.toe_box_category()

            partner_products_list = list(queryset)
            partner_products_list.sort(
                key=lambda pp: (
                    abs(getattr(pp.product, "width", 0) - foot_width_cat),
                    0 if getattr(pp.product, "toe_box", None) == foot_toe_box else 1,
                    -pp.product.match_with_scan(scan).get("score", 0),
                )
            )
            return partner_products_list[:20]  # Top 20 matches

        return queryset[:20]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        scan = FootScan.objects.filter(user=self.request.user).first()
        context["scan"] = scan
        context["match"] = True
        # Pre-fetch favorite IDs to optimize serializer
        if self.request.user.is_authenticated:
            favorite_ids = Favorite.objects.filter(user=self.request.user).values_list('products__id', flat=True)
            context["favorite_ids"] = set(favorite_ids)
        else:
            context["favorite_ids"] = set()
        return context

                
class ProductQnAFilterAPIView(views.APIView):
    """
    Filter products by Q&A in multi-vendor system.
    Returns PartnerProducts with partner-specific pricing.
    """
    pagination_class = CustomLimitPagination
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        data = request.data

        if not isinstance(data, dict):
            return Response(
                {"error": "Invalid data format, expected a JSON object."},
                status=status.HTTP_400_BAD_REQUEST
            )

        cat = data.get("sub_category")
        questions_data = data.get("questions", [])

        # If no questions provided, return empty
        if not questions_data:
            return self.empty_paginated_response(request)

        if not cat:
            return self.empty_paginated_response(request)

        # Build OR query across ALL questions
        combined_query = Q()
        
        for question_item in questions_data:
            question_key = question_item.get("question")
            answer_keys = question_item.get("answers", [])
            
            if not question_key or not answer_keys:
                continue
            
            # Find the question object by EXACT key match
            try:
                question_obj = Question.objects.get(key=question_key)
            except Question.DoesNotExist:
                continue
            
            # For this question, build OR query for all answer options
            for answer_key in answer_keys:
                if answer_key and answer_key.strip():
                    combined_query |= Q(
                        product__question_answers__question=question_obj,
                        product__question_answers__answers__key=answer_key
                    )
        
        # If no valid query built, return empty
        if not combined_query:
            return self.empty_paginated_response(request)
        
        # Get PartnerProducts matching the Q&A filter
        queryset = PartnerProduct.objects.filter(
            is_active=True,
            product__is_active=True,
            product__sub_category__slug=cat
        ).filter(combined_query).select_related(
            'product', 'product__brand', 'product__sub_category',
            'partner'
        ).prefetch_related('product__images', 'size_quantities__size', 'color').distinct()
        
        # Final check
        if not queryset.exists():
            return self.empty_paginated_response(request)

        # Get scan for context
        scan = FootScan.objects.filter(user=request.user).first()

        # Pagination and serialization
        paginator = self.pagination_class()
        paginated_products = paginator.paginate_queryset(queryset, request, view=self)
        serializer = PartnerProductListSerializer(
            paginated_products, 
            many=True, 
            context={'request': request, 'scan': scan, 'favorite_ids': set(Favorite.objects.filter(user=request.user).values_list('products__id', flat=True)) if request.user.is_authenticated else set()}
        )
        
        return paginator.get_paginated_response(serializer.data)

    # Helper method for empty response
    def empty_paginated_response(self, request):
        paginator = self.pagination_class()
        empty_queryset = PartnerProduct.objects.none()
        paginated = paginator.paginate_queryset(empty_queryset, request, view=self)
        serializer = PartnerProductListSerializer(paginated, many=True)
        return paginator.get_paginated_response(serializer.data)


class AllProductsForPartnerView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated, IsPartner]
    pagination_class = CustomLimitPagination
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['name', 'description', 'brand__name']
    filterset_fields = ['sub_category__slug', 'gender', 'brand']

    def get_queryset(self):
        user = self.request.user
        # Get all product IDs that this partner has already added
        partner_product_ids = PartnerProduct.objects.filter(partner=user).values_list('product_id', flat=True)
        
        # Return all active products that are NOT in the partner's inventory
        queryset = Product.objects.filter(is_active=True).exclude(id__in=partner_product_ids).order_by('-id')
        return queryset


class SingleProductForPartnerView(views.APIView):
    permission_classes = [permissions.IsAuthenticated, IsPartner]
    
    def get(self, request, product_id):
        try:
            partner_product = PartnerProduct.objects.get(product_id=product_id, partner=request.user)
            serializer = PartnerProductSerializer(partner_product)
            return Response(serializer.data)
        except PartnerProduct.DoesNotExist:
            return Response({"error": "Partner product not found"}, status=status.HTTP_404_NOT_FOUND)


class ApprovedPartnerProductView(generics.ListAPIView):
    """View to show all products in the partner's inventory"""
    permission_classes = [permissions.IsAuthenticated, IsPartner]
    pagination_class = CustomLimitPagination
    serializer_class = PartnerProductSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['product__name', 'product__description', 'product__brand__name']
    filterset_fields = ['product__sub_category__slug', 'product__gender', 'product__brand']

    def get_queryset(self):
        # Return all PartnerProduct entries for this partner
        return PartnerProduct.objects.filter(partner=self.request.user).select_related('product', 'product__brand').prefetch_related('product__images', 'product__images__color')  


class ApprovedPartnerProductUpdateView(views.APIView):
    """View to add or remove products from partner's inventory"""
    permission_classes = [permissions.IsAuthenticated, IsPartner]

    def patch(self, request, *args, **kwargs):
        product_id = kwargs.get('product_id')
        warehouse_id = request.data.get('warehouse_id', None)
        action = kwargs.get('action')
        
        # Valid actions: add, update, del/remove
        if not product_id or action not in ['add', 'update', 'del', 'remove']:
            return Response({"error": "Invalid request. Provide product_id and valid action (add/update/del)."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            product = Product.objects.get(id=product_id, is_active=True)
        except Product.DoesNotExist:
            return Response({"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

        if action == 'add':
            # Check if already exists
            if PartnerProduct.objects.filter(partner=request.user, product=product).exists():
                return Response({"error": "Product already exists in your inventory. Use 'update' action instead."}, status=status.HTTP_400_BAD_REQUEST)

            price = request.data.get('price')
            size_quantities = request.data.get('sizes', [])
            color_ids = request.data.get('colors', [])

            if not price:
                return Response({"error": "Price is required when adding a product."}, status=status.HTTP_400_BAD_REQUEST)
            if not size_quantities or not isinstance(size_quantities, list):
                return Response({"error": "Sizes with quantities are required."}, status=status.HTTP_400_BAD_REQUEST)
            # Validate colors (Support 'colors' OR 'images')
            req_color_ids = request.data.get('colors', [])
            req_image_ids = request.data.get('images', [])
            
            final_color_ids = set()
            
            # 1. Direct Colors
            if req_color_ids and isinstance(req_color_ids, list):
                final_color_ids.update(req_color_ids)
                
            # 2. Images -> Colors
            if req_image_ids and isinstance(req_image_ids, list):
                images = ProductImage.objects.filter(id__in=req_image_ids).select_related('color')
                for img in images:
                    if img.color:
                        final_color_ids.add(img.color.id)
            
            # Validation
            if not final_color_ids:
                 return Response({"error": "At least one color (or image with color) is required."}, status=status.HTTP_400_BAD_REQUEST)
            
            valid_colors = list(Color.objects.filter(id__in=final_color_ids))
            if not valid_colors:
                return Response({"error": "One or more colors not found."}, status=status.HTTP_404_NOT_FOUND)
            
            # Proceed with valid_colors (list of objects) or their IDs
            final_valid_color_ids = [c.id for c in valid_colors]

            partner_product = PartnerProduct.objects.create(
                partner=request.user,
                product=product,
                price=price,
                is_active=True,
                online=request.data.get('online', True),
                local=request.data.get('local', True)
            )
            partner_product.color.set(final_valid_color_ids)

            for sq_data in size_quantities:
                PartnerProductSize.objects.create(
                    partner_product=partner_product,
                    size_id=sq_data.get('size_id'),
                    quantity=sq_data.get('quantity', 0)
                )

            if warehouse_id:
                try:
                    warehouse = Warehouse.objects.get(id=warehouse_id, partner=request.user)
                    warehouse.product.add(partner_product)
                except Warehouse.DoesNotExist:
                    pass

            serializer = PartnerProductSerializer(partner_product)
            return Response({"message": "Product added to inventory", "data": serializer.data}, status=status.HTTP_201_CREATED)

        elif action == 'update':
            try:
                partner_product = PartnerProduct.objects.get(partner=request.user, product=product)
            except PartnerProduct.DoesNotExist:
                return Response({"error": "Product not found in your inventory."}, status=status.HTTP_404_NOT_FOUND)

            # Update fields if present (Patch behavior)
            fields_to_update = ['price', 'is_active', 'online', 'local']
            for field in fields_to_update:
                if field in request.data:
                    setattr(partner_product, field, request.data.get(field))
            partner_product.save()

            # -- Handle Colors (Modified to support Image IDs) --
            # User might send 'colors' (Color IDs) OR 'images' (ProductImage IDs)
            # We want to support both.
            
            req_color_ids = request.data.get('colors')
            req_image_ids = request.data.get('images')
            
            final_color_ids = set()

            # 1. Check Colors
            if req_color_ids and isinstance(req_color_ids, list):
                final_color_ids.update(req_color_ids)

            # 2. Check Images (Resolve to Colors)
            if req_image_ids and isinstance(req_image_ids, list):
                 # Get valid images and their colors
                 images = ProductImage.objects.filter(id__in=req_image_ids).select_related('color')
                 for img in images:
                     if img.color:
                         final_color_ids.add(img.color.id)
            
            # If we have gathered color IDs, update/set them
            if final_color_ids:
                # Basic validation that these colors exist will happen via .set() usually, 
                # but let's be safe if they passed raw IDs that might be wrong
                # We can just filter valid ones
                valid_colors = Color.objects.filter(id__in=final_color_ids).values_list('id', flat=True)
                partner_product.color.set(valid_colors)
            elif 'colors' in request.data: 
                # If 'colors' key was explicitly sent as empty list, maybe they want to clear colors?
                # But requirement says "One or more colors not found" if invalid.
                # If they sent empty list, we effectively cleared it above (set() is empty).
                # But let's respect explicit empty list if intended. 
                # However, if they sent INVALID IDs previously, we might have ignored them.
                # Let's trust valid_colors logic.
                partner_product.color.set([])

            if 'sizes' in request.data:
                size_quantities = request.data.get('sizes', [])
                if isinstance(size_quantities, list):
                    resolved_map = {}
                    
                    # Validate and Resolve IDs
                    for sq_data in size_quantities:
                        input_id = sq_data.get('size_id')
                        if input_id is None: continue
                        
                        # 1. Is it a PartnerProductSize ID for THIS product?
                        # Using filter().first() avoids exception
                        pps = PartnerProductSize.objects.filter(id=input_id, partner_product=partner_product).first()
                        if pps:
                            resolved_map[input_id] = pps.size_id
                            continue
                            
                        # 2. Is it a raw Size ID?
                        # We cast to int to be safe, though Django checks handle strings often
                        try:
                            if Size.objects.filter(id=input_id).exists():
                                resolved_map[input_id] = input_id
                                continue
                        except (ValueError, TypeError):
                            pass
                            
                        return Response({"error": f"Size ID {input_id} not found."}, status=status.HTTP_404_NOT_FOUND)

                    # Apply Updates
                    for sq_data in size_quantities:
                        input_id = sq_data.get('size_id')
                        quantity = sq_data.get('quantity', 0)
                        real_size_id = resolved_map.get(input_id)
                        
                        if real_size_id is not None:
                            PartnerProductSize.objects.update_or_create(
                                partner_product=partner_product,
                                size_id=real_size_id,
                                defaults={'quantity': quantity}
                            )

            serializer = PartnerProductSerializer(partner_product)
            return Response({"message": "Product updated in inventory", "data": serializer.data}, status=status.HTTP_200_OK)

        else:  # action in ['del', 'remove']
            deleted_count, _ = PartnerProduct.objects.filter(partner=request.user, product=product).delete()
            if deleted_count == 0:
                return Response({"error": "Product not found in your inventory."}, status=status.HTTP_404_NOT_FOUND)
            return Response({"message": "Product removed from inventory"}, status=status.HTTP_200_OK)


class FileUploadPartnerProductView(views.APIView):
    """
    View to upload and read data from Excel or CSV files for partner products.
    """
    permission_classes = [permissions.IsAuthenticated, IsPartner]
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        file = request.FILES.get('file')
        if not file:
            return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)

        filename = file.name
        data = []

        if filename.endswith('.csv'):
            try:
                # Read CSV file
                decoded_file = file.read().decode('utf-8').splitlines()
                reader = csv.DictReader(decoded_file)
                for row in reader:
                    data.append(row)
            except Exception as e:
                return Response({"error": f"Error reading CSV: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

        elif filename.endswith('.xlsx') or filename.endswith('.xls'):
            try:
                # Read Excel file
                workbook = openpyxl.load_workbook(file, data_only=True)
                sheet = workbook.active
                
                # Get headers from the first row
                headers = [cell.value for cell in sheet[1]]
                
                # Iterate through rows starting from the second row
                for row in sheet.iter_rows(min_row=2, values_only=True):
                    # Create a dictionary for each row mapping headers to values
                    row_data = dict(zip(headers, row))
                    data.append(row_data)
            except Exception as e:
                return Response({"error": f"Error reading Excel: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": "Unsupported file format. Please upload CSV or XLSX."}, status=status.HTTP_400_BAD_REQUEST)

        return self.process_uploaded_data(request, data)

    def process_uploaded_data(self, request, data):
        partner = request.user
        total_rows = len(data)
        matched_products_count = 0
        skipped_rows_count = 0
        new_partner_products_count = 0
        size_updates_count = 0
        
        # Local cache for products to avoid redundant queries
        product_cache = {}

        for row in data:
            item_name = row.get('Item name')
            if not item_name:
                skipped_rows_count += 1
                continue
            
            # 1. Match Product
            product = product_cache.get(item_name)
            if not product:
                # Try exact match first, then icontains
                product = Product.objects.filter(name__iexact=item_name).first()
                if not product:
                    product = Product.objects.filter(name__icontains=item_name).first()
                
                if product:
                    product_cache[item_name] = product
            
            if not product:
                skipped_rows_count += 1
                continue
            
            matched_products_count += 1
            
            # 2. Parse Price
            price_str = row.get('Unit price', '0')
            price = self.clean_price(price_str)
            
            # 3. Handle Status (online/local)
            status_val = row.get('Status')
            is_confirmed = (status_val == 'Confirmed')
            
            # 4. Get or Create PartnerProduct
            partner_product, created = PartnerProduct.objects.get_or_create(
                partner=partner,
                product=product,
                defaults={
                    'price': price,
                    'online': is_confirmed,
                    'local': is_confirmed,
                    'is_active': True
                }
            )
            
            if created:
                new_partner_products_count += 1
            else:
                # Update existing PartnerProduct price and status if confirmed
                partner_product.price = price
                partner_product.online = is_confirmed
                partner_product.local = is_confirmed
                partner_product.save()

            # 5. Handle Sizes
            # Check EU, US, UK, BR columns
            size_types = [
                ('Size EU', 'EU'),
                ('Size US', 'USM'),
                ('Size US', 'USW'),
            ]
            
            matching_size = None
            for col, s_type in size_types:
                val = str(row.get(col))
                if val and val != 'None':
                    # Find size associated with the product tables
                    matching_size = Size.objects.filter(
                        table__products=product,
                        type=s_type,
                        value=val
                    ).first()
                    if matching_size:
                        break
            
            if matching_size:
                quantity = 0
                try:
                    quantity = int(row.get('Quantity', 0))
                except:
                    pass
                
                if quantity > 0:
                    pps, pps_created = PartnerProductSize.objects.get_or_create(
                        partner_product=partner_product,
                        size=matching_size,
                        defaults={'quantity': quantity}
                    )
                    if not pps_created:
                        pps.quantity += quantity # Add to existing quantity
                        pps.save()
                    size_updates_count += 1

        return Response({
            "message": "File processed successfully",
            "details": {
                "total_rows": total_rows,
                "matched_products": matched_products_count,
                "new_partner_products": new_partner_products_count,
                "size_updates": size_updates_count,
                "skipped_rows": skipped_rows_count
            }
        }, status=status.HTTP_200_OK)

    def clean_price(self, price_str):
        if not price_str: return Decimal('0.00')
        # Remove currency symbols and spaces
        cleaned = "".join(c for c in str(price_str) if c.isdigit() or c in '.,')
        if not cleaned: return Decimal('0.00')
        
        # Consistent decimal separator
        if ',' in cleaned and '.' in cleaned:
            cleaned = cleaned.replace(',', '')
        elif ',' in cleaned:
            cleaned = cleaned.replace(',', '.')
        
        try:
            return Decimal(cleaned)
        except:
            return Decimal('0.00')
