from django.contrib import admin
from .models import *
from unfold.admin import ModelAdmin
# Register your models here.
admin.site.register(Product,ModelAdmin)
admin.site.register(AvailableSize,ModelAdmin)
admin.site.register(AvailableWidth,ModelAdmin)
admin.site.register(PdfFile,ModelAdmin)
admin.site.register(Category,ModelAdmin)
admin.site.register(SubCategory,ModelAdmin)