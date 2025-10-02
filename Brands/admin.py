from django.contrib import admin
from .models import *
from unfold.admin import ModelAdmin
class BrandAdmin(ModelAdmin):
    search_fields = ['name']
    list_display = ['name',]
    list_per_page = 20

admin.site.register(Brand,BrandAdmin)

