import logging
from django.forms import ModelForm
from .services import one_time, recurring

logger = logging.getLogger(__name__)


class RecurringAdminForm(ModelForm):
    def clean(self):
        cd = super().clean()
        changed_data = self.changed_data
        validation = recurring.RecurringValidation(cd, changed_data, logger)
        validation.validate()
        return cd


class OneTimeForm(ModelForm):
    def clean(self):
        cd = super().clean()
        changed_data = self.changed_data
        validation = one_time.OneTimeValidation(cd, changed_data, logger)
        validation.validate()
        return cd
