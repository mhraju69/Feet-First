from .models import *
from Others.models import *
from django.contrib import admin
from unfold.admin import ModelAdmin
from unfold.admin import TabularInline
from dal import autocomplete
from django import forms
import json
from django.db.models import Q

class AnswerAutocomplete(autocomplete.Select2QuerySetView):
    """
    Custom autocomplete for Answer field
    Question select করলে শুধু সেই question এর answers দেখাবে
    """
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Answer.objects.none()

        qs = Answer.objects.all()

        question_id = self.forwarded.get('question', None)
        
        if question_id:
            qs = qs.filter(question_id=question_id)

        if self.q:
            qs = qs.filter(label__icontains=self.q)

        return qs.order_by('label')

class ProductQuestionAnswerForm(forms.ModelForm):
    class Meta:
        model = ProductQuestionAnswer
        fields = '__all__'
        widgets = {
            'answers': autocomplete.ModelSelect2Multiple(
                url='answer-autocomplete',
                forward=['question'],  
            )
        }

class ProductQuestionAnswerInline(TabularInline):
    model = ProductQuestionAnswer
    form = ProductQuestionAnswerForm  
    extra = 1
    autocomplete_fields = ['question']  
    
    class Media:
        css = {
            'all': ('admin/css/custom_select2.css',)  
        }

class ProductImageInline(TabularInline):
    model = ProductImage
    extra = 1
    fields = ["image"]

class SizeInline(TabularInline):
    model = Size
    extra = 1

class SubCategoryAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return SubCategory.objects.none()
        
        qs = SubCategory.objects.all()
        
        # Get the forwarded category value from the main_category field
        category_id = self.forwarded.get('main_category', None)
        
        if category_id:
            qs = qs.filter(category_id=category_id)
        
        if self.q:
            qs = qs.filter(name__icontains=self.q)
        
        return qs.order_by('name')
    
class ProductSubcategoryForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'
        widgets = {
            'sub_category': autocomplete.ModelSelect2(
                url='subcategory-autocomplete',
                forward=['main_category'],
                attrs={
                    'data-placeholder': 'Select a subcategory...',
                    'data-minimum-input-length': 0,
                }
            ),
        }
        
@admin.register(Color)
class ColorAdmin(ModelAdmin):
    list_display = ('color', 'hex_code')
    search_fields = ["color", 'hex_code']

@admin.register(Features)
class FeaturesAdmin(ModelAdmin):
    search_fields = ["text"]

@admin.register(SizeTable)
class SizeTableAdmin(ModelAdmin):
    list_display = ('name', 'brand')
    search_fields = ('brand',)
    inlines = [SizeInline]
    autocomplete_fields = ['brand']

@admin.register(ProductQuestionAnswer)
class ProductQuestionAnswerAdmin(ModelAdmin):
    list_display = ('product', 'question')
    search_fields = ('product__name', 'question__label')
    autocomplete_fields = ['product', 'question', 'answers']

@admin.register(Question)
class ShoesQuestionAdmin(ModelAdmin):
    readonly_fields = ('key', 'label')
    list_display = ["label"]
    search_fields = ["label"]
    # has_add_permission = lambda self, request, obj=None: False
    # has_delete_permission = lambda self, request, obj=None: False

@admin.register(Answer)
class ShoesAnswerAdmin(ModelAdmin):
    list_display = ["label", "question"]
    search_fields = ["label", "question__label"]
    readonly_fields = ("question", 'key', 'label')
    list_filter = ["label"]
    # has_add_permission = lambda self, request, obj=None: False
    # has_delete_permission = lambda self, request, obj=None: False

@admin.register(Product)
class ProductAdmin(ModelAdmin):
    form = ProductSubcategoryForm
    list_display = (
        'name',
        'main_category', 'sub_category', 'gender',
        'is_active'
    )
    search_fields = ('name',)
    list_filter = (
        'gender', 'is_active', 'main_category', 'sub_category',
        'width', 'toe_box', 'brand', 'colors',
    )
    autocomplete_fields = ['colors', 'brand','features','sizes']
    inlines = [ProductImageInline, ProductQuestionAnswerInline]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        if hasattr(request.user, "role") and request.user.role == 'partner':
            return qs.filter(partner=request.user)
        return qs.none()

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if obj is None:
            return True
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

    def save_model(self, request, obj, form, change):
        if not obj.pk and hasattr(request.user, "role") and request.user.role == 'partner':
            obj.partner = request.user
        super().save_model(request, obj, form, change)
        
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "partner":
            if request.user.is_superuser:
                kwargs["queryset"] = User.objects.filter(role="partner")
            elif hasattr(request.user, "role") and request.user.role == "partner":
                kwargs["queryset"] = User.objects.filter(id=request.user.id)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

@admin.register(Favorite)
class FavoriteAdmin(ModelAdmin):
    list_display = ('user',)
    search_fields = ('user__email',)
    readonly_fields = ('user','products')
    autocomplete_fields = ['products']
    has_add_permission = lambda self, request, obj=None: False
    # has_delete_permission = lambda self, request, obj=None: False

@admin.register(PartnerProduct)
class PartnerProductAdmin(ModelAdmin):
    has_add_permission = lambda self, request, obj=None: False
    has_delete_permission = lambda self, request, obj=None: False
