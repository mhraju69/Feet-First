from .models import *
from django.contrib import admin
from unfold.admin import ModelAdmin
from django.utils.html import format_html

from .models import *
from django.contrib import admin
from unfold.admin import ModelAdmin
from django.utils.text import Truncator
from django.utils.html import format_html
# Register your models here.
class DeleteAdmin(ModelAdmin):
    list_display = ('user', 'formatted_reason', 'confirmed', 'deleted_at')

    # Make non-editable and nicely formatted fields readonly
    readonly_fields = ('user','formatted_reason', 'deleted_at')

    # Specify fields for the detail page (exclude non-editable from fields list)
    fields = ('user','formatted_reason', 'deleted_at', 'confirmed')

    search_fields = ('user__email', 'reason', )
    list_filter = ('confirmed',)

    def formatted_reason(self, obj):
        # Display reason as badges
        return format_html(
            " ".join([
                f'<span style="background:#eee;padding:2px 5px;border-radius:3px;margin-right:3px;">{s}</span>'
                for s in obj.reason
            ])
        )
    formatted_reason.short_description = 'Reason'

    # Disable add button
    def has_add_permission(self, request):
        return False
# Register your models here.
class UserAdmin(ModelAdmin ):
    list_display = ('email', 'name',  'role','date_of_birth', 'is_active','suspend')
    search_fields = ('email', 'name','phone')
    list_filter = ('is_active','suspend',  'is_superuser','role')

class OtpAdmin(ModelAdmin):
    list_display = ('user', 'otp', 'created_at')
    search_fields = ('user__email', 'otp')
    list_filter = ('created_at',)
    readonly_fields = ('user','otp', 'attempt_count','last_tried','created_at',)
    # Disable add button
    def has_add_permission(self, request):
        return False
    
class SurvayAdmin(ModelAdmin):
    list_display = ('user', 'formatted_sources', 'product_preference', 'truncated_foot_problems', 'created_at')

    # Make non-editable and nicely formatted fields readonly
    readonly_fields = ('user','formatted_sources', 'created_at', 'product_preference', 'foot_problems')

    # Specify fields for the detail page (exclude non-editable from fields list)
    fields = ('user','formatted_sources', 'product_preference', 'foot_problems', 'created_at')

    search_fields = ('user__email', 'sources', )
    list_filter = ('product_preference',)    

    def formatted_sources(self, obj):
        # Display sources as badges
        return format_html(
            " ".join([
                f'<span style="background:#eee;padding:2px 5px;border-radius:3px;margin-right:3px;">{s}</span>'
                for s in obj.sources
            ])
        )
    formatted_sources.short_description = 'Sources'
    def truncated_foot_problems(self, obj):
        # Truncate to 30 characters (adjust as needed)
        return Truncator(obj.foot_problems).chars(20)
    truncated_foot_problems.short_description = 'Foot Problems'

admin.site.register(AccountDeletionRequest,DeleteAdmin)
admin.site.register(User,UserAdmin)
admin.site.register(OTP,OtpAdmin)
