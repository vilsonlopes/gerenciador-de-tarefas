# Generated by Django 4.2.2 on 2024-03-23 22:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0005_sprint_epic_sprint_end_date_after_start_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='epic',
            name='tasks',
            field=models.ManyToManyField(blank=True, related_name='epics', to='tasks.task'),
        ),
        migrations.AddField(
            model_name='sprint',
            name='epic',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sprints', to='tasks.epic'),
        ),
    ]
