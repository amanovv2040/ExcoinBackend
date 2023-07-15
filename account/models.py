from django.urls import reverse
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone

from .managers import UserManager


# Custom User model
class User(AbstractUser):
    username = None
    email = models.EmailField(
        verbose_name=_('Email'),
        unique=True
    )
    is_verified = models.BooleanField(
        verbose_name=_('Verification'),
        default=False
    )
    # phone = models.CharField(verbose_name=_('Телефон'), max_length=12, unique=True, validators=[
    #     RegexValidator(regex=r'^996\d{9}$', message=_('Передать действительный номер телефона '))])
    phone = models.CharField(
        verbose_name=_('Phone'),
        max_length=12,
        unique=True,
        null=True,
        blank=True
    )
    avatar = models.ImageField(
        verbose_name=_('Profile photo'),
        upload_to='avatars/',
        blank=True,
        default='avatars/default.png'
    )
    balance = models.FloatField(
        verbose_name=_('Remaining balance'),
        default=0
    )
    second_name = models.CharField(
        verbose_name=_('Second name'),
        max_length=150,
        blank=True
    )
    passport = models.IntegerField(
        verbose_name=_('Passport ID'),
        blank=True,
        null=True,
        default=0
    )
    verification_code = models.CharField(
        verbose_name=_('Verification code'),
        null=True,
        blank=True
    )
    verification_code_created_at = models.DateTimeField(
        verbose_name=_('Verifcation code created time'),
        null=True
        )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        db_table = 'user'
        verbose_name = _('User')
        verbose_name_plural = _('Users')

    def __str__(self):
        return self.email

    def token(self):
        refresh = RefreshToken.for_user(self)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
