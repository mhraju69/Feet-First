from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Product)
admin.site.register(AvailableSize)
admin.site.register(AvailableWidth)
admin.site.register(PdfFile)
admin.site.register(Category)
admin.site.register(SubCategory)