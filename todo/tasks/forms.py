from logging import getLogger
from django import forms
from django.utils import timezone
from .models import Task, OneTime, Recurring
from .services import one_time, recurring

logger = getLogger(__name__)


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ["name", "description"]


class RecurringForm(forms.ModelForm):
    class Meta:
        model = Recurring
        fields = ["start_time", "end_time", "interval"]
        widgets = {
            "start_time": forms.widgets.DateTimeInput(attrs={"type": "datetime-local"}),
            "end_time": forms.widgets.DateTimeInput(attrs={"type": "datetime-local"}),
        }

    def clean(self):
        cd = self.cleaned_data
        logger.info(f"{cd}, {timezone.get_current_timezone()}")
        changed_data = self.changed_data
        validation = recurring.RecurringValidation(cd, changed_data, logger)
        validation.validate()
        return cd


class OneTimeForm(forms.ModelForm):
    class Meta:
        model = OneTime
        fields = ["expires_at", "starts_at"]
        widgets = {
            "expires_at": forms.widgets.DateTimeInput(attrs={"type": "datetime-local"}),
            "starts_at": forms.widgets.DateTimeInput(attrs={"type": "datetime-local"}),
        }

    def clean(self):
        cd = self.cleaned_data
        changed_data = self.changed_data
        validation = one_time.OneTimeValidation(cd, changed_data, logger)
        validation.validate()
        return cd
