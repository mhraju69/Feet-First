from .models import *
from django.contrib import admin
from unfold.admin import ModelAdmin
from unfold.admin import TabularInline
# Register your models here.

class QuesInline(TabularInline):  # Inline child model
    model = Ques
    extra = 1
    fields = ["questions"]


# @admin.register(Questions)
class QuestionsAdmin(ModelAdmin):
    list_display = ("sub_category", "created_at")
    search_fields = ("sub_category",)
    inlines = [QuesInline]  # ✅ allows adding unlimited Ques inline


class AnswerItemInline(TabularInline):
    model = AnswerItem
    extra = 1

# @admin.register(Answer)
class AnswerAdmin(ModelAdmin):
    list_display = ("user", "created_at")
    readonly_fields = ('user',)
    inlines = [AnswerItemInline]