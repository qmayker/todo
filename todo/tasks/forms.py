from django import forms
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
        recurring.validate_time(cd, changed_data)
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
        cd = super().clean()
        changed_data = self.changed_data
        one_time.validate(cd, changed_data)
        return cd
