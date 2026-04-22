from django.contrib import admin
from .models import Task, OneTime

# Register your models here.

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'completed']
    search_fields = ['name']
    list_filter = ['user', 'completed']

@admin.register(OneTime)
class OneTimeAdmin(admin.ModelAdmin):
    list_filter = ['expires_at']



