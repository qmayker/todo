from django.contrib import admin
from .models import Task

# Register your models here.

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['celery_id', 'task_name', 'start']
    list_filter = ['start']
    search_fields = ['task_name']


    def task_name(self, obj:Task):
        return obj.task.name