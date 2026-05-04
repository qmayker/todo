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
        start_time = cleaned_data.get("start_time")
        logger.info(f"{self.changed_data} {self.cleaned_data}")
        if self.instance:
            return cleaned_data
        if start_time and start_time < timezone.now():
            raise ValidationError({"start_time": "Must be in future, not past"})

        return cleaned_data
