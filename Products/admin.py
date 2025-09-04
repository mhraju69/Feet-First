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

class ProductAdmin(ModelAdmin):
    list_display = ('name_de', 'name_it', 'price', 'discount', 'stock_quantity', 'is_active', 'brand', 'subcategory', 'created_at')
    search_fields = ('name_de', 'name_it', 'brand', 'subcategory','price', 'discount','stock_quantity')

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

admin.site.register(Product,ProductAdmin)
admin.site.register(AvailableSize,SizeAdmin)
admin.site.register(AvailableWidth,WidthAdmin)
admin.site.register(PdfFile,PdfFileAdmin)
admin.site.register(Category,CategoryAdmin)
admin.site.register(SubCategory,SubCategoryAdmin)