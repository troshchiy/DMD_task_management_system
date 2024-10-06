import json
import re
from datetime import timezone, timedelta

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
        self.assertContains(response, 'class="submit-btn"')

    def test_passes_only_tasks_with_null_parent(self):
        task = self.create_task()
        task.save()
        subtask = self.create_task(parent=task)
        subtask.save()

        response = self.client.get('/')

        self.assertIn(task, response.context['tasks'])
        self.assertNotIn(subtask, response.context['tasks'])


class NewTaskTest(UnitTest):
    def test_can_save_a_POST_request(self):
        self.client.post('/tasks/new', data=UnitTest.VALID_TASK_DATA)

        self.assertEqual(Task.objects.count(), 1)
        added_task = Task.objects.first()
        self.assertEqual(added_task.title, UnitTest.VALID_TASK_DATA['title'])
        self.assertEqual(added_task.description, UnitTest.VALID_TASK_DATA['description'])
        self.assertEqual(added_task.performers, UnitTest.VALID_TASK_DATA['performers'])
        self.assertEqual(
            added_task.deadline.astimezone(timezone(timedelta(hours=7))).strftime(UnitTest.DATETIME_FORMAT),
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

    def test_for_invalid_input_passes_to_template_only_tasks_with_null_parent(self):
        task = self.create_task()
        task.save()
        subtask = self.create_task(parent=task)
        subtask.save()

        response = self.client.post('/tasks/new', data={})

        self.assertIn(task, response.context['tasks'])
        self.assertNotIn(subtask, response.context['tasks'])


class NewSubtaskTest(UnitTest):
    def test_can_save_a_POST_request(self):
        task = self.create_task()
        task.save()

        subtask_data = {
            'title': 'Subtask 1',
            'description': 'Subtask Description 1',
            'performers': 'Subtask Performer 1',
            'deadline': '2020-12-25 10:00',
            'status': 'AS'
        }
        self.client.post(f'/tasks/{task.id}/subtasks/new', data=subtask_data)
        self.assertEqual(Task.objects.count(), 2)

        subtask = Task.objects.get(parent=task.id)
        self.assertEqual(subtask.title, subtask_data['title'])
        self.assertEqual(subtask.description, subtask_data['description'])
        self.assertEqual(subtask.performers, subtask_data['performers'])
        self.assertEqual(
            subtask.deadline.astimezone(timezone(timedelta(hours=7))).strftime(UnitTest.DATETIME_FORMAT),
            subtask_data['deadline']
        )

    def test_redirects_after_POST(self):
        task = self.create_task()
        task.save()

        subtask_data = {
            'title': 'Subtask 1',
            'description': 'Subtask Description 1',
            'performers': 'Subtask Performer 1',
            'deadline': '2020-12-25 10:00',
            'status': 'AS'
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
            task.created_at.astimezone(timezone(timedelta(hours=7))).strftime(UnitTest.DATETIME_FORMAT)
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

    def test_for_invalid_input_passes_to_template_only_tasks_with_null_parent(self):
        task = self.create_task()
        task.save()
        subtask = self.create_task(parent=task)
        subtask.save()

        response = self.post_invalid_input()

        self.assertIn(task, response.context['tasks'])
        self.assertNotIn(subtask, response.context['tasks'])


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
                'created_at': task.created_at.astimezone(timezone(timedelta(hours=7))).strftime('%Y-%m-%d %H:%M')
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
            task.created_at.astimezone(timezone(timedelta(hours=7))).strftime(UnitTest.DATETIME_FORMAT)
        )

        ajax_response = self.ajax_get(task.id)
        form = json.loads(ajax_response.content)['form']
        self.assertIn(task.created_at.astimezone(timezone(timedelta(hours=7))).strftime(UnitTest.DATETIME_FORMAT), form)

    def test_passes_correct_url_to_ajax_response(self):
        task = self.create_task()
        task.save()

        response = self.ajax_get(task.id)

        url = json.loads(response.content)['url']
        self.assertEqual(url, f'/tasks/{task.id}/')

    def test_for_AJAX_shows_task_detail_form_on_page(self):
        task = self.create_task()
        task.save()

        ajax_response = self.ajax_get(task.id)

        form = json.loads(ajax_response.content)['form']
        self.assertIn('id="task-detail"', form)
        task_detail_form = re.findall('<form id="task-detail".*?</form>',
                                   form.replace('\t', ' ').replace('\n', ' '))[0]
        self.assertIn('id="id_title"', task_detail_form)
        self.assertIn('id="id_description"', task_detail_form)
        self.assertIn('id="id_performers"', task_detail_form)
        self.assertIn('id="id_deadline"', task_detail_form)
        self.assertIn('id="id_created_at"', task_detail_form)
        self.assertIn('id="id_status"', task_detail_form)
        self.assertIn('class="submit-btn"', task_detail_form)
        self.assertIn('id="id_planned_labor_intensity"', task_detail_form)
        self.assertIn('id="id_created_at"', task_detail_form)

    def test_for_AJAX_shows_correct_completed_at_value(self):
        task = self.create_task(status='CM')
        task.save(clean=False)

        ajax_response = self.ajax_get(task.id)
        form = json.loads(ajax_response.content)['form']

        task = Task.objects.first()
        expected_completed_at = task.completed_at
        actual_completed_at = re.findall('<div id="id_completed_at".*?>(.*?)</div>', form)[0]
        self.assertEqual(
            expected_completed_at.astimezone(timezone(timedelta(hours=7))).strftime(UnitTest.DATETIME_FORMAT),
            actual_completed_at
        )

    def test_for_AJAX_shows_correct_actual_completion_time_value(self):
        task = self.create_task(status='CM')
        task.save(clean=False)

        ajax_response = self.ajax_get(task.id)
        form = json.loads(ajax_response.content)['form']

        task = Task.objects.first()
        actual_completion_time = re.findall('<div id="id_actual_completion_time".*?>(.*?)</div>', form)[0]
        self.assertEqual(
            task.get_actual_completion_time(),
            actual_completion_time
        )

    def test_for_AJAX_shows_correct_planned_labor_intensity_value(self):
        task = self.create_task()
        task.save()

        ajax_response = self.ajax_get(task.id)
        form = json.loads(ajax_response.content)['form']

        task = Task.objects.first()
        actual_planned_labor_intensity = re.findall('<div id="id_planned_labor_intensity".*?>(.*?)</div>', form)[0]
        self.assertEqual(
            task.get_planned_labor_intensity(),
            actual_planned_labor_intensity
        )

    def test_for_AJAX_shows_correct_planned_labor_intensity_value_when_creating_subtasks(self):
        task = self.create_task()
        task.save()
        subtask_1 = self.create_task(parent=task)
        subtask_1.save()
        subtask_2 = self.create_task(parent=task)
        subtask_2.save()

        ajax_response = self.ajax_get(task.id)
        form = json.loads(ajax_response.content)['form']

        task = Task.objects.get(id=task.id)
        actual_planned_labor_intensity = re.findall('<div id="id_planned_labor_intensity".*?>(.*?)</div>', form)[0]
        self.assertEqual(
            task.get_planned_labor_intensity(),
            actual_planned_labor_intensity
        )

    def test_for_AJAX_shows_correct_planned_labor_intensity_value_when_deleting_subtasks(self):
        task = self.create_task()
        task.save()
        subtask_1 = self.create_task(parent=task)
        subtask_1.save()
        subtask_2 = self.create_task(parent=task)
        subtask_2.save()

        subtask_2.delete()

        ajax_response = self.ajax_get(task.id)
        form = json.loads(ajax_response.content)['form']

        task = Task.objects.get(id=task.id)
        actual_planned_labor_intensity = re.findall('<div id="id_planned_labor_intensity".*?>(.*?)</div>', form)[0]
        self.assertEqual(
            task.get_planned_labor_intensity(),
            actual_planned_labor_intensity
        )

    def test_for_GET_shows_task_detail_form_on_page(self):
        task = self.create_task()
        task.save()

        response = self.client.get(f'/tasks/{task.id}/').content.decode('utf8')

        self.assertIn('id="task-detail"', response)
        task_detail_form = re.findall('<form id="task-detail".*?</form>',
                                   response.replace('\t', ' ').replace('\n', ' '))[0]
        self.assertIn('id="id_title"', task_detail_form)
        self.assertIn('id="id_description"', task_detail_form)
        self.assertIn('id="id_performers"', task_detail_form)
        self.assertIn('id="id_deadline"', task_detail_form)
        self.assertIn('id="id_created_at"', task_detail_form)
        self.assertIn('id="id_status"', task_detail_form)
        self.assertIn('class="submit-btn"', task_detail_form)
        self.assertIn('id="id_planned_labor_intensity"', task_detail_form)
        self.assertIn('id="id_created_at"', task_detail_form)

    def test_for_GET_shows_correct_planned_labor_intensity_value(self):
        task = self.create_task()
        task.save()

        response = self.client.get(f'/tasks/{task.id}/').content.decode('utf8')

        task = Task.objects.first()
        actual_planned_labor_intensity = re.findall('<div id="id_planned_labor_intensity".*?>(.*?)</div>', response)[0]
        self.assertEqual(
            task.get_planned_labor_intensity(),
            actual_planned_labor_intensity
        )

    def test_for_GET_shows_correct_planned_labor_intensity_value_when_creating_subtasks(self):
        task = self.create_task()
        task.save()
        subtask_1 = self.create_task(parent=task)
        subtask_1.save()
        subtask_2 = self.create_task(parent=task)
        subtask_2.save()

        response = self.client.get(f'/tasks/{task.id}/').content.decode('utf8')

        task = Task.objects.get(id=task.id)
        subtask_1 = Task.objects.get(id=subtask_1.id)
        subtask_2 = Task.objects.get(id=subtask_2.id)

        actual_planned_labor_intensity = re.findall('<div id="id_planned_labor_intensity".*?>(.*?)</div>', response)[0]
        self.assertEqual(
            task.get_planned_labor_intensity(),
            actual_planned_labor_intensity
        )

    def test_for_GET_shows_correct_planned_labor_intensity_value_when_deleting_subtasks(self):
        task = self.create_task()
        task.save()
        subtask_1 = self.create_task(parent=task)
        subtask_1.save()
        subtask_2 = self.create_task(parent=task)
        subtask_2.save()

        subtask_2.delete()

        response = self.client.get(f'/tasks/{task.id}/').content.decode('utf8')

        task = Task.objects.get(id=task.id)
        actual_planned_labor_intensity = re.findall('<div id="id_planned_labor_intensity".*?>(.*?)</div>', response)[0]
        self.assertEqual(
            task.get_planned_labor_intensity(),
            actual_planned_labor_intensity
        )

    def test_for_GET_shows_correct_actual_completion_time_value(self):
        task = self.create_task(status='CM')
        task.save(clean=False)

        response = self.client.get(f'/tasks/{task.id}/').content.decode('utf8')

        task = Task.objects.first()
        actual_completion_time = re.findall('<div id="id_actual_completion_time".*?>(.*?)</div>', response)[0]
        self.assertEqual(
            task.get_actual_completion_time(),
            actual_completion_time
        )

    def test_shows_add_subtask_form_on_page(self):
        task = self.create_task()
        task.save()

        ajax_response = self.ajax_get(task.id)

        form = json.loads(ajax_response.content)['form']
        self.assertIn('id="add-subtask"', form)
        add_subtask_form = re.findall('<form id="add-subtask".*?</form>',
                                   form.replace('\t', ' ').replace('\n', ' '))[0]
        self.assertIn('id="id_title"', add_subtask_form)
        self.assertIn('id="id_description"', add_subtask_form)
        self.assertIn('id="id_performers"', add_subtask_form)
        self.assertIn('id="id_deadline"', add_subtask_form)
        self.assertIn('class="submit-btn"', add_subtask_form)

        response = self.client.get(f'/tasks/{task.id}/').content.decode('utf8')
        self.assertIn('id="add-subtask"', response)
        add_subtask_form = re.findall('<form id="add-subtask".*?</form>',
                                   response.replace('\t', ' ').replace('\n', ' '))[0]
        self.assertIn('id="id_title"', add_subtask_form)
        self.assertIn('id="id_description"', add_subtask_form)
        self.assertIn('id="id_performers"', add_subtask_form)
        self.assertIn('id="id_deadline"', add_subtask_form)
        self.assertIn('class="submit-btn"', add_subtask_form)

    def test_for_not_existing_task_id_returns_http404(self):
        ajax_response = self.client.get('/tasks/532/', headers={'X-Requested-With': 'XMLHttpRequest'})
        self.assertEqual(ajax_response.status_code, 404)
        self.assertIn( 'Not Found', ajax_response.content.decode('utf8'))

        response = self.client.get('/tasks/532/')
        self.assertEqual(response.status_code, 404)
        self.assertIn( 'Not Found', response.content.decode('utf8'))

    def test_passes_to_home_template_only_tasks_with_null_parent(self):
        task = self.create_task()
        task.save()
        subtask = self.create_task(parent=task)
        subtask.save()

        response = self.client.get(f'/tasks/{task.id}/')

        self.assertIn(task, response.context['tasks'])
        self.assertNotIn(subtask, response.context['tasks'])

    def test_can_save_a_POST_request(self):
        task = self.create_task()
        task.save()

        new_data = {
            'title': 'New title',
            'description': 'New Description',
            'performers': 'New performers',
            'deadline': '2021-09-13 15:00',
            'status': 'PR'
        }
        self.client.post(f'/tasks/{task.id}/', data=new_data)
        self.assertEqual(Task.objects.count(), 1)


        edited_task = Task.objects.first()
        self.assertEqual(task, edited_task)
        self.assertEqual(edited_task.title, new_data['title'])
        self.assertEqual(edited_task.description, new_data['description'])
        self.assertEqual(edited_task.performers, new_data['performers'])
        self.assertEqual(
            edited_task.deadline.astimezone(timezone(timedelta(hours=7))).strftime(UnitTest.DATETIME_FORMAT),
            new_data['deadline']
        )

    def test_redirects_after_POST(self):
        task = self.create_task()
        task.save()

        new_data = {
            'title': 'New title',
            'description': 'New Description',
            'performers': 'New performers',
            'deadline': '2021-09-13 15:00',
            'status': 'PR'
        }
        response = self.client.post(f'/tasks/{task.id}/', data=new_data)
        self.assertRedirects(response, f'/tasks/{task.id}/')

    def post_invalid_input(self):
        task = self.create_task()
        task.save()
        return self.client.post(f'/tasks/{task.id}/', data={})

    def test_for_invalid_input_doesnt_change_task(self):
        task_data = {
            'title': 'Old title',
            'description': 'Old Description',
            'performers': 'Old performers',
            'deadline': '2021-09-13 15:00'
        }

        task = self.create_task(
            title=task_data['title'],
            description=task_data['description'],
            performers=task_data['performers'],
            deadline=task_data['deadline']
        )
        task.save()

        self.client.post(f'/tasks/{task.id}/', data={})

        edit_task = Task.objects.first()
        self.assertEqual(edit_task.title, task_data['title'])
        self.assertEqual(edit_task.description, task_data['description'])
        self.assertEqual(edit_task.performers, task_data['performers'])
        self.assertEqual(edit_task.deadline.astimezone(timezone(timedelta(hours=7))).strftime('%Y-%m-%d %H:%M'), task_data['deadline'])

    def test_for_invalid_input_renders_home_template(self):
        response = self.post_invalid_input()
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tasks/home.html')

    def test_for_invalid_input_passes_task_form_to_template(self):
        response = self.post_invalid_input()
        self.assertIsInstance(response.context['task_form'], TaskForm)

    def test_for_invalid_input_passes_task_detail_form_to_template(self):
        response = self.post_invalid_input()
        self.assertIsInstance(response.context['task_detail']['form'], TaskForm)

    def test_for_invalid_input_passes_subtask_form_to_template(self):
        response = self.post_invalid_input()
        self.assertIsInstance(response.context['subtask_form'], TaskForm)

    def test_for_invalid_input_shows_errors_on_page(self):
        response = self.post_invalid_input().content.decode('utf8')

        task_detail_form = re.findall('<form id="task-detail".*?</form>',
                                   response.replace('\t', ' ').replace('\n', ' '))[0]
        self.assertIn(
            escape(str(EmptyFieldErrorMessage('title'))),
            task_detail_form
        )
        self.assertIn(
            escape(str(EmptyFieldErrorMessage('description'))),
            task_detail_form
        )
        self.assertIn(
            escape(str(EmptyFieldErrorMessage('performers'))),
            task_detail_form
        )
        self.assertIn(
            escape(str(EmptyFieldErrorMessage('deadline'))),
            task_detail_form
        )

    def test_for_invalid_input_passes_to_template_only_tasks_with_null_parent(self):
        task = self.create_task()
        task.save()
        subtask = self.create_task(parent=task)
        subtask.save()

        response = self.post_invalid_input()

        self.assertIn(task, response.context['tasks'])
        self.assertNotIn(subtask, response.context['tasks'])

    def test_shows_error_on_page_when_task_cannot_be_SUSPENDED(self):
        task = self.create_task()
        task.save()

        new_data = UnitTest.VALID_TASK_DATA
        new_data['status'] = 'SP'

        response = self.client.post(f'/tasks/{task.id}/', data=new_data)
        self.assertContains(response, escape('The status "Suspended" can only be set after the status "In Progress".'))

    def test_shows_error_on_page_when_task_cannot_be_COMPLETED(self):
        task = self.create_task()
        task.save()

        new_data = UnitTest.VALID_TASK_DATA
        new_data['status'] = 'CM'

        response = self.client.post(f'/tasks/{task.id}/', data=new_data)
        self.assertContains(response, escape('The status "Completed" can only be set after the status "In Progress".'))

    def test_sets_subtasks_status_to_COMPLETED_when_task_is_completed(self):
        task = self.create_task(status='PR')
        task.save(clean=False)
        subtask_1 = self.create_task(parent=task, status='PR')
        subtask_1.save(clean=False)
        subtask_2 = self.create_task(parent=task, status='PR')
        subtask_2.save(clean=False)

        new_data = UnitTest.VALID_TASK_DATA
        new_data['status'] = 'CM'

        self.client.post(f'/tasks/{task.id}/', data=new_data)

        task = Task.objects.get(id=task.id)
        subtask_1 = Task.objects.get(id=subtask_1.id)
        subtask_2 = Task.objects.get(id=subtask_2.id)
        self.assertEqual(task.status, 'CM')
        self.assertEqual(subtask_1.status, 'CM')
        self.assertEqual(subtask_2.status, 'CM')

    def test_doesnt_change_status_if_any_of_subtasks_cannot_be_COMPLETED(self):
        task = self.create_task(status='PR')
        task.save(clean=False)
        subtask_1 = self.create_task(parent=task, status='PR')
        subtask_1.save(clean=False)
        subtask_2 = self.create_task(parent=task, status='AS')
        subtask_2.save(clean=False)

        new_data = UnitTest.VALID_TASK_DATA
        new_data['status'] = 'CM'

        self.client.post(f'/tasks/{task.id}/', data=new_data)

        task = Task.objects.get(id=task.id)
        subtask_1 = Task.objects.get(id=subtask_1.id)
        subtask_2 = Task.objects.get(id=subtask_2.id)
        self.assertEqual(task.status, 'PR')
        self.assertEqual(subtask_1.status, 'PR')
        self.assertEqual(subtask_2.status, 'AS')

    def test_shows_error_on_page_when_subtask_cannot_be_completed(self):
        task = self.create_task(status='PR')
        task.save(clean=False)
        subtask_1 = self.create_task(parent=task, status='PR')
        subtask_1.save(clean=False)
        subtask_2 = self.create_task(parent=task, status='AS')
        subtask_2.save(clean=False)

        new_data = UnitTest.VALID_TASK_DATA
        new_data['status'] = 'CM'

        response = self.client.post(f'/tasks/{task.id}/', data=new_data)

        self.assertContains(response,
                            escape(f'The subtask "{subtask_2.title}" cannot be completed. '
                                    f'The status "Completed" can only be set after the status "In Progress".'))


class DeleteTaskTest(UnitTest):
    def test_can_delete_task_via_POST_request(self):
        task = self.create_task()
        task.save()
        self.assertEqual(Task.objects.count(), 1)

        self.client.post(f'/tasks/{task.id}/delete', data={'delete': ''})

        self.assertEqual(Task.objects.count(), 0)

    def test_redirects_after_POST(self):
        task = self.create_task()
        task.save()

        response = self.client.post(f'/tasks/{task.id}/delete', data={'delete': ''})

        self.assertRedirects(response, '/')

    def test_for_invalid_POST_does_not_delete_task(self):
        task = self.create_task()
        task.save()
        self.assertEqual(Task.objects.count(), 1)

        self.client.post(f'/tasks/{task.id}/delete', data={})

        self.assertEqual(Task.objects.count(), 1)

    def post_invalid_data(self):
        task = self.create_task()
        task.save()
        return self.client.post(f'/tasks/{task.id}/delete', data={})

    def test_for_invalid_POST_renders_home_template(self):
        response = self.post_invalid_data()

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tasks/home.html')

    def test_for_invalid_POST_passes_task_form_to_template(self):
        response = self.post_invalid_data()
        self.assertIsInstance(response.context['task_form'], TaskForm)

    def test_for_invalid_POST_passes_task_detail_to_template(self):
        task = self.create_task()
        task.save()
        response = self.post_invalid_data()
        self.assertIsInstance(response.context['task_detail']['form'], TaskForm)
        self.assertEqual(
            response.context['task_detail']['created_at'],
            task.created_at.astimezone(timezone(timedelta(hours=7))).strftime(UnitTest.DATETIME_FORMAT)
        )

    def test_for_invalid_POST_passes_subtask_form_to_template(self):
        response = self.post_invalid_data()
        self.assertIsInstance(response.context['subtask_form'], TaskForm)

    def test_for_invalid_POST_shows_errors_on_page(self):
        response = self.post_invalid_data()
        self.assertContains(response, 'Error deleting the task')

    def test_for_invalid_POST_passes_to_template_only_tasks_with_null_parent(self):
        task = self.create_task()
        task.save()
        subtask = self.create_task(parent=task)
        subtask.save()

        response = self.client.post(f'/tasks/{task.id}/delete', data={})

        self.assertIn(task, response.context['tasks'])
        self.assertNotIn(subtask, response.context['tasks'])
