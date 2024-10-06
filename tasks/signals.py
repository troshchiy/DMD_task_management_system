from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import Task

@receiver(post_delete, sender=Task)
def calculate_planned_labor_intensity(sender, instance, **kwargs):
    if instance.parent:
        instance.parent.calculate_planned_labor_intensity()
