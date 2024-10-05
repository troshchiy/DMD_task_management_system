import datetime

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from .base import FunctionalTest


class TaskCreationTest(FunctionalTest):
    def test_can_create_a_task(self):
        # User goes to homepage of the task management web-application
        self.browser.get(self.live_server_url)

        # User noticed that the page title and header mention the task management web-application
        self.assertIn('Tasks', self.browser.title)
        header_text = self.browser.find_element(By.TAG_NAME, 'h1').text
        self.assertIn('Tasks', header_text)

        # The website offers to enter a title, description, performers and deadline
        title_inputbox = self.get_new_task_element_by_id('id_title')
        self.assertEqual(
            title_inputbox.get_attribute('placeholder'),
            'Title'
        )

        description_inputbox = self.get_new_task_element_by_id('id_description')
        self.assertEqual(
            description_inputbox.get_attribute('placeholder'),
            'Description'
        )

        performers_inputbox = self.get_new_task_element_by_id('id_performers')
        self.assertEqual(
            performers_inputbox.get_attribute('placeholder'),
            'Performers'
        )

        deadline = self.get_new_task_element_by_id('deadline')
        deadline_label = deadline.find_element(By.TAG_NAME, 'label')
        self.assertEqual(deadline_label.text, 'Deadline:')

        deadline_inputbox = deadline.find_element(By.ID, 'id_deadline')
        self.assertEqual(
            deadline_inputbox.get_attribute('placeholder'),
            'e.g. 2025-01-25 14:30'
        )

        # User types "Buy tea" as a title
        title_inputbox.send_keys('Buy tea')

        # User types a description
        description_inputbox.send_keys('Go to the shop "Tea Master" and buy puer tea')

        # User set a performer
        performers_inputbox.send_keys('Vladislav Troshchiy')

        # User set a deadline
        deadline_inputbox.send_keys('2024-10-02 20:00')

        # When user hits on the "Add task" button, the page update,
        # and now the page contains "Buy tea" as an item in a tasks lists
        add_task_btn = self.browser.find_element(By.CLASS_NAME, 'submit-btn')
        self.assertEqual(add_task_btn.get_attribute('value'), 'Add task')
        add_task_btn.click()
        self.wait_for_item_in_tasks_list('Buy tea')

        # There is still a form inviting user to add another task
        # User add task "Brew the tea"
        add_task_form = self.wait_for(
            lambda: self.browser.find_element(By.ID, 'add-task')
        )
        self.add_task(
            form=add_task_form,
            title='Brew the tea',
            description='Place 10g of tea into the 500ml tea pot, '
                        'pour the heated water and steep tea between 3 to 5 minutes.',
            performers='Vladislav Troshchiy',
            deadline='2024-10-03 13:00'
        )

        # The page updates again, and now shows both items on tasks list
        self.wait_for_item_in_tasks_list('Buy tea')
        self.wait_for_item_in_tasks_list('Brew the tea')

    def test_cannot_add_task_with_empty_fields(self):
        # User goes to homepage and accidentally tries to submit a task with empty title
        # User hits Enter on the empty title input
        self.browser.get(self.live_server_url)
        self.get_new_task_element_by_id('id_title').send_keys(Keys.ENTER)

        # The browser intercepts the request, and does not load the page
        self.wait_for(lambda: self.browser.find_element(By.CSS_SELECTOR, '#id_title:invalid'))
        self.wait_for(lambda: self.browser.find_element(By.CSS_SELECTOR, '#id_description:invalid'))
        self.wait_for(lambda: self.browser.find_element(By.CSS_SELECTOR, '#id_performers:invalid'))
        self.wait_for(lambda: self.browser.find_element(By.CSS_SELECTOR, '#id_deadline:invalid'))

        # User starts typing some text for the new task and the error disappears
        add_task_form = self.wait_for(
            lambda: self.browser.find_element(By.ID, 'add-task')
        )
        self.add_task(
            form=add_task_form,
            title='Buy tea',
            description='Go to the tea shop and buy puer tea',
            performers='Vladislav Troshchiy',
            deadline='2024-10-02 20:00',
            submit=False
        )
        self.wait_for(lambda: self.browser.find_element(By.CSS_SELECTOR, '#id_title:valid'))
        self.wait_for(lambda: self.browser.find_element(By.CSS_SELECTOR, '#id_description:valid'))
        self.wait_for(lambda: self.browser.find_element(By.CSS_SELECTOR, '#id_performers:valid'))
        self.wait_for(lambda: self.browser.find_element(By.CSS_SELECTOR, '#id_deadline:valid'))

        # And he can submit it successfully
        self.get_new_task_element_by_id('id_title').send_keys(Keys.ENTER)
        self.wait_for_item_in_tasks_list('Buy tea')

        # Perversely, user now decides to submit a second task with blank fields
        self.get_new_task_element_by_id('id_title').send_keys(Keys.ENTER)

        # Again, the browser will not comply
        tasks_list = self.browser.find_element(By.ID, 'tasks-list')
        list_items = tasks_list.find_elements(By.TAG_NAME, 'li')
        self.assertEqual(len(list_items), 1)
        self.assertEqual('Buy tea', list_items[0].text)

        self.wait_for(lambda: self.browser.find_element(By.CSS_SELECTOR, '#id_title:invalid'))
        self.wait_for(lambda: self.browser.find_element(By.CSS_SELECTOR, '#id_description:invalid'))
        self.wait_for(lambda: self.browser.find_element(By.CSS_SELECTOR, '#id_performers:invalid'))
        self.wait_for(lambda: self.browser.find_element(By.CSS_SELECTOR, '#id_deadline:invalid'))

        # And user can correct it by filling some text in
        add_task_form = self.wait_for(
            lambda: self.browser.find_element(By.ID, 'add-task')
        )
        self.add_task(
            form=add_task_form,
            title='Brew the tea',
            description='Place 10g of tea into the 500ml tea pot, '
                        'pour the heated water and steep tea between 3 to 5 minutes.',
            performers='Vladislav Troshchiy',
            deadline='2024-10-03 13:00',
            submit=False
        )
        self.wait_for(lambda: self.browser.find_element(By.CSS_SELECTOR, '#id_title:valid'))
        self.wait_for(lambda: self.browser.find_element(By.CSS_SELECTOR, '#id_description:valid'))
        self.wait_for(lambda: self.browser.find_element(By.CSS_SELECTOR, '#id_performers:valid'))
        self.wait_for(lambda: self.browser.find_element(By.CSS_SELECTOR, '#id_deadline:valid'))

        self.get_new_task_element_by_id('id_title').send_keys(Keys.ENTER)
        self.wait_for_item_in_tasks_list('Buy tea')
        self.wait_for_item_in_tasks_list('Brew the tea')

    def test_can_create_a_subtask(self):
        # User goes to homepage and add a task "Brew the tea"
        self.browser.get(self.live_server_url)
        add_task_form = self.wait_for(lambda: self.browser.find_element(By.ID, 'add-task'))
        brew_the_tea_task_data = {
            'title': 'Brew the tea',
            'description': 'Place 10g of tea into the tea pot and steep tea between 3 to 5 minutes.',
            'performers': 'Vlad Troshchiy',
            'deadline': '2024-10-03 13:00'
        }
        brew_the_tea_created_at = datetime.datetime.now()
        self.add_task(form=add_task_form, **brew_the_tea_task_data)

        # Then user hits on the task title at the sidebar
        self.wait_for_item_in_tasks_list('Brew the tea').click()

        # Page offers to enter a title, description, performers and deadline to add a subtask
        add_subtask_form = self.wait_for(lambda: self.browser.find_element(By.ID, 'add-subtask'))

        # User enters data and submit the form via 'Add subtask' button
        self.add_task(
            form=add_subtask_form,
            title='Heat water',
            description='Heat water to 94 degrees C',
            performers='Troshchiy Vladislav',
            deadline='2024-10-03 12:50',
            submit=False
        )
        add_subtask_btn = add_subtask_form.find_element(By.CLASS_NAME, 'submit-btn')
        self.assertEqual(add_subtask_btn.get_property('value'), 'Add subtask')
        add_subtask_btn.click()

        # The page is being updated, and now the page contains added subtask title in the tasks list
        self.wait_for_item_in_tasks_list('Heat water')

        # User notices that the page still shows the "Brew the tea" task detail page
        self.wait_for(
            lambda: self.assert_task_details_equals_to(
                **brew_the_tea_task_data,
                created_at=brew_the_tea_created_at,
                status_label='Assigned'
            )
        )

        # And now the page contains "Heat water" as an item of subtasks list
        subtasks_list = self.browser.find_element(By.ID, 'subtasks-list').find_elements(By.CLASS_NAME, 'task-title')
        self.assertIn('Heat water', [subtask.text for subtask in subtasks_list])

        # There is still a form inviting user to add another subtask
        # User add subtask "Steep the tea"
        add_subtask_form = self.wait_for(lambda: self.browser.find_element(By.ID, 'add-subtask'))
        self.add_task(
            form=add_subtask_form,
            title='Steep the tea',
            description='Pour the heated water over the tea leaves and steep tea between 3 to 5 minutes.',
            performers='Vladislav',
            deadline='2024-10-04 13:00'
        )

        # The page updates again, and now shows both subtask on the sidebar tasks list
        self.wait_for_item_in_tasks_list('Heat water')
        self.wait_for_item_in_tasks_list('Steep the tea')

        # Also the subtasks are present on the "Brew the tea" task details page
        subtasks_list = self.browser.find_element(By.ID, 'subtasks-list').find_elements(By.CLASS_NAME, 'task-title')
        self.assertIn('Heat water', [subtask.text for subtask in subtasks_list])
        self.assertIn('Steep the tea', [subtask.text for subtask in subtasks_list])
