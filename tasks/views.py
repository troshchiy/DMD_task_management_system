from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.template.loader import render_to_string

from .models import Task
from .forms import TaskForm


def home_page(request):
    return render(request,'tasks/home.html', {'task_form': TaskForm(), 'tasks': Task.objects.all()})


def new_task(request):
    task_form = TaskForm(data=request.POST)
    if task_form.is_valid():
        task_form.save()
        return redirect('/')
    else:
        return render(request,'tasks/home.html', {'task_form': task_form, 'tasks': Task.objects.all()})


def new_subtask(request, task_id):
    task = get_object_or_404(Task, id=task_id)

    subtask_form = TaskForm(data=request.POST)
    if subtask_form.is_valid():
        subtask_form.instance.parent = task
        subtask_form.save()
        return redirect(task)

    return render(request, 'tasks/home.html', {
                                                'task_form': TaskForm(),
                                                'task_detail': {
                                                    'form': TaskForm(instance=task),
                                                    'created_at': task.created_at.strftime('%Y-%m-%d %H:%M')
                                                    },
                                                'subtask_form': subtask_form,
                                                'tasks': Task.objects.all()
                                               })


def task_detail(request, task_id):
    task = get_object_or_404(Task, id=task_id)

    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if is_ajax:
        created_at = task.created_at.strftime('%Y-%m-%d %H:%M')
        form = render_to_string(
            'tasks/task_detail.html',
            {
            'task_detail': {
                'form': TaskForm(instance=task),
                'created_at': created_at
                },
            'subtask_form': TaskForm()
            },
            request=request
        )
        return JsonResponse({'form': form, 'url': task.get_absolute_url()})
    else:
        return render(request,
                      'tasks/home.html',
                      {
                          'task_form': TaskForm(),
                          'task_detail': {
                              'form': TaskForm(instance=task),
                              'created_at': task.created_at.strftime('%Y-%m-%d %H:%M')
                          },
                          'subtask_form': TaskForm(),
                          'tasks': Task.objects.all()
                      })
