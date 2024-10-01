from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseNotFound
from django.template.loader import render_to_string

from .models import Task
from .forms import TaskForm


def home_page(request):
    return render(request,'tasks/home.html', {'form': TaskForm(), 'tasks': Task.objects.all()})


def new_task(request):
    form = TaskForm(data=request.POST)
    if form.is_valid():
        form.save()
        return redirect('/')
    else:
        return render(request,'tasks/home.html', {'form': form, 'tasks': Task.objects.all()})


def task_detail(request, task_id):
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if is_ajax:
        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            return HttpResponseNotFound('Not Found')

        created_at = task.created_at.strftime('%Y-%m-%d %H:%M')
        form = render_to_string('tasks/task_detail.html', {'form': TaskForm(instance=task),
                                                                                    'created_at': created_at,
                                                                                    'add_subtask_form': TaskForm()})
        return JsonResponse({'form': form, 'url': task.get_absolute_url()})
    else:
        return HttpResponseBadRequest('Invalid request')
