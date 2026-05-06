from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from django.template.loader import render_to_string
from django.utils.html import format_html
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
    readonly_fields = ["duration_time", "task_history"]
    fieldsets = (
        (
            "Main",
            {
                "fields": (
                    "start_time",
                    "end_time",
                    "interval",
                    "duration_time",
                )
            },
        ),
        ("History", {"fields": ("task_history",), "classes": ["collapse"]}),
    )
    form = RecurringAdminForm
    inlines = [TaskInline, RecurringStateInline]

    def task_name(self, obj: Recurring):
        task = obj.task.first()
        if not task:
            return "task not exists"
        return task.name or "-"

    def task_history(self, obj: Recurring):
        history = obj.state.history.all()[:30]
        html = render_to_string(
            "tasks/admin/task_history.html", context={"object_list": history}
        )
        return html

    def save_model(self, request, obj, form, change):
        create_recurring_state(obj, form.changed_data)


@admin.register(RecurringStateHistory)
class StateHistoryAdmin(admin.ModelAdmin):
    list_display = ["completed", "state"]
    readonly_fields = ["completed", "state", "started_at", "ended_at"]

    def state(self, obj: RecurringStateHistory):
        state = obj.state
        return f"{str(state)}"
