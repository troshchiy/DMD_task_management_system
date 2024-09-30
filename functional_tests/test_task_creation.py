from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from .base import FunctionalTest


class NewVisitorTest(FunctionalTest):
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

        # When user hits on the "Add" button, the page update,
        # and now the page contains "Buy tea" as an item in a tasks lists
        add_task_btn = self.browser.find_element(By.ID, 'add-task-btn')
        add_task_btn.click()
        self.wait_for_item_in_tasks_list('Buy tea')

        # There is still a form inviting user to add another task
        # User add task "Brew the tea"
        self.add_task(
            title='Brew the tea',
            description='Place 10g of tea into the 500ml tea pot, '
                        'pour the heated water and steep tea between 3 to 5 minutes.',
            performers='Vladislav Troshchiy',
            deadline='2024-10-03 13:00'
        )

        # The page updates again, and now shows both items on user's list
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
        self.add_task(
            title='Buy tea',
            description='Go to the tea shop and buy puer tea',
            performers='Vladislav Troshchiy',
            deadline='2024-10-02 20:00'
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
        self.add_task(
            title='Brew the tea',
            description='Place 10g of tea into the 500ml tea pot, '
                        'pour the heated water and steep tea between 3 to 5 minutes.',
            performers='Vladislav Troshchiy',
            deadline='2024-10-03 13:00'
        )
        self.wait_for(lambda: self.browser.find_element(By.CSS_SELECTOR, '#id_title:valid'))
        self.wait_for(lambda: self.browser.find_element(By.CSS_SELECTOR, '#id_description:valid'))
        self.wait_for(lambda: self.browser.find_element(By.CSS_SELECTOR, '#id_performers:valid'))
        self.wait_for(lambda: self.browser.find_element(By.CSS_SELECTOR, '#id_deadline:valid'))

        self.get_new_task_element_by_id('id_title').send_keys(Keys.ENTER)
        self.wait_for_item_in_tasks_list('Buy tea')
        self.wait_for_item_in_tasks_list('Brew the tea')

    def test_can_view_task_info(self):
        # User goes to homepage
        self.browser.get(self.live_server_url)

        # User adds task "Buy tea"
        self.add_task(
            title='Buy tea',
            description='Go to the tea shop and buy puer tea',
            performers='Vladislav Troshchiy',
            deadline='2024-10-02 20:00'
        )
        self.wait_for_item_in_tasks_list('Buy tea')

        # Then user adds task "Brew the tea"
        self.add_task(
            title='Brew the tea',
            description='Place 10g of tea into the 500ml tea pot, '
                        'pour the heated water and steep tea between 3 to 5 minutes.',
            performers='Vladislav Troshchiy',
            deadline='2024-10-03 13:00'
        )
        self.wait_for_item_in_tasks_list('Brew the tea')

        # User wants to see detail info about the "Buy tea" task, so he hits on the "Brew tea" list item at the sidebar
        buy_tea_li = self.wait_for(
            lambda: self.browser.find_element(By.ID, 'tasks-list').find_element(By.LINK_TEXT, 'Buy tea')
        )
        buy_tea_li.click()

        # The page shows the "Buy tea" task info
        task_detail_form = self.wait_for(
            lambda: self.browser.find_element(By.ID, 'task-detail')
        )
        title = task_detail_form.find_element(By.ID, 'id_title')
        self.assertEqual('Buy tea', title.get_attribute('value'))

        # Then user wants to see detail info about the "Brew the tea" task, and he hits on the list item
        brew_the_tea_li = self.wait_for(
            lambda: self.browser.find_element(By.ID, 'tasks-list').find_element(By.LINK_TEXT, 'Brew the tea')
        )
        brew_the_tea_li.click()

        # And the page shows the detail info
        task_info_form = self.wait_for(
            lambda: self.browser.find_element(By.ID, 'task-detail')
        )
        title = task_info_form.find_element(By.ID, 'id_title')
        self.assertEqual('Brew the tea', title.get_attribute('value'))

        # User noticed that now there are no info about the "Buy tea" task
        content = self.browser.find_element(By.ID, 'content')
        self.assertNotIn('Buy tea', content.get_attribute('innerHTML'))
