from django.db import models
from django.conf import settings

# Create your models here.


class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile"
    )
    timezone = models.CharField(default='Europe/Kyiv')

    def __str__(self):
        return f"{self.user}'s profile"
