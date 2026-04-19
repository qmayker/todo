from django.contrib import admin
from .models import Task

# Register your models here.

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'completed', 'task_type']
    search_fields = ['name']
    list_filter = ['user', 'completed', 'task_type']