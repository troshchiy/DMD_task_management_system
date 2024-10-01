import datetime

from django.core.exceptions import ValidationError
from django.utils import timezone

from tasks.models import Task
from .base import UnitTest


class TaskModelTest(UnitTest):
    def test_can_save_task(self):
        task = self.create_task()
        task.full_clean()
        task.save()

        saved_task = Task.objects.first()
        self.assertEqual(task, saved_task)
        self.assertEqual(UnitTest.VALID_TASK_DATA['title'], saved_task.title)
        self.assertEqual(UnitTest.VALID_TASK_DATA['description'], saved_task.description)
        self.assertEqual(UnitTest.VALID_TASK_DATA['performers'], saved_task.performers)
        self.assertEqual(
            UnitTest.VALID_TASK_DATA['deadline'],
            saved_task.deadline.strftime(UnitTest.DATETIME_FORMAT)
        )

    def assert_cannot_save_task_with_blank_field(self, task_instance, field_name):
        with self.assertRaises(ValidationError) as assert_raises_context:
            task_instance.full_clean()

        self.assertIn(field_name, assert_raises_context.exception.error_dict)
        self.assertEqual(
            ['This field cannot be blank.'],
            assert_raises_context.exception.message_dict[field_name]
        )

    def assert_cannot_save_task_with_null_field(self, task_instance, field_name):
        with self.assertRaises(ValidationError) as context:
            task_instance.full_clean()

        self.assertIn(field_name, context.exception.error_dict)
        self.assertEqual(['This field cannot be null.'], context.exception.message_dict[field_name])

    def test_cannot_save_tasks_with_blank_or_null_title(self):
        blank_title_task = self.create_task(title='')
        null_title_task = self.create_task(title=None)

        self.assert_cannot_save_task_with_blank_field(blank_title_task, 'title')
        self.assert_cannot_save_task_with_null_field(null_title_task, 'title')

    def test_cannot_save_tasks_with_blank_or_null_performers(self):
        blank_performers_task = self.create_task(performers='')
        null_performers_task = self.create_task(performers=None)

        self.assert_cannot_save_task_with_blank_field(blank_performers_task, 'performers')
        self.assert_cannot_save_task_with_null_field(null_performers_task, 'performers')

    def test_cannot_save_tasks_with_blank_or_null_description(self):
        blank_description_task = self.create_task(description='')
        null_description_task = self.create_task(description=None)

        self.assert_cannot_save_task_with_blank_field(blank_description_task, 'description')
        self.assert_cannot_save_task_with_null_field(null_description_task, 'description')

    def test_cannot_save_tasks_with_null_deadline(self):
        null_deadline_task = self.create_task(deadline=None)

        self.assert_cannot_save_task_with_null_field(null_deadline_task, 'deadline')

    def test_automatically_set_created_at_field_value(self):
        self.create_task().save()

        task = Task.objects.first()
        self.assertAlmostEqual(task.created_at, timezone.now(), delta=datetime.timedelta(seconds=1))

    def test_get_absolute_url(self):
        task = self.create_task()
        task.save()
        self.assertEqual(task.get_absolute_url(), f'/tasks/{task.id}/')
