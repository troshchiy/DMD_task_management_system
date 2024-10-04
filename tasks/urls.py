from django.urls import path

from tasks import views
from tasks.views import new_task

urlpatterns = [
    path('new', views.new_task, name='new_task'),
    path('<int:task_id>/', views.task_detail, name='task_detail'),
    path('<int:task_id>/subtasks/new', views.new_subtask, name='new_subtask'),
    path('<int:task_id>/delete', views.delete_task, name='delete_task'),
]