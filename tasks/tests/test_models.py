from django.test import TestCase
from django.core.exceptions import ValidationError

from tasks.models import Task


class TaskModelTest(TestCase):
    def test_cannot_save_tasks_with_empty_title(self):
        task = Task(title='')

        with self.assertRaises(ValidationError):
            task.save()
            task.full_clean()
