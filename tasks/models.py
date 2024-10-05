from django.db import models
from django.urls import reverse


class Task(models.Model):
    class Status(models.TextChoices):
        ASSIGNED = 'ASGD', 'Assigned'
        IN_PROGRESS = 'PRGS', 'In progress'
        SUSPENDED = 'SPND', 'Suspended'
        COMPLETED = 'CMPL', 'Completed'

    parent = models.ForeignKey('self', null=True, blank=True, default=None, on_delete=models.SET_NULL)
    title = models.TextField()
    description = models.TextField()
    performers = models.TextField()
    deadline = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=4,
                              choices=Status.choices,
                              default=Status.ASSIGNED)

    def get_absolute_url(self):
        return reverse('task_detail', args=[self.id])