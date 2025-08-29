from django.contrib import admin
from .models import *
from unfold.admin import ModelAdmin

# Register your models here.
class UserAdmin(ModelAdmin ):
    list_display = ('email', 'name',  'role','date_of_birth', 'is_active')
    search_fields = ('email', 'name')
    list_filter = ('is_active', 'is_superuser')

class OtpAdmin(ModelAdmin):
    list_display = ('user', 'otp', 'created_at')
    search_fields = ('user__email', 'otp')
    list_filter = ('created_at',)
    readonly_fields = ('otp','user')


admin.site.register(User,UserAdmin)
admin.site.register(OTP,OtpAdmin)
admin.site.register(OnboardingSurvey,ModelAdmin)

    