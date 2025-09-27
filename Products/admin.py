from .models import *
from Questions.models import *
from django.contrib import admin
from unfold.admin import ModelAdmin
from unfold.admin import TabularInline
from dal import autocomplete
from django import forms
# Register your models here.

class ProductQnAForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['question', 'answers']
        widgets = {
            'answers': autocomplete.ModelSelect2Multiple(
                url='answer-autocomplete',
                forward=['question'],
                attrs={  
                        'style': 'border: none; outline: none; box-shadow: none; background-color: transparent;',
                        'class': 'form-control',
                        'placeholder': 'Select answers',
                }
            )
        }

class AnswerAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Ans.objects.all()
        question_id = self.forwarded.get('question', None)
        if question_id:
            qs = qs.filter(parent_id=question_id)
        return qs
    
class ColorAdmin(ModelAdmin):
    list_display = ('color', 'details'  )
    search_fields = ["color"]  # <-- allow searching by both

class ProductImageInline(TabularInline):
    model = ProductImage
    extra = 1
    fields = ["image", "is_primary"]

class SizeInline(TabularInline):
    model = Size
    extra = 1

class ProductQuestionAnswerInline(TabularInline):
    model = Question
    extra = 1  # Number of empty forms
    form = ProductQnAForm
    autocomplete_fields = ['question', 'answers'] 
    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if db_field.name == "answer":
            if 'question' in request.GET:
                kwargs["queryset"] = Ans.objects.filter(parent_id=request.GET['question'])
            else:
                kwargs["queryset"] = Ans.objects.none()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
        

@admin.register(SizeTable)
class SizeTableAdmin(ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    inlines = [SizeInline]

class ProductAdmin(ModelAdmin):
    list_display = (
        'name',
        'main_category', 'sub_category', 'gender',
        'price', 'stock_quantity',
        'is_active'
    )
    search_fields = (
        'name', 'brand',
        'main_category', 'sub_category',
    )
    list_filter = (
        'gender','is_active', 'main_category', 'sub_category',
        'width', 'toe_box', 'brand'
    )
    autocomplete_fields = ['colors','sizes']
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

class FavoriteAdmin(ModelAdmin):
    list_display = ('user', )
    search_fields = ('user__email',)
    # readonly_fields = ('user','products')
    autocomplete_fields = ['products']

admin.site.register(Product,ProductAdmin)
admin.site.register(Color,ColorAdmin)
admin.site.register(FootScan,ModelAdmin)
admin.site.register(Favorite,FavoriteAdmin)
