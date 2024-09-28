from django.urls import path

from tasks.views import home_page, task_detail

urlpatterns = [
    path('', home_page, name='home'),
    path('task/<int:task_id>/', task_detail, name='task_detail'),
]