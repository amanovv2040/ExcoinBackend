# Generated by Django 4.2.2 on 2023-07-05 18:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('review', '0003_review_name_review_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='date_created',
            field=models.CharField(blank=True, default='06.07.2023, 00:28', null=True, verbose_name='Review created date'),
        ),
    ]