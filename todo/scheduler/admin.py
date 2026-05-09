from django.contrib import admin
from .models import CeleryTask
from .services.tasks import check_tasks

# Register your models here.

@admin.action(description="Run a check_tasks function")
def check(modeladmin, request, queryset):
    check_tasks.apply_async()

@admin.register(CeleryTask)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['celery_id', 'task_name', 'start']
    list_filter = ['start']
    search_fields = ['task_name']
    actions = [check]


    def task_name(self, obj:CeleryTask):
        return obj.task.name