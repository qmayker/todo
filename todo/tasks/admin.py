from django.contrib import admin
from .models import Task, OneTime

# Register your models here.

class OneTimeTaskInline(admin.TabularInline):
    model = OneTime

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'completed']
    search_fields = ['name']
    list_filter = ['user', 'completed']
    inlines = [OneTimeTaskInline]



