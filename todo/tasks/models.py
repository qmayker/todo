from django.db import models
from django.conf import settings
from django.urls import reverse

# Create your models here.


class Task(models.Model):
    class Types(models.Choices):
        one_time = "Одноразовий"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=500)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    completed = models.BooleanField(default=False)
    task_type = models.CharField(choices=Types)

    class Meta:
        ordering = ["-created"]
        indexes = [models.Index(fields=["-created"])]

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('tasks:detail', kwargs={'pk': self.pk})
