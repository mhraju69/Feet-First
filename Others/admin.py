from .models import *
from django.contrib import admin
from unfold.admin import ModelAdmin
from unfold.admin import TabularInline
# Register your models here.

admin.site.register(FAQ,ModelAdmin)
admin.site.register(News,ModelAdmin)