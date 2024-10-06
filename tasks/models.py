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
    status = models.CharField(max_length=2,
                              choices=Status.choices,
                              default=Status.ASSIGNED,
                              blank=True)
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
                with transaction.atomic():
                    try:
                        for subtask in self.task_set.all():
                            subtask.status = Task.Status.COMPLETED
                            subtask.save()
                        models.Model.save(self)
                    except ValidationError as e:
                        raise ValidationError(f'The subtask "{subtask.title}" cannot be completed. {e.messages[0]}')

        models.Model.save(self)
        if self.status == Task.Status.COMPLETED:
            self.completed_at = timezone.now()
            self.actual_completion_time = self.completed_at - self.created_at

        models.Model.save(self)
        self.calculate_planned_labor_intensity()

    def delete(self):
        models.Model.delete(self)
        if self.parent:
            self.parent.calculate_planned_labor_intensity()

    def calculate_planned_labor_intensity(self):
        planned_labor_intensity = Task.objects.get(id=self.id).deadline - self.created_at.replace(second=0, microsecond=0)
        for subtask in self.task_set.all():
            planned_labor_intensity += subtask.planned_labor_intensity

        self.planned_labor_intensity = planned_labor_intensity
        models.Model.save(self)

        if self.parent:
            self.parent.calculate_planned_labor_intensity()

    def get_planned_labor_intensity(self):
        days = self.planned_labor_intensity.days
        seconds = self.planned_labor_intensity.seconds
        hours, seconds = divmod(seconds, 3600)
        minutes, seconds = divmod(seconds, 60)
        return f'{days} days, {hours} hours, {minutes} minutes'

    def get_actual_completion_time(self):
        days = self.actual_completion_time.days
        seconds = self.actual_completion_time.seconds
        hours, seconds = divmod(seconds, 3600)
        minutes, seconds = divmod(seconds, 60)
        return f'{days} days, {hours} hours, {minutes} minutes'

    def get_completed_at(self):
        if self.completed_at:
            return self.completed_at.astimezone(datetime.timezone(datetime.timedelta(hours=7))).strftime('%Y-%m-%d %H:%M')

    def get_created_at(self):
        return self.created_at.astimezone(datetime.timezone(datetime.timedelta(hours=7))).strftime('%Y-%m-%d %H:%M')

    def get_absolute_url(self):
        return reverse('task_detail', args=[self.id])