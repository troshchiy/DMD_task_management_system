import json

from django.template.loader import render_to_string
from django.test import TestCase

from tasks.models import Task
from tasks.forms import TaskForm


class HomePageTest(TestCase):
    def test_uses_home_template(self):
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'tasks/home.html')

    def test_displays_task_form(self):
        response = self.client.get('/')
        self.assertIsInstance(response.context['form'], TaskForm)
        self.assertContains(response, 'name="title"')

    def test_can_save_a_POST_request(self):
        self.client.post('/', data={'title': 'A new task'})

        self.assertEqual(Task.objects.count(), 1)
        new_task = Task.objects.first()
        self.assertEqual(new_task.title, 'A new task')

    def test_redirects_after_POST(self):
        response = self.client.post('/', data={'title': 'A new task'})
        self.assertRedirects(response, '/')


class TaskDetailTest(TestCase):
    def test_handles_only_AJAX_requests(self):
        task = Task.objects.create()

        ajax_response = self.client.get(f'/task/{task.id}/', headers={'X-Requested-With': 'XMLHttpRequest'})
        self.assertEqual(ajax_response.status_code, 200)

        not_ajax_response = self.client.get(f'/task/{task.id}/')
        self.assertEqual(not_ajax_response.status_code, 400)
        self.assertEqual(
            'Invalid request',
            not_ajax_response.content.decode('utf8')
        )

    def test_uses_task_detail_template(self):
        task = Task.objects.create()
        response = self.client.get(f'/task/{task.id}/', headers={'X-Requested-With': 'XMLHttpRequest'})

        form = json.loads(response.content)['form']
        expected_form = render_to_string('tasks/task_detail.html',
                                         {'form': TaskForm(instance=task)})

        self.assertEqual(form, expected_form)

    def test_passes_correct_task_to_template(self):
        other_task = Task.objects.create(title='Other task')
        correct_task = Task.objects.create(title='Correct task')

        response = self.client.get(f'/task/{correct_task.id}/', headers={'X-Requested-With': 'XMLHttpRequest'})
        form = json.loads(response.content)['form']

        self.assertIn(correct_task.title, form)
        self.assertNotIn(other_task.title, form)
