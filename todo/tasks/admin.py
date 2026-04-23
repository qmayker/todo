from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from .models import Task, OneTime

# Register your models here.


class TaskInline(GenericTabularInline):
    model = Task
    extra=0

@admin.register(OneTime)
class OneTimeAdmin(admin.ModelAdmin):
    list_display = ['expires_at']
    list_filter = ['expires_at']
    inlines = [TaskInline]


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ["name", "user", "completed"]
    search_fields = ["name"]
    list_filter = ["user", "completed"]
