from django.contrib import admin
from .models import *
from unfold.admin import ModelAdmin
# Register your models here.
class SizeAdmin(ModelAdmin):
    list_display = ('size', 'details')
    search_fields = ('size',)

class WidthAdmin(ModelAdmin):
    list_display = ('width', 'details'  )
    search_fields = ('width',)

class CategoryAdmin(ModelAdmin):
    list_display = ('name_de', 'name_it')
    search_fields = ('name_de', 'name_it')

class SubCategoryAdmin(ModelAdmin):
    list_display = ('name_de', 'name_it', 'category')
    search_fields = ('name_de', 'name_it', 'category')
    list_filter = ('category',)

class PdfFileAdmin(ModelAdmin):
    list_display = ('user', 'pdf_file', 'uploaded_at')
    list_filter = ('user',)
# admin.site.register(Category,CategoryAdmin)
# admin.site.register(SubCategory,SubCategoryAdmin)

@admin.register(Product)
class ProductAdmin(ModelAdmin):
    list_display = ('name_de', 'name_it', 'price', 'discount', 'stock_quantity', 'is_active', 'brand', "category")
    search_fields = ('name_de', 'name_it', 'brand', 'category', 'price', 'discount', 'stock_quantity')
    list_filter = ('is_active', 'category')

    # Row-level restriction
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        if request.user.role == 'partner':
            # Example: only products assigned to this partner
            # Make sure you have a 'partner' field in Product model
            return qs.filter(partner=request.user)
        return qs

    # Restrict change permission similarly
    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if obj is None:
            return True  # needed for list view
        if request.user.role == 'partner':
            return obj.partner == request.user
        return False

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if obj is None:
            return False
        if request.user.role == 'partner':
            return obj.partner == request.user
        return False

    def has_view_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if obj is None:
            return True
        if request.user.role == 'partner':
            return obj.partner == request.user
        return False
    

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("order_number", "customer", "partner", "status", "total_amount")
    search_fields = ("order_number", "customer__email", "partner__email")
    list_filter = ("status",)

    # Row-level restriction
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        # Partner can only see orders where he is the partner
        if request.user.role == 'partner':
            return qs.filter(partner=request.user)
        # Customers can only see their own orders (optional)
        if request.user.role == 'customer':
            return qs.filter(customer=request.user)
        return qs

    # Restrict edit permission similarly
    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if obj is None:
            return True  # Needed to show list view
        if request.user.role == 'partner':
            return obj.partner == request.user
        if request.user.role == 'customer':
            return obj.customer == request.user
        return False

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if obj is None:
            return False
        if request.user.role == 'partner':
            return obj.partner == request.user
        if request.user.role == 'customer':
            return obj.customer == request.user
        return False

    def has_view_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if obj is None:
            return True
        if request.user.role == 'partner':
            return obj.partner == request.user
        if request.user.role == 'customer':
            return obj.customer == request.user
        return False
    



    
admin.site.register(AvailableSize,SizeAdmin)
admin.site.register(AvailableWidth,WidthAdmin)
admin.site.register(PdfFile,PdfFileAdmin)