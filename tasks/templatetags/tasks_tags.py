from django import template
from tasks.models import Task

register = template.Library()

@register.simple_tag
def get_tasks():
    return Task.objects.filter(parent__isnull=True)


@register.filter
def duration(timedelta):
    days = timedelta.days
    seconds = timedelta.seconds
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    return f'{days} days, {hours} hours, {minutes} minutes'
