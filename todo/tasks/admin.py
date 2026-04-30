from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from .models import Task, OneTime, Recurring, RecurringState

# Register your models here.


class TaskInline(GenericTabularInline):
    model = Task
    extra = 0
    max_num = 1


@admin.register(OneTime)
class OneTimeAdmin(admin.ModelAdmin):
    list_display = ["expires_at"]
    list_filter = ["expires_at", "expired"]
    inlines = [TaskInline]


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ["name", "user", "completed"]
    search_fields = ["name"]
    list_filter = ["user", "completed"]


class RecurringStateInline(admin.TabularInline):
    model = RecurringState
    exclude = ["last_run_at"]


@admin.register(Recurring)
class RecurringAdmin(admin.ModelAdmin):
    list_display = ["interval", "duration_time", "task_name"]
    list_filter = ["interval"]
    exclude = ["duration_time"]
    inlines = [RecurringStateInline, TaskInline]

    def task_name(self, obj: Recurring):
        task = obj.task.first()
        return task.name or "-"
