from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from .services.recurring import create_recurring_state
from .models import Task, OneTime, Recurring, RecurringState, RecurringStateHistory
from .admin_forms import RecurringAdminForm

# Register your models here.


class RecurringStateHistoryInline(admin.TabularInline):
    model = RecurringStateHistory
    extra = 0

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


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
    list_display = ["name", "user"]
    search_fields = ["name"]
    list_filter = ["user"]


class RecurringStateInline(admin.TabularInline):
    model = RecurringState
    extra = 0
    inlines = [RecurringStateHistoryInline]

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Recurring)
class RecurringAdmin(admin.ModelAdmin):
    list_display = ["interval", "duration_time", "task_name"]
    list_filter = ["interval"]
    exclude = ["duration_time"]
    form = RecurringAdminForm
    inlines = [TaskInline, RecurringStateInline]

    def task_name(self, obj: Recurring):
        task = obj.task.first()
        if not task:
            return "task not exists"
        return task.name or "-"

    def save_model(self, request, obj, form, change):
        create_recurring_state(obj, form.changed_data)


@admin.register(RecurringStateHistory)
class StateHistoryAdmin(admin.ModelAdmin):
    list_display = ["completed", "state"]

    def state(self, obj: RecurringStateHistory):
        state = obj.state
        return f"{str(state)}"
