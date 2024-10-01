import json
import re

from django.http import JsonResponse
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
        self.assertIsInstance(response.context['task_form'], TaskForm)
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
        self.assertIsInstance(response.context['task_form'], TaskForm)

    def test_for_invalid_input_shows_errors_on_page(self):
        response = self.client.post('/tasks/new', data={'title': '', 'performers': '', 'deadline': ''})
        self.assertContains(response, escape(str(EmptyFieldErrorMessage('title'))))
        self.assertContains(response, escape(str(EmptyFieldErrorMessage('description'))))
        self.assertContains(response, escape(str(EmptyFieldErrorMessage('performers'))))
        self.assertContains(response, escape(str(EmptyFieldErrorMessage('deadline'))))


class NewSubtaskTest(UnitTest):
    def test_can_save_a_POST_request(self):
        task = self.create_task()
        task.save()

        subtask_data = {
            'title': 'Subtask 1',
            'description': 'Subtask Description 1',
            'performers': 'Subtask Performer 1',
            'deadline': '2020-12-25 10:00'
        }
        self.client.post(f'/tasks/{task.id}/subtasks/new', data=subtask_data)
        self.assertEqual(Task.objects.count(), 2)

        subtask = Task.objects.get(parent=task.id)
        self.assertEqual(subtask.title, subtask_data['title'])
        self.assertEqual(subtask.description, subtask_data['description'])
        self.assertEqual(subtask.performers, subtask_data['performers'])
        self.assertEqual(
            subtask.deadline.strftime(UnitTest.DATETIME_FORMAT),
            subtask_data['deadline']
        )

    def test_redirects_after_POST(self):
        task = self.create_task()
        task.save()

        subtask_data = {
            'title': 'Subtask 1',
            'description': 'Subtask Description 1',
            'performers': 'Subtask Performer 1',
            'deadline': '2020-12-25 10:00'
        }
        response = self.client.post(f'/tasks/{task.id}/subtasks/new', data=subtask_data)
        self.assertRedirects(response, f'/tasks/{task.id}/')

    def post_invalid_input(self):
        task = self.create_task()
        task.save()
        return self.client.post(f'/tasks/{task.id}/subtasks/new', data={})

    def test_for_invalid_input_nothing_saves_to_db(self):
        self.post_invalid_input()
        self.assertEqual(Task.objects.count(), 1)

    def test_for_invalid_input_renders_home_template(self):
        response = self.post_invalid_input()
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tasks/home.html')

    def test_for_invalid_input_passes_task_form_to_template(self):
        response = self.post_invalid_input()
        self.assertIsInstance(response.context['task_form'], TaskForm)

    def test_for_invalid_input_passes_task_detail_to_template(self):
        task = self.create_task()
        task.save()
        response = self.post_invalid_input()
        self.assertIsInstance(response.context['task_detail']['form'], TaskForm)
        self.assertEqual(
            response.context['task_detail']['created_at'],
            task.created_at.strftime(UnitTest.DATETIME_FORMAT)
        )

    def test_for_invalid_input_passes_subtask_form_to_template(self):
        response = self.post_invalid_input()
        self.assertIsInstance(response.context['subtask_form'], TaskForm)

    def test_for_invalid_input_shows_errors_on_page(self):
        response = self.post_invalid_input()
        self.assertContains(response, escape(str(EmptyFieldErrorMessage('title'))))
        self.assertContains(response, escape(str(EmptyFieldErrorMessage('description'))))
        self.assertContains(response, escape(str(EmptyFieldErrorMessage('performers'))))
        self.assertContains(response, escape(str(EmptyFieldErrorMessage('deadline'))))


class TaskDetailTest(UnitTest):
    def ajax_get(self, task_id):
        return self.client.get(f'/tasks/{task_id}/', headers={'X-Requested-With': 'XMLHttpRequest'})

    def test_returns_JSONResponse_on_AJAX_requests(self):
        task = self.create_task()
        task.save()

        ajax_response = self.ajax_get(task.id)
        self.assertEqual(ajax_response.status_code, 200)
        self.assertIsInstance(ajax_response, JsonResponse)

    def test_uses_task_detail_template_on_AJAX_responses(self):
        task = self.create_task()
        task.save()
        response = self.ajax_get(task.id)

        form = json.loads(response.content)['form']
        expected_form = render_to_string(
            'tasks/task_detail.html',
            {
            'task_detail': {
                'form': TaskForm(instance=task),
                'created_at': task.created_at.strftime('%Y-%m-%d %H:%M')
            },
            'subtask_form': TaskForm()
            }
        )

        csrf_token_input = re.findall('<input type="hidden" name="csrfmiddlewaretoken".*?>', form)[0]
        form_without_csrf = form.replace(csrf_token_input, '')  # render_to_string can't render csrf token without request object

        self.assertEqual(form_without_csrf, expected_form)

    def test_passes_correct_task_to_template(self):
        other_task = self.create_task(title='Other task')
        other_task.save()
        correct_task = self.create_task(title='Correct task')
        correct_task.save()

        response = self.client.get(f'/tasks/{correct_task.id}/')
        self.assertEqual(response.context['task_detail']['form'].instance, correct_task)

        ajax_response = self.ajax_get(correct_task.id)
        ajax_response_json = json.loads(ajax_response.content)
        self.assertIn(correct_task.title, ajax_response_json['form'])
        self.assertNotIn(other_task.title, ajax_response_json['form'])

    def test_passes_correct_created_at_value_to_template(self):
        task = self.create_task()
        task.save()

        response = self.client.get(f'/tasks/{task.id}/')
        self.assertEqual(
            response.context['task_detail']['created_at'],
            task.created_at.strftime(UnitTest.DATETIME_FORMAT)
        )

        ajax_response = self.ajax_get(task.id)
        form = json.loads(ajax_response.content)['form']
        self.assertIn(task.created_at.strftime(UnitTest.DATETIME_FORMAT), form)

    def test_passes_correct_url_to_ajax_response(self):
        task = self.create_task()
        task.save()

        response = self.ajax_get(task.id)

        url = json.loads(response.content)['url']
        self.assertEqual(url, f'/tasks/{task.id}/')

    def test_shows_task_detail_form_on_page(self):
        task = self.create_task()
        task.save()

        response = self.ajax_get(task.id)

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

        response = self.ajax_get(task.id)

        form = json.loads(response.content)['form']
        self.assertIn('id="add-subtask"', form)
        add_subtask_form = re.findall('<form id="add-subtask".*?</form>',
                                   form.replace('\t', ' ').replace('\n', ' '))[0]
        self.assertIn('id="id_title"', add_subtask_form)
        self.assertIn('id="id_description"', add_subtask_form)
        self.assertIn('id="id_performers"', add_subtask_form)
        self.assertIn('id="id_deadline"', add_subtask_form)

    def test_for_not_existing_task_id_returns_http404(self):
        ajax_response = self.client.get('/tasks/532/', headers={'X-Requested-With': 'XMLHttpRequest'})
        self.assertEqual(ajax_response.status_code, 404)
        self.assertIn( 'Not Found', ajax_response.content.decode('utf8'))

        response = self.client.get('/tasks/532/')
        self.assertEqual(response.status_code, 404)
        self.assertIn( 'Not Found', response.content.decode('utf8'))
