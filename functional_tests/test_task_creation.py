import time

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

        # The website offers to enter a task
        inputbox = self.get_new_task_title_inputbox()
        self.assertEqual(
            inputbox.get_attribute('placeholder'),
            'Title'
        )

        # User types "Buy tea"
        inputbox.send_keys('Buy tea')

        # When user hits enter, the page update, and now the page contains "Buy tea" as an item in a tasks lists
        inputbox.send_keys(Keys.ENTER)
        self.wait_for_item_in_tasks_list('Buy tea')

        # There is still a text box inviting user to add another item
        # User enters "Brew the tea"
        self.add_task('Brew the tea')

        # The page updates again, and now shows both items on user's list
        self.wait_for_item_in_tasks_list('Buy tea')
        self.wait_for_item_in_tasks_list('Brew the tea')

    def test_cannot_add_task_with_empty_title(self):
        # User goes to homepage and accidentally tries to submit a task with empty title
        # User hits Enter on the empty title input
        self.browser.get(self.live_server_url)
        self.get_new_task_title_inputbox() .send_keys(Keys.ENTER)

        # The browser intercepts the request, and does not load the page
        self.wait_for(lambda: self.browser.find_element(By.CSS_SELECTOR, '#id_title:invalid'))

        # User starts typing some text for the new item and the error disappears
        self.get_new_task_title_inputbox().send_keys('Buy tea')
        self.wait_for(lambda: self.browser.find_element(By.CSS_SELECTOR, '#id_title:valid'))

        # And he can submit it successfully
        self.get_new_task_title_inputbox().send_keys(Keys.ENTER)
        self.wait_for_item_in_tasks_list('Buy tea')

        # Perversely, user now decides to submit a second task with blank title
        self.get_new_task_title_inputbox().send_keys(Keys.ENTER)

        # Again, the browser will not comply
        tasks_list = self.browser.find_element(By.ID, 'tasks-list')
        list_items = tasks_list.find_elements(By.TAG_NAME, 'li')
        self.assertEqual(len(list_items), 1)
        self.assertEqual('Buy tea', list_items[0].text)

        self.wait_for(lambda: self.browser.find_element(By.CSS_SELECTOR, '#id_title:invalid'))

        # And user can correct it by filling some text in
        self.get_new_task_title_inputbox().send_keys('Brew the tea')
        self.wait_for(lambda: self.browser.find_element(By.CSS_SELECTOR, '#id_title:valid'))
        self.get_new_task_title_inputbox().send_keys(Keys.ENTER)
        self.wait_for_item_in_tasks_list('Buy tea')
        self.wait_for_item_in_tasks_list('Brew the tea')

    def test_can_view_task_info(self):
        # User goes to homepage
        self.browser.get(self.live_server_url)

        # User adds task "Buy tea"
        self.add_task('Buy tea')
        self.wait_for_item_in_tasks_list('Buy tea')

        # Then user adds task "Brew the tea"
        self.add_task('Brew the tea')
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
