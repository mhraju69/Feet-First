from .models import *
from Others.models import *
from django.contrib import admin
from unfold.admin import ModelAdmin
from unfold.admin import TabularInline
from dal import autocomplete
from django import forms
import json
# Register your models here.
    
class ColorAdmin(ModelAdmin):
    list_display = ('color', 'hex_code'  )
    search_fields = ["color",'hex_code']  # <-- allow searching by both

class ProductImageInline(TabularInline):
    model = ProductImage
    extra = 1
    fields = ["image",]

class SizeInline(TabularInline):
    model = Size
    extra = 1

@admin.register(SizeTable)
class SizeTableAdmin(ModelAdmin):
    list_display = ('name','brand',)
    search_fields = ('brand',)
    inlines = [SizeInline]
    autocomplete_fields = ['brand']

@admin.register(ProductQuestionAnswer)
class ProductQuestionAnswerAdmin(ModelAdmin):
    list_display = ('product', 'question',)
    search_fields = ('product__name', 'question__label',)
    autocomplete_fields = ['product', 'question', 'answers']

class ProductQuestionAnswerInline(TabularInline):
    model = ProductQuestionAnswer
    extra = 1
    autocomplete_fields = ['question', 'answers']
    # filter_horizontal = ("answers",)  # Multi-select answers

@admin.register(ShoesQuestion)
class ShoesQuestionAdmin(ModelAdmin):
    readonly_fields = ('key','label',)
    list_display = ["label"]
    search_fields = ["label",]
    has_add_permission = lambda self, request, obj=None: False
    has_delete_permission = lambda self, request, obj=None: False  # Prevent deletion

@admin.register(ShoesAnswer)
class ShoesAnswerAdmin(ModelAdmin):
    list_display = ["label", "question"]
    search_fields = ["label", "question__label"]
    readonly_fields = ( "question",'key','label',)
    has_add_permission = lambda self, request, obj=None: False
    has_delete_permission = lambda self, request, obj=None: False  

class ProductAdmin(ModelAdmin):
    list_display = (
        'name',
        'main_category', 'sub_category', 'gender',
        'price', 'stock_quantity',
        'is_active'
    )
    search_fields = (
        'name',
    )
    list_filter = (
        'gender','is_active', 'main_category', 'sub_category',
        'width', 'toe_box', 'brand','colors',
    )
    autocomplete_fields = ['colors','sizes', 'brand',]
    inlines = [ProductImageInline, ProductQuestionAnswerInline]


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

class FavoriteAdmin(ModelAdmin):
    list_display = ('user', )
    search_fields = ('user__email',)
    # readonly_fields = ('user','products')
    autocomplete_fields = ['products']

admin.site.register(Product,ProductAdmin)
admin.site.register(Color,ColorAdmin)
admin.site.register(FootScan,ModelAdmin)
admin.site.register(Favorite,FavoriteAdmin)
