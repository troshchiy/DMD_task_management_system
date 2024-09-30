from tasks.models import Task
from tasks.forms import TaskForm, EmptyFieldErrorMessage
from .base import UnitTest


class TaskFormTest(UnitTest):
    def test_form_save(self):
        form = TaskForm(data=UnitTest.VALID_TASK_DATA)
        task = form.save()
        added_task = Task.objects.first()

        self.assertEqual(task, added_task)
        self.assertEqual(added_task.title, UnitTest.VALID_TASK_DATA['title'])
        self.assertEqual(added_task.description, UnitTest.VALID_TASK_DATA['description'])
        self.assertEqual(added_task.performers, UnitTest.VALID_TASK_DATA['performers'])
        self.assertEqual(
            added_task.deadline.strftime(UnitTest.DATETIME_FORMAT),
            UnitTest.VALID_TASK_DATA['deadline']
        )

    def test_form_renders_title_field(self):
        form = TaskForm()
        self.assertIn('placeholder="Title"', form.as_p())

    def test_form_renders_description_field(self):
        form = TaskForm()
        self.assertIn('placeholder="Description"', form.as_p())

    def test_form_renders_performers_field(self):
        form = TaskForm()
        self.assertIn('placeholder="Performers"', form.as_p())

    def test_form_renders_deadline_field(self):
        form = TaskForm()
        self.assertIn('placeholder="e.g. 2025-01-25 14:30"', form.as_p())

    def assert_form_validation_for_blank_field(self, form_instance, field_name):
        self.assertFalse(form_instance.is_valid())
        self.assertEqual(
            form_instance.errors[field_name],
            [str(EmptyFieldErrorMessage(field_name))]
        )

    def test_form_validation_for_blank_title(self):
        form = self.create_task_form_with_data(title='')
        self.assert_form_validation_for_blank_field(form, 'title')

    def test_form_validation_for_blank_description(self):
        form = self.create_task_form_with_data(description='')
        self.assert_form_validation_for_blank_field(form, 'description')

    def test_form_validation_for_blank_performers(self):
        form = self.create_task_form_with_data(performers='')
        self.assert_form_validation_for_blank_field(form, 'performers')

    def test_form_validation_for_blank_deadline(self):
        form = self.create_task_form_with_data(deadline='')
        self.assert_form_validation_for_blank_field(form, 'deadline')

