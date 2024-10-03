import time
from datetime import datetime

from selenium.webdriver.common.by import By

from .base import FunctionalTest


class TaskEditingTest(FunctionalTest):
    def test_can_edit_a_task(self):
        # User goes to homepage of the web-application and creates a task
        self.browser.get(self.live_server_url)
        add_task_form = self.wait_for(lambda: self.browser.find_element(By.ID, 'add-task'))
        self.add_task(
            form=add_task_form,
            title='Old title',
            description='Old description',
            performers='Old performers',
            deadline='1999-12-21 17:15'
        )

        # User choose the added task at the sidebar tasks list to open task details
        self.wait_for_item_in_tasks_list('Old title').click()

        # User decides to change all task details
        # He edits task title, description, performers and deadline
        task_detail = self.wait_for(lambda: self.browser.find_element(By.ID, 'task-detail'))
        old_task_created_at = task_detail.find_element(By.ID, 'id_created_at').text
        edit_data = {
            'title': 'New title',
            'description': 'New description',
            'performers': 'New performers',
            'deadline': '2025-01-29 08:00'
        }

        title_inputbox = task_detail.find_element(By.ID, 'id_title')
        title_inputbox.clear()
        title_inputbox.send_keys(edit_data['title'])

        description_inputbox = task_detail.find_element(By.ID, 'id_description')
        description_inputbox.clear()
        description_inputbox.send_keys(edit_data['description'])

        performers_inputbox = task_detail.find_element(By.ID, 'id_performers')
        performers_inputbox.clear()
        performers_inputbox.send_keys(edit_data['performers'])

        deadline_inputbox = task_detail.find_element(By.ID, 'id_deadline')
        deadline_inputbox.clear()
        deadline_inputbox.send_keys(edit_data['deadline'])

        # Then User submit changes via "Save" button
        save_btn = task_detail.find_element(By.CLASS_NAME, 'submit-btn')
        self.assertEqual(save_btn.get_attribute('value'), 'Save')
        save_btn.click()

        # The page updates and now shows new task details, but created_at value hasn't changed
        self.wait_for(
            lambda: self.assert_task_details_equals_to(
                title=edit_data['title'],
                description=edit_data['description'],
                performers=edit_data['performers'],
                deadline=edit_data['deadline'],
                created_at=datetime.strptime(old_task_created_at, '%Y-%m-%d %H:%M')
            )
        )

        # User notices that there is still only one task at the sidebar tasks list, and it's title has changed too
        tasks_list = self.browser.find_element(By.ID, 'tasks-list')
        items = tasks_list.find_elements(By.CLASS_NAME, 'task-title')
        self.assertEqual(len(items), 1)
        self.assertIn('New title', [item.text for item in items])
        self.assertNotIn('Old title', [item.text for item in items])
