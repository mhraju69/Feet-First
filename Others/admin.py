from .models import *
from django.contrib import admin
from unfold.admin import ModelAdmin
# Register your models here.

admin.site.register(FAQ,ModelAdmin)
admin.site.register(News,ModelAdmin)