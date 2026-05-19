from django.db import models
from django.urls import reverse_lazy
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from .querysets import OneTimeQuerySet, HistoryQuerySet


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
    starts_at = models.DateTimeField(blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    started = models.BooleanField(default=False, blank=True)
    expired = models.BooleanField(default=False, blank=True)
    completed = models.BooleanField(default=False, blank=True)
    task = GenericRelation(Task, related_query_name="onetime")
    objects = OneTimeQuerySet.as_manager()

    class Meta:
        indexes = [
            models.Index(fields=["started", "expired"]),
            models.Index(fields=["expired", "completed"]),
        ]

    def save(self, *args, **kwargs):
        if self.expires_at and timezone.is_naive(self.expires_at):
            self.expires_at = timezone.make_aware(self.expires_at)
        if self.starts_at and timezone.is_naive(self.starts_at):
            self.starts_at = timezone.make_aware(self.starts_at)

        super().save(*args, **kwargs)

    def __str__(self):
        return "Onetime task"

    def mark_completed(self, completed: bool):
        qs = OneTime.objects.filter(pk=self.pk)
        qs.update(completed=completed)

    @property
    def is_completed(self):
        return self.completed

    def get_task(self):
        return self.task.first()


# TODO - duration_time to RecurringState
class Recurring(models.Model):
    start_time = models.DateTimeField(blank=True)
    end_time = models.DateTimeField()
    duration_time = models.DurationField(blank=True, editable=False)
    interval = models.DurationField(default=timedelta(days=7))
    task = GenericRelation(Task, related_query_name="recurring")

    def __str__(self):
        return "Recurring task"

    def save(self, *args, **kwargs):
        if self.end_time and self.start_time:
            self.duration_time = self.end_time - self.start_time
        return super().save(*args, **kwargs)

    def mark_completed(self, completed: bool):
        qs = RecurringState.objects.filter(pk=self.state.pk)
        qs.update(completed=completed)

    @property
    def is_completed(self):
        return self.state.completed

    def get_task(self):
        return self.task.first()


class RecurringState(models.Model):
    recurring = models.OneToOneField(
        Recurring, on_delete=models.CASCADE, related_name="state"
    )
    is_running = models.BooleanField(default=False)
    completed = models.BooleanField(default=False)
    last_run_at = models.DateTimeField(null=True, blank=True)
    next_time = models.DateTimeField(blank=True)
    ends_at = models.DateTimeField(blank=True)

    # add indexes


# add task_id, task_name
class RecurringStateHistory(models.Model):
    completed = models.BooleanField(default=False)
    state = models.ForeignKey(
        RecurringState,
        on_delete=models.CASCADE,
        related_name="history",
    )
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    started_at = models.DateTimeField()
    ended_at = models.DateTimeField()
    task_name = models.CharField()
    objects = HistoryQuerySet.as_manager()

    class Meta:
        ordering = ["-ended_at"]

    # TODO - update
    def save(self, *args, **kwargs):
        if not self.state:
            return super().save(*args, **kwargs)
        self.started_at = self.state.last_run_at
        return super().save(*args, **kwargs)

    def get_admin_url(self):
        return reverse_lazy(
            f"admin:{self._meta.app_label}_{self._meta.model_name}_change",
            args=[self.pk],
        )

    def get_absolute_url(self):
        return reverse("tasks:history_detail", args=[self.task_id, self.pk])
