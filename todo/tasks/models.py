from django.db import models
from django.conf import settings
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.utils import timezone


# Create your models here.


class Task(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=500, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    completed = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created"]
        indexes = [models.Index(fields=["-created"])]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("tasks:detail", kwargs={"pk": self.pk})


class OneTime(models.Model):
    task = models.OneToOneField(
        Task, on_delete=models.CASCADE, related_name="onetime", null=True
    )
    expires_at = models.DateTimeField(null=True, blank=True)

    def clean(self):
        if self.expires_at <= timezone.now():
            raise ValidationError('Time error')

    def __str__(self):
        return "Onetime task"
