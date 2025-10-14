from .utils import *
from .models import *
from io import BytesIO
from .serializers import *
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
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['name', 'description', 'brand__name']
    filterset_fields = [ 'sub_category__slug', 'gender', 'brand']
    

    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True).select_related('brand').prefetch_related('images', 'colors')

        # Filter by sub_category if provided
        sub = self.request.query_params.get("sub_category")
        if sub:
            sub_cat = SubCategory.objects.filter(slug=sub).first()
            queryset = queryset.filter(sub_category=sub_cat)
            return queryset
        
        # Filter by gender
        gender = self.request.query_params.get("gender")
        if gender:
            queryset = queryset.filter(gender=gender)

        # Get match param and user's foot scan
        match = self.request.query_params.get("match")
        scan = FootScan.objects.filter(user=self.request.user).first()

        # Sort by match score if requested and scan exists
        if match and match.lower() == "true" and scan:
            # Convert to list for sorting
            products_list = list(queryset)
            products_list.sort(
                key=lambda product: product.match_with_scan(scan)["score"],
                reverse=True
            )
            return products_list

        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        match = self.request.query_params.get("match")
        scan = FootScan.objects.filter(user=self.request.user).first()
        
        context['scan'] = scan
        context['match'] = match and match.lower() == "true"    
        
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
            for label, value in user_info:
                ws[f'A{row}'] = label
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
                ("Width Category", foot_scan.get_width_label()),
                ("Toe Box Category", foot_scan.toe_box_category()),
            ]
            row += 1
            for label, value in summary:
                ws[f'A{row}'] = label
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
        product_id = self.kwargs.get('product_id')
        
        if not product_id:
            return Product.objects.none()

        try:
            product = Product.objects.get(id=product_id, is_active=True)
        except Product.DoesNotExist:
            return Product.objects.none()
        size = product.sizes.all()
        # size_values = Size.objects.filter(table__in=size)
        print(size)
        # Get scan for better suggestions
        scan = FootScan.objects.filter(user=self.request.user).first()
        
        # Base criteria: same sub_category and gender
        queryset = Product.objects.filter(
            is_active=True,
            sub_category=product.sub_category,
            gender=product.gender,
            sizes__in=size

        ).exclude(id=product_id).select_related('brand').prefetch_related('images', 'colors')

        # If scan exists, prioritize products with similar width/toe box
        if scan:
            foot_width_cat = scan.width_category()
            foot_toe_box = scan.toe_box_category()
            
            # Convert to list and sort by relevance
            products_list = list(queryset)
            products_list.sort(
                key=lambda p: (
                    # Prioritize matching width (primary)
                    abs(p.width - foot_width_cat),
                    # Then matching toe box
                    0 if p.toe_box == foot_toe_box else 1,
                    # Then overall match score
                    -p.match_with_scan(scan)["score"]
                )
            )
            return products_list[:20]  # Limit to top 20

        return queryset[:20]
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        scan = FootScan.objects.filter(user=self.request.user).first()
        context['scan'] = scan
        context['match'] = True  # Always show match data for suggestions
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
            # First, get products by sub_category (using slug since you have slug field)
            subcategory_products = Product.objects.filter(sub_category__slug=cat)

            if not subcategory_products.exists():
                return self.empty_paginated_response(request)
                
        except Exception as e:
            return self.empty_paginated_response(request)

        # Build query for each question
        final_queryset = subcategory_products
        
        for i, question_item in enumerate(questions_data):
            question_label = question_item.get("question")
            answer_labels = question_item.get("answers", [])
            
            if not question_label or not answer_labels:
                return self.empty_paginated_response(request)

            # Find the question object
            question_obj = Question.objects.filter(label__icontains=question_label).first()
            if not question_obj:
                return self.empty_paginated_response(request)
            
            # For this question, we need to find products that have AT LEAST ONE of the answers
            question_query = Q()
            valid_answers = 0
            
            for answer_label in answer_labels:
                if answer_label and answer_label.strip():
                    # Check if any products have this question-answer combination
                    answer_match_count = final_queryset.filter(
                        question_answers__question=question_obj,
                        question_answers__answers__label__icontains=answer_label
                    ).count()
                                        
                    if answer_match_count > 0:
                        question_query |= Q(
                            question_answers__question=question_obj,
                            question_answers__answers__label__icontains=answer_label
                        )
                        valid_answers += 1
            
            if valid_answers == 0:
                return self.empty_paginated_response(request)

            # Apply this question's filter to the queryset
            previous_count = final_queryset.count()
            final_queryset = final_queryset.filter(question_query).distinct()
            current_count = final_queryset.count()
            
            if current_count == 0:
                return self.empty_paginated_response(request)
            
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
    

