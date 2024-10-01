from django.urls import path

from tasks import views
from tasks.views import new_task

urlpatterns = [
    path('new', views.new_task, name='new_task'),
    path('<int:task_id>/', views.task_detail, name='task_detail'),
]