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
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = CustomLimitPagination    

    # enable filters + search
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['name', 'description', 'brand__name']
    filterset_fields = ['sub_category__slug', 'gender', 'brand']

    # base querysets
    def get_queryset(self):
        """
        Build the queryset dynamically depending on the 'brandName' param.
        Apply additional filters and optional match score sorting.
        """
        # Get only active products that have at least one partner selling them
        queryset = Product.objects.filter(
            partner_prices__isnull=False,  # ensures product is linked to at least one PartnerProduct
            is_active=True
        ).select_related('brand').prefetch_related('images', 'colors').distinct()

        # --- Choose base queryset based on brandName ---
        brand = self.request.query_params.get("brandName")

        if brand:
            queryset = queryset.filter(brand__name__iexact=brand)
        else:
            # No brand requested, exclude Imotana by default
            queryset = queryset.exclude(brand__name__iexact="imotana")

        # --- Extra filters ---
        sub = self.request.query_params.get("sub_category")
        if sub:
            sub_cat = SubCategory.objects.filter(slug=sub).first()
            if sub_cat:
                queryset = queryset.filter(sub_category=sub_cat)

        gender = self.request.query_params.get("gender")
        if gender:
            queryset = queryset.filter(gender=gender)

        # --- Match sorting ---
        match = self.request.query_params.get("match")
        scan = FootScan.objects.filter(user=self.request.user).first()

        if match and match.lower() == "true" and scan:
            products = list(queryset)
            products.sort(
                key=lambda p: p.match_with_scan(scan).get("score", 0),
                reverse=True  # higher score first
            )
            return products

        # Default: order by latest (descending id)
        return queryset.order_by('-id')


    def list(self, request, *args, **kwargs):
        """
        Apply DRF search + filter backends even when get_queryset() returns a list.
        """
        queryset = self.get_queryset()

        # ✅ Apply search and filters manually
        if not isinstance(queryset, list):
            queryset = self.filter_queryset(queryset)

        # ✅ Handle pagination
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
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        sub = request.query_params.get("sub_category")
        gender = request.query_params.get("gender")

        queryset = Product.objects.filter(is_active=True)
        
        if sub:
            queryset = queryset.filter(sub_category=sub)
        
        if gender:
            queryset = queryset.filter(gender=gender)
        
        count = queryset.count()

        return Response({"count": count}, status=200)

class ProductDetailView(generics.RetrieveAPIView):
    serializer_class = ProductDetailsSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Product.objects.filter(is_active=True)
    lookup_field = 'id'

    def get_queryset(self):
        return super().get_queryset().select_related('brand').prefetch_related(
            'images', 'colors'
        )

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
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = CustomLimitPagination

    def get_queryset(self):
        product_id = self.kwargs.get("product_id")

        if not product_id:
            return Product.objects.none()

        try:
            product = Product.objects.get(id=product_id, is_active=True)
        except Product.DoesNotExist:
            return Product.objects.none()

        # ✅ Get all SizeTable IDs linked to this product via sizes ManyToMany
        size_table_ids = product.sizes.values_list('id', flat=True)

        # ✅ Prepare base queryset
        queryset = (
            Product.objects.filter(
                is_active=True,
                sub_category=product.sub_category,
                gender=product.gender,
                sizes__id__in=size_table_ids,  # match same size tables
            )
            .exclude(id=product_id)
            .select_related("brand")
            .prefetch_related("images", "colors")
            .distinct()
        )

        # ✅ Add scan-based ranking (if exists)
        scan = FootScan.objects.filter(user=self.request.user).first()

        if scan:
            foot_width_cat = scan.width_category()
            foot_toe_box = scan.toe_box_category()

            products_list = list(queryset)
            products_list.sort(
                key=lambda p: (
                    abs(getattr(p, "width", 0) - foot_width_cat),
                    0 if getattr(p, "toe_box", None) == foot_toe_box else 1,
                    -p.match_with_scan(scan).get("score", 0),
                )
            )
            return products_list[:20]  # Top 20 matches

        return queryset[:20]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        scan = FootScan.objects.filter(user=self.request.user).first()
        context["scan"] = scan
        context["match"] = True
        return context
           
class ProductQnAFilterAPIView(views.APIView):
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

        # Start with all products in the sub_category
        try:
            # Get products by sub_category slug
            subcategory_products = Product.objects.filter(
                sub_category__slug=cat,
                is_active=True
            ).select_related('brand').prefetch_related('images', 'colors')

            if not subcategory_products.exists():
                return self.empty_paginated_response(request)
                
        except Exception as e:
            return self.empty_paginated_response(request)

        # Build OR query across ALL questions - product matches if it has ANY of the questions
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
                # If question doesn't exist, skip it
                continue
            
            # For this question, build OR query for all answer options
            for answer_key in answer_keys:
                if answer_key and answer_key.strip():
                    # Add to combined OR query
                    combined_query |= Q(
                        question_answers__question=question_obj,
                        question_answers__answers__key=answer_key
                    )
        
        # If no valid query built, return empty
        if not combined_query:
            return self.empty_paginated_response(request)
        
        # Filter products: match ANY of the question/answer combinations
        final_queryset = subcategory_products.filter(combined_query).distinct()
        
        # Final check
        if not final_queryset.exists():
            return self.empty_paginated_response(request)

        # Pagination and serialization
        paginator = self.pagination_class()
        paginated_products = paginator.paginate_queryset(final_queryset, request, view=self)
        serializer = ProductSerializer(paginated_products, many=True)
        
        return paginator.get_paginated_response(serializer.data)

    # Helper method for empty response
    def empty_paginated_response(self, request):
        paginator = self.pagination_class()
        empty_queryset = Product.objects.none()
        paginated = paginator.paginate_queryset(empty_queryset, request, view=self)
        serializer = ProductSerializer(paginated, many=True)
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
        size_id = request.data.get('size_id')
        color_id = request.data.get('color_id')

        if not product_id or action not in ['add', 'remove']:
            return Response({"error": "Invalid request. Provide product_id and action (add/remove)."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            product = Product.objects.get(id=product_id, is_active=True)
        except Product.DoesNotExist:
            return Response({"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

        if action == 'add':
            if not price:
                return Response({"error": "Price is required when adding a product."}, status=status.HTTP_400_BAD_REQUEST)
            
            if not size_id:
                return Response({"error": "Size is required when adding a product."}, status=status.HTTP_400_BAD_REQUEST)
            
            if not color_id:
                return Response({"error": "Color is required when adding a product."}, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                size = SizeTable.objects.get(id=size_id)
            except SizeTable.DoesNotExist:
                return Response({"error": "Size not found."}, status=status.HTTP_404_NOT_FOUND)
            
            try:
                color = Color.objects.get(id=color_id)
            except Color.DoesNotExist:
                return Response({"error": "Color not found."}, status=status.HTTP_404_NOT_FOUND)
            
            # Create or update PartnerProduct entry
            partner_product, created = PartnerProduct.objects.update_or_create(
                partner=request.user,
                product=product,
                size=size,
                color=color,
                defaults={
                    'price': price,
                    'discount': discount,
                    'stock_quantity': stock_quantity,
                    'is_active': True
                }
            )
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

