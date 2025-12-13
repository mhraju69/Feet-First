from .models import *
from Products.models import *
from django.contrib import admin
from unfold.admin import ModelAdmin
# Register your models here.

admin.site.register(FAQ,ModelAdmin)
admin.site.register(News,ModelAdmin)
admin.site.register(FootScan,ModelAdmin)
admin.site.register(Order,ModelAdmin)
admin.site.register(Warehouse,ModelAdmin)