from datetime import timezone, timedelta
import zoneinfo

from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.contrib import messages

from .models import Task
from .forms import TaskForm


def home_page(request):
    return render(request,'tasks/home.html', {'task_form': TaskForm(),
                                              'tasks': Task.objects.filter(parent__isnull=True)})


def new_task(request):
    task_form = TaskForm(data=request.POST)
    if task_form.is_valid():
        task_form.save()
        return redirect('/')
    else:
        return render(request,'tasks/home.html', {'task_form': task_form,
                                                  'tasks': Task.objects.filter(parent__isnull=True)})


def new_subtask(request, task_id):
    task = get_object_or_404(Task, id=task_id)

    subtask_form = TaskForm(data=request.POST)
    if subtask_form.is_valid():
        subtask_form.instance.parent = task
        subtask_form.save()
        return redirect(task)

    return render(request, 'tasks/home.html', {'task_form': TaskForm(),
                                                'task_detail_form': TaskForm(instance=task),
                                                'subtask_form': subtask_form,
                                                'tasks': Task.objects.filter(parent__isnull=True)})


def task_detail(request, task_id):
    task = get_object_or_404(Task, id=task_id)

    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if is_ajax:
        form = render_to_string('tasks/task_detail.html',
                                {'task_detail_form': TaskForm(instance=task), 'subtask_form': TaskForm()},
                                request=request)
        return JsonResponse({'form': form, 'url': task.get_absolute_url()})
    else:
        task_detail_form = TaskForm(instance=task)
        if request.method == 'POST':
            task_detail_form = TaskForm(instance=task, data=request.POST)

            if task_detail_form.is_valid():
                try:
                    task_detail_form.save()
                    return redirect(task)
                except ValidationError as e:
                    task_detail_form.add_error(None, e)

        return render(request, 'tasks/home.html', {'task_form': TaskForm(),
                                                   'task_detail_form': task_detail_form,
                                                    'subtask_form': TaskForm(),
                                                    'tasks': Task.objects.filter(parent__isnull=True)})


def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    if 'delete' in request.POST:
        task.delete()
        return redirect('/')
    else:
        messages.error(request, 'Error deleting the task')

    return render(request, 'tasks/home.html', {'task_form': TaskForm(),
                                                'task_detail_form': TaskForm(instance=task),
                                                'subtask_form': TaskForm(),
                                                'tasks': Task.objects.filter(parent__isnull=True)})
