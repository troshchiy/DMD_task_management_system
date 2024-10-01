import json
import re

from django.template.loader import render_to_string
from django.utils.html import escape

from tasks.models import Task
from tasks.forms import TaskForm, EmptyFieldErrorMessage
from .base import UnitTest


class HomePageTest(UnitTest):
    def test_uses_home_template(self):
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'tasks/home.html')

    def test_displays_task_form(self):
        response = self.client.get('/')
        self.assertIsInstance(response.context['form'], TaskForm)
        self.assertContains(response, 'name="title"')

    def test_shows_fields_on_page(self):
        response = self.client.get('/')
        self.assertContains(response, 'placeholder="Title"')
        self.assertContains(response, 'placeholder="Description"')
        self.assertContains(response, 'placeholder="Performers"')
        self.assertContains(response, 'placeholder="e.g. 2025-01-25 14:30"')


class NewTaskTest(UnitTest):
    def test_can_save_a_POST_request(self):
        self.client.post('/tasks/new', data=UnitTest.VALID_TASK_DATA)

        self.assertEqual(Task.objects.count(), 1)
        added_task = Task.objects.first()
        self.assertEqual(added_task.title, UnitTest.VALID_TASK_DATA['title'])
        self.assertEqual(added_task.description, UnitTest.VALID_TASK_DATA['description'])
        self.assertEqual(added_task.performers, UnitTest.VALID_TASK_DATA['performers'])
        self.assertEqual(
            added_task.deadline.strftime(UnitTest.DATETIME_FORMAT),
            UnitTest.VALID_TASK_DATA['deadline']
        )

    def test_redirects_after_POST(self):
        response = self.client.post('/tasks/new', data=UnitTest.VALID_TASK_DATA)
        self.assertRedirects(response, '/')

    def test_for_invalid_input_nothing_saved_to_db(self):
        self.client.post('/tasks/new', data={'title': ''})
        self.assertEqual(Task.objects.count(), 0)

    def test_for_invalid_input_renders_home_template(self):
        response = self.client.post('/tasks/new', data={'title': ''})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tasks/home.html')

    def test_for_invalid_input_passes_form_to_template(self):
        response = self.client.post('/tasks/new', data={'title': ''})
        self.assertIsInstance(response.context['form'], TaskForm)

    def test_for_invalid_input_shows_errors_on_page(self):
        response = self.client.post('/tasks/new', data={'title': '', 'performers': '', 'deadline': ''})
        self.assertContains(response, escape(str(EmptyFieldErrorMessage('title'))))
        self.assertContains(response, escape(str(EmptyFieldErrorMessage('performers'))))
        self.assertContains(response, escape(str(EmptyFieldErrorMessage('deadline'))))


class TaskDetailTest(UnitTest):
    def test_handles_only_AJAX_requests(self):
        task = self.create_task()
        task.save()

        ajax_response = self.client.get(f'/tasks/{task.id}/', headers={'X-Requested-With': 'XMLHttpRequest'})
        self.assertEqual(ajax_response.status_code, 200)

        not_ajax_response = self.client.get(f'/tasks/{task.id}/')
        self.assertEqual(not_ajax_response.status_code, 400)
        self.assertEqual(
            'Invalid request',
            not_ajax_response.content.decode('utf8')
        )

    def test_uses_task_detail_template(self):
        task = self.create_task()
        task.save()
        response = self.client.get(f'/tasks/{task.id}/', headers={'X-Requested-With': 'XMLHttpRequest'})

        form = json.loads(response.content)['form']
        expected_form = render_to_string('tasks/task_detail.html',
                                         {'form': TaskForm(instance=task),
                                                    'created_at': task.created_at.strftime('%Y-%m-%d %H:%M'),
                                                    'add_subtask_form': TaskForm()})

        self.assertEqual(form, expected_form)

    def test_passes_correct_task_to_template(self):
        other_task = self.create_task(title='Other task')
        other_task.save()
        correct_task = self.create_task(title='Correct task')
        correct_task.save()

        response = self.client.get(f'/tasks/{correct_task.id}/', headers={'X-Requested-With': 'XMLHttpRequest'})
        form = json.loads(response.content)['form']

        self.assertIn(correct_task.title, form)
        self.assertNotIn(other_task.title, form)

    def test_passes_correct_created_at_value_to_template(self):
        task = self.create_task()
        task.save()

        response = self.client.get(f'/tasks/{task.id}/', headers={'X-Requested-With': 'XMLHttpRequest'})

        form = json.loads(response.content)['form']
        self.assertIn(task.created_at.strftime(UnitTest.DATETIME_FORMAT), form)

    def test_shows_task_detail_form_on_page(self):
        task = self.create_task()
        task.save()

        response = self.client.get(f'/tasks/{task.id}/', headers={'X-Requested-With': 'XMLHttpRequest'})

        form = json.loads(response.content)['form']
        self.assertIn('id="task-detail"', form)
        add_task_form = re.findall('<form id="task-detail".*?</form>',
                                   form.replace('\t', ' ').replace('\n', ' '))[0]
        self.assertIn('id="id_title"', add_task_form)
        self.assertIn('id="id_description"', add_task_form)
        self.assertIn('id="id_performers"', add_task_form)
        self.assertIn('id="id_deadline"', add_task_form)
        self.assertIn('id="id_created_at"', add_task_form)

    def test_shows_add_subtask_form_on_page(self):
        task = self.create_task()
        task.save()

        response = self.client.get(f'/tasks/{task.id}/', headers={'X-Requested-With': 'XMLHttpRequest'})

        form = json.loads(response.content)['form']
        self.assertIn('id="add-subtask"', form)
        add_subtask_form = re.findall('<form id="add-subtask".*?</form>',
                                   form.replace('\t', ' ').replace('\n', ' '))[0]
        self.assertIn('id="id_title"', add_subtask_form)
        self.assertIn('id="id_description"', add_subtask_form)
        self.assertIn('id="id_performers"', add_subtask_form)
        self.assertIn('id="id_deadline"', add_subtask_form)

    def test_for_not_existing_task_id_returns_http404(self):
        response = self.client.get(f'/tasks/532/', headers={'X-Requested-With': 'XMLHttpRequest'})
        self.assertEqual(response.status_code, 404)
        self.assertEqual('Not Found', response.content.decode('utf8'))

