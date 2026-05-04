import logging
from django.forms import ModelForm, ValidationError
from django.utils import timezone

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class RecurringAdminForm(ModelForm):
    def clean(self):
        cleaned_data = super().clean()
        changed_data = self.changed_data
        if not changed_data:
            return cleaned_data
        start_time = cleaned_data.get("start_time")
        end_time = cleaned_data.get("end_time")
        if "end_time" and "start_time" not in changed_data:
            return cleaned_data
        if start_time and start_time < timezone.now():
            raise ValidationError({"start_time": "Must be in future, not past"})
        if end_time <= start_time:
            raise ValidationError(
                {"end_time": "End time cannot be earlier than start time"}
            )

        return cleaned_data


class OneTimeForm(ModelForm):
    def clean(self):
        cd = super().clean()
        changed_data = self.changed_data
        if not changed_data:
            return cd
        if "expires_at" not in changed_data:
            return cd
        expires_at = cd.get("expires_at")
        if not expires_at:
            return cd 
        if expires_at <= timezone.now():
            raise ValidationError(
                {"expires_at" : "Expiring time can not be in past"}
            )
        return cd
