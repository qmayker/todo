import logging
from django.forms import ModelForm
from django.utils import timezone
from django.core.exceptions import ValidationError
from .services import one_time, recurring

logger = logging.getLogger(__name__)


class RecurringAdminForm(ModelForm):
    def clean(self):
        cd = super().clean()
        changed_data = self.changed_data
        recurring.validate_time(cd, changed_data)
        return cd

    def clean_start_time(self):
        start_time = self.cleaned_data.get("start_time")
        if start_time < timezone.now():
            raise ValidationError("Must be in future, not past")

    def clean_end_time(self):
        end_time = self.cleaned_data.get("end_time")
        if end_time <= timezone.now():
            raise ValidationError("Must be in future, not past")


class OneTimeForm(ModelForm):
    def clean(self):
        cd = super().clean()
        changed_data = self.changed_data
        one_time.validate_time(cd, changed_data)
        return cd

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
