from .utils import *
from .models import *
from io import BytesIO
from .serializers import *
from core.permission import *
from datetime import datetime
from openpyxl import Workbook
from django.db.models import Q
from rest_framework import filters
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from openpyxl.styles import Font, PatternFill, Alignment
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, generics, views, status

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
        # Get only active partner products with stock
        queryset = PartnerProduct.objects.filter(
            is_active=True,
            stock_quantity__gt=0,
            product__is_active=True
        ).select_related(
            'product', 'product__brand', 'product__sub_category',
            'partner'
        ).prefetch_related('product__images', 'size', 'color')
        
        # DEBUG: Print queryset count
        print(f"DEBUG: Initial queryset count: {queryset.count()}")
        if queryset.count() == 0:
            print("DEBUG: No products found! Checking conditions...")
            print(f"  - Total PartnerProducts: {PartnerProduct.objects.count()}")
            print(f"  - Active: {PartnerProduct.objects.filter(is_active=True).count()}")
            print(f"  - With stock: {PartnerProduct.objects.filter(stock_quantity__gt=0).count()}")
            print(f"  - Product active: {PartnerProduct.objects.filter(product__is_active=True).count()}")

        # --- Brand filter ---
        brand = self.request.query_params.get("brandName")
        if brand:
            queryset = queryset.filter(product__brand__name__iexact=brand)
            print(f"DEBUG: After brand filter '{brand}': {queryset.count()}")
        else:
            # No brand requested, exclude Imotana by default
            queryset = queryset.exclude(product__brand__name__iexact="imotana")
            print(f"DEBUG: After excluding 'imotana': {queryset.count()}")

        # --- Sub category filter ---
        sub = self.request.query_params.get("sub_category")
        if sub:
            queryset = queryset.filter(product__sub_category__slug=sub)
            print(f"DEBUG: After sub_category filter '{sub}': {queryset.count()}")

        # --- Gender filter ---
        gender = self.request.query_params.get("gender")
        if gender:
            queryset = queryset.filter(product__gender=gender)
            print(f"DEBUG: After gender filter '{gender}': {queryset.count()}")

        # --- Size filter ---
        size_id = self.request.query_params.get("size_id")
        if size_id:
            queryset = queryset.filter(size__id=size_id)
            print(f"DEBUG: After size filter '{size_id}': {queryset.count()}")

        # --- Color filter ---
        color_id = self.request.query_params.get("color_id")
        if color_id:
            queryset = queryset.filter(color__id=color_id)
            print(f"DEBUG: After color filter '{color_id}': {queryset.count()}")

        # --- Partner filter ---
        partner_id = self.request.query_params.get("partner_id")
        if partner_id:
            queryset = queryset.filter(partner_id=partner_id)
            print(f"DEBUG: After partner filter '{partner_id}': {queryset.count()}")

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
        print(f"DEBUG: Final queryset count: {queryset.count()}")
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
        return context

