from django.contrib import admin
from.models import *
from unfold.admin import ModelAdmin
# Register your models here.
class ContactAdmin(ModelAdmin):
    list_display = ('name', 'email', 'subject','created_at','read')
    search_fields = ('email','name','subject')
    readonly_fields =  ('name', 'email', 'subject','message','created_at')
    list_filter = ('read',)
    list_per_page = 10
    fieldsets = (
        (None, {
            'fields': (
                ('name', 'email', 'subject','message','created_at','read')
            ),
        }),
    )
    ordering = ('-created_at',)

admin.site.register(ContactUs, ContactAdmin)
