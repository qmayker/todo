from django.views.generic import CreateView
from django.contrib.auth import forms
from django.urls import reverse_lazy
from django.conf import settings
from django.utils import timezone
from .models import UserProfile


class UserCreateView(CreateView):
    template_name = "accounts/user/create.html"
    form_class = forms.UserCreationForm
    success_url = reverse_lazy("tasks:list")

    def form_valid(self, form):
        response = super().form_valid(form)
        tzname = timezone.get_current_timezone_name()
        UserProfile.objects.create(
            user=self.object, timezone=tzname or settings.TIME_ZONE
        )
        return response