class ProductsCountView(views.APIView):
    """Count available partner products (multi-vendor)"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        sub = request.query_params.get("sub_category")
        gender = request.query_params.get("gender")

        queryset = PartnerProduct.objects.filter(
            is_active=True, 
            stock_quantity__gt=0,
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
        ).prefetch_related('product__images', 'product__colors', 'product__features', 'size', 'color')

    def get_serializer_context(self):
        context = super().get_serializer_context()
        scan = FootScan.objects.filter(user=self.request.user).first()
        context['scan'] = scan
        return context

class FootScanListCreateView(generics.ListCreateAPIView):
    """List all foot scans or create a new one."""
    serializer_class = FootScanSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return FootScan.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class DownloadFootScanExcel(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            foot_scan = get_object_or_404(FootScan, user=request.user)

        except Exception as e:
            return Response({"error": f"FootScan no found"}, status=500)

        try:
            wb = Workbook()
            ws = wb.active
            ws.title = f"FootScan_of_{request.user.email}"

            header_font = Font(bold=True, size=12)
            header_fill = PatternFill(start_color="C0C0C0", end_color="C0C0C0", fill_type="solid")
            header_alignment = Alignment(horizontal="center", vertical="center")

            # Title
            ws.merge_cells('A1:B1')
            ws['A1'] = f"Foot Scan Report - Email: {request.user.email}"
            ws['A1'].font = Font(bold=True, size=14)
            ws['A1'].alignment = Alignment(horizontal="center")

            # User Info
            ws['A3'] = "User Information"
            ws['A3'].font = Font(bold=True, size=12)

            user_info = [
                ("Email", foot_scan.user.email),
                ("Scan Date", foot_scan.created_at.strftime("%d-%m-%Y %H:%M:%S")),
                ("Foot Type", foot_scan.get_foot_type()),
            ]
            row = 4
            for key, value in user_info:
                ws[f'A{row}'] = key
                ws[f'B{row}'] = value
                row += 1

            # Measurements
            row += 1
            ws[f'A{row}'] = "Foot Measurements (mm)"
            ws[f'A{row}'].font = Font(bold=True, size=12)
            ws[f'A{row}'].fill = header_fill
            ws[f'A{row}'].alignment = header_alignment
            ws.merge_cells(f'A{row}:C{row}')

            row += 1
            headers = ["Measurement Type", "Left Foot", "Right Foot"]
            for col, header in enumerate(headers, 1):
                cell = ws.cell(row=row, column=col)
                cell.value = header
                cell.font = header_font
                cell.fill = header_fill
                cell.alignment = header_alignment

            measurements = [
                ("Length (mm)", float(foot_scan.left_length), float(foot_scan.right_length)),
                ("Width (mm)", float(foot_scan.left_width), float(foot_scan.right_width)),
                ("Arch Index", float(foot_scan.left_arch_index) if foot_scan.left_arch_index else "N/A",
                                float(foot_scan.right_arch_index) if foot_scan.right_arch_index else "N/A"),
                ("Heel Angle (°)", float(foot_scan.left_heel_angle) if foot_scan.left_heel_angle else "N/A",
                                    float(foot_scan.right_heel_angle) if foot_scan.right_heel_angle else "N/A"),
            ]
            row += 1
            for measurement in measurements:
                for col, value in enumerate(measurement, 1):
                    ws.cell(row=row, column=col, value=value)
                row += 1

            # Summary
            row += 2
            ws[f'A{row}'] = "Summary & Analysis"
            ws[f'A{row}'].font = Font(bold=True, size=12)
            ws[f'A{row}'].fill = header_fill
            
            summary = [
                ("Average Length", f"{foot_scan.average_length():.2f} mm"),
                ("Average Width", f"{foot_scan.average_width():.2f} mm"),
                ("Maximum Length (for sizing)", f"{foot_scan.max_length():.2f} mm"),
                ("Maximum Width (for sizing)", f"{foot_scan.max_width():.2f} mm"),
                ("Width Category", foot_scan.get_width_key()),
                ("Toe Box Category", foot_scan.toe_box_category()),
            ]
            row += 1
            for key, value in summary:
                ws[f'A{row}'] = key
                ws[f'B{row}'] = value
                row += 1

            ws.column_dimensions['A'].width = 30
            ws.column_dimensions['B'].width = 25
            ws.column_dimensions['C'].width = 25

            output = BytesIO()
            wb.save(output)
            output.seek(0)

            filename = f"FootScan_{request.user.email}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

            from django.http import HttpResponse
            response = HttpResponse(
                output.getvalue(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response

        except Exception as e:
            return Response(
                {"detail": f"Error generating Excel file: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class FavoriteUpdateView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        favorite, created = Favorite.objects.get_or_create(user=request.user)
        serializer = FavoriteSerializer(favorite, context={'request': request, 'scan': None, 'match': False})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        favorite, created = Favorite.objects.get_or_create(user=request.user)

        product_id = request.data.get('product_id')
        action = request.data.get('action')

        if not product_id or action not in ['add', 'remove']:
            return Response({"error": "Invalid request."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            product = Product.objects.get(id=product_id, is_active=True)
        except Product.DoesNotExist:
            return Response({"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

        if action == 'add':
            favorite.products.add(product)
            message = "Product added to favorites"
        else:
            favorite.products.remove(product)
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
            stock_quantity__gt=0,
            product__is_active=True,
            product__sub_category=product.sub_category,
            product__gender=product.gender,
            product__sizes__id__in=size_table_ids,  # match same size tables
        ).exclude(
            id=partner_product_id
        ).select_related(
            'product', 'product__brand', 'product__sub_category',
            'partner'
        ).prefetch_related('product__images', 'size', 'color').distinct()

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
            stock_quantity__gt=0,
            product__is_active=True,
            product__sub_category__slug=cat
        ).filter(combined_query).select_related(
            'product', 'product__brand', 'product__sub_category',
            'partner'
        ).prefetch_related('product__images', 'size', 'color').distinct()
        
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
            context={'request': request, 'scan': scan}
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
        return PartnerProduct.objects.filter(partner=self.request.user).select_related('product', 'product__brand').prefetch_related('product__images', 'product__colors')  

class ApprovedPartnerProductUpdateView(views.APIView):
    """View to add or remove products from partner's inventory"""
    permission_classes = [permissions.IsAuthenticated, IsPartner]

    def patch(self, request, *args, **kwargs):
        product_id = kwargs.get('product_id')
        action = kwargs.get('action')
        price = request.data.get('price')
        discount = request.data.get('discount', None)
        stock_quantity = request.data.get('stock_quantity', 0)
        size_ids = request.data.get('sizes', [])
        color_ids = request.data.get('colors', [])

        if not product_id or action not in ['add', 'remove']:
            return Response({"error": "Invalid request. Provide product_id and action (add/remove)."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            product = Product.objects.get(id=product_id, is_active=True)
        except Product.DoesNotExist:
            return Response({"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

        if action == 'add':
            if not price:
                return Response({"error": "Price is required when adding a product."}, status=status.HTTP_400_BAD_REQUEST)
            
            if not size_ids or not isinstance(size_ids, list):
                return Response({"error": "Size IDs (as list) are required when adding a product."}, status=status.HTTP_400_BAD_REQUEST)
            
            if not color_ids or not isinstance(color_ids, list):
                return Response({"error": "Color IDs (as list) are required when adding a product."}, status=status.HTTP_400_BAD_REQUEST)
            
            # Validate sizes
            sizes = SizeTable.objects.filter(id__in=size_ids)
            if sizes.count() != len(size_ids):
                return Response({"error": "One or more sizes not found."}, status=status.HTTP_404_NOT_FOUND)
            
            # Validate colors
            colors = Color.objects.filter(id__in=color_ids)
            if colors.count() != len(color_ids):
                return Response({"error": "One or more colors not found."}, status=status.HTTP_404_NOT_FOUND)
            
            # Create or update PartnerProduct entry
            partner_product, created = PartnerProduct.objects.get_or_create(
                partner=request.user,
                product=product,
                defaults={
                    'price': price,
                    'discount': discount,
                    'stock_quantity': stock_quantity,
                    'is_active': True
                }
            )
            
            # If not created, update the fields
            if not created:
                partner_product.price = price
                partner_product.discount = discount
                partner_product.stock_quantity = stock_quantity
                partner_product.is_active = True
                partner_product.save()
            
            # Set ManyToMany relationships
            partner_product.size.set(sizes)
            partner_product.color.set(colors)
            
            message = "Product added to inventory" if created else "Product updated in inventory"
        else:  # action == 'remove'
            # Delete PartnerProduct entry
            deleted_count, _ = PartnerProduct.objects.filter(
                partner=request.user,
                product=product
            ).delete()
            
            if deleted_count == 0:
                return Response({"error": "Product not found in your inventory."}, status=status.HTTP_404_NOT_FOUND)
            
            message = "Product removed from inventory"

        return Response({"message": message}, status=status.HTTP_200_OK)

