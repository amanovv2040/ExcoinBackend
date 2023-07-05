from django.db import models
from django.utils.translation import gettext_lazy as _
from excoin.settings import AUTH_USER_MODEL
from account.models import User
from datetime import datetime


class Review(models.Model):
    user = models.ForeignKey(
        AUTH_USER_MODEL,
        verbose_name=_('Review author'),
        on_delete=models.CASCADE,
        null=True, blank=True
    )
    name = models.CharField(
        verbose_name=_('Review author name'),
        max_length=255,
        null=True, blank=True
    )
    email = models.EmailField(
        verbose_name=_('Review author email'),
        max_length=255,
        null=True, blank=True
    )
    text = models.TextField(
        verbose_name=_('Review text'),
        null=True, blank=True
    )
    date_created = models.CharField(
        verbose_name=_('Review created date'),
        null=True, blank=True
    )

    def __str__(self):
        return self.name

    def get_user(self):
        user = User.objects.get(email=self.email).exists()
        if user:
            return user.id
        return None

    def save(self, *args, **kwargs):
        self.date_created = datetime.now().strftime('%d.%m.%Y, %H:%M')
        return super().save(*args, **kwargs)