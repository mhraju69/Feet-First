from django.contrib import admin
from .models import *
from unfold.admin import ModelAdmin

# Register your models here.
class UserAdmin(ModelAdmin ):
    list_display = ('email', 'name',  'role','date_of_birth', 'is_active')
    search_fields = ('email', 'name')
    list_filter = ('is_active', 'is_superuser')
    actions = ['delete_selected']
    

admin.site.register(User,UserAdmin)
admin.site.register(OTP)
admin.site.register(OnboardingSurvey)

    