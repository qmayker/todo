from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.conf import settings
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.utils import timezone
from zoneinfo import ZoneInfo


# Create your models here.


class Task(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=500, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    completed = models.BooleanField(default=False)
    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, null=True, related_name="task"
    )
    object_id = models.PositiveBigIntegerField(null=True)
    content_object = GenericForeignKey("content_type", "object_id")

    class Meta:
        ordering = ["-created"]
        indexes = [models.Index(fields=["-created"])]
        constraints = [
            models.UniqueConstraint(
                fields=["content_type", "object_id"], name="content type unique"
            )
        ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("tasks:detail", kwargs={"pk": self.pk})

    def delete(self, using=..., keep_parents=...):
        print('DELETE')
        obj = self.content_object
        print(obj)
        r = super().delete(using, keep_parents)
        if obj:
            obj.delete()
        return r
    
        #override with signals


class OneTime(models.Model):
    expires_at = models.DateTimeField(null=True, blank=True)
    expired = models.BooleanField(default=False)
    task = GenericRelation(Task, related_query_name="onetime")

    def save(self, *args, **kwargs):
        if self.expires_at:
            utc_time = self.expires_at.astimezone(ZoneInfo("UTC"))
            self.expires_at = utc_time
        super().save(*args, **kwargs)

    def clean(self):
        if not self.expires_at:
            return
        if self.expires_at <= timezone.now():
            raise ValidationError("Time error")

    def __str__(self):
        return "Onetime task"
