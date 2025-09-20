from .models import *
from django.contrib import admin
from unfold.admin import ModelAdmin
from django.utils.html import format_html
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.text import Truncator
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django import forms


@admin.register(User)
class UserAdmin(ModelAdmin):
    icon = 'user'
    list_display = ("email", "name", "role", "is_active", "is_staff", "suspend", "date_joined")
    list_filter = ("role", "is_active"  , "is_staff", "suspend")
    ordering = ("-date_joined",)
    search_fields = ("email", "name")
    readonly_fields = ("last_login", "date_joined")
    autocomplete_fields = ['groups']
    fieldsets = (
        ("Credentials", {"fields": ("email", "password")}),
        ("Personal Info", {"fields": ("name", "phone", "date_of_birth", "image", "language")}),
        ('Partner Info', {"fields": ("latitude", "longitude", "match_score", "notes", "groups",)}),
        ("Permissions", {"fields": ("role", "is_active", "is_staff", "is_superuser", "suspend")}),
        ("Important dates", {"fields": ("date_joined",)}),
    )

    # Row-level restriction: only show self to partner
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        if request.user.role == 'partner':
            return qs.filter(id=request.user.id)  # only their own user
        return qs

    # Restrict change permissions
    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if obj is None:
            return True  # needed for list view
        if request.user.role == 'partner':
            return obj.id == request.user.id
        return False

    # Restrict delete permission
    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if obj is None:
            return False
        if request.user.role == 'partner':
            return obj.id == request.user.id
        return False
    
    def get_fieldsets(self, request, obj=None):
        fieldsets = list(self.fieldsets)
        if request.user.role == 'partner' and not request.user.is_superuser:
            # Remove fields that partner should not see
            new_fieldsets = []
            for title, opts in fieldsets:
                fields = opts.get('fields', ())
                # Filter out restricted fields
                fields = [f for f in fields if f not in ("role", "groups", "user_permissions", "is_staff", "is_superuser", "suspend",'password')]
                new_fieldsets.append((title, {"fields": fields}))
            return new_fieldsets
        return fieldsets
    
    # Make certain fields readonly for partners

    def get_readonly_fields(self, request, obj=None):
        ro_fields = list(self.readonly_fields)
        if request.user.role == 'partner':
            # partners cannot edit role, groups, user_permissions
            ro_fields += ["is_active"]
        return ro_fields

class DeleteAdmin(ModelAdmin):
    list_display = ('email', 'formatted_reason', 'deleted_at')

    # Make non-editable and nicely formatted fields readonly
    readonly_fields = ('email','formatted_reason', 'deleted_at')

    # Specify fields for the detail page (exclude non-editable from fields list)
    fields = ('email','formatted_reason', 'deleted_at',)

    search_fields = ('email', 'reason', )

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

class AddressAdmin(ModelAdmin):
    list_display = ('user','first_name','street_address','city','postal_code','country','phone_number')
    list_filter = ('country', 'city', 'postal_code')
    search_fields = ('user','first_name', 'last_name', 'street_address', 'city', 'postal_code', 'phone_number','country')
    ordering = ('-created_at',)
    readonly_fields = ('user','created_at', 'updated_at',)

# admin.site.register(OTP,OtpAdmin)
admin.site.register(Address,AddressAdmin)
admin.site.register(AccountDeletionRequest,DeleteAdmin)
    