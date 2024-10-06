from django import template
from tasks.models import Task

register = template.Library()

@register.simple_tag
def get_tasks():
    return Task.objects.filter(parent__isnull=True)
