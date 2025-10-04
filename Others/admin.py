from .models import *
from django.contrib import admin
from unfold.admin import ModelAdmin
from unfold.admin import TabularInline
# Register your models here.

class AnsInline(TabularInline):  # Inline child model
    model = Ans
    extra = 1
    fields = ["answer"]

@admin.register(Ques)
class QuestionsAdmin(ModelAdmin):
    
    search_fields = ("question",)
    inlines = [AnsInline]  

@admin.register(Ans)
class AnsAdmin(ModelAdmin):
    list_display = ("answer", "parent")
    list_filter = ("parent",)
    search_fields = ("answer", "parent__sub_category")  # Allow searching by answer text and parent sub_category

admin.site.register(FAQ,ModelAdmin)
admin.site.register(News,ModelAdmin)