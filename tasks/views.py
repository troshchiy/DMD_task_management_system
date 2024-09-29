from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseNotFound
from django.template.loader import render_to_string

from .models import Task
from .forms import TaskForm


def home_page(request):
    form = TaskForm()

    if request.method == 'POST':
        form = TaskForm(data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('/')

    tasks = Task.objects.all()
    return render(request,'tasks/home.html', {'form': form, 'tasks': tasks})


def task_detail(request, task_id):
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if is_ajax:
        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            return HttpResponseNotFound('Not Found')

        form = render_to_string('tasks/task_detail.html', {'form': TaskForm(instance=task)})
        return JsonResponse({'form': form})
    else:
        return HttpResponseBadRequest('Invalid request')
