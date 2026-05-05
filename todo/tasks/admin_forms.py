from django.forms import ModelForm
from .services import recurring, onetime


class RecurringAdminForm(ModelForm):
    def clean(self):
        cd = super().clean()
        changed_data = self.changed_data
        return recurring.validate_time(cd, changed_data)


class OneTimeForm(ModelForm):
    def clean(self):
        cd = super().clean()
        changed_data = self.changed_data
        return onetime.validate_time(cd, changed_data)
