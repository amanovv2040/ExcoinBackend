# Generated by Django 4.2.2 on 2023-07-05 18:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('review', '0004_alter_review_date_created'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='date_created',
            field=models.CharField(blank=True, null=True, verbose_name='Review created date'),
        ),
    ]