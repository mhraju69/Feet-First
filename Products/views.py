from .utils import *
from .models import *
from io import BytesIO
from .serializers import *
from datetime import datetime
from openpyxl import Workbook
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import permissions,generics,views,status
from openpyxl.styles import Font, PatternFill, Alignment
from rest_framework.pagination import PageNumberPagination

class CustomLimitPagination(PageNumberPagination):
    page_size = 10  # default page size
    page_size_query_param = 'limit'  # frontend can send ?limit=20
    max_page_size = 20  # optional maximum limit

class ProductListView(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = CustomLimitPagination  # add pagination

    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True)
        sub : str = self.request.query_params.get("sub_category")
        
        if sub:
            s = queryset.filter(sub_category=sub)
            queryset = s
            
        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        scan_id = self.request.query_params.get("scan_id")
        
        if scan_id:
            scan = FootScan.objects.filter(user=self.request.user, id=scan_id).first()
            if not scan:
                scan = FootScan.objects.filter(user=self.request.user).first()
            context['scan'] = scan
            
        return context
    
class ProductsCountView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        sub = request.query_params.get("sub_category")

        if sub:
            # Filter by sub_category if provided
            count = Product.objects.filter(is_active=True, sub_category=sub).count()
        else:
            # Otherwise count all active products
            count = 0

        return Response({"count": count}, status=200)
    
class ProductDetailView(generics.RetrieveAPIView):
    serializer_class = ProductDetailsSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Product.objects.filter(is_active = True)
    lookup_field = 'id'
    def get_serializer_context(self):
        context = super().get_serializer_context()
        scan_id = self.request.query_params.get("scan_id")

        if scan_id:
            try:
                # Get the scan object
                scan = get_object_or_404(FootScan,user=self.request.user, id=scan_id)
                context['scan'] = scan
            except :
                scan = FootScan.objects.filter(user=self.request.user).first()
                context['scan'] = scan
                
        return context

class FootScanListCreateView(generics.ListCreateAPIView):
    """List all foot scans or create a new one."""
    serializer_class = FootScanSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Customers only see their own scans
        user = self.request.user
        if user.role == "customer":
            return FootScan.objects.filter(user=user)
        # Admins/staff see all
        return FootScan.objects.all()

class FootScanDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a foot scan."""
    serializer_class = FootScanSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == "customer":
            return FootScan.objects.filter(user=user)
        return FootScan.objects.all()

class DownloadFootScanExcel(views.APIView):
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [ExcelRenderer]   # force Excel output

    def get(self, request, *args, **kwargs):
        try:
            scan_id = self.kwargs.get('scan_id')
            if not scan_id:
                return Response({"detail": "Scan ID is required"}, status=400)
            
            foot_scan = get_object_or_404(FootScan, id=scan_id, user=request.user)

        except Exception as e:
            return Response({"detail": f"Error retrieving FootScan: {str(e)}"}, status=500)

        try:
            # ----- Excel workbook -----
            wb = Workbook()
            ws = wb.active
            ws.title = f"FootScan_{scan_id}"

            header_font = Font(bold=True, size=12)
            header_fill = PatternFill(start_color="C0C0C0", end_color="C0C0C0", fill_type="solid")
            header_alignment = Alignment(horizontal="center", vertical="center")

            # Title row
            ws.merge_cells('A1:B1')
            ws['A1'] = f"Foot Scan Report - ID: {scan_id}"
            ws['A1'].font = Font(bold=True, size=14)
            ws['A1'].alignment = Alignment(horizontal="center")

            # User Info
            ws['A3'] = "User Information"
            ws['A3'].font = Font(bold=True, size=12)

            user_info = [
                ("Email", foot_scan.user.email),
                ("Scan Date", foot_scan.created_at.strftime("%d-%m-%Y %H:%M:%S")),
            ]
            row = 4
            for label, value in user_info:
                ws[f'A{row}'] = label
                ws[f'B{row}'] = value
                row += 1

            # Measurements Header
            row += 1
            ws[f'A{row}'] = "Foot Measurements (mm)"
            ws[f'A{row}'].font = Font(bold=True, size=12)
            ws[f'A{row}'].fill = header_fill
            ws[f'A{row}'].alignment = header_alignment
            ws.merge_cells(f'A{row}:C{row}')

            # Table headers
            row += 1
            headers = ["Measurement Type", "Left Foot", "Right Foot"]
            for col, header in enumerate(headers, 1):
                cell = ws.cell(row=row, column=col)
                cell.value = header
                cell.font = header_font
                cell.fill = header_fill
                cell.alignment = header_alignment

            # Data
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
            ws[f'A{row}'] = "Summary"
            ws[f'A{row}'].font = Font(bold=True, size=12)
            ws[f'A{row}'].fill = header_fill
            summary = [
                ("Average Length", f"{foot_scan.average_length():.2f} mm"),
                ("Average Width", f"{foot_scan.average_width():.2f} mm"),
                ("Maximum Length", f"{foot_scan.max_length():.2f} mm"),
                ("Maximum Width", f"{foot_scan.max_width():.2f} mm"),
            ]
            row += 1
            for label, value in summary:
                ws[f'A{row}'] = label
                ws[f'B{row}'] = value
                row += 1

            ws.column_dimensions['A'].width = 25
            ws.column_dimensions['B'].width = 20
            ws.column_dimensions['C'].width = 20

            # Save to BytesIO buffer
            output = BytesIO()
            wb.save(output)
            output.seek(0)

            filename = f"FootScan_{scan_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

            # Use DRF Response with our renderer
            headers = {
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
            return Response(output.getvalue(), headers=headers, content_type=ExcelRenderer.media_type)

        except Exception as e:
            return Response({"detail": f"Error generating Excel file: {str(e)}"},status=status.HTTP_404_NOT_FOUND)
        
class FavoriteUpdateView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        favorite, created = Favorite.objects.get_or_create(user=request.user)
        serializer = FavoriteSerializer(favorite)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, *args, **kwargs):

        # Get or create the Favorite object for this user
        favorite, created = Favorite.objects.get_or_create(user=request.user)

        # Extract product_id and action from request data
        product_id = request.data.get('product_id')
        action = request.data.get('action')

        if not product_id or action not in ['add', 'remove']:
            return Response({"detail": "Invalid request."}, status=status.HTTP_400_BAD_REQUEST)

        # Validate the product exists and is active
        try:
            product = Product.objects.get(id=product_id, is_active=True)
        except Product.DoesNotExist:
            return Response({"detail": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

        # Perform add or remove
        if action == 'add':
            favorite.products.add(product)
        else:  # remove
            favorite.products.remove(product)

        # Serialize and return the updated favorite object
        serializer = FavoriteSerializer(favorite)
        return Response(serializer.data, status=status.HTTP_200_OK)

