from django.test import TestCase
from tasks.models import Task
from tasks.forms import TaskForm


class UnitTest(TestCase):
    valid_task_data = {
        'title': 'Buy tea',
        'description': 'Go to tea shop and buy puer tea',
        'performers': 'Vladislav Troshchiy',
        'deadline': '2024-10-02 20:00'
    }

    def create_task(self,
                    title=valid_task_data['title'],
                    description=valid_task_data['description'],
                    performers=valid_task_data['performers'],
                    deadline=valid_task_data['deadline']
                    ):
        return Task(title=title, description=description, performers=performers, deadline=deadline)

    def create_task_form_with_data(self,
                                   title=valid_task_data['title'],
                                   description=valid_task_data['description'],
                                   performers=valid_task_data['performers'],
                                   deadline=valid_task_data['deadline']
                                   ):
        return TaskForm(data={'title': title,
                              'description': description,
                              'performers': performers,
                              'deadline': deadline})