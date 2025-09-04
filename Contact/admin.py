from django.contrib import admin
from.models import *
from unfold.admin import ModelAdmin
# Register your models here.
class ContactAdmin(ModelAdmin):
    list_display = ('name', 'email', 'subject','read')
    search_fields = ('email','name','subject')
    list_filter = ('read',)
    list_per_page = 10
    ordering = ('-created_at',)
    verbose_name = "Contact Us"
    verbose_name_plural = "Contact Us"

admin.site.register(ContactUs, ContactAdmin)
