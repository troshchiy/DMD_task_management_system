import datetime
import zoneinfo
from datetime import tzinfo

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
            saved_task.deadline.astimezone(datetime.timezone(datetime.timedelta(hours=7))).strftime(UnitTest.DATETIME_FORMAT)
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
        task.full_clean()
        task.save()

        added_task = Task.objects.first()
        self.assertIsNone(added_task.parent)

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

    def test_automatically_sets_created_at_field_value(self):
        self.create_task().save()

        task = Task.objects.first()
        self.assertAlmostEqual(task.created_at, timezone.now(), delta=datetime.timedelta(seconds=1))

    def test_automatically_sets_planned_labor_intensity_field_value_when_creating_task(self):
        task = self.create_task()
        task.save()

        added_task = Task.objects.first()
        expected_planned_labor_intensity = added_task.deadline - added_task.created_at.replace(second=0, microsecond=0)
        self.assertEqual(added_task.planned_labor_intensity, expected_planned_labor_intensity)

    def test_automatically_sets_planned_labor_intensity_field_value_when_editing_task(self):
        task = self.create_task(deadline='2024-10-02 20:00')
        task.save()

        added_task = Task.objects.first()
        expected_planned_labor_intensity_1 = added_task.deadline - added_task.created_at.replace(second=0, microsecond=0)
        self.assertEqual(added_task.planned_labor_intensity, expected_planned_labor_intensity_1)

        task.deadline = datetime.datetime(2027, 5, 6, 16,10)
        task.save()

        edited_task = Task.objects.first()
        expected_planned_labor_intensity_2 = edited_task.deadline - edited_task.created_at.replace(second=0, microsecond=0)
        self.assertEqual(edited_task.planned_labor_intensity, expected_planned_labor_intensity_2)
        self.assertNotEqual(
            expected_planned_labor_intensity_1,
            expected_planned_labor_intensity_2
        )

    def test_automatically_edits_planned_labor_intensity_field_value_when_creating_subtasks(self):
        task = self.create_task()
        task.save()
        subtask_1 = self.create_task(parent=task)
        subtask_1.save()

        task = Task.objects.get(id=task.id)
        subtask_1 = Task.objects.get(id=subtask_1.id)
        expected_planned_labor_intensity = ((task.deadline - task.created_at.replace(second=0, microsecond=0))
                                            + (subtask_1.deadline - subtask_1.created_at.replace(second=0, microsecond=0)))
        self.assertEqual(task.planned_labor_intensity, expected_planned_labor_intensity)

        subtask_2 = self.create_task(parent=task)
        subtask_2.save()

        task = Task.objects.get(id=task.id)
        subtask_2 = Task.objects.get(id=subtask_2.id)
        expected_planned_labor_intensity = ((task.deadline - task.created_at.replace(second=0, microsecond=0))
                                            + (subtask_1.deadline - subtask_1.created_at.replace(second=0, microsecond=0))
                                            + (subtask_2.deadline - subtask_2.created_at.replace(second=0, microsecond=0)))
        self.assertEqual(task.planned_labor_intensity, expected_planned_labor_intensity)

    def test_automatically_edits_planned_labor_intensity_field_value_when_deleting_subtasks(self):
        task = self.create_task()
        task.save()
        subtask_1 = self.create_task(parent=task)
        subtask_1.save()

        task = Task.objects.get(id=task.id)
        subtask_1 = Task.objects.get(id=subtask_1.id)
        expected_planned_labor_intensity = ((task.deadline - task.created_at.replace(second=0, microsecond=0))
                                            + (subtask_1.deadline - subtask_1.created_at.replace(second=0, microsecond=0)))
        self.assertEqual(task.planned_labor_intensity, expected_planned_labor_intensity)

        subtask_1.delete()

        task = Task.objects.get(id=task.id)
        expected_planned_labor_intensity = task.deadline - task.created_at.replace(second=0, microsecond=0)
        self.assertEqual(task.planned_labor_intensity, expected_planned_labor_intensity)

    def test_automatically_sets_completed_at_field_value(self):
        self.create_task().save()

        task = Task.objects.first()
        self.assertIsNone(task.completed_at)

        task.status = 'CM'
        task.save(clean=False)

        task = Task.objects.first()
        self.assertAlmostEqual(task.completed_at, timezone.now(), delta=datetime.timedelta(seconds=1))

    def test_automatically_sets_actual_completion_time_field_value_when_completing_task(self):
        task = self.create_task(status='CM')
        task.save(clean=False)

        added_task = Task.objects.first()
        expected_actual_completion_time = added_task.completed_at - added_task.created_at
        self.assertEqual(added_task.actual_completion_time, expected_actual_completion_time)

    def test_sets_status_ASSIGNED_when_its_null(self):
        task = self.create_task(status=None)
        task.save()

        added_task = Task.objects.first()
        self.assertEqual(added_task.status, 'AS')

    def test_sets_status_ASSIGNED_when_its_blank(self):
        task = self.create_task(status='')
        task.save()

        added_task = Task.objects.first()
        self.assertEqual(added_task.status, 'AS')

    def test_acceptable_status_values(self):
        task = self.create_task()

        for status in ('AS', 'PR', 'SP', 'PR', 'CM'):
            task.status = status
            task.save()             # Should not raise ValidationError
            self.assertEqual(Task.objects.first().status, status)

    def test_cannot_save_task_with_invalid_status(self):
        task = self.create_task()

        invalid_status = 'NVLD'
        task.status = invalid_status

        with self.assertRaises(ValidationError) as context:
            task.full_clean()

        self.assertIn('status', context.exception.error_dict)
        self.assertEqual(
            [f"Value '{invalid_status}' is not a valid choice."],
            context.exception.message_dict['status']
        )

    def test_get_absolute_url(self):
        task = self.create_task()
        task.save()
        self.assertEqual(task.get_absolute_url(), f'/tasks/{task.id}/')

    def test_can_set_status_COMPLETED_only_after_IN_PROGRESS(self):
        task = self.create_task()
        task.save()

        task.status = 'CM'
        with self.assertRaises(ValidationError) as context:
            task.save()

        self.assertIn('status', context.exception.error_dict)
        self.assertEqual(
            ['The status "Completed" can only be set after the status "In Progress".'],
            context.exception.message_dict['status']
        )

    def test_can_set_status_SUSPENDED_only_after_IN_PROGRESS(self):
        task = self.create_task()
        task.save()

        task.status = 'SP'
        with self.assertRaises(ValidationError) as context:
            task.save()

        self.assertIn('status', context.exception.error_dict)
        self.assertEqual(
            ['The status "Suspended" can only be set after the status "In Progress".'],
            context.exception.message_dict['status']
        )

    def test_can_set_status_only_ASSIGNED_when_creating(self):
        task = self.create_task()

        for status in ('PR', 'SP', 'PR', 'CM'):
            task.status = status

            with self.assertRaises(ValidationError) as context:
                task.save()

            self.assertIn('status', context.exception.error_dict)
            self.assertEqual(
                [f'The status "{task.get_status_display()}" cannot be set when creating a task. '
                           'Only the status "Assigned" is available".'],
                context.exception.message_dict['status']
            )

    def test_sets_subtasks_status_to_COMPLETED_when_task_is_completed(self):
        task = self.create_task(status='PR')
        task.save(clean=False)
        subtask_1 = self.create_task(parent=task, status='PR')
        subtask_1.save(clean=False)
        subtask_2 = self.create_task(parent=task, status='PR')
        subtask_2.save(clean=False)

        task.status = 'CM'
        task.save()

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

        task.status = 'CM'
        with self.assertRaises(ValidationError) as context:
            task.save()

        self.assertEqual(
            f'The subtask "{subtask_2.title}" cannot be completed. '
             f'The status "Completed" can only be set after the status "In Progress".',
            context.exception.message
        )
