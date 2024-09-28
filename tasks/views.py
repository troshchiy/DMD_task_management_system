from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponseBadRequest
from django.template.loader import render_to_string

from .models import Task
from .forms import TaskForm


def home_page(request):
    if request.method == 'POST':
        Task.objects.create(title=request.POST['title'])
        return redirect('/')
    form = TaskForm()
    tasks = Task.objects.all()
    return render(request,'tasks/home.html', {'form': form, 'tasks': tasks})


def task_detail(request, task_id):
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if is_ajax:
        task = Task.objects.get(id=task_id)
        form = render_to_string('tasks/task_detail.html', {'form': TaskForm(instance=task)})
        return JsonResponse({'form': form})
    else:
        return HttpResponseBadRequest('Invalid request')
