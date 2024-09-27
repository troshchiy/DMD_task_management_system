from django.shortcuts import render, redirect
from .models import Task


def home_page(request):
    if request.method == 'POST':
        Task.objects.create(title=request.POST['title'])
        return redirect('/')
    tasks = Task.objects.all()
    return render(request,'tasks/home.html', {'tasks': tasks})
