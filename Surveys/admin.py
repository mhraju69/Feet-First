from .models import *
from django.contrib import admin
from unfold.admin import ModelAdmin
from django.utils.text import Truncator
from django.utils.html import format_html
# Register your models here.
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
    def has_add_permission(self, request):
        return False

admin.site.register(OnboardingSurvey,SurvayAdmin)