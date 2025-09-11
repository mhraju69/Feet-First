from .models import *
from django.contrib import admin
from unfold.admin import ModelAdmin
from django.utils.html import format_html
from django import forms
from unfold.admin import TabularInline
from django.utils.safestring import mark_safe
from django.forms.widgets import ClearableFileInput
# Register your models here.

class ColorAdmin(ModelAdmin):
    list_display = ('color', 'details'  )
    search_fields = ('color',)

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


# --- Inline for product images ---
class ProductImageInline(TabularInline):
    model = ProductImage
    extra = 1
    fields = ["image", "is_primary"]


# --- Product Admin ---

class ProductAdmin(ModelAdmin):
    list_display = (
        'name_de', 'name_it', 'brand',
        'main_category', 'sub_category',
        'price', 'stock_quantity',
        'is_active'
    )
    search_fields = (
        'name_de', 'name_it', 'brand',
        'main_category', 'sub_category',
        'size_value', 'price', 'discount'
    )
    list_filter = (
        'is_active', 'main_category', 'sub_category',
        'size_system', 'width_category', 'toe_box', 'brand'
    )

    inlines = [ProductImageInline]

    # Row-level restriction
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        if hasattr(request.user, "role") and request.user.role == 'partner':
            return qs.filter(partner=request.user)
        return qs.none()

    # Restrict change permission
    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if obj is None:
            return True  # needed for list view
        if hasattr(request.user, "role") and request.user.role == 'partner':
            return obj.partner == request.user
        return False

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if obj is None:
            return False
        if hasattr(request.user, "role") and request.user.role == 'partner':
            return obj.partner == request.user
        return False

    def has_view_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if obj is None:
            return True
        if hasattr(request.user, "role") and request.user.role == 'partner':
            return obj.partner == request.user
        return False

    # Automatically assign partner on save
    def save_model(self, request, obj, form, change):
        if not obj.pk and hasattr(request.user, "role") and request.user.role == 'partner':
            obj.partner = request.user
        super().save_model(request, obj, form, change)


class OrderAdmin(ModelAdmin):
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

admin.site.register(Product,ProductAdmin)
admin.site.register(Order,OrderAdmin)
admin.site.register(Color,ColorAdmin)
admin.site.register(PdfFile,PdfFileAdmin)
admin.site.register(FootScan,ModelAdmin)