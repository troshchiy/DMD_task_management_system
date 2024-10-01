import datetime

from django.core.exceptions import ValidationError
from django.utils import timezone

from tasks.models import Task
from .base import UnitTest


class TaskModelTest(UnitTest):
    def test_can_save_task(self):
        task = self.create_task()
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

    def test_can_save_tasks_with_null_parent(self):
        self.create_task(parent=None).save()
        self.assertEqual(Task.objects.count(), 1)
        added_task = Task.objects.first()
        self.assertIsNone(added_task.parent)

    def test_default_parent(self):
        task = Task(
            title=UnitTest.VALID_TASK_DATA['title'],
            description=UnitTest.VALID_TASK_DATA['description'],
            performers=UnitTest.VALID_TASK_DATA['performers'],
            deadline=UnitTest.VALID_TASK_DATA['deadline']
        )
        self.assertIsNone(task.parent)

    def test_task_is_related_to_another_task(self):
        task = self.create_task()
        task.save()

        subtask = self.create_task(parent=task)
        subtask.save()

        self.assertIn(subtask, task.task_set.all())

    def test_sets_parent_null_on_delete(self):
        task = self.create_task()
        task.save()
        self.create_task(parent=task).save()

        task.delete()
        self.assertEqual(Task.objects.count(), 1)
        self.assertIsNone(Task.objects.first().parent)

    def test_automatically_set_created_at_field_value(self):
        self.create_task().save()

        task = Task.objects.first()
        self.assertAlmostEqual(task.created_at, timezone.now(), delta=datetime.timedelta(seconds=1))

    def test_get_absolute_url(self):
        task = self.create_task()
        task.save()
        self.assertEqual(task.get_absolute_url(), f'/tasks/{task.id}/')
