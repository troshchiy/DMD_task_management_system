import datetime

from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.urls import reverse
from django.utils import timezone


class Task(models.Model):
    class Status(models.TextChoices):
        ASSIGNED = 'AS', 'Assigned'
        IN_PROGRESS = 'PR', 'In progress'
        SUSPENDED = 'SP', 'Suspended'
        COMPLETED = 'CM', 'Completed'

    parent = models.ForeignKey('self', null=True, blank=True, default=None, on_delete=models.SET_NULL)
    title = models.TextField()
    description = models.TextField()
    performers = models.TextField()
    deadline = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=2, choices=Status.choices, default=Status.ASSIGNED, blank=True)
    planned_labor_intensity = models.DurationField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    actual_completion_time = models.DurationField(null=True, blank=True)

    def clean(self):
        existing_task = None
        try:
            existing_task = Task.objects.get(id=self.id)
        except Task.DoesNotExist:
            if not self.status:
                self.status = Task.Status.ASSIGNED
            if self.status in (Task.Status.IN_PROGRESS, Task.Status.SUSPENDED, Task.Status.COMPLETED):
                raise ValidationError(
                    {'status': f'The status "{self.get_status_display()}" cannot be set when creating a task. '
                                'Only the status "Assigned" is available".'}
                )

        if self.status == Task.Status.COMPLETED and existing_task.status != Task.Status.IN_PROGRESS:
            raise ValidationError(
                {'status': 'The status "Completed" can only be set after the status "In Progress".'}
            )
        elif self.status == Task.Status.SUSPENDED and existing_task.status != Task.Status.IN_PROGRESS:
            raise ValidationError(
                {'status': 'The status "Suspended" can only be set after the status "In Progress".'}
            )

    def save(self, clean=True):
        if clean:
            self.clean()

            if self.status == Task.Status.COMPLETED:
                self.set_completed_status_recursively()

                self.completed_at = timezone.now()
                self.calculate_actual_completion_time()

            self.calculate_planned_labor_intensity()

        models.Model.save(self)

    def set_completed_status_recursively(self):
        with transaction.atomic():
            try:
                for subtask in self.task_set.all():
                    subtask.status = Task.Status.COMPLETED
                    subtask.save()
                models.Model.save(self)
            except ValidationError as e:
                raise ValidationError(f'The subtask "{subtask.title}" cannot be completed. {e.messages[0]}')

    def calculate_planned_labor_intensity(self):
        models.Model.save(self)
        task = Task.objects.get(id=self.id)
        planned_labor_intensity = task.deadline - task.created_at.replace(second=0, microsecond=0)

        for subtask in self.task_set.all():
            planned_labor_intensity += subtask.planned_labor_intensity

        self.planned_labor_intensity = planned_labor_intensity
        models.Model.save(self)

        if self.parent:
            self.parent.calculate_planned_labor_intensity()

    def calculate_actual_completion_time(self):
        actual_completion_time = self.completed_at - self.created_at
        for subtask in self.task_set.all():
            actual_completion_time += subtask.actual_completion_time

        self.actual_completion_time = actual_completion_time
        models.Model.save(self)

    def get_absolute_url(self):
        return reverse('task_detail', args=[self.id])