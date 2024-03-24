from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Task(models.Model):
    STATUS_CHOICES = [
        ("UNASSIGNED", "Unassigned"),
        ("IN_PROGRESS", "In Progress"),
        ("DONE", "Completed"),
        ("ARCHIVED", "Archived"),
    ]
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=False, default="")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="UNASSIGNED",
                              db_comment="Can be UNASSIGNED, IN_PROGRESS, DONE or ARCHIVED.",)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    creator = models.ForeignKey(User, related_name="created_tasks", on_delete=models.CASCADE)
    owner = models.ForeignKey(User, related_name="owned_tasks", on_delete=models.SET_NULL, null=True,
                              db_comment="Foreign Key to the User who currently owns the task.",)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(status='UNASSIGNED')
                | models.Q(status='IN_PROGRESS')
                | models.Q(status='DONE')
                | models.Q(status='ARCHIVED'),
                name='status_check',
            ),
        ]


class Epic(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    creator = models.ForeignKey(User, related_name="created_epics", on_delete=models.CASCADE)
    tasks = models.ManyToManyField("Task", related_name="epics", blank=True)


class Sprint(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    creator = models.ForeignKey(User, related_name="created_sprints", on_delete=models.CASCADE)
    tasks = models.ManyToManyField(Task, related_name='sprints', blank=True)
    epic = models.ForeignKey(Epic, related_name="sprints", on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        constraints = [
            models.CheckConstraint(check=models.Q(end_date__gt=models.F('start_date')), name='end_date_after_start_date'),
        ]
