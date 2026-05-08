from django.contrib import admin
from .models import Task
from .services.celery import check_tasks

# Register your models here.

@admin.action(description="Run a check_tasks function")
def check(modeladmin, request, queryset):
    check_tasks()

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['celery_id', 'task_name', 'start']
    list_filter = ['start']
    search_fields = ['task_name']
    actions = [check]


    def task_name(self, obj:Task):
        return obj.task.name