# Generated by Django 5.1.1 on 2024-09-26 05:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('problems', '0002_problemcompletion_weekcommit'),
    ]

    operations = [
        migrations.AlterField(
            model_name='problem',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='problems/images/'),
        ),
    ]
