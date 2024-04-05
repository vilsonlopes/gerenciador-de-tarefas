# Generated by Django 4.2.2 on 2024-04-04 21:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0008_epic_completion_status_task_version_alter_task_owner_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='SubscribeEmail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254)),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='watchers', to='tasks.task')),
            ],
        ),
    ]