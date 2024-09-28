from django.shortcuts import render, redirect
from .models import Task
from .forms import TaskForm


def home_page(request):
    if request.method == 'POST':
        Task.objects.create(title=request.POST['title'])
        return redirect('/')
    form = TaskForm()
    tasks = Task.objects.all()
    return render(request,'tasks/home.html', {'form': form, 'tasks': tasks})


def get_task(request):
    task_id = request.POST.get('id')
