from django.test import TestCase

from tasks.models import Task
from tasks.forms import TaskForm, EMPTY_TITLE_ERROR


class TaskFormTest(TestCase):
    def test_form_renders_title_field(self):
        form = TaskForm()
        self.assertIn('placeholder="Title"', form.as_p())

    def test_form_validation_for_blank_title(self):
        form = TaskForm(data={'title': ''})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['title'], [EMPTY_TITLE_ERROR])

    def test_form_save(self):
        form = TaskForm(data={'title': 'hi'})
        new_task = form.save()
        self.assertEqual(new_task, Task.objects.first())
