from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Task, OneTime, Recurring
from .services import one_time, recurring


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
        cd = super().clean()
        changed_data = self.changed_data
        return recurring.validate_time(cd, changed_data)


class OneTimeForm(forms.ModelForm):
    class Meta:
        model = OneTime
        fields = ["expires_at", "starts_at"]
        widgets = {
            "expires_at": forms.widgets.DateTimeInput(attrs={"type": "datetime-local"}),
            "starts_at": forms.widgets.DateTimeInput(attrs={"type": "datetime-local"}),
        }

    def clean(self):
        cd = super().clean()
        changed_data = self.changed_data
        return one_time.validate_time(cd, changed_data)

    def clean_starts_at(self):
        changed_data = self.changed_data
        starts_at = self.cleaned_data.get("starts_at")
        if "starts_at" not in changed_data:
            return starts_at
        if not starts_at:
            return starts_at
        if starts_at <= timezone.now():
            raise ValidationError("Starting time can not be in past")
        return starts_at

    def clean_expires_at(self):
        changed_data = self.changed_data
        expires_at = self.cleaned_data.get("expires_at")
        if "expires_at" not in changed_data:
            return expires_at
        if not expires_at:
            return expires_at
        if expires_at <= timezone.now():
            raise ValidationError("Expiring time can not be in past")
        return expires_at
