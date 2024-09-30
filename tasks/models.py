from django.db import models


class Task(models.Model):
    title = models.TextField()
    description = models.TextField()
    performers = models.TextField()
    deadline = models.DateTimeField()
