# Generated by Django 4.2.2 on 2024-04-05 00:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0009_subscribeemail'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='file_upload',
            field=models.FileField(blank=True, null=True, upload_to='tasks/files'),
        ),
        migrations.AddField(
            model_name='task',
            name='image_upload',
            field=models.ImageField(blank=True, null=True, upload_to='tasks/images'),
        ),
    ]
