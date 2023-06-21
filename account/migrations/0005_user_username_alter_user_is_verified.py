# Generated by Django 4.2.2 on 2023-06-21 15:59

import django.contrib.auth.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0004_user_is_verified'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='username',
            field=models.CharField(default='', error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='user',
            name='is_verified',
            field=models.BooleanField(default=False, verbose_name='Verification'),
        ),
    ]
