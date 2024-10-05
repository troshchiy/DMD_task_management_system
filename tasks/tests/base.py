from django.test import TestCase
from tasks.models import Task
from tasks.forms import TaskForm


class UnitTest(TestCase):
    VALID_TASK_DATA = {
        'title': 'Buy tea',
        'description': 'Go to tea shop and buy puer tea',
        'performers': 'Vladislav Troshchiy',
        'deadline': '2024-10-02 20:00',
        'status': 'ASGD'
    }
    DATETIME_FORMAT = '%Y-%m-%d %H:%M'

    def create_task(self,
                    title=VALID_TASK_DATA['title'],
                    description=VALID_TASK_DATA['description'],
                    performers=VALID_TASK_DATA['performers'],
                    deadline=VALID_TASK_DATA['deadline'],
                    status=VALID_TASK_DATA['status'],
                    parent=None,
                    ):
        return Task(title=title,
                    description=description,
                    performers=performers,
                    deadline=deadline,
                    status=status,
                    parent=parent)

    def create_task_form_with_data(self,
                                   title=VALID_TASK_DATA['title'],
                                   description=VALID_TASK_DATA['description'],
                                   performers=VALID_TASK_DATA['performers'],
                                   deadline=VALID_TASK_DATA['deadline'],
                                   status=VALID_TASK_DATA['status']
                                   ):
        return TaskForm(data={'title': title,
                              'description': description,
                              'performers': performers,
                              'deadline': deadline,
                              'status': status})