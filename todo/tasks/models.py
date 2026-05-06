from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta


class Task(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=500, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, null=True, related_name="task"
    )
    object_id = models.PositiveBigIntegerField(null=True)
    content_object = GenericForeignKey("content_type", "object_id")

    class Meta:
        ordering = ["-created"]
        indexes = [
            models.Index(fields=["-created"]),
            models.Index(fields=["user"]),
            models.Index(fields=["content_type", "object_id"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["content_type", "object_id"],
                name="unique_content_type_object_id",
            )
        ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("tasks:detail", kwargs={"pk": self.pk})


class OneTime(models.Model):
    expires_at = models.DateTimeField(null=True, blank=True)
    expired = models.BooleanField(default=False)
    completed = models.BooleanField(default=False)
    task = GenericRelation(Task, related_query_name="onetime")

    def save(self, *args, **kwargs):
        if self.expires_at and timezone.is_naive(self.expires_at):
            self.expires_at = timezone.make_aware(self.expires_at)

    def __str__(self):
        return "Onetime task"


class Recurring(models.Model):
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    duration_time = models.DurationField(blank=True, editable=False)
    interval = models.DurationField(default=timedelta(days=7))
    task = GenericRelation(Task, related_query_name="recurring")


class RecurringState(models.Model):
    recurring = models.OneToOneField(
        Recurring, on_delete=models.CASCADE, related_query_name="state"
    )
    is_running = models.BooleanField(default=False)
    completed = models.BooleanField(default=False)
    last_run_at = models.DateTimeField(null=True, blank=True)
    next_time = models.DateTimeField(blank=True)
    ends_at = models.DateTimeField(blank=True)


class RecurringStateHistory(models.Model):
    completed = models.BooleanField(default=False, editable=False)
    state = models.ForeignKey(
        RecurringState,
        on_delete=models.CASCADE,
        related_name="completes",
        editable=False,
    )
    started_at = models.DateTimeField(editable=False)
    ended_at = models.DateTimeField(editable=False)

    class Meta:
        ordering = ["-ended_at"]

    def save(self, *args, **kwargs):
        if not self.state:
            raise ValueError("")
        self.started_at = self.state.last_run_at
        if not self.started_at:
            raise ValueError("")
        return super().save(*args, **kwargs)
        # todo - saving
