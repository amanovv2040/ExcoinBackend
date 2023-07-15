# Generated by Django 4.2.2 on 2023-07-15 16:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0004_user_verification_code_created_at'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='username',
        ),
        migrations.AlterField(
            model_name='user',
            name='verification_code_created_at',
            field=models.DateTimeField(null=True, verbose_name='Verifcation code created time'),
        ),
    ]
