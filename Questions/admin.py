from .models import *
from django.contrib import admin
from unfold.admin import ModelAdmin
from unfold.admin import TabularInline
# Register your models here.

class AnsInline(TabularInline):  # Inline child model
    model = Ans
    extra = 1
    fields = ["answer"]

@admin.register(Questions)
class QuestionsAdmin(ModelAdmin):
    list_display = ("sub_category", "created_at")
    search_fields = ("sub_category",)
    inlines = [AnsInline]  

@admin.register(Ans)
class AnsAdmin(ModelAdmin):
    list_display = ("answer", "parent")
    search_fields = ("answer", "parent__sub_category")  # Allow searching by answer text and parent sub_category

admin.site.register(FAQ,ModelAdmin)