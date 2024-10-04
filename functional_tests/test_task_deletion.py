from selenium.webdriver.common.by import By

from .base import FunctionalTest


class TaskDeletionTest(FunctionalTest):
    def test_can_delete_a_task(self):
        # User goes to homepage of the web-application and creates task 'Brew the tea'
        self.browser.get(self.live_server_url)
        add_task_form = self.wait_for(lambda: self.browser.find_element(By.ID, 'add-task'))
        self.add_task(
            form=add_task_form,
            title='Brew the tea',
            description='Place 10g of tea into the tea pot and steep tea between 3 to 5 minutes.',
            performers='Vladislav Troshchiy',
            deadline='2024-10-03 13:00'
        )

        # He opens the task detail page by clicking on item 'Brew the tea' at the sidebar tasks list
        self.wait_for_item_in_tasks_list('Brew the tea').click()

        # And he creates two subtasks: 'Heat water' and 'Steep the tea'
        add_subtask_form = self.wait_for(lambda: self.browser.find_element(By.ID, 'add-subtask'))
        self.add_task(
            form=add_subtask_form,
            title='Heat water',
            description='Heat water to 94 degrees C',
            performers='Troshchiy Vladislav',
            deadline='2024-10-03 12:50'
        )

        add_subtask_form = self.wait_for(lambda: self.browser.find_element(By.ID, 'add-subtask'))
        self.add_task(
            form=add_subtask_form,
            title='Steep the tea',
            description='Pour the heated water over the tea leaves and steep tea between 3 to 5 minutes.',
            performers='Vladislav',
            deadline='2024-10-04 13:00'
        )

        # Suddenly, user decides to delete the task for some reason
        # He finds 'Delete task' button on the task detail page
        delete_task_btn = self.wait_for(lambda: self.browser.find_element(By.ID, 'delete-task-btn'))

        # And user presses the button
        delete_task_btn.click()

        # The page updates and shows homepage
        self.wait_for(
            lambda: self.assertEqual(self.browser.current_url, f'{self.live_server_url}/')
        )

        # User noticed that there isn't 'Brew the tea' task item at the sidebar tasks list
        tasks_list = self.browser.find_element(By.ID, 'tasks-list')
        items = tasks_list.find_elements(By.CLASS_NAME, 'task-title')
        items_text = [item.text for item in items]

        self.assertNotIn('Brew the tea', items_text)

        # Although, there are two tasks: 'Heat water' and 'Steep the tea'
        self.assertIn('Heat water', items_text)
        self.assertIn('Steep the tea', items_text)
