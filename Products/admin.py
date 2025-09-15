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
    search_fields = ["color", "code"]  # <-- allow searching by both

class CategoryAdmin(ModelAdmin):
    list_display = ('name_de', 'name_it')
    search_fields = ('name_de', 'name_it')

class SubCategoryAdmin(ModelAdmin):
    list_display = ('name_de', 'name_it', 'category')
    search_fields = ('name_de', 'name_it', 'category')
    list_filter = ('category',)

# --- Inline for product images ---
class ProductImageInline(TabularInline):
    model = ProductImage
    extra = 1
    fields = ["image", "is_primary"]

@admin.register(Size)
class Sizeadmin(ModelAdmin):
    search_fields = ('type','size')

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
        'sizes', 'price', 'discount'
    )
    list_filter = (
        'is_active', 'main_category', 'sub_category',
        'sizes', 'width', 'toe_box', 'brand'
    )
    autocomplete_fields =['colors', 'sizes']
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
        
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "partner":
            if request.user.is_superuser:
                # Superuser can see all partner accounts
                kwargs["queryset"] = User.objects.filter(role="partner")
            elif hasattr(request.user, "role") and request.user.role == "partner":
                # Partner can only see (and select) themselves
                kwargs["queryset"] = User.objects.filter(id=request.user.id)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

class OrderAdmin(ModelAdmin):
    list_display = ('id',"order_number", "status", "total_amount",'created_at')
    search_fields = ("order_number", "customer__email", "partner__email",'created_at')
    list_filter = ("status",)
    autocomplete_fields = ['customer','partner','products']
    readonly_fields = ["order_number", "customer", "partner", "products",
                       "shipping_address", "billing_address", "total_amount",
                       'created_at', "notes"]


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
admin.site.register(FootScan,ModelAdmin)

from django.contrib import admin
from .models import Favourite, Product, User # Make sure to import all relevant models

@admin.register(Favourite)
class FavouriteAdmin(ModelAdmin):
    """
    Admin configuration for the Favourite model.
    """
    # Fields to display in the main list view of the admin
    list_display = ('user', 'display_products', 'created_at')

    # Add a search bar to search by user's username
    search_fields = ('user__username',)

    # For a better UI to select products (provides a two-box selection interface)
    filter_horizontal = ('product',)

    # Fields that should not be editable in the admin
    readonly_fields = ('created_at',)
    autocomplete_fields = ['product']

    def display_products(self, obj):
        """
        Creates a string of the first 5 product names for the list_display.
        This avoids querying and displaying potentially thousands of products.
        """
        products = obj.product.all()[:5]
        return ", ".join([p.name_de for p in products]) + ('...' if obj.product.count() > 5 else '')

    # Give the custom method a user-friendly column header
    display_products.short_description = 'Favourite Products'