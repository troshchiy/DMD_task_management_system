from django.db import models
from django.urls import reverse


class Task(models.Model):
    title = models.TextField()
    description = models.TextField()
    performers = models.TextField()
    deadline = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def get_absolute_url(self):
        return reverse('task_detail', args=[self.id])